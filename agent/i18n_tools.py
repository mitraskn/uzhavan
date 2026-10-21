"""English and Tamil text for the farm tools: {key: (English, Tamil)}. Merged into i18n.EN / i18n.TA."""

TOOL_TEXT = {
    # labels shown on the cards
    "lbl.rain": ("Rain", "மழை"), "lbl.chance": ("Chance", "வாய்ப்பு"), "lbl.wind": ("Wind", "காற்று"),
    "lbl.gust": ("Gusts", "காற்று வீச்சு"), "lbl.soil": ("Soil", "மண்"), "lbl.et": ("Crop water use", "பயிர் நீர் தேவை"),
    "lbl.sun": ("Sunshine", "வெயில்"), "lbl.humid": ("Humidity", "ஈரப்பதம்"), "lbl.hours": ("Humid hours", "ஈர நேரம்"),
    "lbl.temp": ("Max temp", "அதிக வெப்பம்"), "lbl.thi": ("Heat index", "வெப்பக் குறியீடு"),
    "lbl.rain2": ("Rain, 2 days", "மழை, 2 நாள்"), "lbl.rain3": ("Rain, 3 days", "மழை, 3 நாள்"),
    "lbl.total": ("Total", "மொத்தம்"),
    "soil.dry": ("dry", "காய்ந்த"), "soil.moist": ("moist", "ஈரமான"), "soil.wet": ("wet", "அதிக ஈரம்"),
    "soil.flooded": ("waterlogged", "நீர் தேங்கிய"),
    "yesterday": ("Yesterday", "நேற்று"),

    # fertilizer
    "fert.GREEN": ("Good day to apply fertilizer {day}", "{day} உரம் இட ஏற்ற நாள்"),
    "fert.YELLOW": ("Apply fertilizer with care {day}", "{day} கவனமாக உரம் இடவும்"),
    "fert.RED": ("Don't apply fertilizer {day}", "{day} உரம் இட வேண்டாம்"),
    "fert.why.GREEN": ("Little rain in the next 2 days ({rain} mm), so it stays in the soil.",
                       "அடுத்த 2 நாட்களில் மழை குறைவு ({rain} மி.மீ); உரம் மண்ணில் தங்கும்."),
    "fert.why.YELLOW": ("Some rain is coming ({rain} mm in 2 days). Light rain helps it soak in; heavy rain washes it away.",
                        "சிறிது மழை வரும் (2 நாட்களில் {rain} மி.மீ). லேசான மழை உரம் மண்ணில் இறங்க உதவும்; கனமழை கழுவிவிடும்."),
    "fert.why.RED": ("{rain} mm rain in the next 2 days will wash the fertilizer away.",
                     "அடுத்த 2 நாட்களில் {rain} மி.மீ மழை உரத்தைக் கழுவிவிடும்."),
    "fert.why.flooded": ("The field is waterlogged; fertilizer would be wasted.", "வயலில் நீர் தேங்கியுள்ளது; உரம் வீணாகும்."),
    "fert.best": ("Best day for fertilizer: {when}", "உரம் இட சிறந்த நாள்: {when}"),
    "fert.none": ("No good day for fertilizer in the next 5 days", "அடுத்த 5 நாட்களில் உரம் இட ஏற்ற நாள் இல்லை"),

    # sowing / transplanting
    "sow.GREEN": ("Good day to sow or transplant {day}", "{day} விதைக்க அல்லது நடவு செய்ய ஏற்ற நாள்"),
    "sow.YELLOW": ("Sow with care {day}", "{day} கவனமாக விதைக்கவும்"),
    "sow.RED": ("Don't sow {day}", "{day} விதைக்க வேண்டாம்"),
    "sow.why.GREEN": ("The soil is moist and no heavy rain is coming.", "மண் ஈரமாக உள்ளது, கனமழை வரவில்லை."),
    "sow.why.dry": ("The soil is dry. Water the field before sowing.", "மண் காய்ந்துள்ளது. விதைக்கும் முன் தண்ணீர் பாய்ச்சவும்."),
    "sow.why.rain": ("Moderate rain is coming ({rain} mm in 2 days); make sure the field drains well.",
                     "மிதமான மழை வரும் (2 நாட்களில் {rain} மி.மீ); வயலில் வடிகால் சரியாக உள்ளதா எனப் பார்க்கவும்."),
    "sow.why.RED": ("Heavy rain ({rain} mm in 2 days) can wash away seeds and young plants.",
                    "கனமழை (2 நாட்களில் {rain} மி.மீ) விதைகளையும் இளம் செடிகளையும் கழுவிவிடும்."),
    "sow.why.flooded": ("The field is waterlogged. Let it drain first.", "வயலில் நீர் தேங்கியுள்ளது. முதலில் நீர் வடியட்டும்."),

    # ploughing
    "plough.GREEN": ("Good day to plough {day}", "{day} உழவு செய்ய ஏற்ற நாள்"),
    "plough.YELLOW": ("Ploughing may be hard {day}", "{day} உழவு கடினமாக இருக்கலாம்"),
    "plough.RED": ("Don't plough {day}", "{day} உழ வேண்டாம்"),
    "plough.why.GREEN": ("Soil moisture is right and little rain is expected.", "மண் ஈரப்பதம் சரியாக உள்ளது, மழை குறைவு."),
    "plough.why.wet": ("The soil is too wet; ploughing now packs it hard.", "மண் மிகவும் ஈரமாக உள்ளது; இப்போது உழுதால் மண் கெட்டியாகும்."),
    "plough.why.rain": ("{rain} mm rain is expected.", "{rain} மி.மீ மழை எதிர்பார்க்கப்படுகிறது."),
    "plough.why.dry": ("The soil is very dry and hard; plough after light rain or watering.",
                       "மண் மிகவும் காய்ந்து கடினமாக உள்ளது; லேசான மழை அல்லது நீர் பாய்ச்சிய பின் உழவும்."),

    # harvest
    "harvest.GREEN": ("Good to harvest {day}", "{day} அறுவடை செய்யலாம்"),
    "harvest.YELLOW": ("Wait: harvest from {when}", "காத்திருக்கவும்: {when} முதல் அறுவடை செய்யலாம்"),
    "harvest.RED": ("Don't harvest in the next few days", "அடுத்த சில நாட்களில் அறுவடை வேண்டாம்"),
    "harvest.why.GREEN": ("The next 2 days are dry ({r1} mm, {r2} mm).", "அடுத்த 2 நாட்கள் வறண்டிருக்கும் ({r1} மி.மீ, {r2} மி.மீ)."),
    "harvest.why.YELLOW": ("Rain before that ({rain} mm {day}).", "அதற்கு முன் மழை ({day} {rain} மி.மீ)."),
    "harvest.why.RED": ("Rain on most days ({total} mm in 5 days). Keep harvested crop covered.",
                        "பெரும்பாலான நாட்களில் மழை (5 நாட்களில் {total} மி.மீ). அறுவடை செய்த பயிரை மூடி வைக்கவும்."),

    # drying produce
    "dry.GREEN": ("Good day to sun-dry {day}", "{day} வெயிலில் உலர்த்த ஏற்ற நாள்"),
    "dry.YELLOW": ("Drying will be slow {day}", "{day} உலர்த்துவது மெதுவாக இருக்கும்"),
    "dry.RED": ("Don't dry outside {day}", "{day} வெளியே உலர்த்த வேண்டாம்"),
    "dry.why.GREEN": ("{sun} hours of sun, humidity {rh}%, no rain.", "{sun} மணி நேர வெயில், ஈரப்பதம் {rh}%, மழை இல்லை."),
    "dry.why.YELLOW": ("Only {sun} hours of sun and humidity {rh}%; cover the produce if clouds come.",
                       "{sun} மணி நேர வெயில் மட்டும், ஈரப்பதம் {rh}%; மேகம் வந்தால் மூடி வைக்கவும்."),
    "dry.why.RED": ("Rain ({rain} mm) or too little sun ({sun} hours); keep the produce covered.",
                    "மழை ({rain} மி.மீ) அல்லது வெயில் குறைவு ({sun} மணி); மூடி வைக்கவும்."),
    "dry.best": ("Best day to dry: {when}", "உலர்த்த சிறந்த நாள்: {when}"),
    "dry.none": ("No good drying day in the next 5 days", "அடுத்த 5 நாட்களில் உலர்த்த ஏற்ற நாள் இல்லை"),

    # watering (upgraded)
    "water.why.balance": ("Your crop uses about {et} mm of water in 2 days, and rain gives only {rain} mm.",
                          "2 நாட்களில் பயிர் சுமார் {et} மி.மீ நீரைப் பயன்படுத்தும்; மழை {rain} மி.மீ மட்டுமே."),
    "water.why.check": ("Rain {rain} mm vs crop water use {et} mm in 2 days; the soil is {soil}.",
                        "2 நாட்களில் மழை {rain} மி.மீ, பயிர் நீர் தேவை {et} மி.மீ; மண் {soil}."),
    "water.why.wet": ("The soil is already very wet.", "மண் ஏற்கனவே மிகவும் ஈரமாக உள்ளது."),

    # drainage
    "drain.GREEN": ("No waterlogging expected", "நீர் தேங்க வாய்ப்பு இல்லை"),
    "drain.YELLOW": ("Check your field drains", "வடிகால்களைச் சரிபார்க்கவும்"),
    "drain.RED": ("Flood risk: clear field drains now", "வெள்ள அபாயம்: இப்போதே வடிகால்களைச் சுத்தம் செய்யவும்"),
    "drain.why.GREEN": ("Only {rain} mm rain in the next 3 days.", "அடுத்த 3 நாட்களில் {rain} மி.மீ மழை மட்டுமே."),
    "drain.why.YELLOW": ("{rain} mm rain expected in the next 3 days.", "அடுத்த 3 நாட்களில் {rain} மி.மீ மழை எதிர்பார்க்கப்படுகிறது."),
    "drain.why.RED": ("{rain} mm rain in the next 3 days.", "அடுத்த 3 நாட்களில் {rain} மி.மீ மழை."),
    "drain.why.wet": (" The soil is already wet.", " மண் ஏற்கனவே ஈரமாக உள்ளது."),

    # disease risk
    "disease.GREEN": ("Low disease risk", "நோய் அபாயம் குறைவு"),
    "disease.YELLOW": ("Moderate disease risk", "நோய் அபாயம் மிதமானது"),
    "disease.RED": ("High fungal disease risk", "பூஞ்சை நோய் அபாயம் அதிகம்"),
    "disease.why.GREEN": ("Only {n} very humid hours in the next 2 days.", "அடுத்த 2 நாட்களில் {n} மணி நேரம் மட்டுமே அதிக ஈரப்பதம்."),
    "disease.why.YELLOW": ("{n} very humid hours in the next 2 days. Check the leaves for spots.",
                           "அடுத்த 2 நாட்களில் {n} மணி நேரம் அதிக ஈரப்பதம். இலைகளில் புள்ளிகள் உள்ளதா எனப் பார்க்கவும்."),
    "disease.why.RED": ("{n} hours of very humid, warm weather in the next 2 days. Check the leaves every day; ask your "
                        "agriculture officer before spraying anything.",
                        "அடுத்த 2 நாட்களில் {n} மணி நேரம் அதிக ஈரப்பதம், மிதமான வெப்பம். தினமும் இலைகளைப் பார்க்கவும்; "
                        "எதையும் தெளிக்கும் முன் வேளாண் அலுவலரைக் கேளுங்கள்."),

    # heat
    "heat.GREEN": ("No heat stress", "வெப்ப அழுத்தம் இல்லை"),
    "heat.YELLOW": ("Hot days ahead", "வெப்பமான நாட்கள்"),
    "heat.RED": ("Extreme heat: protect your crop and yourself", "கடும் வெப்பம்: பயிரையும் உங்களையும் பாதுகாக்கவும்"),
    "heat.why.GREEN": ("Highest {t}°C in the next 2 days.", "அடுத்த 2 நாட்களில் அதிகபட்சம் {t}°C."),
    "heat.why.YELLOW": ("Up to {t}°C. Water in the early morning or evening; avoid field work at noon.",
                        "{t}°C வரை. அதிகாலை அல்லது மாலையில் நீர் பாய்ச்சவும்; மதிய நேர வயல் வேலையைத் தவிர்க்கவும்."),
    "heat.why.RED": ("Up to {t}°C. Water in the early morning or evening, finish field work before 11 AM, drink water often.",
                     "{t}°C வரை. அதிகாலை அல்லது மாலையில் நீர் பாய்ச்சவும், காலை 11 மணிக்குள் வயல் வேலையை முடிக்கவும், அடிக்கடி தண்ணீர் குடிக்கவும்."),

    # cattle (Temperature-Humidity Index)
    "cattle.GREEN": ("Cattle are comfortable", "கால்நடைகள் நலமாக இருக்கும்"),
    "cattle.YELLOW": ("Some heat stress for cattle", "கால்நடைகளுக்குச் சிறிது வெப்ப அழுத்தம்"),
    "cattle.RED": ("Severe heat stress for cattle", "கால்நடைகளுக்குக் கடும் வெப்ப அழுத்தம்"),
    "cattle.why.GREEN": ("Heat index up to {thi} (below 72).", "வெப்பக் குறியீடு {thi} வரை (72-க்குக் கீழ்)."),
    "cattle.why.YELLOW": ("Heat index up to {thi}. Keep shade and fresh water ready; avoid grazing at noon.",
                          "வெப்பக் குறியீடு {thi} வரை. நிழலும் சுத்தமான தண்ணீரும் தயாராக வைக்கவும்; மதிய நேர மேய்ச்சலைத் தவிர்க்கவும்."),
    "cattle.why.RED": ("Heat index up to {thi}. Give shade and plenty of water; avoid grazing from 11 AM to 4 PM.",
                       "வெப்பக் குறியீடு {thi} வரை. நிழலும் நிறைய தண்ணீரும் கொடுக்கவும்; காலை 11 முதல் மாலை 4 வரை மேய்ச்சலைத் தவிர்க்கவும்."),

    # storm and lightning
    "storm.GREEN": ("No storm expected", "புயல், இடி மழை வாய்ப்பு இல்லை"),
    "storm.YELLOW": ("Strong winds {day}", "{day} பலத்த காற்று"),
    "storm.RED": ("Thunderstorm likely {day}, {window}", "{day} {window} இடி மின்னலுடன் மழை வாய்ப்பு"),
    "storm.RED.wind": ("Very strong winds {day}", "{day} மிகப் பலத்த காற்று"),
    "storm.why.GREEN": ("Gusts up to {gust} km/h and no thunderstorm.", "காற்று வீச்சு {gust} கி.மீ/மணி வரை, இடி மழை இல்லை."),
    "storm.why.YELLOW": ("Gusts up to {gust} km/h. Support banana and sugarcane; secure sheds.",
                         "காற்று வீச்சு {gust} கி.மீ/மணி வரை. வாழை, கரும்புக்கு முட்டுக் கொடுக்கவும்; கொட்டகைகளைப் பாதுகாக்கவும்."),
    "storm.why.RED": ("Stay out of open fields and away from tall trees at that time. Gusts up to {gust} km/h.",
                      "அந்த நேரத்தில் திறந்த வயல்களிலும் உயரமான மரங்களின் கீழும் இருக்க வேண்டாம். காற்று வீச்சு {gust} கி.மீ/மணி வரை."),

    # past rainfall
    "past.title": ("{district} · last 7 days · {total} mm rain", "{district} · கடந்த 7 நாட்கள் · {total} மி.மீ மழை"),
    "past.sum": ("{district} got {total} mm rain in the last 7 days; the wettest day was {day} ({max} mm).",
                 "{district} கடந்த 7 நாட்களில் {total} மி.மீ மழை பெற்றது; அதிக மழை {day} ({max} மி.மீ)."),
    "past.none": ("{district} got no rain in the last 7 days.", "{district} கடந்த 7 நாட்களில் மழை இல்லை."),

    # weekly plan (extra actions)
    "act.dry": ("Good for harvest & drying", "அறுவடை, உலர்த்த ஏற்றது"),
    "act.storm": ("Thunderstorm: stay safe", "இடி மழை: பாதுகாப்பாக இருக்கவும்"),

    # Decider "why" line and corrections
    "why.checked": ("Decider checked", "Decider சரிபார்த்தது"),
    "why.selected": ("you selected it", "நீங்கள் தேர்ந்தெடுத்தது"),
    "why.said": ("you said it", "நீங்கள் சொன்னது"),
    "why.district": ("district", "மாவட்டம்"), "why.crop": ("crop", "பயிர்"),
    "fixed": ("The AI guessed {guess}; Decider corrected it to {value}, which you gave.",
              "AI {guess} என ஊகித்தது; நீங்கள் கொடுத்த {value} என Decider திருத்தியது."),
}
