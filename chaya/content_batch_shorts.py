"""Science Chaya: six nostalgia and village Shorts (petrichor, goli soda, chenda, banana ripening, zero shadow day, fireflies)."""
from chaya.content_monsoon import BL, BR, DK, GD, GR, LF, OR, RD, SE, B
from chaya.dsl import GROUND, LB, PT, RINGS, C, I, R, T
from chaya.scenes import lab

SUB = "കൂടുതൽ കാണാൻ സബ്സ്ക്രൈബ് ചെയ്യൂ"


def short(vid, title_ml, title_en, thumb, beats):
    return {"id": vid, "orient": "tall", "mood": "curious", "title_ml": title_ml, "title_en": title_en, "thumb": thumb, "beats": beats}


def outro(ml, en, text):
    return B(text, None, {"kind": "outro", "p": {"ml": ml, "en": en, "sub": SUB}})


PETRICHOR = short("petrichor_s", "ആദ്യ മഴയുടെ മണം എവിടെ നിന്ന്? #Shorts", "Where does the smell of the first rain come from?", {"ml": "മഴയുടെ മണം!", "en": "PETRICHOR", "hero": "compose"}, [
    B("ആദ്യ മഴ പെയ്യുമ്പോൾ മണ്ണിന്റെ ആ മണം എവിടെ നിന്നാണ്?", ("മഴയുടെ മണം", "THE SMELL OF THE FIRST RAIN", BL), C([R(0, 0.72, 1, 0.28, "#8a5a36"), PT("rain", 40, [0.05, 0.1, 0.95, 0.72], "#4aa3d8", 6), I("cloudDark", 0.5, 0.18, 6)], bg="storm")),
    B("ഇതിന് പെട്രിക്കോർ എന്ന് പറയും.", ("പെട്രിക്കോർ", "PETRICHOR", DK)),
    B("വേനലിൽ ചെടികൾ ഒരു തരം എണ്ണ മണ്ണിലേക്ക് പുറത്തുവിടും.", ("ചെടികളുടെ എണ്ണ", "PLANTS RELEASE AN OIL", LF), C([R(0, 0.65, 1, 0.35, "#8a5a36"), I("tree", 0.5, 0.52, 6), PT("bubbles", 16, [0.4, 0.62, 0.6, 0.95], "#e8c35f", 7)], bg="sky")),
    B("മണ്ണിലെ ബാക്ടീരിയകൾ ജിയോസ്മിൻ എന്ന വസ്തു ഉണ്ടാക്കും.", ("ജിയോസ്മിൻ", "SOIL BACTERIA MAKE GEOSMIN", OR)),
    B("മഴത്തുള്ളി വീഴുമ്പോൾ ചെറിയ കുമിളകൾ ആ മണം വായുവിലേക്ക് തെറിപ്പിക്കും.", ("മണം തെറിക്കുന്നു", "DROPS FLICK THE SMELL INTO THE AIR", SE), C([R(0, 0.7, 1, 0.3, "#8a5a36"), PT("rain", 12, [0.3, 0.1, 0.7, 0.7], "#4aa3d8", 8), PT("bubbles", 28, [0.3, 0.3, 0.7, 0.7], "#f3e2b8", 5)], bg="storm")),
    B("ചെറിയ മഴയിലാണ് ഈ മണം ഏറ്റവും കൂടുതൽ.", ("ചെറിയ മഴ, വലിയ മണം", "LIGHT RAIN SMELLS STRONGEST", BL)),
    outro("മണ്ണിന്റെ മണം, ശാസ്ത്രത്തിന്റെ മണം!", "THE SMELL OF SCIENCE", "മണ്ണിന്റെ മണം, ശാസ്ത്രത്തിന്റെ മണം!"),
])
GOLI = short("goli_s", "ഗോലി സോഡയുടെ കുപ്പി അടയുന്നത് എങ്ങനെ? #Shorts", "How does a goli soda bottle stay shut?", {"ml": "ഗോലി സോഡയുടെ രഹസ്യം", "en": "THE MARBLE BOTTLE", "hero": "compose"}, [
    B("ഗോലി സോഡയുടെ കുപ്പി എങ്ങനെയാണ് അടഞ്ഞിരിക്കുന്നത്?", ("ഗോലി സോഡ", "HOW IS IT SEALED?", OR), C([I("bottle", 0.5, 0.55, 8, label=LB("ഗോലി സോഡ", "GOLI SODA", OR, 360)), I("marble", 0.5, 0.2, 3.4, anim="pulse"), PT("bubbles", 26, [0.42, 0.35, 0.58, 0.8], "#fff", 7)], bg="dusk")),
    B("അടപ്പില്ല, കഴുത്തിൽ ഒരു ഗോലി മാത്രം!", ("ഒരു ഗോലി മാത്രം", "JUST A MARBLE", BL)),
    B("കുപ്പിക്കുള്ളിലെ വാതകത്തിന്റെ മർദ്ദം ആ ഗോലിയെ മുകളിലേക്ക് അമർത്തുന്നു.", ("വാതക മർദ്ദം", "GAS PRESSURE PUSHES IT UP", SE)),
    B("ഗോലി ഒരു റബ്ബർ വളയത്തിൽ ഉറച്ച് കുപ്പി അടയ്ക്കുന്നു.", ("റബ്ബർ വളയം", "IT PRESSES AGAINST A RUBBER RING", DK)),
    B("ഗോലി അകത്തേക്ക് തള്ളിയാൽ കുപ്പി തുറക്കും, ശൂ!", ("ശൂ!", "PUSH IT IN, PSSSH!", GD)),
    B("ഈ കുപ്പി ആയിരത്തി എണ്ണൂറ്റി എഴുപത്തിരണ്ടിൽ ഹിറാം കോഡ് എന്ന ബ്രിട്ടീഷുകാരൻ രൂപകൽപ്പന ചെയ്തതാണ്.", ("1872 · ഹിറാം കോഡ്", "DESIGNED BY HIRAM CODD", BR)),
    outro("ഒരു ഗോലി, ഒരു വലിയ ആശയം!", "A MARBLE AND A BIG IDEA", "ഒരു ഗോലി, ഒരു വലിയ ശാസ്ത്രം!"),
])
CHENDA = short("chenda_s", "ചെണ്ടമേളം നെഞ്ചിൽ കൊള്ളുന്നത് എന്തുകൊണ്ട്? #Shorts", "Why does the chenda hit you in the chest?", {"ml": "ചെണ്ടയുടെ ശാസ്ത്രം", "en": "THE CHENDA", "hero": "compose"}, [
    B("പൂരത്തിന് ചെണ്ടമേളം കേൾക്കുമ്പോൾ നെഞ്ചിൽ കൊള്ളുന്നത് എന്തുകൊണ്ടാണ്?", ("ചെണ്ടമേളം", "WHY DOES IT HIT YOUR CHEST?", RD), C([I("chenda", 0.5, 0.5, 8, anim="shake"), RINGS(0.5, 0.5, "#c8442f", speed=0.7, r=0.6)], bg="dusk")),
    B("ചെണ്ട പ്ലാവിൻ തടികൊണ്ട് ഉണ്ടാക്കിയ ഒരു ഉരുളയാണ്.", ("പ്ലാവിൻ തടി", "A CYLINDER OF JACKFRUIT WOOD", GD), C([I("chenda", 0.5, 0.5, 8), I("jackfruit", 0.2, 0.8, 3, anim="float")], bg="dusk")),
    B("അതിന്റെ രണ്ട് വശത്തും തുകൽ മുറുക്കിക്കെട്ടിയിരിക്കുന്നു.", ("രണ്ട് വശത്തും തുകൽ", "SKIN STRETCHED ON BOTH ENDS", BR)),
    B("ഒരു വശത്ത് കനം കുറഞ്ഞ തുകലും മറ്റേ വശത്ത് പല അടുക്കുള്ള കനമുള്ള തുകലുമാണ്.", ("കനം കുറഞ്ഞതും കൂടിയതും", "ONE THIN HEAD, ONE LAYERED HEAD", OR)),
    B("രണ്ട് കോലുകൊണ്ട് കൊട്ടുമ്പോൾ ഉറച്ച ഉച്ചത്തിലുള്ള ശബ്ദം ഉണ്ടാകുന്നു.", ("ഉറച്ച ശബ്ദം", "A SHARP, LOUD SOUND", RD)),
    B("മുറുകിയ തുകൽ വേഗത്തിൽ വിറയ്ക്കുകയും ആ വിറയൽ വായുവിനെ തള്ളുകയും ചെയ്യും.", ("വിറയൽ → ശബ്ദം", "THE SKIN VIBRATES AND PUSHES THE AIR", SE), C([I("chenda", 0.5, 0.5, 8, anim="shake"), RINGS(0.5, 0.5, "#146a85", speed=1.0, r=0.7)], bg="dusk")),
    B("ഒരുപാട് ചെണ്ടകൾ ഒരേ താളത്തിൽ കൊട്ടുമ്പോൾ ശബ്ദം കൂടിച്ചേർന്ന് കൂടുതൽ ഉച്ചത്തിലാകും.", ("ഒരേ താളം = വലിയ ശബ്ദം", "MANY DRUMS, ONE BEAT, A HUGE SOUND", GD)),
    outro("നെഞ്ചിൽ കൊള്ളുന്ന ആ താളം!", "THAT BEAT YOU FEEL IN YOUR CHEST", "അതാണ് നെഞ്ചിൽ കൊള്ളുന്ന ആ താളം!"),
])
BANANA = short("banana_s", "പഴം പെട്ടെന്ന് പഴുക്കാൻ എന്ത് ചെയ്യണം? #Shorts", "Why do fruits ripen faster together?", {"ml": "പഴം പഴുക്കുന്ന രഹസ്യം", "en": "ETHYLENE", "hero": "compose"}, [
    B("പച്ച വാഴക്കായ പെട്ടെന്ന് പഴുപ്പിക്കാൻ പഴുത്ത പഴത്തിനൊപ്പം വെച്ചാൽ മതി എന്ന് കേട്ടിട്ടുണ്ടോ?", ("പഴുപ്പിക്കാനുള്ള വിദ്യ", "THE RIPENING TRICK", GD), C([I("banana", 0.35, 0.5, 6, anim="float"), I("banana", 0.65, 0.55, 6, anim="float")], bg="dusk")),
    B("ഇതിന് പിന്നിൽ എഥിലീൻ എന്ന വാതകമാണ്.", ("എഥിലീൻ വാതകം", "THE GAS IS ETHYLENE", OR)),
    B("പഴുക്കുന്ന പഴങ്ങൾ ഈ വാതകം പുറത്തുവിടും.", ("പഴങ്ങൾ വാതകം വിടും", "RIPENING FRUIT RELEASES IT", LF), C([I("banana", 0.5, 0.65, 6), PT("bubbles", 26, [0.3, 0.1, 0.7, 0.6], "#cfe9a6", 7)], bg="dusk")),
    B("ഈ വാതകം അടുത്തുള്ള പഴങ്ങളോട് പഴുക്കാൻ തുടങ്ങാൻ സൂചന നൽകും.", ("സൂചന നൽകുന്നു", "IT SIGNALS NEIGHBOURS TO RIPEN", BL)),
    B("വാഴപ്പഴം, മാങ്ങ, ചക്ക തുടങ്ങിയവ ഇങ്ങനെ പഴുക്കുന്ന പഴങ്ങളാണ്.", ("വാഴപ്പഴം · മാങ്ങ · ചക്ക", "BANANA, MANGO, JACKFRUIT", BR), C([I("banana", 0.25, 0.5, 4.5, anim="float"), I("mango", 0.5, 0.5, 4.5, anim="float"), I("jackfruit", 0.75, 0.5, 4.5, anim="float")], bg="dusk")),
    B("അടച്ച പാത്രത്തിലോ കടലാസ് സഞ്ചിയിലോ വാതകം പുറത്തുപോകാതെ നിൽക്കും, അതുകൊണ്ട് പഴുപ്പ് വേഗത്തിലാകും.", ("അടച്ചുവെക്കുക", "A CLOSED BAG KEEPS THE GAS IN", GD)),
    B("സ്ട്രോബെറി, മുന്തിരി, നാരങ്ങ പോലുള്ളവ ഇങ്ങനെ പഴുക്കുന്നവയല്ല.", ("എല്ലാ പഴങ്ങളും അല്ല", "STRAWBERRY, GRAPES AND LIME DO NOT", GR)),
    outro("ഒരു വാതകം, ഒരു കൂട്ടം പഴങ്ങൾ!", "ONE GAS, A BOWL OF FRUIT", "ഒരു ചെറിയ വാതകം, വലിയ മാറ്റം!"),
])
ZERO = short("zeroshadow_s", "ഉച്ചയ്ക്ക് നിഴൽ കാണാതാകുന്ന ദിവസം! #Shorts", "The day your shadow disappears at noon", {"ml": "നിഴൽ ഇല്ലാത്ത ദിവസം", "en": "ZERO SHADOW DAY", "hero": "compose"}, [
    B("ഉച്ചയ്ക്ക് ഒരു ദിവസം നിങ്ങളുടെ നിഴൽ കാണാതാകും, ഇത് മാജിക് അല്ല!", ("നിഴൽ കാണാതാകും", "THE DAY YOUR SHADOW VANISHES", DK), C([I("sun", 0.5, 0.1, 5, anim="spin", speed=20), I("person", 0.5, 0.65, 5), GROUND("#c9a35e", 0.85)], bg="sky")),
    B("ഇതിനെ സീറോ ഷാഡോ ഡേ എന്ന് പറയും.", ("സീറോ ഷാഡോ ഡേ", "ZERO SHADOW DAY", BR)),
    B("സൂര്യൻ നമ്മുടെ തലയ്ക്ക് നേരെ മുകളിൽ വരുന്ന ദിവസമാണ് ഇത്.", ("സൂര്യൻ നേരെ മുകളിൽ", "THE SUN IS DIRECTLY OVERHEAD", OR)),
    B("അപ്പോൾ ഒരു കോലിന്റെ നിഴൽ അതിന്റെ ചുവട്ടിൽ തന്നെ ഒതുങ്ങും.", ("നിഴൽ ചുവട്ടിൽ", "A STICK'S SHADOW SHRINKS TO ITS FOOT", GD), C([I("sun", 0.5, 0.1, 5), R(0.497, 0.4, 0.006, 0.45, "#4a2a17"), GROUND("#c9a35e", 0.85), T("നിഴൽ = 0", 0.5, 0.86, 90)], bg="sky")),
    B("ഉഷ്ണമേഖലയിൽ, അതായത് കർക്കടകരേഖയ്ക്കും മകരരേഖയ്ക്കും ഇടയിൽ, ഇത് വർഷത്തിൽ രണ്ട് തവണ സംഭവിക്കും.", ("വർഷത്തിൽ രണ്ട് തവണ", "TWICE A YEAR BETWEEN THE TROPICS", SE)),
    B("കേരളത്തിൽ ഏപ്രിൽ മാസത്തിലും ഓഗസ്റ്റ് സെപ്റ്റംബർ സമയത്തും ഇത് കാണാം, ദിവസം സ്ഥലം അനുസരിച്ച് മാറും.", ("ഏപ്രിൽ, ഓഗസ്റ്റ്–സെപ്റ്റംബർ", "APRIL, AND AUGUST–SEPTEMBER", LF)),
    outro("ഒരു കോലും വെയിലും ഉച്ചയും!", "A STICK, THE SUN AND NOON", "അടുത്ത തവണ ഒരു കോലും ഉച്ചവെയിലും റെഡിയാക്കി വച്ചോളൂ!"),
])
FIREFLY = short("firefly_s", "മിന്നാമിനുങ്ങിന്റെ വെളിച്ചത്തിന് ചൂടില്ലാത്തത് എന്തുകൊണ്ട്? #Shorts", "Why is a firefly's light cold?", {"ml": "തണുത്ത വെളിച്ചം", "en": "FIREFLIES", "hero": "compose"}, [
    B("മിന്നാമിനുങ്ങിന്റെ വെളിച്ചത്തിന് ചൂടില്ലാത്തത് എന്തുകൊണ്ടാണ്?", ("ചൂടില്ലാത്ത വെളിച്ചം", "WHY IS THE LIGHT COLD?", DK), C([I("moon", 0.82, 0.12, 2.6), GROUND("#12301f", 0.82), I("tree", 0.2, 0.7, 5), I("tree", 0.8, 0.68, 5), PT("fireflies", 26, [0.05, 0.3, 0.95, 0.8], "#fff36b", 8)], bg="night")),
    B("അതിന്റെ ശരീരത്തിൽ ലൂസിഫെറിൻ എന്ന വസ്തു ഉണ്ട്.", ("ലൂസിഫെറിൻ", "THE CHEMICAL LUCIFERIN", GD), C([I("firefly", 0.5, 0.5, 9, anim="blink", glow="#fff36b")], bg="night")),
    B("അത് ഓക്സിജനുമായി ചേർന്ന് വെളിച്ചം ഉണ്ടാക്കുന്നു.", ("+ ഓക്സിജൻ = വെളിച്ചം", "IT REACTS WITH OXYGEN", SE)),
    B("ഈ രാസപ്രവർത്തനത്തിൽ ഊർജ്ജം ഏതാണ്ട് മുഴുവനും വെളിച്ചമാകും.", ("ഏതാണ്ട് മുഴുവനും വെളിച്ചം", "ALMOST ALL THE ENERGY BECOMES LIGHT", OR)),
    B("അതുകൊണ്ടാണ് ഇതിനെ തണുത്ത വെളിച്ചം എന്ന് പറയുന്നത്.", ("തണുത്ത വെളിച്ചം", "COLD LIGHT", BL)),
    B("ഒരു ബൾബിൽ ഊർജ്ജത്തിന്റെ വലിയൊരു ഭാഗം ചൂടായി പോകും.", ("ബൾബ്: ചൂട് നഷ്ടം", "A BULB WASTES MOST AS HEAT", RD), C([I("bulb", 0.5, 0.45, 8, glow="#ff9a3c"), PT("bubbles", 20, [0.35, 0.15, 0.65, 0.5], "#ff9a3c", 8)], bg="warm")),
    outro("പ്രകൃതിയുടെ തണുത്ത ബൾബ്!", "NATURE'S COLD BULB", "പ്രകൃതിയുടെ സ്വന്തം തണുത്ത ബൾബ്!"),
])
# richer scene: the Sun overhead and a stick without a shadow
lab(ZERO, 0, 5, "sunshadow", {"sun": 0, "noon": 3}, [(3, "നിഴൽ ചുവട്ടിൽ ഒതുങ്ങുന്നു", "THE SHADOW SHRINKS TO ITS FOOT", 500, 300)])

VIDEOS = [PETRICHOR, GOLI, CHENDA, BANANA, ZERO, FIREFLY]
FACTS = [
    "Petrichor: plant oils and the soil-bacteria compound geosmin make the smell; raindrops throw it into the air as tiny aerosols (Met Office; Smithsonian).",
    "The Codd-neck bottle was designed by Hiram Codd in 1872; gas pressure seals the marble against a ring (Wikipedia: Codd-neck bottle).",
    "The chenda is a cylindrical drum of jackfruit wood with skin on both ends, played with two sticks (Kerala Tourism; Wikipedia: Chenda).",
    "Ripening fruit releases ethylene; climacteric fruits such as banana, mango and tomato ripen in response, while strawberry, grape and citrus do not (USDA; PMC review).",
    "Zero Shadow Day happens twice a year for places between the Tropic of Cancer and the Tropic of Capricorn when the Sun is directly overhead at noon (Astronomical Society outreach pages); the exact date depends on latitude.",
    "Firefly light comes from luciferin reacting with oxygen and is almost 100% efficient, so it gives almost no heat (Britannica; Scientific American).",
]
