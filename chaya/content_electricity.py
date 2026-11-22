"""Science Chaya: the electricity video (long) and its three Shorts. Same format as content_monsoon.py (one sentence per beat)."""
from chaya.content_monsoon import BL, BR, DK, GD, LF, OR, RD, SE, B

METER_ITEMS = [{"icon": "led", "ml": "എൽഇഡി ബൾബ്", "watts": 9}, {"icon": "fan", "ml": "സീലിംഗ് ഫാൻ", "watts": 60}, {"icon": "ac", "ml": "എസി", "watts": 1000}]
CHAIN = [{"icon": "dam", "ml": "അണക്കെട്ട്", "en": "DAM"}, {"icon": "turbine", "ml": "ടർബൈൻ", "en": "TURBINE"}, {"icon": "generator", "ml": "ജനറേറ്റർ", "en": "GENERATOR"},
         {"icon": "transformer", "ml": "ട്രാൻസ്ഫോർമർ", "en": "TRANSFORMER"}, {"icon": "pylon", "ml": "ടവർ ലൈൻ", "en": "HIGH-VOLTAGE LINE"}, {"icon": "pole", "ml": "പോസ്റ്റ്", "en": "POLE"}, {"icon": "house", "ml": "വീട്", "en": "HOME"}]

LONG = {
    "id": "electricity_long", "orient": "wide", "mood": "curious",
    "title_ml": "ഇടുക്കി ഡാമിൽ നിന്ന് നിങ്ങളുടെ വീട്ടിലെ ബൾബിലേക്ക് വൈദ്യുതി എത്തുന്ന വഴി",
    "title_en": "How electricity travels from Idukki dam to the bulb in your home",
    "thumb": {"ml": "ഡാം മുതൽ ബൾബ് വരെ", "en": "HOW ELECTRICITY REACHES YOU", "hero": "dam"},
    "comment": "നിങ്ങളുടെ വീട്ടിലെ ഏറ്റവും കൂടുതൽ വൈദ്യുതി എടുക്കുന്ന ഉപകരണം ഏതാണ്?",
    "beats": [
        B("നിങ്ങൾ സ്വിച്ച് ഇടുമ്പോൾ ബൾബ് ഉടനെ കത്തുന്നു.", ("സ്വിച്ച് ഓൺ!", "FLICK THE SWITCH, THE BULB LIGHTS", BR), {"kind": "text", "p": {"ml": "സ്വിച്ച് ഓൺ!", "en": "WHERE DOES THE POWER COME FROM?", "icon": "bulb", "col": GD}}),
        B("ആ വൈദ്യുതി എവിടെ നിന്നാണ് വരുന്നത്?", ("എവിടെ നിന്ന്?", "WHERE FROM?", DK)),
        B("കേരളത്തിൽ അതിന്റെ വലിയൊരു ഭാഗം വരുന്നത് വെള്ളത്തിൽ നിന്നാണ്.", ("വെള്ളത്തിൽ നിന്ന്", "A LOT OF IT COMES FROM WATER", SE), {"kind": "damx", "p": {"cams": [{"atb": 0, "x": 500, "y": 540, "z": 1.0}, {"atb": 1, "x": 380, "y": 410, "z": 2.0}, {"atb": 2, "x": 150, "y": 400, "z": 1.7}, {"atb": 3, "x": 330, "y": 480, "z": 2.2},
                {"atb": 4, "x": 580, "y": 640, "z": 1.7}, {"atb": 5, "x": 910, "y": 820, "z": 2.3}, {"atb": 6, "x": 890, "y": 830, "z": 3.0}], "atb": {"height": 1.2, "tunnel": 4.0, "flow": 3.0, "house": 5.1, "spin": 6.0}}}),
        B("ഉദാഹരണത്തിന് ഇടുക്കി ആർച്ച് ഡാം, ഏകദേശം നൂറ്റി അറുപത്തിയൊമ്പത് മീറ്റർ ഉയരം.", ("ഇടുക്കി ഡാം", "IDUKKI ARCH DAM, ABOUT 169 M HIGH", BR)),
        B("ഉയരത്തിൽ കെട്ടിനിർത്തിയ വെള്ളത്തിന് ഊർജ്ജമുണ്ട്, അതിനെ സ്ഥിതികോർജ്ജം എന്ന് പറയും.", ("സ്ഥിതികോർജ്ജം", "STORED ENERGY OF HEIGHT", BL)),
        B("വെള്ളം താഴേക്ക് വീഴുമ്പോൾ ആ ഊർജ്ജം ചലനോർജ്ജമായി മാറും.", ("ചലനോർജ്ജം", "FALLING WATER HAS MOVING ENERGY", SE)),
        B("ഡാമിൽ നിന്ന് തുരങ്കത്തിലൂടെ വെള്ളം മലയ്ക്കുള്ളിലെ പവർഹൗസിലേക്ക് ഒഴുകുന്നു.", ("തുരങ്കം", "A TUNNEL THROUGH THE ROCK", DK)),
        B("ഇടുക്കിയിലെ പവർഹൗസ് മൂലമറ്റത്ത്, പാറയ്ക്കുള്ളിൽ ഭൂമിക്കടിയിലാണ്.", ("ഭൂഗർഭ പവർഹൗസ്", "AN UNDERGROUND POWER HOUSE AT MOOLAMATTOM", BR)),
        B("അവിടെ ശക്തിയിൽ വരുന്ന വെള്ളം ഒരു ടർബൈനിനെ കറക്കുന്നു.", ("ടർബൈൻ കറങ്ങുന്നു", "THE WATER SPINS THE TURBINE", SE)),
        B("ഇടുക്കിയിൽ ആറ് ടർബൈനുകളുണ്ട്, ഓരോന്നും നൂറ്റി മുപ്പത് മെഗാവാട്ട്, ആകെ ഏഴുന്നൂറ്റി എൺപത് മെഗാവാട്ട്.", ("6 × 130 = 780 MW", "SIX TURBINES, 780 MEGAWATTS IN ALL", OR), {"kind": "stat", "p": {"value": 780, "suffix": " MW", "ml": "ഇടുക്കിയുടെ ശേഷി", "en": "6 TURBINES × 130 MW", "icon": "bolt"}}),
        B("പക്ഷേ ടർബൈൻ കറങ്ങിയതുകൊണ്ട് മാത്രം വൈദ്യുതിയായില്ല.", ("ഇനിയും ബാക്കി", "SPINNING IS NOT ELECTRICITY YET", DK)),
        B("ടർബൈനിന്റെ അറ്റത്ത് ജനറേറ്റർ ഉണ്ട്.", ("ജനറേറ്റർ", "THE GENERATOR", RD), {"kind": "generator", "p": {"speed": 2.4}}),
        B("ഒരു കാന്തം ഒരു ചെമ്പ് കമ്പിച്ചുരുളിനുള്ളിൽ കറങ്ങുന്നു.", ("കറങ്ങുന്ന കാന്തം", "A MAGNET SPINNING INSIDE A COIL", RD)),
        B("കാന്തത്തിന്റെ വലയം മാറുമ്പോൾ കമ്പിയിൽ വൈദ്യുതി ഉണ്ടാകും.", ("മാറുന്ന കാന്തമണ്ഡലം → വൈദ്യുതി", "CHANGING MAGNETIC FIELD MAKES CURRENT", GD)),
        B("ആയിരത്തി എണ്ണൂറ്റി മുപ്പത്തൊന്നിൽ മൈക്കിൾ ഫാരഡെ ഇത് കണ്ടെത്തി.", ("1831 · ഫാരഡെ", "MICHAEL FARADAY, 1831", BR), {"kind": "text", "p": {"ml": "1831 · ഫാരഡെ", "en": "THE IDEA BEHIND EVERY POWER STATION", "icon": "bolt", "col": BR}}),
        B("അതായത് ഇടുക്കിയിൽ വെള്ളത്തിന്റെ ചലനം കാന്തത്തിന്റെ ചലനമായി, പിന്നെ വൈദ്യുതിയായി മാറുന്നു.", ("വെള്ളം → കാന്തം → വൈദ്യുതി", "WATER → MAGNET → ELECTRICITY", SE), {"kind": "flow", "p": {"carry": "charge", "nodes": CHAIN[:4]}}),
        B("ഇനി ഈ വൈദ്യുതി നമ്മുടെ വീട്ടിലെത്തണം.", ("വീട്ടിലേക്ക്", "NOW IT HAS TO REACH YOUR HOME", LF)),
        B("പക്ഷേ വൈദ്യുതി വയറിലൂടെ പോകുമ്പോൾ കുറച്ച് ചൂടായി നഷ്ടപ്പെടും.", ("ചൂടായി നഷ്ടം", "SOME IS LOST AS HEAT ON THE WAY", OR)),
        B("കറന്റ് കൂടുതലാണെങ്കിൽ നഷ്ടം വളരെ കൂടുതലായിരിക്കും.", ("വലിയ കറന്റ് = വലിയ നഷ്ടം", "BIG CURRENT, BIG LOSS", RD)),
        B("കറന്റ് പകുതിയാക്കിയാൽ നഷ്ടം നാലിലൊന്നായി കുറയും.", ("പകുതി കറന്റ് → നാലിലൊന്ന് നഷ്ടം", "HALF THE CURRENT, A QUARTER OF THE LOSS", LF), {"kind": "bars", "p": {"unit": "%", "items": [{"ml": "വലിയ കറന്റ്", "en": "FULL CURRENT", "v": 100, "col": RD}, {"ml": "പകുതി കറന്റ്", "en": "HALF THE CURRENT", "v": 25, "col": LF}]}}),
        B("അതിനുള്ള വഴിയാണ് വോൾട്ടേജ് കൂട്ടുക.", ("വോൾട്ടേജ് കൂട്ടുക", "RAISE THE VOLTAGE", OR)),
        B("വോൾട്ടേജ് കൂട്ടിയാൽ അതേ ശക്തി കുറഞ്ഞ കറന്റിൽ കൊണ്ടുപോകാം.", ("ഉയർന്ന വോൾട്ടേജ്, കുറഞ്ഞ കറന്റ്", "HIGH VOLTAGE, LOW CURRENT", RD)),
        B("അത് ചെയ്യുന്നത് ട്രാൻസ്ഫോർമർ എന്ന ഉപകരണമാണ്.", ("ട്രാൻസ്ഫോർമർ", "THE TRANSFORMER", DK), {"kind": "transformer", "p": {}}),
        B("ഇതിന് രണ്ട് ചുരുളുകളുണ്ട്, ഒന്നിൽ ചുറ്റുകൾ കുറവ്, മറ്റതിൽ കൂടുതൽ.", ("ചുറ്റുകൾ കൂടുതൽ", "MORE TURNS ON THE OUTPUT SIDE", GD)),
        B("ചുറ്റുകളുടെ കണക്കനുസരിച്ച് വോൾട്ടേജ് കൂടും, കറന്റ് കുറയും.", ("വോൾട്ടേജ് ↑ കറന്റ് ↓", "VOLTAGE UP, CURRENT DOWN", RD)),
        B("ഇത് പ്രവർത്തിക്കുന്നത് ഒരു പ്രത്യേക തരം വൈദ്യുതി കൊണ്ടാണ്, ആൾട്ടർനേറ്റിങ് കറന്റ്.", ("എസി: ആൾട്ടർനേറ്റിങ് കറന്റ്", "ALTERNATING CURRENT", BL)),
        B("നമ്മുടെ നാട്ടിൽ അത് ഒരു സെക്കൻഡിൽ അമ്പത് തവണ ദിശ മാറുന്നു, അതായത് അമ്പത് ഹെർട്സ്.", ("സെക്കൻഡിൽ 50 തവണ", "50 HERTZ: IT FLIPS 50 TIMES A SECOND", BL), {"kind": "stat", "p": {"value": 50, "suffix": " Hz", "ml": "സെക്കൻഡിൽ 50 തവണ", "en": "THE DIRECTION OF CURRENT FLIPS", "icon": "bolt"}}),
        B("മാറുന്ന വൈദ്യുതിയാണ് ട്രാൻസ്ഫോർമറിന് വേണ്ടത്, അതുകൊണ്ടാണ് നമ്മൾ എസി ഉപയോഗിക്കുന്നത്.", ("ട്രാൻസ്ഫോർമറിന് എസി വേണം", "TRANSFORMERS NEED AC", DK)),
        B("ഉയർന്ന വോൾട്ടേജിൽ വൈദ്യുതി വലിയ ടവറുകളിലൂടെ നൂറുകണക്കിന് കിലോമീറ്റർ സഞ്ചരിക്കുന്നു.", ("ഹൈ വോൾട്ടേജ് ലൈൻ", "HIGH-VOLTAGE LINES, HUNDREDS OF KM", RD), {"kind": "flow", "p": {"carry": "charge", "nodes": CHAIN[3:]}}),
        B("നമ്മുടെ നാട്ടിലെത്തുമ്പോൾ സബ്സ്റ്റേഷനിൽ വോൾട്ടേജ് ഘട്ടം ഘട്ടമായി കുറയ്ക്കുന്നു.", ("സബ്സ്റ്റേഷൻ", "SUBSTATIONS STEP IT DOWN", GD)),
        B("അവസാനം തെരുവിലെ പോസ്റ്റിലെ ട്രാൻസ്ഫോർമർ അത് ഇരുനൂറ്റി മുപ്പത് വോൾട്ടാക്കി വീടുകളിലേക്ക് തരുന്നു.", ("230 V · വീടുകളിലേക്ക്", "THE POLE TRANSFORMER: 230 V FOR HOMES", LF)),
        B("ഇതുവരെ പറഞ്ഞ വഴി ഒറ്റ നോട്ടത്തിൽ ഇതാണ്.", ("ഒറ്റ നോട്ടത്തിൽ", "THE WHOLE JOURNEY", BR), {"kind": "flow", "p": {"carry": "charge", "nodes": CHAIN}}),
        B("ഇനി നിങ്ങളുടെ വീട്ടിലെ മീറ്ററിലേക്ക് വരാം.", ("മീറ്റർ", "THE METER AT HOME", DK), {"kind": "home", "p": {"cams": [{"atb": 0, "x": 500, "y": 520, "z": 1.0}, {"atb": 1, "x": 860, "y": 560, "z": 2.2}, {"atb": 2, "x": 500, "y": 520, "z": 1.0}, {"atb": 3, "x": 150, "y": 330, "z": 2.0}, {"atb": 4, "x": 800, "y": 320, "z": 2.0}, {"atb": 5, "x": 500, "y": 520, "z": 1.0}],
                "items": [{"icon": "led", "ml": "≈ 111 മണിക്കൂർ", "en": "9 W LED BULB", "atb": 3, "col": "#2f7d4f"}, {"icon": "fan", "ml": "≈ 17 മണിക്കൂർ", "en": "60 W FAN", "atb": 5, "col": "#2d6fa0"}, {"icon": "ac", "ml": "≈ 1 മണിക്കൂർ", "en": "1000 W AC", "atb": 4}], "atb": {"meter": 1.1}}}),
        B("ബില്ലിൽ കാണുന്ന ഒരു യൂണിറ്റ് എന്നാൽ ഒരു കിലോവാട്ട് മണിക്കൂറാണ്.", ("1 യൂണിറ്റ് = 1 kWh", "ONE UNIT IS ONE KILOWATT-HOUR", OR)),
        B("ആയിരം വാട്ട് ശക്തിയുള്ള ഉപകരണം ഒരു മണിക്കൂർ ഓടിയാൽ ഒരു യൂണിറ്റ് ആകും.", ("1000 W × 1 മണിക്കൂർ", "1000 WATTS FOR ONE HOUR", OR)),
        B("ഒൻപത് വാട്ടിന്റെ എൽഇഡി ബൾബ് ഏകദേശം നൂറ്റി പതിനൊന്ന് മണിക്കൂർ കത്തിയാലേ ഒരു യൂണിറ്റ് ആകൂ.", ("എൽഇഡി: ≈ 111 മണിക്കൂർ", "AN LED BULB TAKES ABOUT 111 HOURS", LF)),
        B("ഒരു എസി ഒരു മണിക്കൂർ കൊണ്ട് തന്നെ ഒരു യൂണിറ്റിനടുത്ത് എടുക്കും.", ("എസി: ≈ 1 മണിക്കൂർ", "AN AC USES ABOUT A UNIT IN ONE HOUR", RD)),
        B("അതുകൊണ്ടാണ് വേനലിൽ കറന്റ് ബിൽ ഉയരുന്നത്.", ("വേനലിൽ ബിൽ കൂടും", "WHY SUMMER BILLS JUMP", RD)),
        B("കേരളത്തിൽ ആവശ്യമായ വൈദ്യുതിയുടെ വലിയൊരു ഭാഗം പുറത്തുനിന്ന് വാങ്ങുന്നുണ്ട്.", ("പുറത്തുനിന്ന് വാങ്ങുന്നു", "KERALA BUYS MUCH OF ITS POWER FROM OUTSIDE", GD)),
        B("കാരണം ജലവൈദ്യുതി ആശ്രയിക്കുന്നത് മൺസൂൺ മഴയെയാണ്, വേനലിൽ ഡാമുകളിൽ വെള്ളം കുറയും.", ("ഡാമിന് മഴ വേണം", "HYDRO POWER NEEDS THE MONSOON", SE), {"kind": "text", "p": {"ml": "മഴ → ഡാം → വൈദ്യുതി", "en": "ELECTRICITY AND RAIN ARE CONNECTED", "icon": "cloud", "col": SE}}),
        B("അപ്പോൾ നിങ്ങളുടെ ബൾബിന് പിന്നിൽ ഒരു മല, ഒരു മഴ, ഒരു കാന്തം, ഒരു കമ്പിച്ചുരുൾ ഉണ്ട്.", ("ബൾബിന് പിന്നിൽ", "BEHIND THE BULB", BR)),
        B("വൈദ്യുതി ലാഭിക്കുന്നത് വെള്ളം ലാഭിക്കുന്നതിന് തുല്യമാണ്.", ("ലാഭിക്കൂ", "SAVING POWER SAVES WATER TOO", LF)),
        B("നിങ്ങളുടെ വീട്ടിലെ ഏറ്റവും കൂടുതൽ വൈദ്യുതി എടുക്കുന്ന ഉപകരണം ഏതാണ്?", None, {"kind": "outro", "p": {"ml": "നിങ്ങളുടെ വീട്ടിൽ ഏറ്റവും കൂടുതൽ കറന്റ് എടുക്കുന്നത് എന്താണ്?", "en": "WHICH APPLIANCE USES THE MOST POWER AT YOUR HOME?"}}),
        B("താഴെ കമന്റ് ചെയ്യൂ, ഇതുപോലുള്ള വീഡിയോകൾക്കായി സയൻസ് ചായ സബ്സ്ക്രൈബ് ചെയ്യൂ."),
    ],
}

SHORT1 = {
    "id": "electricity_s1", "orient": "tall", "mood": "curious", "title_ml": "കറന്റ് ബില്ലിലെ ഒരു യൂണിറ്റ് എന്നാൽ എന്താണ്? #Shorts", "title_en": "What is one unit on your electricity bill?",
    "thumb": {"ml": "ഒരു യൂണിറ്റ് എന്നാൽ?", "en": "WHAT IS 1 UNIT?", "hero": "meter"},
    "beats": [
        B("കറന്റ് ബില്ലിലെ ഒരു യൂണിറ്റ് എന്നാൽ എന്താണ്?", ("1 യൂണിറ്റ്?", "WHAT IS ONE UNIT?", DK), {"kind": "home", "p": {"cams": [{"atb": 0, "x": 500, "y": 520, "z": 1.0}, {"atb": 1, "x": 860, "y": 560, "z": 2.2}, {"atb": 2, "x": 500, "y": 520, "z": 1.0}, {"atb": 3, "x": 150, "y": 330, "z": 2.0}, {"atb": 4, "x": 460, "y": 260, "z": 1.9}, {"atb": 5, "x": 800, "y": 320, "z": 2.0}],
                "items": [{"icon": "led", "ml": "≈ 111 മണിക്കൂർ", "en": "9 W LED BULB", "atb": 3, "col": "#2f7d4f"}, {"icon": "fan", "ml": "≈ 17 മണിക്കൂർ", "en": "60 W FAN", "atb": 4, "col": "#2d6fa0"}, {"icon": "ac", "ml": "≈ 1 മണിക്കൂർ", "en": "1000 W AC", "atb": 5}], "atb": {"meter": 1.1}}}),
        B("ഒരു യൂണിറ്റ് എന്നാൽ ഒരു കിലോവാട്ട് മണിക്കൂർ.", ("1 യൂണിറ്റ് = 1 kWh", "ONE KILOWATT-HOUR", OR)),
        B("ആയിരം വാട്ട് ശക്തിയുള്ള ഉപകരണം ഒരു മണിക്കൂർ ഓടിയാൽ ഒരു യൂണിറ്റ്.", ("1000 W × 1 മണിക്കൂർ", "1000 WATTS FOR ONE HOUR", OR)),
        B("ഒൻപത് വാട്ടിന്റെ എൽഇഡി ബൾബിന് നൂറ്റി പതിനൊന്ന് മണിക്കൂർ വേണം.", ("എൽഇഡി ≈ 111 മണിക്കൂർ", "AN LED BULB: 111 HOURS", LF)),
        B("അറുപത് വാട്ടിന്റെ ഫാൻ ഏകദേശം പതിനേഴ് മണിക്കൂർ.", ("ഫാൻ ≈ 17 മണിക്കൂർ", "A FAN: ABOUT 17 HOURS", BL)),
        B("എസി ആകട്ടെ ഏകദേശം ഒരു മണിക്കൂർ!", ("എസി ≈ 1 മണിക്കൂർ", "AN AC: ABOUT ONE HOUR", RD)),
        B("അതാണ് ബിൽ കൂടുന്നതിന്റെ രഹസ്യം.", None, {"kind": "outro", "p": {"ml": "ബിൽ കൂട്ടുന്നത് എസിയാണ്!", "en": "THE AC IS THE BILL MAKER", "sub": "കൂടുതൽ കാണാൻ സബ്സ്ക്രൈബ് ചെയ്യൂ"}}),
    ],
}

SHORT2 = {
    "id": "electricity_s2", "orient": "tall", "mood": "curious", "title_ml": "ഇടുക്കി ഡാമിന്റെ വൈദ്യുതി ഉണ്ടാകുന്നത് പാറയ്ക്കുള്ളിൽ #Shorts", "title_en": "Idukki's power is made inside a mountain",
    "thumb": {"ml": "പാറയ്ക്കുള്ളിലെ പവർഹൗസ്", "en": "INSIDE THE MOUNTAIN", "hero": "dam"},
    "beats": [
        B("ഇടുക്കിയിലെ വൈദ്യുതി ഉണ്ടാകുന്നത് ഒരു മലയ്ക്കുള്ളിലാണ്.", ("മലയ്ക്കുള്ളിൽ!", "MADE INSIDE A MOUNTAIN", BR), {"kind": "damx", "p": {"cams": [{"atb": 0, "x": 500, "y": 540, "z": 1.0}, {"atb": 0.5, "x": 380, "y": 420, "z": 1.9}, {"atb": 1, "x": 580, "y": 640, "z": 1.7}, {"atb": 2, "x": 910, "y": 830, "z": 2.5}],
                "atb": {"height": 0.6, "tunnel": 1.0, "flow": 1.0, "house": 2.0, "spin": 2.3}}}),
        B("ഡാമിൽ കെട്ടിനിർത്തിയ വെള്ളം തുരങ്കത്തിലൂടെ താഴേക്ക് ഒഴുകും.", ("തുരങ്കത്തിലൂടെ", "WATER RUSHES DOWN A TUNNEL", SE)),
        B("മൂലമറ്റത്തെ ഭൂഗർഭ പവർഹൗസിൽ അത് ടർബൈനിൽ വീഴും.", ("മൂലമറ്റം പവർഹൗസ്", "THE UNDERGROUND POWER HOUSE", DK)),
        B("ടർബൈൻ ജനറേറ്ററിനെ കറക്കും.", ("ജനറേറ്റർ", "THE TURBINE SPINS THE GENERATOR", RD), {"kind": "generator", "p": {"speed": 3.0}}),
        B("കാന്തം കറങ്ങുമ്പോൾ കമ്പിയിൽ വൈദ്യുതി ഉണ്ടാകും.", ("കാന്തം + കമ്പി = വൈദ്യുതി", "MAGNET + COIL = ELECTRICITY", GD)),
        B("ആറ് ടർബൈനുകൾ ചേർന്ന് ഏഴുന്നൂറ്റി എൺപത് മെഗാവാട്ട്!", ("780 MW", "SIX TURBINES TOGETHER", OR), {"kind": "stat", "p": {"value": 780, "suffix": " MW", "ml": "ഇടുക്കി", "en": "6 × 130 MW", "icon": "bolt"}}),
        B("വെള്ളത്തിൽ നിന്ന് വെളിച്ചത്തിലേക്ക്!", None, {"kind": "outro", "p": {"ml": "വെള്ളം → വെളിച്ചം", "en": "FROM WATER TO LIGHT", "sub": "കൂടുതൽ കാണാൻ സബ്സ്ക്രൈബ് ചെയ്യൂ"}}),
    ],
}

SHORT3 = {
    "id": "electricity_s3", "orient": "tall", "mood": "curious", "title_ml": "ഹൈ വോൾട്ടേജ് ലൈനിൽ ഇരിക്കുന്ന പക്ഷിക്ക് ഷോക്ക് അടിക്കാത്തത് എന്തുകൊണ്ട്? #Shorts", "title_en": "Why birds on high-voltage wires don't get shocked",
    "thumb": {"ml": "പക്ഷിക്ക് ഷോക്ക് ഇല്ല!", "en": "WHY NO SHOCK?", "hero": "bird"},
    "beats": [
        B("ഹൈ വോൾട്ടേജ് ലൈനിൽ ഇരിക്കുന്ന പക്ഷിക്ക് ഷോക്ക് അടിക്കാത്തത് എന്തുകൊണ്ട്?", ("ഷോക്ക് ഇല്ല!", "WHY NO SHOCK?", DK), {"kind": "crow", "p": {
            "cams": [{"atb": 0, "x": 500, "y": 430, "z": 1.0}, {"atb": 0.5, "x": 530, "y": 300, "z": 2.1}, {"atb": 1, "x": 500, "y": 400, "z": 3.1},
                     {"atb": 2, "x": 500, "y": 425, "z": 2.4}, {"atb": 3, "x": 530, "y": 470, "z": 1.8}, {"atb": 4, "x": 480, "y": 330, "z": 2.2}],
            "atb": {"badges": 2.05, "meter": 3.0, "ok": 3.35, "danger": 4.25}}}),
        B("പക്ഷിയുടെ രണ്ട് കാലുകളും ഒരേ കമ്പിയിലാണ്.", ("ഒരേ കമ്പി", "BOTH FEET ON THE SAME WIRE", BR)),
        B("അതുകൊണ്ട് രണ്ട് കാലിലും വോൾട്ടേജ് ഒരുപോലെയാണ്.", ("ഒരേ വോൾട്ടേജ്", "THE SAME VOLTAGE AT BOTH FEET", OR)),
        B("വോൾട്ടേജ് വ്യത്യാസം ഇല്ലെങ്കിൽ കറന്റ് ഒഴുകില്ല.", ("വ്യത്യാസമില്ല, കറന്റില്ല", "NO DIFFERENCE, NO CURRENT", LF)),
        B("പക്ഷി ഒരു കാൽ നിലത്തേക്കോ മറ്റൊരു കമ്പിയിലോ തൊട്ടാൽ അപകടമാണ്.", ("അപകടം!", "TOUCH THE GROUND AND IT FLOWS", RD)),
        B("അതുകൊണ്ട് മനുഷ്യൻ ഒരിക്കലും പരീക്ഷിക്കരുത്!", None, {"kind": "outro", "p": {"ml": "വ്യത്യാസമില്ലെങ്കിൽ കറന്റില്ല!", "en": "NO DIFFERENCE, NO CURRENT", "sub": "കൂടുതൽ കാണാൻ സബ്സ്ക്രൈബ് ചെയ്യൂ"}}),
    ],
}

FACTS = [
    "Idukki arch dam is about 169 m high; the installed capacity is 780 MW (6 x 130 MW Pelton turbines) in an underground power house at Moolamattom (KSEB / Wikipedia: Idukki Dam).",
    "Faraday discovered electromagnetic induction in 1831. India's mains frequency is 50 Hz; household supply is 230 V single phase. One unit is one kilowatt-hour.",
    "Power lost in a line is I squared times R, so halving the current cuts the loss to a quarter.",
    "Kerala imports a large share of its electricity (KSEB statements); hydro generation depends on monsoon inflow.",
]
VIDEOS = [LONG, SHORT1, SHORT2, SHORT3]
