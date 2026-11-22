"""Science Chaya: five science secrets in a Kerala kitchen (long)."""
from chaya.content_monsoon import BL, BR, DK, GD, GR, LF, OR, RD, SE, B
from chaya.dsl import LB, PT, C, I, T

LONG = {
    "id": "kitchen_long", "orient": "wide", "mood": "curious",
    "title_ml": "അടുക്കളയിലെ അഞ്ച് ശാസ്ത്ര രഹസ്യങ്ങൾ: ഇഡ്ഡലി മാവ് മുതൽ പ്രഷർ കുക്കർ വരെ",
    "title_en": "Five science secrets in a Kerala kitchen: from idli batter to the pressure cooker",
    "thumb": {"ml": "അടുക്കളയിലെ ശാസ്ത്രം", "en": "KITCHEN SCIENCE", "hero": "compose"},
    "comment": "ഇതിൽ ഏത് അടുക്കള രഹസ്യമാണ് നിങ്ങൾക്ക് പുതിയ അറിവായത്?",
    "beats": [
        B("ഇഡ്ഡലി മാവ് പൊങ്ങുന്നത്, തൈര് ഉറയുന്നത്, കുക്കർ വിസിൽ അടിക്കുന്നത്, അടുക്കളയിൽ എപ്പോഴും ശാസ്ത്രം നടക്കുന്നുണ്ട്.", ("അടുക്കളയിലെ ശാസ്ത്രം", "SCIENCE HAPPENS IN EVERY KITCHEN", BR), C([I("bowl", 0.2, 0.5, 3.4, anim="float"), I("cooker", 0.4, 0.5, 3.4, anim="float"), I("onion", 0.6, 0.5, 3.4, anim="float"), I("bottle", 0.8, 0.5, 3, anim="float")], bg="dusk")),
        B("ഒന്നാമത്തേത് ഇഡ്ഡലി മാവ്.", ("1. ഇഡ്ഡലി മാവ്", "IDLI BATTER", OR), C([I("bowl", 0.5, 0.5, 6.5, label=LB("ഇഡ്ഡലി മാവ്", "IDLI BATTER", OR, 400)), PT("bubbles", 24, [0.4, 0.2, 0.6, 0.55], "#fffaf0", 7)], bg="dusk")),
        B("അരച്ച മാവ് രാത്രി വെച്ചാൽ രാവിലെ പൊങ്ങിയിരിക്കും.", ("രാത്രി വെച്ചാൽ രാവിലെ പൊങ്ങും", "LEFT OVERNIGHT, IT RISES", BL)),
        B("ഇതിന് കാരണം ല്യൂക്കോനോസ്റ്റോക് മെസെന്ററോയിഡസ് എന്ന ലാക്റ്റിക് ആസിഡ് ബാക്ടീരിയയാണ്.", ("ലാക്റ്റിക് ആസിഡ് ബാക്ടീരിയ", "LEUCONOSTOC MESENTEROIDES", DK)),
        B("അവ പുളിപ്പും കാർബൺ ഡയോക്സൈഡ് വാതകവും ഉണ്ടാക്കും.", ("പുളിപ്പും വാതകവും", "SOURNESS AND CARBON DIOXIDE", SE), C([I("bowl", 0.5, 0.65, 7), PT("bubbles", 40, [0.35, 0.1, 0.65, 0.6], "#fffaf0", 9, speed=0.5)], bg="dusk")),
        B("ആ വാതകക്കുമിളകളാണ് മാവിനെ പൊക്കി ഇഡ്ഡലിയെ മൃദുവാക്കുന്നത്.", ("കുമിളകൾ = മൃദുവായ ഇഡ്ഡലി", "BUBBLES MAKE IT SOFT", LF)),
        B("രണ്ടാമത്തേത് തൈര്.", ("2. തൈര്", "CURD", GD), C([I("bowl", 0.5, 0.5, 6.5, glow="#fff", label=LB("തൈര്", "CURD", GD, 300))], bg="dusk")),
        B("ഒരു സ്പൂൺ പഴയ തൈര് ഇളംചൂടുള്ള പാലിൽ ചേർത്തുവച്ചാൽ രാവിലെ തൈരാകും.", ("ഒരു സ്പൂൺ മതി", "ONE SPOON OF OLD CURD IS ENOUGH", BR)),
        B("ആ തൈരിലെ ബാക്ടീരിയകൾ പാലിലെ പഞ്ചസാരയെ ലാക്റ്റിക് ആസിഡാക്കി മാറ്റും.", ("പഞ്ചസാര → ആസിഡ്", "BACTERIA TURN MILK SUGAR INTO ACID", OR)),
        B("അമ്ലത കൂടുമ്പോൾ പാലിലെ മാംസ്യം കട്ടപിടിച്ച് തൈരാകും.", ("മാംസ്യം കട്ടപിടിക്കുന്നു", "THE ACID CLUMPS THE MILK PROTEIN", RD)),
        B("പാൽ ഇളംചൂടിലായിരിക്കണം, നന്നായി തണുത്താൽ ബാക്ടീരിയകൾ പതുക്കെയാകും.", ("ഇളംചൂട് വേണം", "KEEP IT LUKEWARM", GD)),
        B("മൂന്നാമത്തേത് വെളിച്ചെണ്ണ.", ("3. വെളിച്ചെണ്ണ", "COCONUT OIL", LF), C([I("bottle", 0.5, 0.5, 6), T("വെളിച്ചെണ്ണ", 0.5, 0.86, 90)], bg="dusk")),
        B("ഇരുപത്തിനാല്, ഇരുപത്തിയഞ്ച് ഡിഗ്രി സെൽഷ്യസിൽ താഴെ വെളിച്ചെണ്ണ കട്ടിയാകും.", ("24–25 °C ന് താഴെ കട്ടിയാകും", "IT SOLIDIFIES BELOW ABOUT 24 °C", BL), {"kind": "stat", "p": {"value": 24, "suffix": " °C", "ml": "ഇതിന് താഴെ കട്ടിയാകും", "en": "COCONUT OIL SOLIDIFIES BELOW ABOUT THIS", "icon": "thermo"}}),
        B("ലോറിക് ആസിഡ് കൂടുതലുള്ളതുകൊണ്ടാണ് ഇതിന്റെ ഉരുകൽ നില ഇത്ര കുറവ്.", ("ലോറിക് ആസിഡ്", "RICH IN LAURIC ACID", DK)),
        B("അതുകൊണ്ട് തണുത്ത പ്രഭാതത്തിൽ കുപ്പിയിൽ വെളിച്ചെണ്ണ കട്ടിയാകുന്നത് കേടായതല്ല, സാധാരണമാണ്.", ("കേടല്ല, സാധാരണം", "NOT SPOILED, JUST COLD", GR)),
        B("നാലാമത്തേത് പ്രഷർ കുക്കർ.", ("4. പ്രഷർ കുക്കർ", "THE PRESSURE COOKER", RD), C([I("cooker", 0.5, 0.5, 6.5, anim="shake"), PT("bubbles", 22, [0.43, 0.1, 0.57, 0.4], "#fff", 8)], bg="dusk")),
        B("സാധാരണ വെള്ളം നൂറ് ഡിഗ്രിയിൽ തിളയ്ക്കും.", ("100 °C ൽ തിളയ്ക്കും", "WATER BOILS AT 100 °C", SE)),
        B("കുക്കറിൽ ആവി പുറത്തുപോകാതെ അടച്ചുവയ്ക്കുമ്പോൾ ഉള്ളിലെ മർദ്ദം കൂടും.", ("മർദ്ദം കൂടും", "TRAPPED STEAM RAISES THE PRESSURE", OR)),
        B("മർദ്ദം കൂടുമ്പോൾ വെള്ളം ഏകദേശം നൂറ്റി ഇരുപത്തിയൊന്ന് ഡിഗ്രി വരെ ചൂടാകും.", ("≈ 121 °C", "BOILING POINT RISES TO ABOUT 121 °C", RD), {"kind": "stat", "p": {"value": 121, "suffix": " °C", "ml": "കുക്കറിനുള്ളിലെ ചൂട്", "en": "AT ABOUT 15 PSI OVER ATMOSPHERIC", "icon": "thermo"}}),
        B("ചൂട് കൂടുതലായതുകൊണ്ട് അരിയും പയറും വേഗം വേവും, വിസിൽ അടിക്കുന്നത് അധികം ആവി പുറത്തുവിടുന്നതാണ്.", ("വേഗം വേവും", "HOTTER MEANS FASTER COOKING", GD)),
        B("അഞ്ചാമത്തേത് ഉള്ളി.", ("5. ഉള്ളി", "THE ONION", GD), C([I("onion", 0.5, 0.5, 6.5, anim="float"), T("ഉള്ളി", 0.5, 0.86, 90)], bg="dusk")),
        B("ഉള്ളി മുറിക്കുമ്പോൾ അതിലെ കോശങ്ങൾ പൊട്ടി എൻസൈമുകൾ പുറത്തുവരും.", ("കോശങ്ങൾ പൊട്ടുന്നു", "CUTTING RELEASES ENZYMES", OR)),
        B("അവ ഒരു ആവിയായ വസ്തു ഉണ്ടാക്കും, സിൻ പ്രൊപ്പനെത്തിയൽ എസ് ഓക്സൈഡ്.", ("ഒരു ആവിയായ വസ്തു", "A VAPOUR: SYN-PROPANETHIAL-S-OXIDE", RD), C([I("onion", 0.5, 0.65, 7), PT("bubbles", 26, [0.4, 0.15, 0.6, 0.55], "#e9b6d6", 7)], bg="dusk")),
        B("അത് കണ്ണിൽ തട്ടുമ്പോൾ എരിച്ചിലുണ്ടായി കണ്ണ് നിറയും.", ("കണ്ണ് നിറയുന്നു", "IT STINGS, SO YOUR EYES WATER", BL)),
        B("നമ്മുടെ അടുക്കള ഒരു കൊച്ചു ലാബാണ്.", ("അടുക്കള = ലാബ്", "YOUR KITCHEN IS A LAB", BR)),
        B("ഇതിൽ ഏത് അടുക്കള രഹസ്യമാണ് നിങ്ങൾക്ക് പുതിയ അറിവായത്?", None, {"kind": "outro", "p": {"ml": "ഇതിൽ ഏത് അടുക്കള രഹസ്യമാണ് നിങ്ങൾക്ക് പുതിയ അറിവായത്?", "en": "WHICH KITCHEN SECRET WAS NEW TO YOU?"}}),
        B("താഴെ കമന്റ് ചെയ്യൂ, ഇതുപോലുള്ള വീഡിയോകൾക്കായി സയൻസ് ചായ സബ്സ്ക്രൈബ് ചെയ്യൂ."),
    ],
}
FACTS = [
    "Idli batter rises because heterofermentative lactic acid bacteria, mainly Leuconostoc mesenteroides, make acid and carbon dioxide (Mattada and Mukherjee study, 1965; reviews on PMC).",
    "Curd forms when bacteria turn milk sugar into lactic acid and the acid clumps the milk protein.",
    "Coconut oil is solid below about 24-25 degrees Celsius because of its high lauric acid content (Wikipedia: Coconut oil).",
    "A pressure cooker at about 15 psi above atmospheric pressure raises water's boiling point to about 121 degrees Celsius (Wikipedia: Pressure cooking; HyperPhysics).",
    "Cut onions release syn-propanethial-S-oxide, made by the enzyme lachrymatory factor synthase, which irritates the eyes (ACS Chemical Biology 2017; Wikipedia).",
]
VIDEOS = [LONG]
