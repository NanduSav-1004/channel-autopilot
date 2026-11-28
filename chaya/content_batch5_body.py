"""Science Chaya batch 5: the body (why we get a fever long; hiccups, wrinkled fingers, goosebumps, yawning, soap, the heart Shorts)."""
from chaya.quick import ST, TX, S, lg, sh

FEVER = lg(
    "fever_long", "പനി വരുന്നത് എന്തിന്? | ശരീരത്തിന്റെ ചൂടിന് പിന്നിലെ ശാസ്ത്രം", "Why do we get a fever? The science behind the body's heat",
    "പനി വരുന്നത് എന്തിന്?", "WHY WE GET FEVER", "പനി വരുമ്പോൾ നിങ്ങളുടെ വീട്ടിൽ ആദ്യം ചെയ്യുന്ന കാര്യം എന്താണ്?", "WHAT IS THE FIRST THING YOU DO AT HOME?",
    [
        ("പനി വന്നാൽ നമുക്ക് ക്ഷീണവും വിറയലും തോന്നും.", "പനിയും വിറയലും", "FEVER AND SHIVERS", S(["thermo", "person"], "dusk", label=("പനി", "FEVER"))),
        ("പക്ഷേ പനി ഒരു രോഗമല്ല, ശരീരത്തിന്റെ ഒരു പ്രതിരോധ തന്ത്രമാണ്.", "പനി = പ്രതിരോധം", "A DEFENCE, NOT A DISEASE"),
        ("ഇന്ന് ആ തന്ത്രം എങ്ങനെ പ്രവർത്തിക്കുന്നു എന്ന് നോക്കാം.", "ഇന്നത്തെ വിഷയം", "HOW THE TRICK WORKS", TX("പനിയുടെ രഹസ്യം", "THE SECRET OF FEVER", "thermo", "#c8442f")),
        ("ആരോഗ്യമുള്ള ഒരാളുടെ ശരീര താപനില ഏകദേശം മുപ്പത്തിയേഴ് ഡിഗ്രി സെൽഷ്യസാണ്.", "ഏകദേശം 37 °C", "NORMAL IS ABOUT 37 °C", ST(37, " °C", "സാധാരണ ശരീര താപനില", "NORMAL BODY TEMPERATURE", "thermo")),
        ("തലച്ചോറിലെ ഹൈപ്പോതലാമസ് എന്ന ഭാഗം ഒരു തെർമോസ്റ്റാറ്റ് പോലെ ഈ താപനില നിയന്ത്രിക്കുന്നു.", "ഹൈപ്പോതലാമസ്", "THE BRAIN'S THERMOSTAT"),
        ("രോഗാണുക്കൾ ശരീരത്തിൽ കയറുമ്പോൾ പ്രതിരോധ കോശങ്ങൾ സൈറ്റോകൈനുകൾ എന്ന സന്ദേശവാഹക വസ്തുക്കൾ പുറത്തുവിടും.", "പ്രതിരോധ സന്ദേശങ്ങൾ", "IMMUNE CELLS SEND SIGNALS", S(["person"], "dark")),
        ("ആ സന്ദേശങ്ങൾ ഹൈപ്പോതലാമസിനോട് താപനില കൂട്ടാൻ പറയും.", "താപനില കൂട്ടൂ", "TURN THE THERMOSTAT UP"),
        ("തെർമോസ്റ്റാറ്റ് ഉയർത്തി വച്ചാൽ ശരീരത്തിന് ഇപ്പോഴത്തെ ചൂട് കുറവായി തോന്നും.", "ചൂട് കുറവായി തോന്നും", "NORMAL NOW FEELS COLD"),
        ("അതുകൊണ്ടാണ് പനി തുടങ്ങുമ്പോൾ തണുപ്പ് തോന്നി വിറയ്ക്കുന്നത്.", "തണുപ്പും വിറയലും", "WHY YOU SHIVER", S(["thermo"], "storm", text="വിറയൽ", anim="shake")),
        ("വിറയൽ പേശികൾ ചൂട് ഉണ്ടാക്കാനുള്ള ശരീരത്തിന്റെ മാർഗമാണ്.", "വിറയൽ = ചൂടുണ്ടാക്കൽ", "SHIVERING MAKES HEAT"),
        ("തൊലിയിലെ രക്തക്കുഴലുകൾ ചുരുങ്ങി ചൂട് പുറത്തുപോകുന്നത് തടയും.", "രക്തക്കുഴലുകൾ ചുരുങ്ങുന്നു", "SKIN VESSELS NARROW"),
        ("താപനില പുതിയ നിലയിലെത്തുമ്പോൾ ശരീരം ചൂടാണെന്ന് നമുക്ക് തോന്നും.", "ചൂട് തോന്നുന്നു", "NOW YOU FEEL HOT"),
        ("പനി മുപ്പത്തിയെട്ട് ഡിഗ്രിക്ക് മുകളിലായാൽ പനിയായി കണക്കാക്കും.", "38 °C ന് മുകളിൽ", "ABOVE 38 °C IS A FEVER"),
        ("ഇനി ചോദ്യം, ശരീരം എന്തിനാണ് ഇങ്ങനെ ചൂടാകുന്നത്?", "എന്തിന് ചൂടാകുന്നു?", "WHY HEAT UP?", TX("എന്തിന് ചൂട്?", "WHY HEAT UP?", "thermo", "#4a2a17")),
        ("ഉയർന്ന ചൂടിൽ പല രോഗാണുക്കൾക്കും പെരുകാൻ ബുദ്ധിമുട്ടാണ്.", "രോഗാണുക്കൾക്ക് ബുദ്ധിമുട്ട്", "GERMS STRUGGLE IN THE HEAT"),
        ("അതേ സമയം പ്രതിരോധ കോശങ്ങൾ കൂടുതൽ വേഗത്തിൽ പ്രവർത്തിക്കും.", "പ്രതിരോധം വേഗത്തിൽ", "DEFENCES WORK FASTER"),
        ("ചൂട് കൊണ്ടുള്ള ഈ ഇരട്ട ഗുണം കൊണ്ടാണ് പരിണാമത്തിൽ പനി നിലനിന്നത്.", "ഇരട്ട ഗുണം", "A DOUBLE BENEFIT"),
        ("പാരസെറ്റാമോൾ പോലുള്ള മരുന്നുകൾ ഈ തെർമോസ്റ്റാറ്റിനെ താഴേക്ക് കൊണ്ടുവരാൻ സഹായിക്കും.", "തെർമോസ്റ്റാറ്റ് താഴ്ത്തുന്നു", "MEDICINE LOWERS THE SETTING", S(["thermo"], "dusk")),
        ("അപ്പോൾ ശരീരം വിയർത്ത് ചൂട് പുറത്തുകളയും.", "വിയർത്ത് ചൂട് പോകും", "SWEATING CARRIES HEAT OUT"),
        ("പനിയിൽ ധാരാളം വെള്ളം കുടിക്കുകയും വിശ്രമിക്കുകയും വേണം.", "വെള്ളം, വിശ്രമം", "DRINK AND REST", S(["cup"], "dusk", text="വെള്ളവും വിശ്രമവും")),
        ("പനി മൂന്ന് ദിവസത്തിൽ കൂടുതൽ നീണ്ടാൽ ഡോക്ടറെ കാണണം.", "3 ദിവസത്തിൽ കൂടിയാൽ", "OVER THREE DAYS? SEE A DOCTOR"),
        ("വളരെ ഉയർന്ന പനിയും ഫിറ്റ്സും ശ്വാസംമുട്ടലും ഉണ്ടെങ്കിൽ ഉടൻ ആശുപത്രിയിൽ പോകണം.", "ഉടൻ ആശുപത്രി", "SEVERE SIGNS NEED A HOSPITAL NOW"),
        ("ചെറിയ കുട്ടികളിലും പ്രായമായവരിലും പനിയെ ഒരിക്കലും അവഗണിക്കരുത്.", "കുട്ടികളും മുതിർന്നവരും", "NEVER IGNORE IT IN THE YOUNG AND OLD"),
        ("അപ്പോൾ പനി ശരീരത്തിന്റെ ഒരു അലാറം കൂടിയാണ്.", "പനി ഒരു അലാറം", "FEVER IS AN ALARM", TX("പനി = അലാറം", "AN ALARM AND A DEFENCE", "thermo", "#2f7d4f")),
        ("അതിനെ ശ്രദ്ധയോടെ കേൾക്കുന്നത് ആരോഗ്യത്തിന് നല്ലതാണ്.", "ശ്രദ്ധയോടെ കേൾക്കൂ", "LISTEN TO IT"),
    ],
)
FACTS_FEVER = ["Fever occurs when pyrogens such as cytokines raise the hypothalamic temperature set-point; shivering and skin vasoconstriction raise body temperature to the new set-point (Cleveland Clinic; StatPearls: Physiology, Fever).",
               "Normal body temperature is about 37 degrees Celsius and a fever is generally above 38 degrees (NHS; WHO).",
               "Higher temperatures can slow some pathogens and speed up some immune responses (Evans et al., Nature Reviews Immunology 2015)."]

HICCUP = sh(
    "hiccup_s", "എക്കിൾ വരുന്നത് എന്തുകൊണ്ട്?", "Why do we get hiccups?", "എക്കിൾ വരുന്നത്", "HICCUPS",
    [
        ("പെട്ടെന്ന് എക്കിൾ വരുന്നത് എന്തുകൊണ്ടാണ്?", "എക്കിൾ!", "WHY HICCUPS?", S(["person"], "dusk", label=("എക്കിൾ", "HIC!"))),
        ("നെഞ്ചിനെയും വയറിനെയും വേർതിരിക്കുന്ന ഡയഫ്രം എന്ന പേശിയാണ് ശ്വസിക്കാൻ സഹായിക്കുന്നത്.", "ഡയഫ്രം പേശി", "THE BREATHING MUSCLE"),
        ("അത് പെട്ടെന്ന് വലിഞ്ഞുമുറുകി ഒരു വലിയ തവണ ഉള്ളിലേക്ക് ശ്വാസം വലിക്കും.", "പെട്ടെന്ന് വലിവ്", "A SUDDEN SPASM"),
        ("അതേ നിമിഷം തൊണ്ടയിലെ വോക്കൽ കോഡുകൾ അടഞ്ഞുപോകും.", "തൊണ്ട അടയുന്നു", "THE VOCAL CORDS SNAP SHUT"),
        ("വായു തടയപ്പെടുമ്പോഴാണ് ആ 'ഹിക്' ശബ്ദം ഉണ്ടാകുന്നത്.", "ഹിക് ശബ്ദം", "THAT HIC SOUND"),
        ("വേഗത്തിൽ കഴിക്കുന്നതും ധാരാളം കാർബണേറ്റഡ് പാനീയവും ഇതിന് കാരണമാകാം, മിക്കവാറും ചെറിയ നേരം കൊണ്ട് മാറും.", "പെട്ടെന്ന് മാറും", "USUALLY IT PASSES SOON"),
    ],
    "പേശിയുടെ ഒരു കുസൃതി!", "A MUSCLE'S PRANK", "എക്കിൾ ഡയഫ്രത്തിന്റെ ഒരു ചെറിയ കുസൃതിയാണ്!")

WRINKLE = sh(
    "pruning_s", "വെള്ളത്തിൽ കിടന്നാൽ വിരലുകൾ ചുളിയുന്നത് എന്തിന്?", "Why do fingers wrinkle in water?", "വിരൽ ചുളിയുന്നത്", "WRINKLED FINGERS",
    [
        ("കുളിച്ച് കഴിയുമ്പോൾ വിരലുകൾ ചുളിഞ്ഞിരിക്കുന്നത് എന്തുകൊണ്ടാണ്?", "ചുളിഞ്ഞ വിരലുകൾ", "WHY WRINKLED?", S(["drop", "person"], "sky")),
        ("തൊലി വെള്ളം വലിച്ചെടുത്ത് വീർക്കുന്നതുകൊണ്ടാണ് എന്നാണ് പണ്ട് കരുതിയിരുന്നത്.", "പഴയ വിശദീകരണം", "THE OLD EXPLANATION"),
        ("പക്ഷേ ഇത് ഞരമ്പുകളുടെ നിയന്ത്രണത്തിൽ നടക്കുന്ന ഒന്നാണെന്ന് ഇപ്പോൾ അറിയാം.", "ഞരമ്പ് നിയന്ത്രണം", "THE NERVES CONTROL IT"),
        ("വിരലിലെ രക്തക്കുഴലുകൾ ചുരുങ്ങുമ്പോൾ തൊലി ഉള്ളിലേക്ക് വലിഞ്ഞ് ചുളിവുകൾ ഉണ്ടാകും.", "രക്തക്കുഴലുകൾ ചുരുങ്ങുന്നു", "VESSELS NARROW, SKIN FOLDS"),
        ("ഈ ചുളിവുകൾ ടയറിലെ ചാലുകൾ പോലെ വെള്ളം ഒഴുക്കിക്കളഞ്ഞ് പിടിത്തം കൂട്ടുമെന്ന് പഠനങ്ങൾ പറയുന്നു.", "പിടിത്തം കൂട്ടും", "BETTER GRIP IN WET"),
        ("നനഞ്ഞ വസ്തുക്കൾ പിടിക്കാൻ ഇത് സഹായിക്കുമെന്ന് ഒരു ഗവേഷണത്തിൽ കണ്ടു.", "നനഞ്ഞാലും പിടിക്കാം", "HELPS HOLD WET OBJECTS"),
    ],
    "വിരലിന്റെ റെയിൻ ടയർ!", "RAIN TYRES FOR YOUR FINGERS", "വിരലുകൾ നനയുമ്പോൾ ടയർ പോലെ പിടിത്തം കൂട്ടുകയാണ്!")

GOOSE = sh(
    "goosebumps_s", "രോമാഞ്ചം വരുന്നത് എന്തുകൊണ്ട്?", "Why do we get goosebumps?", "രോമാഞ്ചം!", "GOOSEBUMPS",
    [
        ("ഒരു പാട്ട് കേൾക്കുമ്പോഴോ തണുക്കുമ്പോഴോ രോമം എഴുന്നുനിൽക്കുന്നത് എന്തുകൊണ്ടാണ്?", "രോമാഞ്ചം", "WHY THE SHIVER?", S(["person"], "storm", label=("രോമാഞ്ചം", "GOOSEBUMPS"))),
        ("ഓരോ രോമത്തിന്റെയും അടിയിൽ ഒരു ചെറിയ പേശി ഉണ്ട്.", "രോമത്തിനടിയിൽ പേശി", "A TINY MUSCLE UNDER EACH HAIR"),
        ("തണുപ്പോ പേടിയോ വികാരമോ തോന്നുമ്പോൾ ഞരമ്പുകൾ ആ പേശിയെ ചുരുക്കും.", "പേശി ചുരുങ്ങുന്നു", "THE NERVES TIGHTEN IT"),
        ("അപ്പോൾ രോമം എഴുന്നേറ്റ് തൊലിയിൽ ചെറിയ മുഴകൾ ഉണ്ടാകും.", "മുഴകളും രോമവും", "HAIRS STAND, SKIN BUMPS"),
        ("പണ്ട് ശരീരം നിറയെ രോമമുള്ള പൂർവികർക്ക് ഇത് ചൂട് പിടിച്ചുനിർത്തി.", "പൂർവികരുടെ ചൂട്", "IT TRAPPED HEAT FOR FURRY ANCESTORS"),
        ("ഇന്ന് നമുക്ക് അതിന്റെ ഗുണം കാര്യമായില്ലെങ്കിലും ആ ശീലം ബാക്കിയായി.", "ബാക്കിയായ ശീലം", "THE HABIT REMAINS"),
    ],
    "പൂർവികരുടെ ഓർമ്മ ശരീരത്തിൽ!", "A MEMORY FROM OUR ANCESTORS", "ഓരോ രോമാഞ്ചവും നമ്മുടെ പൂർവികരുടെ ഒരു ഓർമ്മയാണ്!")

YAWN = sh(
    "yawn_s", "കോട്ടുവായ് ഇടുന്നത് എന്തിന്? മറ്റുള്ളവർ ഇടുന്നത് കണ്ടാൽ നമ്മളും ഇടുന്നത് എന്തുകൊണ്ട്?", "Why do we yawn, and why is yawning contagious?", "കോട്ടുവായ് രഹസ്യം", "WHY WE YAWN",
    [
        ("ഒരാൾ കോട്ടുവായ് ഇടുന്നത് കണ്ടാൽ നമ്മളും ഇടുന്നത് എന്തുകൊണ്ടാണ്?", "പകരുന്ന കോട്ടുവായ്", "CONTAGIOUS YAWNS", S(["person"], "dusk", label=("ആവൂ!", "YAWN"))),
        ("കോട്ടുവായ് എന്തിനാണെന്ന് ശാസ്ത്രജ്ഞർക്ക് ഇപ്പോഴും പൂർണ്ണമായി ഉറപ്പില്ല.", "ഉറപ്പില്ലാത്ത രഹസ്യം", "SCIENCE IS NOT SURE YET"),
        ("ഒരു സിദ്ധാന്തം പറയുന്നത് തലച്ചോറിനെ തണുപ്പിക്കാൻ ആണെന്നാണ്.", "തലച്ചോറിന് തണുപ്പ്", "ONE IDEA: COOLING THE BRAIN"),
        ("ക്ഷീണം, ബോറടി, ഉറക്കം എന്നിവയുടെ സമയത്താണ് കോട്ടുവായ് കൂടുതലും വരുന്നത്.", "ഉറക്കത്തിന്റെ സൂചന", "TIRED AND BORED TIMES"),
        ("മറ്റൊരാളുടെ കോട്ടുവായ് കണ്ടാൽ നമ്മളും ഇടുന്നത് സഹാനുഭൂതിയുമായി ബന്ധപ്പെട്ടിരിക്കാം എന്ന് പഠനങ്ങൾ സൂചിപ്പിക്കുന്നു.", "സഹാനുഭൂതിയുമായി ബന്ധം", "LINKED TO EMPATHY, SAY STUDIES"),
        ("ഈ വീഡിയോ കണ്ടപ്പോൾ നിങ്ങൾ കോട്ടുവായ് ഇട്ടോ?", "നിങ്ങൾ ഇട്ടോ?", "DID YOU YAWN?"),
    ],
    "ഒരു കോട്ടുവായ്, ഒരു രഹസ്യം!", "A YAWN, A MYSTERY", "കോട്ടുവായുടെ രഹസ്യം ശാസ്ത്രം ഇപ്പോഴും തിരയുകയാണ്!")

SOAP = sh(
    "soap_s", "സോപ്പ് രോഗാണുക്കളെ കൊല്ലുന്നത് എങ്ങനെ?", "How does soap kill germs?", "സോപ്പിന്റെ ശക്തി", "HOW SOAP WORKS",
    [
        ("വെറും സോപ്പും വെള്ളവും കൊണ്ട് രോഗാണുക്കളെ ഇല്ലാതാക്കുന്നത് എങ്ങനെയാണ്?", "സോപ്പ് എന്ന ആയുധം", "SOAP, THE WEAPON", S(["drop", "bottle"], "sky")),
        ("പല വൈറസുകൾക്കും ചുറ്റും കൊഴുപ്പ് കൊണ്ടുള്ള ഒരു ആവരണം ഉണ്ട്.", "കൊഴുപ്പ് ആവരണം", "A FATTY COAT"),
        ("സോപ്പിന്റെ തന്മാത്രകൾക്ക് ഒരറ്റം വെള്ളത്തോടും മറ്റേ അറ്റം കൊഴുപ്പിനോടും ഇഷ്ടമാണ്.", "ഒരറ്റം വെള്ളം, മറ്റേത് കൊഴുപ്പ്", "ONE END LOVES WATER, THE OTHER FAT"),
        ("അവ ആ കൊഴുപ്പ് ആവരണത്തെ പൊളിച്ച് വൈറസിനെ നശിപ്പിക്കും.", "ആവരണം പൊളിക്കും", "THEY BREAK THE COAT OPEN"),
        ("അഴുക്കും രോഗാണുക്കളും കൈയിൽ നിന്ന് ഇളകി വെള്ളത്തിൽ ഒഴുകിപ്പോകും.", "ഒഴുകിപ്പോകുന്നു", "THEY WASH AWAY"),
        ("അതുകൊണ്ട് ഇരുപത് സെക്കൻഡ് നേരം നന്നായി തേച്ച് കഴുകണം.", "20 സെക്കൻഡ് കഴുകൂ", "SCRUB FOR TWENTY SECONDS", ST(20, " സെക്കൻഡ്", "കൈ കഴുകാൻ വേണ്ട സമയം", "SCRUB TIME", "drop")),
    ],
    "സോപ്പ് ഒരു ചെറിയ കവചം!", "SOAP IS A TINY SHIELD", "ഇരുപത് സെക്കൻഡ് സോപ്പിട്ട് കഴുകിയാൽ രോഗം തടയാം!")

HEART = sh(
    "heart_s", "ഹൃദയം ഒരു ദിവസം എത്ര തവണ മിടിക്കും?", "How many times does your heart beat in a day?", "ഹൃദയമിടിപ്പ് കണക്ക്", "YOUR HEART",
    [
        ("ഒരു ദിവസം നിങ്ങളുടെ ഹൃദയം എത്ര തവണ മിടിക്കും?", "ഹൃദയമിടിപ്പ്", "HOW MANY BEATS A DAY?", S(["person"], "dusk", label=("ഹൃദയം", "HEART"))),
        ("വിശ്രമത്തിൽ ഒരാളുടെ ഹൃദയം മിനിറ്റിൽ ഏകദേശം എഴുപത്തിരണ്ട് തവണ മിടിക്കും.", "മിനിറ്റിൽ ≈ 72", "ABOUT 72 A MINUTE", ST(72, " / മിനിറ്റ്", "വിശ്രമത്തിലെ ഹൃദയമിടിപ്പ്", "RESTING HEART RATE", "person")),
        ("അതായത് ഒരു ദിവസം ഒരു ലക്ഷത്തോളം തവണ.", "ദിവസം ഒരു ലക്ഷം", "ABOUT 100,000 A DAY"),
        ("ഒരു വർഷം മൂന്നര കോടിയിലധികം തവണ.", "വർഷം 3.5 കോടി", "OVER 35 MILLION A YEAR"),
        ("ഓരോ മിടിപ്പിലും ഹൃദയം ശരീരമാകെ രക്തം പമ്പ് ചെയ്യുന്നു.", "ശരീരമാകെ രക്തം", "PUMPING BLOOD EVERYWHERE"),
        ("ഒരിക്കലും വിശ്രമമില്ലാതെ പ്രവർത്തിക്കുന്ന ഈ പേശിയെ നമ്മൾ നന്നായി നോക്കണം.", "ഹൃദയത്തെ നോക്കൂ", "TAKE CARE OF IT"),
    ],
    "ഒരിക്കലും നിൽക്കാത്ത പമ്പ്!", "THE PUMP THAT NEVER STOPS", "ഈ വീഡിയോ കാണുന്ന നേരത്ത് പോലും ഹൃദയം നിങ്ങൾക്കായി മിടിക്കുന്നു!")

FACTS = [
    "Hiccups are involuntary diaphragm spasms followed by sudden closure of the vocal cords (Cleveland Clinic: Hiccups).",
    "Finger wrinkling in water is controlled by the nervous system, which narrows blood vessels; the wrinkles may improve grip on wet objects (Changizi et al. 2011; Kareklas et al. 2013).",
    "Goosebumps are caused by arrector pili muscles pulling hairs upright (Wikipedia: Goose bumps; NHS).",
    "The purpose of yawning is not settled; brain cooling and social contagion are among the hypotheses (Gallup 2011; Wikipedia: Yawn).",
    "Soap molecules disrupt the fatty envelope of many viruses and lift germs off the skin; wash for at least 20 seconds (CDC; WHO).",
    "A resting adult heart beats about 60 to 100 times a minute (American Heart Association).",
] + FACTS_FEVER
VIDEOS = [FEVER, HICCUP, WRINKLE, GOOSE, YAWN, SOAP, HEART]
