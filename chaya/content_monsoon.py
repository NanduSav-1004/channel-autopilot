"""Science Chaya: the monsoon video (long) and its three Shorts, as data: every beat is ONE sentence of narration, an optional label card and, where a
new picture starts, the scene that shows it. `atb` gives the beat (counted from the scene's first beat) at which a part of a scene starts.
Facts and their sources are in FACTS (they go into the video descriptions)."""
BR, LF, SE, OR, BL, GD, DK, RD, GR = "#7b4a2b", "#2f7d4f", "#1f8aa8", "#c45a2a", "#2d6fa0", "#a8782f", "#4a2a17", "#c8442f", "#5b7189"


def B(text, card=None, scene=None):
    return {"t": text, "card": card, "scene": scene}


TERRAIN_TAG_ANAMUDI = {"u": 0.74, "v": 0.12, "ml": "ആനമുടി 2,695 മീ", "en": "ANAMUDI", "w": 400}

LONG = {
    "id": "monsoon_long", "orient": "wide", "mood": "curious",
    "title_ml": "കേരളത്തിൽ മഴ കൃത്യമായി വരുന്നത് എങ്ങനെ? | മൺസൂണിന്റെ ശാസ്ത്രം",
    "title_en": "How does the monsoon reach Kerala on time? The science of the monsoon",
    "thumb": {"ml": "മഴയ്ക്ക് തീയതി", "en": "HOW THE MONSOON ARRIVES", "hero": "terrain"},
    "comment": "നിങ്ങളുടെ നാട്ടിൽ ഈ വർഷം മഴ ആദ്യം എത്തിയത് ഏത് ദിവസമായിരുന്നു?",
    "beats": [
        B("കേരളത്തിൽ മഴ എത്തുന്നത് ഏകദേശം ജൂൺ ഒന്നിനാണ്.", ("ജൂൺ 1", "THE DAY THE RAIN ARRIVES", BR), {"kind": "text", "p": {"ml": "ജൂൺ 1", "en": "THE DAY THE RAIN ARRIVES", "icon": "drop", "col": BL}}),
        B("എല്ലാ വർഷവും, ഒരാഴ്ച മുന്നോട്ടോ പിന്നോട്ടോ.", ("എല്ലാ വർഷവും", "EVERY YEAR, GIVE OR TAKE A WEEK", LF)),
        B("ഇതെങ്ങനെ സാധിക്കുന്നു?", ("ഇതെങ്ങനെ?", "HOW?", DK), {"kind": "text", "p": {"ml": "ഇതെങ്ങനെ?", "en": "HOW DOES IT KEEP TIME?", "icon": "cloud", "col": DK}}),
        B("ഉത്തരം കടലിലാണ്.", ("ഉത്തരം: കടൽ", "THE ANSWER IS THE SEA", SE), {"kind": "terrain", "p": {"atb": {"heat": 1.0, "wind": 5.0, "cool": 15.2, "cloud": 16.0, "rain": 17.5}, "zoom": {"cx": 0.22, "cy": 0.62, "s": 1.5, "at": 0.0, "dur": 0.12}, "tags": []}}),
        B("വേനലിൽ കര പെട്ടെന്ന് ചൂടാകും.", ("ചൂടാകുന്ന കര", "LAND HEATS UP FAST", OR)),
        B("കടൽ പതുക്കെയേ ചൂടാകൂ, കാരണം വെള്ളത്തിന് ചൂട് സംഭരിക്കാനുള്ള കഴിവ് കൂടുതലാണ്.", ("കടൽ പതുക്കെ ചൂടാകും", "WATER HEATS SLOWLY", SE)),
        B("അതുകൊണ്ട് മെയ് മാസത്തിൽ കര കടലിനേക്കാൾ വളരെയധികം ചൂടാകുന്നു.", ("കര > കടൽ", "LAND IS HOTTER THAN SEA", OR)),
        B("ചൂടുള്ള വായു മുകളിലേക്ക് ഉയരും.", ("ചൂടുള്ള വായു ഉയരുന്നു", "HOT AIR RISES", OR)),
        B("താഴെ വായു കുറയും, അതായത് മർദ്ദം കുറയും.", ("കുറഞ്ഞ മർദ്ദം", "LOW PRESSURE", DK)),
        B("ആ ഒഴിവ് നികത്താൻ കടലിലെ വായു കരയിലേക്ക് ഓടിയെത്തും.", ("കാറ്റ് വീശുന്നു", "THE SEA AIR RUSHES IN", SE)),
        B("ഈ വായുവിൽ നിറയെ നീരാവിയുണ്ട്, കാരണം അത് ആഴ്ചകളോളം ഇന്ത്യൻ മഹാസമുദ്രത്തിന് മുകളിലൂടെ വന്നതാണ്.", ("ഈർപ്പമുള്ള കാറ്റ്", "MOIST WIND FROM THE INDIAN OCEAN", SE)),
        B("ഇതാണ് തെക്കുപടിഞ്ഞാറൻ മൺസൂൺ.", ("തെക്കുപടിഞ്ഞാറൻ മൺസൂൺ", "THE SOUTH-WEST MONSOON", BL)),
        B("മൺസൂൺ എന്ന പേര് വന്നത് മൗസിം എന്ന അറബി വാക്കിൽ നിന്നാണ്, അർത്ഥം കാലം.", ("മൗസിം = കാലം", "ARABIC 'MAUSIM' MEANS SEASON", GD), {"kind": "text", "p": {"ml": "മൗസിം = കാലം", "en": "MONSOON COMES FROM THE ARABIC WORD FOR SEASON", "icon": "sun", "col": GD}}),
        B("ഈ കാറ്റ് ആദ്യം തൊടുന്നത് ഇന്ത്യയുടെ തെക്കുപടിഞ്ഞാറൻ മുനമ്പിലാണ്, അതായത് കേരളത്തിൽ.", ("ആദ്യം കേരളം", "KERALA GETS IT FIRST", LF), {"kind": "map", "p": {"arrows": True, "shade": "rain", "atb": {"arrows": 0.0, "shade": 1.5, "ridge": 2.0}, "pins": [{"id": "tvm", "ml": "തിരുവനന്തപുരം", "en": "THIRUVANANTHAPURAM", "atb": 0.5, "w": 330}, {"id": "kochi", "ml": "കൊച്ചി", "en": "KOCHI", "atb": 0.8, "w": 250}, {"id": "kozhikode", "ml": "കോഴിക്കോട്", "en": "KOZHIKODE", "atb": 1.1, "w": 290}]}}),
        B("അതുകൊണ്ടാണ് മൺസൂൺ ആദ്യം എത്തുന്നത് കേരളത്തിലാണ്.", ("ജൂൺ 1 ± 7 ദിവസം", "NORMAL ONSET DATE, GIVE OR TAKE A WEEK", BR)),
        B("പിന്നെ അത് വടക്കോട്ട് നീങ്ങി, ഏകദേശം ജൂലൈ എട്ടോടെ ഇന്ത്യ മുഴുവൻ എത്തും.", ("ജൂലൈ 8: ഇന്ത്യ മുഴുവൻ", "WHOLE OF INDIA BY ABOUT 8 JULY", BL), {"kind": "text", "p": {"ml": "ജൂൺ 1 → ജൂലൈ 8", "en": "KERALA → THE WHOLE COUNTRY (NORMAL DATES)", "icon": "cloud", "col": BL}}),
        B("കേരളത്തിന്റെ കിഴക്ക് ഒരു വലിയ മതിൽ പോലെ പശ്ചിമഘട്ടം നിൽക്കുന്നു.", ("പശ്ചിമഘട്ടം", "THE WESTERN GHATS", LF), {"kind": "terrain", "p": {"atb": {"wind": 0.0, "lapse": 4.0, "cool": 5.0, "cloud": 6.8, "rain": 9.0, "river": 12.0, "ground": 13.0}, "tags": [dict(TERRAIN_TAG_ANAMUDI, atb=1.0)]}}),
        B("ഏറ്റവും ഉയരമുള്ള കൊടുമുടി ആനമുടി, രണ്ടായിരത്തി അറുനൂറ്റി തൊണ്ണൂറ്റി അഞ്ച് മീറ്റർ.", ("ആനമുടി 2,695 മീ", "THE HIGHEST PEAK IN SOUTH INDIA", LF)),
        B("ഈർപ്പം നിറഞ്ഞ കാറ്റ് ഈ മലയിൽ തട്ടും.", ("മലയിൽ തട്ടുന്നു", "THE WIND HITS THE MOUNTAIN", SE)),
        B("പോകാൻ വേറെ വഴിയില്ലാത്തതുകൊണ്ട് അത് ചരിവിലൂടെ മുകളിലേക്ക് കയറും.", ("മുകളിലേക്ക്", "FORCED UP THE SLOPE", SE)),
        B("മുകളിലേക്ക് പോകുമ്പോൾ വായുവിന്റെ മർദ്ദം കുറയും, വായു വികസിക്കും.", ("വികസിക്കുന്ന വായു", "THE AIR EXPANDS", DK)),
        B("വികസിക്കുമ്പോൾ അത് തണുക്കും, ഓരോ കിലോമീറ്റർ ഉയരത്തിലും ഏകദേശം അഞ്ചോ ആറോ ഡിഗ്രി സെൽഷ്യസ്.", ("ഓരോ കി.മീ.ലും ≈ −6°C", "ABOUT 5–6°C COOLER PER KILOMETRE", OR)),
        B("തണുത്ത വായുവിന് നീരാവിയെ പിടിച്ചുനിർത്താനുള്ള കഴിവ് കുറവാണ്.", ("നീരാവി പിടിച്ചുനിർത്താനാവില്ല", "COLD AIR HOLDS LESS VAPOUR", GR)),
        B("അങ്ങനെ നീരാവി ചെറിയ വെള്ളത്തുള്ളികളായി മാറും.", ("വെള്ളത്തുള്ളികൾ", "VAPOUR BECOMES DROPLETS", SE)),
        B("ഇതിനെ ഘനീകരണം എന്ന് പറയും, ആ തുള്ളികൾ ചേർന്നതാണ് മേഘം.", ("ഘനീകരണം → മേഘം", "CONDENSATION MAKES CLOUD", GR)),
        B("തുള്ളികൾ വലുതായി ഭാരം കൂടുമ്പോൾ അവ താഴേക്ക് വീഴും.", ("ഭാരം കൂടുന്ന തുള്ളികൾ", "HEAVY DROPS FALL", BL)),
        B("അതാണ് നമ്മുടെ മുറ്റത്തെ മഴ!", ("മഴ!", "RAIN", BL)),
        B("ഇത് നിങ്ങൾക്ക് വീട്ടിൽ തന്നെ കാണാം: ഒരു ചൂടുള്ള ചായ ഗ്ലാസിന് മുകളിൽ ഒരു തണുത്ത പ്ലേറ്റ് പിടിക്കൂ.", ("ചായ പരീക്ഷണം", "TRY IT WITH A GLASS OF CHAI", BR), {"kind": "tea", "p": {}}),
        B("ചൂടുള്ള ആവി പ്ലേറ്റിൽ തട്ടി തണുത്ത് വെള്ളത്തുള്ളികളാകുന്നു.", ("ആവി → തുള്ളികൾ", "STEAM → DROPS", SE)),
        B("മഴ അതിന്റെ വലിയ രൂപമാണ്.", ("മഴ = വലിയ ചായ പരീക്ഷണം", "RAIN IS THE SAME THING, MUCH BIGGER", BR)),
        B("ആ മഴ നദികളായി ഒഴുകി കടലിലേക്ക് തിരിച്ചുപോകുന്നു.", ("നദികളായി ഒഴുകുന്നു", "RAIN BECOMES RIVERS", SE), {"kind": "terrain", "p": {"atb": {"wind": 0.0, "cool": 0.0, "cloud": 0.0, "rain": 0.0, "river": 0.6, "ground": 2.2, "shadow": 99}, "zoom": {"cx": 0.55, "cy": 0.62, "s": 1.5, "at": 0.0, "dur": 0.2}}}),
        B("ഒരു ഭാഗം മണ്ണിലൂടെ താഴേക്ക് ഊർന്ന് ഭൂഗർഭജലമാകും.", ("ഭൂഗർഭജലം", "SOME SOAKS INTO THE GROUND", LF)),
        B("കേരളത്തിലെ നാൽപ്പത്തിനാല് നദികളും ഈ മഴയിലാണ് ജീവിക്കുന്നത്.", ("44 നദികൾ", "KERALA'S 44 RIVERS LIVE ON IT", SE)),
        B("ഇനി മലയുടെ അങ്ങേ വശത്ത് എന്ത് സംഭവിക്കുമെന്ന് നോക്കാം.", ("മറുവശം", "NOW THE OTHER SIDE", GD), {"kind": "terrain", "p": {"atb": {"wind": 0.0, "cool": 0.0, "cloud": 0.0, "rain": 0.0, "river": 0.0, "shadow": 2.0}, "zoom": {"cx": 0.82, "cy": 0.38, "s": 1.6, "at": 0.0, "dur": 0.18}}}),
        B("കാറ്റിലെ ഈർപ്പത്തിൽ മിക്കതും ഈ വശത്ത് മഴയായി പെയ്തു കഴിഞ്ഞു.", ("ഈർപ്പം തീർന്നു", "MOST MOISTURE IS ALREADY GONE", GR)),
        B("മറുവശത്തേക്ക് ഇറങ്ങുമ്പോൾ ഉണങ്ങിയ വായു ചൂടാകുന്നു.", ("ഇറങ്ങുന്ന വായു ചൂടാകും", "SINKING AIR WARMS UP", OR)),
        B("ചൂടുള്ള ഉണങ്ങിയ വായുവിൽ മേഘങ്ങൾ അലിഞ്ഞു പോകും.", ("മേഘങ്ങൾ അലിയുന്നു", "CLOUDS DISSOLVE", GR)),
        B("അതുകൊണ്ട് അവിടെ മഴ വളരെ കുറവായിരിക്കും, ഇതിനെ മഴനിഴൽ പ്രദേശം എന്ന് പറയും.", ("മഴനിഴൽ പ്രദേശം", "THE RAIN SHADOW", GD)),
        B("ഇടുക്കിയിലെ മറയൂർ ഇതിന് നല്ലൊരു ഉദാഹരണമാണ്.", ("മറയൂർ", "MARAYOOR: A RAIN SHADOW TOWN", GD), {"kind": "map", "p": {"shade": "dry", "arrows": True, "atb": {"arrows": 0.0, "shade": 1.0, "ridge": 0.0}, "pins": [{"id": "munnar", "ml": "മൂന്നാർ", "en": "MUNNAR", "atb": 0.5, "w": 250, "side": -1}, {"id": "marayoor", "ml": "മറയൂർ", "en": "MARAYOOR", "atb": 1.0, "w": 260, "col": GD}]}}),
        B("മൂന്നാറിൽ ധാരാളം മഴ ലഭിക്കുന്നു, അവിടെ നിന്ന് ഏകദേശം നാല്പത് കിലോമീറ്റർ അകലെയാണ് മറയൂർ.", ("ഏകദേശം 40 കി.മീ.", "ABOUT 40 KM APART", LF)),
        B("പക്ഷേ അവിടെ മഴ കുറവാണ്, ചന്ദനമരങ്ങൾ വളരുന്ന നാടാണത്.", ("മഴ കുറവ്, ചന്ദനം", "LITTLE RAIN, SANDALWOOD", GD)),
        B("തമിഴ്‌നാടിന്റെ ഉൾഭാഗങ്ങളിലും ജൂണിൽ മഴ കുറവാണ്, അവർക്ക് ഒക്ടോബർ മുതൽ ഡിസംബർ വരെയുള്ള വടക്കുകിഴക്കൻ മൺസൂണാണ് പ്രധാനം.", ("തമിഴ്‌നാട്ടിൽ മറ്റൊരു മഴക്കാലം", "TAMIL NADU'S RAIN COMES IN OCT–DEC", OR)),
        B("ഇതെല്ലാം എല്ലാ വർഷവും ആവർത്തിക്കും, പക്ഷേ ഒരുപോലെയല്ല.", ("എല്ലാ വർഷവും ഒരുപോലെയല്ല", "NOT THE SAME EVERY YEAR", DK), {"kind": "text", "p": {"ml": "എൽ നിനോ", "en": "WHEN THE SEA WARMS DIFFERENTLY, THE MONSOON CHANGES", "icon": "sun", "col": OR}}),
        B("കടൽ ചൂടാകുന്ന രീതിയിലെ മാറ്റങ്ങൾ, എൽ നിനോ പോലുള്ളവ, മഴയുടെ അളവും തീയതിയും മാറ്റും.", ("എൽ നിനോ", "EL NIÑO CAN WEAKEN THE MONSOON", OR)),
        B("അതുകൊണ്ടാണ് ചില വർഷങ്ങളിൽ മൺസൂൺ വൈകുന്നത്.", ("ചിലപ്പോൾ വൈകും", "SOMETIMES IT IS LATE", DK)),
        B("കേരളത്തിൽ ഒരു രണ്ടാം മഴക്കാലവും ഉണ്ട്, ഒക്ടോബർ നവംബറിലെ തുലാവർഷം.", ("തുലാവർഷം", "THE SECOND RAINY SEASON", BL), {"kind": "text", "p": {"ml": "തുലാവർഷം", "en": "THE OCTOBER–NOVEMBER RAINS", "icon": "cloud", "col": BL}}),
        B("അപ്പോൾ ചുരുക്കി പറയാം: ചൂടുള്ള കര, ഈർപ്പമുള്ള കടൽക്കാറ്റ്, ഒരു വലിയ മല.", ("ചുരുക്കത്തിൽ", "IN SHORT", BR), {"kind": "flow", "p": {"carry": "water", "nodes": [{"icon": "sun", "ml": "ചൂടുള്ള കര", "en": "HOT LAND"}, {"icon": "drop", "ml": "ഈർപ്പമുള്ള കാറ്റ്", "en": "MOIST WIND"}, {"icon": "mountain", "ml": "പശ്ചിമഘട്ടം", "en": "THE GHATS"}, {"icon": "cloud", "ml": "മേഘം", "en": "CLOUD"}, {"icon": "drop", "ml": "മഴ", "en": "RAIN"}]}}),
        B("ഇതാണ് കേരളത്തിന്റെ മഴയുടെ സൂത്രവാക്യം.", ("മഴയുടെ സൂത്രവാക്യം", "THE RECIPE FOR KERALA'S RAIN", BR)),
        B("നിങ്ങളുടെ നാട്ടിൽ ഈ വർഷം മഴ ആദ്യം എത്തിയത് ഏത് ദിവസമായിരുന്നു?", None, {"kind": "outro", "p": {"ml": "നിങ്ങളുടെ നാട്ടിൽ ഈ വർഷം മഴ ആദ്യം എത്തിയത് ഏത് ദിവസം?", "en": "WHEN DID THE RAIN FIRST ARRIVE WHERE YOU LIVE?"}}),
        B("താഴെ കമന്റ് ചെയ്യൂ, ഇതുപോലുള്ള വീഡിയോകൾക്കായി സയൻസ് ചായ സബ്സ്ക്രൈബ് ചെയ്യൂ."),
    ],
}

SHORT1 = {
    "id": "monsoon_s1", "orient": "tall", "mood": "curious", "title_ml": "കേരളത്തിൽ മഴ ജൂൺ 1-ന് എത്തുന്നത് എങ്ങനെ? #Shorts", "title_en": "How does the rain reach Kerala on 1 June?",
    "thumb": {"ml": "മഴയ്ക്ക് തീയതി?", "en": "WHY JUNE 1?", "hero": "terrain"},
    "beats": [
        B("കേരളത്തിൽ മഴ എത്തുന്നത് ഏകദേശം ജൂൺ ഒന്നിനാണ്, എല്ലാ വർഷവും.", ("ജൂൺ 1", "THE DAY THE RAIN ARRIVES", BR), {"kind": "text", "p": {"ml": "ജൂൺ 1", "en": "EVERY YEAR, GIVE OR TAKE A WEEK", "icon": "drop", "col": BL}}),
        B("ഇതെങ്ങനെ സാധിക്കുന്നു?", ("ഇതെങ്ങനെ?", "HOW?", DK)),
        B("ഉത്തരം കടലിലാണ്.", ("ഉത്തരം: കടൽ", "THE ANSWER IS THE SEA", SE), {"kind": "terrain", "p": {"atb": {"heat": 1.0, "wind": 3.0, "lapse": 4.5, "cool": 5.0, "cloud": 5.5, "rain": 6.5, "shadow": 8.5}}}),
        B("വേനലിൽ കര ചൂടാകുമ്പോൾ, അറബിക്കടലിൽ നിന്ന് ഈർപ്പം നിറഞ്ഞ കാറ്റ് കരയിലേക്ക് വീശും.", ("ഈർപ്പമുള്ള കാറ്റ്", "MOIST WIND FROM THE ARABIAN SEA", SE)),
        B("ആ കാറ്റ് പശ്ചിമഘട്ടത്തിൽ തട്ടി മുകളിലേക്ക് ഉയരും.", ("പശ്ചിമഘട്ടം", "THE WESTERN GHATS", LF)),
        B("ഉയരുമ്പോൾ തണുക്കും.", ("തണുക്കുന്നു", "IT COOLS", OR)),
        B("തണുക്കുമ്പോൾ മേഘമാകും.", ("മേഘം", "A CLOUD FORMS", GR)),
        B("ആ മേഘം പിന്നെ മഴയായി നമ്മുടെ മുറ്റത്ത്!", ("മഴ!", "RAIN", BL)),
        B("മലയുടെ മറുവശത്താകട്ടെ, മഴ കുറവാണ്.", ("മറുവശത്ത് മഴ കുറവ്", "THE OTHER SIDE STAYS DRY", GD)),
        B("ഇതാണ് മൺസൂൺ.", ("മൺസൂൺ", "MONSOON", BL)),
        B("ഇതുപോലുള്ളവ കാണാൻ സയൻസ് ചായ സബ്സ്ക്രൈബ് ചെയ്യൂ.", None, {"kind": "outro", "p": {"ml": "മഴ വരുന്ന വഴി ഇപ്പോൾ അറിയാം!", "en": "NOW YOU KNOW HOW THE RAIN COMES", "sub": "കൂടുതൽ കാണാൻ സബ്സ്ക്രൈബ് ചെയ്യൂ"}}),
    ],
}

SHORT2 = {
    "id": "monsoon_s2", "orient": "tall", "mood": "curious", "title_ml": "മൂന്നാറിൽ പേമാരി, മറയൂരിൽ ചന്ദനം: ഒരേ മല, രണ്ട് കാലാവസ്ഥ #Shorts", "title_en": "Munnar and Marayoor: one mountain, two climates",
    "thumb": {"ml": "ഒരേ മല, രണ്ട് മഴ", "en": "RAIN SHADOW", "hero": "map"},
    "beats": [
        B("മൂന്നാറും മറയൂരും തമ്മിൽ ഏകദേശം നാല്പത് കിലോമീറ്റർ മാത്രം.", ("40 കി.മീ. മാത്രം", "ONLY ABOUT 40 KM APART", LF), {"kind": "map", "p": {"shade": "dry", "arrows": True, "atb": {"arrows": 0.0, "shade": 3.0, "ridge": 0.0}, "pins": [{"id": "munnar", "ml": "മൂന്നാർ", "en": "MUNNAR", "atb": 0.3, "w": 250, "side": -1}, {"id": "marayoor", "ml": "മറയൂർ", "en": "MARAYOOR", "atb": 0.6, "w": 260, "col": GD}]}}),
        B("പക്ഷേ ഒരിടത്ത് ധാരാളം മഴ, മറ്റൊരിടത്ത് വളരെ കുറവ്.", ("ഒരിടത്ത് മഴ, ഒരിടത്ത് വരൾച്ച", "WET HERE, DRY THERE", GD)),
        B("രഹസ്യം ആ രണ്ട് നാടിനും ഇടയിലെ പശ്ചിമഘട്ടമാണ്.", ("പശ്ചിമഘട്ടം", "THE WESTERN GHATS IN BETWEEN", LF), {"kind": "terrain", "p": {"atb": {"wind": 0.0, "lapse": 9.0, "cool": 1.0, "cloud": 2.0, "rain": 3.0, "shadow": 5.0}, "zoom": {"cx": 0.74, "cy": 0.34, "s": 1.5, "at": 0.0, "dur": 0.15}}}),
        B("ഈർപ്പമുള്ള കാറ്റ് മലയിൽ തട്ടി ഉയർന്ന് ഒരു വശത്ത് മഴയായി പെയ്യും.", ("ഒരു വശത്ത് മഴ", "RAIN FALLS ON ONE SIDE", BL)),
        B("മറുവശത്തേക്ക് ഇറങ്ങുന്ന വായുവിൽ ഈർപ്പം ബാക്കിയില്ല.", ("ഈർപ്പം ബാക്കിയില്ല", "THE MOISTURE IS GONE", GR)),
        B("അത് ചൂടാകുകയും ചെയ്യും, അതുകൊണ്ട് മേഘം പോലും ഉണ്ടാകില്ല.", ("ചൂടുള്ള ഉണങ്ങിയ വായു", "WARM, DRY AIR", OR)),
        B("ഇതാണ് മഴനിഴൽ പ്രദേശം.", ("മഴനിഴൽ", "THE RAIN SHADOW", GD)),
        B("മറയൂർ ചന്ദനമരങ്ങൾ വളരുന്ന നാടായത് അങ്ങനെയാണ്.", ("മറയൂർ ചന്ദനം", "THAT IS WHY SANDALWOOD GROWS THERE", GD)),
        B("ഒരു മല ഒരു നാടിന്റെ കാലാവസ്ഥ തന്നെ മാറ്റും!", None, {"kind": "outro", "p": {"ml": "ഒരു മല, രണ്ട് കാലാവസ്ഥ!", "en": "ONE MOUNTAIN, TWO CLIMATES", "sub": "കൂടുതൽ കാണാൻ സബ്സ്ക്രൈബ് ചെയ്യൂ"}}),
    ],
}

SHORT3 = {
    "id": "monsoon_s3", "orient": "tall", "mood": "curious", "title_ml": "ചായ ഗ്ലാസിൽ മഴയുടെ രഹസ്യം #Shorts", "title_en": "The secret of rain, in a glass of chai",
    "thumb": {"ml": "ചായയിൽ മഴ!", "en": "RAIN IN A GLASS", "hero": "tea"},
    "beats": [
        B("ഒരു ചൂടുള്ള ചായ ഗ്ലാസിൽ നിന്ന് ആവി ഉയരുന്നത് കണ്ടിട്ടുണ്ടോ?", ("ചൂടുള്ള ചായ", "HOT CHAI, RISING STEAM", BR), {"kind": "tea", "p": {}}),
        B("അതിന് മുകളിൽ ഒരു തണുത്ത പ്ലേറ്റ് പിടിച്ചു നോക്കൂ.", ("തണുത്ത പ്ലേറ്റ്", "HOLD A COLD PLATE ABOVE IT", SE)),
        B("ആവി പ്ലേറ്റിൽ തട്ടി തണുത്ത് ചെറിയ വെള്ളത്തുള്ളികളാകും.", ("ആവി → വെള്ളത്തുള്ളി", "STEAM → DROPS", SE)),
        B("ഇതിനെ ഘനീകരണം എന്ന് പറയും.", ("ഘനീകരണം", "CONDENSATION", DK)),
        B("ആകാശത്തും ഇതുതന്നെയാണ് സംഭവിക്കുന്നത്.", ("ആകാശത്തും ഇതുതന്നെ", "THE SAME HAPPENS IN THE SKY", BL), {"kind": "terrain", "p": {"atb": {"wind": 0.0, "lapse": 9.0, "cool": 1.0, "cloud": 2.0, "rain": 4.0, "shadow": 99}, "zoom": {"cx": 0.70, "cy": 0.32, "s": 1.6, "at": 0.0, "dur": 0.15}}}),
        B("കടലിൽ നിന്നുള്ള ഈർപ്പമുള്ള വായു മലയിൽ കയറി തണുക്കുന്നു.", ("മലയിൽ കയറി തണുക്കുന്നു", "MOIST AIR CLIMBS AND COOLS", SE)),
        B("നീരാവി തുള്ളികളായി മേഘമാകുന്നു.", ("മേഘം", "CLOUD", GR)),
        B("ആ തുള്ളികൾ വലുതാകുമ്പോൾ മഴ പെയ്യുന്നു.", ("മഴ", "RAIN", BL)),
        B("അപ്പോൾ മഴ ഒരു വലിയ ചായ പരീക്ഷണമാണ്!", None, {"kind": "outro", "p": {"ml": "മഴ = ഒരു വലിയ ചായ പരീക്ഷണം!", "en": "RAIN IS A GIANT CHAI EXPERIMENT", "sub": "കൂടുതൽ കാണാൻ സബ്സ്ക്രൈബ് ചെയ്യൂ"}}),
    ],
}

FACTS = [
    "Normal onset of the monsoon over Kerala is 1 June, give or take about a week (India Meteorological Department).",
    "The monsoon normally covers the whole of India by about 8 July (India Meteorological Department).",
    "Anamudi, 2,695 m, is the highest peak of the Western Ghats / South India (Wikipedia: Anamudi).",
    "Marayoor lies on the eastern, rain-shadow side of the Western Ghats about 40 km from Munnar (Wikipedia: Marayur; munnar.com).",
    "Moist air forced up the Ghats gives very heavy rain on the windward slopes (studies of Kerala rainfall; Valparai/Anaimudi sources).",
    "Natural Earth admin-1 boundaries (public domain) were used for the maps.",
]
VIDEOS = [LONG, SHORT1, SHORT2, SHORT3]
