"""Put the Uzhavan web app on a public link: AWS Lambda + a Function URL, talking to the agent on AgentCore.

    .\\.venv\\Scripts\\python.exe scripts\\deploy_web.py          # create or update, prints the public link
    .\\.venv\\Scripts\\python.exe scripts\\deploy_web.py --delete # remove it after the hackathon

What it creates (in your AWS_REGION, the same region as the agent):
  - an S3 bucket `uzhavan-web-<account>-<region>` holding the code package (uploaded in parts);
  - an IAM role `uzhavan-web-role` that may only call your AgentCore runtime (and write logs);
  - a Lambda function `uzhavan-web` (Python 3.12) running deploy/web/lambda_app.py, which serves
    demo/server.py: the same page and API as `./kit demo --target agentcore`;
  - a public Function URL. No keys are in the function or the page. Each device may send
    CHAT_LIMIT_PER_HOUR questions an hour, and at most 5 copies run at once, to cap the cost.

The Linux packages (FastAPI, Strands, ...) come from deploy/web/deps.zip. To rebuild it:
  pip install --target build --platform manylinux2014_x86_64 --python-version 3.12 --only-binary=:all: \\
      strands-agents fastapi mangum gTTS pyyaml   (then zip the contents of build/ as deploy/web/deps.zip)
"""

from __future__ import annotations

import io
import json
import sys
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from decider_kit.config import load_dotenv, settings  # noqa: E402

load_dotenv()
import boto3  # noqa: E402

NAME = "uzhavan-web"
ROLE = "uzhavan-web-role"
DEPS = ROOT / "deploy" / "web" / "deps.zip"
OUT = ROOT / "submission" / "web.json"
SKIP = ("__pycache__", ".pyc", "eval_cases.jsonl", "demo_script.yaml")


def build_zip() -> bytes:
    if not DEPS.exists():
        sys.exit(f"missing {DEPS}: see the note at the top of this script to build it")
    buf = io.BytesIO(DEPS.read_bytes())
    with zipfile.ZipFile(buf, "a", zipfile.ZIP_DEFLATED) as z:
        for folder in ("agent", "decider_kit", "demo"):
            for p in (ROOT / folder).rglob("*"):
                if p.is_file() and not any(s in str(p) for s in SKIP):
                    z.write(p, p.relative_to(ROOT).as_posix())
        z.write(ROOT / "deploy" / "web" / "lambda_app.py", "lambda_app.py")
    return buf.getvalue()


def runtime_arn() -> str:
    dep = ROOT / "submission" / "deployment.json"
    if not dep.exists():
        sys.exit("deploy the agent first: .\\kit.cmd deploy")
    return json.loads(dep.read_text())["runtime_arn"]


def ensure_role(iam, arn: str) -> str:
    trust = {"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"},
                                                       "Action": "sts:AssumeRole"}]}
    try:
        role = iam.get_role(RoleName=ROLE)["Role"]["Arn"]
        fresh = False
    except iam.exceptions.NoSuchEntityException:
        role = iam.create_role(RoleName=ROLE, AssumeRolePolicyDocument=json.dumps(trust),
                               Description="Uzhavan public web app: may only call the Uzhavan agent")["Role"]["Arn"]
        fresh = True
    iam.attach_role_policy(RoleName=ROLE, PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole")
    iam.put_role_policy(RoleName=ROLE, PolicyName="invoke-uzhavan-agent", PolicyDocument=json.dumps({
        "Version": "2012-10-17",
        "Statement": [{"Effect": "Allow", "Action": "bedrock-agentcore:InvokeAgentRuntime", "Resource": [arn, f"{arn}/*"]}]}))
    if fresh:
        print("[web] new role: waiting 15 s for IAM to be ready...")
        time.sleep(15)
    return role


def upload(code: bytes, region: str, cfg) -> dict:
    """Send the package to an S3 bucket in small parts with retries (a 30 MB direct upload can drop on home
    internet), and return where Lambda should take it from."""
    from boto3.s3.transfer import TransferConfig

    acct = boto3.client("sts", region_name=region).get_caller_identity()["Account"]
    bucket, key = f"uzhavan-web-{acct}-{region}", "uzhavan-web.zip"
    s3 = boto3.client("s3", region_name=region, config=cfg)
    try:
        s3.head_bucket(Bucket=bucket)
    except Exception:  # noqa: BLE001  not there yet
        s3.create_bucket(Bucket=bucket, CreateBucketConfiguration={"LocationConstraint": region})
    print(f"[web] uploading the package ({len(code) / 1e6:.1f} MB) to s3://{bucket} in small parts...")
    s3.upload_fileobj(io.BytesIO(code), bucket, key,
                      Config=TransferConfig(multipart_threshold=5 * 1024 * 1024, multipart_chunksize=5 * 1024 * 1024,
                                            max_concurrency=2))
    print("[web] uploaded")
    return {"S3Bucket": bucket, "S3Key": key}


def deploy() -> None:
    region = settings().aws_region
    arn = runtime_arn()
    from botocore.config import Config

    # the code upload is about 30 MB: give slow home internet time to send it
    slow = Config(connect_timeout=60, read_timeout=900, retries={"max_attempts": 3})
    lam, iam = boto3.client("lambda", region_name=region, config=slow), boto3.client("iam")
    role = ensure_role(iam, arn)
    code = build_zip()
    src = upload(code, region, slow)
    env = {"Variables": {"AGENTCORE_ARN": arn, "DEMO_TARGET": "agentcore", "DECIDER_MODE": settings().decider_mode,
                         "BEDROCK_MODEL_ID": settings().bedrock_model, "CHAT_LIMIT_PER_HOUR": "30"}}
    try:
        lam.get_function(FunctionName=NAME)
        lam.update_function_code(FunctionName=NAME, **src)
        lam.get_waiter("function_updated_v2").wait(FunctionName=NAME)
        lam.update_function_configuration(FunctionName=NAME, Environment=env, Timeout=90, MemorySize=1024)
        print("[web] updated the function")
    except lam.exceptions.ResourceNotFoundException:
        for attempt in range(5):  # a new role can take a little longer to be usable
            try:
                lam.create_function(FunctionName=NAME, Runtime="python3.12", Role=role, Handler="lambda_app.handler",
                                    Code=src, Timeout=90, MemorySize=1024, Environment=env,
                                    Architectures=["x86_64"], Description="Uzhavan: public web app for the farm agent")
                break
            except lam.exceptions.InvalidParameterValueException as e:
                if attempt == 4:
                    raise
                print(f"[web] waiting for the role ({e.response['Error']['Message'][:60]}...)")
                time.sleep(10)
        print("[web] created the function")
    lam.get_waiter("function_active_v2").wait(FunctionName=NAME)
    lam.get_waiter("function_updated_v2").wait(FunctionName=NAME)
    try:
        lam.put_function_concurrency(FunctionName=NAME, ReservedConcurrentExecutions=5)
    except Exception as e:  # noqa: BLE001  some new accounts cannot reserve concurrency: the hourly limit still applies
        print(f"[web] note: could not cap concurrency ({type(e).__name__}); the per-device limit still applies")
    try:
        url = lam.get_function_url_config(FunctionName=NAME)["FunctionUrl"]
    except lam.exceptions.ResourceNotFoundException:
        url = lam.create_function_url_config(FunctionName=NAME, AuthType="NONE")["FunctionUrl"]
    for sid, action, extra in (("public-url", "lambda:InvokeFunctionUrl", {"FunctionUrlAuthType": "NONE"}),
                               ("public-url-invoke", "lambda:InvokeFunction", {"InvokedViaFunctionUrl": True})):
        try:
            lam.add_permission(FunctionName=NAME, StatementId=sid, Action=action, Principal="*", **extra)
        except lam.exceptions.ResourceConflictException:
            pass  # already there
        except Exception as e:  # noqa: BLE001  older boto3 without InvokedViaFunctionUrl
            print(f"[web] note: {sid}: {type(e).__name__}: {str(e)[:120]}")
    OUT.write_text(json.dumps({"url": url, "function": NAME, "region": region, "deployed_at": time.time()}, indent=2))
    print(f"[web] live: {url}\n[web] open it on your phone; the first answer can take 20 s while AWS wakes up")


def delete() -> None:
    region = settings().aws_region
    lam, iam = boto3.client("lambda", region_name=region), boto3.client("iam")
    for call in (lambda: lam.delete_function_url_config(FunctionName=NAME), lambda: lam.delete_function(FunctionName=NAME),
                 lambda: iam.delete_role_policy(RoleName=ROLE, PolicyName="invoke-uzhavan-agent"),
                 lambda: iam.detach_role_policy(RoleName=ROLE, PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"),
                 lambda: iam.delete_role(RoleName=ROLE)):
        try:
            call()
        except Exception as e:  # noqa: BLE001
            print(f"[web] skip: {type(e).__name__}")
    try:
        acct = boto3.client("sts", region_name=region).get_caller_identity()["Account"]
        b = boto3.resource("s3", region_name=region).Bucket(f"uzhavan-web-{acct}-{region}")
        b.objects.all().delete()
        b.delete()
    except Exception as e:  # noqa: BLE001
        print(f"[web] skip bucket: {type(e).__name__}")
    OUT.unlink(missing_ok=True)
    print("[web] deleted")


if __name__ == "__main__":
    delete() if "--delete" in sys.argv else deploy()
