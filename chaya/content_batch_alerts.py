"""Science Chaya: weather alerts and cyclonic circulation (long) explained for Kerala."""
from chaya.content_monsoon import BL, BR, DK, GR, LF, OR, RD, SE, B
from chaya.dsl import GROUND, LB, PT, SPIRAL, C, I, O, R, T

YEL = "#d9a21b"
LONG = {
    "id": "alerts_long", "orient": "wide", "mood": "curious",
    "title_ml": "ഓറഞ്ച് അലർട്ട്, ചക്രവാതച്ചുഴി: ടിവിയിൽ കേൾക്കുന്ന വാക്കുകളുടെ അർത്ഥം",
    "title_en": "Orange alert, cyclonic circulation: what Kerala's weather news words really mean",
    "thumb": {"ml": "ഓറഞ്ച് അലർട്ട് എന്നാൽ?", "en": "WEATHER ALERTS EXPLAINED", "hero": "compose"},
    "comment": "നിങ്ങളുടെ ജില്ലയിൽ ഈ വർഷം ഏറ്റവും കൂടുതൽ കണ്ട അലർട്ട് ഏത് നിറമായിരുന്നു?",
    "beats": [
        B("മഴക്കാലത്ത് ടിവിയിൽ കേൾക്കാറില്ലേ, ഇന്ന് ഓറഞ്ച് അലർട്ട്, നാളെ റെഡ് അലർട്ട്?", ("അലർട്ട് നിറങ്ങൾ", "WHAT DO THE COLOURS MEAN?", DK),
          C([O(0.28, 0.5, 0.17, YEL, pulse=True), O(0.5, 0.5, 0.17, "#e8731d", pulse=True, atb=0.4), O(0.72, 0.5, 0.17, "#c8442f", pulse=True, atb=0.8), T("മഞ്ഞ", 0.28, 0.82, 80, atb=0.4), T("ഓറഞ്ച്", 0.5, 0.82, 80, atb=0.8), T("ചുവപ്പ്", 0.72, 0.82, 80, atb=1.2)], bg="warm")),
        B("ഈ നിറങ്ങൾ വെറുതെ ഇടുന്നതല്ല, അതിന് കൃത്യമായ കണക്കുണ്ട്.", ("നിറത്തിന് കണക്കുണ്ട്", "THE COLOURS FOLLOW NUMBERS", BR)),
        B("ഇത് തീരുമാനിക്കുന്നത് ഇന്ത്യൻ കാലാവസ്ഥാ വകുപ്പാണ്, അതായത് ഐഎംഡി.", ("ഐഎംഡി", "INDIA METEOROLOGICAL DEPARTMENT", BL), C([T("IMD", 0.5, 0.45, 220, BL), T("ഇന്ത്യൻ കാലാവസ്ഥാ വകുപ്പ്", 0.5, 0.75, 70)], bg="warm")),
        B("അവർ നോക്കുന്നത് ഇരുപത്തിനാല് മണിക്കൂറിൽ എത്ര മഴ പെയ്യും എന്നാണ്.", ("24 മണിക്കൂറിലെ മഴ", "RAIN IN 24 HOURS", SE), C([I("cloudDark", 0.5, 0.2, 5), PT("rain", 70, [0.25, 0.3, 0.75, 0.85], "#4aa3d8", 5), GROUND("#6b8f4e", 0.86), I("thermo", 0.2, 0.62, 3.2, label=LB("24 മണിക്കൂർ", "24 HOURS", SE, 330))], bg="storm")),
        B("ഒരു ദിവസം അറുപത്തിനാലര മുതൽ നൂറ്റി പതിനഞ്ചര മില്ലിമീറ്റർ വരെ പെയ്താൽ ശക്തമായ മഴ, മഞ്ഞ അലർട്ട്.", ("മഞ്ഞ: 64.5–115.5 mm", "HEAVY RAIN", YEL),
          {"kind": "bars", "p": {"unit": "mm", "items": [{"ml": "മഞ്ഞ അലർട്ട്", "en": "YELLOW", "v": 115.5, "col": YEL}, {"ml": "ഓറഞ്ച് അലർട്ട്", "en": "ORANGE", "v": 204.4, "col": "#e8731d"}, {"ml": "റെഡ് അലർട്ട്", "en": "RED", "v": 260, "col": "#c8442f"}], "max": 280}}),
        B("നൂറ്റി പതിനഞ്ചര മുതൽ ഇരുനൂറ്റി നാലര വരെയാണെങ്കിൽ അതിശക്തമായ മഴ, ഓറഞ്ച് അലർട്ട്.", ("ഓറഞ്ച്: 115.6–204.4 mm", "VERY HEAVY RAIN", "#e8731d")),
        B("ഇരുനൂറ്റി നാലര മില്ലിമീറ്ററിൽ കൂടിയാൽ അതിതീവ്ര മഴ, റെഡ് അലർട്ട്.", ("റെഡ്: 204.4 mm മുതൽ", "EXTREMELY HEAVY RAIN", RD)),
        B("ഒരു മില്ലിമീറ്റർ മഴ എന്നാൽ ഒരു ചതുരശ്ര മീറ്ററിൽ ഒരു ലിറ്റർ വെള്ളമാണ്.", ("1 mm = 1 ലിറ്റർ / m²", "ONE MILLIMETRE IS ONE LITRE PER SQUARE METRE", SE),
          C([R(0.3, 0.2, 0.4, 0.55, "#e9f4fb", stroke="#4a2a17", sw=6), PT("rain", 30, [0.3, 0.05, 0.7, 0.7], "#4aa3d8", 6), T("1 m²", 0.5, 0.88, 90), I("drop", 0.5, 0.5, 4, label=LB("1 ലിറ്റർ", "1 LITRE", SE, 300))], bg="warm")),
        B("അതായത് ഇരുനൂറ് മില്ലിമീറ്റർ പെയ്താൽ മുറ്റത്തെ ഓരോ ചതുരശ്ര മീറ്ററിലും ഇരുനൂറ് ലിറ്റർ വെള്ളം വീഴും.", ("200 mm = 200 ലിറ്റർ", "IN EVERY SQUARE METRE", SE),
          {"kind": "stat", "p": {"value": 200, "suffix": " L", "ml": "ഓരോ ചതുരശ്ര മീറ്ററിലും", "en": "AT 200 MM OF RAIN", "icon": "drop"}}),
        B("നിറത്തിന്റെ അർത്ഥം മഴയുടെ അളവ് മാത്രമല്ല, എന്ത് ചെയ്യണം എന്ന് കൂടിയാണ്.", ("എന്ത് ചെയ്യണം?", "WHAT SHOULD YOU DO?", DK)),
        B("മഞ്ഞ അലർട്ട് എന്നാൽ ശ്രദ്ധിക്കുക.", ("മഞ്ഞ: ശ്രദ്ധിക്കുക", "BE AWARE", YEL), C([O(0.5, 0.45, 0.2, YEL, pulse=True), T("ശ്രദ്ധിക്കുക", 0.5, 0.85, 100)], bg="warm")),
        B("ഓറഞ്ച് അലർട്ട് എന്നാൽ തയ്യാറായിരിക്കുക.", ("ഓറഞ്ച്: തയ്യാറാകുക", "BE PREPARED", "#e8731d"), C([O(0.5, 0.45, 0.2, "#e8731d", pulse=True), T("തയ്യാറായിരിക്കുക", 0.5, 0.85, 100)], bg="warm")),
        B("റെഡ് അലർട്ട് എന്നാൽ നടപടി എടുക്കുക.", ("റെഡ്: നടപടി എടുക്കുക", "TAKE ACTION", RD), C([O(0.5, 0.45, 0.2, RD, pulse=True), T("നടപടി എടുക്കുക", 0.5, 0.85, 100)], bg="warm")),
        B("ഇത് ജില്ല അനുസരിച്ച് ഓരോ ദിവസവും മാറും.", ("ജില്ല തിരിച്ച്", "IT CHANGES BY DISTRICT AND BY DAY", GR)),
        B("അതുകൊണ്ട് നിങ്ങളുടെ ജില്ലയുടെ നിറം തന്നെ നോക്കണം.", ("നിങ്ങളുടെ ജില്ല", "CHECK YOUR OWN DISTRICT", LF), {"kind": "text", "p": {"ml": "നിങ്ങളുടെ ജില്ല", "en": "CHECK YOUR OWN DISTRICT'S COLOUR", "icon": "house", "col": LF}}),
        B("ഇനി മറ്റൊരു വാക്ക്: ചക്രവാതച്ചുഴി.", ("ചക്രവാതച്ചുഴി", "CYCLONIC CIRCULATION", DK), C([SPIRAL(0.5, 0.5, 0.4), T("ചക്രവാതച്ചുഴി", 0.5, 0.93, 90, "#2a1a10")])),
        B("അന്തരീക്ഷത്തിൽ കാറ്റ് ഒരു ചുഴി പോലെ കറങ്ങുന്ന ഭാഗമാണ് ഇത്.", ("കറങ്ങുന്ന കാറ്റ്", "WIND SPINNING AROUND A CENTRE", SE)),
        B("വടക്കൻ അർദ്ധഗോളത്തിൽ ഈ കാറ്റ് എതിർ ഘടികാര ദിശയിൽ ചുറ്റും.", ("എതിർ ഘടികാര ദിശയിൽ", "ANTI-CLOCKWISE IN THE NORTH", BL)),
        B("ഈ ചുഴിയുടെ നടുവിലേക്ക് ചുറ്റുമുള്ള വായു വന്ന് മുകളിലേക്ക് ഉയരും.", ("നടുവിലേക്ക് വായു", "AIR CONVERGES AND RISES", OR),
          C([SPIRAL(0.5, 0.62, 0.3, col="#ffffff"), I("cloudDark", 0.5, 0.18, 4, rise=0.0), PT("bubbles", 18, [0.42, 0.2, 0.58, 0.6], "#fff", 6)])),
        B("ഉയരുന്ന വായു തണുത്ത് മേഘമാകും, അങ്ങനെ മഴ കിട്ടും.", ("മേഘം → മഴ", "RISING AIR MAKES CLOUD AND RAIN", SE),
          C([I("cloudDark", 0.5, 0.2, 6), PT("rain", 60, [0.25, 0.3, 0.75, 0.88], "#4aa3d8", 5), GROUND("#6b8f4e", 0.88)], bg="storm")),
        B("ഇതിന്റെ വലിയ രൂപമാണ് ന്യൂനമർദ്ദം, അതായത് ലോ പ്രഷർ ഏരിയ.", ("ന്യൂനമർദ്ദം", "LOW PRESSURE AREA", DK)),
        B("കാറ്റ് കൂടുതൽ ശക്തമാകുമ്പോൾ അത് ശക്തമായ ന്യൂനമർദ്ദമാകും, പിന്നെ ഡിപ്രഷൻ, പിന്നെ ചുഴലിക്കാറ്റ്.", ("ഘട്ടങ്ങൾ", "STAGE BY STAGE", OR),
          {"kind": "flow", "p": {"carry": "water", "nodes": [{"icon": "cloud", "ml": "ചുഴി", "en": "CIRCULATION"}, {"icon": "cloudDark", "ml": "ന്യൂനമർദ്ദം", "en": "LOW PRESSURE"}, {"icon": "thermo", "ml": "ശക്തം", "en": "WELL-MARKED LOW"}, {"icon": "drop", "ml": "ഡിപ്രഷൻ", "en": "DEPRESSION"}, {"icon": "bolt", "ml": "ചുഴലിക്കാറ്റ്", "en": "CYCLONIC STORM"}]}}),
        B("ഓരോ ഘട്ടത്തിലും കാറ്റിന്റെ വേഗവും മഴയും കൂടും.", ("വേഗവും മഴയും കൂടും", "WIND AND RAIN GROW", RD)),
        B("എല്ലാ ചക്രവാതച്ചുഴിയും ചുഴലിക്കാറ്റ് ആകണമെന്നില്ല.", ("എല്ലാം ചുഴലിക്കാറ്റല്ല", "MOST NEVER BECOME STORMS", GR)),
        B("മിക്കതും ചെറിയ മഴ തന്ന് അടങ്ങിപ്പോകും.", ("ചിലത് അടങ്ങും", "MANY FADE AFTER SOME RAIN", GR)),
        B("കേരളത്തിൽ ഈ ചുഴികൾ ഒക്ടോബർ നവംബറിലെ തുലാവർഷ സമയത്ത് പ്രത്യേകം ശ്രദ്ധിക്കണം.", ("തുലാവർഷം", "WATCH THEM IN OCTOBER AND NOVEMBER", BL)),
        B("ഇനി ടിവിയിൽ ഈ വാക്കുകൾ കേട്ടാൽ നിങ്ങൾക്ക് അർത്ഥം അറിയാം.", ("ഇപ്പോൾ അറിയാം", "NOW YOU KNOW THE WORDS", LF)),
        B("ചുരുക്കി പറഞ്ഞാൽ ഒരു ചുഴി, മേഘം, മഴ, അലർട്ട്.", ("ചുരുക്കത്തിൽ", "IN SHORT", BR),
          {"kind": "flow", "p": {"carry": "water", "nodes": [{"icon": "cloud", "ml": "ചുഴി", "en": "SPIN"}, {"icon": "cloudDark", "ml": "മേഘം", "en": "CLOUD"}, {"icon": "drop", "ml": "മഴ", "en": "RAIN"}, {"icon": "bolt", "ml": "അലർട്ട്", "en": "ALERT"}]}}),
        B("നിങ്ങളുടെ ജില്ലയിൽ ഈ വർഷം ഏറ്റവും കൂടുതൽ കണ്ട അലർട്ട് ഏത് നിറമായിരുന്നു?", None, {"kind": "outro", "p": {"ml": "നിങ്ങളുടെ ജില്ലയിൽ ഈ വർഷം ഏറ്റവും കൂടുതൽ കണ്ട അലർട്ട് ഏത് നിറം?", "en": "WHICH ALERT COLOUR DID YOUR DISTRICT SEE MOST THIS YEAR?"}}),
        B("താഴെ കമന്റ് ചെയ്യൂ, ഇതുപോലുള്ള വീഡിയോകൾക്കായി സയൻസ് ചായ സബ്സ്ക്രൈബ് ചെയ്യൂ."),
    ],
}
FACTS = [
    "IMD colour-coded rainfall warnings use 24-hour rainfall: heavy 64.5-115.5 mm (yellow), very heavy 115.6-204.4 mm (orange), extremely heavy above 204.4 mm (red) (India Meteorological Department; Kerala press coverage).",
    "One millimetre of rain is one litre of water on one square metre.",
    "IMD names the stages: cyclonic circulation, low pressure area, well-marked low pressure area, depression, deep depression, cyclonic storm (IMD bulletins).",
    "In the northern hemisphere cyclonic circulation turns anti-clockwise.",
]
VIDEOS = [LONG]
