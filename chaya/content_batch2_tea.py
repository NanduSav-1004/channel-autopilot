"""Science Chaya: the science of a cup of tea, from Munnar to the glass (long)."""
from chaya.content_monsoon import BL, BR, DK, GD, LF, OR, RD, SE, B
from chaya.dsl import GROUND, LB, PT, C, I, T

LONG = {
    "id": "tea_long", "orient": "wide", "mood": "curious",
    "title_ml": "ഒരു ഗ്ലാസ് ചായയുടെ ശാസ്ത്രം: മൂന്നാറിലെ ഇല മുതൽ നിങ്ങളുടെ ഗ്ലാസ് വരെ",
    "title_en": "The science of a cup of chai: from a Munnar leaf to your glass",
    "thumb": {"ml": "ചായയുടെ ശാസ്ത്രം", "en": "THE SCIENCE OF TEA", "hero": "compose"},
    "comment": "നിങ്ങളുടെ ചായയിൽ എന്തൊക്കെ ചേർക്കും: ഏലം, ഇഞ്ചി, അതോ വെറും ചായയോ?",
    "beats": [
        B("ഒരു ഗ്ലാസ് ചായ ഉണ്ടാക്കാൻ ഒരു പച്ച ഇല നടത്തുന്ന യാത്ര അറിയാമോ?", ("ചായയുടെ യാത്ര", "THE JOURNEY OF A CUP OF TEA", BR), C([I("leaf", 0.3, 0.5, 5, anim="float"), I("cup", 0.7, 0.5, 5, anim="float", label=LB("ചായ", "CHAI", BR, 240)), T("ഇല → ചായ", 0.5, 0.86, 90)], bg="dusk")),
        B("നമ്മുടെ ചായപ്പൊടി ഉണ്ടാകുന്നത് കാമെല്ലിയ സൈനെൻസിസ് എന്ന ചെടിയുടെ ഇലയിൽ നിന്നാണ്.", ("കാമെല്ലിയ സൈനെൻസിസ്", "THE TEA PLANT: CAMELLIA SINENSIS", LF), C([GROUND("#3f8f4f", 0.7), I("leaf", 0.2, 0.55, 3), I("leaf", 0.4, 0.5, 4), I("leaf", 0.6, 0.55, 3.4), I("leaf", 0.8, 0.5, 4)], bg="sky")),
        B("കേരളത്തിലെ ഏറ്റവും പ്രശസ്തമായ തേയിലത്തോട്ടങ്ങൾ മൂന്നാറിലാണ്.", ("മൂന്നാർ", "MUNNAR, KERALA'S TEA COUNTRY", LF), {"kind": "map", "p": {"arrows": False, "shade": "none", "atb": {"arrows": 99, "shade": 99, "ridge": 99}, "pins": [{"id": "munnar", "ml": "മൂന്നാർ", "en": "MUNNAR", "atb": 0.3, "w": 250}]}}),
        B("മൂന്നാർ സമുദ്രനിരപ്പിൽ നിന്ന് ആയിരത്തി അഞ്ഞൂറിലധികം മീറ്റർ ഉയരത്തിലാണ്.", ("1,500 മീറ്ററിലധികം ഉയരം", "OVER 1,500 METRES ABOVE SEA LEVEL", SE), {"kind": "stat", "p": {"value": 1532, "suffix": " m", "ml": "മൂന്നാറിന്റെ ഉയരം", "en": "ABOVE SEA LEVEL", "icon": "mountain"}}),
        B("തണുപ്പും ധാരാളം മഴയും തേയിലച്ചെടിക്ക് ഇഷ്ടമാണ്.", ("തണുപ്പും മഴയും", "TEA LOVES COOL AIR AND RAIN", BL), C([I("cloudDark", 0.5, 0.2, 5), PT("rain", 50, [0.25, 0.3, 0.75, 0.85], "#4aa3d8", 5), GROUND("#3f8f4f", 0.86), I("leaf", 0.3, 0.76, 3), I("leaf", 0.7, 0.76, 3)], bg="storm")),
        B("പശ്ചിമഘട്ടത്തിലെ മഴ തന്നെയാണ് ഈ തോട്ടങ്ങളെ പച്ചപ്പിൽ നിർത്തുന്നത്.", ("പശ്ചിമഘട്ടത്തിലെ മഴ", "THE GHATS' RAIN KEEPS THEM GREEN", LF)),
        B("ഒരു കഥയനുസരിച്ച് കണ്ണൻ ദേവൻ മലകൾക്ക് ആ പേര് വന്നത് കണ്ണൻ, ദേവൻ എന്ന ആദിവാസി മനുഷ്യരിൽ നിന്നാണ്.", ("കണ്ണൻ ദേവൻ", "HOW THE KANNAN DEVAN HILLS GOT THEIR NAME", GD)),
        B("ആയിരത്തി എണ്ണൂറ്റി തൊണ്ണൂറ്റി അഞ്ചിനോടടുത്ത് ഫിൻലേ കമ്പനി ഇവിടെ തോട്ടങ്ങൾ വാങ്ങി.", ("ഫിൻലേ കമ്പനി", "FINLAY BOUGHT THE ESTATES IN THE 1890s", BR)),
        B("ഇനി ആ പച്ച ഇല ചായപ്പൊടിയാകുന്ന വഴി നോക്കാം.", ("ഇല → ചായപ്പൊടി", "FROM LEAF TO TEA POWDER", DK)),
        B("ഒന്നാം ഘട്ടം വാട്ടൽ, ഇലകൾ കുറച്ചുനേരം വാട്ടി ഈർപ്പം കുറയ്ക്കുന്നു.", ("1. വാട്ടൽ", "WITHERING", LF), C([I("leaf", 0.5, 0.5, 8, anim="float"), T("വാട്ടൽ", 0.5, 0.86, 90)], bg="dusk")),
        B("രണ്ടാം ഘട്ടം ഉരുട്ടൽ, ഉരുട്ടുമ്പോൾ ഇലയിലെ കോശങ്ങൾ പൊട്ടി അകത്തെ രസം പുറത്തുവരും.", ("2. ഉരുട്ടൽ", "ROLLING BREAKS THE LEAF CELLS", OR)),
        B("മൂന്നാം ഘട്ടം ഓക്സീകരണം, ആ രസം വായുവിലെ ഓക്സിജനുമായി ചേർന്ന് തവിട്ടുനിറവും രുചിയും ഉണ്ടാകുന്നു.", ("3. ഓക്സീകരണം", "OXIDATION GIVES COLOUR AND FLAVOUR", RD)),
        B("ഇതിനെ പലരും പുളിപ്പിക്കൽ എന്ന് വിളിക്കാറുണ്ട്, പക്ഷേ ശരിക്കും അത് ഓക്സീകരണമാണ്.", ("പുളിപ്പിക്കലല്ല, ഓക്സീകരണം", "IT IS OXIDATION, NOT FERMENTATION", GD)),
        B("നാലാം ഘട്ടം ഉണക്കൽ, ചൂടുള്ള വായുവിൽ ഉണക്കി ഈ മാറ്റം നിർത്തുന്നു.", ("4. ഉണക്കൽ", "DRYING STOPS THE CHANGE", BR)),
        B("ഇല പൊട്ടാതെ മൃദുവായി ഉരുട്ടുന്ന രീതിക്ക് ഓർത്തഡോക്സ് എന്ന് പറയും.", ("ഓർത്തഡോക്സ്", "ORTHODOX: GENTLE, LEAVES STAY WHOLE", LF)),
        B("ഇലകൾ ചെറു തരികളായി മുറിക്കുന്ന രീതിയാണ് സിടിസി, ചായക്കടയിലെ കടുപ്പമുള്ള ചായപ്പൊടി മിക്കവാറും അതാണ്.", ("സിടിസി: ചെറു തരികൾ", "CTC: CHOPPED INTO TINY GRAINS", OR)),
        B("തരികൾ ചെറുതായതുകൊണ്ട് അവയിലെ രുചിയും നിറവും വെള്ളത്തിലേക്ക് വേഗം ഇറങ്ങും.", ("വേഗം കടുപ്പം", "SMALL GRAINS GIVE UP FLAVOUR FAST", SE)),
        B("ചായയിലെ ഉന്മേഷം തരുന്ന വസ്തു കഫീൻ ആണ്.", ("കഫീൻ", "CAFFEINE", DK)),
        B("കഫീൻ തലച്ചോറിലെ അഡിനോസിൻ എന്ന വസ്തുവിന്റെ പ്രവർത്തനം തടഞ്ഞ് ഉറക്കം വരുന്നത് വൈകിക്കുന്നു.", ("ഉറക്കത്തെ വൈകിക്കുന്നു", "IT BLOCKS THE SLEEPINESS SIGNAL", BL)),
        B("വെള്ളം കൂടുതൽ ചൂടാകുമ്പോൾ രുചിയും നിറവും വേഗത്തിൽ ഇറങ്ങും.", ("ചൂട് കൂടിയാൽ വേഗം", "HOTTER WATER EXTRACTS FASTER", RD)),
        B("പാൽ ചേർക്കുമ്പോൾ ചായയുടെ ചവർപ്പ് കുറഞ്ഞതായി തോന്നും.", ("പാൽ ചേർക്കുമ്പോൾ", "MILK SOFTENS THE BITTERNESS", GD)),
        B("ഒരേ ചായപ്പൊടി തന്നെ വെള്ളത്തിന്റെ ചൂടും സമയവും അനുസരിച്ച് വ്യത്യസ്ത രുചി തരും.", ("ചൂടും സമയവും", "HEAT AND TIME CHANGE THE TASTE", OR)),
        B("ഒരു ഇലയിൽ നിന്ന് നിങ്ങളുടെ ഗ്ലാസ് വരെയുള്ള യാത്ര ഇങ്ങനെയാണ്.", ("ചുരുക്കത്തിൽ", "THE WHOLE JOURNEY", BR), {"kind": "flow", "p": {"carry": "water", "nodes": [{"icon": "leaf", "ml": "ഇല", "en": "LEAF"}, {"icon": "bowl", "ml": "ഉരുട്ടൽ", "en": "ROLL"}, {"icon": "sun", "ml": "ഓക്സീകരണം", "en": "OXIDISE"}, {"icon": "thermo", "ml": "ഉണക്കൽ", "en": "DRY"}, {"icon": "cup", "ml": "ചായ", "en": "CHAI"}]}}),
        B("നിങ്ങളുടെ ചായയിൽ എന്തൊക്കെ ചേർക്കും, ഏലം, ഇഞ്ചി, അതോ വെറും ചായയോ?", None, {"kind": "outro", "p": {"ml": "നിങ്ങളുടെ ചായയിൽ എന്തൊക്കെ ചേർക്കും: ഏലം, ഇഞ്ചി, അതോ വെറും ചായയോ?", "en": "WHAT GOES INTO YOUR CHAI: CARDAMOM, GINGER, OR PLAIN?"}}),
        B("താഴെ കമന്റ് ചെയ്യൂ, ഇതുപോലുള്ള വീഡിയോകൾക്കായി സയൻസ് ചായ സബ്സ്ക്രൈബ് ചെയ്യൂ."),
    ],
}
FACTS = [
    "Black tea is made by withering, rolling (which breaks the leaf cells), oxidation by polyphenol oxidase, and drying; the orthodox method keeps leaves whole, CTC chops them into tiny grains (Britannica: Black tea; PMC review).",
    "Munnar lies at about 1,532 m; Finlay bought the estates in the mid-1890s; the Kannan Devan name is said to come from two local guides (Wikipedia: Munnar; Kerala Museum; Kerala Tourism).",
    "Caffeine blocks adenosine receptors in the brain, delaying sleepiness (standard pharmacology).",
]
VIDEOS = [LONG]
