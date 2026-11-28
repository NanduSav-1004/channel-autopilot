"""Science Chaya batch 9: Kerala's heritage science (Madhava and the Kerala school of mathematics long; laterite, clay pot cooling, Aranmula mirror, coir, tiled roofs, copper vessels Shorts)."""
from chaya.quick import ST, TX, S, lab, lg, rich, sh

MADHAVA = lg(
    "madhava_long", "മാധവൻ: പൈയുടെ അനന്തശ്രേണി കണ്ടെത്തിയ കേരളത്തിലെ ഗണിതശാസ്ത്രജ്ഞൻ", "Madhava of Kerala: the mathematician who found infinite series for pi",
    "യൂറോപ്പിന് 250 വർഷം മുൻപ്!", "MADHAVA OF KERALA", "ഗണിതം ഇഷ്ടമാണെങ്കിൽ നിങ്ങളുടെ ഇഷ്ട ഗണിത വിഷയം ഏതാണ്?", "DO YOU LIKE MATHS? WHICH TOPIC?",
    [
        ("ഇരിങ്ങാലക്കുടയ്ക്ക് അടുത്തുള്ള ഒരു ഗ്രാമത്തിൽ ജീവിച്ച ഒരാൾ ലോകത്തിന്റെ ഗണിതചരിത്രം മാറ്റി.", "ഒരു ഗ്രാമത്തിലെ പ്രതിഭ", "A VILLAGE GENIUS", S(["person", "leaf"], "dusk", label=("മാധവൻ", "MADHAVA"))),
        ("അദ്ദേഹത്തിന്റെ പേര് സംഗമഗ്രാമത്തിലെ മാധവൻ എന്നാണ്.", "സംഗമഗ്രാമ മാധവൻ", "MADHAVA OF SANGAMAGRAMA"),
        ("ഇന്ന് അദ്ദേഹത്തെയും അദ്ദേഹത്തിന്റെ കേരള ഗണിതപാരമ്പര്യത്തെയും നമുക്ക് പരിചയപ്പെടാം.", "കേരള ഗണിതപാരമ്പര്യം", "THE KERALA SCHOOL", TX("മാധവൻ", "MADHAVA", "person", "#4a2a17")),
        ("പതിനാലാം നൂറ്റാണ്ടിലാണ് അദ്ദേഹം ജീവിച്ചിരുന്നത്.", "പതിനാലാം നൂറ്റാണ്ട്", "THE 14TH CENTURY"),
        ("അന്ന് യൂറോപ്പ് ഇരുണ്ട മധ്യകാലത്തിലൂടെ കടന്നുപോവുകയായിരുന്നു.", "അന്ന് യൂറോപ്പിൽ", "WHILE EUROPE WAS IN THE MIDDLE AGES"),
        ("മാധവൻ ഒരു വലിയ ചോദ്യത്തിന് ഉത്തരം തേടി, വൃത്തത്തിന്റെ ചുറ്റളവ് എങ്ങനെ കൃത്യമായി കണ്ടെത്താം?", "വൃത്തത്തിന്റെ ചുറ്റളവ്", "HOW TO MEASURE A CIRCLE", S(["moon"], "sky", text="വൃത്തം")),
        ("ഒരു വൃത്തത്തിന്റെ ചുറ്റളവും വ്യാസവും തമ്മിലുള്ള അനുപാതമാണ് പൈ.", "പൈ = ചുറ്റളവ് ÷ വ്യാസം", "PI IS CIRCUMFERENCE OVER DIAMETER"),
        ("അതിന്റെ വില ഏകദേശം മൂന്ന് ദശാംശം ഒന്ന് നാല് ഒന്ന് അഞ്ച് ഒൻപത് ആണ്.", "≈ 3.14159", "ABOUT 3.14159", ST(3.14159, "", "പൈയുടെ വില", "THE VALUE OF PI", "moon", decimals=5)),
        ("പക്ഷേ ആ സംഖ്യ ഒരിക്കലും അവസാനിക്കില്ല.", "അവസാനിക്കാത്ത സംഖ്യ", "IT NEVER ENDS"),
        ("അത് കൃത്യമായി എഴുതാൻ കഴിയില്ലെങ്കിൽ എത്ര അടുത്തെത്താം എന്നതായിരുന്നു ചോദ്യം.", "എത്ര അടുത്തെത്താം?", "HOW CLOSE CAN WE GET?"),
        ("മാധവൻ ഒരു അത്ഭുത വഴി കണ്ടെത്തി, അനന്തശ്രേണി.", "അനന്തശ്രേണി", "THE INFINITE SERIES", TX("അനന്തശ്രേണി", "INFINITE SERIES", "moon", "#c8442f")),
        ("ഒന്നിൽ നിന്ന് തുടങ്ങി, മൂന്നിലൊന്ന് കുറയ്ക്കുക, അഞ്ചിലൊന്ന് കൂട്ടുക, ഏഴിലൊന്ന് കുറയ്ക്കുക, അങ്ങനെ അനന്തമായി തുടരുക.", "1 − 1/3 + 1/5 − 1/7 …", "ADD, SUBTRACT, FOREVER"),
        ("ഈ കൂട്ടലും കുറയ്ക്കലും എത്ര കൂടുതൽ ചെയ്യുന്നോ ഉത്തരം പൈയുടെ നാലിലൊന്നിനോട് അടുത്തുവരും.", "ഉത്തരം π/4 ലേക്ക്", "THE ANSWER CREEPS TO PI OVER FOUR"),
        ("അതിനെ നാല് കൊണ്ട് ഗുണിച്ചാൽ പൈ കിട്ടും.", "× 4 = π", "TIMES FOUR GIVES PI"),
        ("ഇത് യൂറോപ്പിൽ ഗ്രിഗറിയും ലൈബ്നിറ്റ്സും കണ്ടെത്തുന്നതിന് ഏകദേശം രണ്ടര നൂറ്റാണ്ട് മുൻപായിരുന്നു.", "250 വർഷം മുൻപേ", "ABOUT 250 YEARS EARLIER", ST(250, " വർഷം", "യൂറോപ്പിന് മുൻപേ", "AHEAD OF EUROPE", "moon")),
        ("അതുകൊണ്ട് ഇതിനെ മാധവ ലൈബ്നിറ്റ്സ് ശ്രേണി എന്ന് വിളിക്കുന്നു.", "മാധവ-ലൈബ്നിറ്റ്സ് ശ്രേണി", "THE MADHAVA-LEIBNIZ SERIES"),
        ("ശ്രേണി പതുക്കെയാണ് അടുത്തുവരുന്നത്, അതുകൊണ്ട് മാധവൻ ഒരു തിരുത്തൽ പദം കൂടി ചേർത്തു.", "തിരുത്തൽ പദം", "A CORRECTION TERM"),
        ("അതുപയോഗിച്ച് അദ്ദേഹം പൈയുടെ വില പതിനൊന്ന് ദശാംശസ്ഥാനം വരെ ശരിയായി കണ്ടെത്തി.", "11 ദശാംശസ്ഥാനം", "CORRECT TO ELEVEN DECIMALS"),
        ("ഇത് സൈൻ, കൊസൈൻ, ആർക്ക് ടാൻജെന്റ് എന്നിവയുടെ ശ്രേണികളിലേക്കും അദ്ദേഹം വ്യാപിപ്പിച്ചു.", "സൈൻ, കൊസൈൻ", "SINE AND COSINE TOO"),
        ("ഈ ആശയങ്ങളാണ് പിന്നീട് കാൽക്കുലസിന്റെ അടിസ്ഥാനമായി മാറിയത്.", "കാൽക്കുലസിന്റെ വിത്ത്", "SEEDS OF CALCULUS", S(["leaf"], "dusk", text="കാൽക്കുലസ്")),
        ("മാധവന് ശേഷം പരമേശ്വരൻ, നീലകണ്ഠ സോമയാജി തുടങ്ങിയ പണ്ഡിതർ ഈ പാരമ്പര്യം തുടർന്നു.", "ശിഷ്യപരമ്പര", "A LINE OF SCHOLARS"),
        ("നീലകണ്ഠൻ ഗ്രഹങ്ങൾ സൂര്യനെ ചുറ്റുന്ന ഒരു മാതൃക വരെ മുന്നോട്ടുവച്ചു.", "ഗ്രഹങ്ങൾ സൂര്യനെ ചുറ്റുന്നു", "PLANETS ORBIT THE SUN"),
        ("ജ്യേഷ്ഠദേവൻ യുക്തിഭാഷ എന്ന പുസ്തകം എഴുതിയത് സംസ്കൃതത്തിലല്ല, മലയാളത്തിലാണ്.", "യുക്തിഭാഷ മലയാളത്തിൽ", "YUKTIBHASHA, IN MALAYALAM"),
        ("അതിൽ ഈ ശ്രേണികളുടെ കാരണങ്ങൾ വിശദമായി തെളിയിച്ചിട്ടുണ്ട്.", "തെളിവുകളോടെ", "WITH PROOFS", TX("യുക്തിഭാഷ", "YUKTIBHASHA", "leaf", "#2f7d4f")),
        ("നമ്മുടെ മലയാള ഭാഷയിൽ ഒരു ഗണിത ഗ്രന്ഥം ഉണ്ടായിരുന്നു എന്നത് അഭിമാനകരമാണ്.", "മലയാളത്തിൽ ഗണിതം", "MATHS IN OUR LANGUAGE"),
        ("അടുത്ത തവണ പൈ എന്ന് കേൾക്കുമ്പോൾ ഇരിങ്ങാലക്കുടയിലെ ആ പ്രതിഭയെ ഓർക്കൂ.", "മാധവനെ ഓർക്കൂ", "REMEMBER MADHAVA", TX("മാധവനെ ഓർക്കൂ", "REMEMBER MADHAVA", "person", "#c8442f")),
    ],
)
FACTS_MADHAVA = ["Madhava of Sangamagrama (c. 1340-1425) founded the Kerala school of astronomy and mathematics and found infinite series for pi, sine, cosine and arctangent about 250 years before Gregory and Leibniz (MacTutor History of Mathematics; Joseph, The Crest of the Peacock).",
                 "The Madhava-Leibniz series pi/4 = 1 - 1/3 + 1/5 - 1/7 + ... with correction terms gave pi correct to 11 decimal places (MacTutor).",
                 "Nilakantha Somayaji (1444-1544) proposed a model where planets orbit the Sun, which orbits the Earth (Tantrasangraha, 1501).",
                 "Jyeshthadeva's Yuktibhasha (c. 1530) was written in Malayalam and gives proofs of the series (Wikipedia: Yuktibhasa)."]

LATERITE = sh(
    "laterite_s", "ചെങ്കല്ല് വെട്ടിയെടുക്കുമ്പോൾ മൃദുവും പിന്നീട് കല്ലുപോലെ കട്ടിയും ആകുന്നത് എന്തുകൊണ്ട്?", "Why does laterite stone harden after it is cut?", "ചെങ്കല്ലിന്റെ രഹസ്യം", "LATERITE STONE",
    [
        ("കേരളത്തിലെ ചെങ്കല്ല് ഖനിയിൽ നിന്ന് വെട്ടുമ്പോൾ മൃദുവാണ്, പിന്നെ കല്ലുപോലെ കട്ടിയാകുന്നത് എന്തുകൊണ്ടാണ്?", "മൃദുവിൽ നിന്ന് കട്ടിയിലേക്ക്", "SOFT TO HARD", S(["house", "mountain"], "dusk", label=("ചെങ്കല്ല്", "LATERITE"))),
        ("ചെങ്കല്ല് ചൂടും മഴയും ഏറെക്കാലം മണ്ണിനെ കഴുകി ഉണ്ടാകുന്ന ഒരു പാറയാണ്.", "മഴയും ചൂടും ഉണ്ടാക്കിയത്", "MADE BY HEAT AND RAIN"),
        ("അതിൽ ഇരുമ്പിന്റെയും അലൂമിനിയത്തിന്റെയും ഓക്സൈഡുകൾ ധാരാളമുണ്ട്, അതാണ് ചുവന്ന നിറം.", "ഇരുമ്പ് ഓക്സൈഡ്", "IRON OXIDE MAKES IT RED"),
        ("ഭൂമിക്കടിയിൽ അത് വെള്ളം നിറഞ്ഞ് മൃദുവായിരിക്കും.", "ഭൂമിക്കടിയിൽ മൃദുവായ", "SOFT UNDERGROUND"),
        ("വെട്ടിയെടുത്ത് വായുവിൽ വെയ്ക്കുമ്പോൾ വെള്ളം ആവിയായി ഇരുമ്പ് ഓക്സൈഡുകൾ കട്ടിയുള്ള ഘടനയായി ഉറയ്ക്കും.", "വായുവിൽ ഉറയ്ക്കുന്നു", "AIR HARDENS IT"),
        ("അതുകൊണ്ട് പഴയ കോട്ടകളും ക്ഷേത്രങ്ങളും ചെങ്കല്ലിൽ പണിതപ്പോൾ നൂറ്റാണ്ടുകൾ നിലനിന്നു.", "നൂറ്റാണ്ടുകളോളം നിലനിൽക്കും", "FORTS LASTED FOR CENTURIES"),
    ],
    "കാലം കട്ടിയാക്കുന്ന കല്ല്!", "A STONE HARDENED BY AIR", "ചെങ്കല്ലിനെ കല്ലാക്കുന്നത് കാറ്റും വെയിലുമാണ്!")

POT = sh(
    "matka_s", "മൺകുടത്തിലെ വെള്ളം തണുത്തിരിക്കുന്നത് എങ്ങനെ?", "How does a clay pot keep water cool?", "മൺകുടത്തിലെ തണുപ്പ്", "THE CLAY POT FRIDGE",
    [
        ("ഫ്രിഡ്ജില്ലാതെ മൺകുടത്തിലെ വെള്ളം തണുത്തിരിക്കുന്നത് എങ്ങനെയാണ്?", "ഫ്രിഡ്ജില്ലാത്ത തണുപ്പ്", "COOL WITHOUT A FRIDGE", S(["bottle", "drop"], "dusk", label=("മൺകുടം", "CLAY POT"))),
        ("മൺകുടത്തിന്റെ ചുമരിൽ കണ്ണിന് കാണാത്ത ചെറിയ സുഷിരങ്ങളുണ്ട്.", "ചെറിയ സുഷിരങ്ങൾ", "TINY PORES"),
        ("ആ സുഷിരങ്ങളിലൂടെ വെള്ളം പുറത്തേക്ക് നേർത്ത പാടയായി വരും.", "പുറത്ത് നനവ്", "A THIN FILM OF WATER OUTSIDE"),
        ("ആ നനവ് ബാഷ്പീകരിക്കുമ്പോൾ കുടത്തിൽ നിന്ന് ചൂട് വലിച്ചെടുക്കും.", "ബാഷ്പീകരണം ചൂടെടുക്കുന്നു", "EVAPORATION TAKES HEAT"),
        ("അങ്ങനെ ഉള്ളിലെ വെള്ളം തണുക്കും.", "ഉള്ളിലെ വെള്ളം തണുക്കുന്നു", "THE WATER INSIDE COOLS"),
        ("വെയിലും കാറ്റും ഉള്ള സ്ഥലത്ത് വെച്ചാൽ ഈ തണുപ്പ് കൂടും.", "കാറ്റിൽ കൂടുതൽ തണുപ്പ്", "BREEZE MAKES IT COOLER"),
    ],
    "മണ്ണിന്റെ ഫ്രിഡ്ജ്!", "THE EARTH'S FRIDGE", "വിയർപ്പ് കൊണ്ട് തണുക്കുന്ന നമ്മളെപ്പോലെയാണ് മൺകുടവും!")

MIRROR = sh(
    "aranmula_s", "ആറന്മുള കണ്ണാടി ലോഹം കൊണ്ടുള്ളതാണെന്ന് അറിയാമോ?", "Did you know the Aranmula mirror is made of metal?", "ലോഹ കണ്ണാടി!", "THE ARANMULA MIRROR",
    [
        ("ഗ്ലാസില്ലാത്ത ഒരു കണ്ണാടി, ആറന്മുള കണ്ണാടി, എങ്ങനെയാണ് പ്രവർത്തിക്കുന്നത്?", "ഗ്ലാസില്ലാത്ത കണ്ണാടി", "A MIRROR WITHOUT GLASS", S(["moon", "leaf"], "dusk", label=("ആറന്മുള കണ്ണാടി", "ARANMULA MIRROR"))),
        ("ഇത് ചെമ്പും വെളുത്തീയവും ചേർന്ന ഒരു ലോഹസങ്കരം കൊണ്ടുള്ളതാണ്.", "ചെമ്പും വെളുത്തീയവും", "A COPPER AND TIN ALLOY"),
        ("ഉരച്ച് മിനുക്കി ലോഹത്തെ കണ്ണാടിയാക്കി മാറ്റും.", "ഉരച്ച് മിനുക്കൽ", "POLISHED INTO A MIRROR"),
        ("സാധാരണ കണ്ണാടിയിൽ പ്രകാശം ഗ്ലാസിലൂടെ കടന്ന് പിന്നിലെ പാളിയിൽ തട്ടി തിരിച്ചുവരും.", "സാധാരണ കണ്ണാടി", "AN ORDINARY MIRROR REFLECTS BEHIND GLASS"),
        ("ഇതിൽ ഗ്ലാസില്ലാത്തതുകൊണ്ട് പ്രതിബിംബം ഉപരിതലത്തിൽ നിന്ന് തന്നെ തെളിഞ്ഞുവരും.", "ഉപരിതല പ്രതിഫലനം", "THE IMAGE COMES FROM THE SURFACE"),
        ("അതുകൊണ്ട് ഇരട്ട പ്രതിബിംബം വരില്ല, വളരെ തെളിഞ്ഞ കാഴ്ച കിട്ടും.", "ഇരട്ട പ്രതിബിംബമില്ല", "NO DOUBLE IMAGE"),
    ],
    "ഒരു കലയുടെ ശാസ്ത്രം!", "ART WITH PHYSICS", "ആറന്മുള കണ്ണാടി കലയും ഭൗതികശാസ്ത്രവും ചേർന്ന ഒരു അത്ഭുതമാണ്!")

COIR = sh(
    "coir_s", "തേങ്ങയുടെ തൊണ്ട് കയറായി മാറുന്നത് എങ്ങനെ?", "How does a coconut husk become rope?", "തൊണ്ടിൽ നിന്ന് കയർ", "HUSK TO ROPE",
    [
        ("തൊണ്ടിനെ ഉറപ്പുള്ള കയറാക്കി മാറ്റുന്നത് എങ്ങനെയാണ്?", "തൊണ്ട് → കയർ", "HUSK TO ROPE", S(["coconut", "boat"], "dusk", label=("കയർ", "COIR"))),
        ("ആദ്യം തൊണ്ട് കായലിലെ വെള്ളത്തിൽ മാസങ്ങളോളം കുതിർത്തിടും.", "കായലിൽ കുതിർക്കൽ", "SOAKED IN BACKWATERS"),
        ("ഇതിനെ ചീയിക്കൽ എന്ന് പറയും, സൂക്ഷ്മജീവികൾ നാരുകൾക്കിടയിലെ പശ അലിയിക്കും.", "ചീയിക്കൽ", "RETTING"),
        ("പിന്നെ തൊണ്ട് അടിച്ച് നാരുകൾ വേർതിരിക്കും.", "നാര് വേർതിരിക്കുന്നു", "THE FIBRES ARE BEATEN OUT"),
        ("നാരുകൾ ചർക്കയിൽ പിരിച്ച് ഒന്നിച്ച് ചേർത്ത് കയറാക്കും.", "പിരിച്ച് കയറാക്കുന്നു", "TWISTED INTO ROPE"),
        ("കയർ ഉപ്പുവെള്ളത്തിൽ പോലും അഴുകാത്തതുകൊണ്ട് വള്ളങ്ങളിലും പായകളിലും ഉപയോഗിക്കുന്നു.", "ഉപ്പിൽ അഴുകില്ല", "IT SURVIVES SALT WATER"),
    ],
    "മാലിന്യത്തിൽ നിന്ന് സമ്പത്ത്!", "WEALTH FROM WASTE", "തൊണ്ടിനെ പൊന്നാക്കിയ ശാസ്ത്രമാണ് കയർ!")

TILE = sh(
    "tileroof_s", "കേരളത്തിലെ വീടുകൾക്ക് ചരിഞ്ഞ ഓടിട്ട മേൽക്കൂര എന്തിന്?", "Why do Kerala houses have sloped tiled roofs?", "ചരിഞ്ഞ മേൽക്കൂര", "SLOPED TILED ROOFS",
    [
        ("കേരളത്തിലെ പഴയ വീടുകൾക്ക് ചരിഞ്ഞ ഓടിട്ട മേൽക്കൂര ഉണ്ടായത് എന്തുകൊണ്ടാണ്?", "ചരിഞ്ഞ ഓട് മേൽക്കൂര", "WHY SLOPED TILES?", S(["house", "cloudDark"], "storm", ("rain", 30, "#4aa3d8"), label=("ഓട്", "TILES"))),
        ("ഒന്നാമത്തെ കാരണം മഴയാണ്.", "ഒന്ന്: മഴ", "REASON ONE: RAIN"),
        ("ചരിവുള്ള മേൽക്കൂരയിൽ വീഴുന്ന മഴവെള്ളം വേഗം ഒഴുകി താഴേക്ക് പോകും.", "വെള്ളം ഒഴുകിപ്പോകും", "WATER RUNS OFF FAST"),
        ("രണ്ടാമത്തെ കാരണം ചൂടാണ്.", "രണ്ട്: ചൂട്", "REASON TWO: HEAT", S(["sun"], "dusk")),
        ("ഓടുകൾക്കിടയിലൂടെ വായു കടക്കുന്നതുകൊണ്ട് ചൂടുവായു പുറത്തേക്ക് പോകും.", "ചൂടുവായു പുറത്തേക്ക്", "HOT AIR ESCAPES"),
        ("അതുകൊണ്ട് വീടിനുള്ളിൽ തണുപ്പ് കൂടുതൽ കിട്ടും.", "വീടിനുള്ളിൽ തണുപ്പ്", "A COOLER HOME INSIDE"),
    ],
    "കാലാവസ്ഥയ്ക്ക് ഇണങ്ങിയ രൂപകൽപ്പന!", "BUILT FOR THE CLIMATE", "നമ്മുടെ പഴയ വീടുകൾ കാലാവസ്ഥയെ അറിഞ്ഞ് പണിതതാണ്!")

COPPER = sh(
    "copper_s", "ചെമ്പ് പാത്രത്തിൽ വെച്ച വെള്ളം ശുദ്ധമാകുമോ?", "Does water kept in copper become cleaner?", "ചെമ്പിലെ വെള്ളം", "COPPER AND WATER",
    [
        ("ചെമ്പ് പാത്രത്തിൽ വച്ച വെള്ളം ശുദ്ധമാകും എന്ന് പഴയ ആളുകൾ പറയുമായിരുന്നു, അതിൽ കാര്യമുണ്ടോ?", "ചെമ്പിലെ വെള്ളം", "IS THERE ANY TRUTH?", S(["bowl", "drop"], "dusk", label=("ചെമ്പ്", "COPPER"))),
        ("ചെമ്പിന് ചില ബാക്ടീരിയകളെ നശിപ്പിക്കാൻ കഴിയും എന്ന് ലാബ് പഠനങ്ങൾ കാണിക്കുന്നു.", "ബാക്ടീരിയയെ കൊല്ലും", "COPPER CAN KILL SOME BACTERIA"),
        ("ഇതിനെ ഒലിഗോഡൈനാമിക് പ്രഭാവം എന്ന് പറയും.", "ഒലിഗോഡൈനാമിക് പ്രഭാവം", "THE OLIGODYNAMIC EFFECT"),
        ("ചെമ്പ് അയോണുകൾ ബാക്ടീരിയയുടെ കോശത്തെ തകരാറിലാക്കും.", "കോശത്തിന് കേട്", "COPPER IONS DAMAGE THE CELL"),
        ("പക്ഷേ അതിന് മണിക്കൂറുകൾ വേണം, അഴുക്കുള്ള വെള്ളം ശുദ്ധമാക്കാൻ ഇത് മതിയാവില്ല.", "അഴുക്കുള്ള വെള്ളത്തിന് മതിയാവില്ല", "NOT ENOUGH FOR DIRTY WATER"),
        ("അതുകൊണ്ട് കുടിക്കുന്നതിന് മുൻപ് വെള്ളം തിളപ്പിക്കുകയോ അരിക്കുകയോ ചെയ്യുന്നത് തുടരണം.", "തിളപ്പിക്കുക", "STILL BOIL OR FILTER IT"),
    ],
    "ചെമ്പ് സഹായിയാണ്, പകരമല്ല!", "A HELPER, NOT A REPLACEMENT", "ചെമ്പ് ഒരു സഹായി മാത്രമാണ്, തിളപ്പിക്കൽ ഒഴിവാക്കരുത്!")

FACTS = [
    "Laterite is a rock formed by intense tropical weathering, rich in iron and aluminium oxides; it is soft when quarried and hardens on exposure to air (Wikipedia: Laterite; Geological Survey of India).",
    "Water evaporating from a porous clay pot's surface takes heat from the pot and cools the water inside (general physics; evaporative cooling).",
    "The Aranmula kannadi is a metal-alloy (copper and tin) mirror whose reflection comes from the polished surface, so it has no double image (Wikipedia: Aranmula Kannadi).",
    "Coir is made from coconut husk fibre softened by retting in water, then beaten, spun and twisted; it resists salt water (Coir Board of India).",
    "Sloped tiled roofs shed monsoon rain and let hot air escape (traditional Kerala architecture; Laurie Baker's writings).",
    "Copper surfaces can kill some bacteria through the oligodynamic effect, but this is slow and does not replace boiling or filtering (Grass et al., Applied and Environmental Microbiology 2011; WHO).",
] + FACTS_MADHAVA
# richer scene: Madhava's series, drawn
rich(MADHAVA, 10, 13, "series", {"terms": 1, "pi": 2}, [(0, 500, 300, 1.2), (1, 500, 620, 1.1)])
rich(MADHAVA, 15, 17, "series", {"terms": 0, "pi": 0, "fix": 1}, [(0, 500, 620, 1.1), (1, 500, 660, 1.3)])

# richer scenes (lab cut-aways) for the heritage Shorts
lab(LATERITE, 0, 5, "laterite", {"cut": 3, "air": 4, "harden": 4.5}, [(3, "ഭൂമിക്കടിയിൽ മൃദുവായ", "SOFT UNDERGROUND", 500, 340), (4, "വായുവിൽ ഉറയ്ക്കുന്നു", "AIR HARDENS IT", 500, 340)])
lab(POT, 0, 5, "matka", {"pores": 1, "seep": 2, "evap": 3, "cool": 4}, [(1, "ചെറിയ സുഷിരങ്ങൾ", "TINY PORES", 500, 380), (3, "ബാഷ്പീകരണം ചൂടെടുക്കുന്നു", "EVAPORATION TAKES HEAT", 500, 330)])
lab(MIRROR, 0, 5, "aranmula", {"glass": 3, "double": 3.5, "metal": 4}, [(3, "ഗ്ലാസ് കണ്ണാടി: പിന്നിൽ പ്രതിഫലനം", "GLASS REFLECTS FROM BEHIND", 500, 320), (4, "ലോഹ കണ്ണാടി: ഉപരിതലത്തിൽ", "METAL REFLECTS AT THE SURFACE", 500, 320)])
lab(COIR, 0, 5, "coir", {"soak": 1, "beat": 3, "twist": 4}, [(1, "കായലിൽ കുതിർക്കൽ", "SOAKED IN BACKWATER", 400, 560), (3, "അടിച്ച് നാര് വേർതിരിക്കൽ", "BEATEN INTO FIBRES", 700, 540), (4, "പിരിച്ച് കയറാക്കൽ", "TWISTED INTO ROPE", 800, 640)])
lab(TILE, 0, 5, "tileroof", {"rain": 1, "heat": 3, "air": 4}, [(1, "മഴ ഒഴുകിപ്പോകും", "RAIN RUNS OFF", 500, 300), (4, "ചൂടുവായു പുറത്തേക്ക്", "HOT AIR ESCAPES", 500, 300)])
lab(COPPER, 0, 5, "copper", {"water": 0, "ions": 2, "kill": 3, "boil": 5}, [(2, "ഒലിഗോഡൈനാമിക് പ്രഭാവം", "THE OLIGODYNAMIC EFFECT", 500, 400), (5, "ഇപ്പോഴും തിളപ്പിക്കണം", "STILL BOIL IT", 880, 560)])

VIDEOS = [MADHAVA, LATERITE, POT, MIRROR, COIR, TILE, COPPER]
