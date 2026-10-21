"""English and Tamil text for everything Uzhavan says (cards, questions, alerts, photo tips).

Fixed templates, not machine translation, so a farmer always gets the same clear words.
`t(lang, key, **values)`; lang is "en" or "ta".
"""

from __future__ import annotations

from datetime import datetime

CROP_TA = {"Paddy": "நெல்", "Banana": "வாழை", "Sugarcane": "கரும்பு", "Cotton": "பருத்தி", "Groundnut": "நிலக்கடலை",
           "Coconut": "தென்னை", "Maize": "மக்காச்சோளம்", "Turmeric": "மஞ்சள்", "Vegetables": "காய்கறி"}

DISTRICT_TA = {
    "Ariyalur": "அரியலூர்", "Chengalpattu": "செங்கல்பட்டு", "Chennai": "சென்னை", "Coimbatore": "கோயம்புத்தூர்",
    "Cuddalore": "கடலூர்", "Dharmapuri": "தருமபுரி", "Dindigul": "திண்டுக்கல்", "Erode": "ஈரோடு",
    "Kallakurichi": "கள்ளக்குறிச்சி", "Kancheepuram": "காஞ்சிபுரம்", "Kanniyakumari": "கன்னியாகுமரி", "Karur": "கரூர்",
    "Krishnagiri": "கிருஷ்ணகிரி", "Madurai": "மதுரை", "Mayiladuthurai": "மயிலாடுதுறை", "Nagapattinam": "நாகப்பட்டினம்",
    "Namakkal": "நாமக்கல்", "Nilgiris": "நீலகிரி", "Perambalur": "பெரம்பலூர்", "Pudukkottai": "புதுக்கோட்டை",
    "Ramanathapuram": "ராமநாதபுரம்", "Ranipet": "ராணிப்பேட்டை", "Salem": "சேலம்", "Sivaganga": "சிவகங்கை",
    "Tenkasi": "தென்காசி", "Thanjavur": "தஞ்சாவூர்", "Theni": "தேனி", "Thoothukudi": "தூத்துக்குடி",
    "Tiruchirappalli": "திருச்சிராப்பள்ளி", "Tirunelveli": "திருநெல்வேலி", "Tirupathur": "திருப்பத்தூர்",
    "Tiruppur": "திருப்பூர்", "Tiruvallur": "திருவள்ளூர்", "Tiruvannamalai": "திருவண்ணாமலை", "Tiruvarur": "திருவாரூர்",
    "Vellore": "வேலூர்", "Viluppuram": "விழுப்புரம்", "Virudhunagar": "விருதுநகர்",
}

WEEKDAY_TA = ["திங்கள்", "செவ்வாய்", "புதன்", "வியாழன்", "வெள்ளி", "சனி", "ஞாயிறு"]

# WMO weather code -> (icon, English, Tamil)
WMO = {0: ("☀️", "Clear", "வெயில்"), 1: ("🌤️", "Mostly clear", "பெரும்பாலும் வெயில்"), 2: ("⛅", "Partly cloudy", "சிறிது மேகம்"),
       3: ("☁️", "Cloudy", "மேகமூட்டம்"), 45: ("🌫️", "Fog", "பனிமூட்டம்"), 48: ("🌫️", "Fog", "பனிமூட்டம்"),
       51: ("🌦️", "Light drizzle", "லேசான தூறல்"), 53: ("🌦️", "Drizzle", "தூறல்"), 55: ("🌦️", "Heavy drizzle", "அதிக தூறல்"),
       61: ("🌧️", "Light rain", "லேசான மழை"), 63: ("🌧️", "Rain", "மழை"), 65: ("🌧️", "Heavy rain", "கனமழை"),
       80: ("🌦️", "Showers", "விட்டு விட்டு மழை"), 81: ("🌧️", "Showers", "விட்டு விட்டு மழை"),
       82: ("⛈️", "Heavy showers", "பலத்த மழை"), 95: ("⛈️", "Thunderstorm", "இடியுடன் மழை"),
       96: ("⛈️", "Thunderstorm", "இடியுடன் மழை"), 99: ("⛈️", "Thunderstorm", "இடியுடன் மழை")}

EN = {
    "today": "Today", "tomorrow": "Tomorrow",
    "spray.GREEN": "Safe to spray today", "spray.YELLOW": "Spray only {window} today",
    "spray.YELLOW.care": "Spray with care today", "spray.RED": "Don't spray today",
    "spray.GREEN.tmrw": "Safe to spray tomorrow", "spray.YELLOW.tmrw": "Spray tomorrow, only {window}",
    "spray.YELLOW.care.tmrw": "Spray with care tomorrow", "spray.RED.tmrw": "Don't spray tomorrow",
    "spray.why.rain.tmrw": "{rain} mm rain will wash the spray away, and there is no dry, calm window tomorrow.",
    "spray.late": "Too late to spray today. ",
    "spray.why.dry": "Dry and calm all day.", "spray.why.window": "Dry and calm then; rain or wind later ({rain} mm in the day).",
    "spray.why.rain": "{rain} mm rain will wash the spray away, and there is no dry, calm window today.",
    "spray.why.wind": "Wind up to {wind} km/h will blow the spray away.",
    "spray.why.chance": "{chance}% chance of rain; spray early in the morning.",
    "spray.why.breezy": "Breezy (up to {wind} km/h); spray early in the morning when it is calm.",
    "best": "Best time to spray: {when}", "best.none": "No safe time to spray in the next 5 days",
    "water.GREEN": "Water today", "water.YELLOW": "Water only if the soil is dry", "water.RED": "Don't water today",
    "water.why.GREEN": "Almost no rain expected ({rain} mm in two days).",
    "water.why.YELLOW": "Light rain expected ({rain} mm in two days).",
    "water.why.RED": "{rain} mm rain expected today and tomorrow will water your field.",
    "plan.title": "5-day plan", "plan.ready": "Your 5-day plan for {crop} in {district} is ready. {best}.",
    "act.protect": "Protect harvest, drain field", "act.wait": "Wait (rain)", "act.wind": "No spraying (wind)",
    "act.spray": "Spray OK", "act.window": "Spray {window}", "act.water": "Water if soil is dry", "act.light": "Light work only",
    "weather.title": "{district} · next 5 days · {total} mm rain",
    "weather.sum": "{district}: today {t0} ({r0} mm), tomorrow {t1} ({r1} mm). About {total} mm in 5 days.",
    "alert.rain": "Heavy rain alert: {district}, {day} ({mm} mm). Don't spray pesticide. Cover your harvested crop.",
    "alert.wind": "Strong wind alert: {district}, {day} ({kmh} km/h). Don't spray. Support banana and sugarcane.",
    "ask.district": "Which district is your farm in? Tap it on the map or tell me the name.",
    "ask.crop": "Which crop are you growing? Tap a crop button or tell me.",
    "confirm.district": "Just to check: is your farm in {district}?", "confirm.crop": "Just to check: are you growing {crop}?",
    "deny": "I can only help with farming and weather. I can't change my rules.",
    "redirect": "I help with farming and weather: rain, spraying, watering and your weekly farm plan. What would you like to know?",
    "weather.err": "The weather service is not reachable right now. Check the internet and try again.",
    "district.unknown": "I don't know the district '{name}'. Tap your district on the map.",
    "photo.bad": "Please send a clear photo of a crop leaf.",
    "photo.bad.tip": "Hold the phone close to one leaf, in daylight, so the leaf fills the photo.",
    "photo.unsure": "Not sure what this is. Please show it to your local agriculture officer.",
    "photo.issue": "Possible issue: {label}", "photo.healthy": "Your leaf looks healthy",
}

TA = {
    "today": "இன்று", "tomorrow": "நாளை",
    "spray.GREEN": "இன்று மருந்து தெளிக்கலாம்", "spray.YELLOW": "இன்று {window} மட்டும் தெளிக்கவும்",
    "spray.YELLOW.care": "இன்று கவனமாகத் தெளிக்கவும்", "spray.RED": "இன்று மருந்து தெளிக்க வேண்டாம்",
    "spray.GREEN.tmrw": "நாளை மருந்து தெளிக்கலாம்", "spray.YELLOW.tmrw": "நாளை {window} மட்டும் தெளிக்கவும்",
    "spray.YELLOW.care.tmrw": "நாளை கவனமாகத் தெளிக்கவும்", "spray.RED.tmrw": "நாளை மருந்து தெளிக்க வேண்டாம்",
    "spray.why.rain.tmrw": "{rain} மி.மீ மழை மருந்தைக் கழுவிவிடும்; நாளை தெளிக்க ஏற்ற நேரம் இல்லை.",
    "spray.late": "இன்று தெளிக்க நேரம் கடந்துவிட்டது. ",
    "spray.why.dry": "நாள் முழுவதும் வறண்ட, அமைதியான வானிலை.",
    "spray.why.window": "அந்த நேரத்தில் மழை, காற்று இல்லை; பிறகு மழை வரலாம் (நாளில் {rain} மி.மீ).",
    "spray.why.rain": "{rain} மி.மீ மழை மருந்தைக் கழுவிவிடும்; இன்று தெளிக்க ஏற்ற நேரம் இல்லை.",
    "spray.why.wind": "{wind} கி.மீ/மணி வேகக் காற்று மருந்தைச் சிதறடிக்கும்.",
    "spray.why.chance": "மழை வாய்ப்பு {chance}%; அதிகாலையில் தெளிக்கவும்.",
    "spray.why.breezy": "காற்று அதிகம் ({wind} கி.மீ/மணி வரை); அமைதியான அதிகாலையில் தெளிக்கவும்.",
    "best": "தெளிக்க சிறந்த நேரம்: {when}", "best.none": "அடுத்த 5 நாட்களில் தெளிக்க ஏற்ற நேரம் இல்லை",
    "water.GREEN": "இன்று தண்ணீர் பாய்ச்சலாம்", "water.YELLOW": "மண் காய்ந்திருந்தால் மட்டும் தண்ணீர் பாய்ச்சவும்",
    "water.RED": "இன்று தண்ணீர் பாய்ச்ச வேண்டாம்",
    "water.why.GREEN": "இரண்டு நாட்களில் மழை கிட்டத்தட்ட இல்லை ({rain} மி.மீ).",
    "water.why.YELLOW": "லேசான மழை எதிர்பார்க்கப்படுகிறது (இரண்டு நாட்களில் {rain} மி.மீ).",
    "water.why.RED": "இன்றும் நாளையும் {rain} மி.மீ மழை உங்கள் வயலுக்குத் தண்ணீர் தரும்.",
    "plan.title": "5 நாள் திட்டம்", "plan.ready": "{district} மாவட்டத்தில் {crop} பயிருக்கான 5 நாள் திட்டம் தயார். {best}.",
    "act.protect": "அறுவடையைப் பாதுகாக்கவும், வடிகால் செய்யவும்", "act.wait": "காத்திருக்கவும் (மழை)",
    "act.wind": "தெளிக்க வேண்டாம் (காற்று)", "act.spray": "தெளிக்கலாம்", "act.window": "{window} தெளிக்கலாம்",
    "act.water": "மண் காய்ந்தால் தண்ணீர்", "act.light": "லேசான வேலை மட்டும்",
    "weather.title": "{district} · அடுத்த 5 நாட்கள் · {total} மி.மீ மழை",
    "weather.sum": "{district}: இன்று {t0} ({r0} மி.மீ), நாளை {t1} ({r1} மி.மீ). 5 நாட்களில் சுமார் {total} மி.மீ.",
    "alert.rain": "கனமழை எச்சரிக்கை: {district}, {day} ({mm} மி.மீ). மருந்து தெளிக்க வேண்டாம். அறுவடை செய்த பயிரை மூடி வைக்கவும்.",
    "alert.wind": "பலத்த காற்று எச்சரிக்கை: {district}, {day} ({kmh} கி.மீ/மணி). மருந்து தெளிக்க வேண்டாம். வாழை, கரும்புக்கு முட்டுக் கொடுக்கவும்.",
    "ask.district": "உங்கள் வயல் எந்த மாவட்டத்தில் உள்ளது? வரைபடத்தில் தட்டவும் அல்லது பெயரைச் சொல்லவும்.",
    "ask.crop": "என்ன பயிர் வளர்க்கிறீர்கள்? பயிர் பொத்தானைத் தட்டவும் அல்லது சொல்லவும்.",
    "confirm.district": "சரிபார்க்க: உங்கள் வயல் {district} மாவட்டத்தில் உள்ளதா?",
    "confirm.crop": "சரிபார்க்க: நீங்கள் {crop} வளர்க்கிறீர்களா?",
    "deny": "நான் விவசாயம் மற்றும் வானிலை பற்றி மட்டுமே உதவுவேன். என் விதிகளை மாற்ற முடியாது.",
    "redirect": "நான் விவசாயம் மற்றும் வானிலைக்கு உதவுகிறேன்: மழை, மருந்து தெளித்தல், தண்ணீர் பாய்ச்சுதல், வாரத் திட்டம். என்ன தெரிந்து கொள்ள வேண்டும்?",
    "weather.err": "இப்போது வானிலை சேவையை அணுக முடியவில்லை. இணையத்தைச் சரிபார்த்து மீண்டும் முயற்சிக்கவும்.",
    "district.unknown": "'{name}' மாவட்டம் எனக்குத் தெரியவில்லை. வரைபடத்தில் உங்கள் மாவட்டத்தைத் தட்டவும்.",
    "photo.bad": "பயிர் இலையின் தெளிவான புகைப்படத்தை அனுப்பவும்.",
    "photo.bad.tip": "ஒரு இலை புகைப்படம் முழுவதும் தெரியும்படி, பகல் வெளிச்சத்தில், போனை அருகில் பிடிக்கவும்.",
    "photo.unsure": "சரியாகத் தெரியவில்லை. உங்கள் வேளாண் அலுவலரிடம் காட்டவும்.",
    "photo.issue": "இருக்கக்கூடிய பிரச்சனை: {label}", "photo.healthy": "உங்கள் இலை ஆரோக்கியமாக உள்ளது",
}

PHOTO_LABELS = {
    "en": {"healthy": "Looks healthy", "yellowing": "Yellowing leaves", "spots": "Spots on the leaves",
           "pest_damage": "Possible pest damage", "wilting": "Drying or wilting"},
    "ta": {"healthy": "ஆரோக்கியமாக உள்ளது", "yellowing": "இலைகள் மஞ்சளாகின்றன", "spots": "இலைகளில் புள்ளிகள்",
           "pest_damage": "பூச்சி சேதம்", "wilting": "இலை காய்தல் அல்லது வாடுதல்"},
}

PHOTO_TIPS = {
    "en": {
        "healthy": ["Keep your normal watering and feeding schedule.", "Check the underside of a few leaves every week."],
        "yellowing": ["Yellow leaves are often a sign of too much water or too little nitrogen.",
                      "Check that water is not standing around the plants for days.",
                      "A soil test at your local agriculture office tells you what fertiliser is needed."],
        "spots": ["Spots can be a fungal or bacterial disease.", "Remove badly spotted leaves and keep the field clean.",
                  "Do not spray before rain; check the spray advice first."],
        "pest_damage": ["Look for insects under the leaves early in the morning.", "Remove and destroy badly damaged leaves.",
                        "Spray only in a safe spray time, and only what the agriculture officer recommends."],
        "wilting": ["Check if the soil is dry; water in the early morning or evening.",
                    "If the soil is wet and plants still wilt, the roots may be diseased."],
    },
    "ta": {
        "healthy": ["வழக்கமான நீர் மற்றும் உர அட்டவணையைத் தொடரவும்.", "வாரம் ஒருமுறை சில இலைகளின் அடிப்பகுதியைப் பார்க்கவும்."],
        "yellowing": ["இலை மஞ்சளாவது பெரும்பாலும் அதிக நீர் அல்லது தழைச்சத்து குறைவால் வரும்.",
                      "செடிகளைச் சுற்றி நாட்கணக்கில் நீர் தேங்காமல் பார்க்கவும்.",
                      "என்ன உரம் தேவை என்று அறிய வேளாண் அலுவலகத்தில் மண் பரிசோதனை செய்யவும்."],
        "spots": ["புள்ளிகள் பூஞ்சை அல்லது பாக்டீரியா நோயாக இருக்கலாம்.",
                  "அதிகம் பாதிக்கப்பட்ட இலைகளை அகற்றி வயலைச் சுத்தமாக வைக்கவும்.",
                  "மழைக்கு முன் தெளிக்க வேண்டாம்; முதலில் தெளிப்பு ஆலோசனையைப் பார்க்கவும்."],
        "pest_damage": ["அதிகாலையில் இலைகளின் அடியில் பூச்சிகள் உள்ளதா எனப் பார்க்கவும்.",
                        "அதிகம் சேதமடைந்த இலைகளை அகற்றி அழிக்கவும்.",
                        "தெளிக்க ஏற்ற நேரத்தில் மட்டும், வேளாண் அலுவலர் பரிந்துரைத்ததை மட்டும் தெளிக்கவும்."],
        "wilting": ["மண் காய்ந்துள்ளதா எனப் பார்க்கவும்; அதிகாலை அல்லது மாலையில் நீர் பாய்ச்சவும்.",
                    "மண் ஈரமாக இருந்தும் செடி வாடினால், வேர் நோய் இருக்கலாம்."],
    },
}


def lang_of(lang: str | None) -> str:
    return "ta" if (lang or "").lower().startswith("ta") else "en"


def t(lang: str, key: str, **v) -> str:
    table = TA if lang_of(lang) == "ta" else EN
    return (table.get(key) or EN[key]).format(**v)


def district_name(name: str | None, lang: str) -> str:
    return (DISTRICT_TA.get(name or "", name) if lang_of(lang) == "ta" else name) or ""


def crop_name(name: str | None, lang: str) -> str:
    return (CROP_TA.get(name or "", name) if lang_of(lang) == "ta" else name) or ""


def day_name(iso: str, i: int, lang: str) -> str:
    if i == 0:
        return t(lang, "today")
    if i == 1:
        return t(lang, "tomorrow")
    if i == -1:
        return t(lang, "yesterday")
    d = datetime.strptime(iso, "%Y-%m-%d")
    return WEEKDAY_TA[d.weekday()] if lang_of(lang) == "ta" else d.strftime("%a %d %b")


def hour_label(h: int, lang: str) -> str:
    if lang_of(lang) == "ta":
        part = "அதிகாலை" if h < 6 else "காலை" if h < 12 else "மதியம்" if h < 16 else "மாலை" if h < 19 else "இரவு"
        return f"{part} {h % 12 or 12}"
    return f"{h % 12 or 12} {'AM' if h < 12 else 'PM'}"


def window_label(start: int, end: int, lang: str) -> str:
    """7..11 -> '7 AM–11 AM' / 'காலை 7–காலை 11 மணி'."""
    if lang_of(lang) == "ta":
        return f"{hour_label(start, lang)}–{hour_label(end, lang)} மணி"
    return f"{hour_label(start, lang)}–{hour_label(end, lang)}"


from .i18n_tools import TOOL_TEXT  # noqa: E402

for _k, (_en, _ta) in TOOL_TEXT.items():
    EN.setdefault(_k, _en)
    TA.setdefault(_k, _ta)
