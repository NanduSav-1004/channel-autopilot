"""Science Chaya: eight kitchen and village Shorts (idli batter, curd, coconut oil, pressure cooker, onion, fan, snake boat, tender coconut)."""
from chaya.content_batch_shorts import outro, short
from chaya.content_monsoon import BL, BR, DK, GD, GR, LF, OR, RD, SE, B
from chaya.dsl import LB, PT, C, I, R, T
from chaya.quick import lab

IDLI = short("idli_s", "ഇഡ്ഡലി മാവ് പൊങ്ങുന്നത് എങ്ങനെ? #Shorts", "Why does idli batter rise overnight?", {"ml": "മാവ് പൊങ്ങുന്നത് എങ്ങനെ?", "en": "IDLI BATTER", "hero": "compose"}, [
    B("രാത്രി വെച്ച ഇഡ്ഡലി മാവ് രാവിലെ പൊങ്ങിയിരിക്കുന്നത് എങ്ങനെയാണ്?", ("മാവ് പൊങ്ങുന്നു", "HOW DOES BATTER RISE OVERNIGHT?", OR), C([I("bowl", 0.5, 0.5, 6.5, label=LB("ഇഡ്ഡലി മാവ്", "IDLI BATTER", OR, 400)), PT("bubbles", 24, [0.4, 0.25, 0.6, 0.58], "#fffaf0", 7)], bg="dusk")),
    B("മാവിൽ കണ്ണിന് കാണാത്ത ബാക്ടീരിയകൾ ഉണ്ട്.", ("കണ്ണിന് കാണാത്ത ബാക്ടീരിയ", "TINY BACTERIA IN THE BATTER", BL)),
    B("ല്യൂക്കോനോസ്റ്റോക് മെസെന്ററോയിഡസ് എന്ന ബാക്ടീരിയയാണ് പ്രധാനി.", ("ല്യൂക്കോനോസ്റ്റോക്", "LEUCONOSTOC MESENTEROIDES", DK)),
    B("അവ മാവിലെ പഞ്ചസാര ഭക്ഷിച്ച് പുളിപ്പും കാർബൺ ഡയോക്സൈഡ് വാതകവും ഉണ്ടാക്കും.", ("പുളിപ്പും വാതകവും", "SOUR ACID AND CO₂", SE), C([I("bowl", 0.5, 0.65, 7), PT("bubbles", 40, [0.35, 0.1, 0.65, 0.6], "#fffaf0", 9, speed=0.5)], bg="dusk")),
    B("ആ വാതകക്കുമിളകൾ മാവിനെ പൊക്കി ഇഡ്ഡലിയെ പഞ്ഞി പോലെ മൃദുവാക്കും.", ("കുമിളകൾ = മൃദുത്വം", "BUBBLES MAKE IT SOFT", LF)),
    B("അതുകൊണ്ടാണ് ഇഡ്ഡലിക്ക് ചെറിയ പുളിരുചിയും ഉണ്ടാകുന്നത്.", ("പുളിരുചി", "THAT IS THE SOUR TASTE", GD)),
    outro("കണ്ണിന് കാണാത്ത പാചകക്കാർ!", "TINY COOKS AT WORK", "ബാക്ടീരിയകളാണ് യഥാർത്ഥ പാചകക്കാർ!"),
])
CURD = short("curd_s", "തൈര് ഉറയുന്നത് എങ്ങനെ? #Shorts", "How does milk turn into curd overnight?", {"ml": "തൈര് ഉറയുന്ന രഹസ്യം", "en": "HOW CURD SETS", "hero": "compose"}, [
    B("ഒരു സ്പൂൺ തൈര് കൊണ്ട് ഒരു പാത്രം പാൽ തൈരാകുന്നത് എങ്ങനെയാണ്?", ("ഒരു സ്പൂൺ തൈര്", "HOW DOES ONE SPOON DO IT?", GD), C([I("bowl", 0.5, 0.5, 6.5, glow="#fff", label=LB("തൈര്", "CURD", GD, 300))], bg="dusk")),
    B("ആ സ്പൂൺ തൈരിൽ ലക്ഷക്കണക്കിന് ബാക്ടീരിയകൾ ഉണ്ട്.", ("ബാക്ടീരിയകൾ", "FULL OF BACTERIA", BL)),
    B("അവ പാലിലെ പഞ്ചസാരയെ ലാക്റ്റിക് ആസിഡാക്കി മാറ്റും.", ("പഞ്ചസാര → ആസിഡ്", "MILK SUGAR BECOMES LACTIC ACID", OR)),
    B("അമ്ലത കൂടുമ്പോൾ പാലിലെ മാംസ്യം കട്ടപിടിക്കും.", ("മാംസ്യം കട്ടപിടിക്കുന്നു", "THE ACID CLUMPS THE PROTEIN", RD)),
    B("അങ്ങനെ പാൽ തൈരായി മാറും.", ("പാൽ → തൈര്", "MILK BECOMES CURD", GD)),
    B("പാൽ ഇളംചൂടിൽ ആയിരിക്കണം, നന്നായി തണുത്താൽ ബാക്ടീരിയകൾ പതുക്കെയാകും.", ("ഇളംചൂട് വേണം", "KEEP IT LUKEWARM", LF)),
    outro("ഒരു സ്പൂൺ, ഒരു ലോകം!", "ONE SPOON, A WHOLE WORLD", "ഒരു ചെറിയ സ്പൂൺ, ഒരു വലിയ ലോകം!"),
])
COIL = short("coconutoil_s", "വെളിച്ചെണ്ണ കട്ടിയാകുന്നത് എന്തുകൊണ്ട്? #Shorts", "Why does coconut oil turn solid?", {"ml": "വെളിച്ചെണ്ണ കട്ടിയാകുന്നത്", "en": "COCONUT OIL", "hero": "compose"}, [
    B("തണുത്ത പ്രഭാതത്തിൽ വെളിച്ചെണ്ണ കട്ടിയാകുന്നത് കേടായതുകൊണ്ടാണോ?", ("കട്ടിയായ വെളിച്ചെണ്ണ", "IS IT SPOILED?", LF), C([I("bottle", 0.5, 0.5, 6.5), I("thermo", 0.2, 0.5, 4, anim="float")], bg="dusk")),
    B("അല്ല, അത് സാധാരണമാണ്.", ("കേടല്ല", "NO, IT IS NORMAL", GR)),
    B("വെളിച്ചെണ്ണ ഇരുപത്തിനാല്, ഇരുപത്തിയഞ്ച് ഡിഗ്രി സെൽഷ്യസിന് താഴെ കട്ടിയാകും.", ("24–25 °C ന് താഴെ", "SOLID BELOW ABOUT 24 °C", BL), {"kind": "stat", "p": {"value": 24, "suffix": " °C", "ml": "ഇതിന് താഴെ കട്ടിയാകും", "en": "COCONUT OIL SOLIDIFIES", "icon": "thermo"}}),
    B("അതിൽ ലോറിക് ആസിഡ് എന്ന കൊഴുപ്പ് കൂടുതലാണ്.", ("ലോറിക് ആസിഡ്", "RICH IN LAURIC ACID", DK)),
    B("ഈ കൊഴുപ്പാണ് ഇതിന്റെ ഉരുകൽ നില നിശ്ചയിക്കുന്നത്.", ("ഉരുകൽ നില", "IT SETS THE MELTING POINT", OR)),
    B("ചൂടുവെള്ളത്തിൽ കുപ്പി ഇറക്കിവെച്ചാൽ വീണ്ടും ഒഴുകുന്ന എണ്ണയാകും.", ("ചൂടാക്കിയാൽ ഒഴുകും", "WARM IT AND IT FLOWS AGAIN", RD)),
    outro("കട്ടിയായാലും ഗുണം കുറയില്ല!", "SOLID OR LIQUID, SAME OIL", "തണുപ്പിൽ കട്ടിയായാലും അത് ശുദ്ധമായ വെളിച്ചെണ്ണ തന്നെ!"),
])
COOKER = short("cooker_s", "പ്രഷർ കുക്കർ വിസിൽ അടിക്കുന്നത് എന്തിന്? #Shorts", "Why does a pressure cooker whistle?", {"ml": "കുക്കർ വിസിൽ", "en": "PRESSURE COOKER", "hero": "compose"}, [
    B("പ്രഷർ കുക്കർ വിസിൽ അടിക്കുന്നത് എന്തിനാണ്?", ("കുക്കർ വിസിൽ", "WHY DOES IT WHISTLE?", RD), C([I("cooker", 0.5, 0.5, 7, anim="shake"), PT("bubbles", 22, [0.43, 0.1, 0.57, 0.4], "#fff", 8)], bg="dusk")),
    B("സാധാരണ വെള്ളം നൂറ് ഡിഗ്രിയിൽ തിളയ്ക്കും.", ("100 °C ൽ തിളയ്ക്കും", "WATER BOILS AT 100 °C", SE)),
    B("കുക്കറിൽ ആവി പുറത്തുപോകാതെ അടച്ചുവയ്ക്കുമ്പോൾ മർദ്ദം കൂടും.", ("മർദ്ദം കൂടും", "TRAPPED STEAM RAISES PRESSURE", OR)),
    B("മർദ്ദം കൂടിയാൽ വെള്ളം ഏകദേശം നൂറ്റി ഇരുപത്തിയൊന്ന് ഡിഗ്രി വരെ ചൂടാകും.", ("≈ 121 °C", "ABOUT 121 °C", RD)),
    B("ആ ചൂടിൽ അരിയും പയറും വേഗം വേവും.", ("വേഗം വേവും", "FOOD COOKS FASTER", GD)),
    B("വിസിൽ അടിക്കുന്നത് അധികമുള്ള ആവി പുറത്തുവിടുന്ന വാൽവ് ആണ്.", ("വിസിൽ = സുരക്ഷാ വാൽവ്", "THE WHISTLE RELEASES EXTRA STEAM", LF)),
    outro("ഒരു വിസിൽ, ഒരു ശാസ്ത്രം!", "ONE WHISTLE, ONE BIT OF SCIENCE", "ഓരോ വിസിലിനും പിന്നിൽ ഒരു ശാസ്ത്രമുണ്ട്!"),
])
ONION = short("onion_s", "ഉള്ളി മുറിക്കുമ്പോൾ കണ്ണ് നിറയുന്നത് എന്തുകൊണ്ട്? #Shorts", "Why do onions make you cry?", {"ml": "ഉള്ളി കരയിക്കുന്നത്", "en": "ONION TEARS", "hero": "compose"}, [
    B("ഉള്ളി മുറിക്കുമ്പോൾ കണ്ണ് നിറയുന്നത് എന്തുകൊണ്ടാണ്?", ("ഉള്ളിയും കണ്ണീരും", "WHY DO ONIONS MAKE YOU CRY?", GD), C([I("onion", 0.5, 0.5, 7, anim="float"), T("ഉള്ളി", 0.5, 0.86, 90)], bg="dusk")),
    B("ഉള്ളി മുറിക്കുമ്പോൾ അതിലെ കോശങ്ങൾ പൊട്ടും.", ("കോശങ്ങൾ പൊട്ടുന്നു", "CUTTING BREAKS THE CELLS", OR)),
    B("അപ്പോൾ അകത്തുള്ള എൻസൈമുകൾ പുറത്തുവരും.", ("എൻസൈമുകൾ പുറത്ത്", "ENZYMES ESCAPE", BL)),
    B("അവ ചേർന്ന് ഒരു ആവിയായ വസ്തു ഉണ്ടാക്കും.", ("ആവിയായ വസ്തു", "THEY MAKE A VAPOUR", RD), C([I("onion", 0.5, 0.65, 8), PT("bubbles", 26, [0.4, 0.15, 0.6, 0.55], "#e9b6d6", 7)], bg="dusk")),
    B("ആ ആവി കണ്ണിൽ തട്ടുമ്പോൾ എരിച്ചിലുണ്ടാക്കും.", ("കണ്ണിൽ എരിച്ചിൽ", "IT STINGS THE EYES", DK)),
    B("അതിനെ ശമിപ്പിക്കാൻ കണ്ണ് കണ്ണീര് ഒഴുക്കും.", ("കണ്ണീർ ഒഴുകുന്നു", "SO THE EYES MAKE TEARS", SE)),
    outro("ഉള്ളി കരയിക്കുന്നത് ശാസ്ത്രം കൊണ്ടാണ്!", "AN ONION'S CHEMICAL DEFENCE", "ഉള്ളിയുടെ ആ ചെറിയ രാസായുധം!"),
])
FAN = short("fan_s", "ഫാൻ മുറി തണുപ്പിക്കുന്നില്ല, പിന്നെ എങ്ങനെ തണുക്കുന്നു? #Shorts", "A fan does not cool the room, so why do you feel cooler?", {"ml": "ഫാൻ തണുപ്പിക്കുന്നില്ല!", "en": "WHY FANS FEEL COOL", "hero": "compose"}, [
    B("ഫാൻ ഇട്ടാൽ തണുപ്പ് തോന്നുന്നു, പക്ഷേ മുറി തണുക്കുന്നില്ല, എങ്ങനെ?", ("ഫാൻ തണുപ്പിക്കുന്നില്ല", "THE FAN DOES NOT COOL THE ROOM", SE), C([I("fan", 0.5, 0.5, 9, anim="spin", speed=480), PT("bubbles", 14, [0.1, 0.2, 0.9, 0.8], "#cfe6f5", 6)], bg="sky")),
    B("നമ്മുടെ തൊലിയിൽ എപ്പോഴും നേരിയ വിയർപ്പ് ഉണ്ടാകും.", ("തൊലിയിലെ വിയർപ്പ്", "A THIN LAYER OF SWEAT", BL)),
    B("വിയർപ്പ് ആവിയാകുമ്പോൾ ശരീരത്തിൽ നിന്ന് ചൂട് എടുത്തുകൊണ്ടുപോകും.", ("ആവിയാകുമ്പോൾ തണുപ്പ്", "EVAPORATION TAKES HEAT AWAY", OR)),
    B("ഫാനിന്റെ കാറ്റ് ഈ ആവിയാകൽ വേഗത്തിലാക്കും.", ("കാറ്റ് ആവിയാക്കൽ കൂട്ടും", "THE BREEZE SPEEDS IT UP", LF)),
    B("അതുകൊണ്ടാണ് നമുക്ക് തണുപ്പ് തോന്നുന്നത്, മുറിയുടെ ചൂട് കുറയുന്നില്ല.", ("തോന്നലാണ്, മുറി തണുക്കുന്നില്ല", "YOU FEEL COOLER, THE AIR DOES NOT", DK)),
    B("അതുകൊണ്ട് മുറിയിൽ ആരുമില്ലെങ്കിൽ ഫാൻ ഓഫ് ചെയ്യാം.", ("ആരുമില്ലെങ്കിൽ ഓഫ്", "TURN IT OFF IN AN EMPTY ROOM", GD)),
    outro("ഫാൻ തണുപ്പിക്കുന്നത് നിങ്ങളെയാണ്, മുറിയെ അല്ല!", "A FAN COOLS YOU, NOT THE ROOM", "ഫാൻ തണുപ്പിക്കുന്നത് നിങ്ങളെയാണ്, മുറിയെ അല്ല!"),
])
BOAT = short("snakeboat_s", "ചുണ്ടൻ വള്ളം ഇത്ര വേഗത്തിൽ പായുന്നത് എങ്ങനെ? #Shorts", "How does a snake boat fly across the water?", {"ml": "ചുണ്ടൻ വള്ളത്തിന്റെ ശാസ്ത്രം", "en": "SNAKE BOAT PHYSICS", "hero": "compose"}, [
    B("ചുണ്ടൻ വള്ളം ഇത്ര വേഗത്തിൽ പായുന്നത് എങ്ങനെയാണ്?", ("ചുണ്ടൻ വള്ളം", "HOW DOES IT FLY?", RD), C([R(0, 0.5, 1, 0.5, "#1f8aa8", op=0.95), I("boat", 0.5, 0.5, 9, anim="float"), PT("bubbles", 20, [0.05, 0.55, 0.95, 0.95], "#d8f0f8", 6)], bg="sky")),
    B("ചുണ്ടൻ വള്ളത്തിന് നൂറ് മുതൽ നൂറ്റി മുപ്പത്തെട്ട് അടി വരെ നീളമുണ്ട്.", ("100–138 അടി നീളം", "100 TO 138 FEET LONG", BR)),
    B("നീളമുള്ള വള്ളം വെള്ളത്തെ എളുപ്പം കീറിമുറിച്ച് മുന്നോട്ട് പോകും.", ("നീളം കൂടിയാൽ വേഗം", "LONGER BOATS CUT THROUGH WATER EASILY", SE)),
    B("ഒരുപാട് തുഴക്കാർ ഒരേ താളത്തിൽ തുഴയുന്നു.", ("ഒരേ താളത്തിൽ", "MANY OARS, ONE RHYTHM", GD)),
    B("ഒരേ സമയത്ത് വെള്ളത്തെ പിന്നിലേക്ക് തള്ളുമ്പോൾ എല്ലാവരുടെയും ബലം ഒന്നിച്ച് ചേരും.", ("ബലം ഒന്നിച്ച്", "EVERY PUSH ADDS UP", OR)),
    B("നെഹ്രു ട്രോഫി വള്ളംകളി ആയിരത്തി തൊള്ളായിരത്തി അൻപത്തിരണ്ട് മുതൽ പുന്നമടക്കായലിൽ നടക്കുന്നു.", ("1952 മുതൽ", "SINCE 1952 ON PUNNAMADA LAKE", LF)),
    outro("ഒരേ താളം, ഒരേ ലക്ഷ്യം!", "ONE RHYTHM, ONE GOAL", "ഒരേ താളത്തിന്റെ ശക്തി!"),
])
COCO = short("tendercoconut_s", "ഇളനീരിൽ എന്താണ് ഉള്ളത്? #Shorts", "What is inside tender coconut water?", {"ml": "ഇളനീരിലെ രഹസ്യം", "en": "TENDER COCONUT", "hero": "compose"}, [
    B("ഇളനീരിൽ എന്താണ് ഉള്ളത്?", ("ഇളനീർ", "WHAT IS IN IT?", LF), C([I("coconut", 0.5, 0.5, 9, anim="float"), T("ഇളനീർ", 0.5, 0.86, 90)], bg="dusk")),
    B("ഇളനീരിൽ ഏകദേശം തൊണ്ണൂറ്റി നാല്, തൊണ്ണൂറ്റി അഞ്ച് ശതമാനം വെള്ളമാണ്.", ("≈ 95 % വെള്ളം", "ABOUT 94–95 % WATER", SE), {"kind": "stat", "p": {"value": 95, "suffix": " %", "ml": "ഇളനീരിലെ വെള്ളം", "en": "TENDER COCONUT WATER", "icon": "drop"}}),
    B("ബാക്കി ചെറിയ അളവ് പഞ്ചസാരയും ധാതുക്കളുമാണ്.", ("പഞ്ചസാരയും ധാതുക്കളും", "A LITTLE SUGAR AND MINERALS", GD)),
    B("അതിൽ ഏറ്റവും കൂടുതലുള്ള ധാതു പൊട്ടാസ്യമാണ്.", ("പൊട്ടാസ്യം", "POTASSIUM IS THE MAIN MINERAL", OR)),
    B("തേങ്ങ മൂക്കുംതോറും ഈ പൊട്ടാസ്യത്തിന്റെ അളവ് കൂടും.", ("മൂത്താൽ പൊട്ടാസ്യം കൂടും", "MORE POTASSIUM AS THE NUT MATURES", BL)),
    B("അതുകൊണ്ടാണ് ചൂടുള്ള ദിവസം ഇളനീർ കുടിച്ചാൽ ദാഹം മാറി ഉന്മേഷം തോന്നുന്നത്.", ("ദാഹം മാറ്റും", "THAT IS WHY IT QUENCHES THIRST", LF)),
    outro("പ്രകൃതിയുടെ സ്വന്തം പാനീയം!", "NATURE'S OWN DRINK", "പ്രകൃതി തന്ന സ്വന്തം പാനീയം!"),
])
FACTS = [
    "Idli batter: Leuconostoc mesenteroides makes acid and CO2 that leaven the batter (Mattada and Mukherjee, 1965). Curd: bacteria turn lactose into lactic acid, which clumps milk protein.",
    "Coconut oil solidifies below about 24-25 degrees Celsius (lauric acid); a pressure cooker at about 15 psi gauge raises the boiling point to about 121 degrees Celsius.",
    "Cut onions release syn-propanethial-S-oxide, which irritates the eyes (ACS Chemical Biology 2017).",
    "A fan cools you by speeding up sweat evaporation, not by cooling the air; in air above about 35 degrees Celsius a fan alone is not enough (University of Ottawa review in The Lancet Planetary Health, 2024).",
    "Chundan vallams are about 100-138 feet long; the Nehru Trophy Boat Race has run on Punnamada Lake since 1952 (Wikipedia: Chundan vallam, Nehru Trophy Boat Race).",
    "Tender coconut water is about 94-95% water, with potassium as the main mineral, rising as the nut matures (Tetra Pak Coconut Handbook; Wikipedia: Coconut water).",
]
# richer scenes: a close look inside each kitchen and village thing
lab(IDLI, 0, 5, "ferment", {"bact": 1, "eat": 3, "rise": 4}, [(1, "കണ്ണിന് കാണാത്ത ബാക്ടീരിയ", "TINY BACTERIA", 500, 380), (3, "പുളിപ്പും വാതകവും", "ACID AND GAS", 500, 350), (4, "കുമിളകൾ മാവിനെ പൊക്കുന്നു", "BUBBLES LIFT THE BATTER", 500, 360)], kind="idli")
lab(CURD, 0, 5, "ferment", {"bact": 1, "eat": 2, "set": 3}, [(1, "ലക്ഷക്കണക്കിന് ബാക്ടീരിയ", "MILLIONS OF BACTERIA", 500, 380), (2, "പഞ്ചസാര → ആസിഡ്", "SUGAR TO ACID", 500, 350), (3, "മാംസ്യം കട്ടപിടിക്കുന്നു", "THE PROTEIN CLUMPS", 500, 360)], kind="curd")
lab(COIL, 0, 5, "oilsolid", {"cool": 2, "warm": 5}, [(2, "24–25 °C ന് താഴെ കട്ടിയാകും", "SOLID BELOW ABOUT 24 °C", 500, 300), (5, "ചൂടാക്കിയാൽ വീണ്ടും ഒഴുകും", "WARM IT AND IT FLOWS", 500, 300)])
lab(COOKER, 0, 5, "cooker", {"heat": 1, "steam": 1.5, "pressure": 2, "whistle": 5}, [(1, "100 °C ൽ തിളയ്ക്കും", "WATER BOILS AT 100 °C", 500, 330), (2, "മർദ്ദം കൂടുന്നു", "THE PRESSURE RISES", 500, 330), (5, "വിസിൽ = അധിക ആവി", "THE WHISTLE LETS STEAM OUT", 500, 330)])
lab(ONION, 0, 5, "onion", {"cut": 1, "enzyme": 2, "vapor": 3, "tears": 5}, [(1, "കോശങ്ങൾ പൊട്ടുന്നു", "CELLS BREAK OPEN", 420, 400), (2, "എൻസൈമുകൾ പുറത്ത്", "ENZYMES ESCAPE", 420, 400), (3, "ആവിയായ വസ്തു", "A VAPOUR FORMS", 640, 380), (5, "കണ്ണീര്", "TEARS", 880, 620)])
lab(FAN, 0, 5, "sweat", {"sweat": 1, "evap": 2, "fan": 3, "room": 4}, [(1, "തൊലിയിൽ വിയർപ്പ്", "SWEAT ON THE SKIN", 500, 600), (2, "ആവിയാകുമ്പോൾ ചൂട് പോകും", "EVAPORATION CARRIES HEAT", 500, 500), (3, "കാറ്റ് ആവിയാകൽ കൂട്ടും", "MOVING AIR SPEEDS IT UP", 250, 330), (4, "മുറിയുടെ ചൂട് അതുതന്നെ", "THE ROOM STAYS THE SAME", 880, 360)])
lab(BOAT, 0, 5, "snakeboat", {"long": 1, "rhythm": 3, "push": 4}, [(1, "100–138 അടി നീളം", "UP TO 138 FEET", 40, 840), (3, "ഒരേ താളം", "THE SAME RHYTHM", 40, 330), (4, "ഒന്നിച്ച് തള്ളുന്നു", "ALL PUSH TOGETHER", 40, 330)])
lab(COCO, 0, 5, "coconutwater", {"water": 1, "minerals": 2, "potassium": 3}, [(1, "94–95 % വെള്ളം", "ABOUT 94–95% WATER", 760, 850), (2, "പഞ്ചസാരയും ധാതുക്കളും", "SUGAR AND MINERALS", 760, 850), (3, "ഏറ്റവും കൂടുതൽ പൊട്ടാസ്യം", "MOST OF ALL POTASSIUM", 980, 250)])

VIDEOS = [IDLI, CURD, COIL, COOKER, ONION, FAN, BOAT, COCO]
