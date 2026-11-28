"""Science Chaya batch 7: nature (Western Ghats biodiversity long; neelakurinji, kingfisher, honeybee dance, bats, mangroves, peacock colour Shorts)."""
from chaya.quick import ST, TX, S, lg, sh

GHATS = lg(
    "ghats_long", "പശ്ചിമഘട്ടത്തിൽ ഇത്രയധികം ജീവികൾ എന്തുകൊണ്ട്? | ലോകത്തിലെ ജൈവവൈവിധ്യ കേന്ദ്രം", "Why does the Western Ghats hold so many species? A world biodiversity hotspot",
    "പശ്ചിമഘട്ടത്തിന്റെ രഹസ്യം", "WESTERN GHATS SECRET", "പശ്ചിമഘട്ടത്തിൽ നിങ്ങൾ കണ്ട ഏറ്റവും അപൂർവമായ ജീവി ഏതാണ്?", "WHAT IS THE RAREST CREATURE YOU HAVE SEEN THERE?",
    [
        ("കേരളത്തിന്റെ കിഴക്കൻ അതിരിൽ നീണ്ടുകിടക്കുന്ന പശ്ചിമഘട്ടം ലോകത്തിലെ ഏറ്റവും ജീവസമ്പന്നമായ പ്രദേശങ്ങളിൽ ഒന്നാണ്.", "ലോകത്തിലെ ജീവസമ്പന്ന പ്രദേശം", "ONE OF THE RICHEST PLACES ON EARTH", S(["mountain", "tree", "elephant"], "sky", label=("പശ്ചിമഘട്ടം", "WESTERN GHATS"))),
        ("ഇത് യുനെസ്കോ ലോക പൈതൃക പട്ടികയിൽ ഉൾപ്പെട്ട സ്ഥലമാണ്.", "ലോക പൈതൃക പ്രദേശം", "A UNESCO WORLD HERITAGE SITE"),
        ("ഇത്രയും ജീവികൾ ഇവിടെ എങ്ങനെ ഒന്നിച്ച് വന്നു എന്ന് ഇന്ന് നോക്കാം.", "എങ്ങനെ ഒന്നിച്ചു?", "HOW SO MANY LIVE HERE", TX("എങ്ങനെ ഇത്രയും?", "HOW SO MANY?", "tree", "#4a2a17")),
        ("ഇവിടെ ഏഴായിരത്തിലധികം ഇനം പുഷ്പിക്കുന്ന സസ്യങ്ങൾ ഉണ്ടെന്ന് കണക്കാക്കുന്നു.", "7000+ സസ്യങ്ങൾ", "OVER 7,000 FLOWERING PLANTS", ST(7000, "+", "പുഷ്പിക്കുന്ന സസ്യ ഇനങ്ങൾ", "FLOWERING PLANT SPECIES", "leaf")),
        ("നൂറ്റിമുപ്പതിലധികം ഇനം സസ്തനികളും അഞ്ഞൂറിലധികം ഇനം പക്ഷികളും ഇവിടെയുണ്ട്.", "സസ്തനികളും പക്ഷികളും", "MAMMALS AND BIRDS GALORE", S(["elephant", "bird"], "sky")),
        ("ഇതിൽ പലതും ലോകത്ത് മറ്റൊരിടത്തും കാണാത്തവയാണ്, അവയെ തദ്ദേശീയ ജീവികൾ എന്ന് പറയും.", "മറ്റൊരിടത്തുമില്ല", "FOUND NOWHERE ELSE"),
        ("ആദ്യത്തെ കാരണം മഴയാണ്.", "ഒന്നാം കാരണം: മഴ", "REASON ONE: RAIN", S(["cloudDark"], "storm", ("rain", 40, "#4aa3d8"))),
        ("മൺസൂൺ കാറ്റ് പശ്ചിമഘട്ടത്തിൽ തട്ടി ധാരാളം മഴ പെയ്യിക്കും.", "മലയിൽ തട്ടുന്ന കാറ്റ്", "WINDS HIT THE MOUNTAINS"),
        ("ധാരാളം വെള്ളം ഉള്ളതുകൊണ്ട് ഇവിടെ നിത്യഹരിത വനങ്ങൾ വളരും.", "നിത്യഹരിത വനം", "EVERGREEN FORESTS GROW"),
        ("രണ്ടാമത്തെ കാരണം ഉയരത്തിലെ വ്യത്യാസമാണ്.", "രണ്ടാം കാരണം: ഉയരം", "REASON TWO: ALTITUDE", S(["mountain"], "sky", text="ഉയരം")),
        ("കടൽനിരപ്പിൽ നിന്ന് ആനമുടിയുടെ രണ്ടായിരത്തി അറുനൂറ്റി തൊണ്ണൂറ്റഞ്ച് മീറ്റർ വരെ ഉയരമുണ്ട്.", "ആനമുടി 2,695 m", "ANAMUDI, 2,695 M", ST(2695, " m", "ആനമുടിയുടെ ഉയരം", "THE HIGHEST PEAK IN SOUTH INDIA", "mountain")),
        ("ഓരോ ഉയരത്തിലും താപനിലയും ഈർപ്പവും മാറും, അതുകൊണ്ട് ഓരോ ഉയരത്തിനും വ്യത്യസ്ത ജീവികൾ.", "ഓരോ ഉയരത്തിനും ജീവികൾ", "EACH HEIGHT, ITS OWN LIFE"),
        ("താഴെ ചൂടുള്ള കാടുകൾ, മുകളിൽ തണുപ്പുള്ള പുൽമേടുകൾ.", "കാടും പുൽമേടും", "WARM FOREST BELOW, COOL GRASS ABOVE", S(["tree", "mountain"], "sky")),
        ("മൂന്നാമത്തെ കാരണം ഒറ്റപ്പെടലാണ്.", "മൂന്നാം കാരണം: ഒറ്റപ്പെടൽ", "REASON THREE: ISOLATION", TX("ഒറ്റപ്പെടൽ", "ISOLATION", "mountain", "#c8442f")),
        ("പശ്ചിമഘട്ടം ഒരു നീണ്ട മലനിരയായി മറ്റ് കാടുകളിൽ നിന്ന് ഒറ്റപ്പെട്ട് നിൽക്കുന്നു.", "ഒറ്റപ്പെട്ട മലനിര", "A LONG, ISOLATED CHAIN"),
        ("ഒറ്റപ്പെട്ട സ്ഥലത്ത് ജീവികൾ ലക്ഷക്കണക്കിന് വർഷം കൊണ്ട് സ്വന്തം വഴിയിൽ പരിണമിച്ച് പുതിയ ഇനങ്ങളായി മാറും.", "സ്വന്തം വഴിയിൽ പരിണാമം", "EVOLVING ON ITS OWN PATH"),
        ("സിംഹവാലൻ കുരങ്ങും നീലഗിരി മലയാടും ഇതിന് ഉദാഹരണങ്ങളാണ്.", "സിംഹവാലൻ, വരയാട്", "LION-TAILED MACAQUE, NILGIRI TAHR", S(["elephant"], "sky", label=("തദ്ദേശീയർ", "ENDEMIC"))),
        ("പാലക്കാട് ചുരം എന്ന വിടവ് ഈ മലനിരയെ തെക്കും വടക്കുമായി വേർതിരിക്കുന്നു.", "പാലക്കാട് ചുരം", "THE PALAKKAD GAP"),
        ("ആ വിടവ് ചില ജീവികൾക്ക് മറുവശത്തേക്ക് കടക്കാൻ തടസ്സമായി.", "വിടവ് ഒരു തടസ്സം", "A BARRIER FOR SOME SPECIES"),
        ("നാലാമത്തേത് ചൂടുള്ള കാലാവസ്ഥയാണ്.", "നാലാം കാരണം: ചൂട്", "REASON FOUR: WARMTH", S(["sun"], "dusk")),
        ("ഉഷ്ണമേഖലയിൽ വർഷം മുഴുവൻ ചൂടും വെളിച്ചവും കിട്ടുന്നതുകൊണ്ട് ജീവികൾക്ക് വളരാൻ തടസ്സമില്ല.", "വർഷം മുഴുവൻ വളർച്ച", "GROWTH ALL YEAR"),
        ("അതുകൊണ്ട് ചെറിയ സ്ഥലത്ത് പോലും ധാരാളം ജീവികൾ ഒന്നിച്ച് കഴിയും.", "ചെറിയ സ്ഥലത്ത് വലിയ വൈവിധ്യം", "MANY SPECIES, SMALL SPACE"),
        ("എന്നാൽ ഈ സമ്പത്ത് അപകടത്തിലുമാണ്.", "അപകടത്തിൽ", "BUT IT IS AT RISK", S(["tree", "house"], "dusk")),
        ("കാടുകൾ വെട്ടിത്തെളിച്ച് തോട്ടങ്ങളും വീടുകളും ഉണ്ടാക്കുമ്പോൾ ജീവികളുടെ വീട് ചുരുങ്ങുന്നു.", "വീട് ചുരുങ്ങുന്നു", "THEIR HOMES SHRINK"),
        ("ഒരിടത്തെ ജീവി ഇല്ലാതായാൽ അത് ലോകത്ത് നിന്ന് തന്നെ ഇല്ലാതാകും, കാരണം മറ്റൊരിടത്തും അത് ഇല്ല.", "ഇവിടെ പോയാൽ എവിടെയുമില്ല", "LOSE IT HERE, LOSE IT EVERYWHERE"),
        ("കാടിനെ അറിയുകയും സംരക്ഷിക്കുകയും ചെയ്യുന്നത് നമ്മുടെ നാടിന്റെ ഭാവിക്ക് വേണ്ടിയാണ്.", "അറിയൂ, സംരക്ഷിക്കൂ", "KNOW IT, PROTECT IT", TX("അറിയൂ, സംരക്ഷിക്കൂ", "KNOW IT, PROTECT IT", "tree", "#2f7d4f")),
    ],
)
FACTS_GHATS = ["The Western Ghats are a UNESCO World Heritage Site (inscribed 2012) and a global biodiversity hotspot with over 7,000 flowering plant species, more than 139 mammal and 508 bird species, many of them endemic (UNESCO World Heritage Centre).",
               "Anamudi, at 2,695 m, is the highest peak in the Western Ghats and in South India (Wikipedia: Anamudi).",
               "The lion-tailed macaque and the Nilgiri tahr are endemic to the Western Ghats; the Palakkad Gap divides the range (Wikipedia; IUCN)."]

KURINJI = sh(
    "neelakurinji_s", "നീലക്കുറിഞ്ഞി പന്ത്രണ്ട് വർഷത്തിൽ ഒരിക്കൽ പൂക്കുന്നത് എന്തുകൊണ്ട്?", "Why does neelakurinji bloom once in twelve years?", "പന്ത്രണ്ട് വർഷത്തിൽ ഒരിക്കൽ", "NEELAKURINJI",
    [
        ("മൂന്നാറിലെ മലകൾ പന്ത്രണ്ട് വർഷത്തിൽ ഒരിക്കൽ നീല നിറത്തിൽ പൂക്കുന്നത് എന്തുകൊണ്ടാണ്?", "മലകളിൽ നീല പൂക്കൾ", "BLUE HILLS OF MUNNAR", S(["mountain", "leaf"], "sky", label=("നീലക്കുറിഞ്ഞി", "NEELAKURINJI"))),
        ("ഈ ചെടിയുടെ ഒരു തലമുറ ഒരുമിച്ച് പൂക്കുന്ന സ്വഭാവം ഉള്ളതാണ്.", "ഒരുമിച്ച് പൂക്കും", "THEY ALL BLOOM TOGETHER"),
        ("ഒരേ വർഷം ഒന്നിച്ച് പൂവിട്ട് വിത്തുണ്ടാക്കി ചെടികൾ നശിക്കും.", "പൂവിട്ട് വിത്താകും", "FLOWER, SEED, AND DIE"),
        ("ഒന്നിച്ച് ഒരുപാട് വിത്തുണ്ടാകുമ്പോൾ ജീവികൾക്ക് മുഴുവൻ തിന്നു തീർക്കാൻ കഴിയില്ല.", "തിന്നുതീർക്കാനാവില്ല", "TOO MANY SEEDS TO EAT"),
        ("ആ വിത്തുകളിൽ നിന്ന് അടുത്ത തലമുറ മുളയ്ക്കും.", "അടുത്ത തലമുറ", "THE NEXT GENERATION SPROUTS"),
        ("അവസാനം പൂത്തത് രണ്ടായിരത്തി പതിനെട്ടിലാണ്, അടുത്തത് രണ്ടായിരത്തി മുപ്പതിൽ പ്രതീക്ഷിക്കുന്നു.", "2018 കഴിഞ്ഞു, അടുത്തത് 2030", "LAST IN 2018, NEXT IN 2030"),
    ],
    "പന്ത്രണ്ട് വർഷത്തെ കാത്തിരിപ്പ്!", "A TWELVE-YEAR WAIT", "നീലക്കുറിഞ്ഞി പൂക്കാൻ പ്രകൃതി പന്ത്രണ്ട് വർഷം കാത്തിരിക്കുന്നു!")

KINGFISHER = sh(
    "kingfisher_s", "മീൻകൊത്തി വെള്ളത്തിൽ തെറിപ്പിക്കാതെ മുങ്ങുന്നത് എങ്ങനെ?", "How does a kingfisher dive without a splash?", "മീൻകൊത്തിയുടെ മുങ്ങൽ", "THE KINGFISHER DIVE",
    [
        ("മീൻകൊത്തി വെള്ളത്തിലേക്ക് ഒരു തുള്ളി പോലും തെറിപ്പിക്കാതെ മുങ്ങുന്നത് എങ്ങനെയാണ്?", "തെറിക്കാത്ത മുങ്ങൽ", "A DIVE WITHOUT A SPLASH", S(["bird", "drop"], "sky", label=("മീൻകൊത്തി", "KINGFISHER"))),
        ("അതിന്റെ നീണ്ട കൂർത്ത ചുണ്ടിന്റെ ആകൃതി വളരെ പ്രധാനമാണ്.", "നീണ്ട കൂർത്ത ചുണ്ട്", "THE LONG POINTED BEAK"),
        ("ചുണ്ടിന്റെ കനം പടിപടിയായി കൂടുന്ന ആകൃതി വെള്ളത്തെ സാവധാനം വകഞ്ഞുമാറ്റും.", "പടിപടിയായ ആകൃതി", "IT PARTS THE WATER GENTLY"),
        ("ഇതേ ആകൃതി അനുകരിച്ചാണ് ജപ്പാനിലെ ബുള്ളറ്റ് ട്രെയിനിന്റെ മുൻഭാഗം രൂപകൽപ്പന ചെയ്തത്.", "ബുള്ളറ്റ് ട്രെയിൻ", "COPIED BY THE BULLET TRAIN"),
        ("അങ്ങനെ ട്രെയിൻ തുരങ്കത്തിൽ കയറുമ്പോൾ ഉണ്ടാകുന്ന വലിയ ശബ്ദം കുറഞ്ഞു.", "ശബ്ദം കുറഞ്ഞു", "THE TUNNEL BOOM FELL"),
        ("പ്രകൃതിയുടെ രൂപകൽപ്പനയിൽ നിന്ന് പഠിക്കുന്നതിനെ ബയോമിമിക്രി എന്ന് പറയും.", "ബയോമിമിക്രി", "BIOMIMICRY"),
    ],
    "പക്ഷിയിൽ നിന്ന് ട്രെയിനിലേക്ക്!", "FROM A BIRD TO A TRAIN", "ഒരു ചെറിയ പക്ഷി ഒരു വലിയ ട്രെയിനിനെ പഠിപ്പിച്ചു!")

BEE = sh(
    "beedance_s", "തേനീച്ചകൾ നൃത്തം ചെയ്ത് വഴി പറയുന്നത് എങ്ങനെ?", "How do honeybees dance to give directions?", "തേനീച്ചയുടെ നൃത്തം", "THE WAGGLE DANCE",
    [
        ("തേനീച്ചകൾ നൃത്തം ചെയ്തുകൊണ്ട് പൂക്കളുടെ വഴി പറഞ്ഞുകൊടുക്കും എന്ന് അറിയാമോ?", "വഴി പറയുന്ന നൃത്തം", "A DANCE THAT GIVES DIRECTIONS", S(["leaf", "sun"], "sky", label=("തേനീച്ച", "HONEYBEE"))),
        ("പൂക്കൾ കണ്ടെത്തിയ ഒരു തേനീച്ച കൂട്ടിലേക്ക് മടങ്ങി ഒരു പ്രത്യേക നൃത്തം ചെയ്യും.", "മടങ്ങി വന്ന് നൃത്തം", "IT DANCES BACK AT THE HIVE"),
        ("അതിനെ വാഗിൾ ഡാൻസ് എന്ന് പറയും, ശരീരം ഇളക്കി നേർവരയിൽ നീങ്ങും.", "വാഗിൾ ഡാൻസ്", "THE WAGGLE DANCE"),
        ("ആ വരയുടെ ദിശ സൂര്യനെ അടിസ്ഥാനമാക്കി പൂക്കളുടെ ദിശ കാണിക്കും.", "ദിശ = സൂര്യനോട് ആപേക്ഷികം", "THE ANGLE SHOWS THE DIRECTION"),
        ("ഇളക്കത്തിന്റെ ദൈർഘ്യം പൂക്കളിലേക്കുള്ള ദൂരം പറയും.", "ദൈർഘ്യം = ദൂരം", "THE LENGTH SHOWS THE DISTANCE"),
        ("ഈ കണ്ടുപിടുത്തത്തിന് കാൾ ഫോൺ ഫ്രിഷിന് നൊബേൽ സമ്മാനം കിട്ടി.", "നൊബേൽ സമ്മാനം", "A NOBEL PRIZE FOR THE DISCOVERY"),
    ],
    "ചെറിയ ജീവി, വലിയ ഭാഷ!", "A TINY CREATURE, A BIG LANGUAGE", "ഒരു തേനീച്ചയുടെ നൃത്തത്തിൽ ഒരു മുഴുവൻ ഭൂപടം ഒളിച്ചിരിക്കുന്നു!")

BAT = sh(
    "bat_s", "വവ്വാലുകൾ ഇരുട്ടിൽ കാണുന്നത് എങ്ങനെ?", "How do bats see in the dark?", "വവ്വാലിന്റെ കണ്ണ് ചെവിയാണ്", "ECHOLOCATION",
    [
        ("കൂരിരുട്ടിൽ വവ്വാലുകൾ തടസ്സങ്ങളിൽ തട്ടാതെ പറക്കുന്നത് എങ്ങനെയാണ്?", "ഇരുട്ടിലെ പറക്കൽ", "FLYING IN PITCH DARK", S(["moon", "bird"], "night", label=("വവ്വാൽ", "BAT"))),
        ("അവ നമുക്ക് കേൾക്കാൻ കഴിയാത്ത ഉയർന്ന ശബ്ദ തരംഗങ്ങൾ പുറപ്പെടുവിക്കും.", "കേൾക്കാത്ത ശബ്ദം", "SOUNDS WE CANNOT HEAR"),
        ("ആ ശബ്ദം മുന്നിലുള്ള വസ്തുക്കളിൽ തട്ടി പ്രതിധ്വനിയായി തിരികെ വരും.", "പ്രതിധ്വനി തിരികെ", "THE ECHO COMES BACK"),
        ("പ്രതിധ്വനി എത്ര വേഗത്തിൽ തിരികെ വരുന്നു എന്ന് നോക്കി ദൂരം തിരിച്ചറിയും.", "സമയം = ദൂരം", "ECHO TIME GIVES DISTANCE"),
        ("പ്രതിധ്വനിയുടെ സ്വഭാവം നോക്കി ഒരു പ്രാണിയാണോ മരമാണോ എന്നും മനസ്സിലാക്കും.", "വസ്തു തിരിച്ചറിയുന്നു", "EVEN WHAT THE OBJECT IS"),
        ("ഇതിനെ എക്കോലൊക്കേഷൻ എന്ന് പറയും, കപ്പലുകളിലെ സോണാറും ഇതേ തത്വമാണ്.", "എക്കോലൊക്കേഷൻ", "THE SAME IDEA AS SONAR"),
    ],
    "ചെവി കൊണ്ട് കാണുന്നവർ!", "SEEING WITH EARS", "വവ്വാലുകൾ ശബ്ദം കൊണ്ട് ഇരുട്ടിൽ ഒരു ചിത്രം വരയ്ക്കുന്നു!")

MANGROVE = sh(
    "mangrove_s", "കണ്ടൽക്കാടുകൾ ഉപ്പുവെള്ളത്തിൽ വളരുന്നത് എങ്ങനെ?", "How do mangroves grow in salt water?", "കണ്ടൽക്കാടിന്റെ രഹസ്യം", "MANGROVES",
    [
        ("മറ്റ് മരങ്ങൾ ചത്തുപോകുന്ന ഉപ്പുവെള്ളത്തിൽ കണ്ടൽച്ചെടികൾ വളരുന്നത് എങ്ങനെയാണ്?", "ഉപ്പുവെള്ളത്തിലെ മരം", "TREES IN SALT WATER", S(["tree", "boat"], "dusk", label=("കണ്ടൽ", "MANGROVE"))),
        ("ചില കണ്ടൽച്ചെടികൾ വേരിൽ തന്നെ ഉപ്പ് അരിച്ച് മാറ്റും.", "വേരിൽ ഉപ്പ് അരിപ്പ", "ROOTS FILTER THE SALT"),
        ("ചിലത് ഇലകളിലൂടെ ഉപ്പ് പുറത്തുകളയും, ഇലയിൽ ഉപ്പ് തരികൾ കാണാം.", "ഇലയിലൂടെ ഉപ്പ് പുറത്ത്", "SALT OUT THROUGH LEAVES"),
        ("ചളിയിൽ വായു കുറവായതുകൊണ്ട് വേരുകൾ മുകളിലേക്ക് കുത്തനെ പൊങ്ങിനിൽക്കും.", "ശ്വസന വേരുകൾ", "BREATHING ROOTS POKE UP"),
        ("അവയുടെ കെട്ടുപിണഞ്ഞ വേരുകൾ തിരമാലയെ തടഞ്ഞ് കരയെ സംരക്ഷിക്കും.", "തിരമാലയെ തടയും", "ROOTS BLOCK THE WAVES"),
        ("മത്സ്യങ്ങളുടെ കുഞ്ഞുങ്ങൾക്ക് വളരാനുള്ള നഴ്സറിയും കണ്ടൽക്കാടുകളാണ്.", "മീൻകുഞ്ഞുങ്ങളുടെ നഴ്സറി", "A NURSERY FOR FISH"),
    ],
    "കരയുടെ കാവൽക്കാർ!", "GUARDIANS OF THE COAST", "ഉപ്പിനെ തോൽപ്പിച്ച് കരയെ കാക്കുന്ന മരങ്ങളാണ് കണ്ടലുകൾ!")

PEACOCK = sh(
    "peacock_s", "മയിൽപ്പീലിയുടെ നിറം എവിടെ നിന്ന്? | നിറമില്ലാത്ത നിറം", "Where does a peacock feather get its colour?", "മയിൽപ്പീലിയുടെ നിറം", "PEACOCK COLOURS",
    [
        ("മയിൽപ്പീലിക്ക് ആ തിളങ്ങുന്ന നീലയും പച്ചയും എവിടെ നിന്നാണ്?", "തിളങ്ങുന്ന നിറങ്ങൾ", "WHERE DO THE COLOURS COME FROM?", S(["bird", "leaf"], "sky", label=("മയിൽപ്പീലി", "PEACOCK"))),
        ("അതിൽ നീല ചായം ഇല്ല എന്നതാണ് അത്ഭുതം.", "ചായമില്ല", "THERE IS NO BLUE DYE"),
        ("പീലിയിലെ വളരെ ചെറിയ ഘടനകൾ വെളിച്ചത്തെ ചില നിറങ്ങളായി മാത്രം പ്രതിഫലിപ്പിക്കും.", "ചെറിയ ഘടനകൾ", "TINY STRUCTURES REFLECT LIGHT"),
        ("ഇതിനെ ഘടനാപരമായ നിറം എന്ന് പറയും.", "ഘടനാപരമായ നിറം", "STRUCTURAL COLOUR"),
        ("അതുകൊണ്ട് പീലി ചരിച്ചുപിടിച്ചാൽ നിറം മാറിമാറി കാണും.", "ചരിച്ചാൽ നിറം മാറും", "TILT IT AND THE COLOUR SHIFTS"),
        ("ഉണങ്ങിയ പീലിയുടെ നിറം മങ്ങാത്തത് ഇതുകൊണ്ടാണ്.", "മങ്ങാത്ത നിറം", "THE COLOUR NEVER FADES"),
    ],
    "നിറം ഒരു കെട്ടിടം പോലെ പണിതത്!", "COLOUR BUILT, NOT PAINTED", "മയിൽപ്പീലിയുടെ നിറം പണിതുണ്ടാക്കിയതാണ്, ചായം തേച്ചതല്ല!")

FACTS = [
    "Neelakurinji (Strobilanthes kunthiana) blooms gregariously once in about 12 years in the Western Ghats, last in 2018 (Wikipedia: Strobilanthes kunthiana; Kerala Forest Department).",
    "The Shinkansen 500 Series nose was modelled on the kingfisher's beak to reduce tunnel boom (Wikipedia: Biomimetics; Nakatsu's design story).",
    "Honeybees communicate direction and distance with the waggle dance, described by Karl von Frisch, Nobel Prize 1973 (Nobel Prize site).",
    "Bats use echolocation: they emit high-frequency calls and judge distance and object type from the returning echoes (Britannica: Echolocation).",
    "Mangroves exclude or excrete salt, have aerial breathing roots (pneumatophores) and protect coasts and fish nurseries (FAO; IUCN).",
    "Peacock feather colours are structural: nanostructures reflect specific wavelengths (Zi et al., PNAS 2003).",
] + FACTS_GHATS
VIDEOS = [GHATS, KURINJI, KINGFISHER, BEE, BAT, MANGROVE, PEACOCK]
