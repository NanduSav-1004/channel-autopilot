"""Science Chaya batch 6: spice and food (black pepper long; turmeric and lime, chilli, puttu, pappadam, cardamom, pickle Shorts)."""
from chaya.quick import TX, S, lg, sh

PEPPER = lg(
    "pepper_long", "കുരുമുളക്: കേരളത്തെ ലോകം തേടിവന്നത് എന്തിന്? | കറുത്ത പൊന്നിന്റെ ശാസ്ത്രം", "Black pepper: why did the world sail to Kerala? The science of black gold",
    "കറുത്ത പൊന്ന്!", "THE SCIENCE OF PEPPER", "നിങ്ങളുടെ അടുക്കളയിൽ കുരുമുളക് ഏതൊക്കെ കറികളിൽ ഉപയോഗിക്കാറുണ്ട്?", "WHICH DISHES DO YOU USE PEPPER IN?",
    [
        ("ഒരു കാലത്ത് കുരുമുളകിന് സ്വർണ്ണത്തോളം വിലയുണ്ടായിരുന്നു.", "കുരുമുളക് = കറുത്ത പൊന്ന്", "ONCE WORTH ITS WEIGHT IN GOLD", S(["leaf", "boat"], "dusk", label=("കുരുമുളക്", "BLACK PEPPER"))),
        ("ആ കുരുമുളകിന്റെ ജന്മനാട് നമ്മുടെ കേരളമാണ്.", "ജന്മനാട് കേരളം", "ITS HOME IS KERALA"),
        ("ഇന്ന് ആ കുരുമുളകിന്റെ ശാസ്ത്രവും ചരിത്രവും നോക്കാം.", "ശാസ്ത്രവും ചരിത്രവും", "THE SCIENCE AND THE STORY", TX("കുരുമുളക്", "BLACK PEPPER", "leaf", "#4a2a17")),
        ("കുരുമുളക് ചെടിയുടെ ശാസ്ത്രീയ നാമം പൈപ്പർ നിഗ്രം എന്നാണ്.", "പൈപ്പർ നിഗ്രം", "PIPER NIGRUM"),
        ("ഇത് ഒരു വള്ളിച്ചെടിയാണ്, മരങ്ങളിൽ പടർന്നുകയറി വളരും.", "പടർന്നുകയറുന്ന വള്ളി", "A CLIMBING VINE", S(["tree", "leaf"], "sky")),
        ("പശ്ചിമഘട്ടത്തിലെ ചൂടും ഈർപ്പവും മഴയും ഇതിന് ഏറ്റവും അനുയോജ്യമാണ്.", "പശ്ചിമഘട്ടത്തിന്റെ സമ്മാനം", "A GIFT OF THE WESTERN GHATS", S(["mountain", "cloudDark"], "storm", ("rain", 30, "#4aa3d8"))),
        ("ചെടിയിൽ ചെറിയ പച്ച മണികൾ കുലകളായി വിടരും.", "പച്ച മണികൾ", "GREEN BERRIES IN BUNCHES"),
        ("പഴുക്കുമ്പോൾ ആ മണികൾ ചുവപ്പാകും.", "പഴുക്കുമ്പോൾ ചുവപ്പ്", "RED WHEN RIPE"),
        ("കറുത്ത കുരുമുളക് ഉണ്ടാക്കാൻ മുഴുവൻ പഴുക്കുന്നതിന് മുൻപ് പറിച്ച് ഉണക്കും.", "പറിച്ച് ഉണക്കും", "PICKED EARLY AND DRIED"),
        ("ഉണങ്ങുമ്പോൾ മണിയുടെ തൊലിയിലെ എൻസൈമുകൾ പ്രവർത്തിച്ച് അത് കറുത്തു ചുളിയും.", "എൻസൈമുകൾ കറുപ്പിക്കുന്നു", "ENZYMES TURN IT BLACK", S(["bowl"], "dusk", ("bubbles", 12, "#4a2a17"))),
        ("പഴുത്ത മണികളുടെ തൊലി കളഞ്ഞാണ് വെള്ള കുരുമുളക് ഉണ്ടാക്കുന്നത്.", "വെള്ള കുരുമുളക്", "WHITE PEPPER HAS NO HUSK"),
        ("ഇനി എരിവ് എങ്ങനെ വരുന്നു എന്ന് നോക്കാം.", "എരിവ് എങ്ങനെ?", "WHERE THE HEAT COMES FROM", TX("എരിവ് എങ്ങനെ?", "WHERE IS THE HEAT?", "leaf", "#c8442f")),
        ("കുരുമുളകിന്റെ എരിവിന് കാരണം പൈപ്പറിൻ എന്ന രാസവസ്തുവാണ്.", "പൈപ്പറിൻ", "THE CHEMICAL PIPERINE"),
        ("മുളകിലെ എരിവ് ക്യാപ്സെയ്സിൻ ആണ്, അത് കുരുമുളകിന്റെ എരിവിൽ നിന്ന് വേറെയാണ്.", "മുളകിൽ ക്യാപ്സെയ്സിൻ", "CHILLI USES CAPSAICIN"),
        ("പൈപ്പറിൻ നമ്മുടെ നാക്കിലെ വേദന അറിയുന്ന ഭാഗങ്ങളെ ഉണർത്തുന്നു.", "നാക്കിലെ സെൻസറുകൾ", "IT TRIGGERS PAIN SENSORS"),
        ("അതുകൊണ്ട് എരിവ് ഒരു രുചിയല്ല, ഒരു ചെറിയ വേദനയുടെ തോന്നലാണ്.", "എരിവ് = വേദന", "HEAT IS A SENSATION, NOT A TASTE"),
        ("മഞ്ഞളിനോടൊപ്പം കുരുമുളക് ചേർക്കുമ്പോൾ മഞ്ഞളിലെ കുർക്കുമിൻ ശരീരത്തിൽ കൂടുതൽ വലിച്ചെടുക്കപ്പെടുമെന്ന് പഠനങ്ങൾ പറയുന്നു.", "മഞ്ഞളും കുരുമുളകും", "PEPPER HELPS ABSORB CURCUMIN"),
        ("ഇനി ചരിത്രത്തിലേക്ക് വരാം.", "ചരിത്രത്തിലേക്ക്", "NOW THE HISTORY", S(["boat"], "dusk")),
        ("രണ്ടായിരം വർഷങ്ങൾക്ക് മുൻപേ റോമിൽ നിന്നും ഗ്രീസിൽ നിന്നും കപ്പലുകൾ കേരളത്തിലേക്ക് വന്നിരുന്നു.", "2000 വർഷം മുൻപ്", "SHIPS CAME 2,000 YEARS AGO"),
        ("മുസിരിസ് എന്ന പുരാതന തുറമുഖം ഇന്നത്തെ കൊടുങ്ങല്ലൂരിനടുത്തായിരുന്നു.", "മുസിരിസ് തുറമുഖം", "THE PORT OF MUZIRIS"),
        ("കപ്പലുകൾ മൺസൂൺ കാറ്റിനെ ആശ്രയിച്ചാണ് അറബിക്കടൽ കടന്നത്.", "മൺസൂൺ കാറ്റിൽ യാത്ര", "SAILING ON MONSOON WINDS"),
        ("പകരമായി അവർ സ്വർണ്ണനാണയങ്ങൾ കൊണ്ടുവന്ന് കുരുമുളക് വാങ്ങി.", "സ്വർണ്ണത്തിന് പകരം കുരുമുളക്", "GOLD COINS FOR PEPPER"),
        ("കുരുമുളകിന് പിന്നാലെയാണ് പിന്നീട് യൂറോപ്യൻ കപ്പലുകളും കേരളത്തിൽ എത്തിയത്.", "പിന്നാലെ യൂറോപ്പ്", "EUROPE FOLLOWED THE PEPPER"),
        ("ഇന്നും കേരളം ഇന്ത്യയിലെ ഏറ്റവും വലിയ കുരുമുളക് ഉത്പാദക സംസ്ഥാനമാണ്.", "ഇന്നും മുന്നിൽ", "STILL INDIA'S TOP PRODUCER"),
        ("ഒരു ചെറിയ കറുത്ത മണിയാണ് ലോകചരിത്രത്തിന്റെ ഗതി മാറ്റിയത്.", "ഒരു ചെറു മണി, വലിയ ചരിത്രം", "A SMALL BERRY CHANGED HISTORY", TX("ചെറു മണി, വലിയ ചരിത്രം", "A SMALL BERRY, BIG HISTORY", "leaf", "#2f7d4f")),
    ],
)
FACTS_PEPPER = ["Black pepper (Piper nigrum) is native to the Western Ghats of Kerala and is a climbing vine; black pepper is made from unripe berries dried until enzymes darken the skin, white pepper from ripe berries with the husk removed (Britannica; Wikipedia: Black pepper).",
                "Pepper's pungency comes from piperine; capsaicin is the compound in chillies (Wikipedia: Piperine; Capsaicin).",
                "Piperine can increase the absorption of curcumin (Shoba et al., Planta Medica 1998).",
                "Muziris, near present-day Kodungallur, was a major Indo-Roman trade port about 2,000 years ago, and ships used the monsoon winds (Muziris Heritage Project; Wikipedia: Muziris).",
                "Kerala is India's leading pepper-producing state (Spices Board India)."]

TURMERIC = sh(
    "turmeric_s", "മഞ്ഞളിൽ ചുണ്ണാമ്പ് തൊട്ടാൽ ചുവക്കുന്നത് എന്തുകൊണ്ട്?", "Why does turmeric turn red with lime?", "മഞ്ഞൾ ചുവക്കുന്നു!", "TURMERIC AND LIME",
    [
        ("മഞ്ഞളിൽ ചുണ്ണാമ്പ് ചേർത്താൽ ചുവന്ന നിറം വരുന്നത് എന്തുകൊണ്ടാണ്?", "മഞ്ഞൾ → ചുവപ്പ്", "YELLOW TURNS RED", S(["bowl", "leaf"], "dusk", label=("മഞ്ഞൾ", "TURMERIC"))),
        ("മഞ്ഞളിലെ മഞ്ഞ നിറത്തിന് കാരണം കുർക്കുമിൻ എന്ന വസ്തുവാണ്.", "കുർക്കുമിൻ", "THE DYE CURCUMIN"),
        ("ചുണ്ണാമ്പ് ഒരു ക്ഷാരമാണ്.", "ചുണ്ണാമ്പ് = ക്ഷാരം", "LIME IS AN ALKALI"),
        ("ക്ഷാരത്തിൽ കുർക്കുമിന്റെ ഘടന മാറും, അപ്പോൾ അത് ചുവപ്പ് കലർന്ന തവിട്ടു നിറം കാണിക്കും.", "ഘടന മാറുന്നു", "ITS STRUCTURE SHIFTS", S(["bottle"], "dusk")),
        ("അമ്ലം ചേർത്താൽ ആ നിറം വീണ്ടും മഞ്ഞയാകും.", "അമ്ലം: വീണ്ടും മഞ്ഞ", "ACID BRINGS THE YELLOW BACK"),
        ("അതുകൊണ്ട് സോപ്പ് പോലുള്ള ക്ഷാര വസ്തുക്കൾ പുരണ്ടാലും മഞ്ഞൾ കറ ചുവക്കും.", "സോപ്പിലും ചുവക്കും", "SOAP TURNS IT RED TOO"),
    ],
    "മഞ്ഞളൊരു ചെറിയ രസതന്ത്രജ്ഞൻ!", "A KITCHEN CHEMIST", "മഞ്ഞൾ അടുക്കളയിലെ ഒരു രാസപരീക്ഷണമാണ്!")

CHILLI = sh(
    "chilli_s", "മുളക് കഴിച്ചാൽ എരിയുന്നത് എന്തുകൊണ്ട്? പാല് കുടിച്ചാൽ ആശ്വാസം?", "Why does chilli burn and why does milk help?", "മുളകിന്റെ എരിവ്", "WHY CHILLI BURNS",
    [
        ("എരിവുള്ള മുളക് കഴിച്ചാൽ വായ് എരിയുന്നത് എന്തുകൊണ്ടാണ്?", "വായ് എരിയുന്നു", "WHY THE BURN?", S(["person", "leaf"], "dusk", label=("എരിവ്", "HOT!"))),
        ("മുളകിൽ ക്യാപ്സെയ്സിൻ എന്ന വസ്തു ഉണ്ട്.", "ക്യാപ്സെയ്സിൻ", "CAPSAICIN"),
        ("അത് നാക്കിലെ ചൂട് അറിയുന്ന സെൻസറുകളിൽ ചെന്ന് പിടിക്കും.", "ചൂടിന്റെ സെൻസർ", "IT GRABS THE HEAT SENSORS"),
        ("അപ്പോൾ തലച്ചോറിന് ചൂടും വേദനയും ഉണ്ടെന്ന് സന്ദേശം കിട്ടും, ഒന്നും ചൂടായിട്ടില്ലെങ്കിലും.", "തലച്ചോറ് പറ്റിക്കപ്പെടുന്നു", "THE BRAIN IS FOOLED"),
        ("ക്യാപ്സെയ്സിൻ വെള്ളത്തിൽ ലയിക്കില്ല, അതുകൊണ്ട് വെള്ളം കുടിച്ചിട്ട് കാര്യമില്ല.", "വെള്ളം സഹായിക്കില്ല", "WATER DOES NOT HELP"),
        ("പാലിലെ കേസീൻ എന്ന മാംസ്യം ക്യാപ്സെയ്സിനെ പിടിച്ചെടുത്ത് ആശ്വാസം തരും.", "പാലിലെ കേസീൻ", "MILK'S CASEIN CATCHES IT"),
    ],
    "എരിവിന് പാല് മറുമരുന്ന്!", "MILK BEATS THE BURN", "അടുത്ത തവണ എരിഞ്ഞാൽ വെള്ളമല്ല, പാലോ തൈരോ കുടിക്കൂ!")

PUTTU = sh(
    "puttu_s", "പുട്ടുകുറ്റിയിൽ പുട്ട് വേവുന്നത് എങ്ങനെ?", "How does puttu cook in a tube?", "പുട്ടിന്റെ ശാസ്ത്രം", "THE SCIENCE OF PUTTU",
    [
        ("വെള്ളത്തിൽ മുക്കാതെ പുട്ട് വേവുന്നത് എങ്ങനെയാണ്?", "വെള്ളമില്ലാതെ വേവ്", "COOKED WITHOUT BOILING", S(["bowl", "coconut"], "dusk", label=("പുട്ട്", "PUTTU"))),
        ("പുട്ടുകുറ്റിയുടെ താഴെ കലത്തിലെ വെള്ളം തിളച്ച് ആവിയാകും.", "വെള്ളം ആവിയാകുന്നു", "WATER BECOMES STEAM", S(["cooker"], "dusk", ("bubbles", 22, "#fff"))),
        ("ആ ആവി മുകളിലേക്ക് കുറ്റിയിലൂടെ കടന്നുപോകും.", "ആവി മുകളിലേക്ക്", "STEAM RISES THROUGH THE TUBE"),
        ("അരിപ്പൊടിയും തേങ്ങയും അടുക്കടുക്കായി നിറച്ചതുകൊണ്ട് ആവിക്ക് ഇടയിലൂടെ കയറാൻ വഴിയുണ്ട്.", "അടുക്കുകൾ, വഴികൾ", "LAYERS LEAVE GAPS FOR STEAM"),
        ("ആവിയുടെ ചൂടിൽ അരിപ്പൊടിയിലെ അന്നജം വെള്ളം വലിച്ച് വേവും.", "അന്നജം വേവുന്നു", "STARCH SOAKS UP AND COOKS"),
        ("അതുകൊണ്ടാണ് പുട്ട് പൊടിഞ്ഞുപോകാത്ത മൃദുവായ കട്ടയായി വരുന്നത്.", "മൃദുവായ കട്ട", "A SOFT, SET CYLINDER"),
    ],
    "ആവിയുടെ അത്ഭുതം!", "THE MAGIC OF STEAM", "ഒരു തുള്ളി വെള്ളം തൊടാതെ പുട്ട് വേവിക്കുന്നത് ആവിയാണ്!")

PAPAD = sh(
    "pappadam_s", "പപ്പടം വറുക്കുമ്പോൾ പൊങ്ങുന്നത് എന്തുകൊണ്ട്?", "Why does a pappadam puff up when fried?", "പപ്പടം പൊങ്ങുന്നു!", "PAPPADAM PUFFS",
    [
        ("പരന്ന പപ്പടം എണ്ണയിൽ ഇട്ടാൽ പൊങ്ങിവരുന്നത് എന്തുകൊണ്ടാണ്?", "പരന്നത് പൊങ്ങുന്നു", "FLAT TO PUFFY", S(["bowl"], "dusk", label=("പപ്പടം", "PAPPADAM"))),
        ("ഉണങ്ങിയ പപ്പടത്തിനുള്ളിലും ചെറിയ അളവിൽ ജലാംശം ഉണ്ട്.", "ഉള്ളിൽ ജലാംശം", "A LITTLE WATER INSIDE"),
        ("ചൂടെണ്ണയിൽ ആ വെള്ളം പെട്ടെന്ന് ആവിയാകും.", "ആവിയായി മാറുന്നു", "IT FLASHES INTO STEAM", S(["bowl"], "dusk", ("bubbles", 25, "#fff"))),
        ("ആവി പുറത്തുപോകാൻ വഴി തേടി പപ്പടത്തെ വീർപ്പിക്കും.", "ആവി വീർപ്പിക്കുന്നു", "STEAM INFLATES IT"),
        ("അതോടൊപ്പം ഉഴുന്നുമാവിലെ മാംസ്യം ചൂടിൽ ഉറച്ച് ആ ആകൃതി നിലനിർത്തും.", "മാംസ്യം ഉറയ്ക്കുന്നു", "PROTEIN SETS THE SHAPE"),
        ("അതുകൊണ്ട് വീർത്തതിന് ശേഷം പപ്പടം മൊരിഞ്ഞ് ഉറച്ചിരിക്കും.", "മൊരിഞ്ഞ് ഉറച്ചു", "CRISP AND SET"),
    ],
    "ആവി നിറച്ച ബലൂൺ!", "A STEAM BALLOON", "ഓരോ പപ്പടവും ചെറിയൊരു ആവി ബലൂണാണ്!")

CARDAMOM = sh(
    "cardamom_s", "ഏലക്കായ്ക്ക് മണം വരുന്നത് എവിടെ നിന്ന്?", "Where does cardamom get its scent?", "ഏലത്തിന്റെ മണം", "QUEEN OF SPICES",
    [
        ("സുഗന്ധവ്യഞ്ജനങ്ങളുടെ റാണി എന്ന് ഏലക്കായ് അറിയപ്പെടുന്നത് എന്തുകൊണ്ടാണ്?", "സുഗന്ധറാണി", "WHY THE QUEEN?", S(["leaf", "mountain"], "sky", label=("ഏലം", "CARDAMOM"))),
        ("ഇടുക്കി പോലുള്ള കുളിർമയും മഴയുമുള്ള മലകളിലാണ് ഏലം നന്നായി വളരുന്നത്.", "ഇടുക്കിയുടെ ഏലം", "IT LOVES COOL, WET HILLS"),
        ("ഏലക്കായുടെ ഉള്ളിലെ കറുത്ത വിത്തുകളിൽ സുഗന്ധ എണ്ണ നിറഞ്ഞിരിക്കുന്നു.", "വിത്തിൽ സുഗന്ധ എണ്ണ", "SCENTED OIL IN THE SEEDS"),
        ("അതിൽ സിനിയോൾ പോലുള്ള വാസനയുള്ള രാസവസ്തുക്കൾ ഉണ്ട്.", "വാസനയുള്ള രാസവസ്തുക്കൾ", "AROMA CHEMICALS LIKE CINEOLE"),
        ("ആ വസ്തുക്കൾ വളരെ എളുപ്പത്തിൽ ആവിയായി വായുവിലെത്തും, അതാണ് നമ്മൾ മണം പിടിക്കുന്നത്.", "ആവിയായി മണം", "THEY EVAPORATE INTO SCENT"),
        ("തൊലി പൊളിച്ച് പൊടിച്ചാൽ എണ്ണ കൂടുതൽ പുറത്തുവരുന്നതുകൊണ്ട് ചായയിൽ ചേർക്കുമ്പോൾ മണം കൂടും.", "പൊടിച്ചാൽ മണം കൂടും", "CRUSH IT FOR MORE AROMA"),
    ],
    "ഒരു മണിയിൽ ഒരു കാട്!", "A FOREST IN A POD", "ഒരു ഏലക്കായിൽ ഇടുക്കിയുടെ മുഴുവൻ സുഗന്ധവും ഒളിച്ചിരിക്കുന്നു!")

PICKLE = sh(
    "pickle_s", "അച്ചാർ കേടാകാത്തത് എന്തുകൊണ്ട്?", "Why doesn't pickle spoil?", "അച്ചാർ കേടാകില്ല!", "WHY PICKLE LASTS",
    [
        ("മാസങ്ങൾ വച്ചാലും അച്ചാർ കേടാകാത്തത് എന്തുകൊണ്ടാണ്?", "കേടാകാത്ത അച്ചാർ", "WHY IT KEEPS", S(["bottle", "mango"], "dusk", label=("അച്ചാർ", "PICKLE"))),
        ("ധാരാളം ഉപ്പ് ചേർത്താൽ മാങ്ങയിലെ വെള്ളം പുറത്തേക്ക് വലിഞ്ഞു വരും.", "ഉപ്പ് വെള്ളം വലിക്കും", "SALT DRAWS WATER OUT"),
        ("ഇതിനെ ഓസ്മോസിസ് എന്ന് പറയും.", "ഓസ്മോസിസ്", "OSMOSIS"),
        ("ബാക്ടീരിയകൾക്ക് വളരാൻ വെള്ളം വേണം, ഉപ്പുള്ള വെള്ളത്തിൽ അവ ജലം നഷ്ടപ്പെട്ട് തളരും.", "ബാക്ടീരിയകൾ തളരുന്നു", "BACTERIA DRY OUT"),
        ("എണ്ണയും വിനാഗിരിയും നാരങ്ങയും ചേർന്ന് അമ്ലത കൂടും, അതും രോഗാണുക്കളെ അകറ്റും.", "അമ്ലതയും എണ്ണയും", "ACID AND OIL HELP TOO"),
        ("നനഞ്ഞ സ്പൂൺ ഇടാതിരുന്നാൽ അച്ചാർ വളരെക്കാലം നിൽക്കും.", "ഉണങ്ങിയ സ്പൂൺ", "USE A DRY SPOON"),
    ],
    "ഉപ്പിന്റെ ശക്തി!", "THE POWER OF SALT", "പണ്ടുള്ളവരുടെ ഫ്രിഡ്ജ് ഉപ്പും എണ്ണയുമായിരുന്നു!")

FACTS = [
    "Curcumin, the yellow pigment of turmeric, turns reddish-brown in alkaline conditions and yellow again in acid (Wikipedia: Curcumin; pH indicator use).",
    "Capsaicin triggers the heat receptor TRPV1, is not soluble in water, and milk's casein protein helps remove it (Wikipedia: Capsaicin; Harvard Health).",
    "Steam from boiling water passes through the layered flour and coconut in a puttu tube and cooks the starch (general food science; Wikipedia: Puttu).",
    "A pappadam puffs because moisture inside turns to steam in hot oil while the protein-rich dough sets (general food science).",
    "Cardamom (Elettaria cardamomum) seeds hold aromatic oils such as 1,8-cineole and grow in cool, wet hills like Idukki (Wikipedia: Cardamom; Spices Board India).",
    "Salt preserves food by osmosis, drawing water out of microbes and food; acid and oil also hinder spoilage (USDA food preservation guidance).",
] + FACTS_PEPPER
VIDEOS = [PEPPER, TURMERIC, CHILLI, PUTTU, PAPAD, CARDAMOM, PICKLE]
