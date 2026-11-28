"""Science Chaya: how India's space programme began at Thumba, Kerala (long)."""
from chaya.content_monsoon import BL, BR, DK, GD, LF, OR, RD, SE, B
from chaya.dsl import GROUND, PT, C, I, O, R, T
from chaya.quick import rich

LONG = {
    "id": "thumba_long", "orient": "wide", "mood": "curious",
    "title_ml": "ഇന്ത്യയുടെ ആദ്യ റോക്കറ്റ് പറന്നത് കേരളത്തിലെ ഒരു പള്ളിമുറ്റത്ത് നിന്ന്: തുമ്പയുടെ കഥ",
    "title_en": "India's first rocket flew from a church in Kerala: the story of Thumba",
    "thumb": {"ml": "പള്ളിമുറ്റത്ത് നിന്ന് ബഹിരാകാശത്തേക്ക്", "en": "THE STORY OF THUMBA", "hero": "compose"},
    "comment": "നിങ്ങൾ തുമ്പയിലെ ബഹിരാകാശ മ്യൂസിയം കണ്ടിട്ടുണ്ടോ? അവിടുത്തെ ഏറ്റവും വലിയ കൗതുകം എന്താണ്?",
    "beats": [
        B("ഇന്ത്യയുടെ ആദ്യത്തെ റോക്കറ്റ് പറന്നത് കേരളത്തിലെ ഒരു പള്ളിമുറ്റത്ത് നിന്നാണ്!", ("പള്ളിമുറ്റത്ത് നിന്ന് റോക്കറ്റ്!", "INDIA'S FIRST ROCKET LIFTED OFF FROM A CHURCH YARD", DK),
          C([GROUND("#6b8f4e", 0.78), I("church", 0.35, 0.62, 7), I("rocket", 0.7, 0.45, 5, anim="float")], bg="sky")),
        B("ഒരു പള്ളിയാണ് ശാസ്ത്രജ്ഞർക്ക് ഓഫീസും കൺട്രോൾ റൂമും ആയത്.", ("പള്ളി = കൺട്രോൾ റൂം", "A CHURCH BECAME THE CONTROL ROOM", BR)),
        B("ഈ കഥ തുടങ്ങുന്നത് തിരുവനന്തപുരത്തിനടുത്തുള്ള തുമ്പ എന്ന മത്സ്യത്തൊഴിലാളി ഗ്രാമത്തിലാണ്.", ("തുമ്പ", "A FISHING VILLAGE NEAR THIRUVANANTHAPURAM", SE), {"kind": "map", "p": {"arrows": False, "shade": "none", "atb": {"arrows": 99, "shade": 99, "ridge": 99}, "pins": [{"id": "tvm", "ml": "തുമ്പ", "en": "THUMBA", "atb": 0.3, "w": 250}]}}),
        B("ഡോക്ടർ വിക്രം സാരാഭായി ആയിരുന്നു ഇന്ത്യയുടെ ബഹിരാകാശ പദ്ധതിയുടെ തുടക്കക്കാരൻ.", ("വിക്രം സാരാഭായി", "THE FOUNDER OF INDIA'S SPACE PROGRAMME", LF), {"kind": "text", "p": {"ml": "വിക്രം സാരാഭായി", "en": "THE FATHER OF INDIA'S SPACE PROGRAMME", "icon": "rocket", "col": LF}}),
        B("അദ്ദേഹത്തിന് ഒരു പ്രത്യേക സ്ഥലം വേണമായിരുന്നു, ഭൂമിയുടെ കാന്തിക മധ്യരേഖയിൽ.", ("കാന്തിക മധ്യരേഖ", "A SPOT ON THE MAGNETIC EQUATOR", OR)),
        B("ഭൂമിക്ക് ചുറ്റും ഒരു കാന്തമണ്ഡലമുണ്ട്, അതിന്റെ മധ്യരേഖ കടന്നുപോകുന്നത് തുമ്പയ്ക്ക് മുകളിലൂടെയാണ്.", ("ഭൂമിയുടെ കാന്തമണ്ഡലം", "EARTH'S MAGNETIC FIELD", RD),
          C([O(0.5, 0.5, 0.26, "#2d6fa0"), I("magnet", 0.5, 0.5, 5, rot=90, anim="float"), R(0.12, 0.49, 0.76, 0.012, "#c8442f"), T("മാഗ്നറ്റിക് ഇക്വേറ്റർ", 0.5, 0.86, 80)], bg="night")),
        B("അവിടെ മുകളിലെ അന്തരീക്ഷത്തിൽ ഒരു പ്രത്യേക വൈദ്യുതപ്രവാഹം ഉണ്ടാകും, അതിനെ ഇക്വറ്റോറിയൽ ഇലക്ട്രോജെറ്റ് എന്ന് പറയും.", ("ഇക്വറ്റോറിയൽ ഇലക്ട്രോജെറ്റ്", "A RIVER OF CURRENT HIGH IN THE ATMOSPHERE", BL)),
        B("അത് പഠിക്കാൻ ഏറ്റവും നല്ല സ്ഥലമായിരുന്നു തുമ്പ.", ("പഠിക്കാൻ പറ്റിയ സ്ഥലം", "THUMBA WAS THE PERFECT PLACE", GD)),
        B("പക്ഷേ അവിടെ വാഹനങ്ങൾ പോകുന്ന നല്ല റോഡുകൾ ഇല്ലായിരുന്നു.", ("റോഡുകളില്ല", "THERE WERE NO GOOD ROADS", RD)),
        B("അതുകൊണ്ട് റോക്കറ്റിന്റെ ഭാഗങ്ങൾ സൈക്കിളിലും കാളവണ്ടിയിലും കൊണ്ടുപോയി.", ("സൈക്കിളിലും കാളവണ്ടിയിലും", "CARRIED BY BICYCLE AND BULLOCK CART", OR), C([GROUND("#c9a35e", 0.78), I("bicycle", 0.25, 0.64, 6, mvb=0, to=[0.7, 0.64], dur=0.9), I("rocket", 0.25, 0.52, 3, rot=90, mvb=0, to=[0.7, 0.52], dur=0.9)], bg="sky")),
        B("സെന്റ് മേരി മഗ്ദലീൻ പള്ളി ആദ്യ ഓഫീസും കൺട്രോൾ റൂമും ആയി.", ("സെന്റ് മേരി മഗ്ദലീൻ പള്ളി", "ST MARY MAGDALENE CHURCH", BR), C([GROUND("#6b8f4e", 0.78), I("church", 0.5, 0.58, 9)], bg="sky")),
        B("ബിഷപ്പിന്റെ വീട് ശാസ്ത്രജ്ഞരുടെ ഓഫീസായി.", ("ബിഷപ്പിന്റെ വീട് = ഓഫീസ്", "THE BISHOP'S HOUSE BECAME AN OFFICE", GD)),
        B("ഗ്രാമവാസികൾ അവരുടെ പള്ളിയും സ്ഥലവും ഈ പദ്ധതിക്ക് വിട്ടുകൊടുത്തു.", ("നാട്ടുകാരുടെ സമ്മാനം", "THE VILLAGERS GAVE UP THEIR CHURCH AND LAND", LF)),
        B("ആയിരത്തി തൊള്ളായിരത്തി അറുപത്തിമൂന്ന് നവംബർ ഇരുപത്തിയൊന്നിന് ആദ്യ റോക്കറ്റ് ഉയർന്നു.", ("1963 നവംബർ 21", "21 NOVEMBER 1963", RD), {"kind": "text", "p": {"ml": "1963 നവംബർ 21", "en": "THE FIRST ROCKET LIFTS OFF", "icon": "rocket", "col": RD}}),
        B("അത് അമേരിക്കയിൽ നിർമ്മിച്ച നൈക്കി അപ്പാച്ചി എന്ന ചെറിയ സൗണ്ടിങ് റോക്കറ്റായിരുന്നു.", ("നൈക്കി അപ്പാച്ചി", "A SMALL US-MADE SOUNDING ROCKET", BL), C([I("rocket", 0.5, 0.75, 6, mvb=0.5, to=[0.5, 0.18], dur=0.45), PT("bubbles", 18, [0.46, 0.35, 0.54, 0.95], "#ffb347", 8), GROUND("#6b8f4e", 0.88)], bg="sky")),
        B("സൗണ്ടിങ് റോക്കറ്റ് എന്നാൽ അന്തരീക്ഷം പഠിക്കാൻ ഉയരത്തിലേക്ക് പോയി തിരിച്ചുവരുന്ന റോക്കറ്റാണ്.", ("സൗണ്ടിങ് റോക്കറ്റ്", "STUDIES THE UPPER ATMOSPHERE AND COMES BACK", SE)),
        B("അതിൽ ഉപഗ്രഹം ഉണ്ടായിരുന്നില്ല, പക്ഷേ അതൊരു വലിയ തുടക്കമായിരുന്നു.", ("ചെറിയ തുടക്കം", "A SMALL START", GD)),
        B("അന്ന് അവിടെ ഉണ്ടായിരുന്ന യുവ ശാസ്ത്രജ്ഞരിൽ എപിജെ അബ്ദുൽ കലാമും ഉൾപ്പെട്ടിരുന്നു.", ("എപിജെ അബ്ദുൽ കലാം", "A YOUNG A.P.J. ABDUL KALAM WAS THERE", BR)),
        B("പിന്നീട് ഇന്ത്യ സ്വന്തമായി റോക്കറ്റുകളും ഉപഗ്രഹങ്ങളും നിർമ്മിച്ചു.", ("സ്വന്തം റോക്കറ്റുകൾ", "INDIA BUILT ITS OWN ROCKETS", LF)),
        B("തുമ്പയിലെ ആ കേന്ദ്രത്തിൽ നിന്നാണ് ഇന്നത്തെ വിക്രം സാരാഭായി സ്പേസ് സെന്റർ വളർന്നത്.", ("വിക്രം സാരാഭായി സ്പേസ് സെന്റർ", "THE SEED OF TODAY'S VSSC", DK)),
        B("ആ പള്ളിക്കെട്ടിടം ഇന്ന് ഒരു ബഹിരാകാശ മ്യൂസിയമാണ്.", ("പള്ളി ഇന്ന് മ്യൂസിയം", "THE CHURCH IS NOW A SPACE MUSEUM", GD), C([I("church", 0.5, 0.55, 9), T("ബഹിരാകാശ മ്യൂസിയം", 0.5, 0.86, 90)], bg="dusk")),
        B("ചന്ദ്രയാനും മംഗൾയാനും വരെ എത്തിയ യാത്രയുടെ ആദ്യ ചുവട് ഇവിടെയായിരുന്നു.", ("യാത്രയുടെ ആദ്യ ചുവട്", "THE FIRST STEP OF A LONG JOURNEY", BL)),
        B("സൈക്കിളിൽ നിന്ന് റോക്കറ്റിലേക്ക്, ഒരു ചെറിയ ഗ്രാമത്തിൽ നിന്ന് ഒരു വലിയ സ്വപ്നത്തിലേക്ക്.", ("സൈക്കിൾ → റോക്കറ്റ്", "FROM A BICYCLE TO A ROCKET", BR), {"kind": "flow", "p": {"carry": "charge", "nodes": [{"icon": "bicycle", "ml": "സൈക്കിൾ", "en": "BICYCLE"}, {"icon": "church", "ml": "പള്ളി", "en": "CHURCH"}, {"icon": "rocket", "ml": "റോക്കറ്റ്", "en": "ROCKET"}, {"icon": "moon", "ml": "ചന്ദ്രൻ", "en": "MOON"}]}}),
        B("നിങ്ങൾ തുമ്പയിലെ ബഹിരാകാശ മ്യൂസിയം കണ്ടിട്ടുണ്ടോ, അവിടുത്തെ ഏറ്റവും വലിയ കൗതുകം എന്താണ്?", None, {"kind": "outro", "p": {"ml": "തുമ്പയിലെ ബഹിരാകാശ മ്യൂസിയം കണ്ടിട്ടുണ്ടോ? എന്താണ് ഏറ്റവും വലിയ കൗതുകം?", "en": "HAVE YOU VISITED THE THUMBA SPACE MUSEUM?"}}),
        B("താഴെ കമന്റ് ചെയ്യൂ, ഇതുപോലുള്ള വീഡിയോകൾക്കായി സയൻസ് ചായ സബ്സ്ക്രൈബ് ചെയ്യൂ."),
    ],
}
FACTS = [
    "India's first rocket, a US-made Nike-Apache sounding rocket, was launched from Thumba on 21 November 1963 (Thumba Equatorial Rocket Launching Station; The Better India; Frontline).",
    "Thumba was chosen because it lies on the Earth's magnetic equator, where the equatorial electrojet forms (ISRO / TERLS).",
    "St Mary Magdalene Church and the bishop's house served as early offices and control room; parts were moved by bicycle and bullock cart; A.P.J. Abdul Kalam was among the young scientists present (The Better India; Daily Excelsior; The South First).",
    "The church building is now a space museum.",
]
# richer scene: the village, the church, the bicycle and bullock cart, and the first launch
rich(LONG, 9, 21, "thumba", {"bicycle": 0, "cart": 0.4, "church": 1, "bishop": 2, "villagers": 3, "rocket": 3.5, "date": 4, "count": 4, "launch": 5.2, "kalam": 8, "museum": 11},
     [(0, -600, 580, 1.2), (1, 330, 480, 1.3), (2, -120, 560, 1.7), (3, 330, 650, 1.6), (3.8, 850, 480, 1.3), (5, 900, 300, 1.0), (6, 1150, -250, 0.85), (7.5, 600, 500, 1.0), (8, 560, 560, 1.7), (9.5, 400, 480, 1.0), (11, 330, 520, 1.5)])

VIDEOS = [LONG]
