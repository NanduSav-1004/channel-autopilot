"""Science Chaya: tides, the backwaters and chakara (long)."""
from chaya.content_monsoon import BL, BR, DK, GD, GR, LF, OR, RD, SE, B
from chaya.dsl import PT, C, I, R
from chaya.quick import lab

LONG = {
    "id": "backwaters_long", "orient": "wide", "mood": "curious",
    "title_ml": "കായലും വേലിയേറ്റവും ചാകരയും: കേരളത്തിന്റെ വെള്ളത്തിന്റെ ശാസ്ത്രം",
    "title_en": "Backwaters, tides and chakara: the science of Kerala's water",
    "thumb": {"ml": "കായലും ചാകരയും", "en": "TIDES AND CHAKARA", "hero": "compose"},
    "comment": "നിങ്ങളുടെ നാട്ടിൽ ചാകര കണ്ടിട്ടുണ്ടോ, അതോ കായൽ വേലിയേറ്റം?",
    "beats": [
        B("കേരളത്തിലെ കായലിൽ വെള്ളം ദിവസത്തിൽ രണ്ട് തവണ ഉയരുകയും താഴുകയും ചെയ്യുന്നത് ശ്രദ്ധിച്ചിട്ടുണ്ടോ?", ("ഉയരുന്ന വെള്ളം", "WATER RISING AND FALLING", SE), C([R(0, 0.55, 1, 0.45, "#1f8aa8", op=0.9), I("boat", 0.5, 0.52, 5, anim="float"), PT("bubbles", 18, [0.05, 0.6, 0.95, 0.95], "#d8f0f8", 6)], bg="sky")),
        B("അതാണ് വേലിയേറ്റവും വേലിയിറക്കവും.", ("വേലിയേറ്റം · വേലിയിറക്കം", "HIGH TIDE AND LOW TIDE", BL)),
        B("ചന്ദ്രന്റെ ഗുരുത്വാകർഷണം കടലിലെ വെള്ളത്തെ വലിക്കുന്നതാണ് ഇതിന് കാരണം.", ("ചന്ദ്രന്റെ വലി", "THE MOON'S GRAVITY PULLS THE SEA", DK), C([I("moon", 0.5, 0.2, 4), R(0, 0.6, 1, 0.4, "#146a85", op=0.9), PT("bubbles", 20, [0.2, 0.6, 0.8, 0.95], "#d8f0f8", 6)], bg="night")),
        B("സൂര്യനും ഒരു പങ്കുണ്ട്, പക്ഷേ ചന്ദ്രൻ അടുത്തായതുകൊണ്ട് സ്വാധീനം കൂടുതലാണ്.", ("ചന്ദ്രൻ അടുത്ത്", "THE MOON IS CLOSER, SO IT MATTERS MORE", GD)),
        B("കടൽ ഒരു വായിലൂടെ കായലുമായി ചേരുന്നതുകൊണ്ട് കായലിലെ വെള്ളവും ഈ താളത്തിൽ ഉയരുകയും താഴുകയും ചെയ്യും.", ("കടലും കായലും", "THE LAKE BREATHES WITH THE SEA", SE)),
        B("വേമ്പനാട്ട് കായൽ കേരളത്തിലെ ഏറ്റവും വലിയ കായലാണ്.", ("വേമ്പനാട്ട് കായൽ", "VEMBANAD, KERALA'S LARGEST LAKE", LF)),
        B("അത് ഒരു റാംസർ തണ്ണീർത്തടം കൂടിയാണ്.", ("റാംസർ തണ്ണീർത്തടം", "A RAMSAR WETLAND", LF)),
        B("കടൽവെള്ളം കയറുമ്പോൾ കായലിൽ ഉപ്പ് കൂടും, മഴക്കാലത്ത് പുഴവെള്ളം വരുമ്പോൾ ഉപ്പ് കുറയും.", ("ഉപ്പ് കൂടും, കുറയും", "SALINITY RISES AND FALLS", OR)),
        B("ഈ മാറ്റത്തിനനുസരിച്ച് അവിടത്തെ ജീവികളുടെ ജീവിതവും മാറും.", ("ജീവികൾ മാറും", "LIFE CHANGES WITH THE SALT", GR)),
        B("കുട്ടനാട്ടിലെ നെൽകൃഷിക്ക് ഉപ്പുവെള്ളം ദോഷമാണ്.", ("നെല്ലിന് ഉപ്പ് ദോഷം", "SALT WATER HARMS THE RICE", RD)),
        B("അതുകൊണ്ട് തണ്ണീർമുക്കത്ത് ഒരു ബണ്ട് കെട്ടി ഉപ്പുവെള്ളം തടയുന്നു.", ("തണ്ണീർമുക്കം ബണ്ട്", "THE THANNEERMUKKOM BUND", BR)),
        B("ഇനി ചാകരയിലേക്ക് വരാം.", ("ഇനി ചാകര", "NOW, CHAKARA", DK)),
        B("മഴക്കാലത്ത് കേരള തീരത്ത് ചില ഇടങ്ങളിൽ കടൽ ശാന്തമായി ചെളി നിറഞ്ഞ ഭാഗങ്ങൾ ഉണ്ടാകും, അതാണ് ചെളിത്തിട്ട.", ("ചെളിത്തിട്ട", "THE MUD BANK", GD), C([R(0, 0.5, 1, 0.5, "#1f8aa8", op=0.95), R(0.35, 0.5, 0.3, 0.5, "#a98a62", op=0.9), PT("bubbles", 30, [0.0, 0.5, 0.3, 0.95], "#e8f6fb", 9, speed=0.8), PT("bubbles", 30, [0.7, 0.5, 1.0, 0.95], "#e8f6fb", 9, speed=0.8)], bg="sky")),
        B("പുറത്ത് തിരമാലകൾ ആഞ്ഞടിക്കുമ്പോഴും അവിടെ കടൽ ശാന്തമായിരിക്കും.", ("ശാന്തമായ കടൽ", "CALM WATER AMONG THE SURF", BL)),
        B("മത്സ്യത്തൊഴിലാളികൾക്ക് അവിടെ സുരക്ഷിതമായി വള്ളമിറക്കാം, കൂടുതൽ മീനും കിട്ടും.", ("സുരക്ഷിതം, മീനും കൂടുതൽ", "SAFE LAUNCHING, BIGGER CATCHES", LF), C([R(0, 0.5, 1, 0.5, "#1f8aa8", op=0.95), I("boat", 0.5, 0.5, 5, anim="float")], bg="sky")),
        B("ഈ ചെളിത്തിട്ടകൾ ഉണ്ടാകുന്നത് എങ്ങനെയെന്ന് ശാസ്ത്രജ്ഞർക്ക് ഇപ്പോഴും പൂർണ്ണമായി വ്യക്തമല്ല.", ("ഇപ്പോഴും രഹസ്യം", "STILL NOT FULLY EXPLAINED", RD)),
        B("ഒരു സിദ്ധാന്തം പറയുന്നത് അടിത്തട്ടിലെ ചെളി മുകളിലേക്ക് ഉയർന്നുവരുന്നതുകൊണ്ടാണെന്നാണ്.", ("ചെളി മുകളിലേക്ക്", "ONE IDEA: MUD UPWELLS", OR)),
        B("മറ്റൊന്ന് പുഴകളിൽ നിന്നും കായലിൽ നിന്നുമുള്ള ജൈവവസ്തുക്കൾ ഇതിൽ പങ്കുവഹിക്കുന്നു എന്നാണ്.", ("ജൈവവസ്തുക്കൾ", "ANOTHER: ORGANIC MATTER FROM RIVERS", GR)),
        B("ആലപ്പുഴയിലെ ചെളിത്തിട്ടയാണ് ഏറ്റവും പ്രസിദ്ധം, അത് പത്ത് മുതൽ അമ്പത് ചതുരശ്ര കിലോമീറ്റർ വരെ വ്യാപിക്കാം.", ("10–50 ചതുരശ്ര കി.മീ.", "ALAPPUZHA'S MUD BANK, 10-50 SQ KM", GD)),
        B("അടുത്ത കാലത്ത് ചാകര കുറഞ്ഞുവരുന്നു എന്ന് മത്സ്യത്തൊഴിലാളികൾ പറയുന്നു.", ("ചാകര കുറയുന്നു", "FISHERS SAY CHAKARA IS FADING", RD)),
        B("അതിന്റെ കാരണം പഠിക്കാൻ ഇനിയും ഗവേഷണം വേണം.", ("ഗവേഷണം വേണം", "MORE RESEARCH IS NEEDED", DK)),
        B("ചന്ദ്രൻ, കായൽ, ഒരു ബണ്ട്, ഒരു ചെളിത്തിട്ട, ഒരു നാടിന്റെ ജീവിതം ഇവയെ ആശ്രയിച്ചിരിക്കുന്നു.", ("ഒരു നാടിന്റെ ജീവിതം", "A WHOLE REGION'S LIFE DEPENDS ON THEM", BR), {"kind": "flow", "p": {"carry": "water", "nodes": [{"icon": "moon", "ml": "ചന്ദ്രൻ", "en": "MOON"}, {"icon": "boat", "ml": "കായൽ", "en": "LAKE"}, {"icon": "dam", "ml": "ബണ്ട്", "en": "BUND"}, {"icon": "drop", "ml": "ചെളിത്തിട്ട", "en": "MUD BANK"}]}}),
        B("നിങ്ങളുടെ നാട്ടിൽ ചാകര കണ്ടിട്ടുണ്ടോ, അതോ കായൽ വേലിയേറ്റം?", None, {"kind": "outro", "p": {"ml": "നിങ്ങളുടെ നാട്ടിൽ ചാകര കണ്ടിട്ടുണ്ടോ, അതോ കായൽ വേലിയേറ്റം?", "en": "HAVE YOU SEEN CHAKARA OR THE LAKE TIDES NEAR YOU?"}}),
        B("താഴെ കമന്റ് ചെയ്യൂ, ഇതുപോലുള്ള വീഡിയോകൾക്കായി സയൻസ് ചായ സബ്സ്ക്രൈബ് ചെയ്യൂ."),
    ],
}
FACTS = [
    "Tides come mainly from the Moon's gravity, with a smaller pull from the Sun; the Vembanad lake is Kerala's largest lake and a Ramsar wetland; the Thanneermukkom bund keeps salt water out of Kuttanad's rice fields.",
    "Mud banks (chakara) are calm, muddy patches of inshore water along Kerala's coast in the south-west monsoon; their origin is still not fully explained; the Alappuzha mud bank can spread over 10 to 50 sq km and fishers report chakara is declining (research papers on Kerala mud banks; Deccan Chronicle; The South First).",
]
# richer scenes: the Moon's pull on the sea and a mud bank
lab(LONG, 2, 10, "tide", {"pull": 0, "rise": 2, "bund": 8}, [(0, "ചന്ദ്രന്റെ ഗുരുത്വാകർഷണം", "THE MOON'S PULL", 500, 330), (2, "കായലിലും ഉയരും", "THE BACKWATER RISES TOO", 1250, 330), (8, "ഉപ്പുവെള്ളം തടയാൻ ബണ്ട്", "A BUND KEEPS OUT SALT", 1600, 330)])
lab(LONG, 12, 20, "mudbank", {"waves": 0, "mud": 1, "boats": 2}, [(0, "ചാകര", "CHAKARA", 500, 360), (1, "ചെളി തിരമാലയെ ശമിപ്പിക്കുന്നു", "MUD CALMS THE WAVES", 550, 360), (2, "സുരക്ഷിതമായി വള്ളമിറക്കാം", "BOATS CAN LAUNCH SAFELY", 550, 360)])

VIDEOS = [LONG]
