"""Science Chaya: the science behind childhood memories (long)."""
from chaya.content_monsoon import BL, BR, DK, GD, GR, LF, OR, RD, SE, B
from chaya.dsl import GROUND, LB, PT, C, I, R, T

LONG = {
    "id": "memories_long", "orient": "wide", "mood": "curious",
    "title_ml": "ചെറുപ്പത്തിലെ ആറ് ഓർമ്മകളും അവയുടെ ശാസ്ത്രവും: മഴയുടെ മണം മുതൽ ഗോലി സോഡ വരെ",
    "title_en": "The science behind six childhood memories: the smell of rain, fireflies, goli soda and more",
    "thumb": {"ml": "ആ ഓർമ്മകളുടെ ശാസ്ത്രം", "en": "THE SCIENCE OF CHILDHOOD", "hero": "compose"},
    "comment": "ഈ ആറ് ഓർമ്മകളിൽ നിങ്ങൾ ഏറ്റവും കൂടുതൽ മിസ്സ് ചെയ്യുന്നത് ഏതാണ്?",
    "beats": [
        B("ആദ്യ മഴയുടെ മണം, രാത്രിയിലെ മിന്നാമിനുങ്ങ്, ഗോലി സോഡ, ഓർമ്മയുണ്ടോ ഇതൊക്കെ?", ("ഓർമ്മയുണ്ടോ?", "DO YOU REMEMBER THESE?", DK),
          C([I("drop", 0.2, 0.5, 3, anim="float"), I("firefly", 0.4, 0.5, 3, anim="blink"), I("bottle", 0.6, 0.5, 3, anim="float"), I("cassette", 0.8, 0.5, 2.6, anim="float"), T("ഓർമ്മകൾ", 0.5, 0.86, 110)], bg="dusk")),
        B("ഇവയ്ക്കെല്ലാം പിന്നിൽ അത്ഭുതകരമായ ശാസ്ത്രമുണ്ട്.", ("ശാസ്ത്രമുണ്ട്", "THERE IS SCIENCE BEHIND EACH", BR)),
        B("ഒന്നാമത്തേത് ആദ്യ മഴയുടെ മണം.", ("1. മഴയുടെ മണം", "THE SMELL OF THE FIRST RAIN", BL), C([R(0, 0.7, 1, 0.3, "#8a5a36"), PT("rain", 45, [0.05, 0.1, 0.95, 0.7], "#4aa3d8", 5), I("cloudDark", 0.5, 0.18, 5)], bg="storm")),
        B("ഇതിന് പെട്രിക്കോർ എന്ന് പറയും, ആയിരത്തി തൊള്ളായിരത്തി അറുപത്തിനാലിൽ ഓസ്ട്രേലിയയിലെ രണ്ട് ഗവേഷകരാണ് ഈ പേര് നൽകിയത്.", ("പെട്രിക്കോർ · 1964", "NAMED BY TWO AUSTRALIAN SCIENTISTS", GD)),
        B("വേനലിൽ ചെടികൾ ഒരു തരം എണ്ണ മണ്ണിലേക്ക് പുറത്തുവിടും.", ("ചെടികളുടെ എണ്ണ", "PLANTS RELEASE AN OIL IN DRY SPELLS", LF), C([R(0, 0.65, 1, 0.35, "#8a5a36"), I("tree", 0.5, 0.55, 5), PT("bubbles", 16, [0.4, 0.62, 0.6, 0.95], "#e8c35f", 6)], bg="sky")),
        B("മണ്ണിലെ ബാക്ടീരിയകൾ ജിയോസ്മിൻ എന്ന വസ്തുവും ഉണ്ടാക്കും.", ("ജിയോസ്മിൻ", "SOIL BACTERIA MAKE GEOSMIN", OR)),
        B("മഴത്തുള്ളി മണ്ണിൽ വീഴുമ്പോൾ ചെറിയ കുമിളകൾ ഉണ്ടായി ആ മണം വായുവിലേക്ക് തെറിക്കും.", ("മണം വായുവിലേക്ക്", "RAINDROPS FLICK THE SMELL INTO THE AIR", SE), C([R(0, 0.7, 1, 0.3, "#8a5a36"), PT("rain", 12, [0.3, 0.1, 0.7, 0.7], "#4aa3d8", 7), PT("bubbles", 26, [0.3, 0.3, 0.7, 0.7], "#f3e2b8", 4)], bg="storm")),
        B("അതുകൊണ്ടാണ് ചെറിയ മഴയിൽ മണം കൂടുതൽ അറിയുന്നത്.", ("ചെറിയ മഴ, വലിയ മണം", "LIGHT RAIN SMELLS STRONGEST", BL)),
        B("രണ്ടാമത്തേത് രാത്രിയിലെ മിന്നാമിനുങ്ങ്.", ("2. മിന്നാമിനുങ്ങ്", "FIREFLIES", DK), C([I("moon", 0.82, 0.15, 2.5), GROUND("#12301f", 0.8), I("tree", 0.2, 0.7, 4), I("tree", 0.8, 0.68, 4), PT("fireflies", 26, [0.05, 0.3, 0.95, 0.8], "#fff36b", 7)], bg="night")),
        B("അവയുടെ ശരീരത്തിൽ ലൂസിഫെറിൻ എന്ന വസ്തു ഓക്സിജനുമായി പ്രതിപ്രവർത്തിച്ച് വെളിച്ചം ഉണ്ടാക്കുന്നു.", ("ലൂസിഫെറിൻ + ഓക്സിജൻ", "A CHEMICAL REACTION MAKES THE LIGHT", GD), C([I("firefly", 0.5, 0.5, 6, anim="blink", glow="#fff36b", label=LB("ജീവനുള്ള വെളിച്ചം", "BIOLUMINESCENCE", GD, 420))], bg="night")),
        B("ഇതിനെ തണുത്ത വെളിച്ചം എന്ന് പറയും, കാരണം ഊർജ്ജം ഏതാണ്ട് മുഴുവനും വെളിച്ചമായി മാറും.", ("തണുത്ത വെളിച്ചം", "COLD LIGHT: ALMOST NO HEAT", SE)),
        B("ഒരു ബൾബാകട്ടെ ഊർജ്ജത്തിന്റെ വലിയൊരു ഭാഗം ചൂടാക്കി കളയും.", ("ബൾബ്: ചൂട് നഷ്ടം", "A BULB WASTES MOST AS HEAT", RD), C([I("bulb", 0.5, 0.45, 6, glow="#ff9a3c"), PT("bubbles", 20, [0.35, 0.15, 0.65, 0.5], "#ff9a3c", 7)], bg="warm")),
        B("വെളിച്ചം കൂടുന്നതും കാടുകൾ കുറയുന്നതും കാരണം മിന്നാമിനുങ്ങുകൾ കുറയുന്നു എന്ന് പഠനങ്ങൾ പറയുന്നു.", ("മിന്നാമിനുങ്ങുകൾ കുറയുന്നു", "STUDIES SAY THEY ARE DISAPPEARING", GR)),
        B("മൂന്നാമത്തേത് ഗോലി സോഡ.", ("3. ഗോലി സോഡ", "THE MARBLE SODA BOTTLE", OR), C([I("bottle", 0.5, 0.55, 7, label=LB("ഗോലി സോഡ", "GOLI SODA", OR, 360)), I("marble", 0.5, 0.2, 3, anim="pulse"), PT("bubbles", 26, [0.42, 0.35, 0.58, 0.8], "#fff", 6)], bg="dusk")),
        B("കുപ്പിയുടെ കഴുത്തിൽ ഒരു ഗോലി കുടുങ്ങിക്കിടക്കും.", ("കഴുത്തിൽ ഒരു ഗോലി", "A MARBLE SITS IN THE NECK", BL)),
        B("സോഡയ്ക്കുള്ളിലെ കാർബൺ ഡയോക്സൈഡ് വാതകത്തിന്റെ മർദ്ദം ആ ഗോലിയെ റബ്ബർ വളയത്തിലേക്ക് അമർത്തി കുപ്പി അടച്ചുവയ്ക്കുന്നു.", ("വാതക മർദ്ദം അടയ്ക്കുന്നു", "GAS PRESSURE SEALS THE BOTTLE", SE)),
        B("ഗോലി അകത്തേക്ക് തള്ളുമ്പോൾ കുപ്പി തുറക്കുന്നു, കൂടെ ഒരു ശൂ എന്ന ശബ്ദവും!", ("ശൂ!", "PUSH THE MARBLE, PSSSH!", GD)),
        B("ഈ കുപ്പി ആയിരത്തി എണ്ണൂറ്റി എഴുപത്തിരണ്ടിൽ ഹിറാം കോഡ് എന്ന ബ്രിട്ടീഷുകാരൻ രൂപകൽപ്പന ചെയ്തതാണ്.", ("1872 · ഹിറാം കോഡ്", "DESIGNED BY HIRAM CODD IN 1872", BR)),
        B("നാലാമത്തേത് കാസറ്റ്.", ("4. കാസറ്റ്", "THE CASSETTE", DK), C([I("cassette", 0.5, 0.5, 8, anim="float")], bg="dusk")),
        B("അതിനുള്ളിലെ നേർത്ത ടേപ്പിൽ ചെറിയ കാന്തകണങ്ങൾ പൂശിയിട്ടുണ്ട്.", ("കാന്തകണങ്ങൾ", "TINY MAGNETIC PARTICLES ON THE TAPE", RD), C([I("cassette", 0.3, 0.5, 6), I("magnet", 0.72, 0.5, 4, anim="float", label=LB("കാന്തം", "MAGNET", RD, 260))], bg="dusk")),
        B("റെക്കോർഡ് ചെയ്യുമ്പോൾ ശബ്ദത്തിനനുസരിച്ച് ആ കണങ്ങളുടെ കാന്തശക്തി മാറും.", ("ശബ്ദം → കാന്തം", "SOUND BECOMES A MAGNETIC PATTERN", OR)),
        B("പ്ലേ ചെയ്യുമ്പോൾ ആ മാറ്റം വീണ്ടും വൈദ്യുതിയും പിന്നെ ശബ്ദവുമായി മാറും.", ("കാന്തം → ശബ്ദം", "AND BACK INTO SOUND", SE)),
        B("അഞ്ചാമത്തേത് ഉപ്പ് തൊട്ട മാങ്ങ.", ("5. ഉപ്പുമാങ്ങ", "SALT ON RAW MANGO", LF), C([I("mango", 0.35, 0.5, 6), I("salt", 0.7, 0.5, 5, anim="float")], bg="dusk")),
        B("മാങ്ങയിൽ ഉപ്പ് തൊടുമ്പോൾ അതിലെ വെള്ളം പുറത്തേക്ക് വരും, ഇതിനെ ഓസ്മോസിസ് എന്ന് പറയും.", ("ഓസ്മോസിസ്", "OSMOSIS PULLS WATER OUT", SE), C([I("mango", 0.5, 0.5, 7), PT("bubbles", 18, [0.4, 0.3, 0.6, 0.75], "#8fd0f0", 6)], bg="dusk")),
        B("പുളിയും ഉപ്പും ചേരുമ്പോൾ നാവിൽ വെള്ളമൂറും.", ("വായിൽ വെള്ളമൂറും", "SOUR AND SALT MAKE YOUR MOUTH WATER", OR)),
        B("ആറാമത്തേത് മണ്ണെണ്ണ വിളക്ക്.", ("6. മണ്ണെണ്ണ വിളക്ക്", "THE KEROSENE LAMP", GD), C([I("lamp", 0.5, 0.52, 8, anim="float", glow="#ffe27a")], bg="night")),
        B("തിരിയിലെ ചെറിയ വിടവുകളിലൂടെ മണ്ണെണ്ണ മുകളിലേക്ക് കയറും, ഇതിനെ കാപ്പില്ലറി പ്രവർത്തനം എന്ന് പറയും.", ("തിരിയിലൂടെ മുകളിലേക്ക്", "THE WICK PULLS OIL UP", RD)),
        B("തീ കത്തുന്നത് മണ്ണെണ്ണയുടെ ആവിയാണ്, ദ്രാവകമല്ല.", ("കത്തുന്നത് ആവി", "THE VAPOUR BURNS, NOT THE LIQUID", OR)),
        B("ചിമ്മിനി വായുവിനെ വലിച്ച് തീ ആളിക്കത്തിക്കും.", ("ചിമ്മിനിയുടെ പണി", "THE CHIMNEY DRAWS AIR IN", BL)),
        B("ഓരോ ഓർമ്മയുടെയും പിന്നിൽ ഒരു ശാസ്ത്രം ഒളിച്ചിരിപ്പുണ്ട്.", ("ഓർമ്മയിൽ ശാസ്ത്രം", "SCIENCE HIDES IN EVERY MEMORY", BR)),
        B("ഈ ആറ് ഓർമ്മകളിൽ നിങ്ങൾ ഏറ്റവും കൂടുതൽ മിസ്സ് ചെയ്യുന്നത് ഏതാണ്?", None, {"kind": "outro", "p": {"ml": "ഈ ആറ് ഓർമ്മകളിൽ നിങ്ങൾ ഏറ്റവും കൂടുതൽ മിസ്സ് ചെയ്യുന്നത് ഏത്?", "en": "WHICH OF THESE SIX DO YOU MISS THE MOST?"}}),
        B("താഴെ കമന്റ് ചെയ്യൂ, ഇതുപോലുള്ള വീഡിയോകൾക്കായി സയൻസ് ചായ സബ്സ്ക്രൈബ് ചെയ്യൂ."),
    ],
}
FACTS = [
    "Petrichor was named by two CSIRO researchers in a 1964 Nature article; plant oils and the bacterial compound geosmin make the smell, and MIT researchers (2015) showed raindrops throw it into the air as tiny aerosols (Met Office; Smithsonian; Popular Science).",
    "Fireflies make 'cold light' by oxidising luciferin with the enzyme luciferase; the reaction is almost 100% efficient (Britannica; Scientific American).",
    "The Codd-neck bottle was designed by Hiram Codd in 1872; gas pressure presses the marble against a washer to seal the fizz (Wikipedia: Codd-neck bottle, Banta).",
    "Cassette tape stores sound as a pattern of magnetised particles; salt draws water out of fruit by osmosis; a kerosene lamp wick lifts oil by capillary action and the vapour burns.",
]
VIDEOS = [LONG]
