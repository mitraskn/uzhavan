"""Uzhavan tools: real weather from Open-Meteo, and farm advice computed from it with fixed rules.

The advice is plain Python (no LLM): the same forecast always gives the same answer, with the
numbers behind it. Spraying uses the HOURLY forecast to find a dry, calm window (rain often comes
in the afternoon, so a morning window can still be safe). Every card carries its text in English
and Tamil ({"en": ..., "ta": ...}); the UI shows both. The Strands @tool wrappers at the bottom let
the LLM call the same functions for typed or spoken questions.

Open-Meteo is free and needs no API key: https://open-meteo.com
"""

from __future__ import annotations

import contextvars
import json
import re
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any

from strands import tool

from .i18n import DISTRICT_TA, WMO, crop_name, day_name, district_name, t, window_label

IST = timezone(timedelta(hours=5, minutes=30))
LANGS = ("en", "ta")

# ---- the 38 districts of Tamil Nadu (approximate district headquarters, lat/lon) ----------------

TN_DISTRICTS: dict[str, tuple[float, float]] = {
    "Ariyalur": (11.140, 79.078), "Chengalpattu": (12.692, 79.977), "Chennai": (13.083, 80.270),
    "Coimbatore": (11.017, 76.956), "Cuddalore": (11.748, 79.768), "Dharmapuri": (12.128, 78.158),
    "Dindigul": (10.362, 77.980), "Erode": (11.341, 77.717), "Kallakurichi": (11.738, 78.959),
    "Kancheepuram": (12.834, 79.703), "Kanniyakumari": (8.178, 77.411), "Karur": (10.960, 78.077),
    "Krishnagiri": (12.519, 78.214), "Madurai": (9.925, 78.120), "Mayiladuthurai": (11.103, 79.655),
    "Nagapattinam": (10.766, 79.843), "Namakkal": (11.219, 78.168), "Nilgiris": (11.406, 76.696),
    "Perambalur": (11.234, 78.883), "Pudukkottai": (10.380, 78.821), "Ramanathapuram": (9.371, 78.830),
    "Ranipet": (12.932, 79.333), "Salem": (11.664, 78.146), "Sivaganga": (9.847, 78.481),
    "Tenkasi": (8.959, 77.315), "Thanjavur": (10.787, 79.138), "Theni": (10.010, 77.477),
    "Thoothukudi": (8.764, 78.135), "Tiruchirappalli": (10.790, 78.705), "Tirunelveli": (8.714, 77.757),
    "Tirupathur": (12.496, 78.567), "Tiruppur": (11.108, 77.341), "Tiruvallur": (13.143, 79.909),
    "Tiruvannamalai": (12.226, 79.075), "Tiruvarur": (10.773, 79.637), "Vellore": (12.916, 79.132),
    "Viluppuram": (11.940, 79.493), "Virudhunagar": (9.580, 77.962),
}

DISTRICT_ALIASES = {
    "tanjore": "Thanjavur", "thanjai": "Thanjavur", "trichy": "Tiruchirappalli", "tiruchi": "Tiruchirappalli",
    "tuticorin": "Thoothukudi", "kanyakumari": "Kanniyakumari", "nagercoil": "Kanniyakumari",
    "kanchipuram": "Kancheepuram", "villupuram": "Viluppuram", "ooty": "Nilgiris", "kovai": "Coimbatore",
    "nellai": "Tirunelveli", "tirupur": "Tiruppur", "thiruvarur": "Tiruvarur", "thiruvallur": "Tiruvallur",
    "thiruvannamalai": "Tiruvannamalai", "tirupattur": "Tirupathur", "ramnad": "Ramanathapuram",
    "sivagangai": "Sivaganga", "madras": "Chennai", "mayavaram": "Mayiladuthurai", "pudukottai": "Pudukkottai",
    "thanjore": "Thanjavur", "thanjavoor": "Thanjavur", "tanjavur": "Thanjavur", "coimbatoor": "Coimbatore",
    "kovaii": "Coimbatore", "maduri": "Madurai", "mathurai": "Madurai", "salam": "Salem", "erodu": "Erode",
    "thirunelveli": "Tirunelveli", "thiruchi": "Tiruchirappalli", "dindugal": "Dindigul", "thindukal": "Dindigul",
    "kumbakonam": "Thanjavur", "pollachi": "Coimbatore", "karur": "Karur", "namakal": "Namakkal",
    "thoothukudi": "Thoothukudi", "vellur": "Vellore", "krishnagiri": "Krishnagiri", "theni": "Theni",
}

CROPS = ["Paddy", "Banana", "Sugarcane", "Cotton", "Groundnut", "Coconut", "Maize", "Turmeric", "Vegetables"]
CROP_ALIASES = {
    "rice": "Paddy", "nel": "Paddy", "nellu": "Paddy", "vazhai": "Banana", "vaazhai": "Banana",
    "karumbu": "Sugarcane", "paruthi": "Cotton", "kadalai": "Groundnut", "nilakadalai": "Groundnut",
    "verkadalai": "Groundnut", "peanut": "Groundnut", "thennai": "Coconut", "makkacholam": "Maize",
    "corn": "Maize", "manjal": "Turmeric", "kaikari": "Vegetables", "vegetable": "Vegetables",
}
# Tamil script (what Tamil speech recognition writes); matched without the final pulli (்) so
# "தஞ்சாவூரில்" (in Thanjavur) still matches "தஞ்சாவூர்"
TAMIL_DISTRICTS = {**{v: k for k, v in DISTRICT_TA.items()}, "தஞ்சை": "Thanjavur", "கோவை": "Coimbatore",
                   "திருச்சி": "Tiruchirappalli", "நெல்லை": "Tirunelveli"}
TAMIL_CROPS = {"நெல்": "Paddy", "வாழை": "Banana", "கரும்பு": "Sugarcane", "பருத்தி": "Cotton",
               "நிலக்கடலை": "Groundnut", "கடலை": "Groundnut", "தென்னை": "Coconut", "மக்காச்சோளம்": "Maize",
               "மஞ்சள்": "Turmeric", "காய்கறி": "Vegetables"}


def norm_district(name: str | None) -> str | None:
    if not name:
        return None
    key = name.strip().lower()
    for d in TN_DISTRICTS:
        if d.lower() == key:
            return d
    return DISTRICT_ALIASES.get(key) or TAMIL_DISTRICTS.get(name.strip())


def norm_crop(name: str | None) -> str | None:
    if not name:
        return None
    key = name.strip().lower()
    for c in CROPS:
        if c.lower() == key:
            return c
    return CROP_ALIASES.get(key) or TAMIL_CROPS.get(name.strip())


def is_tamil(text: str) -> bool:
    return bool(re.search(r"[஀-௿]", text or ""))


def find_mentions(text: str) -> tuple[str | None, str | None]:
    """The district and crop a farmer names in a message (English, Tanglish or Tamil script)."""
    text = text or ""
    district = crop = None
    for w in re.findall(r"[a-z]+", text.lower()):
        district = district or norm_district(w)
        crop = crop or norm_crop(w)
    for ta, name in sorted(TAMIL_DISTRICTS.items(), key=lambda kv: -len(kv[0])):
        if not district and ta.rstrip("்") in text:
            district = name
    for ta, name in sorted(TAMIL_CROPS.items(), key=lambda kv: -len(kv[0])):
        if not crop and ta.rstrip("்") in text:
            crop = name
    return district, crop


def both(fn) -> dict[str, str]:
    """{"en": fn("en"), "ta": fn("ta")}"""
    return {lg: fn(lg) for lg in LANGS}


# ---- real weather ----------------------------------------------------------------------------------

OPEN_METEO = "https://api.open-meteo.com/v1/forecast"
_CACHE: dict[str, tuple[float, dict]] = {}
CACHE_S = 15 * 60


class WeatherError(RuntimeError):
    def __init__(self, key: str, **v):
        self.text = both(lambda lg: t(lg, key, **v))
        super().__init__(self.text["en"])


def _fetch(url: str) -> dict:  # separate so tests can replace it
    with urllib.request.urlopen(url, timeout=12) as r:
        return json.loads(r.read().decode())


def now_ist() -> datetime:
    return datetime.now(IST)


DAILY = ("weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,"
         "wind_speed_10m_max,wind_gusts_10m_max,sunshine_duration,et0_fao_evapotranspiration")
HOURLY = ("precipitation,precipitation_probability,wind_speed_10m,wind_gusts_10m,temperature_2m,relative_humidity_2m,"
          "weather_code,soil_moisture_3_to_9cm")


def _num(arr: Any, i: int, default: float = 0.0) -> float:
    try:
        v = arr[i]
        return default if v is None else float(v)
    except (IndexError, TypeError, KeyError):
        return default


def all_days(district: str) -> list[dict[str, Any]]:
    """Real weather for a district: the last 7 days and the next 5, each with its hours.
    Day i: 0 = today, 1 = tomorrow, -1 = yesterday."""
    d = norm_district(district)
    if not d:
        raise WeatherError("district.unknown", name=district)
    hit = _CACHE.get(d)
    if not hit or time.time() - hit[0] > CACHE_S:
        lat, lon = TN_DISTRICTS[d]
        q = urllib.parse.urlencode({"latitude": lat, "longitude": lon, "timezone": "Asia/Kolkata",
                                    "forecast_days": 5, "past_days": 7, "daily": DAILY, "hourly": HOURLY})
        try:
            raw = _fetch(f"{OPEN_METEO}?{q}")
        except Exception as e:  # noqa: BLE001
            raise WeatherError("weather.err") from e
        hit = (time.time(), raw)
        _CACHE[d] = hit
    daily, hourly = hit[1]["daily"], hit[1].get("hourly") or {}
    hours_by_day: dict[str, list[dict]] = {}
    for i, ts in enumerate(hourly.get("time", [])):
        hours_by_day.setdefault(ts[:10], []).append({
            "h": int(ts[11:13]), "rain": _num(hourly.get("precipitation"), i),
            "chance": int(_num(hourly.get("precipitation_probability"), i)), "wind": _num(hourly.get("wind_speed_10m"), i),
            "gust": _num(hourly.get("wind_gusts_10m"), i), "temp": _num(hourly.get("temperature_2m"), i, 28.0),
            "rh": _num(hourly.get("relative_humidity_2m"), i, 70.0), "code": int(_num(hourly.get("weather_code"), i)),
            "soil": _num(hourly.get("soil_moisture_3_to_9cm"), i, -1.0)})
    today = now_ist().date()
    out = []
    for k, day in enumerate(daily["time"]):
        i = (datetime.strptime(day, "%Y-%m-%d").date() - today).days
        code = int(_num(daily.get("weather_code"), k))
        icon, en, ta = WMO.get(code, ("🌥️", "Cloudy", "மேகமூட்டம்"))
        hours = hours_by_day.get(day, [])
        soils = [x["soil"] for x in hours if x["soil"] >= 0]
        day_rh = [x["rh"] for x in hours if 9 <= x["h"] <= 17]
        out.append({
            "date": day, "i": i, "icon": icon, "text": {"en": en, "ta": ta},
            "day": both(lambda lg, day=day, i=i: day_name(day, i, lg)),
            "rain_mm": round(_num(daily.get("precipitation_sum"), k), 1),
            "rain_chance": int(_num(daily.get("precipitation_probability_max"), k)),
            "tmax": round(_num(daily.get("temperature_2m_max"), k)), "tmin": round(_num(daily.get("temperature_2m_min"), k)),
            "wind_kmh": round(_num(daily.get("wind_speed_10m_max"), k)),
            "gust_kmh": round(_num(daily.get("wind_gusts_10m_max"), k)),
            "sun_h": round(_num(daily.get("sunshine_duration"), k) / 3600, 1),
            "et0_mm": round(_num(daily.get("et0_fao_evapotranspiration"), k), 1),
            "soil": round(sum(soils) / len(soils), 3) if soils else None,
            "rh_day": round(sum(day_rh) / len(day_rh)) if day_rh else None,
            "hours": hours,
        })
    return out


def forecast(district: str, days: int = 5) -> list[dict[str, Any]]:
    """Today and the next days (day i = 0, 1, ...)."""
    return [d for d in all_days(district) if d["i"] >= 0][:days]


def past(district: str) -> list[dict[str, Any]]:
    """The last 7 days, oldest first."""
    return [d for d in all_days(district) if d["i"] < 0]


# ---- the rules (deterministic) -----------------------------------------------------------------------

SPRAY_HOURS = (6, 18)    # spray in daylight
WINDOW_H = 4             # spraying plus drying time
DRY_MM, MAX_CHANCE, MAX_WIND = 0.2, 40, 15


def spray_window(day: dict) -> tuple[int, int] | None:
    """The first dry, calm daylight window of at least WINDOW_H hours (hourly forecast), as (start, end)."""
    hours = {x["h"]: x for x in day.get("hours", [])}
    if not hours:
        return None
    first = SPRAY_HOURS[0]
    if day.get("i") == 0:
        first = max(first, now_ist().hour + 1)  # today: only the hours still ahead

    def ok(h: int) -> bool:
        x = hours.get(h)
        return bool(x) and x["rain"] <= DRY_MM and x["chance"] <= MAX_CHANCE and x["wind"] <= MAX_WIND

    for start in range(first, SPRAY_HOURS[1] - WINDOW_H + 1):
        if all(ok(h) for h in range(start, start + WINDOW_H)):
            end = start + WINDOW_H
            while end < SPRAY_HOURS[1] and ok(end):
                end += 1
            return start, end
    return None


def spray_level(day: dict) -> tuple[str, str, tuple[int, int] | None]:
    """GREEN: dry and calm all day. YELLOW: only a dry, calm window (we say when). RED: no safe window."""
    w = spray_window(day)
    if not day.get("hours"):  # no hourly data: daily rule
        if day["rain_mm"] >= 5:
            return "RED", "spray.why.rain", None
        if day["wind_kmh"] > 20:
            return "RED", "spray.why.wind", None
        if day["rain_chance"] >= 40:
            return "YELLOW", "spray.why.chance", None
        return ("YELLOW", "spray.why.breezy", None) if day["wind_kmh"] >= 12 else ("GREEN", "spray.why.dry", None)
    if not w:
        calm = [x for x in day["hours"] if SPRAY_HOURS[0] <= x["h"] < SPRAY_HOURS[1] and x["wind"] > MAX_WIND]
        return "RED", ("spray.why.wind" if day["rain_mm"] < 1 and calm else "spray.why.rain"), None
    if day["rain_mm"] < 1 and day["rain_chance"] < MAX_CHANCE and day["wind_kmh"] <= MAX_WIND:
        return "GREEN", "spray.why.dry", w
    return "YELLOW", "spray.why.window", w


def _when(day: dict, w: tuple[int, int] | None, lg: str) -> str:
    return f"{day['day'][lg]} {window_label(*w, lg)}" if w else day["day"][lg]


def best_spray(days: list[dict]) -> tuple[dict, tuple[int, int] | None] | None:
    """The earliest day with a safe spraying time (a fully dry day or a dry, calm window)."""
    for d in days:
        level, _, w = spray_level(d)
        if level != "RED":
            return d, w
    return None


def spray_card(district: str, crop: str) -> dict[str, Any]:
    """Today's spray advice; late in the day (no 4-hour window left before dark) it is tomorrow's."""
    days = forecast(district)
    late = now_ist().hour > SPRAY_HOURS[1] - WINDOW_H  # after 2 PM nothing more can be sprayed today
    i = 1 if late and len(days) > 1 else 0
    day = days[i]
    sfx = ".tmrw" if i == 1 else ""
    level, why, w = spray_level(day)
    if why == "spray.why.rain":
        why += sfx
    v = {"rain": day["rain_mm"], "wind": day["wind_kmh"], "chance": day["rain_chance"]}
    title = both(lambda lg: t(lg, "spray.YELLOW" + sfx, window=window_label(*w, lg)) if level == "YELLOW" and w
                 else t(lg, "spray.YELLOW.care" + sfx) if level == "YELLOW" else t(lg, f"spray.{level}{sfx}"))
    best = best_spray(days[i + 1:] if level == "RED" else days[i:])
    return {"type": "traffic", "kind": "spray", "level": level, "title": title, "day": day["day"],
            "reason": both(lambda lg: (t(lg, "spray.late") if late else "") + t(lg, why, **v)),
            "window": list(w) if w else None,
            "best": both(lambda lg: t(lg, "best", when=_when(best[0], best[1], lg)) if best else t(lg, "best.none"))
            if level != "GREEN" else None,
            "district": norm_district(district), "crop": norm_crop(crop) or crop,
            "rain_mm": day["rain_mm"], "rain_chance": day["rain_chance"], "wind_kmh": day["wind_kmh"],
            "stats": [stat("lbl.rain", f"{day['rain_mm']} mm"), stat("lbl.chance", f"{day['rain_chance']}%"),
                      stat("lbl.wind", f"{day['wind_kmh']} km/h")]}


# ---- shared helpers for the cards --------------------------------------------------------------------

LATE_HOUR = 15  # after 3 PM, field-work advice is for tomorrow


def stat(label_key: str, value: str) -> dict[str, Any]:
    return {"label": both(lambda lg: t(lg, label_key)), "value": value}


def target(days: list[dict]) -> dict:
    """Today, or tomorrow once it is late in the day."""
    return days[1] if now_ist().hour >= LATE_HOUR and len(days) > 1 else days[0]


def dword(day: dict, lg: str) -> str:
    """'today' / 'tomorrow' / 'Fri 23 Oct' for use inside a sentence."""
    w = day["day"][lg]
    return w.lower() if lg == "en" and day["i"] in (0, 1) else w


def soil_state(v: float | None) -> str:
    if v is None:
        return "moist"
    return "dry" if v < 0.15 else "moist" if v < 0.35 else "wet" if v < 0.42 else "flooded"


def soil_stat(v: float | None) -> dict[str, Any]:
    st = soil_state(v)
    return {"label": both(lambda lg: t(lg, "lbl.soil")), "value": both(lambda lg: t(lg, f"soil.{st}"))}


def after(days: list[dict], d: dict, n: int) -> list[dict]:
    """d and the n-1 days after it."""
    k = days.index(d)
    return days[k:k + n]


def traffic(kind: str, level: str, title: dict, reason: dict, stats: list, district: str, crop: str | None = None,
            best: dict | None = None, day: dict | None = None, **extra) -> dict[str, Any]:
    return {"type": "traffic", "kind": kind, "level": level, "title": title, "reason": reason, "stats": stats,
            "best": best, "day": day["day"] if day else None, "district": norm_district(district),
            "crop": (norm_crop(crop) or crop) if crop else None, **extra}


# ---- watering (rain vs the crop's water use) ---------------------------------------------------------

def water_card(district: str, crop: str) -> dict[str, Any]:
    """Today + tomorrow: rain against the water the crop loses (FAO reference evapotranspiration), and soil moisture.
    RED = don't water, GREEN = water today."""
    days = forecast(district, 2)
    rain = round(sum(d["rain_mm"] for d in days), 1)
    et = round(sum(d["et0_mm"] for d in days), 1)
    soil = days[0]["soil"]
    st = soil_state(soil)
    if rain >= 10:
        level, why = "RED", both(lambda lg: t(lg, "water.why.RED", rain=rain))
    elif st in ("wet", "flooded"):
        level, why = "RED", both(lambda lg: t(lg, "water.why.wet"))
    elif et - rain >= 4 and st in ("dry", "moist"):
        level, why = "GREEN", both(lambda lg: t(lg, "water.why.balance", et=et, rain=rain))
    else:
        level, why = "YELLOW", both(lambda lg: t(lg, "water.why.check", rain=rain, et=et, soil=t(lg, f"soil.{st}")))
    return traffic("water", level, both(lambda lg: t(lg, f"water.{level}")), why,
                   [stat("lbl.rain2", f"{rain} mm"), stat("lbl.et", f"{et} mm"), soil_stat(soil)], district, crop,
                   rain_mm=rain, rain_chance=max(d["rain_chance"] for d in days), wind_kmh=days[0]["wind_kmh"])


# ---- fertilizer, sowing, ploughing -------------------------------------------------------------------

def _rain2(days: list[dict], d: dict) -> float:
    return round(sum(x["rain_mm"] for x in after(days, d, 2)), 1)


def fert_level(days: list[dict], d: dict) -> tuple[str, str]:
    r2 = _rain2(days, d)
    if soil_state(d["soil"]) == "flooded":
        return "RED", "fert.why.flooded"
    if r2 >= 25 or d["rain_mm"] >= 15:
        return "RED", "fert.why.RED"
    if r2 >= 10:
        return "YELLOW", "fert.why.YELLOW"
    return "GREEN", "fert.why.GREEN"


def fert_card(district: str, crop: str) -> dict[str, Any]:
    days = forecast(district)
    d = target(days)
    level, why = fert_level(days, d)
    r2 = _rain2(days, d)
    best = next((x for x in days[days.index(d):] if fert_level(days, x)[0] == "GREEN"), None)
    return traffic("fert", level, both(lambda lg: t(lg, f"fert.{level}", day=dword(d, lg))),
                   both(lambda lg: t(lg, why, rain=r2)), [stat("lbl.rain2", f"{r2} mm"), soil_stat(d["soil"])],
                   district, crop, day=d,
                   best=None if level == "GREEN" else both(lambda lg: t(lg, "fert.best", when=best["day"][lg]) if best
                                                           else t(lg, "fert.none")))


def sow_card(district: str, crop: str) -> dict[str, Any]:
    days = forecast(district)
    d = target(days)
    r2, st = _rain2(days, d), soil_state(d["soil"])
    if st == "flooded":
        level, why = "RED", "sow.why.flooded"
    elif r2 >= 35:
        level, why = "RED", "sow.why.RED"
    elif st == "dry" and r2 < 5:
        level, why = "YELLOW", "sow.why.dry"
    elif r2 >= 20:
        level, why = "YELLOW", "sow.why.rain"
    else:
        level, why = "GREEN", "sow.why.GREEN"
    return traffic("sow", level, both(lambda lg: t(lg, f"sow.{level}", day=dword(d, lg))),
                   both(lambda lg: t(lg, why, rain=r2)), [stat("lbl.rain2", f"{r2} mm"), soil_stat(d["soil"])],
                   district, crop, day=d)


def plough_card(district: str, crop: str | None = None) -> dict[str, Any]:
    days = forecast(district)
    d = target(days)
    st = soil_state(d["soil"])
    if st in ("wet", "flooded"):
        level, why = "RED", "plough.why.wet"
    elif d["rain_mm"] >= 10:
        level, why = "RED", "plough.why.rain"
    elif (d["soil"] is not None and d["soil"] < 0.12) or d["rain_mm"] >= 3:
        level, why = "YELLOW", ("plough.why.dry" if d["rain_mm"] < 3 else "plough.why.rain")
    else:
        level, why = "GREEN", "plough.why.GREEN"
    return traffic("plough", level, both(lambda lg: t(lg, f"plough.{level}", day=dword(d, lg))),
                   both(lambda lg: t(lg, why, rain=d["rain_mm"])), [stat("lbl.rain", f"{d['rain_mm']} mm"), soil_stat(d["soil"])],
                   district, None, day=d)


# ---- harvest and drying ------------------------------------------------------------------------------

def _dry_day(d: dict) -> bool:
    return d["rain_mm"] < 2 and d["rain_chance"] < 50


def harvest_card(district: str, crop: str) -> dict[str, Any]:
    days = forecast(district)
    d = target(days)
    rest = days[days.index(d):]
    start = next((k for k in range(len(rest) - 1) if _dry_day(rest[k]) and _dry_day(rest[k + 1])), None)
    total = round(sum(x["rain_mm"] for x in days), 1)
    stats = [stat("lbl.rain", f"{d['rain_mm']} mm"), stat("lbl.chance", f"{d['rain_chance']}%")]
    if start == 0:
        r1, r2 = rest[0]["rain_mm"], rest[1]["rain_mm"]
        return traffic("harvest", "GREEN", both(lambda lg: t(lg, "harvest.GREEN", day=dword(d, lg))),
                       both(lambda lg: t(lg, "harvest.why.GREEN", r1=r1, r2=r2)), stats, district, crop, day=d)
    if start is not None:
        w = rest[start]
        return traffic("harvest", "YELLOW", both(lambda lg: t(lg, "harvest.YELLOW", when=w["day"][lg])),
                       both(lambda lg: t(lg, "harvest.why.YELLOW", rain=d["rain_mm"], day=dword(d, lg))), stats,
                       district, crop, day=d)
    return traffic("harvest", "RED", both(lambda lg: t(lg, "harvest.RED")),
                   both(lambda lg: t(lg, "harvest.why.RED", total=total)), stats, district, crop, day=d)


def dry_level(d: dict) -> str:
    rh = d["rh_day"] if d["rh_day"] is not None else 80
    if d["rain_mm"] < 1 and d["sun_h"] >= 6 and rh < 75:
        return "GREEN"
    if d["rain_mm"] < 3 and d["sun_h"] >= 3:
        return "YELLOW"
    return "RED"


def drying_card(district: str, crop: str) -> dict[str, Any]:
    days = forecast(district)
    d = target(days)
    level = dry_level(d)
    rh = d["rh_day"] if d["rh_day"] is not None else 80
    best = next((x for x in days[days.index(d):] if dry_level(x) == "GREEN"), None)
    return traffic("dry", level, both(lambda lg: t(lg, f"dry.{level}", day=dword(d, lg))),
                   both(lambda lg: t(lg, f"dry.why.{level}", sun=d["sun_h"], rh=rh, rain=d["rain_mm"])),
                   [stat("lbl.sun", f"{d['sun_h']} h"), stat("lbl.humid", f"{rh}%"), stat("lbl.rain", f"{d['rain_mm']} mm")],
                   district, crop, day=d,
                   best=None if level == "GREEN" else both(lambda lg: t(lg, "dry.best", when=best["day"][lg]) if best
                                                           else t(lg, "dry.none")))


# ---- drainage, disease, heat, cattle, storm ---------------------------------------------------------

def drain_card(district: str, crop: str | None = None) -> dict[str, Any]:
    days = forecast(district, 3)
    r3 = round(sum(d["rain_mm"] for d in days), 1)
    wet = soil_state(days[0]["soil"]) in ("wet", "flooded")
    level = "RED" if r3 >= 50 or (wet and r3 >= 20) else "YELLOW" if r3 >= 25 else "GREEN"
    return traffic("drain", level, both(lambda lg: t(lg, f"drain.{level}")),
                   both(lambda lg: t(lg, f"drain.why.{level}", rain=r3) + (t(lg, "drain.why.wet") if wet and level != "GREEN" else "")),
                   [stat("lbl.rain3", f"{r3} mm"), soil_stat(days[0]["soil"])], district)


def _next_hours(district: str, n: int = 48) -> list[dict]:
    now = now_ist().hour
    hours = []
    for d in forecast(district, 3):
        hours += [x for x in d["hours"] if d["i"] > 0 or x["h"] >= now]
    return hours[:n]


def disease_card(district: str, crop: str) -> dict[str, Any]:
    hours = _next_hours(district)
    n = sum(1 for x in hours if x["rh"] >= 90 and 18 <= x["temp"] <= 30)
    level = "RED" if n >= 20 else "YELLOW" if n >= 10 else "GREEN"
    rh = round(max((x["rh"] for x in hours), default=0))
    return traffic("disease", level, both(lambda lg: t(lg, f"disease.{level}")),
                   both(lambda lg: t(lg, f"disease.why.{level}", n=n)),
                   [stat("lbl.hours", f"{n} h"), stat("lbl.humid", f"{rh}%")], district, crop)


def heat_card(district: str, crop: str | None = None) -> dict[str, Any]:
    days = forecast(district, 2)
    tmax = max(d["tmax"] for d in days)
    level = "RED" if tmax >= 38 else "YELLOW" if tmax >= 35 else "GREEN"
    return traffic("heat", level, both(lambda lg: t(lg, f"heat.{level}")),
                   both(lambda lg: t(lg, f"heat.why.{level}", t=tmax)), [stat("lbl.temp", f"{tmax}°C")], district)


def thi(temp: float, rh: float) -> float:
    """Temperature-Humidity Index for cattle (°C, %): 0.8 T + RH/100 (T - 14.4) + 46.4."""
    return 0.8 * temp + rh / 100 * (temp - 14.4) + 46.4


def cattle_card(district: str, crop: str | None = None) -> dict[str, Any]:
    hours = _next_hours(district)
    top = round(max((thi(x["temp"], x["rh"]) for x in hours), default=70))
    level = "RED" if top >= 89 else "YELLOW" if top >= 72 else "GREEN"  # THI bands: <72 none, 72-88 mild-moderate, 89+ severe
    return traffic("cattle", level, both(lambda lg: t(lg, f"cattle.{level}")),
                   both(lambda lg: t(lg, f"cattle.why.{level}", thi=top)), [stat("lbl.thi", str(top))], district)


def storm_card(district: str, crop: str | None = None) -> dict[str, Any]:
    days = forecast(district, 2)
    now = now_ist().hour
    gust = round(max(d["gust_kmh"] for d in days))
    for d in days:
        storm = [x["h"] for x in d["hours"] if x["code"] >= 95 and 6 <= x["h"] <= 20 and (d["i"] > 0 or x["h"] >= now)]
        if storm:
            w = (min(storm), max(storm) + 1)
            return traffic("storm", "RED", both(lambda lg: t(lg, "storm.RED", day=dword(d, lg), window=window_label(*w, lg))),
                           both(lambda lg: t(lg, "storm.why.RED", gust=gust)), [stat("lbl.gust", f"{gust} km/h")], district, day=d)
    level = "RED" if gust >= 60 else "YELLOW" if gust >= 40 else "GREEN"
    key = "storm.RED.wind" if level == "RED" else f"storm.{level}"
    d = max(days, key=lambda x: x["gust_kmh"])
    return traffic("storm", level, both(lambda lg: t(lg, key, day=dword(d, lg))),
                   both(lambda lg: t(lg, "storm.why.YELLOW" if level != "GREEN" else "storm.why.GREEN", gust=gust)),
                   [stat("lbl.gust", f"{gust} km/h")], district)


# ---- rain: next 5 days, last 7 days --------------------------------------------------------------------

def _strip(days: list[dict]) -> list[dict]:
    return [{k: d[k] for k in ("date", "day", "icon", "text", "rain_mm", "rain_chance", "tmax", "tmin", "wind_kmh")} for d in days]


def weather_card(district: str, crop: str | None = None) -> dict[str, Any]:
    days = forecast(district)
    total = round(sum(d["rain_mm"] for d in days), 1)
    name = norm_district(district)
    return {"type": "weather", "district": name, "total_rain_mm": total,
            "title": both(lambda lg: t(lg, "weather.title", district=district_name(name, lg), total=total)),
            "days": _strip(days)}


def past_card(district: str, crop: str | None = None) -> dict[str, Any]:
    days = past(district)
    total = round(sum(d["rain_mm"] for d in days), 1)
    name = norm_district(district)
    return {"type": "past", "district": name, "total_rain_mm": total,
            "title": both(lambda lg: t(lg, "past.title", district=district_name(name, lg), total=total)), "days": _strip(days)}


# ---- the weekly plan ------------------------------------------------------------------------------------

def plan_card(district: str, crop: str) -> dict[str, Any]:
    days = forecast(district)
    now = now_ist().hour
    rows = []
    for d in days:
        level, _, w = spray_level(d)
        thunder = any(x["code"] >= 95 and 6 <= x["h"] <= 20 and (d["i"] > 0 or x["h"] >= now) for x in d["hours"])
        if d["rain_mm"] >= 64.5:
            act, lv = both(lambda lg: t(lg, "act.protect")), "RED"
        elif thunder:
            act, lv = both(lambda lg: t(lg, "act.storm")), "RED"
        elif d["rain_mm"] >= 5:
            act, lv = both(lambda lg: t(lg, "act.wait")), "RED"
        elif dry_level(d) == "GREEN":
            act, lv = both(lambda lg: t(lg, "act.dry")), "GREEN"
        elif level == "GREEN":
            act, lv = both(lambda lg: t(lg, "act.spray")), "GREEN"
        elif level == "YELLOW" and w:
            act, lv = both(lambda lg, w=w: t(lg, "act.window", window=window_label(*w, lg))), "YELLOW"
        elif d["wind_kmh"] > 20:
            act, lv = both(lambda lg: t(lg, "act.wind")), "RED"
        else:
            act, lv = both(lambda lg: t(lg, "act.water")), "YELLOW"
        rows.append(_strip([d])[0] | {"level": lv, "action": act})
    best = best_spray(days)
    name = norm_district(district)
    c = norm_crop(crop) or crop
    return {"type": "plan", "district": name, "crop": c,
            "title": both(lambda lg: f"{t(lg, 'plan.title')} · {crop_name(c, lg)} · {district_name(name, lg)}"),
            "days": rows,
            "best": both(lambda lg: t(lg, "best", when=_when(best[0], best[1], lg)) if best else t(lg, "best.none"))}


def alert_for(district: str) -> dict[str, Any] | None:
    """IMD 'heavy rain' (>= 64.5 mm in a day) or wind > 40 km/h in the next 48 hours."""
    name = norm_district(district)
    for d in forecast(district, 2):
        if d["rain_mm"] >= 64.5:
            return {"level": "RED", "text": both(lambda lg: t(lg, "alert.rain", district=district_name(name, lg),
                                                              day=d["day"][lg].lower(), mm=f"{d['rain_mm']:.0f}"))}
        if d["wind_kmh"] > 40:
            return {"level": "RED", "text": both(lambda lg: t(lg, "alert.wind", district=district_name(name, lg),
                                                              day=d["day"][lg].lower(), kmh=d["wind_kmh"]))}
    return None


def summary(card: dict[str, Any]) -> dict[str, str]:
    """One or two short sentences for a card, in both languages (also what the app reads aloud)."""
    if card["type"] == "traffic":
        return both(lambda lg: f"{card['title'][lg]}. {card['reason'][lg]}" + (f" {card['best'][lg]}." if card.get("best") else ""))
    if card["type"] == "plan":
        return both(lambda lg: t(lg, "plan.ready", crop=crop_name(card["crop"], lg), district=district_name(card["district"], lg),
                                 best=card["best"][lg]))
    if card["type"] == "weather":
        d0, d1 = card["days"][0], card["days"][1]
        return both(lambda lg: t(lg, "weather.sum", district=district_name(card["district"], lg), t0=d0["text"][lg].lower(),
                                 r0=d0["rain_mm"], t1=d1["text"][lg].lower(), r1=d1["rain_mm"], total=card["total_rain_mm"]))
    if card["type"] == "past":
        wettest = max(card["days"], key=lambda x: x["rain_mm"]) if card["days"] else None
        if not wettest or card["total_rain_mm"] == 0:
            return both(lambda lg: t(lg, "past.none", district=district_name(card["district"], lg)))
        return both(lambda lg: t(lg, "past.sum", district=district_name(card["district"], lg), total=card["total_rain_mm"],
                                 day=wettest["day"][lg], max=wettest["rain_mm"]))
    if card["type"] == "photo":
        return dict(card["title"])
    return {"en": "", "ta": ""}


# ---- the tool registry: quick buttons, Strands tools, Decider guard ------------------------------------

CARDS: contextvars.ContextVar[list | None] = contextvars.ContextVar("uzhavan_cards", default=None)

# intent: (tool name, function, needs crop, group, icon, English label, Tamil label, what it answers)
REGISTRY: dict[str, tuple] = {
    "rain": ("get_forecast", weather_card, False, "weather", "🌧️", "Rain this week", "இந்த வாரம் மழை",
             "Real 5-day weather: rain mm, rain chance, temperature."),
    "past": ("past_rainfall", past_card, False, "weather", "📊", "Past rain", "கடந்த மழை",
             "How much rain fell in the last 7 days."),
    "storm": ("storm_safety", storm_card, False, "weather", "⛈️", "Storm safety", "இடி, புயல்",
              "Thunderstorm / lightning hours and strong winds today and tomorrow: is it safe to work in the field?"),
    "spray": ("spray_advice", spray_card, True, "field", "🧴", "Spraying", "மருந்து தெளிப்பு",
              "Is it safe to spray pesticide, and at what time? (dry, calm hours)"),
    "fert": ("fertilizer_timing", fert_card, True, "field", "🌱", "Fertilizer", "உரம்",
             "Good day to apply fertilizer (no heavy rain to wash it away)?"),
    "sow": ("sowing_advice", sow_card, True, "field", "🌾", "Sowing", "விதைப்பு",
            "Good time to sow or transplant (soil moisture, no heavy rain coming)?"),
    "plough": ("ploughing_advice", plough_card, False, "field", "🚜", "Ploughing", "உழவு",
               "Can the field be ploughed (soil not too wet or dry, no rain)?"),
    "harvest": ("harvest_advice", harvest_card, True, "field", "✂️", "Harvest", "அறுவடை",
                "When to harvest: the next run of dry days."),
    "dry": ("drying_advice", drying_card, True, "field", "☀️", "Drying", "உலர்த்துதல்",
            "Can produce (paddy, chilli, copra, turmeric) be sun-dried: sunshine, humidity, rain?"),
    "water": ("irrigation_advice", water_card, True, "water", "💧", "Watering", "நீர் பாய்ச்சுதல்",
              "Should the field be watered today: rain vs the crop's water use, and soil moisture."),
    "drain": ("drainage_advice", drain_card, False, "water", "🌊", "Drainage", "வடிகால்",
              "Waterlogging / flood risk in the next 3 days: clear the field drains?"),
    "disease": ("disease_risk", disease_card, True, "health", "🦠", "Disease risk", "நோய் அபாயம்",
                "Fungal disease weather risk: hours of very high humidity with warm temperatures."),
    "heat": ("heat_stress", heat_card, False, "health", "🔥", "Heat", "வெப்பம்",
             "Heat stress for crops and farm workers (max temperature)."),
    "cattle": ("cattle_heat", cattle_card, False, "health", "🐄", "Cattle", "கால்நடை",
               "Heat stress for cows and buffaloes (Temperature-Humidity Index)."),
    "plan": ("farm_plan", plan_card, True, "plan", "📅", "My week", "என் வாரம்",
             "A 5-day plan: what to do each day (spray time, wait, harvest and dry, protect)."),
}
TOOL_FUNCS = {k: (v[0], v[1]) for k, v in REGISTRY.items()}
NEEDS_CROP = {v[0] for v in REGISTRY.values() if v[2]}
GROUPS = {"weather": ("Weather", "வானிலை"), "field": ("Field work", "வயல் வேலை"), "water": ("Water", "நீர்"),
          "health": ("Health", "நலம்"), "plan": ("Plan", "திட்டம்")}


def _record(card: dict[str, Any]) -> str:
    bucket = CARDS.get()
    if bucket is not None:
        bucket.append(card)
    return json.dumps({"summary": summary(card)["en"], "level": card.get("level"), "district": card.get("district")})


def _make_tool(intent: str):
    name, fn, needs_crop, _, _, _, _, doc = REGISTRY[intent]

    if needs_crop:
        def run(district: Annotated[str, "Tamil Nadu district"], crop: Annotated[str, "the farmer's crop"]) -> str:
            try:
                return _record(fn(district, crop) | {"tool": name})
            except WeatherError as e:
                return json.dumps({"error": e.text["en"]})
    else:
        def run(district: Annotated[str, "Tamil Nadu district"]) -> str:
            try:
                return _record(fn(district, None) | {"tool": name})
            except WeatherError as e:
                return json.dumps({"error": e.text["en"]})
    run.__name__ = name
    run.__doc__ = doc
    return tool(run)


TOOLS = [_make_tool(k) for k in REGISTRY]
