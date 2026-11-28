"""Science Chaya batch 10: the sea and the coast (waves and coastal erosion long; salty sea, why waves break, blue sea, black sand, fish gills, floating Shorts)."""
from chaya.quick import ST, TX, S, lg, sh

WAVES = lg(
    "waves_long", "തിരമാലകൾ ഉണ്ടാകുന്നത് എങ്ങനെ? കടൽ കരയെ എടുക്കുന്നത് എന്തുകൊണ്ട്?", "How are waves made, and why does the sea eat the coast?",
    "തിരമാലയുടെ ശക്തി!", "THE POWER OF WAVES", "നിങ്ങളുടെ നാട്ടിലെ കടൽത്തീരത്ത് ഏറ്റവും വലിയ മാറ്റം എന്താണ് കണ്ടത്?", "WHAT CHANGE HAVE YOU SEEN ON YOUR COAST?",
    [
        ("കേരളത്തിന് ഏകദേശം അറുനൂറ് കിലോമീറ്റർ നീളമുള്ള കടൽത്തീരമുണ്ട്.", "600 km കടൽത്തീരം", "ABOUT 600 KM OF COAST", S(["boat", "cloud"], "sky", label=("തിരമാല", "WAVES"))),
        ("ആ തീരത്ത് ഓരോ ദിവസവും ലക്ഷക്കണക്കിന് തിരമാലകൾ വന്നുപോകുന്നു.", "ലക്ഷക്കണക്കിന് തിരമാലകൾ", "MILLIONS OF WAVES"),
        ("ഇന്ന് ആ തിരമാലകളുടെ ശക്തി എവിടെ നിന്ന് വരുന്നു എന്ന് നോക്കാം.", "തിരമാലയുടെ ശക്തി", "WHERE WAVES GET THEIR POWER", TX("തിരമാലയുടെ ശക്തി", "THE POWER OF WAVES", "boat", "#4a2a17")),
        ("മിക്ക തിരമാലകളുടെയും ഉറവിടം കാറ്റാണ്.", "ഉറവിടം: കാറ്റ്", "THE SOURCE IS WIND", S(["cloud"], "sky", ("bubbles", 18, "#fff"))),
        ("കാറ്റ് വെള്ളത്തിന്റെ ഉപരിതലത്തിലൂടെ ഉരസുമ്പോൾ ചെറിയ അലകൾ ഉണ്ടാകും.", "കാറ്റുരസി അലകൾ", "WIND RUBS UP RIPPLES"),
        ("ആ അലകൾ കാറ്റിൽ നിന്ന് കൂടുതൽ ഊർജം വാങ്ങി വലുതാകും.", "ഊർജം വാങ്ങി വളരുന്നു", "THEY GROW BY TAKING ENERGY"),
        ("കാറ്റിന്റെ വേഗം, നീണ്ടുനിൽക്കുന്ന സമയം, കടലിന്റെ വിസ്തൃതി ഇവ കൂടുന്തോറും തിരമാല വലുതാകും.", "വേഗം, സമയം, വിസ്തൃതി", "SPEED, TIME AND DISTANCE"),
        ("തിരമാലയിൽ വെള്ളം മുന്നോട്ട് സഞ്ചരിക്കുന്നില്ല, ഊർജം മാത്രമാണ് സഞ്ചരിക്കുന്നത്.", "ഊർജം മാത്രം സഞ്ചരിക്കുന്നു", "ONLY ENERGY TRAVELS", TX("വെള്ളമല്ല, ഊർജം!", "NOT WATER, ENERGY", "drop", "#c8442f")),
        ("ഒരു കടൽപ്പായൽ തിരമാലയിൽ പൊങ്ങിത്താഴുന്നത് ഏതാണ്ട് ഒരേ സ്ഥലത്താണ്.", "പൊങ്ങിത്താഴുന്ന പായൽ", "A FLOATING LEAF BOBS IN PLACE", S(["leaf"], "sky")),
        ("തിരമാല കരയോട് അടുക്കുമ്പോൾ കടലിന്റെ ആഴം കുറയും.", "ആഴം കുറയുന്നു", "THE SEA GETS SHALLOW"),
        ("അടിഭാഗം തറയിൽ ഉരസി വേഗം കുറയും, മുകൾഭാഗം മുന്നോട്ട് ചാടും.", "അടിയിൽ ഉരസൽ", "THE BOTTOM DRAGS, THE TOP LEANS"),
        ("അങ്ങനെ തിരമാല ഉയർന്ന് മറിഞ്ഞ് പതഞ്ഞ് തീരത്ത് പൊട്ടും.", "ഉയർന്ന് പൊട്ടുന്നു", "IT RISES AND BREAKS", S(["boat", "drop"], "sky", ("bubbles", 30, "#fff"))),
        ("ഇനി തീരത്തെ മണലിന് എന്ത് സംഭവിക്കുന്നു എന്ന് നോക്കാം.", "തീരത്തെ മണൽ", "WHAT HAPPENS TO THE SAND", TX("തീരത്തെ മണൽ", "THE SAND", "coconut", "#a8782f")),
        ("സാധാരണ ദിവസങ്ങളിൽ തിരമാല മണൽ കരയിലേക്ക് കൊണ്ടുവന്നിടും.", "മണൽ കൊണ്ടുവരുന്നു", "WAVES BRING SAND IN"),
        ("മഴക്കാലത്തെ വലിയ തിരമാലകൾ ആ മണൽ കടലിലേക്ക് കോരിക്കൊണ്ടുപോകും.", "മഴക്കാലത്ത് കോരിയെടുക്കുന്നു", "STORM WAVES TAKE IT BACK"),
        ("ശാന്തമായ കാലത്ത് തീരം വീണ്ടും വളരും, ഇതൊരു സ്വാഭാവിക ചക്രമാണ്.", "സ്വാഭാവിക ചക്രം", "A NATURAL CYCLE"),
        ("പക്ഷേ തീരത്ത് കരിങ്കൽഭിത്തി കെട്ടുമ്പോൾ ഈ ചക്രം തടസ്സപ്പെടും.", "കരിങ്കൽഭിത്തി", "SEAWALLS BREAK THE CYCLE"),
        ("തിരമാല ഭിത്തിയിൽ തട്ടി തിരിച്ചുവന്ന് അടിയിലെ മണൽ കൂടുതൽ കവരും.", "ഭിത്തിക്ക് മുന്നിൽ ചോർച്ച", "SAND SCOURS AT THE WALL"),
        ("ഒരിടത്ത് ഭിത്തി കെട്ടുമ്പോൾ അടുത്ത ഇടത്ത് തീരം കൂടുതൽ നഷ്ടപ്പെടാം.", "അടുത്ത തീരം പോകുന്നു", "THE NEXT COAST LOSES MORE"),
        ("കേരള തീരത്ത് ചിലപ്പോൾ കാറ്റില്ലാത്ത ദിവസവും പെട്ടെന്ന് വലിയ തിരമാല കയറും, അതിനെ കള്ളക്കടൽ എന്ന് പറയും.", "കള്ളക്കടൽ", "THE SURPRISE SWELL: KALLAKKADAL", S(["boat", "moon"], "dusk")),
        ("ഇതിന് കാരണം ആയിരക്കണക്കിന് കിലോമീറ്റർ അകലെ തെക്കൻ സമുദ്രത്തിൽ ഉണ്ടായ കൊടുങ്കാറ്റിന്റെ തിരമാലകളാണ്.", "ദൂരെ ഒരു കൊടുങ്കാറ്റ്", "A STORM THOUSANDS OF KM AWAY"),
        ("ഇൻകോയിസ് ഇതിന് മുന്നറിയിപ്പ് നൽകാറുണ്ട്.", "INCOIS മുന്നറിയിപ്പ്", "INCOIS ISSUES WARNINGS"),
        ("മുന്നറിയിപ്പ് വന്നാൽ കടൽത്തീരത്ത് നിന്ന് മാറിനിൽക്കുകയും വള്ളങ്ങൾ സുരക്ഷിതമായി കെട്ടിയിടുകയും വേണം.", "മുന്നറിയിപ്പ് കേൾക്കൂ", "FOLLOW THE WARNING", TX("മുന്നറിയിപ്പ് കേൾക്കൂ", "LISTEN TO THE WARNING", "boat", "#c8442f")),
        ("തിരമാലകളെ അറിയുന്നത് തീരത്തെ സ്നേഹിക്കുന്നതിന്റെ ആദ്യ പടിയാണ്.", "അറിഞ്ഞാൽ കാക്കാം", "KNOW THEM TO PROTECT THE COAST"),
    ],
)
FACTS_WAVES = ["Most ocean waves are wind waves; they carry energy while water moves in small orbits, and waves break when the seabed slows their base in shallow water (NOAA Ocean Service: Waves; Britannica).",
               "Seawalls reflect wave energy and can increase scouring at their base and erosion on neighbouring beaches (National Centre for Coastal Research, India; USACE Coastal Engineering Manual).",
               "Kallakkadal is a sudden coastal swell flooding along India's southwest coast caused by distant swells from storms in the Southern Indian Ocean; INCOIS issues swell surge alerts (INCOIS; Kerala State Disaster Management Authority).",
               "Kerala's coastline is about 590 km long (Government of Kerala)."]

SALT = sh(
    "saltysea_s", "കടൽ ഉപ്പുരസമുള്ളത് എന്തുകൊണ്ട്?", "Why is the sea salty?", "കടലിന് ഉപ്പ് എവിടെ നിന്ന്?", "WHY THE SEA IS SALTY",
    [
        ("പുഴകളിലെ വെള്ളത്തിന് ഉപ്പില്ലാത്തപ്പോൾ കടലിന് മാത്രം ഉപ്പുരസം എവിടെ നിന്നാണ്?", "കടലിലെ ഉപ്പ്", "WHERE DOES THE SALT COME FROM?", S(["boat", "salt"], "sky", label=("ഉപ്പ്", "SALT"))),
        ("മഴ പാറകളെ പതുക്കെ അലിയിച്ച് അതിലെ ലവണങ്ങൾ പുഴകളിലൂടെ കടലിലേക്ക് എത്തിക്കും.", "പാറകളിൽ നിന്ന് ഉപ്പ്", "RAIN DISSOLVES SALTS FROM ROCKS"),
        ("കടൽത്തറയിലെ അഗ്നിപർവത പ്രവർത്തനങ്ങളും ലവണങ്ങൾ ചേർക്കുന്നു.", "കടലിനടിയിൽ നിന്നും", "SEA-FLOOR VENTS ADD MORE"),
        ("കടലിൽ നിന്ന് വെള്ളം മാത്രം ആവിയായി പോകും, ഉപ്പ് അവിടെ തന്നെ ബാക്കിയാകും.", "ആവിയാകും, ഉപ്പ് ബാക്കി", "WATER EVAPORATES, SALT STAYS"),
        ("കോടിക്കണക്കിന് വർഷം ഇങ്ങനെ കൂടിക്കൂടി ഇന്ന് ആയിരം ഗ്രാം കടൽവെള്ളത്തിൽ ഏകദേശം മുപ്പത്തഞ്ച് ഗ്രാം ഉപ്പ് ഉണ്ട്.", "1000 ഗ്രാമിൽ 35 ഗ്രാം", "ABOUT 35 G PER KILOGRAM", ST(35, " g", "ഒരു കിലോ കടൽവെള്ളത്തിലെ ഉപ്പ്", "SALT IN A KILO OF SEAWATER", "salt")),
        ("പുഴയിലെ വെള്ളം തുടർച്ചയായി ഒഴുകി കടലിലേക്ക് ഉപ്പ് കൊണ്ടുപോകുന്നു.", "ഉപ്പ് കൊണ്ടുപോകുന്ന പുഴ", "RIVERS KEEP DELIVERING"),
    ],
    "കടലിലെ ഉപ്പ് കോടി വർഷത്തെ സമ്പാദ്യം!", "SALT SAVED OVER BILLIONS OF YEARS", "കടലിന്റെ ഉപ്പ് കോടിക്കണക്കിന് വർഷത്തെ പുഴകളുടെ സമ്മാനമാണ്!")

BREAK = sh(
    "wavebreak_s", "തിരമാല കരയിൽ എത്തുമ്പോൾ പൊട്ടുന്നത് എന്തുകൊണ്ട്?", "Why do waves break near the shore?", "തിരമാല പൊട്ടുന്നത്", "WHY WAVES BREAK",
    [
        ("തിരമാല തീരത്ത് എത്തുമ്പോൾ മാത്രം പതഞ്ഞ് പൊട്ടുന്നത് എന്തുകൊണ്ടാണ്?", "തീരത്ത് പൊട്ടുന്നു", "WHY BREAK AT THE SHORE?", S(["boat", "drop"], "sky", ("bubbles", 25, "#fff"), label=("തിര", "WAVE"))),
        ("ആഴക്കടലിൽ തിരമാലകൾ ഒരേ ആകൃതിയിൽ നീങ്ങും.", "ആഴക്കടലിൽ ശാന്തം", "CALM IN DEEP WATER"),
        ("തീരത്തോട് അടുക്കുമ്പോൾ കടലിന്റെ അടിത്തട്ട് ഉയർന്നുവരും.", "അടിത്തട്ട് ഉയരുന്നു", "THE SEABED RISES"),
        ("തിരമാലയുടെ അടിഭാഗം തട്ടിൽ ഉരസി വേഗം കുറയും.", "അടി വേഗം കുറയും", "THE BASE SLOWS DOWN"),
        ("മുകൾഭാഗം പഴയ വേഗത്തിൽ തന്നെ മുന്നോട്ട് ഓടി തിരമാല ഉയരം കൂടി കുത്തനെയാകും.", "ഉയരം കൂടി കുത്തനെ", "THE TOP RUNS AHEAD, IT STEEPENS"),
        ("ഒടുവിൽ മുകൾഭാഗത്തിന് അടിഭാഗം താങ്ങാൻ കഴിയാതെ അത് മുന്നോട്ട് മറിഞ്ഞ് വീഴും.", "മറിഞ്ഞുവീഴുന്നു", "IT TOPPLES FORWARD"),
    ],
    "തിര പൊട്ടുന്നത് ആഴം കുറയുമ്പോൾ!", "SHALLOW WATER MAKES THEM BREAK", "തിരമാലയെ പൊട്ടിക്കുന്നത് തീരത്തെ ആഴക്കുറവാണ്!")

BLUE = sh(
    "bluesea_s", "കടലിന് നീല നിറം വരുന്നത് എന്തുകൊണ്ട്?", "Why is the sea blue?", "കടൽ നീലയാകുന്നത്", "WHY THE SEA IS BLUE",
    [
        ("ഒരു ഗ്ലാസ് വെള്ളത്തിന് നിറമില്ല, പക്ഷേ കടലിന് നീല നിറം എവിടെ നിന്നാണ്?", "കടലിന്റെ നീല", "WHERE DOES THE BLUE COME FROM?", S(["drop", "boat"], "sky", label=("നീല", "BLUE"))),
        ("ആകാശത്തിന്റെ നീല പ്രതിഫലനമാണ് കാരണം എന്ന് പലരും കരുതും, പക്ഷേ അത് മുഴുവൻ ശരിയല്ല.", "ആകാശ പ്രതിഫലനം മാത്രമല്ല", "NOT JUST THE SKY'S REFLECTION"),
        ("വെള്ളം സൂര്യപ്രകാശത്തിലെ ചുവപ്പ് വെളിച്ചം കൂടുതൽ വലിച്ചെടുക്കും.", "ചുവപ്പ് വലിച്ചെടുക്കും", "WATER ABSORBS RED LIGHT"),
        ("നീല വെളിച്ചം കുറച്ച് മാത്രം വലിച്ചെടുത്ത് തിരിച്ച് ചിതറും.", "നീല തിരിച്ചുവരും", "BLUE SCATTERS BACK"),
        ("അതുകൊണ്ട് ആഴമുള്ള വെള്ളത്തിൽ നിന്ന് നമ്മുടെ കണ്ണിലെത്തുന്നത് കൂടുതലും നീല വെളിച്ചമാണ്.", "ആഴം കൂടിയാൽ നീല", "DEEP WATER LOOKS BLUE"),
        ("കായലിലോ പുഴയിലോ ചെളിയും പായലും കൂടുതലുള്ളതുകൊണ്ട് പച്ചയോ തവിട്ടോ കാണും.", "പായൽ: പച്ച", "ALGAE AND MUD MAKE GREEN"),
    ],
    "വെള്ളം നിറം തിരഞ്ഞെടുക്കുന്നു!", "WATER PICKS ITS COLOURS", "വെള്ളം ചുവപ്പ് വിഴുങ്ങി നീല തിരിച്ചുതരുന്നു!")

SAND = sh(
    "blacksand_s", "ചവറയിലെ കടൽത്തീരത്തെ കറുത്ത മണലിന്റെ രഹസ്യം", "What is the black sand on the Kerala coast?", "കറുത്ത മണൽ!", "KERALA'S BLACK SAND",
    [
        ("കേരളത്തിലെ ചില കടൽത്തീരങ്ങളിൽ മണൽ കറുത്തിരിക്കുന്നത് എന്തുകൊണ്ടാണ്?", "കറുത്ത മണൽ", "WHY IS THE SAND BLACK?", S(["boat", "mountain"], "dusk", label=("കറുത്ത മണൽ", "BLACK SAND"))),
        ("ഇതിൽ ഇൽമനൈറ്റ്, റൂട്ടൈൽ, മോണസൈറ്റ് തുടങ്ങിയ കനത്ത ധാതുക്കൾ ധാരാളമുണ്ട്.", "കനത്ത ധാതുക്കൾ", "RICH IN HEAVY MINERALS"),
        ("പശ്ചിമഘട്ടത്തിലെ പാറകൾ പൊടിഞ്ഞ് പുഴകളിലൂടെ കടലിലെത്തിയതാണ് ഇവ.", "മലകളിൽ നിന്ന് വന്നവർ", "WASHED DOWN FROM THE GHATS"),
        ("തിരമാലകൾ ഭാരം കുറഞ്ഞ മണൽ കൊണ്ടുപോകുകയും ഭാരമുള്ള ധാതുക്കളെ തീരത്ത് ബാക്കിവയ്ക്കുകയും ചെയ്യും.", "ഭാരമുള്ളവ ബാക്കി", "WAVES LEAVE THE HEAVY GRAINS"),
        ("ഇൽമനൈറ്റ് ടൈറ്റാനിയം ഉണ്ടാക്കാൻ ഉപയോഗിക്കുന്നു, അത് ചായങ്ങളിലും വിമാനഭാഗങ്ങളിലും ഉപയോഗമുണ്ട്.", "ടൈറ്റാനിയം", "ILMENITE MAKES TITANIUM"),
        ("മോണസൈറ്റിൽ ചെറിയ തോതിൽ റേഡിയോ ആക്ടീവ് മൂലകമായ തോറിയം ഉണ്ട്.", "തോറിയം", "MONAZITE HAS THORIUM"),
    ],
    "മണലിൽ ഒളിഞ്ഞ നിധി!", "TREASURE IN THE SAND", "കേരളത്തിലെ കറുത്ത മണലിൽ മലകളുടെ ചരിത്രം ഒളിഞ്ഞിരിക്കുന്നു!")

GILL = sh(
    "fishgill_s", "മീൻ വെള്ളത്തിൽ ശ്വസിക്കുന്നത് എങ്ങനെ?", "How does a fish breathe underwater?", "മീനിന്റെ ശ്വാസം", "HOW FISH BREATHE",
    [
        ("മീനുകൾ വെള്ളത്തിനടിയിൽ ശ്വസിക്കുന്നത് എങ്ങനെയാണ്?", "വെള്ളത്തിൽ ശ്വാസം", "BREATHING UNDERWATER", S(["drop", "boat"], "sky", label=("മീൻ", "FISH"))),
        ("വെള്ളത്തിൽ ലയിച്ചിരിക്കുന്ന ഓക്സിജൻ വളരെ കുറച്ച് മാത്രമാണ്.", "വെള്ളത്തിൽ ഓക്സിജൻ കുറവ്", "LITTLE OXYGEN IN WATER"),
        ("മീൻ വായിലൂടെ വെള്ളം ഉള്ളിലേക്ക് എടുത്ത് ചെകിളകളിലൂടെ പുറത്തേക്ക് വിടും.", "വായ്, ചെകിള", "MOUTH IN, GILLS OUT"),
        ("ചെകിളയിൽ ചെറിയ രക്തക്കുഴലുകൾ നിറഞ്ഞ നേർത്ത ഇതളുകൾ ഉണ്ട്.", "ഇതളുകളിൽ രക്തക്കുഴൽ", "THIN FILAMENTS FULL OF BLOOD"),
        ("വെള്ളത്തിലെ ഓക്സിജൻ ആ നേർത്ത ഭിത്തിയിലൂടെ രക്തത്തിലേക്ക് കടക്കും.", "ഓക്സിജൻ രക്തത്തിലേക്ക്", "OXYGEN ENTERS THE BLOOD"),
        ("വെള്ളത്തിന് പുറത്തെടുത്താൽ ചെകിളകൾ ഒട്ടിച്ചേർന്ന് വായു കിട്ടാതെ മീൻ പിടയും.", "പുറത്തെടുത്താൽ", "OUT OF WATER, GILLS COLLAPSE"),
    ],
    "ചെകിള എന്ന ശ്വാസകോശം!", "THE GILL IS ITS LUNG", "ചെകിളയാണ് മീനിന്റെ ശ്വാസകോശം!")

FLOAT = sh(
    "floating_s", "കടലിൽ മുങ്ങാതെ പൊങ്ങിക്കിടക്കാൻ എളുപ്പമാകുന്നത് എന്തുകൊണ്ട്?", "Why is it easier to float in the sea?", "കടലിൽ പൊങ്ങിക്കിടക്കാം!", "FLOATING IN SEAWATER",
    [
        ("പുഴയിൽ മുങ്ങിപ്പോകുന്ന ആൾക്ക് കടലിൽ എളുപ്പത്തിൽ പൊങ്ങിക്കിടക്കാൻ കഴിയുന്നത് എന്തുകൊണ്ടാണ്?", "കടലിൽ പൊങ്ങും", "EASIER TO FLOAT AT SEA", S(["person", "boat"], "sky", label=("പൊങ്ങിക്കിടക്കാം", "FLOAT"))),
        ("വെള്ളം നമ്മളെ മുകളിലേക്ക് തള്ളുന്ന ബലത്തെ പ്ലവക്ഷമബലം എന്ന് പറയും.", "പ്ലവക്ഷമബലം", "BUOYANT FORCE"),
        ("ആ ബലം നമ്മൾ മാറ്റിനിർത്തുന്ന വെള്ളത്തിന്റെ ഭാരത്തിന് തുല്യമാണ്.", "മാറ്റിനിർത്തിയ വെള്ളത്തിന്റെ ഭാരം", "THE WEIGHT OF DISPLACED WATER"),
        ("ഉപ്പുവെള്ളത്തിന് ശുദ്ധജലത്തേക്കാൾ സാന്ദ്രത കൂടുതലാണ്.", "ഉപ്പുവെള്ളം സാന്ദ്രം", "SALT WATER IS DENSER"),
        ("അതുകൊണ്ട് ഒരേ അളവ് വെള്ളം മാറ്റിനിർത്തുമ്പോൾ കടൽവെള്ളത്തിൽ കൂടുതൽ മുകളിലേക്കുള്ള ബലം കിട്ടും.", "കൂടുതൽ മുകളിലേക്ക് ബലം", "MORE UPWARD PUSH"),
        ("ഇസ്രായേലിലെ ചാവുകടലിൽ ഉപ്പ് ഇതിലും വളരെ കൂടുതലായതുകൊണ്ട് ആളുകൾക്ക് മുങ്ങാതെ ഇരുന്ന് പത്രം വായിക്കാം.", "ചാവുകടലിൽ പത്രം വായന", "READING A PAPER IN THE DEAD SEA"),
    ],
    "ഉപ്പ് നമ്മളെ താങ്ങുന്നു!", "SALT HOLDS US UP", "കടലിലെ ഉപ്പ് നമ്മളെ താങ്ങിനിർത്തുന്ന ഒരു കൂട്ടുകാരനാണ്!")

FACTS = [
    "Seawater's salt comes from rock weathering carried by rivers and from sea-floor vents; water evaporates and salts remain, giving about 35 g of salt per kg (NOAA Ocean Service: Why is the ocean salty).",
    "Waves break in shallow water as the base slows against the seabed while the crest keeps moving (NOAA; Britannica: Breaker).",
    "Water absorbs red light more strongly than blue, so deep water looks blue (USGS Water Science School; Pope and Fry 1997).",
    "Kerala's coastal sands carry heavy minerals such as ilmenite, rutile and monazite (Indian Rare Earths Ltd; Geological Survey of India).",
    "Fish extract dissolved oxygen through gill filaments rich in blood vessels (Britannica: Gill).",
    "Seawater is denser than fresh water, so it gives a larger buoyant force; the Dead Sea is far saltier (Britannica: Buoyancy; Dead Sea).",
] + FACTS_WAVES
VIDEOS = [WAVES, SALT, BREAK, BLUE, SAND, GILL, FLOAT]
