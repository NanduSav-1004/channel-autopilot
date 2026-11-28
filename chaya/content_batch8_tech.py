"""Science Chaya batch 8: everyday technology (how a phone call travels long; QR code, phone heating, induction cooker, GPS, touchscreen, microwave Shorts)."""
from chaya.quick import ST, TX, S, lg, rich, sh

CALL = lg(
    "phonecall_long", "ഫോൺ വിളിക്കുമ്പോൾ ശബ്ദം എങ്ങനെ അപ്പുറത്തെത്തുന്നു? | മൊബൈൽ നെറ്റ്‌വർക്കിന്റെ ശാസ്ത്രം", "How does your voice reach the other phone? The science of a mobile network",
    "ഫോൺ കോൾ എങ്ങനെ?", "HOW A PHONE CALL TRAVELS", "ഏറ്റവും ഒടുവിൽ ഫോണിൽ സിഗ്നൽ ഇല്ലാതെ കുടുങ്ങിയത് എവിടെ വച്ചാണ്?", "WHERE DID YOU LAST LOSE SIGNAL?",
    [
        ("നിങ്ങൾ ഒരാളെ ഫോൺ വിളിക്കുമ്പോൾ ഒരു സെക്കൻഡിനുള്ളിൽ അയാളുടെ ഫോൺ ബെല്ലടിക്കുന്നു.", "ഒരു സെക്കൻഡിൽ ബെൽ", "RINGING IN A SECOND", S(["phone", "phone"], "dusk", label=("ഫോൺ കോൾ", "A PHONE CALL"))),
        ("ഇടയിൽ എന്താണ് സംഭവിക്കുന്നത്?", "ഇടയിൽ എന്ത്?", "WHAT HAPPENS IN BETWEEN?", TX("ഇടയിൽ എന്ത്?", "WHAT HAPPENS IN BETWEEN?", "phone", "#4a2a17")),
        ("ഇന്ന് ആ യാത്ര ഘട്ടം ഘട്ടമായി പിന്തുടരാം.", "യാത്ര പിന്തുടരാം", "FOLLOW THE JOURNEY"),
        ("ആദ്യം നിങ്ങളുടെ ശബ്ദം ഫോണിലെ മൈക്രോഫോണിൽ എത്തും.", "1. മൈക്രോഫോൺ", "STEP ONE: THE MICROPHONE", S(["phone"], "dusk", text="ശബ്ദം")),
        ("മൈക്രോഫോൺ ശബ്ദത്തിന്റെ വിറയലിനെ വൈദ്യുത സിഗ്നലാക്കി മാറ്റും.", "ശബ്ദം → വൈദ്യുതി", "SOUND BECOMES ELECTRICITY"),
        ("ഫോൺ ആ സിഗ്നലിനെ പൂജ്യവും ഒന്നും ചേർന്ന ഡിജിറ്റൽ കോഡാക്കും.", "പൂജ്യവും ഒന്നും", "TURNED INTO ZEROS AND ONES", S(["phone"], "dark", ("bubbles", 22, "#fff6e2"))),
        ("ആ കോഡ് റേഡിയോ തരംഗമായി ആകാശത്തിലൂടെ പുറപ്പെടും.", "റേഡിയോ തരംഗം", "SENT AS A RADIO WAVE", S(["phone", "satellite"], "sky")),
        ("റേഡിയോ തരംഗങ്ങൾ പ്രകാശത്തിന്റെ വേഗത്തിൽ, സെക്കൻഡിൽ മൂന്ന് ലക്ഷം കിലോമീറ്റർ സഞ്ചരിക്കും.", "സെക്കൻഡിൽ 3 ലക്ഷം km", "THE SPEED OF LIGHT", ST(300000, " km/s", "റേഡിയോ തരംഗത്തിന്റെ വേഗം", "THE SPEED OF A RADIO WAVE", "bolt")),
        ("അത് ഏറ്റവും അടുത്തുള്ള മൊബൈൽ ടവറിൽ ചെന്നെത്തും.", "2. മൊബൈൽ ടവർ", "STEP TWO: THE TOWER", S(["pylon"], "sky", label=("ടവർ", "TOWER"))),
        ("ടവറുകൾ സ്ഥലത്തെ ചെറിയ മേഖലകളായി ഭാഗിക്കും, ഓരോ മേഖലയെയും സെൽ എന്ന് പറയും.", "സെല്ലുകൾ", "THE LAND IS SPLIT INTO CELLS"),
        ("അതുകൊണ്ടാണ് മൊബൈൽ ഫോണിനെ സെല്ലുലാർ ഫോൺ എന്ന് വിളിക്കുന്നത്.", "സെല്ലുലാർ ഫോൺ", "WHY IT IS CALLED CELLULAR"),
        ("അടുത്തടുത്ത സെല്ലുകൾ വ്യത്യസ്ത ആവൃത്തികൾ ഉപയോഗിക്കും, അങ്ങനെ ശബ്ദങ്ങൾ കൂടിക്കലരില്ല.", "വ്യത്യസ്ത ആവൃത്തി", "NEIGHBOURS USE OTHER FREQUENCIES"),
        ("ദൂരെയുള്ള സെല്ലുകൾക്ക് അതേ ആവൃത്തി വീണ്ടും ഉപയോഗിക്കാം, അങ്ങനെ കുറച്ച് ആവൃത്തി കൊണ്ട് ലക്ഷക്കണക്കിന് ഫോണുകൾ പ്രവർത്തിക്കും.", "ആവൃത്തി വീണ്ടും ഉപയോഗം", "REUSE FAR AWAY"),
        ("ഇനി ടവറിൽ നിന്ന് മുന്നോട്ടുള്ള വഴി.", "3. ഫൈബർ കേബിൾ", "STEP THREE: FIBRE", TX("ഫൈബർ കേബിൾ", "OPTICAL FIBRE", "bulb", "#2f7d4f")),
        ("ടവറുകൾ തമ്മിൽ മിക്കവാറും ഗ്ലാസ് നാരുകൾ കൊണ്ടുള്ള ഫൈബർ കേബിളുകളാണ് ബന്ധിപ്പിക്കുന്നത്.", "ഗ്ലാസ് നാരുകൾ", "GLASS THREADS JOIN THE TOWERS"),
        ("അതിലൂടെ വിവരങ്ങൾ പ്രകാശത്തിന്റെ മിന്നലുകളായി കടന്നുപോകും.", "പ്രകാശത്തിന്റെ മിന്നൽ", "DATA AS FLASHES OF LIGHT", S(["led", "bolt"], "dark")),
        ("കടലിനടിയിലൂടെയുള്ള കേബിളുകളാണ് രാജ്യങ്ങൾ തമ്മിലുള്ള ഇന്റർനെറ്റ് വിവരങ്ങൾ ഏറിയ പങ്കും കൊണ്ടുപോകുന്നത്.", "കടലിനടിയിലെ കേബിൾ", "UNDERSEA CABLES CARRY MOST OF IT", S(["boat"], "sky")),
        ("അങ്ങനെ ശബ്ദം അപ്പുറത്തെ ടവറിൽ എത്തും.", "അപ്പുറത്തെ ടവർ", "THE FAR TOWER", S(["pylon", "phone"], "dusk")),
        ("അവിടെ നിന്ന് വീണ്ടും റേഡിയോ തരംഗമായി മറ്റേ ഫോണിൽ എത്തും.", "വീണ്ടും തരംഗമായി", "BACK TO A RADIO WAVE"),
        ("മറ്റേ ഫോൺ കോഡ് വീണ്ടും ശബ്ദമാക്കി സ്പീക്കറിൽ കേൾപ്പിക്കും.", "4. സ്പീക്കർ", "STEP FOUR: THE SPEAKER"),
        ("ഇതെല്ലാം ഒരു സെക്കൻഡിന്റെ ചെറിയൊരു ഭാഗം കൊണ്ട് നടക്കും.", "നിമിഷത്തിൽ", "ALL IN A BLINK"),
        ("ബസിൽ യാത്ര ചെയ്യുമ്പോൾ ഫോൺ ഒരു ടവറിൽ നിന്ന് അടുത്ത ടവറിലേക്ക് തനിയെ മാറും, അതിനെ ഹാൻഡ്ഓവർ എന്ന് പറയും.", "ഹാൻഡ്ഓവർ", "HANDOVER WHILE YOU TRAVEL"),
        ("ലിഫ്റ്റിലും ബേസ്മെന്റിലും സിഗ്നൽ കിട്ടാത്തത് കോൺക്രീറ്റും ലോഹവും തരംഗങ്ങളെ തടയുന്നതുകൊണ്ടാണ്.", "ലിഫ്റ്റിൽ സിഗ്നൽ ഇല്ല", "METAL AND CONCRETE BLOCK WAVES", S(["house"], "storm")),
        ("ടവറിലെ റേഡിയോ തരംഗങ്ങൾ അയോണീകരണം ഉണ്ടാക്കാത്ത വിഭാഗത്തിൽപ്പെടുന്നു.", "അയോണീകരണമില്ലാത്ത തരംഗം", "NON-IONISING WAVES"),
        ("അനുവദനീയമായ പരിധിക്കുള്ളിൽ ആരോഗ്യത്തിന് ദോഷം തെളിഞ്ഞിട്ടില്ലെന്ന് ലോകാരോഗ്യ സംഘടന പറയുന്നു.", "പരിധിക്കുള്ളിൽ സുരക്ഷിതം", "WITHIN LIMITS, NO PROVEN HARM"),
        ("അടുത്ത തവണ ഹലോ പറയുമ്പോൾ ആ വലിയ യാത്ര ഓർക്കൂ.", "ഒരു ഹലോയുടെ യാത്ര", "THE JOURNEY OF ONE HELLO", TX("ഒരു ഹലോയുടെ യാത്ര", "THE JOURNEY OF A HELLO", "phone", "#c8442f")),
    ],
)
FACTS_CALL = ["A mobile network divides land into cells, each served by a base station; neighbouring cells use different frequencies and distant cells reuse them (Britannica: Cellular telephone).",
              "Radio waves travel at the speed of light, about 300,000 km/s (NASA).",
              "Submarine fibre-optic cables carry the large majority of international data (International Cable Protection Committee).",
              "Mobile phone base station radio waves are non-ionising; WHO reports no established adverse effects within international exposure limits (WHO: Electromagnetic fields and public health)."]

QR = sh(
    "qrcode_s", "QR കോഡ് കീറിയാലും സ്കാൻ ആകുന്നത് എങ്ങനെ?", "How does a QR code still scan when torn?", "QR കോഡിന്റെ രഹസ്യം", "THE QR CODE SECRET",
    [
        ("കടയിലെ QR കോഡ് കുറച്ച് കീറിപ്പോയാലും പണം അയക്കാൻ പറ്റുന്നത് എങ്ങനെയാണ്?", "കീറിയാലും സ്കാൻ", "SCANS EVEN WHEN TORN", S(["qr", "phone"], "dusk", label=("QR കോഡ്", "QR CODE"))),
        ("QR കോഡിൽ വിവരങ്ങൾ കറുപ്പും വെളുപ്പും ചതുരങ്ങളായി എഴുതിയിരിക്കുന്നു.", "ചതുരങ്ങളിൽ വിവരം", "DATA IN BLACK AND WHITE SQUARES"),
        ("മൂന്ന് മൂലയിലെ വലിയ ചതുരങ്ങൾ ഫോണിന് കോഡിന്റെ സ്ഥാനവും ദിശയും പറഞ്ഞുകൊടുക്കും.", "മൂന്ന് മൂല ചതുരം", "THREE CORNER MARKERS"),
        ("ഇതിൽ വിവരങ്ങളോടൊപ്പം അധിക വിവരങ്ങളും കൂടി ചേർത്താണ് എഴുതുന്നത്.", "അധിക വിവരങ്ങൾ", "EXTRA DATA IS ADDED"),
        ("ഈ പിശക് തിരുത്തൽ സംവിധാനം ഉപയോഗിച്ച് കോഡിന്റെ മുപ്പത് ശതമാനം വരെ കേടായാലും വായിക്കാം.", "30% വരെ കേടായാലും", "UP TO 30% DAMAGE IS OK", ST(30, "%", "കേടായാലും വായിക്കാവുന്നത്", "DAMAGE IT CAN SURVIVE", "qr")),
        ("ഇതിനെ റീഡ്-സോളമൻ പിശക് തിരുത്തൽ എന്ന് പറയും.", "റീഡ്-സോളമൻ", "REED-SOLOMON CORRECTION"),
    ],
    "കീറിയാലും മറക്കാത്ത കോഡ്!", "A CODE THAT SURVIVES", "ഒരു QR കോഡിൽ അതിന്റെ സ്വന്തം തിരുത്തൽ കൂടി ഒളിച്ചിരിക്കുന്നു!")

HEAT = sh(
    "phoneheat_s", "ഫോൺ ചൂടാകുന്നത് എന്തുകൊണ്ട്?", "Why does a phone get hot?", "ഫോൺ ചൂടാകുന്നത്", "WHY PHONES HEAT UP",
    [
        ("ചാർജ് ചെയ്യുമ്പോഴും ഗെയിം കളിക്കുമ്പോഴും ഫോൺ ചൂടാകുന്നത് എന്തുകൊണ്ടാണ്?", "ചൂടാകുന്ന ഫോൺ", "WHY IS IT HOT?", S(["phone", "thermo"], "dusk", label=("ചൂട്!", "HOT"))),
        ("വൈദ്യുതി ഒരു ചാലകത്തിലൂടെ പോകുമ്പോൾ അല്പം ഊർജം ചൂടായി മാറും.", "വൈദ്യുതി → ചൂട്", "CURRENT MAKES HEAT"),
        ("ഫോണിലെ പ്രോസസർ കൂടുതൽ ജോലി ചെയ്യുമ്പോൾ കൂടുതൽ വൈദ്യുതി ഉപയോഗിക്കും.", "പ്രോസസർ ജോലിയിൽ", "THE PROCESSOR WORKS HARD"),
        ("ചാർജ് ചെയ്യുമ്പോൾ ബാറ്ററിക്കുള്ളിലെ രാസപ്രവർത്തനവും ചൂട് ഉണ്ടാക്കും.", "ബാറ്ററിയും ചൂടാകും", "THE BATTERY WARMS TOO", S(["battery"], "dusk")),
        ("ഫോണിന്റെ ഉള്ളിൽ ഇത്രയും ചെറിയ സ്ഥലത്ത് ചൂട് പുറത്തുപോകാൻ വഴി കുറവാണ്.", "ചൂടിന് വഴിയില്ല", "LITTLE ROOM FOR THE HEAT TO ESCAPE"),
        ("അതുകൊണ്ട് വെയിലത്തോ തലയണയ്ക്കടിയിലോ വെച്ച് ചാർജ് ചെയ്യരുത്.", "വെയിലത്ത് വയ്ക്കരുത്", "NEVER CHARGE IN SUN OR UNDER A PILLOW"),
    ],
    "ഫോണിന്റെ വിയർപ്പ് ചൂടാണ്!", "THE PHONE'S SWEAT", "ഫോൺ വിയർക്കില്ല, അതുകൊണ്ട് അത് ചൂടാകുന്നു!")

INDUCTION = sh(
    "induction_s", "ഇൻഡക്ഷൻ കുക്കർ ചൂടാകാതെ പാത്രം ചൂടാക്കുന്നത് എങ്ങനെ?", "How does an induction cooker heat the pan and not the glass?", "ഇൻഡക്ഷൻ കുക്കർ", "INDUCTION COOKER",
    [
        ("ഇൻഡക്ഷൻ കുക്കറിന്റെ പ്ലേറ്റ് ചൂടാകാതെ പാത്രം മാത്രം ചൂടാകുന്നത് എങ്ങനെയാണ്?", "പാത്രം മാത്രം ചൂടാകുന്നു", "ONLY THE PAN HEATS", S(["cooker", "magnet"], "dusk", label=("ഇൻഡക്ഷൻ", "INDUCTION"))),
        ("പ്ലേറ്റിനടിയിൽ ഒരു കമ്പിച്ചുരുളിലൂടെ മാറിമാറി ഒഴുകുന്ന വൈദ്യുതി ഉണ്ട്.", "കമ്പിച്ചുരുൾ", "A COIL WITH ALTERNATING CURRENT"),
        ("അത് വേഗത്തിൽ മാറുന്ന ഒരു കാന്തിക മണ്ഡലം ഉണ്ടാക്കും.", "മാറുന്ന കാന്തിക മണ്ഡലം", "A CHANGING MAGNETIC FIELD", S(["magnet"], "dark")),
        ("ഇരുമ്പ് പാത്രത്തിൽ ആ കാന്തിക മണ്ഡലം ചെറിയ ചുഴിവൈദ്യുതി ഉണ്ടാക്കും.", "ചുഴിവൈദ്യുതി", "EDDY CURRENTS IN THE PAN"),
        ("ആ വൈദ്യുതി പാത്രത്തിൽ തന്നെ ചൂട് ഉണ്ടാക്കും, അതുകൊണ്ട് പ്ലേറ്റ് ചൂടാകില്ല.", "പാത്രത്തിൽ തന്നെ ചൂട്", "THE HEAT IS MADE INSIDE THE PAN"),
        ("അലൂമിനിയം, ഗ്ലാസ് പാത്രങ്ങൾ പലതും ഇതിൽ പ്രവർത്തിക്കില്ല, കാന്തം പിടിക്കുന്ന പാത്രം വേണം.", "കാന്തം പിടിക്കണം", "THE PAN MUST BE MAGNETIC"),
    ],
    "ചൂട് പാത്രത്തിനുള്ളിൽ തന്നെ!", "HEAT BORN INSIDE THE PAN", "ഇൻഡക്ഷൻ കുക്കറിൽ തീയില്ല, കാന്തമാണ് പാചകം ചെയ്യുന്നത്!")

GPS = sh(
    "gps_s", "ഗൂഗിൾ മാപ്പിന് നമ്മൾ എവിടെയെന്ന് അറിയുന്നത് എങ്ങനെ?", "How does your phone know where you are?", "ഫോൺ എങ്ങനെ അറിയുന്നു?", "HOW GPS WORKS",
    [
        ("ഇന്റർനെറ്റ് ഇല്ലാത്തപ്പോൾ പോലും ഫോണിന് നമ്മൾ എവിടെയാണെന്ന് അറിയുന്നത് എങ്ങനെയാണ്?", "ഞാൻ എവിടെ?", "HOW DOES IT KNOW?", S(["satellite", "phone"], "night", label=("GPS", "GPS"))),
        ("ഭൂമിയെ ചുറ്റുന്ന ഇരുപത്തിനാലിലധികം ഉപഗ്രഹങ്ങൾ തുടർച്ചയായി സമയ സിഗ്നലുകൾ അയക്കുന്നു.", "ഉപഗ്രഹങ്ങളുടെ സിഗ്നൽ", "SATELLITES BROADCAST THE TIME"),
        ("ഓരോ ഉപഗ്രഹത്തിലും വളരെ കൃത്യമായ ആറ്റോമിക് ക്ലോക്ക് ഉണ്ട്.", "ആറ്റോമിക് ക്ലോക്ക്", "ATOMIC CLOCKS ON BOARD"),
        ("സിഗ്നൽ എത്താൻ എടുത്ത സമയത്തെ പ്രകാശവേഗം കൊണ്ട് ഗുണിച്ച് ഫോൺ ഉപഗ്രഹത്തിലേക്കുള്ള ദൂരം കണ്ടെത്തും.", "സമയം → ദൂരം", "TIME TIMES SPEED IS DISTANCE"),
        ("കുറഞ്ഞത് നാല് ഉപഗ്രഹങ്ങളിൽ നിന്നുള്ള ദൂരം അറിഞ്ഞാൽ ഭൂമിയിലെ സ്ഥാനം ഉറപ്പിക്കാം.", "4 ഉപഗ്രഹങ്ങൾ വേണം", "FOUR SATELLITES FIX THE SPOT", ST(4, " ഉപഗ്രഹങ്ങൾ", "സ്ഥാനം അറിയാൻ വേണ്ടത്", "AT LEAST THIS MANY", "satellite")),
        ("ആപേക്ഷികതാ സിദ്ധാന്തം അനുസരിച്ചുള്ള ചെറിയ സമയ വ്യത്യാസം കൂടി തിരുത്തിയില്ലെങ്കിൽ ദിവസവും കിലോമീറ്ററുകൾ പിശകും.", "ഐൻസ്റ്റീന്റെ തിരുത്തൽ", "EINSTEIN'S CORRECTION"),
    ],
    "ആകാശത്തെ ക്ലോക്കുകളുടെ കണക്ക്!", "MATHS OF SKY CLOCKS", "നമ്മുടെ വഴി കാണിക്കുന്നത് ആകാശത്തെ ക്ലോക്കുകളാണ്!")

TOUCH = sh(
    "touchscreen_s", "ഗ്ലൗസ് ഇട്ടാൽ ടച്ച് സ്ക്രീൻ പ്രവർത്തിക്കാത്തത് എന്തുകൊണ്ട്?", "Why does a touchscreen not work with gloves?", "ടച്ച് സ്ക്രീൻ രഹസ്യം", "TOUCHSCREEN SECRET",
    [
        ("കൈയുറയിട്ട് ഫോൺ തൊട്ടാൽ പ്രവർത്തിക്കാത്തത് എന്തുകൊണ്ടാണ്?", "ഗ്ലൗസ് ഇട്ടാൽ?", "WHY NOT WITH GLOVES?", S(["phone", "person"], "dusk", label=("ടച്ച്", "TOUCH"))),
        ("ഫോൺ സ്ക്രീനിൽ വളരെ ചെറിയ ഒരു വൈദ്യുത മണ്ഡലം എപ്പോഴും ഉണ്ട്.", "സ്ക്രീനിൽ വൈദ്യുത മണ്ഡലം", "A TINY ELECTRIC FIELD"),
        ("നമ്മുടെ വിരൽ വൈദ്യുതി കടത്തിവിടുന്ന വസ്തുവാണ്.", "വിരൽ ഒരു ചാലകം", "FINGERS CONDUCT"),
        ("വിരൽ തൊടുമ്പോൾ ആ വൈദ്യുത മണ്ഡലത്തിന് ചെറിയ മാറ്റം വരും.", "മണ്ഡലത്തിന് മാറ്റം", "THE FIELD CHANGES"),
        ("ഫോൺ ആ മാറ്റം തിരിച്ചറിഞ്ഞ് സ്ഥാനം കണക്കാക്കും.", "സ്ഥാനം തിരിച്ചറിയുന്നു", "THE PHONE FINDS THE SPOT"),
        ("സാധാരണ കൈയുറ വൈദ്യുതി കടത്തിവിടാത്തതുകൊണ്ട് ആ മാറ്റം ഉണ്ടാകില്ല.", "കൈയുറ കടത്തില്ല", "A NORMAL GLOVE DOES NOT CONDUCT"),
    ],
    "വിരലിന്റെ വൈദ്യുതി!", "THE ELECTRICITY OF A FINGER", "നമ്മുടെ വിരലിലെ വൈദ്യുതിയാണ് ഫോണിനെ ഉണർത്തുന്നത്!")

MICROWAVE = sh(
    "microwave_s", "മൈക്രോവേവ് ഓവൻ ഭക്ഷണം ചൂടാക്കുന്നത് എങ്ങനെ?", "How does a microwave oven heat food?", "മൈക്രോവേവിന്റെ രഹസ്യം", "MICROWAVE OVEN",
    [
        ("തീയില്ലാതെ മൈക്രോവേവ് ഓവൻ ഭക്ഷണം ചൂടാക്കുന്നത് എങ്ങനെയാണ്?", "തീയില്ലാത്ത ചൂട്", "HEAT WITHOUT FLAME", S(["microwave"], "dusk", label=("മൈക്രോവേവ്", "MICROWAVE"))),
        ("അത് ഏകദേശം രണ്ടര ഗിഗാഹെർട്സ് ആവൃത്തിയുള്ള മൈക്രോവേവ് തരംഗങ്ങൾ ഉണ്ടാക്കുന്നു.", "മൈക്രോവേവ് തരംഗം", "MICROWAVES OF ABOUT 2.45 GHZ"),
        ("ഭക്ഷണത്തിലെ ജല തന്മാത്രകൾ ആ തരംഗത്തിനൊത്ത് ഒരു സെക്കൻഡിൽ കോടിക്കണക്കിന് തവണ തിരിയും.", "ജല തന്മാത്രകൾ തിരിയുന്നു", "WATER MOLECULES TWIST"),
        ("ആ തിരിയലിലെ ഉരസൽ ചൂടാകുന്നു.", "ഉരസൽ = ചൂട്", "FRICTION MAKES HEAT"),
        ("ഉണങ്ങിയ ഭക്ഷണത്തിൽ വെള്ളം കുറവായതുകൊണ്ട് ചൂട് കുറവായിരിക്കും.", "വെള്ളം കുറഞ്ഞാൽ ചൂട് കുറയും", "LESS WATER, LESS HEAT"),
        ("ലോഹ പാത്രം ഉള്ളിൽ വയ്ക്കരുത്, അത് തരംഗങ്ങളെ പ്രതിഫലിപ്പിച്ച് തീപ്പൊരി ഉണ്ടാക്കും.", "ലോഹം വയ്ക്കരുത്", "NEVER PUT METAL INSIDE"),
    ],
    "വെള്ളത്തിന്റെ നൃത്തം!", "THE DANCE OF WATER", "മൈക്രോവേവിൽ ഭക്ഷണം ചൂടാകുന്നത് ജലത്തിന്റെ നൃത്തം കൊണ്ടാണ്!")

FACTS = [
    "QR codes use Reed-Solomon error correction; level H can restore about 30 percent of damaged data (Denso Wave; ISO/IEC 18004).",
    "A phone warms because processor and charging currents turn some electrical energy into heat (general electronics; Apple and Samsung care guidance).",
    "An induction cooker's alternating-current coil creates a changing magnetic field that induces eddy currents and heating in magnetic cookware (Wikipedia: Induction cooking).",
    "GPS needs signals from at least four satellites carrying atomic clocks and corrects for relativistic time differences (GPS.gov; Ashby 2003, Living Reviews in Relativity).",
    "Capacitive touchscreens sense the change in an electric field caused by a conductive fingertip (Wikipedia: Touchscreen).",
    "A microwave oven uses microwaves of about 2.45 GHz that rotate polar water molecules and heat the food (Britannica: Microwave oven).",
] + FACTS_CALL
# richer scene: a call across the cells
rich(CALL, 8, 21, "cells", {"wave": 0, "tower": 0, "cells": 1, "freq": 3, "reuse": 4, "fibre": 5, "call": 7, "bus": 13},
     [(0, -100, 375, 1.8), (1, 700, 450, 0.95), (3, 700, 520, 1.0), (4, 700, 300, 1.0), (5, 900, 375, 1.5), (7, 200, 375, 1.6), (8, 900, 375, 1.4), (9, 1700, 375, 1.6), (12, 400, 540, 1.3), (13, 1000, 540, 1.2)])

VIDEOS = [CALL, QR, HEAT, INDUCTION, GPS, TOUCH, MICROWAVE]
