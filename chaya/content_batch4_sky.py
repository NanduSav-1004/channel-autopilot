"""Science Chaya batch 4: sky and space (Chandrayaan-3 long; blue sky, twinkling, moon illusion, the 2019 ring eclipse over Kerala, the space station, the moon's one face)."""
from chaya.quick import ST, TX, S, lab, lg, rich, sh

MOON = lg(
    "chandrayaan_long", "ചന്ദ്രയാൻ മൂന്ന് ചന്ദ്രനിൽ ഇറങ്ങിയത് എങ്ങനെ? | ഒരു സോഫ്റ്റ് ലാൻഡിങ്ങിന്റെ ശാസ്ത്രം", "How did Chandrayaan-3 land on the Moon? The science of a soft landing",
    "ചന്ദ്രനിൽ ഇറങ്ങിയത് എങ്ങനെ?", "CHANDRAYAAN-3 LANDING", "ചന്ദ്രയാൻ മൂന്ന് ഇറങ്ങിയ ദിവസം നിങ്ങൾ എവിടെ ആയിരുന്നു?", "WHERE WERE YOU WHEN IT LANDED?",
    [
        ("രണ്ടായിരത്തി ഇരുപത്തിമൂന്ന് ഓഗസ്റ്റ് ഇരുപത്തിമൂന്നിന് വൈകുന്നേരം ഇന്ത്യ മുഴുവൻ ഒരു കാര്യം ശ്വാസമടക്കി കണ്ടു.", "ഓഗസ്റ്റ് 23, 2023", "A NATION HOLDS ITS BREATH", S(["moon", "rocket"], "night", label=("ചന്ദ്രയാൻ 3", "CHANDRAYAAN-3"))),
        ("ഒരു ഇന്ത്യൻ പേടകം ചന്ദ്രനിൽ മൃദുവായി ഇറങ്ങുന്നത്.", "ചന്ദ്രനിൽ മൃദു ലാൻഡിങ്", "A SOFT LANDING ON THE MOON"),
        ("ഇന്ന് നമുക്ക് ആ യാത്ര തുടക്കം മുതൽ നോക്കാം.", "യാത്ര തുടക്കം മുതൽ", "THE JOURNEY FROM THE START", TX("തുടക്കം മുതൽ", "FROM THE START", "rocket", "#4a2a17")),
        ("ജൂലൈ പതിന്നാലിന് ശ്രീഹരിക്കോട്ടയിൽ നിന്ന് എൽവിഎം മൂന്ന് റോക്കറ്റിലാണ് ചന്ദ്രയാൻ മൂന്ന് പുറപ്പെട്ടത്.", "LVM3 റോക്കറ്റ്", "LAUNCHED ON AN LVM3 ROCKET", S(["rocket"], "dusk", ("bubbles", 20, "#fff"), anim="shake")),
        ("തിരുവനന്തപുരത്തെ വിക്രം സാരാഭായ് സ്പേസ് സെന്റർ പോലുള്ള കേന്ദ്രങ്ങളിലാണ് ഇത്തരം റോക്കറ്റുകൾ രൂപകൽപ്പന ചെയ്യുന്നത്.", "തിരുവനന്തപുരത്തെ VSSC", "DESIGNED AT VSSC, THIRUVANANTHAPURAM"),
        ("റോക്കറ്റ് നേരെ ചന്ദ്രനിലേക്കല്ല പോയത്, ആദ്യം ഭൂമിയെ ചുറ്റുന്ന ഭ്രമണപഥത്തിൽ കയറി.", "ആദ്യം ഭൂമിയെ ചുറ്റി", "FIRST, AN ORBIT AROUND EARTH", S(["rocket", "moon"], "night")),
        ("പിന്നെ എൻജിൻ കത്തിച്ച് പടിപടിയായി ഭ്രമണപഥം വലുതാക്കി.", "ഭ്രമണപഥം വലുതാക്കുന്നു", "THE ORBIT GROWS STEP BY STEP"),
        ("ഒടുവിൽ ചന്ദ്രന്റെ ഗുരുത്വാകർഷണം അതിനെ പിടിച്ചെടുത്തു.", "ചന്ദ്രൻ പിടിച്ചെടുക്കുന്നു", "THE MOON'S GRAVITY CATCHES IT"),
        ("ഏകദേശം നാല്പത് ദിവസത്തെ യാത്രയ്ക്ക് ശേഷം അത് ചന്ദ്രന്റെ അടുത്തെത്തി.", "40 ദിവസത്തെ യാത്ര", "ABOUT 40 DAYS OF TRAVEL", ST(40, " ദിവസം", "ഭൂമിയിൽ നിന്ന് ചന്ദ്രനിലേക്ക്", "FROM EARTH TO A LANDING", "moon")),
        ("ഇറങ്ങേണ്ട പേടകത്തിന്റെ പേര് വിക്രം ലാൻഡർ.", "വിക്രം ലാൻഡർ", "THE VIKRAM LANDER", S(["moon"], "night", label=("വിക്രം", "VIKRAM"))),
        ("അതിനുള്ളിൽ പ്രഗ്യാൻ എന്ന റോവർ ഉണ്ടായിരുന്നു.", "പ്രഗ്യാൻ റോവർ", "PRAGYAAN, THE ROVER"),
        ("ഇറങ്ങുക എന്നത് ഏറ്റവും കഠിനമായ ഭാഗമാണ്.", "ഏറ്റവും കഠിനം: ഇറങ്ങൽ", "LANDING IS THE HARD PART", TX("ഏറ്റവും കഠിനം", "THE HARDEST PART", "moon", "#c8442f")),
        ("ചന്ദ്രനിൽ വായു ഇല്ലാത്തതുകൊണ്ട് പാരച്യൂട്ട് ഉപയോഗിക്കാൻ പറ്റില്ല.", "പാരച്യൂട്ട് പറ്റില്ല", "NO AIR, SO NO PARACHUTE"),
        ("പേടകം ഏകദേശം സെക്കൻഡിൽ ഒന്നര കിലോമീറ്റർ വേഗത്തിലാണ് ചന്ദ്രനെ ചുറ്റിയിരുന്നത്.", "സെക്കൻഡിൽ ഒന്നര കി.മീ", "ABOUT 1.5 KM EVERY SECOND", ST(1500, " m/s", "ഇറങ്ങും മുൻപുള്ള വേഗം", "THE ORBITAL SPEED BEFORE DESCENT", "rocket")),
        ("ആ വേഗം എൻജിൻ ഉപയോഗിച്ച് തന്നെ പൂജ്യത്തിലേക്ക് കുറയ്ക്കണം.", "എൻജിൻ കൊണ്ട് ബ്രേക്ക്", "BRAKING WITH ENGINES ONLY"),
        ("ഇറങ്ങാൻ ഉള്ള സ്ഥലം തിരഞ്ഞെടുക്കാൻ കാമറകളും സെൻസറുകളും സഹായിച്ചു.", "ഇറങ്ങേണ്ട സ്ഥലം തിരയുന്നു", "CAMERAS PICK THE SPOT"),
        ("വലിയ കല്ലുകളും കുഴികളും ഒഴിവാക്കി പേടകം സ്വയം ഗതി മാറ്റി.", "കല്ലുകൾ ഒഴിവാക്കി", "DODGING ROCKS AND CRATERS", S(["moon", "rocket"], "dark")),
        ("വൈകുന്നേരം ആറ് മണി കഴിഞ്ഞ് നാല് മിനിറ്റിൽ വിക്രം ചന്ദ്രനിൽ തൊട്ടു.", "വൈകിട്ട് 6:04", "TOUCHDOWN AT ABOUT 6:04 PM"),
        ("ഇതോടെ ചന്ദ്രന്റെ ദക്ഷിണധ്രുവത്തിനടുത്ത് ഇറങ്ങുന്ന ആദ്യ രാജ്യമായി ഇന്ത്യ.", "ദക്ഷിണധ്രുവത്തിനടുത്ത്", "FIRST NEAR THE SOUTH POLE"),
        ("ചന്ദ്രനിൽ സോഫ്റ്റ് ലാൻഡിങ് നടത്തിയ നാലാമത്തെ രാജ്യവും ഇന്ത്യയാണ്.", "നാലാമത്തെ രാജ്യം", "THE FOURTH COUNTRY TO LAND", TX("4-ാമത്തെ രാജ്യം", "THE FOURTH COUNTRY", "moon", "#2f7d4f")),
        ("പ്രഗ്യാൻ റോവർ പുറത്തിറങ്ങി ചന്ദ്രന്റെ പ്രതലത്തിലൂടെ ഉരുണ്ടു.", "പ്രഗ്യാൻ ഉരുളുന്നു", "THE ROVER ROLLS OUT"),
        ("അത് മണ്ണിൽ സൾഫർ ഉണ്ടെന്ന് കണ്ടെത്തി.", "സൾഫർ കണ്ടെത്തി", "IT FOUND SULPHUR"),
        ("വിക്രം ഒരു ചെറിയ ഹോപ്പും നടത്തി, ഏകദേശം നാല്പത് സെന്റീമീറ്റർ ഉയർന്ന് വീണ്ടും ഇറങ്ങി.", "ഒരു ചെറിയ ചാട്ടം", "A SMALL HOP OF ABOUT 40 CM"),
        ("ധ്രുവത്തിലെ എപ്പോഴും നിഴൽ വീഴുന്ന കുഴികളിൽ ഐസ് ഉണ്ടാകാമെന്ന് ശാസ്ത്രജ്ഞർ കരുതുന്നു.", "നിഴലിൽ ഐസ്?", "ICE IN PERMANENT SHADOW?"),
        ("ഭാവിയിലെ യാത്രകൾക്ക് വെള്ളവും ഇന്ധനവും അവിടെ നിന്ന് കിട്ടിയാൽ വലിയ നേട്ടമാകും.", "ഭാവിയിലെ വെള്ളം", "WATER FOR FUTURE TRIPS"),
        ("തിരുവനന്തപുരത്തെ പരീക്ഷണശാലകളിൽ ഇരുന്ന് കണ്ട ഒരു സ്വപ്നമാണ് ചന്ദ്രനിൽ ഇറങ്ങിയത്.", "സ്വപ്നം ചന്ദ്രനിൽ", "A DREAM THAT LANDED", S(["moon", "rocket"], "night")),
    ],
)
FACTS_MOON = ["Chandrayaan-3 launched on 14 July 2023 on an LVM3 rocket from Sriharikota and the Vikram lander touched down near the lunar south pole on 23 August 2023, making India the fourth country to soft-land on the Moon (ISRO mission pages).",
              "The Pragyan rover's laser-induced breakdown spectroscope detected sulphur in the lunar soil near the south pole (ISRO, 29 August 2023).",
              "The Vikram lander performed a hop experiment of about 40 cm (ISRO, 4 September 2023).",
              "Launch vehicles are developed at the Vikram Sarabhai Space Centre, Thiruvananthapuram (ISRO)."]

BLUE = sh(
    "bluesky_s", "ആകാശം നീലയും സൂര്യാസ്തമയം ചുവപ്പും ആകുന്നത് എന്തുകൊണ്ട്?", "Why is the sky blue and the sunset red?", "ആകാശം നീല എന്തിന്?", "BLUE SKY",
    [
        ("ആകാശത്തിന് നിറം നീലയും അസ്തമയത്തിന് ചുവപ്പും ആകുന്നത് എന്തുകൊണ്ടാണ്?", "നീലയും ചുവപ്പും", "BLUE BY DAY, RED AT DUSK", S(["sun", "cloud"], "sky")),
        ("സൂര്യപ്രകാശം വെളുത്തതാണെങ്കിലും അതിൽ എല്ലാ നിറങ്ങളും ഉണ്ട്.", "വെളുപ്പിൽ എല്ലാ നിറവും", "WHITE LIGHT HAS ALL COLOURS"),
        ("വായുവിലെ കണികകൾ നീല വെളിച്ചത്തെ ചുവപ്പിനേക്കാൾ കൂടുതൽ എല്ലായിടത്തേക്കും ചിതറിക്കും.", "നീല ചിതറുന്നു", "AIR SCATTERS BLUE MOST"),
        ("അതുകൊണ്ട് ആകാശത്തെവിടെ നോക്കിയാലും നീല നിറം കാണാം.", "എവിടെയും നീല", "BLUE FROM EVERY DIRECTION"),
        ("സന്ധ്യയ്ക്ക് സൂര്യന്റെ വെളിച്ചം കൂടുതൽ ദൂരം വായുവിലൂടെ കടന്നാണ് വരുന്നത്.", "ദൂരം കൂടുതൽ", "A LONGER PATH THROUGH AIR", S(["sun"], "dusk")),
        ("ആ യാത്രയിൽ നീല ചിതറി നഷ്ടപ്പെടും, ചുവപ്പും ഓറഞ്ചും മാത്രം നമ്മുടെ കണ്ണിലെത്തും.", "ചുവപ്പ് മാത്രം ബാക്കി", "ONLY RED AND ORANGE ARRIVE"),
    ],
    "ആകാശത്തിന്റെ നിറം ഒരു തന്ത്രം!", "A TRICK OF LIGHT", "ആകാശത്തിന് സ്വന്തമായി നിറമില്ല, ചിതറുന്ന വെളിച്ചമാണ് നമ്മൾ കാണുന്നത്!")

TWINKLE = sh(
    "twinkle_s", "നക്ഷത്രങ്ങൾ മിന്നുന്നു, ഗ്രഹങ്ങൾ മിന്നുന്നില്ല: എന്തുകൊണ്ട്?", "Why do stars twinkle but planets do not?", "നക്ഷത്രം മിന്നുന്നത്", "TWINKLE TWINKLE",
    [
        ("രാത്രി ആകാശത്ത് നക്ഷത്രങ്ങൾ മിന്നുന്നു, പക്ഷേ ഗ്രഹങ്ങൾ ഏതാണ്ട് സ്ഥിരമായി തിളങ്ങുന്നു.", "മിന്നുന്നതും തിളങ്ങുന്നതും", "TWINKLE VS STEADY", S(["moon"], "night", ("fireflies", 30, "#ffe9a8"))),
        ("നക്ഷത്രത്തിന്റെ വെളിച്ചം നമ്മുടെ അന്തരീക്ഷത്തിലൂടെ കടന്നാണ് വരുന്നത്.", "അന്തരീക്ഷത്തിലൂടെ", "THROUGH OUR AIR"),
        ("അന്തരീക്ഷത്തിലെ ചൂടും തണുപ്പുമുള്ള വായു പാളികൾ ഇളകിക്കൊണ്ടിരിക്കും.", "ഇളകുന്ന വായു", "THE AIR KEEPS SHIFTING"),
        ("അത് വെളിച്ചത്തിന്റെ വഴി ഓരോ നിമിഷവും ചെറുതായി വളയ്ക്കും.", "വഴി വളയുന്നു", "IT BENDS THE LIGHT"),
        ("നക്ഷത്രങ്ങൾ വളരെ ദൂരെയായതുകൊണ്ട് ഒരു ചെറിയ പൊട്ട് പോലെയാണ്, അതിനാൽ ആ വളവ് മിന്നലായി കാണും.", "പൊട്ട് പോലെ ചെറുത്", "A TINY POINT OF LIGHT"),
        ("ഗ്രഹങ്ങൾ അടുത്തായതുകൊണ്ട് ചെറിയ വൃത്തം പോലെയാണ്, അതിൽ പല ഭാഗങ്ങളിലെ മിന്നൽ ഒന്നിച്ച് ശരാശരിയാകും.", "ചെറിയ വൃത്തം", "A SMALL DISC AVERAGES OUT"),
    ],
    "മിന്നുന്നത് വായുവിന്റെ ഇളക്കം!", "IT IS THE AIR THAT TWINKLES", "നക്ഷത്രത്തിന്റെ മിന്നൽ വാസ്തവത്തിൽ നമ്മുടെ വായുവിന്റെ ഇളക്കമാണ്!")

ILLUSION = sh(
    "moonillusion_s", "ഉദിക്കുമ്പോൾ ചന്ദ്രൻ വലുതായി തോന്നുന്നത് എന്തുകൊണ്ട്?", "Why does the Moon look huge when it rises?", "വലിയ ചന്ദ്രൻ?", "THE MOON ILLUSION",
    [
        ("ചക്രവാളത്തിൽ ഉദിച്ചുവരുന്ന ചന്ദ്രൻ നല്ല വലുതായി തോന്നിയിട്ടില്ലേ?", "വലിയ ചന്ദ്രൻ", "THE BIG RISING MOON", S(["moon", "tree"], "dusk")),
        ("എന്നാൽ ചന്ദ്രന്റെ വലുപ്പം ഒട്ടും കൂടുന്നില്ല.", "വലുപ്പം കൂടുന്നില്ല", "IT DOES NOT GROW"),
        ("കാമറയിൽ എടുത്ത് അളന്നാൽ ഉദിക്കുമ്പോഴും തലയ്ക്ക് മുകളിലും ഒരേ വലുപ്പമാണ്.", "അളന്നാൽ ഒരേ വലുപ്പം", "A PHOTO SHOWS THE SAME SIZE"),
        ("ഇത് നമ്മുടെ തലച്ചോറിന്റെ ഒരു തോന്നലാണ്, അതിനെ മൂൺ ഇല്യൂഷൻ എന്ന് പറയും.", "മൂൺ ഇല്യൂഷൻ", "THE MOON ILLUSION"),
        ("ചക്രവാളത്തിൽ മരങ്ങളും വീടുകളും താരതമ്യത്തിന് ഉള്ളതുകൊണ്ട് ചന്ദ്രൻ വലുതായി തോന്നുന്നു.", "താരതമ്യം ചതിക്കുന്നു", "THE TREES FOOL OUR SENSE OF SCALE"),
        ("ഒരു ചെറിയ കുഴലിലൂടെ നോക്കിയാൽ ആ തോന്നൽ മാഞ്ഞുപോകും.", "കുഴലിലൂടെ നോക്കൂ", "LOOK THROUGH A TUBE"),
    ],
    "കണ്ണല്ല, തലച്ചോറാണ് പറ്റിക്കുന്നത്!", "YOUR BRAIN IS PLAYING TRICKS", "ചന്ദ്രനെ വലുതാക്കുന്നത് ആകാശമല്ല, നമ്മുടെ തലച്ചോറാണ്!")

ECLIPSE = sh(
    "ringeclipse_s", "കേരളത്തിൽ കണ്ട ആ വലയ സൂര്യഗ്രഹണം എങ്ങനെ?", "How did Kerala see a ring of fire in 2019?", "തീവള ഗ്രഹണം!", "RING OF FIRE",
    [
        ("രണ്ടായിരത്തി പത്തൊൻപത് ഡിസംബർ ഇരുപത്താറിന് കേരളത്തിൽ ആകാശത്ത് ഒരു തീവള കണ്ടു.", "കേരളത്തിലെ തീവള", "A RING OF FIRE OVER KERALA", S(["sun", "moon"], "sky")),
        ("അത് വലയ സൂര്യഗ്രഹണം ആയിരുന്നു.", "വലയ സൂര്യഗ്രഹണം", "AN ANNULAR ECLIPSE"),
        ("ചന്ദ്രൻ സൂര്യന്റെ മുന്നിലൂടെ കടന്നുപോകുമ്പോഴാണ് സൂര്യഗ്രഹണം ഉണ്ടാകുന്നത്.", "ചന്ദ്രൻ സൂര്യനു മുന്നിൽ", "THE MOON PASSES IN FRONT"),
        ("ചന്ദ്രൻ ഭൂമിയുടെ വളരെ അടുത്താണെങ്കിൽ സൂര്യനെ പൂർണ്ണമായി മൂടും.", "അടുത്താൽ പൂർണ്ണം", "CLOSE: TOTAL ECLIPSE"),
        ("ആ ദിവസം ചന്ദ്രൻ ഭൂമിയിൽ നിന്ന് കുറച്ച് അകലെയായിരുന്നു, അതുകൊണ്ട് ചെറുതായി കാണപ്പെട്ടു.", "അകലെ, ചെറുത്", "FARTHER AWAY, SO SMALLER"),
        ("സൂര്യന്റെ നടുഭാഗം മൂടി, ചുറ്റും തിളങ്ങുന്ന ഒരു വളയം ബാക്കിയായി.", "തിളങ്ങുന്ന വളയം", "A BRIGHT RING LEFT OVER"),
        ("ഗ്രഹണം നേരിട്ട് കണ്ണുകൊണ്ട് നോക്കരുത്, അംഗീകൃത ഗ്രഹണക്കണ്ണട വേണം.", "കണ്ണട വേണം", "USE ECLIPSE GLASSES"),
    ],
    "ആകാശത്തെ ഒരു വലയം!", "A RING IN THE SKY", "ചന്ദ്രന്റെ അകലമാണ് ആ വലയത്തിന്റെ രഹസ്യം!")

ISS = sh(
    "iss_s", "ബഹിരാകാശ നിലയം രാത്രി ആകാശത്ത് കാണുന്നത് എങ്ങനെ?", "How can you see the space station from Kerala?", "ആകാശത്തെ നിലയം!", "SEE THE SPACE STATION",
    [
        ("രാത്രി ആകാശത്ത് ഒരു തിളങ്ങുന്ന പൊട്ട് വേഗത്തിൽ നീങ്ങുന്നത് ശ്രദ്ധിച്ചിട്ടുണ്ടോ?", "നീങ്ങുന്ന പൊട്ട്", "A BRIGHT MOVING DOT", S(["rocket"], "night", ("fireflies", 18, "#fff"))),
        ("അത് ചിലപ്പോൾ അന്താരാഷ്ട്ര ബഹിരാകാശ നിലയം ആകാം.", "ബഹിരാകാശ നിലയം", "THE SPACE STATION"),
        ("അത് ഭൂമിയിൽ നിന്ന് ഏകദേശം നാനൂറ് കിലോമീറ്റർ ഉയരത്തിലാണ് സഞ്ചരിക്കുന്നത്.", "400 km ഉയരം", "ABOUT 400 KM UP", ST(400, " km", "ഭൂമിയിൽ നിന്നുള്ള ഉയരം", "THE STATION'S HEIGHT", "rocket")),
        ("മണിക്കൂറിൽ ഇരുപത്തെണ്ണായിരം കിലോമീറ്ററിലധികം വേഗത്തിൽ അത് ഭൂമിയെ ചുറ്റുന്നു.", "മണിക്കൂറിൽ 28,000 km", "OVER 28,000 KM/H"),
        ("ഏകദേശം തൊണ്ണൂറ് മിനിറ്റിൽ ഒരു തവണ ഭൂമിയെ വലം വയ്ക്കും.", "90 മിനിറ്റിൽ ഒരു ചുറ്റ്", "ONE LAP IN ABOUT 90 MINUTES"),
        ("അതിന് സ്വന്തമായി വെളിച്ചമില്ല, സൂര്യപ്രകാശം പ്രതിഫലിപ്പിച്ചാണ് തിളങ്ങുന്നത്.", "പ്രതിഫലിക്കുന്ന വെളിച്ചം", "IT REFLECTS SUNLIGHT"),
        ("സമയം അറിയാൻ നാസയുടെ സ്പോട്ട് ദ സ്റ്റേഷൻ പോലുള്ള വെബ്സൈറ്റുകൾ നോക്കാം.", "സമയം നോക്കാം", "CHECK THE PASS TIMES"),
    ],
    "തലയ്ക്ക് മുകളിൽ ഒരു വീട്!", "A HOME ABOVE YOUR HEAD", "ഇന്ന് രാത്രി തലയ്ക്ക് മുകളിലൂടെ ഒരു ബഹിരാകാശ വീട് കടന്നുപോകും!")

MOONFACE = sh(
    "moonface_s", "ചന്ദ്രന്റെ ഒരു വശം മാത്രം കാണുന്നത് എന്തുകൊണ്ട്?", "Why do we only ever see one side of the Moon?", "ചന്ദ്രന്റെ ഒരേ മുഖം", "THE MOON'S ONE FACE",
    [
        ("നമ്മൾ എപ്പോഴും ചന്ദ്രന്റെ ഒരേ മുഖം മാത്രം കാണുന്നത് എന്തുകൊണ്ടാണ്?", "ഒരേ മുഖം", "ALWAYS THE SAME FACE", S(["moon"], "night", label=("ചന്ദ്രൻ", "THE MOON"))),
        ("ചന്ദ്രൻ ഭൂമിയെ ഒരു തവണ ചുറ്റാൻ ഏകദേശം ഇരുപത്തിയേഴ് ദിവസം എടുക്കും.", "ഒരു ചുറ്റ്: 27 ദിവസം", "ONE ORBIT TAKES ABOUT 27 DAYS"),
        ("അതേ സമയം കൊണ്ട് ചന്ദ്രൻ സ്വന്തം അക്ഷത്തിൽ ഒരു തവണ കറങ്ങുകയും ചെയ്യും.", "കറക്കവും 27 ദിവസം", "ITS SPIN TAKES THE SAME TIME"),
        ("രണ്ടും ഒരേ വേഗത്തിലായതുകൊണ്ട് ഒരേ വശം എപ്പോഴും ഭൂമിയെ നോക്കുന്നു.", "ഒരേ വേഗം", "THE TWO MATCH"),
        ("ഇതിനെ ടൈഡൽ ലോക്കിങ് എന്ന് പറയും.", "ടൈഡൽ ലോക്കിങ്", "TIDAL LOCKING"),
        ("ഭൂമിയുടെ ഗുരുത്വാകർഷണം കോടിക്കണക്കിന് വർഷം കൊണ്ട് ചന്ദ്രന്റെ കറക്കം ഇങ്ങനെ ക്രമീകരിച്ചു.", "ഗുരുത്വാകർഷണ ബ്രേക്ക്", "GRAVITY SLOWED ITS SPIN"),
    ],
    "മറുവശം നമ്മൾ കാണാറില്ല!", "THE FAR SIDE STAYS HIDDEN", "ചന്ദ്രന്റെ മറുവശം ഭൂമിയിൽ നിന്ന് ഒരിക്കലും കാണാനാകില്ല!")

FACTS = [
    "Rayleigh scattering by air molecules scatters blue light more than red, giving the blue sky and the red sunset (NASA SpacePlace; Wikipedia: Diffuse sky radiation).",
    "Stars twinkle because turbulence in Earth's atmosphere bends their light; planets look like small discs, so the effect averages out (NASA Space Place).",
    "The Moon illusion is a perceptual effect: the Moon's angular size is the same at the horizon and overhead (NASA Science).",
    "An annular solar eclipse was visible from Kerala on 26 December 2019 (Indian Institute of Astrophysics; NASA Eclipse pages). Eclipse glasses certified to ISO 12312-2 are needed to look at the Sun.",
    "The International Space Station orbits at about 400 km altitude at about 28,000 km/h and circles Earth in about 90 minutes (NASA).",
    "The Moon is tidally locked to Earth: its rotation period equals its orbital period of about 27.3 days (NASA Science).",
] + FACTS_MOON
# richer scenes: the trip to the Moon and the landing
rich(MOON, 3, 7, "moonland", {"launch": 0, "orbits": 2, "transfer": 3, "capture": 4}, [(0, -150, 420, 1.1), (1.5, -100, 520, 0.95), (3, 500, 420, 0.8), (4, 1050, 380, 1.3)])
rich(MOON, 14, 24, "moonland", {"descend": 0, "land": 3, "rover": 6}, [(0, 3300, 340, 1.0, True), (3, 3350, 560, 1.5), (6, 3600, 640, 1.4), (8, 3450, 520, 1.1)])

# richer scenes (lab cut-aways) for the sky Shorts
lab(BLUE, 0, 5, "bluesky", {"ray": 1, "scatter": 2, "sunset": 4}, [(1, "വെളുത്ത വെളിച്ചം", "WHITE LIGHT HAS ALL COLOURS", 500, 330), (2, "നീല ചിതറുന്നു", "BLUE SCATTERS", 500, 420), (4, "സന്ധ്യയ്ക്ക് ദൂരം കൂടുതൽ", "A LONGER PATH AT SUNSET", 500, 330)])
lab(TWINKLE, 0, 5, "twinkle", {"ray": 1, "bend": 3, "planet": 5}, [(1, "അന്തരീക്ഷത്തിലൂടെ", "THROUGH OUR AIR", 800, 520), (3, "വെളിച്ചം വളയുന്നു", "THE LIGHT BENDS", 800, 520), (5, "ഗ്രഹം: ചെറിയ വൃത്തം", "A PLANET IS A SMALL DISC", 800, 260)])
lab(ILLUSION, 0, 5, "moonillusion", {"horizon": 0, "overhead": 2, "tube": 5}, [(2, "അളന്നാൽ ഒരേ വലുപ്പം", "THE SAME SIZE", 500, 480), (4, "മരങ്ങൾ വലുപ്പം തോന്നിക്കുന്നു", "TREES FOOL OUR SENSE OF SCALE", 500, 480)])
lab(ECLIPSE, 0, 6, "ringeclipse", {"align": 2, "near": 3, "far": 4, "ring": 5}, [(2, "ചന്ദ്രൻ സൂര്യനു മുന്നിൽ", "THE MOON PASSES IN FRONT", 500, 330), (4, "അകലെ, ചെറുത്", "FARTHER AWAY, SO SMALLER", 500, 330)])
lab(ISS, 0, 6, "iss", {"orbit": 1, "speed": 3, "reflect": 5}, [(1, "ബഹിരാകാശ നിലയം", "THE SPACE STATION", 500, 600), (3, "മണിക്കൂറിൽ 28,000 km", "ABOUT 28,000 KM/H", 500, 260), (5, "സൂര്യപ്രകാശം പ്രതിഫലിക്കുന്നു", "IT REFLECTS SUNLIGHT", 900, 250)])
lab(MOONFACE, 0, 5, "moonface", {"orbit": 1, "spin": 2, "lock": 3}, [(1, "ഒരു ചുറ്റ് ≈ 27 ദിവസം", "ONE ORBIT ABOUT 27 DAYS", 500, 200), (3, "ഒരേ വശം ഭൂമിയെ നോക്കുന്നു", "THE SAME SIDE FACES EARTH", 500, 200)])

VIDEOS = [MOON, BLUE, TWINKLE, ILLUSION, ECLIPSE, ISS, MOONFACE]
