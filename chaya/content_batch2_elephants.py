"""Science Chaya: the science of elephants, in Kerala's festivals and forests (long)."""
from chaya.content_monsoon import BL, BR, DK, GD, GR, LF, OR, RD, SE, B
from chaya.dsl import GROUND, RINGS, C, I
from chaya.quick import lab

LONG = {
    "id": "elephants_long", "orient": "wide", "mood": "curious",
    "title_ml": "ആന കാലുകൊണ്ട് കേൾക്കുമോ? ആനകളുടെ രഹസ്യ ശാസ്ത്രം",
    "title_en": "Can elephants hear with their feet? The hidden science of elephants",
    "thumb": {"ml": "ആന കാലുകൊണ്ട് കേൾക്കുമോ?", "en": "ELEPHANT SCIENCE", "hero": "compose"},
    "comment": "നിങ്ങൾ ആനകളെക്കുറിച്ച് കേട്ട ഏറ്റവും കൗതുകമുള്ള കാര്യം എന്താണ്?",
    "beats": [
        B("ആന നടക്കുമ്പോൾ ഭൂമിയിലൂടെ സന്ദേശം അയക്കും എന്ന് കേട്ടിട്ടുണ്ടോ?", ("ഭൂമിയിലൂടെ സന്ദേശം", "MESSAGES THROUGH THE GROUND", DK), C([GROUND("#c9a35e", 0.78), I("elephant", 0.5, 0.58, 8), RINGS(0.5, 0.82, "#7b4a2b", speed=0.6, r=0.5)], bg="sky")),
        B("ആനയ്ക്ക് ചെവികൊണ്ട് മാത്രമല്ല, കാലുകൊണ്ടും ശബ്ദം അറിയാൻ കഴിയും എന്ന് ഗവേഷകർ കരുതുന്നു.", ("ചെവിയും കാലും", "EARS AND FEET", SE)),
        B("ആനകൾ നമുക്ക് കേൾക്കാൻ കഴിയാത്ത വളരെ താഴ്ന്ന ശബ്ദങ്ങൾ ഉണ്ടാക്കും, അതിനെ ഇൻഫ്രാസൗണ്ട് എന്ന് പറയും.", ("ഇൻഫ്രാസൗണ്ട്", "INFRASOUND: TOO LOW FOR US TO HEAR", BL), C([I("elephant", 0.5, 0.5, 6.5), RINGS(0.5, 0.5, "#146a85", speed=0.4, r=0.6)], bg="dusk")),
        B("ആ ശബ്ദത്തിന്റെ ഒരു ഭാഗം ഭൂമിയിലൂടെ വിറയലായി സഞ്ചരിക്കും.", ("ഭൂമിയിലെ വിറയൽ", "PART OF IT TRAVELS AS A GROUND TREMOR", OR)),
        B("ആനയുടെ കാലുകളിൽ ആ വിറയൽ തിരിച്ചറിയാൻ കഴിയുന്ന പ്രത്യേക നാഡീഭാഗങ്ങളുണ്ട്.", ("കാലിലെ നാഡികൾ", "SPECIAL NERVE ENDINGS IN THE FEET", RD)),
        B("ദൂരെയുള്ള ആനയുടെ വിളി ശ്രദ്ധിക്കുമ്പോൾ ആന കാലുകൾ നിലത്ത് അമർത്തി നിൽക്കുന്നത് കാണാം.", ("കാൽ അമർത്തി കേൾക്കുന്നു", "LISTENING WITH PRESSED FEET", GD)),
        B("ഗവേഷകരുടെ മാതൃകകൾ പറയുന്നത് ഇത്തരം ഭൂശബ്ദങ്ങൾ ഏകദേശം രണ്ട് കിലോമീറ്റർ വരെ എത്താം എന്നാണ്.", ("≈ 2 കി.മീ.", "MODELS SUGGEST ABOUT 2 KM", SE), {"kind": "stat", "p": {"value": 2, "suffix": " km", "ml": "ഭൂശബ്ദം എത്താവുന്ന ദൂരം", "en": "ESTIMATED BY RESEARCHERS", "icon": "elephant"}}),
        B("ഇതെല്ലാം ഇപ്പോഴും പഠനത്തിലാണ്, എല്ലാം ഉറപ്പായി അറിയില്ല.", ("ഇപ്പോഴും പഠനത്തിൽ", "STILL BEING STUDIED", GR)),
        B("കേരളത്തിന്റെ ഉത്സവങ്ങളിൽ ആനകൾക്ക് വലിയ സ്ഥാനമുണ്ട്.", ("ഉത്സവങ്ങളിൽ ആന", "ELEPHANTS IN KERALA'S FESTIVALS", BR), C([I("elephant", 0.3, 0.58, 6), I("chenda", 0.7, 0.55, 5, anim="shake"), GROUND("#c9a35e", 0.84)], bg="dusk")),
        B("ഉത്സവങ്ങൾ ഓഗസ്റ്റ് മുതൽ മെയ് വരെ നീളും, അഞ്ഞൂറിലധികം ഉത്സവങ്ങൾ ഉണ്ടെന്ന് റിപ്പോർട്ടുകൾ പറയുന്നു.", ("500-ലധികം ഉത്സവങ്ങൾ", "OVER 500 FESTIVALS, AUGUST TO MAY", OR)),
        B("ചെണ്ടമേളത്തിന്റെ ഉച്ചത്തിലുള്ള ശബ്ദവും ജനക്കൂട്ടവും ആനകൾക്ക് സമ്മർദ്ദമുണ്ടാക്കാം.", ("ശബ്ദവും ജനക്കൂട്ടവും", "LOUD SOUND AND CROWDS CAN STRESS THEM", RD)),
        B("കേരളത്തിലെ വളർത്താനകളുടെ എണ്ണം കുറഞ്ഞുവരുന്നു എന്ന് കോടതിയിൽ നൽകിയ കണക്കുകൾ കാണിക്കുന്നു.", ("എണ്ണം കുറയുന്നു", "THE NUMBERS ARE FALLING", GD)),
        B("രണ്ടായിരത്തി പതിനെട്ടിൽ അഞ്ഞൂറ്റി ഒൻപത്, രണ്ടായിരത്തി ഇരുപത്തിനാലിൽ മുന്നൂറ്റി എൺപത്തിയെട്ട്.", ("509 → 388", "2018 → 2024", GD), {"kind": "bars", "p": {"unit": "", "items": [{"ml": "2018", "en": "CAPTIVE ELEPHANTS", "v": 509, "col": GD}, {"ml": "2024", "en": "CAPTIVE ELEPHANTS", "v": 388, "col": RD}], "max": 560}}),
        B("കണക്കുകൾ ഓരോ റിപ്പോർട്ടിലും അല്പം വ്യത്യസ്തമാണ്, പക്ഷേ ദിശ ഒന്നുതന്നെ, എണ്ണം കുറയുന്നു.", ("എണ്ണം കുറയുന്നു", "SOURCES DIFFER, THE TREND DOES NOT", GR)),
        B("കാട്ടാനകൾ ഗ്രാമങ്ങളിലേക്ക് ഇറങ്ങുന്ന പ്രശ്നവും കേരളത്തിലുണ്ട്.", ("കാട്ടാന – മനുഷ്യ സംഘർഷം", "HUMAN-ELEPHANT CONFLICT", RD)),
        B("ആനയെ കണ്ടാൽ ബഹുമാനത്തോടെ അകലം പാലിക്കുക, അടുത്ത് ചെന്ന് ഫോട്ടോ എടുക്കരുത്.", ("അകലം പാലിക്കുക", "KEEP A SAFE DISTANCE", LF)),
        B("ആനകളെ കൂടുതൽ അറിഞ്ഞാൽ അവയെ സംരക്ഷിക്കാനും നമുക്ക് എളുപ്പമാകും.", ("അറിഞ്ഞാൽ സംരക്ഷിക്കാം", "KNOWING THEM HELPS PROTECT THEM", BR)),
        B("നിങ്ങൾ ആനകളെക്കുറിച്ച് കേട്ട ഏറ്റവും കൗതുകമുള്ള കാര്യം എന്താണ്?", None, {"kind": "outro", "p": {"ml": "ആനകളെക്കുറിച്ച് നിങ്ങൾ കേട്ട ഏറ്റവും കൗതുകമുള്ള കാര്യം എന്താണ്?", "en": "WHAT IS THE MOST INTERESTING THING YOU HEARD ABOUT ELEPHANTS?"}}),
        B("താഴെ കമന്റ് ചെയ്യൂ, ഇതുപോലുള്ള വീഡിയോകൾക്കായി സയൻസ് ചായ സബ്സ്ക്രൈബ് ചെയ്യൂ."),
    ],
}
FACTS = [
    "Researchers propose that elephants make infrasound and sense ground vibrations through their feet, which hold pressure-sensitive nerve endings; models suggest ground signals could travel about 2 km; the picture is incomplete (Stanford; Physics World; ElephantVoices).",
    "Kerala's festival season runs from August to May with over 500 festivals reported; the number of captive elephants fell from 509 in 2018 to 388 in 2024 according to figures given to the Kerala High Court; other counts differ (Deccan Herald; South First).",
]
# richer scene: a call through the air and the ground
lab(LONG, 2, 7, "seismic", {"call": 0, "ground": 1, "feet": 2, "far": 4}, [(0, "ഇൻഫ്രാസൗണ്ട്", "INFRASOUND", 300, 330), (1, "ഭൂമിയിലൂടെ വിറയൽ", "A TREMOR THROUGH THE GROUND", 520, 800), (2, "കാലിലെ നാഡികൾ", "SENSORS IN THE FEET", 860, 780), (4, "≈ 2 km വരെ?", "UP TO ABOUT 2 KM?", 510, 330)])

VIDEOS = [LONG]
