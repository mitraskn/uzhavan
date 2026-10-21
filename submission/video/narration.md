0. Uzhavan runs on Amazon Bedrock AgentCore Runtime, talks through Amazon Bedrock and gets real weather from Open-Meteo. Before any advice, the Strands Decider checks that the district and the crop are really known, so the app asks instead of guessing.

1. A phone app for Tamil Nadu farmers that turns real weather into clear advice, in Tamil or English. What it does: Fifteen farm tools as traffic-light cards. Tap, type or speak, with answers read aloud. Every card shows what the Strands Decider checked.

2. The agent you are about to see is running on Amazon Bedrock AgentCore Runtime.

3. A new farmer asks about spraying, but has not said where the farm is or what is growing. The decider scored rule override 0.01, off topic 0.16, in scope 0.86, so the verdict was guide, in 6.2 seconds.

4. Now the farmer names the crop and the district, so the advice can be given. The decider scored rule override 0.01, off topic 0.13, in scope 0.90, so the verdict was proceed, in 6.5 seconds.

5. The same farmer asks in Tanglish whether it will rain this week. The decider scored rule override 0.01, off topic 0.17, in scope 0.88, so the verdict was proceed, in 7.1 seconds.

6. The farmer switches the app to Tamil and asks, in Tamil, about the paddy harvest. The decider scored rule override 0.01, off topic 0.12, in scope 0.90, so the verdict was proceed, in 7.9 seconds.

7. Someone tries to change the assistant's rules. The decider scored rule override 0.70, off topic 0.21, in scope 0.40, so the verdict was deny, in 7.2 seconds.

8. An off-topic question. The decider scored rule override 0.41, off topic 0.34, in scope 0.20, so the verdict was redirect, in 6.8 seconds.

9. The farmer sends a photo that is not a leaf. The decider scored is crop photo 0.18, condition confidence 0.40, so the verdict was guide, in 3.1 seconds.

10. On 95 labelled decisions, with the decider on the AWS User Group Madurai hosted API, Strands Decider was 91% accurate at a median of 4085 milliseconds, against 95% and 2840 milliseconds for the Bedrock LLM asked the same questions. The decider costs about 16 times less per check, and when it was confident it was right 100% of the time; when it is unsure, the app asks the farmer.

11. Real weather, clear answers, and a fast decision model that makes sure the advice is about the farmer's own field.