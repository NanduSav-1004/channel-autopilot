"""Science Chaya batch 3: weather and land (landslides long; rainbow, sea breeze, humidity, hail, cloud weight, raindrop Shorts)."""
from chaya.quick import ST, TX, S, lg, sh

LAND = lg(
    "landslide_long", "ഉരുൾപൊട്ടൽ എങ്ങനെ ഉണ്ടാകുന്നു? | മലയിടിച്ചിലിന്റെ ശാസ്ത്രം", "How do landslides happen? The science behind the slopes that slip",
    "ഉരുൾപൊട്ടൽ എങ്ങനെ?", "HOW LANDSLIDES HAPPEN", "നിങ്ങളുടെ നാട്ടിൽ മഴക്കാലത്ത് ചരിവുള്ള സ്ഥലങ്ങളിൽ എന്തൊക്കെ മുൻകരുതൽ എടുക്കാറുണ്ട്?", "WHAT PRECAUTIONS DO YOU TAKE ON SLOPES IN THE RAINS?",
    [
        ("കേരളത്തിലെ മലയോരങ്ങളിൽ മഴക്കാലത്ത് മണ്ണും കല്ലും ഒന്നിച്ച് താഴേക്ക് ഒഴുകിവരുന്നത് ഉരുൾപൊട്ടലാണ്.", "ഉരുൾപൊട്ടൽ", "WHEN A SLOPE SLIPS", S(["mountain", "cloudDark"], "storm", ("rain", 40, "#4aa3d8"))),
        ("ഇത് ഒരു നിമിഷം കൊണ്ട് ഉണ്ടാകുന്നതല്ല, അതിനു പിന്നിൽ കുറേ ദിവസത്തെ ഒരുക്കമുണ്ട്.", "ഒരുക്കം ദിവസങ്ങൾ", "DAYS OF BUILD-UP"),
        ("ഇന്ന് നമുക്ക് ഇത് ഘട്ടം ഘട്ടമായി മനസ്സിലാക്കാം.", "ഘട്ടം ഘട്ടമായി", "STEP BY STEP", TX("ഘട്ടം ഘട്ടമായി", "STEP BY STEP", "mountain", "#4a2a17")),
        ("ആദ്യം, മണ്ണ് എങ്ങനെ ചരിവിൽ പിടിച്ചുനിൽക്കുന്നു എന്ന് നോക്കാം.", "മണ്ണ് പിടിച്ചുനിൽക്കുന്നത്", "HOW SOIL HOLDS ON", S(["mountain"], "sky", text="ചരിവ്")),
        ("മണ്ണിന്റെ തരികൾ തമ്മിലുള്ള ഉരസലും ചെടികളുടെ വേരുകളുമാണ് അതിനെ പിടിച്ചുനിർത്തുന്നത്.", "ഉരസലും വേരുകളും", "FRICTION AND ROOTS", S(["tree", "leaf"], "sky")),
        ("മരങ്ങളുടെ വേരുകൾ ഒരു വല പോലെ മണ്ണിനെ കൂട്ടിക്കെട്ടും.", "വേരുകൾ = വല", "ROOTS ACT LIKE A NET"),
        ("ഇനി മഴ പെയ്യുന്നത് കാണാം.", "മഴ പെയ്യുന്നു", "NOW THE RAIN", S(["cloudDark"], "storm", ("rain", 50, "#4aa3d8"))),
        ("ദിവസങ്ങളോളം പെയ്യുന്ന മഴ മണ്ണിലെ വിടവുകളിൽ വെള്ളം നിറയ്ക്കും.", "വിടവുകളിൽ വെള്ളം", "WATER FILLS THE GAPS", S(["drop", "drop", "drop"], "soil")),
        ("വെള്ളം നിറഞ്ഞ മണ്ണിന് ഭാരം കൂടും.", "ഭാരം കൂടുന്നു", "SOAKED SOIL GETS HEAVIER", S(["mountain"], "soil", text="ഭാരം കൂടുന്നു")),
        ("അതോടൊപ്പം മണ്ണിനുള്ളിലെ ജലമർദ്ദം കൂടി, തരികൾ തമ്മിലുള്ള ഉരസൽ കുറയും.", "ജലമർദ്ദം കൂടുന്നു", "WATER PRESSURE RISES, FRICTION FALLS"),
        ("ഭാരം കൂടുകയും പിടിത്തം കുറയുകയും ചെയ്യുമ്പോൾ ചരിവ് അസ്ഥിരമാകും.", "അസ്ഥിരമായ ചരിവ്", "THE SLOPE BECOMES UNSTABLE", TX("ഭാരം ↑  പിടിത്തം ↓", "HEAVIER AND WEAKER", "mountain", "#c8442f")),
        ("ഒടുവിൽ ഒരു ഘട്ടത്തിൽ മണ്ണും പാറയും മരങ്ങളും ഒന്നിച്ച് താഴേക്ക് തെന്നും.", "താഴേക്ക് തെന്നുന്നു", "IT ALL SLIDES DOWN", S(["mountain", "tree", "tree"], "storm", ("rain", 30, "#4aa3d8"), anim="shake")),
        ("ഇതിൽ ചിലപ്പോൾ മണ്ണ് ചെളിവെള്ളം പോലെ അതിവേഗം ഒഴുകും, അതിനെ ഡെബ്രി ഫ്ലോ എന്ന് പറയും.", "ഡെബ്രി ഫ്ലോ", "A DEBRIS FLOW"),
        ("ചെറിയ മഴയ്ക്ക് ശേഷമല്ല, ദിവസങ്ങൾ നീണ്ട മഴയ്ക്ക് ശേഷമാണ് ഇത് കൂടുതലും സംഭവിക്കുന്നത്.", "ദിവസങ്ങൾ നീണ്ട മഴ", "AFTER DAYS OF RAIN"),
        ("ഇനി മനുഷ്യൻ ഇതിൽ വഹിക്കുന്ന പങ്ക് നോക്കാം.", "മനുഷ്യന്റെ പങ്ക്", "THE HUMAN PART", S(["house", "tree"], "sky")),
        ("മരങ്ങൾ വെട്ടുന്നതും ചരിവുകൾ വെട്ടിനിരത്തുന്നതും വേരുകളുടെ വലയും മണ്ണിന്റെ പിടിത്തവും ഇല്ലാതാക്കും.", "വേരുകളുടെ വല പോകുന്നു", "THE ROOT NET IS LOST"),
        ("വെള്ളം ഒഴുകിപ്പോകേണ്ട വഴികൾ അടഞ്ഞാൽ അത് മണ്ണിനടിയിൽ കെട്ടിനിൽക്കും.", "വെള്ളത്തിന് വഴി വേണം", "WATER NEEDS A WAY OUT", S(["drop"], "soil", text="ഒഴുക്ക് തടഞ്ഞാൽ?")),
        ("പശ്ചിമഘട്ടത്തിലെ കുത്തനെയുള്ള ചരിവുകളിൽ ഇത് പ്രത്യേകം ശ്രദ്ധിക്കണം.", "കുത്തനെയുള്ള ചരിവുകൾ", "STEEP WESTERN GHATS SLOPES", S(["mountain", "mountain"], "sky")),
        ("ഭൂമിശാസ്ത്ര വകുപ്പുകൾ ഏതൊക്കെ പ്രദേശങ്ങൾ ഉരുൾപൊട്ടൽ സാധ്യതയുള്ളവയാണെന്ന് ഭൂപടങ്ങളിൽ അടയാളപ്പെടുത്തിയിട്ടുണ്ട്.", "അപകടസാധ്യതാ ഭൂപടം", "HAZARD MAPS"),
        ("മഴയുടെ അളവ് അളക്കുന്ന മഴമാപിനികൾ മുന്നറിയിപ്പ് നൽകാൻ സഹായിക്കും.", "മഴമാപിനി", "RAIN GAUGES WARN US", S(["cloud", "drop"], "storm")),
        ("ഓറഞ്ച്, റെഡ് അലർട്ട് വരുമ്പോൾ ചരിവിനടുത്ത് താമസിക്കുന്നവർ മാറിത്താമസിക്കുന്നതാണ് സുരക്ഷിതം.", "അലർട്ട് വന്നാൽ മാറൂ", "ALERT? MOVE EARLY", TX("അലർട്ട് → മാറൂ", "ALERT MEANS MOVE", "cloudDark", "#c8442f")),
        ("മലമുകളിൽ നിന്ന് ഒഴുകുന്ന വെള്ളത്തിന്റെ നിറം ചെളിയായി മാറുന്നത് ഒരു അപകട സൂചനയാണ്.", "ചെളിവെള്ളം = സൂചന", "MUDDY STREAMS ARE A SIGN"),
        ("മണ്ണിൽ പുതിയ വിള്ളലുകൾ വീഴുന്നതും മരങ്ങൾ ചരിയുന്നതും ശ്രദ്ധിക്കണം.", "വിള്ളലുകളും ചരിവും", "CRACKS AND TILTED TREES"),
        ("ശാസ്ത്രം അറിഞ്ഞാൽ നമുക്ക് ജീവൻ രക്ഷിക്കാൻ കഴിയും.", "അറിവ് രക്ഷിക്കും", "KNOWING CAN SAVE LIVES", TX("അറിവ് രക്ഷിക്കും", "KNOWLEDGE SAVES LIVES", "mountain", "#2f7d4f")),
    ],
)
FACTS_LAND = ["Landslides are triggered when heavy rain adds weight and raises pore-water pressure, lowering the soil's shear strength (USGS Landslide Hazards Program).",
              "Plant roots reinforce soil; removing vegetation and blocking drainage on slopes raises landslide risk (USGS; Geological Survey of India).",
              "A debris flow is a fast-moving mix of water, soil and rock down a slope (USGS)."]

RAINBOW = sh(
    "rainbow_s", "മഴവില്ല് യഥാർത്ഥത്തിൽ വൃത്തമാണോ?", "Is a rainbow really a circle?", "മഴവില്ല് വൃത്തമോ?", "IS IT A CIRCLE?",
    [
        ("നമ്മൾ കാണുന്ന മഴവില്ല് പകുതി മാത്രമാണെന്ന് അറിയാമോ?", "പകുതി മാത്രം", "ONLY HALF OF IT", S(["cloud", "sun"], "sky", ("rain", 30, "#4aa3d8"))),
        ("സൂര്യപ്രകാശം മഴത്തുള്ളികളിൽ കടക്കുമ്പോൾ വളഞ്ഞ് ഏഴ് നിറങ്ങളായി പിരിയും.", "ഏഴ് നിറങ്ങൾ", "LIGHT SPLITS INSIDE DROPS"),
        ("തുള്ളിക്കുള്ളിൽ ഒരു തവണ തട്ടി പ്രതിഫലിച്ച് ആ പ്രകാശം നമ്മുടെ കണ്ണിലെത്തും.", "ഉള്ളിൽ പ്രതിഫലനം", "IT BOUNCES ONCE INSIDE"),
        ("സൂര്യന്റെ എതിർദിശയിൽ നിന്ന് ഏകദേശം നാല്പത്തിരണ്ട് ഡിഗ്രി കോണിലാണ് ഈ പ്രകാശം വരുന്നത്.", "42° കോൺ", "AT ABOUT 42 DEGREES", ST(42, "°", "സൂര്യന്റെ എതിർദിശയിൽ നിന്ന്", "FROM THE POINT OPPOSITE THE SUN", "sun")),
        ("ആ കോണിലുള്ള എല്ലാ തുള്ളികളും ചേർന്ന് ഒരു വൃത്തം ഉണ്ടാക്കും.", "വൃത്തം ഉണ്ടാകുന്നു", "ALL THE DROPS FORM A CIRCLE"),
        ("നിലം തടസ്സമായതുകൊണ്ട് നമ്മൾ അതിന്റെ മുകൾഭാഗം മാത്രം കാണുന്നു.", "നിലം മറയ്ക്കുന്നു", "THE GROUND HIDES THE REST"),
        ("വിമാനത്തിൽ നിന്നോ മലമുകളിൽ നിന്നോ നോക്കിയാൽ ചിലപ്പോൾ പൂർണ്ണ വൃത്തം കാണാം.", "മുകളിൽ നിന്ന് വൃത്തം", "FROM ABOVE, A FULL CIRCLE"),
    ],
    "മഴവില്ലിന്റെ വൃത്തം!", "THE HIDDEN CIRCLE", "അടുത്ത തവണ മഴവില്ല് കാണുമ്പോൾ അതിന്റെ മറഞ്ഞിരിക്കുന്ന വൃത്തം ഓർക്കൂ!")

BREEZE = sh(
    "seabreeze_s", "പകൽ കടൽക്കാറ്റ്, രാത്രി കരക്കാറ്റ്: എന്തുകൊണ്ട്?", "Why is the breeze from the sea by day and from the land at night?", "കടൽക്കാറ്റ് എന്തിന്?", "SEA BREEZE",
    [
        ("കോവളത്തോ കോഴിക്കോട് ബീച്ചിലോ വൈകുന്നേരം കടലിൽ നിന്ന് തണുത്ത കാറ്റ് വരുന്നത് ശ്രദ്ധിച്ചിട്ടുണ്ടോ?", "കടലിൽ നിന്നൊരു കാറ്റ്", "A BREEZE FROM THE SEA", S(["boat", "sun"], "sky")),
        ("പകൽ സൂര്യപ്രകാശത്തിൽ കര വേഗം ചൂടാകും.", "കര വേഗം ചൂടാകും", "LAND HEATS FAST", S(["sun"], "dusk", text="കര ചൂടാകുന്നു")),
        ("വെള്ളം പതുക്കെയേ ചൂടാകൂ, അതുകൊണ്ട് കടൽ തണുത്തിരിക്കും.", "കടൽ തണുപ്പ്", "THE SEA STAYS COOL"),
        ("കരയിലെ ചൂടുള്ള വായു മുകളിലേക്ക് പൊങ്ങും.", "ചൂടുവായു പൊങ്ങുന്നു", "WARM AIR RISES"),
        ("ആ ഒഴിവിലേക്ക് കടലിലെ തണുത്ത വായു ഒഴുകിയെത്തും, അതാണ് കടൽക്കാറ്റ്.", "കടൽക്കാറ്റ്", "COOL AIR RUSHES IN"),
        ("രാത്രി കര വേഗം തണുക്കും, കടൽ അപ്പോഴും ചൂടോടെ നിൽക്കും, അതുകൊണ്ട് കാറ്റ് തിരിഞ്ഞ് കരയിൽ നിന്ന് കടലിലേക്ക് വീശും.", "രാത്രി: കരക്കാറ്റ്", "AT NIGHT IT TURNS", S(["moon", "boat"], "night")),
    ],
    "കടലും കരയും തമ്മിലുള്ള കളി!", "LAND VS SEA", "കടലും കരയും ചൂടാകുന്ന വേഗത്തിന്റെ വ്യത്യാസമാണ് ഈ കാറ്റ്!")

HUMID = sh(
    "humid_s", "കേരളത്തിൽ എപ്പോഴും വിയർക്കുന്നത് എന്തുകൊണ്ട്?", "Why do we sweat so much in Kerala?", "ഇത്ര വിയർപ്പ് എന്തിന്?", "HUMIDITY",
    [
        ("കേരളത്തിൽ താപനില അത്ര കൂടുതലല്ലെങ്കിലും നമ്മൾ എപ്പോഴും വിയർക്കുന്നത് എന്തുകൊണ്ടാണ്?", "എപ്പോഴും വിയർപ്പ്", "WHY SO STICKY?", S(["thermo", "drop"], "dusk")),
        ("ഉത്തരം വായുവിലെ ഈർപ്പമാണ്, അതായത് ഹ്യൂമിഡിറ്റി.", "ഈർപ്പം", "HUMIDITY", TX("ഹ്യൂമിഡിറ്റി", "THE WATER IN THE AIR", "drop", "#1f8aa8")),
        ("കടലിനോട് അടുത്തായതുകൊണ്ട് കേരളത്തിലെ വായുവിൽ ജലാംശം വളരെ കൂടുതലാണ്.", "കടൽ അടുത്ത്", "THE SEA IS NEAR"),
        ("വിയർപ്പ് ബാഷ്പീകരിക്കുമ്പോഴാണ് ശരീരം തണുക്കുന്നത്.", "ബാഷ്പീകരണം തണുപ്പിക്കും", "EVAPORATION COOLS US"),
        ("വായു ഈർപ്പം നിറഞ്ഞതാണെങ്കിൽ വിയർപ്പ് ബാഷ്പീകരിക്കില്ല, അതുകൊണ്ട് തണുക്കാതെ ഒട്ടിപ്പിടിച്ച് നിൽക്കും.", "ബാഷ്പീകരിക്കാതെ", "SWEAT CANNOT EVAPORATE"),
        ("അതുകൊണ്ടാണ് മുപ്പത് ഡിഗ്രി ചൂടിൽ പോലും നമുക്ക് അസ്വസ്ഥത തോന്നുന്നത്.", "ചൂടിനേക്കാൾ ഈർപ്പം", "IT IS THE MOISTURE"),
    ],
    "ചൂടല്ല, ഈർപ്പമാണ് കാരണം!", "IT IS THE HUMIDITY", "നമ്മളെ വിയർപ്പിക്കുന്നത് ചൂടിനേക്കാൾ ഈർപ്പമാണ്!")

HAIL = sh(
    "hail_s", "ആലിപ്പഴം ഉണ്ടാകുന്നത് എങ്ങനെ? | വേനൽമഴയിലെ ഐസ്", "How does hail form?", "ആലിപ്പഴം!", "HAILSTONES",
    [
        ("വേനൽമഴയിൽ ചിലപ്പോൾ ആകാശത്ത് നിന്ന് ഐസ് കട്ടകൾ വീഴുന്നത് എങ്ങനെയാണ്?", "ആകാശത്ത് നിന്ന് ഐസ്", "ICE FROM THE SKY", S(["cloudDark"], "storm", ("rain", 40, "#e8f4ff"))),
        ("ഇടിമേഘത്തിനുള്ളിൽ ശക്തമായ കാറ്റ് മുകളിലേക്ക് വീശുന്നുണ്ട്.", "മുകളിലേക്കുള്ള കാറ്റ്", "A STRONG UPDRAFT"),
        ("ആ കാറ്റ് ജലത്തുള്ളികളെ മേഘത്തിന്റെ തണുത്തുറഞ്ഞ ഭാഗത്തേക്ക് ഉയർത്തും.", "തണുപ്പിലേക്ക് ഉയരുന്നു", "DROPS RISE INTO THE COLD"),
        ("അവിടെ തുള്ളികൾ ഐസായി മാറി, ചുറ്റും കൂടുതൽ വെള്ളം ഉറഞ്ഞ് പാളികളായി വളരും.", "പാളികളായി വളരുന്നു", "THEY GROW IN LAYERS"),
        ("ഐസ് കട്ടയ്ക്ക് ഭാരം കൂടുമ്പോൾ കാറ്റിന് അതിനെ താങ്ങാൻ പറ്റാതെ അത് താഴേക്ക് വീഴും.", "ഭാരം കൂടി വീഴുന്നു", "TOO HEAVY, SO IT FALLS"),
        ("അതുകൊണ്ട് ആലിപ്പഴം മുറിച്ചാൽ ഉള്ളിൽ ഉള്ളി പോലെ പാളികൾ കാണാം.", "ഉള്ളിൽ പാളികൾ", "LIKE LAYERS OF AN ONION", S(["onion"], "dusk")),
    ],
    "ഐസ് ഉണ്ടാക്കുന്ന ഇടിമേഘം!", "A FREEZER IN THE STORM", "ചൂടുള്ള വേനലിലും മേഘത്തിനുള്ളിൽ തണുപ്പിന്റെ ഒരു ഫാക്ടറിയുണ്ട്!")

CLOUDW = sh(
    "cloudweight_s", "ഒരു മേഘത്തിന് എത്ര ഭാരമുണ്ട്?", "How much does a cloud weigh?", "മേഘത്തിന്റെ ഭാരം!", "HOW HEAVY IS A CLOUD?",
    [
        ("ആകാശത്ത് പൊങ്ങിക്കിടക്കുന്ന മേഘത്തിന് എത്ര ഭാരം ഉണ്ടാകും?", "മേഘത്തിന്റെ ഭാരം", "HOW HEAVY IS IT?", S(["cloud"], "sky", label=("മേഘം", "A CLOUD"))),
        ("ഒരു ചെറിയ കുമുലസ് മേഘത്തിന് ഏകദേശം അഞ്ച് ലക്ഷം കിലോഗ്രാം ഭാരമുണ്ട്.", "5 ലക്ഷം കിലോ", "ABOUT 500,000 KG", ST(500000, " kg", "ഒരു ചെറിയ മേഘത്തിന്റെ ഭാരം", "A SMALL FAIR-WEATHER CLOUD", "cloud")),
        ("അത് ഏകദേശം എൺപത് ആനകളുടെ ഭാരത്തിന് തുല്യമാണ്.", "എൺപത് ആനകൾ", "ABOUT EIGHTY ELEPHANTS", S(["elephant"], "sky", text="× 80")),
        ("പക്ഷേ ആ ഭാരം ഒരുപാട് വലിയ സ്ഥലത്ത് ചെറിയ വെള്ളത്തുള്ളികളായി പരന്നുകിടക്കുന്നു.", "ചെറിയ തുള്ളികൾ", "SPREAD AS TINY DROPS"),
        ("ആ തുള്ളികൾക്ക് ഭാരം തീരെ കുറവായതുകൊണ്ട് വായുവിൽ പൊങ്ങിക്കിടക്കാൻ കഴിയും.", "തൂവൽ പോലെ ഭാരം", "SO LIGHT THEY FLOAT"),
        ("അവ വലുതായി ഭാരം കൂടുമ്പോൾ മഴയായി താഴേക്ക് പെയ്യും.", "വലുതായാൽ മഴ", "GROW HEAVY, AND IT RAINS"),
    ],
    "തലയ്ക്ക് മുകളിൽ അഞ്ഞൂറ് ടൺ!", "TONNES ABOVE YOUR HEAD", "അടുത്ത തവണ മേഘത്തെ നോക്കുമ്പോൾ അതിനുള്ളിലെ ടൺ കണക്കിന് വെള്ളം ഓർക്കൂ!")

DROPS = sh(
    "raindropspeed_s", "മഴത്തുള്ളി വീഴുന്നത് എത്ര വേഗത്തിൽ?", "How fast does a raindrop fall?", "മഴത്തുള്ളിയുടെ വേഗം", "RAINDROP SPEED",
    [
        ("വലിയ മേഘത്തിൽ നിന്ന് വീഴുന്ന ഒരു മഴത്തുള്ളി വീഴ്ചയിൽ വേഗം കൂടിക്കൂടി പോവുകയാണോ?", "വേഗം കൂടുമോ?", "DOES IT KEEP SPEEDING UP?", S(["drop"], "storm", ("rain", 40, "#4aa3d8"))),
        ("അല്ല, ഒരു പരിധി കഴിഞ്ഞാൽ വായുവിന്റെ തടസ്സം കാരണം വേഗം കൂടില്ല.", "ഒരു പരിധി", "AIR PUSHES BACK"),
        ("ഇതിനെ ടെർമിനൽ വേഗം എന്ന് പറയും.", "ടെർമിനൽ വേഗം", "TERMINAL VELOCITY"),
        ("ഒരു ചെറിയ മഴത്തുള്ളി മണിക്കൂറിൽ ഏതാനും കിലോമീറ്റർ വേഗത്തിലേ വീഴൂ.", "ചെറിയ തുള്ളി: പതുക്കെ", "SMALL DROPS FALL SLOWLY"),
        ("വലിയ തുള്ളി മണിക്കൂറിൽ ഏകദേശം മുപ്പത്തിരണ്ട് കിലോമീറ്റർ വരെ വേഗത്തിൽ എത്തും.", "വലിയ തുള്ളി ≈ 32 km/h", "BIG DROPS REACH ABOUT 32 KM/H", ST(32, " km/h", "ഏറ്റവും വലിയ മഴത്തുള്ളി", "THE BIGGEST RAINDROPS", "drop")),
        ("അതുകൊണ്ടാണ് ഉയരമുള്ള മേഘത്തിൽ നിന്ന് വീണിട്ടും മഴ നമ്മളെ വേദനിപ്പിക്കാത്തത്.", "വേദനിപ്പിക്കാത്ത മഴ", "WHY RAIN DOES NOT HURT"),
    ],
    "വായുവാണ് നമ്മുടെ കുട!", "AIR IS OUR UMBRELLA", "വായുവിന്റെ തടസ്സമില്ലെങ്കിൽ മഴ ഒരു വെടിയുണ്ട പോലെ വീഴുമായിരുന്നു!")

FACTS = [
    "A rainbow is a full circle seen from the point opposite the sun at about 42 degrees; the ground hides the lower part (NASA/NOAA explanations; Wikipedia: Rainbow).",
    "Sea breezes blow by day because land heats faster than water; the pattern reverses at night (NOAA JetStream: Sea breeze).",
    "High humidity slows the evaporation of sweat, so the body cools less (NOAA National Weather Service: heat index).",
    "Hail grows in layers as supercooled water freezes on ice pellets lifted by thunderstorm updrafts (NOAA National Severe Storms Laboratory).",
    "A typical small cumulus cloud holds about 500 tonnes of water (USGS Water Science School: How much does a cloud weigh).",
    "Large raindrops fall at about 9 m/s (roughly 32 km/h); drag limits the speed to a terminal velocity (NOAA; Wikipedia: Drop (liquid)).",
] + FACTS_LAND
VIDEOS = [LAND, RAINBOW, BREEZE, HUMID, HAIL, CLOUDW, DROPS]
