#!/usr/bin/env python3
"""
Herbarium — Générateur de pages HTML pour les plantes Z
Génère une page HTML par plante avec le même template que les pages Y.
Utilise l'API GBIF pour récupérer famille et taxonomie.
Les plantes toxiques reçoivent le thème rouge sombre (toxique.css).
"""

import re
import time
import json
import requests
from pathlib import Path

# ══════════════════════════════════════════════
#  CONFIGURATION
#  ⚠ À MODIFIER à chaque nouvelle lettre
# ══════════════════════════════════════════════

DOSSIER_SORTIE  = "./J_Plante_page"              # ← Dossier de sortie         ex: "./V_Plante_page"
LETTRE          = "J"                            # ← Lettre courante            ex: "V"
LETTRE_HTML     = "J.html"                       # ← Fichier index de la lettre ex: "V.html"
LOG_FILE        = "generation_log_pages_J.json"  # ← Fichier log                ex: "generation_log_pages_V.json"
HEADERS         = {"User-Agent": "Herbarium-Bot/1.0"}

# ══════════════════════════════════════════════
#  LISTE DES PLANTES
#  ⚠ À REMPLACER à chaque nouvelle lettre
#  → Coller ici toutes les plantes de la lettre,
#    une par ligne, sans numérotation.
# ══════════════════════════════════════════════

PLANTES = """Jaagichlorella hainangensis
Jaagichlorella luteoviridis
Jaagichlorella Reisigl, 1964
Jaagichlorella sphaerica
Jaagiella Vischer, 1960
Jablonskia congesta
Jaborosa ameghinoi
Jaborosa bergii
Jaborosa cabrerae
Jaborosa caulescens
Jaborosa chubutensis
Jaborosa integrifolia
Jaborosa Juss.
Jaborosa kurtzii
Jaborosa laciniata
Jaborosa lanigera
Jaborosa leucotricha
Jaborosa longiflora
Jaborosa magellanica
Jaborosa odonelliana
Jaborosa oxipetala
Jaborosa parviflora
Jaborosa pinnata
Jaborosa reflexa
Jaborosa runcinata
Jaborosa sativa
Jaborosa squarrosa
Jaborosa volckmannii
Jabrosa Steud.
Jacaima costata
Jacaima parvifolia
Jacaima Rendle
Jacaranda atrolilacina
Jacaranda bracteata
Jacaranda brasiliana
Jacaranda bullata
Jacaranda bullosa
Jacaranda caerulea
Jacaranda campinae
Jacaranda carajasensis
Jacaranda caroba
Jacaranda caucana
Jacaranda copaia
Jacaranda corcovadensis
Jacaranda cowellii
Jacaranda cuspidifolia
Jacaranda decurrens
Jacaranda duckei
Jacaranda ekmanii
Jacaranda glabra
Jacaranda goiasensis
Jacaranda hesperia
Jacaranda heterophylla
Jacaranda hirsuta
Jacaranda intricata
Jacaranda jasminoides
Jacaranda Juss.
Jacaranda longiflora
Jacaranda macrantha
Jacaranda macrocarpa
Jacaranda micrantha
Jacaranda microcalyx
Jacaranda mimosifolia
Jacaranda montana
Jacaranda mutabilis
Jacaranda obovata
Jacaranda obtusifolia
Jacaranda paucifoliata
Jacaranda paucifoliolata
Jacaranda poitaei
Jacaranda praetermissa
Jacaranda puberula
Jacaranda pulcherrima
Jacaranda racemosa
Jacaranda rondoniae
Jacaranda rufa
Jacaranda rugosa
Jacaranda selleana
Jacaranda simplicifolia
Jacaranda sparrei
Jacaranda subalpina
Jacaranda ulei
Jacaratia A.DC.
Jacaratia corumbensis
Jacaratia digitata
Jacaratia dolichaula
Jacaratia heptaphylla
Jacaratia mexicana
Jacaratia spinosa
Jacartia
Jacea Haller, 1768
Jacea Mill.
Jackia Wall.
Jackiella angustifolia
Jackiella curvata
Jackiella javanica
Jackiella renifolia
Jackiella Schiffn.
Jackiella singapurensis
Jackiellaceae
Jackiopsis ornata
Jacksonia acicularis
Jacksonia aculeata
Jacksonia alata
Jacksonia anthoclada
Jacksonia argentea
Jacksonia arida
Jacksonia arnhemica
Jacksonia calycina
Jacksonia capitata
Jacksonia carduacea
Jacksonia chappilliae
Jacksonia compressa
Jacksonia condensata
Jacksonia cupulifera
Jacksonia debilis
Jacksonia divisa
Jacksonia effusa
Jacksonia elongata
Jacksonia eremodendron
Jacksonia fasciculata
Jacksonia flexuosa
Jacksonia floribunda
Jacksonia furcellata
Jacksonia gracillima
Jacksonia grevilleoides
Jacksonia hakeoides
Jacksonia horrida
Jacksonia humilis
Jacksonia intricata
Jacksonia lateritica
Jacksonia nematoclada
Jacksonia nutans
Jacksonia odontoclada
Jacksonia pendens
Jacksonia pungens
Jacksonia quairading
Jacksonia quinkanensis
Jacksonia R.Br. ex Sm.
Jacksonia racemosa
Jacksonia ramosissima
Jacksonia ramulosa
Jacksonia remota
Jacksonia rhadinoclona
Jacksonia rigida
Jacksonia rubra
Jacksonia rupestris
Jacksonia scoparia
Jacksonia spicata
Jacksonia spinosa
Jacksonia stackhousei
Jacksonia stellaris
Jacksonia sternbergiana
Jacksonia tarinensis
Jacksonia thesioides
Jacksonia velutina
Jacksonia venosa
Jacksonia vernicosa
Jacmaia incana
Jacobaea abrotanifolia
Jacobaea acutipinna
Jacobaea adonidifolia
Jacobaea albescens
Jacobaea alpina
Jacobaea alpina x erucifolia
Jacobaea alpina x vulgaris
Jacobaea ambigua
Jacobaea ambracea
Jacobaea analoga
Jacobaea andrzejowskyi
Jacobaea aquatica
Jacobaea aquatica x vulgaris
Jacobaea boissieri
Jacobaea borysthenica
Jacobaea Burm.
Jacobaea buschiana
Jacobaea calvescens
Jacobaea candida
Jacobaea cannabifolia
Jacobaea carniolica
Jacobaea chassanica
Jacobaea cilicia
Jacobaea delphiniifolia
Jacobaea disjuncta
Jacobaea echaeta
Jacobaea erratica
Jacobaea erucifolia
Jacobaea ferganensis
Jacobaea gallerandiana
Jacobaea gigantea
Jacobaea gnaphalioides
Jacobaea graciliflora
Jacobaea incana
Jacobaea inops
Jacobaea insubrica
Jacobaea korshinskyi
Jacobaea kuanshanensis
Jacobaea laggeri
Jacobaea leucophylla
Jacobaea liechtensteinensis
Jacobaea litvinovii
Jacobaea lycopifolia
Jacobaea lyratifolia
Jacobaea maritima
Jacobaea maritima × vulgaris
Jacobaea maroccana
Jacobaea minuta
Jacobaea mollis
Jacobaea morrisonensis
Jacobaea mouterdei
Jacobaea multibracteolata
Jacobaea norica
Jacobaea nudicaulis
Jacobaea ostenfeldii
Jacobaea othonnae
Jacobaea paludosa
Jacobaea pancicii
Jacobaea persoonii
Jacobaea pseudoarnica
Jacobaea racemosa
Jacobaea racemulifera
Jacobaea raphanifolia
Jacobaea reisachii
Jacobaea renardii
Jacobaea sandrasica
Jacobaea schischkiniana
Jacobaea subalpina
Jacobaea tarokoensis
Jacobaea taurica
Jacobaea thuretii
Jacobaea tibetica
Jacobaea uniflora
Jacobaea vulgaris
Jacobaea wartmannii
Jacobea Thunb., 1801
Jacobina
Jacobinia acuminata
Jacobinia angustifolia
Jacobinia breviloba
Jacobinia clausseniana
Jacobinia colorata
Jacobinia cordata
Jacobinia hirsuta
Jacobinia ilhoenis
Jacobinia inaequalis
Jacobinia lancifolia
Jacobinia latifolia
Jacobinia laxa
Jacobinia lutea
Jacobinia moricandiana
Jacobinia penrhosiensis
Jacobinia refulgens
Jacobinia selloviana
Jacobinia squarrosa
Jacobinia varigata
Jacobinia verrucosa
Jacobsenia hallii
Jacobsenia kolbei
Jacobsenia L.Bolus & Schwantes
Jacobsenia vaginata
Jacquemontia abutiloides
Jacquemontia acrocephala
Jacquemontia acuminata
Jacquemontia aequisepala
Jacquemontia agrestis
Jacquemontia albida
Jacquemontia anomala
Jacquemontia asarifolia
Jacquemontia atlantica
Jacquemontia austiniana
Jacquemontia bahiensis
Jacquemontia Bél.
Jacquemontia blanchetii
Jacquemontia boliviana
Jacquemontia bracteosa
Jacquemontia browniana
Jacquemontia cataractae
Jacquemontia cayensis
Jacquemontia cearensis
Jacquemontia chodati
Jacquemontia Choisy
Jacquemontia chrysanthera
Jacquemontia chuquisacensis
Jacquemontia corymbulosa
Jacquemontia cumanensis
Jacquemontia curtisii
Jacquemontia curtissii
Jacquemontia cuspidata
Jacquemontia cuyabana
Jacquemontia decipiens
Jacquemontia densiflora
Jacquemontia diamantinensis
Jacquemontia diversifolia
Jacquemontia Douglas-Daly
Jacquemontia ekmanii
Jacquemontia elegans
Jacquemontia estrellensis
Jacquemontia euricola
Jacquemontia evolvuloides
Jacquemontia Fairview
Jacquemontia floribunda
Jacquemontia frankeana
Jacquemontia fruticulosa
Jacquemontia fusca
Jacquemontia gabrielii
Jacquemontia glabrescens
Jacquemontia glaucescens
Jacquemontia gracilis
Jacquemontia gracillima
Jacquemontia grisea
Jacquemontia guaranitica
Jacquemontia guyanensis
Jacquemontia havanensis
Jacquemontia heterotricha
Jacquemontia hispida
Jacquemontia holosericea
Jacquemontia itatiayensis
Jacquemontia Karunji
Jacquemontia Keep-River
Jacquemontia lasioclados
Jacquemontia linarioides
Jacquemontia linoides
Jacquemontia longipedunculata
Jacquemontia lorentzii
Jacquemontia macrocalyx
Jacquemontia mairae
Jacquemontia martii
Jacquemontia maximiliani
Jacquemontia mexicana
Jacquemontia nelsonii
Jacquemontia nipensis
Jacquemontia nodiflora
Jacquemontia nummularia
Jacquemontia oaxacana
Jacquemontia obcordata
Jacquemontia ochracea
Jacquemontia ovalifolia
Jacquemontia paniculata
Jacquemontia pannosa
Jacquemontia paraguayensis
Jacquemontia parviflora
Jacquemontia pentanthos
Jacquemontia peruviana
Jacquemontia polyantha
Jacquemontia pringlei
Jacquemontia prostrata
Jacquemontia pycnocephala
Jacquemontia reclinata
Jacquemontia revoluta
Jacquemontia robertsoniana
Jacquemontia rojasiana
Jacquemontia rojasii
Jacquemontia rufa
Jacquemontia sandwicensis
Jacquemontia saxicola
Jacquemontia seemannii
Jacquemontia selloi
Jacquemontia serpyllifolia
Jacquemontia smithii
Jacquemontia solanifolia
Jacquemontia sphaerocephala
Jacquemontia sphaerostigma
Jacquemontia spiciflora
Jacquemontia staplesii
Jacquemontia tamnifolia
Jacquemontia tomentella
Jacquemontia tuerckheimii
Jacquemontia turneroides
Jacquemontia unilateralis
Jacquemontia velloziana
Jacquemontia velutina
Jacquemontia verticillata
Jacquemontia villosissima
Jacquemontia warmingii
Jacquemontia weberbaueri
Jacquemontia zollingeri
Jacqueshuberia amplifoliola
Jacqueshuberia brevipes
Jacqueshuberia Ducke
Jacqueshuberia purpurea
Jacqueshuberia pustulata
Jacqueshuberia quinquangulata
Jacquina St.-Lag.
Jacquinia aculeata
Jacquinia acunana
Jacquinia arborea
Jacquinia armillaris
Jacquinia berteroi
Jacquinia clarendonensis
Jacquinia comosa
Jacquinia cristalensis
Jacquinia curvata
Jacquinia dichotoma
Jacquinia incrustata
Jacquinia keyensis
Jacquinia macrantha
Jacquinia macrocarpa
Jacquinia morenoana
Jacquinia obovata
Jacquinia proctorii
Jacquinia roigii
Jacquiniella aporophylla
Jacquiniella cernua
Jacquiniella cobanensis
Jacquiniella equitantifolia
Jacquiniella gigantea
Jacquiniella globosa
Jacquiniella leucomelana
Jacquiniella Schltr.
Jacquiniella standleyi
Jacquiniella steyermarkii
Jacquiniella teretifolia
Jacutopteris N.D.Vasilevskaja, 1960
Jadunia biroi
Jaegeria axillaris
Jaegeria bellidiflora
Jaegeria glabra
Jaegeria gracilis
Jaegeria hirta
Jaegeria macrocephala
Jaegeria pedunculata
Jaegeria purpurascens
Jaegeria robustior
Jaegeria standleyi
Jaegeria sterilis
Jaegerina formosa
Jaegerina guatemalensis
Jaegerina luzonensis
Jaegerina Müll.Hal.
Jaegerina plicata
Jaegerina retrosquarrosa
Jaegerina robillardii
Jaegerina scariosa
Jaegerina solitaria
Jaegerina stolonifera
Jaeschkea canaliculata
Jaeschkea Kurz
Jaeschkea microsperma
Jaeschkea oligosperma
Jaffrea erubescens
Jaffrea xerocarpa
Jaffueliobryum arsenei
Jaffueliobryum latifolium
Jaffueliobryum raui
Jaffueliobryum Thér.
Jaffueliobryum williamsii
Jaffueliobryum wrightii
Jagera Blume
Jagera discolor
Jagera javanica
Jagera madida
Jagera pseudorhus
Jagrantia monstrum
Jailoloa halmaherensis
Jalapa Tourn. ex Adans.
Jalcophila colombiana
Jalcophila M.O.Dillon & Sagást.
Jalcophila peruviana
Jaliscoa goldmanii
Jaliscoa paleacea
Jaliscoa pringlei
Jaliscoa S.Watson
Jaltomata aijana
Jaltomata andersonii
Jaltomata angasmarcae
Jaltomata antillana
Jaltomata aspera
Jaltomata athahuallpae
Jaltomata atiquipa
Jaltomata auriculata
Jaltomata aypatensis
Jaltomata bernardelloana
Jaltomata bicolor
Jaltomata biflora
Jaltomata bohsiana
Jaltomata cajacayensis
Jaltomata calliantha
Jaltomata chihuahuensis
Jaltomata chotanae
Jaltomata confinis
Jaltomata contorta
Jaltomata contumacensis
Jaltomata cuyasensis
Jaltomata darcyana
Jaltomata dendroidea
Jaltomata dentata
Jaltomata diversa
Jaltomata glomeruliflora
Jaltomata grandibaccata
Jaltomata grandiflora
Jaltomata herrerae
Jaltomata hunzikeri
Jaltomata lanata
Jaltomata leivae
Jaltomata lezamae
Jaltomata lojae
Jaltomata mionei
Jaltomata nigricolor
Jaltomata nitida
Jaltomata oppositifolia
Jaltomata pallascana
Jaltomata paneroi
Jaltomata pilosissima
Jaltomata procumbens
Jaltomata propinqua
Jaltomata quipuscoae
Jaltomata repandidentata
Jaltomata sagastegui
Jaltomata salpoensis
Jaltomata sanchez-vegae
Jaltomata sanctae-martae
Jaltomata Schltdl.
Jaltomata sinuosa
Jaltomata truxillana
Jaltomata umbellata
Jaltomata vestita
Jaltomata viridiflora
Jaltomata weberbaueri
Jaltomata werffii
Jaltomata whalenii
Jaltomata yacheri
Jaltomata yungayensis
Jamaicanthus laurifolius
Jambosa Adans., 1763
Jambosa condensata
Jambosa DC.
Jambosa neurocalyx
Jambosa polyneura
Jambosa pseudodensiflora
Jambosa puncticulata
Jambosa salicina
Jamesbrittenia acutiloba
Jamesbrittenia adpressa
Jamesbrittenia albanensis
Jamesbrittenia albiflora
Jamesbrittenia albobadia
Jamesbrittenia albomarginata
Jamesbrittenia amplexicaulis
Jamesbrittenia angolensis
Jamesbrittenia argentea
Jamesbrittenia aridicola
Jamesbrittenia aspalathoides
Jamesbrittenia aspleniifolia
Jamesbrittenia atropurpurea
Jamesbrittenia aurantiaca
Jamesbrittenia barbata
Jamesbrittenia bergae
Jamesbrittenia beverlyana
Jamesbrittenia bicolor
Jamesbrittenia breviflora
Jamesbrittenia burkeana
Jamesbrittenia calciphila
Jamesbrittenia candida
Jamesbrittenia canescens
Jamesbrittenia carvalhoi
Jamesbrittenia chenopodioides
Jamesbrittenia concinna
Jamesbrittenia crassicaulis
Jamesbrittenia dentatisepala
Jamesbrittenia dissecta
Jamesbrittenia dolomitica
Jamesbrittenia elegantissima
Jamesbrittenia filicaulis
Jamesbrittenia fimbriata
Jamesbrittenia fleckii
Jamesbrittenia fodina
Jamesbrittenia foliolosa
Jamesbrittenia fragilis
Jamesbrittenia fruticosa
Jamesbrittenia giessii
Jamesbrittenia glutinosa
Jamesbrittenia grandiflora
Jamesbrittenia hereroensis
Jamesbrittenia heucherifolia
Jamesbrittenia huillana
Jamesbrittenia incisa
Jamesbrittenia integerrima
Jamesbrittenia jurassica
Jamesbrittenia kraussiana
Jamesbrittenia Kuntze
Jamesbrittenia lesutica
Jamesbrittenia linifolia
Jamesbrittenia lyperioides
Jamesbrittenia macrantha
Jamesbrittenia major
Jamesbrittenia maritima
Jamesbrittenia maxii
Jamesbrittenia megadenia
Jamesbrittenia merxmuelleri
Jamesbrittenia micrantha
Jamesbrittenia microphylla
Jamesbrittenia montana
Jamesbrittenia multisecta
Jamesbrittenia myriantha
Jamesbrittenia namaquensis
Jamesbrittenia pallida
Jamesbrittenia pedunculosa
Jamesbrittenia phlogiflora
Jamesbrittenia pilgeriana
Jamesbrittenia pinnatifida
Jamesbrittenia primuliflora
Jamesbrittenia pristisepala
Jamesbrittenia racemosa
Jamesbrittenia ramosissima
Jamesbrittenia sessilifolia
Jamesbrittenia silenoides
Jamesbrittenia stellata
Jamesbrittenia stricta
Jamesbrittenia tenella
Jamesbrittenia tenuifolia
Jamesbrittenia thunbergii
Jamesbrittenia tortuosa
Jamesbrittenia tysonii
Jamesbrittenia zambesica
Jamesbrittenia zuurbergensis
Jamesia americana
Jamesia tetrapetala
Jamesianthus alabamensis
Jamesianthus S.F.Blake & Sherff
Jamesonia accrescens
Jamesonia alstonii
Jamesonia angusta
Jamesonia ascendens
Jamesonia aureonitens
Jamesonia auriculata
Jamesonia biardii
Jamesonia blepharum
Jamesonia bogotensis
Jamesonia boliviensis
Jamesonia brasiliensis
Jamesonia canescens
Jamesonia caracasana
Jamesonia ceracea
Jamesonia cheilanthoides
Jamesonia chiapensis
Jamesonia cinnamomea
Jamesonia congesta
Jamesonia cuatrecasasii
Jamesonia elongata
Jamesonia flabellata
Jamesonia flexuosa
Jamesonia galeana
Jamesonia glaberrima
Jamesonia glandulifera
Jamesonia goudotii
Jamesonia hirsutula
Jamesonia hirta
Jamesonia hispidula
Jamesonia Hook. & Grev.
Jamesonia imbricata
Jamesonia insignis
Jamesonia intermedia
Jamesonia kupperi
Jamesonia lasseri
Jamesonia laxa
Jamesonia lechleri
Jamesonia lindigii
Jamesonia longifolia
Jamesonia longipetiolata
Jamesonia madidiensis
Jamesonia mathewsii
Jamesonia maxonii
Jamesonia orbignyana
Jamesonia osteniana
Jamesonia panamensis
Jamesonia paucifolia
Jamesonia pulchra
Jamesonia refracta
Jamesonia retrofracta
Jamesonia robusta
Jamesonia rotundifolia
Jamesonia rufescens
Jamesonia scalaris
Jamesonia scammanae
Jamesonia scammaniae
Jamesonia setulosa
Jamesonia stuebelii
Jamesonia vellea
Jamesonia verticalis
Jamesonia warscewiczii
Jamesonia wurdackii
Jamesoniella (Spruce) Carrington
Jamesoniella (Spruce) F.Lees
Jamesoniella lieboldiana
Jancaea Boiss.
Jancaea heldreichii
Janczewskia gardneri
Janczewskia lappacea
Janczewskia moriformis
Janczewskia Solms-Laubach, 1877
Janczewskia solmsii
Janczewskia tasmanica
Janczewskia verrucaeformis
Jandufouria minor
Jania acutiloba
Jania adhaerens
Jania adherens
Jania arborescens
Jania articulata
Jania capillacea
Jania compressa
Jania crassa
Jania cubensis
Jania cultrata
Jania dniestrovica
Jania fastigiata
Jania guamensis
Jania intermedia
Jania longiarthra
Jania longifurca
Jania mayei
Jania mengaudi
Jania mexicana
Jania micrarthrodia
Jania novae-zelandiae
Jania occidentalis
Jania pacifica
Jania parva
Jania pedunculata
Jania pulchella
Jania pumila
Jania pusilla
Jania radiata
Jania rosea
Jania rubens
Jania sagittata
Jania Schult. & Schult.f.
Jania spectabilis
Jania squamata
Jania sripadaraoi
Jania subpinnata
Jania subulata
Jania tenella
Jania tenuissima
Jania ucrainica
Jania ungulata
Jania verrucosa
Jania vetus
Jania virgata
Janipha Kunth
Jankaea Boiss.
Jankowskia D.H.Mai, 1987
Jankuceraea pacifica
Jansaella B.L.Mamet & A.Roux, 1975
Jansenella griffithiana
Jansenella neglecta
Jansonia Kippist
Janthe Nel
Jantinella Kylin, 1941
Jantinella verrucaeformis
Janusia A.Juss.
Janusia A.Juss. ex Endl.
Janusia amazonica
Janusia anisandra
Janusia caudata
Janusia diminuta
Janusia guaranitica
Janusia hexandra
Janusia janusioides
Janusia lindmanii
Janusia malmeana
Janusia mediterranea
Janusia paraensis
Janusia prancei
Janusia schwannioides
Jaoa K.C.Fan, 1964
Japanobotrychum chamaeconium
Japanobotrychum lanuginosum
Japanobotrychum Masam.
Japonicalia delphiniifolia
Japonicalia kiusiana
Japonicalia tebakoensis
Japonolirion Nakai
Japonolirion osense
Jaquemontia
Jaquinia L., 1759
Jaracatia corumbensis
Jaracatia dodecaphylla
Jaracatia Marcgr. ex Endl.
Jaramilloa hylibates
Jaramilloa R.M.King & H.Rob.
Jaramilloa sanctae-martae
Jarandersonia clemensiae
Jarandersonia Kosterm.
Jarandersonia paludosa
Jarandersonia parvifolia
Jarandersonia purseglovei
Jarandersonia rinoreoides
Jarandersonia spinulosa
Jarandersonia yahyantha
Jarava castellanosii
Jarava filifolia
Jarava hypsophila
Jarava hystricina
Jarava ichu
Jarava leptostachya
Jarava plumosa
Jarava pseudoichu
Jarava Ruiz & Pav.
Jarava scabrifolia
Jardinea Steud.
Jarilla caudata
Jarilla chocola
Jarilla heterophylla
Jarilla nana
Jarilla Rusby
Jasarum steyermarkii
Jasione amethystina
Jasione appressifolia
Jasione arenaria
Jasione bulgarica
Jasione caespitosa
Jasione cavanillesii
Jasione corymbosa
Jasione crispa
Jasione depressa
Jasione foliosa
Jasione heldreichii
Jasione idaea
Jasione L.
Jasione laevis
Jasione litoralis
Jasione maritima
Jasione montana
Jasione orbiculata
Jasione penicillata
Jasione perennis
Jasione pyrenaea
Jasione sessiliflora
Jasione sphaerocephala
Jasione supina
Jasminanthes Blume
Jasminanthes borneensis
Jasminanthes chunii
Jasminanthes hosei
Jasminanthes laotica
Jasminanthes maingayi
Jasminanthes mucronata
Jasminanthes pilosa
Jasminanthes saxatilis
Jasminanthes suaveolens
Jasminium B.C.J.Dumortier, 1829
Jasminocereus thouarsii
Jasminum abyssinicum
Jasminum aculeatum
Jasminum acuminatum
Jasminum adenophyllum
Jasminum affine
Jasminum aldabrarum
Jasminum alongense
Jasminum amabile
Jasminum ambiguum
Jasminum amoenum
Jasminum amplexicaule
Jasminum anastomosans
Jasminum andamanicum
Jasminum angulare
Jasminum angustifolium
Jasminum annamense
Jasminum anodontum
Jasminum aphanodon
Jasminum arborescens
Jasminum artense
Jasminum attenuatum
Jasminum auriculatum
Jasminum azoricum
Jasminum bakeri
Jasminum beesianum
Jasminum betchei
Jasminum bifarium
Jasminum bignoniaceum
Jasminum brachyscyphum
Jasminum breviflorum
Jasminum brevilobum
Jasminum brevipetiolatum
Jasminum calcareum
Jasminum calcicola
Jasminum calophyllum
Jasminum calycinum
Jasminum campyloneurum
Jasminum cardiomorphum
Jasminum carinatum
Jasminum carissoides
Jasminum caudatum
Jasminum cinnamomifolium
Jasminum coarctatum
Jasminum coarctum
Jasminum coffeinum
Jasminum cordatum
Jasminum cordifolium
Jasminum craibianum
Jasminum crassifolium
Jasminum cumingii
Jasminum curtisii
Jasminum cuspidatum
Jasminum dallachyi
Jasminum degeneri
Jasminum dichotomum
Jasminum didymum
Jasminum dinklagei
Jasminum dispermum
Jasminum domatiigerum
Jasminum duclouxii
Jasminum eberhardtii
Jasminum elatum
Jasminum elegans
Jasminum elongatum
Jasminum Exmouth
Jasminum extensum
Jasminum flexile
Jasminum fluminense
Jasminum gilgianum
Jasminum glandulosum
Jasminum glaucum
Jasminum grandiflorum
Jasminum greveanum
Jasminum griffithii
Jasminum guangxiense
Jasminum harmandianum
Jasminum hasseltianum
Jasminum hirsutum
Jasminum holstii
Jasminum hongshuihoense
Jasminum insigne
Jasminum insularum
Jasminum ixoroides
Jasminum jenniae
Jasminum kajewskii
Jasminum kedahense
Jasminum kerstingii
Jasminum kitchingii
Jasminum kostermansii
Jasminum kriegeri
Jasminum kwangense
Jasminum L.
Jasminum lanceolaria
Jasminum lanceolatum
Jasminum latipetalum
Jasminum laurifolium
Jasminum laxiflorum
Jasminum ledangense
Jasminum listeri
Jasminum longipetalum
Jasminum longitubum
Jasminum loudonianum
Jasminum mackeeorum
Jasminum macrocarpum
Jasminum maingayi
Jasminum marianum
Jasminum melastomatifolium
Jasminum melastomifolium
Jasminum mesnyi
Jasminum meyeri-johannis
Jasminum microcalyx
Jasminum molle
Jasminum mossamedense
Jasminum mouilaense
Jasminum multiflorum
Jasminum multinervosum
Jasminum multipartitum
Jasminum multipetalum
Jasminum nardydorum
Jasminum neocaledonicum
Jasminum nepalense
Jasminum nervosum
Jasminum nintooides
Jasminum nobile
Jasminum noumeense
Jasminum nudiflorum
Jasminum obtusifolium
Jasminum octocuspe
Jasminum officinale
Jasminum oreophilum
Jasminum papuasicum
Jasminum pauciflorum
Jasminum paucinervium
Jasminum pedunculatum
Jasminum pellucidum
Jasminum pentaneurum
Jasminum perissanthum
Jasminum pierreanum
Jasminum pipolyi
Jasminum polyanthum
Jasminum populifolium
Jasminum prainii
Jasminum preussii
Jasminum promunturianum
Jasminum pseudopinnatum
Jasminum pteropodum
Jasminum puberulum
Jasminum pubescens
Jasminum punctulatum
Jasminum quinatum
Jasminum rambayense
Jasminum rehderianum
Jasminum rigidum
Jasminum ritchiei
Jasminum rottlerianum
Jasminum roxburghianum
Jasminum rufohirtum
Jasminum rupestre
Jasminum sambac
Jasminum scandens
Jasminum schimperi
Jasminum sessile
Jasminum sianense
Jasminum simplicifolium
Jasminum sinense
Jasminum smilacifolium
Jasminum spec.
Jasminum spectabile
Jasminum steenisii
Jasminum stellipilum
Jasminum stenolobum
Jasminum stephanense
Jasminum streptopus
Jasminum subglandulosum
Jasminum syringifolium
Jasminum tetraquetrum
Jasminum thomense
Jasminum tortuosum
Jasminum trichotomum
Jasminum trinerve
Jasminum tubiflorum
Jasminum turneri
Jasminum undulatum
Jasminum urophyllum
Jasminum waitzianum
Jasminum wengeri
Jasminum yuanjiangense
Jasminum zippelianum
Jasonia (Cass.) Cass.
Jasonia radiata
Jasonia tuberosa
Jateorhiza calumba
Jateorhiza macrantha
Jateorhiza Miers
Jateorhiza palmata
Jatropa J.A.Scopoli, 1777
Jatropha aceroides
Jatropha aethiopica
Jatropha afrotuberosa
Jatropha alamanii
Jatropha andrieuxii
Jatropha angustidens
Jatropha angustifolia
Jatropha arborea
Jatropha aspleniifolia
Jatropha atacorensis
Jatropha bartlettii
Jatropha baumii
Jatropha botswanica
Jatropha breviloba
Jatropha bullockii
Jatropha calcarea
Jatropha campestris
Jatropha canescens
Jatropha capensis
Jatropha cardiophylla
Jatropha cathartica
Jatropha catingae
Jatropha ceballosii
Jatropha chamelensis
Jatropha chevalieri
Jatropha ciliata
Jatropha cinerea
Jatropha clavuligera
Jatropha collina
Jatropha conzattii
Jatropha cordata
Jatropha costaricensis
Jatropha cuneata
Jatropha curcas
Jatropha decipiens
Jatropha decumbens
Jatropha dehganii
Jatropha dhofarica
Jatropha dichtar
Jatropha dioica
Jatropha dissecta
Jatropha divaricata
Jatropha elbae
Jatropha ellenbeckii
Jatropha elliptica
Jatropha erythropoda
Jatropha euarguta
Jatropha excisa
Jatropha fremontioides
Jatropha gallabatensis
Jatropha galvanii
Jatropha gaumeri
Jatropha giffordiana
Jatropha glandulifera
Jatropha glauca
Jatropha gossypiifolia
Jatropha grossidentata
Jatropha guaranitica
Jatropha hastata
Jatropha hastifolia
Jatropha hernandiifolia
Jatropha heynei
Jatropha hildebrandtii
Jatropha hippocastanifolia
Jatropha hirsuta
Jatropha humboldtiana
Jatropha humifusa
Jatropha hypogyna
Jatropha integerrima
Jatropha intermedia
Jatropha isabellei
Jatropha jaimejimenezii
Jatropha kamerunica
Jatropha krusei
Jatropha L.
Jatropha lagarinthoides
Jatropha latifolia
Jatropha longibracteata
Jatropha macrantha
Jatropha macrocarpa
Jatropha macrophylla
Jatropha macrorhiza
Jatropha maheshwarii
Jatropha malacophylla
Jatropha marginata
Jatropha marmorata
Jatropha martiusii
Jatropha mcvaughii
Jatropha microdonta
Jatropha mirandana
Jatropha miskatensis
Jatropha mollissima
Jatropha monroi
Jatropha moranii
Jatropha multifida
Jatropha mutabilis
Jatropha nana
Jatropha napaeifolia
Jatropha natalensis
Jatropha neopauciflora
Jatropha neriifolia
Jatropha nogalensis
Jatropha nudicaulis
Jatropha obbiadensis
Jatropha oblanceolata
Jatropha orangeana
Jatropha ortegae
Jatropha osteocarpa
Jatropha pachypoda
Jatropha pachyrrhiza
Jatropha paganuccii
Jatropha palmatifida
Jatropha palmatipartita
Jatropha paradoxa
Jatropha pauciflora
Jatropha pedersenii
Jatropha peiranoi
Jatropha pelargoniifolia
Jatropha peltata
Jatropha pereziae
Jatropha prunifolia
Jatropha pseudocurcas
Jatropha purpurea
Jatropha ribifolia
Jatropha riojae
Jatropha rivae
Jatropha robecchii
Jatropha rufescens
Jatropha rzedowskii
Jatropha scaposa
Jatropha schlechteri
Jatropha schweinfurthii
Jatropha seineri
Jatropha sotoi-nunyezii
Jatropha spicata
Jatropha spinosa
Jatropha standleyi
Jatropha stephani
Jatropha stevensii
Jatropha stipulacea
Jatropha stuhlmannii
Jatropha sympetala
Jatropha tanjorensis
Jatropha tehuantepecana
Jatropha tertiaria
Jatropha tetracantha
Jatropha tlalcozotitlanensis
Jatropha trifida
Jatropha tropaeolifolia
Jatropha tupifolia
Jatropha uncinulata
Jatropha unicostata
Jatropha urens
Jatropha variabilis
Jatropha variegata
Jatropha variifolia
Jatropha velutina
Jatropha vernicosa
Jatropha villosa
Jatropha weberbaueri
Jatropha websteri
Jatropha weddeliana
Jatropha woodii
Jatropha zeyheri
Jaubertia Guill.
Jaumea alternifolia
Jaumea linearifolia
Jaumea Pers.
Javorkaea Borhidi & Jarai-Koml.
Jeannerettia lobata
Jeannerettia pedicellata
Jeanpaulia F.J.A.N.Unger, 1845
Jedda multicaulis
Jefea brevifolia
Jefea gnaphalioides
Jefea lantanifolia
Jefea phyllocephala
Jefea pringlei
Jeffersonia diphylla
Jeffersonia W.Bartram
Jeffersonioxylon G.M.Del Fueyo et al., 1995
Jeffreya Cabrera
Jeffreya palustris
Jeffreya Wild
Jeffreycia amaniensis
Jeffreycia hildebrandtii
Jeffreycia usambarensis
Jeffreycia zanzibarensis
Jeffreycia zeylanica
Jejewoodia jiewhoei
Jejewoodia longicalcarata
Jenkinsella apocynoides
Jenmaniella Engl.
Jennyella Lückel & Fessel
Jensenia connivens
Jensenia crassifrons
Jensenia decipiens
Jensenia difformis
Jensenia florschuetzii
Jensenia Lindb.
Jensenia spinosa
Jensenia wallisii
Jensenobotrya lossowiana
Jensensispermum M.E.J.Chandler, 1966
Jensia rammii
Jensia yosemitana
Jenufa Y.Nemcová, M.Eliáš, P.Škaloud & J.Neustupa, 2011
Jepsonia heterandra
Jepsonia malvifolia
Jepsonia parryi
Jepsonia Small
Jerdonia indica
Jerdonia Wight
Jessea cooperi
Jessea megaphylla
Jessea multivenia
Jessenia H.Karst.
Jirivanaea caespitosa
Jirivanaea cuspidifera
Jirivanaea esmeraldica
Jirivanaea galipensis
Jirivanaea U.B.Deshmukh & Rathor
Joannesia princeps
Joannesia Vell.
Jobinia balslevii
Jobinia campii
Jobinia canoi
Jobinia chlorantha
Jobinia connivens
Jobinia eulaxiflora
Jobinia formosa
Jobinia glossostemma
Jobinia grandis
Jobinia hatschbachii
Jobinia latipes
Jobinia lindbergii
Jobinia longicoronata
Jobinia mazzuchii
Jobinia neei
Jobinia paranaensis
Jobinia peruviana
Jobinia schizocorona
Jobinia streptantha
Jobinia tarmensis
Jobinia tiarata
Jobinia trifurcata
Jobinia umbellata
Jochenia Hedenäs, Schlesak & D.Quandt
Jochenia pallescens
Jochenia protuberans
Joculator Manza, 1937
Jodina Hook. & Arn.
Jodina Hook. & Arn. ex Meisn.
Jodina rhombifolia
Jodotella L.Morellet & J.Morellet, 1913
Jodotella veslensis
Jodrellia Baijnath
Joffrea P.R.Crane & R.A.Stockey, 1985
Johanneshowellia crateriorum
Johanneshowellia puberula
Johanneshowellia Reveal
Johannesia Endl., 1840
Johannesteijsmannia altifrons
Johannesteijsmannia magnifica
Johannesteijsmannia perakensis
Johannia elegans
Johansenia K.R.Hind & G.W.Saunders, 2013
Johansenia macmillanii
Johnson-sea -linkia
Johnsonia acaulis
Johnsonia K.B.Korde, 1965
Johnsonia lupulina
Johnsonia pubescens
Johnsonia R.Br.
Johnsonia spinosa
Johnsonia teretifolia
Johnstonalia axilliflora
Johnstonella albida
Johnstonella angelica
Johnstonella angustifolia
Johnstonella costata
Johnstonella diplotricha
Johnstonella geohintonii
Johnstonella grayi
Johnstonella gypsites
Johnstonella holoptera
Johnstonella inaequata
Johnstonella mexicana
Johnstonella micromeres
Johnstonella parviflora
Johnstonella pusilla
Johnstonella racemosa
Johnstonia A.B.Walkom, 1925
Johnstonia coriaceae
Johrenia anatolica
Johrenia araliastrum
Johrenia DC.
Johrenia dichotoma
Johrenia distans
Johrenia polyscias
Johrenia selinoides
Johrenia tortuosa
Johrenia villosa
Joinvillea ascendens
Joinvillea borneensis
Joinvillea bryanii
Joinvillea Gaudich. ex Brongn. & Gris
Joinvillea plicata
Joinvilleaceae
Jollydora armandui
Jollydora duparquetiana
Jollydora glandulosa
Jollydora Pierre
Jollydora Pierre ex Gilg
Jollydora pierrei
Jondraba cambessedesii
Jondraba Medik.
Jonesia Roxb.
Jonesiobryum Bizot & Pócs
Jonesiobryum cerradense
Jonesiobryum termitarum
Jongkindia mulbahii
Jonidium Vent.
Jonopsidium
Jonopsidium savianum
Jonthlaspi All.
Joosia aequatoria
Joosia antioquiana
Joosia capitata
Joosia dichotoma
Joosia dielsiana
Joosia frondosa
Joosia longisepala
Joosia loretensis
Joosia macrocalyx
Joosia obtusa
Joosia oligantha
Joosia panamensis
Joosia pulcherrima
Joosia sericea
Joosia umbellifera
Jordaaniella anemoniflora
Jordaaniella clavifolia
Jordaaniella cuprea
Jordaaniella dubia
Jordaaniella maritima
Jordaaniella spongiosa
Jordaaniella uniflora
Jordania Boiss.
Joseanthus chimborazensis
Joseanthus cuatrecasasii
Joseanthus H.Rob.
Joseanthus sparrei
Joseanthus trichotomus
Josephinia celebica
Josephinia eugeniae
Josephinia fruit
Josephinia grandiflora
Josephinia Mt-Edgar-Station
Jossinia littoralis
Jossinia schlechteri
Jouvea E.Fourn.
Jouvea pilosa
Jouvea straminea
Jovellana punctata
Jovellana repens
Jovellana Ruiz & Pav.
Jovellana sinclairii
Jovellana violacea
Jovetastella Tixier
Jovetia Guédès
Jovetia humilis
Jovibarba (DC.) Opiz
Jovibarba preissiana
Joycea H.P.Linder
Juania australis
Juania Drude
Juanulloa globifera
Juanulloa mexicana
Juanulloa parasitica
Juanulloa Ruiz & Pav.
Juanulloa speciosa
Juanulloa verrucosa
Juanulloa wardiana
Jubaea chilensis
Jubaea Kunth
Jubaeopsis Becc.
Jubaeopsis caffra
Jubelina A.Juss.
Jubelina grisebachiana
Jubelina magnifica
Jubelina riparia
Jubelina rosea
Jubelina uleana
Jubula blepharophylla
Jubula cambouena
Jubula hutchinsiae
Jubulaceae
Jucunda Cham.
Judithia delicatissima
Judithia parasitica
Jugastrum Miers
Juglandicarya depressa
Juglandicarya lubbockii
Juglandicarya simplicarpa
Juglandiphyllum Koch, 1963
Juglandites lacoei
Juglandites primordialis
Juglandites sinuatus
Juglandites Sternberg, 1825
Juglandoxylon G.Kraus, 1886
Juglans affinis
Juglans ailantifolia
Juglans alkalina
Juglans arctica
Juglans arizonica
Juglans australis
Juglans baltica
Juglans bendirei
Juglans berryi
Juglans bixbyi
Juglans boliviana
Juglans californica
Juglans cinerea
Juglans coloradensis
Juglans costata
Juglans crassifolia
Juglans crassipes
Juglans crescentia
Juglans crossii
Juglans cryptata
Juglans dentata
Juglans denticulata
Juglans egregia
Juglans elaenoides
Juglans elongata
Juglans florissanti
Juglans glabra
Juglans hindsii
Juglans hirsuta
Juglans hopeiensis
Juglans hybr
Juglans hybrida
Juglans intermedia
Juglans jamaicensis
Juglans L.
Juglans latifolia
Juglans laurifolia
Juglans laurinea
Juglans leconteana
Juglans major
Juglans mandshurica
Juglans microcarpa
Juglans minutidens
Juglans mollis
Juglans neotropica
Juglans nigella
Juglans nigra
Juglans notha
Juglans nuxtaurinensis
Juglans obtusifolia
Juglans occidentalis
Juglans olanchana
Juglans oregoniana
Juglans ovoidea
Juglans pyriformis
Juglans regia
Juglans rhamnoides
Juglans rostrata
Juglans sapindiformis
Juglans sapindoides
Juglans sepultus
Juglans sigillata
Juglans similis
Juglans smithsoniana
Juglans squamosa
Juglans steyermarkii
Juglans subrupestris
Juglans thermalis
Juglans townsendi
Juglans ungeri
Juglans vetusta
Juglans woodiana
Juglanspollenites G.V.Raatz, 1937
Jujuba Burm.
Julbernardia brieyi
Julbernardia globiflora
Julbernardia gossweileri
Julbernardia hochreutineri
Julbernardia letouzeyi
Julbernardia magnistipulata
Julbernardia paniculata
Julbernardia Pellegr.
Julbernardia pellegriniana
Julbernardia seretii
Julbernardia unijugata
Juliania Schltdl.
Julianiaceae
Julostylis ampumalensis
Julostylis angustifolia
Julostylis polyandra
Julostylis Thwaites
Jumellea ambrensis
Jumellea amplifolia
Jumellea angustifolia
Jumellea anjouanensis
Jumellea arachnantha
Jumellea arborescens
Jumellea bosseri
Jumellea brachycentra
Jumellea brevifolia
Jumellea comorensis
Jumellea cowanii
Jumellea cyrtoceras
Jumellea densifoliata
Jumellea divaricata
Jumellea exilis
Jumellea fragrans
Jumellea francoisii
Jumellea hyalina
Jumellea ibityana
Jumellea intricata
Jumellea jumelleana
Jumellea lignosa
Jumellea linearipetala
Jumellea longivaginans
Jumellea majalis
Jumellea major
Jumellea marojejiensis
Jumellea maxillarioides
Jumellea ophioplectron
Jumellea pachyceras
Jumellea papangensis
Jumellea peyrotii
Jumellea punctata
Jumellea recta
Jumellea recurva
Jumellea rigida
Jumellea Schltr.
Jumellea similis
Jumellea spathulata
Jumellea stenoglossa
Jumellea stenophylla
Jumellea tenuibracteata
Jumellea teretifolia
Jumellea triquetra
Jumellea tsaratananae
Jumellea usambarensis
Jumellea walleri
Jumelleanthus Hochr.
Jumelleanthus perrieri
Juncaginaceae
Juncago Ség.
Juncellus minutus
Juncinella Fourr.
Juncoides Adans., 1763
Juncoides Ség.
Juncus
Juncus abortivus
Juncus acuminatus
Juncus acutiflorus
Juncus acutiflorus x alpinoarticulatus
Juncus acutiflorus x articulatus
Juncus acutiflorus × articulatus
Juncus acutus
Juncus aemulans
Juncus alatus
Juncus albescens
Juncus alexandri
Juncus allioides
Juncus alpigenus
Juncus alpiniformis
Juncus alpinoarticulatus
Juncus alpinoarticulatus subsp. alpinoarticulatus × articulatus
Juncus alpinoarticulatus subsp. rariflorus × articulatus
Juncus alpinoarticulatus x articulatus
Juncus alpinoarticulatus × articulatus
Juncus alpinus
Juncus amabilis
Juncus amplifolius
Juncus amuricus
Juncus anatolicus
Juncus anceps
Juncus anceps × articulatus
Juncus andersonii
Juncus andinus
Juncus antarcticus
Juncus anthelatus
Juncus aquaticus
Juncus arcticus
Juncus arcticus × balticus
Juncus arcticus × filiformis
Juncus arcuatus
Juncus aridicola
Juncus aridicola x Juncus usitatus
Juncus aristatus
Juncus articulatus
Juncus articulatus × bulbosus
Juncus astreptus
Juncus atratus
Juncus australis
Juncus austrobrasiliensis
Juncus baekdusanensis
Juncus balticus
Juncus balticus × filiformis
Juncus bassianus
Juncus batrachium
Juncus benghalensis
Juncus beringensis
Juncus biflorus
Juncus biglumis
Juncus biglumoides
Juncus bolanderi
Juncus brachycarpus
Juncus brachycephalus
Juncus brachyphyllus
Juncus brachyspathus
Juncus brachystigma
Juncus bracteatus
Juncus brasiliensis
Juncus brevibracteus
Juncus brevicaudatus
Juncus brevifolius
Juncus breweri
Juncus brueggeri
Juncus bryoides
Juncus bryophilus
Juncus bufonius
Juncus bufonius × minutulus
Juncus bulbosus
Juncus burkartii
Juncus caesariensis
Juncus caespiticius
Juncus canadensis
Juncus capensis
Juncus capillaceus
Juncus capillaris
Juncus capitatus
Juncus castaneus
Juncus castelli
Juncus cephalostigma
Juncus cephalotes
Juncus chiapasensis
Juncus chrysocarpus
Juncus clarkei
Juncus coarctatus
Juncus compressus
Juncus compressus × gerardii
Juncus concinnus
Juncus concolor
Juncus confusus
Juncus conglomeratus
Juncus conglomeratus x effusus
Juncus conglomeratus x inflexus
Juncus conglomeratus × effusus
Juncus conradii
Juncus continuus
Juncus continuus x Juncus usitatus
Juncus cooperi
Juncus cordobensis
Juncus coriaceus
Juncus covillei
Juncus crassifolius
Juncus crassistylus
Juncus cryptocarpus
Juncus curtisiae
Juncus cyperoides
Juncus debilis
Juncus decipiens
Juncus densiflorus
Juncus depauperatus
Juncus diastrophanthus
Juncus dichotomus
Juncus diemii
Juncus diffusissimus
Juncus diffusus
Juncus digitatus
Juncus distegus
Juncus dongchuanensis
Juncus donyanae
Juncus dregeanus
Juncus drummondii
Juncus dubius
Juncus dudleyi
Juncus dulongjiangensis
Juncus dulongjiongensis
Juncus durus
Juncus duthiei
Juncus ebracteatus
Juncus echinocephalus
Juncus ecuadoriensis
Juncus effusus
Juncus effusus x inflexus
Juncus effusus × inflexus
Juncus elbrusicus
Juncus elegans
Juncus elliottii
Juncus emmanuelis
Juncus engleri
Juncus ensifolius
Juncus ensiformis
Juncus ernesti-barrosii
Juncus exiguus
Juncus exsertus
Juncus falcatus
Juncus fallax
Juncus fasciculatus
Juncus fascinatus
Juncus fauriei
Juncus fauriensis
Juncus filicaulis
Juncus filiformis
Juncus filipendulus
Juncus fimbristyloides
Juncus firmus
Juncus flavidus
Juncus flavidus x Juncus radula
Juncus fluitans
Juncus fockei
Juncus foliosus
Juncus fominii
Juncus fontanesii
Juncus fugongensis
Juncus fulvescens
Juncus fuscatus
Juncus ganeshii
Juncus georgianus
Juncus gerardi
Juncus giganteus
Juncus glaucoturgidus
Juncus glaucus
Juncus glomeratus
Juncus gonggae
Juncus gracilescens
Juncus gracilicaulis
Juncus gracillimus
Juncus greenei
Juncus grisebachii
Juncus gymnocarpus
Juncus haenkei
Juncus harae
Juncus haussknechtii
Juncus heldreichianus
Juncus hemiendytus
Juncus heptopotamicus
Juncus hesperius
Juncus heteranthus
Juncus heterophyllus
Juncus himalensis
Juncus holoschoenus
Juncus homalocaulis
Juncus hondurensis
Juncus hoppii
Juncus hybridus
Juncus hydrophilus
Juncus ilanquihuensis
Juncus imbricatus
Juncus inflexus
Juncus ingens
Juncus interior
Juncus inundatus
Juncus involucratus
Juncus iridifolius
Juncus isolepoides
Juncus jacquinii
Juncus jaxarticus
Juncus kelloggii
Juncus khasiensis
Juncus kingii
Juncus kleinii
Juncus krameri
Juncus kraussii
Juncus laccatus
Juncus laeviusculus
Juncus lampocarpus
Juncus lancastriensis
Juncus langii
Juncus leiospermus
Juncus leptospermus
Juncus leseurii
Juncus lesueurii
Juncus leucanthus
Juncus leucochlamus
Juncus leucomelas
Juncus liebmannii
Juncus littoralis
Juncus llanquihuensis
Juncus lomatophyllus
Juncus longiflorus
Juncus longii
Juncus longirostris
Juncus longistamineus
Juncus longistyles
Juncus longistylis
Juncus loureiranus
Juncus luciensis
Juncus luzuliformis
Juncus luzuloides
Juncus MacDonnell-Ranges
Juncus macrandrus
Juncus macrantherus
Juncus macrophyllus
Juncus marginatus
Juncus maritimus
Juncus maximowiczii
Juncus maximus
Juncus megacephalus
Juncus meianthus
Juncus membranaceus
Juncus mertensianus
Juncus micranthus
Juncus microcephalus
Juncus milashanensis
Juncus militaris
Juncus minimus
Juncus minutulus
Juncus miyiensis
Juncus modicus
Juncus mollis
Juncus monanthos
Juncus montellii
Juncus montserratensis
Juncus multiflorus
Juncus murbeckii
Juncus mustangensis
Juncus nepalicus
Juncus nevadensis
Juncus nivalis
Juncus nodatus
Juncus nodosiformis
Juncus nodosus
Juncus nodosus × Juncus torreyi
Juncus novae-zelandiae
Juncus obliquus
Juncus obotritorum
Juncus obtusiflorus
Juncus occidentalis
Juncus ochraceus
Juncus ochrocoleus
Juncus orchonicus
Juncus oronensis
Juncus orthophyllus
Juncus oxycarpus
Juncus oxymeris
Juncus pallescens
Juncus pallidiflorus
Juncus pallidus
Juncus paludosus
Juncus papillosus
Juncus parryi
Juncus patens
Juncus pauciflorus
Juncus pelocarpus
Juncus perpusillus
Juncus persicus
Juncus petrophilus
Juncus phaeanthus
Juncus phaeocephalus
Juncus pictus
Juncus planifolius
Juncus plumosus
Juncus polyanthemus
Juncus polycarpus
Juncus polycephalos
Juncus polycephalus
Juncus potaninii
Juncus prismatocarpus
Juncus procerus
Juncus prominens
Juncus przewalskii
Juncus psammophilus
Juncus punctorius
Juncus pungens
Juncus pusillus
Juncus pygmaeus
Juncus pylaei
Juncus radula
Juncus raeperi
Juncus ramboi
Juncus ranarius
Juncus rechingeri
Juncus reflexus
Juncus regelii
Juncus remotiflorus
Juncus repens
Juncus requienii
Juncus revolutus
Juncus rigidus
Juncus rohtangensis
Juncus royeri
Juncus rubens
Juncus rugulosus
Juncus ruhmeri
Juncus rupestris
Juncus rusguniensis
Juncus sallandiae
Juncus salsuginosus
Juncus sarophorus
Juncus saximontanus
Juncus scabriusculus
Juncus scheuchzerioides
Juncus schlechteri
Juncus scirpoides
Juncus secundus
Juncus semisolidus
Juncus setaceus
Juncus setchuensis
Juncus sherei
Juncus siculus
Juncus sikkimensis
Juncus socotranus
Juncus sonderianus
Juncus soranthus
Juncus sorrentinii
Juncus sparganiifolius
Juncus sphacelatus
Juncus sphaerocarpus
Juncus spicatus
Juncus sprengelii
Juncus spumosus
Juncus squarrosus
Juncus stellatus
Juncus stenopetalus
Juncus stipulatus
Juncus storae
Juncus striatus
Juncus stuckeyi
Juncus stygius
Juncus subcaudatus
Juncus subglaucus
Juncus subnodulosus
Juncus subsecundus
Juncus subtilis
Juncus subulatus
Juncus subulitepalus
Juncus subverticillatus
Juncus sudeticus
Juncus supiniformis
Juncus supinus
Juncus sylvaticus
Juncus taonanensis
Juncus tenageia
Juncus tenageius
Juncus tenax
Juncus tenuis
Juncus texanus
Juncus textilis
Juncus thomasii
Juncus thompsonianus
Juncus thomsonii
Juncus tiehmii
Juncus tingitanus
Juncus tirfidus
Juncus tobdeniorum
Juncus torreyi
Juncus trachyphyllus
Juncus tracyi
Juncus trichophyllus
Juncus triformis
Juncus triglumis
Juncus trigonocarpus
Juncus trilocularis
Juncus turkestanicus
Juncus tweedyi
Juncus tyraicus
Juncus uncialis
Juncus uniflorus
Juncus uniglumis
Juncus usitatus
Juncus vaginatus
Juncus valbrayi
Juncus validus
Juncus valvatus
Juncus vaseyi
Juncus venturianus
Juncus virens
Juncus wallichianus
Juncus xiphioides
Junellia alba
Junellia aretioides
Junellia azorelloides
Junellia ballsii
Junellia bisulcata
Junellia bryoides
Junellia caespitosa
Junellia clavata
Junellia congesta
Junellia connatibracteata
Junellia crithmifolia
Junellia digitata
Junellia erinacea
Junellia fasciculata
Junellia hookeriana
Junellia juniperina
Junellia lavandulifolia
Junellia micrantha
Junellia minima
Junellia Moldenke
Junellia morenonis
Junellia occulta
Junellia odonellii
Junellia origenes
Junellia pappigera
Junellia patagonica
Junellia pseudojuncea
Junellia selaginoides
Junellia seriphioides
Junellia silvestrii
Junellia spathulata
Junellia succulentifolia
Junellia thymifolia
Junellia toninii
Junellia tridactylites
Junellia trifida
Junellia trifurcata
Junellia tripartita
Junellia ulicina
Junellia uniflora
Jungermannia afoninae
Jungermannia amakawana
Jungermannia atrovirens
Jungermannia bipinnata
Jungermannia borgenii
Jungermannia brasiliensis
Jungermannia calcicola
Jungermannia crenulata
Jungermannia dilitata
Jungermannia eucordifolia
Jungermannia exsertifolia
Jungermannia gollanii
Jungermannia konstantinovae
Jungermannia L.
Jungermannia lateriflora
Jungermannia longiretis
Jungermannia mastigophora
Jungermannia miehena
Jungermannia minima
Jungermannia oblongifolia
Jungermannia ovatotrigona
Jungermannia polaris
Jungermannia pumila
Jungermannia quadridigitata
Jungermannia rupincola
Jungermannia schusterana
Jungermannia serpillifolia
Jungermannia sinuata
Jungermannia stereocauli
Jungermannia subapicaulis
Jungermannia sullivantiana
Jungermannia supina
Jungermannia tenuis
Jungermannia vernicosa
Jungermannia viridis
Jungermannia yamatoensis
Jungermanniaceae
Jungermanniales
Jungermanniopsida
Jungermanniopsis M.Howe & Hollick
Jungermannites cockerellii
Jungermannites eophilus
Jungermannites Göpp.
Jungermannites noterocladioides
Junghuhnia Miq.
Jungia axillaris
Jungia beckii
Jungia calyculata
Jungia coarctata
Jungia crenatifolia
Jungia discolor
Jungia ferruginea
Jungia fistulosa
Jungia floribunda
Jungia glandulifera
Jungia gunnerifolia
Jungia Heist. ex Fabr.
Jungia hirsuta
Jungia karstenii
Jungia mitis
Jungia paniculata
Jungia pauciflora
Jungia polita
Jungia pringlei
Jungia revoluta
Jungia revolutus
Jungia rugosa
Jungia schuerae
Jungia sellowii
Jungia sericea
Jungia sordida
Jungia spectabilis
Jungia stuebelii
Jungia tomentosa
Jungia vitocensis
Jungia weberbaueri
Jungia woodii
Juniperoxylon C.Houlbert, 1910
Juniperus ambigens
Juniperus angosturana
Juniperus arizonica
Juniperus ashei
Juniperus barbadensis
Juniperus bermudiana
Juniperus blancoi
Juniperus brevifolia
Juniperus californica
Juniperus canariensis
Juniperus cedrus
Juniperus cerropastorensis
Juniperus chinensis
Juniperus coahuilensis
Juniperus comitana
Juniperus communis
Juniperus convallium
Juniperus corneyana
Juniperus cupressifolia
Juniperus deppeana
Juniperus drupacea
Juniperus durangensis
Juniperus excelsa
Juniperus flaccida
Juniperus foetidissima
Juniperus formosana
Juniperus gamboana
Juniperus gracilior
Juniperus herragudensis
Juniperus horizontalis
Juniperus hypnoides
Juniperus indica
Juniperus jaliscana
Juniperus komarovii
Juniperus L.
Juniperus mexicana
Juniperus monosperma
Juniperus monticola
Juniperus nepalensis
Juniperus occidentalis
Juniperus osteosperma
Juniperus oxycedrus
Juniperus palanciana
Juniperus pfitzeriana
Juniperus phoenicea
Juniperus pinchotii
Juniperus pingii
Juniperus procera
Juniperus procumbens
Juniperus prostrata
Juniperus przewalskii
Juniperus pseudosabina
Juniperus recurva
Juniperus rigida
Juniperus sabina
Juniperus saltillensis
Juniperus saltuaria
Juniperus saxicola
Juniperus scopulorum
Juniperus semiglobosa
Juniperus sheppardii
Juniperus sinensis
Juniperus squamata
Juniperus squamosa
Juniperus standleyi
Juniperus taiwaniana
Juniperus taxifolia
Juniperus thurifera
Juniperus tibetica
Juniperus virginiana
Juno waryleyensis
Jupunba abbottii
Jupunba adenophora
Jupunba alexandri
Jupunba asplenifolia
Jupunba auriculata
Jupunba barbouriana
Jupunba barnebyana
Jupunba brachystachya
Jupunba campestris
Jupunba cochleata
Jupunba commutata
Jupunba curvicarpa
Jupunba ferruginea
Jupunba filamentosa
Jupunba floribunda
Jupunba gallorum
Jupunba ganymedea
Jupunba glauca
Jupunba idiopoda
Jupunba laeta
Jupunba langsdorffii
Jupunba leucophylla
Jupunba longipedunculata
Jupunba macradenia
Jupunba mataybifolia
Jupunba microcalyx
Jupunba nipensis
Jupunba obovalis
Jupunba oppositifolia
Jupunba oxyphyllidia
Jupunba piresii
Jupunba rhombea
Jupunba trapezifolia
Jupunba turbinata
Jupunba villifera
Jupunba villosa
Jupunba zolleriana
Juraella bifurcata
Juranyiella javorkae
Juratzkaea argentinica
Juratzkaea incisa
Juratzkaea Lorentz
Juratzkaea seminervis
Juratzkaeella sinensis
Jurinea abolinii
Jurinea abramovii
Jurinea abramowii
Jurinea adenocarpa
Jurinea akinfievii
Jurinea alata
Jurinea albescens
Jurinea albicaulis
Jurinea algida
Jurinea almaatensis
Jurinea alpigena
Jurinea ancyrensis
Jurinea androssovii
Jurinea annae
Jurinea antonowi
Jurinea antunowi
Jurinea arachnoidea
Jurinea armeniaca
Jurinea asperifolia
Jurinea atropurpurea
Jurinea aucheriana
Jurinea auriculata
Jurinea baldschuanica
Jurinea bellidioides
Jurinea berardioides
Jurinea bipinnatifida
Jurinea blanda
Jurinea bobrovii
Jurinea bocconei
Jurinea bocconi
Jurinea botschantzevii
Jurinea brachypappa
Jurinea brevicaulis
Jurinea breviscapa
Jurinea bucharica
Jurinea bungei
Jurinea cadmea
Jurinea caespitans
Jurinea caespitosa
Jurinea calcarea
Jurinea capusii
Jurinea carduicephala
Jurinea carduiformis
Jurinea cartaliniana
Jurinea cataonica
Jurinea catharinae
Jurinea cephalopoda
Jurinea ceratocarpa
Jurinea chaetocarpa
Jurinea chenopodiifolia
Jurinea chitralica
Jurinea ciscaucasica
Jurinea consanguinea
Jurinea cordata
Jurinea coronopifolia
Jurinea cretacea
Jurinea creticola
Jurinea crispa
Jurinea cyanoides
Jurinea cypria
Jurinea czilikinoana
Jurinea darvasica
Jurinea deltoidea
Jurinea densisquamea
Jurinea derderioides
Jurinea dobrogensis
Jurinea efeae
Jurinea elbursensis
Jurinea elegantissima
Jurinea eriobasis
Jurinea ewersmanii
Jurinea eximia
Jurinea fedtschenkoana
Jurinea ferganica
Jurinea filicifolia
Jurinea filifolia
Jurinea fontqueri
Jurinea frigida
Jurinea galushkoi
Jurinea gilesii
Jurinea giviensis
Jurinea glycacantha
Jurinea gmelinii
Jurinea gracilis
Jurinea grossheimii
Jurinea grumosa
Jurinea helenae
Jurinea helichrysifolia
Jurinea heteromalla
Jurinea heterophylla
Jurinea humilis
Jurinea iljinii
Jurinea jucunda
Jurinea karatavica
Jurinea karategina
Jurinea kaschgarica
Jurinea kilaea
Jurinea kirghisorum
Jurinea komarovii
Jurinea kopetensis
Jurinea korotkovae
Jurinea kyzylkyrensis
Jurinea lanipes
Jurinea lasiopoda
Jurinea ledebourii
Jurinea leptoloba
Jurinea leptophylla
Jurinea levieri
Jurinea lipskyi
Jurinea longifolia
Jurinea macrocephala
Jurinea mallophora
Jurinea mariae
Jurinea merxmuelleri
Jurinea micevskii
Jurinea michelsonii
Jurinea microcephala
Jurinea mobayenii
Jurinea modesta
Jurinea modesti
Jurinea mollis
Jurinea mollissima
Jurinea mongolica
Jurinea monocephala
Jurinea moschus
Jurinea mugodsharica
Jurinea multicaulis
Jurinea multiceps
Jurinea multiflora
Jurinea multiloba
Jurinea narynensis
Jurinea nivea
Jurinea olgae
Jurinea orientalis
Jurinea peguensis
Jurinea persimilis
Jurinea pinnata
Jurinea poacea
Jurinea polycephala
Jurinea polyclonos
Jurinea pontica
Jurinea propinqua
Jurinea psammophila
Jurinea pseudoiljinii
Jurinea pulchella
Jurinea pumila
Jurinea radians
Jurinea ramosissima
Jurinea ramulosa
Jurinea rhizomatoidea
Jurinea robusta
Jurinea roegneri
Jurinea rosulata
Jurinea salicifolia
Jurinea sangardensis
Jurinea schachimardanica
Jurinea schachimordanica
Jurinea schischkiniana
Jurinea semenovii
Jurinea semenowii
Jurinea serratuloides
Jurinea shahrestanica
Jurinea sharifiana
Jurinea sintenisii
Jurinea sosnowskyi
Jurinea spectabilis
Jurinea spissa
Jurinea squarrosa
Jurinea staehelinae
Jurinea stenophylla
Jurinea stoechadifolia
Jurinea suidunensis
Jurinea tamburiana
Jurinea taygetea
Jurinea tenuiloba
Jurinea tortisquamea
Jurinea tortumensis
Jurinea transsylvanica
Jurinea trautvetteriana
Jurinea trifurcata
Jurinea turcica
Jurinea tzar-ferdinandii
Jurinea viciosoi
Jurinea winkleri
Jurinea woronowii
Jurinea xeranthemoides
Jurinea xerophytica
Jurinea yakla
Jurinea zakirovii
Jurinella Jaub. & Spach
Jurinodendron aegyptiacum
Jurinodendron brevifolium
Jurinodendron dasyphyllum
Jurinodendron kiltorkense
Jurinodendron macconochiei
Jurinodendron sigillarioides
Jurinodendron ursinum
Jurinodendron zafrense
Juruasia Lindau
Jussiaea L.
Jussiaea tenella
Jussiena Rchb., 1837
Jussieua J.A.Murray, 1774
Jussitriporites menendezii
Justenia Hiern
Justica Neck., 1790
Justicia
Justicia abeggii
Justicia abscondita
Justicia aconitiflora
Justicia acuta
Justicia acutangula
Justicia acutifolia
Justicia addisoniensis
Justicia adenostachya
Justicia adenothyrsa
Justicia adhaerens
Justicia adhatoda
Justicia adhatodoides
Justicia aequalis
Justicia aequilabris
Justicia aequiloculata
Justicia aethes
Justicia agria
Justicia alainii
Justicia albadenia
Justicia albobractea
Justicia albobracteata
Justicia albovelata
Justicia alboviridis
Justicia alchorneeticola
Justicia alexandri
Justicia allenii
Justicia almedae
Justicia alopecuroidea
Justicia alsinoides
Justicia alterniflora
Justicia alternifolia
Justicia altior
Justicia amanda
Justicia amazonica
Justicia amherstia
Justicia amphibola
Justicia amplifolia
Justicia anabasa
Justicia anagalloides
Justicia andrographioides
Justicia andromeda
Justicia anfractuosa
Justicia angustata
Justicia angustiflora
Justicia anisophylla
Justicia anisotoides
Justicia ankazobensis
Justicia anselliana
Justicia antirrhina
Justicia antsingensis
Justicia aphelandroides
Justicia aquatica
Justicia arborescens
Justicia arbuscula
Justicia archeri
Justicia arcuata
Justicia areysiana
Justicia argyrostachya
Justicia aristeguietae
Justicia asclepiadea
Justicia asystasioides
Justicia atacta
Justicia atkinsonii
Justicia attenuata
Justicia aurea
Justicia austroguangxiensis
Justicia austrosinensis
Justicia axillaris
Justicia axiologa
Justicia aymardii
Justicia baillonii
Justicia bakeri
Justicia balansae
Justicia balslevii
Justicia barapaniensis
Justicia baravensis
Justicia bartlettii
Justicia baumii
Justicia beckii
Justicia beddomei
Justicia beloperonoides
Justicia bequaertii
Justicia betonica
Justicia bicalcarata
Justicia bitarkarae
Justicia blackii
Justicia blechoides
Justicia boaleri
Justicia boerhaviifolia
Justicia bojeriana
Justicia bolavenensis
Justicia boliviana
Justicia boliviensis
Justicia bolomboensis
Justicia bolusii
Justicia borrerae
Justicia bracteosa
Justicia bradeana
Justicia brandbygei
Justicia brandegeeana
Justicia brandisii
Justicia brasiliana
Justicia breedlovei
Justicia brenesii
Justicia breteleri
Justicia brevifolia
Justicia brevipila
Justicia brevispica
Justicia bridsoniana
Justicia buchholzii
Justicia buchii
Justicia bullata
Justicia burchellii
Justicia cabrerae
Justicia caerulea
Justicia californica
Justicia calliantha
Justicia callopsoidea
Justicia caloneura
Justicia calyculata
Justicia calzadillae
Justicia camerunensis
Justicia campanulata
Justicia campechiana
Justicia campii
Justicia campylostemon
Justicia canbyi
Justicia candida
Justicia capensis
Justicia capitata
Justicia caracasana
Justicia carajensis
Justicia cardiophylla
Justicia careyana
Justicia carnea
Justicia carthaginensis
Justicia cataractae
Justicia catharinensis
Justicia cauliflora
Justicia ceylanica
Justicia chacoensis
Justicia chaconii
Justicia chaetocephala
Justicia chalaensis
Justicia chamaedryoides
Justicia chamaephyton
Justicia chamaeranthemodes
Justicia chamaeranthemoides
Justicia championii
Justicia chapadensis
Justicia chapana
Justicia chapareensis
Justicia chaponensis
Justicia chimalapensis
Justicia chimboracensis
Justicia chinensis
Justicia chiriquiensis
Justicia chloanantha
Justicia chol
Justicia chrysea
Justicia chrysostephana
Justicia chrysotrichoma
Justicia chuquisacensis
Justicia circulibracteata
Justicia ciriloi
Justicia citrina
Justicia claessensii
Justicia clarkii
Justicia clausseniana
Justicia clinopodium
Justicia clivalis
Justicia coahuilana
Justicia cobensis
Justicia cochinchinensis
Justicia colorata
Justicia columbiensis
Justicia comata
Justicia comosa
Justicia concavibracteata
Justicia congestiflora
Justicia congrua
Justicia consanguinea
Justicia coppenamensis
Justicia cordata
Justicia cordifolia
Justicia corumbensis
Justicia costaricana
Justicia cowanii
Justicia crassiradix
Justicia crebrinodis
Justicia crenata
Justicia cristata
Justicia croceochlamys
Justicia cuatrecasasii
Justicia cubana
Justicia cufodontii
Justicia culebritae
Justicia culubritae
Justicia cuneata
Justicia cuneifolia
Justicia curviflora
Justicia cuspidulata
Justicia cyclostegia
Justicia cydoniifolia
Justicia cymulifera
Justicia cynosuroides
Justicia cyrtantheriformis
Justicia cystolithosa
Justicia daidalea
Justicia dalaensis
Justicia dallarii
Justicia damingensis
Justicia dasycarpa
Justicia deaurata
Justicia decaryi
Justicia decumbens
Justicia decurrens
Justicia decurvata
Justicia decussata
Justicia dejecta
Justicia delascioi
Justicia delicatula
Justicia dendropila
Justicia densibracteata
Justicia densiflora
Justicia diclipteroides
Justicia diminuta
Justicia dispar
Justicia disparifolia
Justicia distichophylla
Justicia distincta
Justicia divergens
Justicia diversifolia
Justicia dives
Justicia drummondii
Justicia dumetorum
Justicia durangensis
Justicia dusenii
Justicia eburnea
Justicia edgarcabrerae
Justicia effusa
Justicia ekakusuma
Justicia elegantissima
Justicia elegantula
Justicia elliotii
Justicia enarthrocoma
Justicia engleriana
Justicia ensiflora
Justicia ephemera
Justicia equestris
Justicia equitans
Justicia eranthemanthus
Justicia espiritosantensis
Justicia euosmia
Justicia exigua
Justicia exilis
Justicia extensa
Justicia faulknerae
Justicia ferruginea
Justicia filibracteolata
Justicia fimbriata
Justicia flaccida
Justicia flagelliformis
Justicia flava
Justicia flavescens
Justicia flaviflora
Justicia floribunda
Justicia flosculosa
Justicia fluminensis
Justicia fortunensis
Justicia francoiseana
Justicia fruticosa
Justicia fuchsiifolia
Justicia fuentesii
Justicia fulvicoma
Justicia fulvohirsuta
Justicia funckii
Justicia furcata
Justicia fusagasugana
Justicia galapagana
Justicia galeotti
Justicia gardineri
Justicia gendarussa
Justicia genuflexa
Justicia gesnerifolia
Justicia ghiesbregtiana
Justicia gibsoniae
Justicia gigantophylla
Justicia gilbertii
Justicia gilliesii
Justicia gladiatotheca
Justicia glandulosa
Justicia glauca
Justicia glischrantha
Justicia glomerulata
Justicia glutinosa
Justicia goianiensis
Justicia gonzalezii
Justicia goudotii
Justicia graciliflora
Justicia grandifolia
Justicia grandis
Justicia graphocaula
Justicia graphophylla
Justicia griffithii
Justicia grisea
Justicia guerkeana
Justicia guineensis
Justicia gunnari
Justicia hainanensis
Justicia hantamensis
Justicia harlingii
Justicia hassleri
Justicia hatschbachii
Justicia haughtii
Justicia hayatai
Justicia hedrenii
Justicia helonoma
Justicia henricksonii
Justicia hepperi
Justicia heterocarpa
Justicia heterophylla
Justicia heterosepala
Justicia hians
Justicia hilsenbeckii
Justicia hochreutineri
Justicia hodgei
Justicia holgueri
Justicia homoea
Justicia huacanensis
Justicia huambensis
Justicia huilensis
Justicia humblotii
Justicia hunzikeri
Justicia hygrobia
Justicia hygrophiloides
Justicia hylaea
Justicia hylobia
Justicia hylophila
Justicia hyperdasya
Justicia hyssopifolia
Justicia hystrix
Justicia idiogenes
Justicia ilhensis
Justicia iltisii
Justicia inaequifolia
Justicia inconspicua
Justicia infelix
Justicia inficiens
Justicia ingrata
Justicia insolita
Justicia insularis
Justicia internodialis
Justicia involucrata
Justicia iochila
Justicia irumuensis
Justicia ischnorhachis
Justicia isthmensis
Justicia itatiaiensis
Justicia ivohibensis
Justicia ixodes
Justicia ixtlania
Justicia jamaicensis
Justicia jamisonii
Justicia japurensis
Justicia jitotolana
Justicia johannae
Justicia kampotiana
Justicia kanal
Justicia kempeana
Justicia keriana
Justicia kessleri
Justicia kiborianensis
Justicia killipii
Justicia kirkbridei
Justicia kirkiana
Justicia kiwuensis
Justicia kleinii
Justicia kouytcheensis
Justicia kucharii
Justicia kuestera
Justicia kunhardtii
Justicia kuntzei
Justicia kwangsiensis
Justicia L.
Justicia ladanoides
Justicia lamprophylla
Justicia lanceolata
Justicia lancifolia
Justicia lanstyakii
Justicia laotica
Justicia larsenii
Justicia latiflora
Justicia lavandulaefolia
Justicia lavandulifolia
Justicia laxa
Justicia lazarus
Justicia leikipiensis
Justicia leikpiensis
Justicia lenticellata
Justicia leonardii
Justicia lepida
Justicia leptochlamys
Justicia leptophylla
Justicia leptostachya
Justicia leucantha
Justicia leucothamna
Justicia leucoxiphus
Justicia lianshanica
Justicia lilloana
Justicia lilloi
Justicia linaria
Justicia linarioides
Justicia lindmanii
Justicia linearis
Justicia linearispica
Justicia lineolata
Justicia linifolia
Justicia lithophila
Justicia lithospermoides
Justicia lithspermoides
Justicia loheri
Justicia longepetiolata
Justicia longiacuminata
Justicia longii
Justicia longipetiolata
Justicia longula
Justicia lophura
Justicia lorata
Justicia loretensis
Justicia lovoiensis
Justicia loxensis
Justicia lucens
Justicia lucindae
Justicia lugoi
Justicia lukei
Justicia lundellii
Justicia luschnathii
Justicia luzmariae
Justicia lythroides
Justicia macarenensis
Justicia macrantha
Justicia madagascariensis
Justicia madrensis
Justicia magdalenensis
Justicia maguirei
Justicia maingayi
Justicia malacophylla
Justicia mandonii
Justicia manserichensis
Justicia mariae
Justicia martiana
Justicia martinsoniana
Justicia masiaca
Justicia masuta
Justicia matammensis
Justicia matogrossensis
Justicia maxima
Justicia maximiliani
Justicia maya
Justicia mbalaensis
Justicia mcdowellii
Justicia mckenleyi
Justicia mediocris
Justicia medrani
Justicia medranoi
Justicia megalantha
Justicia mendax
Justicia mendoncae
Justicia mendoncai
Justicia mesetarum
Justicia metallica
Justicia metallicorum
Justicia mexiae
Justicia meyeniana
Justicia micrantha
Justicia microthyrsa
Justicia migeodii
Justicia miguelii
Justicia minensis
Justicia minima
Justicia minutiflora
Justicia minutifolia
Justicia mirabiloides
Justicia mirandae
Justicia modesta
Justicia mollugo
Justicia monachinoi
Justicia monopleurantha
Justicia montealegrensis
Justicia monticola
Justicia montis-salinarum
Justicia moretiana
Justicia moritziana
Justicia morona-santiagoensis
Justicia mossambicensis
Justicia multibracteata
Justicia multicaulis
Justicia multiglandulosa
Justicia myuros
Justicia namatophila
Justicia nana
Justicia neesiana
Justicia nelsonii
Justicia nematocalix
Justicia nemorosa
Justicia neomontana
Justicia nervata
Justicia neurantha
Justicia neurochlamys
Justicia nevlingii
Justicia niassensis
Justicia nigerica
Justicia nilgherrensis
Justicia niokolo-kobae
Justicia nkandlaensis
Justicia nodicaulis
Justicia novogaliciana
Justicia novogranatensis
Justicia nummulus
Justicia nuttii
Justicia nyassana
Justicia oaxacana
Justicia obcordata
Justicia oblongifolia
Justicia obovata
Justicia ochroleuca
Justicia odora
Justicia oellgaardii
Justicia oncodes
Justicia onilahensis
Justicia oranensis
Justicia orbicularis
Justicia orchioides
Justicia oreadum
Justicia oreophila
Justicia ornatopila
Justicia ornithopoda
Justicia orosiensis
Justicia ovalis
Justicia ovatifolia
Justicia pacifica
Justicia pallida
Justicia palmeri
Justicia pampolystachys
Justicia panamense
Justicia panamensis
Justicia panarensis
Justicia paniculata
Justicia parabolica
Justicia paracambi
Justicia paraensis
Justicia parahyba
Justicia parguazensis
Justicia parimensis
Justicia paruana
Justicia parvibracteata
Justicia parvispica
Justicia paspaloides
Justicia pastazana
Justicia patentiflora
Justicia paucifolia
Justicia pedemontana
Justicia pedestris
Justicia pedicellata
Justicia pedropalensis
Justicia peninsularis
Justicia periplocifolia
Justicia perrieri
Justicia petiolaris
Justicia petraea
Justicia petterssonii
Justicia phaeocarpa
Justicia phillipseae
Justicia phillipsiae
Justicia phlebodes
Justicia phlebophylla
Justicia phlomoides
Justicia phyllocalyx
Justicia phyllostachys
Justicia physogaster
Justicia phytolaccoides
Justicia pilosa
Justicia pilosella
Justicia pilzii
Justicia pinensis
Justicia pinguior
Justicia pittieri
Justicia platysepala
Justicia plebeia
Justicia plectranthoides
Justicia plowmanii
Justicia plumbaginifolia
Justicia pluriformis
Justicia poeppigiana
Justicia pohliana
Justicia poilanei
Justicia polita
Justicia polyantha
Justicia polygonoides
Justicia polystachya
Justicia porphyrocoma
Justicia potamogeton
Justicia potamophila
Justicia potarensis
Justicia pozuzoensis
Justicia preussii
Justicia prevostiae
Justicia prietori
Justicia pringlei
Justicia protracta
Justicia pseudohypoestes
Justicia pseudorungia
Justicia pseudospicata
Justicia pseudotenella
Justicia puberula
Justicia pubescens
Justicia pubiflora
Justicia pubigera
Justicia pulgarensis
Justicia purpurea
Justicia purpusii
Justicia pusilla
Justicia pycnophylla
Justicia pyrrhostachya
Justicia quadrifaria
Justicia racemulosa
Justicia radicans
Justicia ramosa
Justicia ramosii
Justicia ramulosa
Justicia readii
Justicia rectiflora
Justicia refractifolia
Justicia refulgens
Justicia regnellii
Justicia reitzii
Justicia remotifolia
Justicia rendlei
Justicia reptabunda
Justicia rhodantha
Justicia rhodesiana
Justicia rhodoides
Justicia rhodoptera
Justicia rhomboidea
Justicia richardii
Justicia richardsiae
Justicia rictus
Justicia riedeliana
Justicia rigida
Justicia riojana
Justicia riparia
Justicia robertii
Justicia rodgersii
Justicia rohrii
Justicia roigii
Justicia romba
Justicia roseopunctata
Justicia rothschuhii
Justicia rubicunda
Justicia rubriflora
Justicia rubrobracteata
Justicia rubropicta
Justicia rubroviolacea
Justicia ruiziana
Justicia runyonii
Justicia rupestris
Justicia rusbyana
Justicia rusbyi
Justicia ruwenzoriensis
Justicia rzedowskii
Justicia sagraeana
Justicia saksuwaniae
Justicia salasiae
Justicia salicifolia
Justicia salma-margaritae
Justicia saltensis
Justicia salvadorensis
Justicia salviiflora
Justicia salvioides
Justicia sambiranensis
Justicia sanchezioides
Justicia sangilensis
Justicia santapaui
Justicia santelisiana
Justicia sarapiquensis
Justicia sarmentosa
Justicia scandens
Justicia scansilis
Justicia scheidweileri
Justicia schenckiana
Justicia schimperiana
Justicia schoensis
Justicia schomburgkiana
Justicia schultesii
Justicia schwackeana
Justicia sciera
Justicia sciota
Justicia scortechinii
Justicia scutifera
Justicia scytophylla
Justicia sebastianopolitanae
Justicia secunda
Justicia segoviaensis
Justicia sejuncta
Justicia sellowiana
Justicia senicula
Justicia sericea
Justicia sericiflora
Justicia serrana
Justicia seslerioides
Justicia sessiliflora
Justicia sessilifolia
Justicia siccanea
Justicia silvicola
Justicia simonisia
Justicia siraensis
Justicia sitiens
Justicia skutchii
Justicia soliana
Justicia sonorae
Justicia soratensis
Justicia soukupii
Justicia sphaerosperma
Justicia spicata
Justicia spicigera
Justicia spiculifera
Justicia spinigera
Justicia spinossisima
Justicia sprucei
Justicia squarrosa
Justicia stachytarphetoides
Justicia stearnii
Justicia steinbachiorum
Justicia stellata
Justicia stenophylla
Justicia sterea
Justicia stereostachya
Justicia straminea
Justicia striata
Justicia strigilis
Justicia striolata
Justicia suarezensis
Justicia subalternans
Justicia subcordatifolia
Justicia subcoriacea
Justicia subcymosa
Justicia subpaniculata
Justicia sulitii
Justicia sulphuriflora
Justicia sumatrana
Justicia superba
Justicia symphyantha
Justicia tabascina
Justicia tarapotensis
Justicia teletheca
Justicia telloensis
Justicia tenera
Justicia tenuiflora
Justicia tenuifolia
Justicia tenuis
Justicia tenuissima
Justicia tenuistachys
Justicia thunbergioides
Justicia thymifolia
Justicia tianguensis
Justicia tinctoriella
Justicia tobagensis
Justicia tocantina
Justicia tomentosula
Justicia tonduzii
Justicia toroensis
Justicia torresii
Justicia tranquebariensis
Justicia tremulifolia
Justicia trianae
Justicia trichocarpa
Justicia trichophylla
Justicia trichotoma
Justicia trifoliata
Justicia triloba
Justicia tristis
Justicia trivialis
Justicia tubulosa
Justicia turneri
Justicia tutukuensis
Justicia tuxtlensis
Justicia tweediana
Justicia udzungwaensis
Justicia ukagurensis
Justicia ulei
Justicia umbricola
Justicia unguiculata
Justicia unyorensis
Justicia upembensis
Justicia urophylla
Justicia uvida
Justicia uxpanapensis
Justicia vagabunda
Justicia valerii
Justicia valerioi
Justicia valvata
Justicia vasculosa
Justicia vasculosoides
Justicia velizii
Justicia venalis
Justicia ventricosa
Justicia venulosa
Justicia veracruzana
Justicia veraguensis
Justicia veridiflavescens
Justicia vernalis
Justicia vicina
Justicia vidalii
Justicia violaceotincta
Justicia virgata
Justicia viridescens
Justicia viridifavescens
Justicia viridiflavescens
Justicia vixspicata
Justicia volkeri
Justicia wallnoeferi
Justicia warmingii
Justicia warnockii
Justicia wasshauseniana
Justicia wasshausenii
Justicia weberbaueri
Justicia wendtii
Justicia whytei
Justicia williamsii
Justicia wynaadensis
Justicia xantholeuca
Justicia xerobatica
Justicia xerophila
Justicia xipotensis
Justicia xylopoda
Justicia xylosteoides
Justicia yhuensis
Justicia yungensis
Justicia yunnanensis
Justicia yurimaguensis
Justicia yuyoensis
Justicia zamudioi
Justicia zapoteca
Justicia zopilotensis
Juttadinteria albata
Juttadinteria attenuata
Juttadinteria ausensis
Juttadinteria deserticola
Juttadinteria simpsonii""".strip().split("\n")

# ══════════════════════════════════════════════
#  LISTE DES PLANTES TOXIQUES
#  ⚠ À REMPLACER à chaque nouvelle lettre
#  → Mettre ici uniquement les noms présents
#    dans PLANTES qui sont toxiques.
#    Le nom doit être identique (même casse).
#  → Si aucune plante toxique : laisser []
# ══════════════════════════════════════════════

PLANTES_TOXIQUES = """Jatropha aceroides
Jatropha aethiopica
Jatropha afrotuberosa
Jatropha alamanii
Jatropha andrieuxii
Jatropha angustidens
Jatropha angustifolia
Jatropha arborea
Jatropha aspleniifolia
Jatropha atacorensis
Jatropha bartlettii
Jatropha baumii
Jatropha botswanica
Jatropha breviloba
Jatropha bullockii
Jatropha calcarea
Jatropha campestris
Jatropha canescens
Jatropha capensis
Jatropha cardiophylla
Jatropha cathartica
Jatropha catingae
Jatropha ceballosii
Jatropha chamelensis
Jatropha chevalieri
Jatropha ciliata
Jatropha cinerea
Jatropha clavuligera
Jatropha collina
Jatropha conzattii
Jatropha cordata
Jatropha costaricensis
Jatropha cuneata
Jatropha curcas
Jatropha decipiens
Jatropha decumbens
Jatropha dehganii
Jatropha dhofarica
Jatropha dichtar
Jatropha dioica
Jatropha dissecta
Jatropha divaricata
Jatropha elbae
Jatropha ellenbeckii
Jatropha elliptica
Jatropha erythropoda
Jatropha euarguta
Jatropha excisa
Jatropha fremontioides
Jatropha gallabatensis
Jatropha galvanii
Jatropha gaumeri
Jatropha giffordiana
Jatropha glandulifera
Jatropha glauca
Jatropha gossypiifolia
Jatropha grossidentata
Jatropha guaranitica
Jatropha hastata
Jatropha hastifolia
Jatropha hernandiifolia
Jatropha heynei
Jatropha hildebrandtii
Jatropha hippocastanifolia
Jatropha hirsuta
Jatropha humboldtiana
Jatropha humifusa
Jatropha hypogyna
Jatropha integerrima
Jatropha intermedia
Jatropha isabellei
Jatropha jaimejimenezii
Jatropha kamerunica
Jatropha krusei
Jatropha L.
Jatropha lagarinthoides
Jatropha latifolia
Jatropha longibracteata
Jatropha macrantha
Jatropha macrocarpa
Jatropha macrophylla
Jatropha macrorhiza
Jatropha maheshwarii
Jatropha malacophylla
Jatropha marginata
Jatropha marmorata
Jatropha martiusii
Jatropha mcvaughii
Jatropha microdonta
Jatropha mirandana
Jatropha miskatensis
Jatropha mollissima
Jatropha monroi
Jatropha moranii
Jatropha multifida
Jatropha mutabilis
Jatropha nana
Jatropha napaeifolia
Jatropha natalensis
Jatropha neopauciflora
Jatropha neriifolia
Jatropha nogalensis
Jatropha nudicaulis
Jatropha obbiadensis
Jatropha oblanceolata
Jatropha orangeana
Jatropha ortegae
Jatropha osteocarpa
Jatropha pachypoda
Jatropha pachyrrhiza
Jatropha paganuccii
Jatropha palmatifida
Jatropha palmatipartita
Jatropha paradoxa
Jatropha pauciflora
Jatropha pedersenii
Jatropha peiranoi
Jatropha pelargoniifolia
Jatropha peltata
Jatropha pereziae
Jatropha prunifolia
Jatropha pseudocurcas
Jatropha purpurea
Jatropha ribifolia
Jatropha riojae
Jatropha rivae
Jatropha robecchii
Jatropha rufescens
Jatropha rzedowskii
Jatropha scaposa
Jatropha schlechteri
Jatropha schweinfurthii
Jatropha seineri
Jatropha sotoi-nunyezii
Jatropha spicata
Jatropha spinosa
Jatropha standleyi
Jatropha stephani
Jatropha stevensii
Jatropha stipulacea
Jatropha stuhlmannii
Jatropha sympetala
Jatropha tanjorensis
Jatropha tehuantepecana
Jatropha tertiaria
Jatropha tetracantha
Jatropha tlalcozotitlanensis
Jatropha trifida
Jatropha tropaeolifolia
Jatropha tupifolia
Jatropha uncinulata
Jatropha unicostata
Jatropha urens
Jatropha variabilis
Jatropha variegata
Jatropha variifolia
Jatropha velutina
Jatropha vernicosa
Jatropha villosa
Jatropha weberbaueri
Jatropha websteri
Jatropha weddeliana
Jatropha woodii
Jatropha zeyheri
Juniperus ambigens
Juniperus angosturana
Juniperus arizonica
Juniperus ashei
Juniperus barbadensis
Juniperus bermudiana
Juniperus blancoi
Juniperus brevifolia
Juniperus californica
Juniperus canariensis
Juniperus cedrus
Juniperus cerropastorensis
Juniperus chinensis
Juniperus coahuilensis
Juniperus comitana
Juniperus communis
Juniperus convallium
Juniperus corneyana
Juniperus cupressifolia
Juniperus deppeana
Juniperus drupacea
Juniperus durangensis
Juniperus excelsa
Juniperus flaccida
Juniperus foetidissima
Juniperus formosana
Juniperus gamboana
Juniperus gracilior
Juniperus herragudensis
Juniperus horizontalis
Juniperus hypnoides
Juniperus indica
Juniperus jaliscana
Juniperus komarovii
Juniperus L.
Juniperus mexicana
Juniperus monosperma
Juniperus monticola
Juniperus nepalensis
Juniperus occidentalis
Juniperus osteosperma
Juniperus oxycedrus
Juniperus palanciana
Juniperus pfitzeriana
Juniperus phoenicea
Juniperus pinchotii
Juniperus pingii
Juniperus procera
Juniperus procumbens
Juniperus prostrata
Juniperus przewalskii
Juniperus pseudosabina
Juniperus recurva
Juniperus rigida
Juniperus sabina
Juniperus saltillensis
Juniperus saltuaria
Juniperus saxicola
Juniperus scopulorum
Juniperus semiglobosa
Juniperus sheppardii
Juniperus sinensis
Juniperus squamata
Juniperus squamosa
Juniperus standleyi
Juniperus taiwaniana
Juniperus taxifolia
Juniperus thurifera
Juniperus tibetica
Juniperus virginiana""".strip().split("\n")

# Convertir en set pour une recherche rapide
TOXIQUES_SET = set(p.strip() for p in PLANTES_TOXIQUES if p.strip())

# ══════════════════════════════════════════════
#  STATISTIQUES (affichées à la fin)
# ══════════════════════════════════════════════

def afficher_stats_toxicite():
    total       = len(PLANTES)
    nb_toxiques = len(TOXIQUES_SET)
    nb_saines   = total - nb_toxiques
    print(f"\n  🌿 Non toxiques : {nb_saines}")
    print(f"  ☠  Toxiques     : {nb_toxiques}")
    print(f"\n  Plantes toxiques listées :")
    for nom in sorted(TOXIQUES_SET):
        print(f"    · {nom}")

# ══════════════════════════════════════════════
#  UTILITAIRES
# ══════════════════════════════════════════════

def slugify(nom):
    """Convertit un nom de plante en nom de fichier HTML."""
    s = nom.lower()
    for src, dst in [('à','a'),('â','a'),('ä','a'),('é','e'),('è','e'),('ê','e'),
                     ('ë','e'),('î','i'),('ï','i'),('ô','o'),('ö','o'),('ù','u'),
                     ('û','u'),('ü','u'),('ç','c'),('ñ','n'),('&',''),('.',''),
                     (',',''),("'",''),('×','x'),('×','-x-')]:
        s = s.replace(src, dst)
    s = re.sub(r'[^a-z0-9]+', '-', s)
    s = s.strip('-')
    return s


def recuperer_gbif(nom):
    """Récupère famille, ordre, règne et GBIF ID depuis l'API GBIF."""
    try:
        r = requests.get(
            "https://api.gbif.org/v1/species/match",
            params={"name": nom, "strict": False},
            headers=HEADERS, timeout=10
        )
        data = r.json()
        if data.get("matchType") == "NONE":
            return {}
        return {
            "gbif_id":  data.get("usageKey", ""),
            "famille":  data.get("family", ""),
            "ordre":    data.get("order", ""),
            "classe":   data.get("class", ""),
            "division": data.get("phylum", ""),
            "regne":    data.get("kingdom", "Plantae"),
            "genre":    data.get("genus", ""),
        }
    except:
        return {}


def generer_html(nom, slug, gbif, est_toxique=False):
    """Génère le HTML complet d'une page plante."""
    famille  = gbif.get("famille", "")
    ordre    = gbif.get("ordre", "")
    classe   = gbif.get("classe", "")
    division = gbif.get("division", "")
    regne    = gbif.get("regne", "Plantae")
    genre    = gbif.get("genre", "")
    gbif_id  = gbif.get("gbif_id", "")

    gbif_block = ""
    if gbif_id:
        gbif_block = f"""
            <div class="sg-label">Référence GBIF</div>
            <div class="sg-id">{gbif_id}</div>
            <a href="https://www.gbif.org/species/{gbif_id}" target="_blank" rel="noopener" class="sg-link">Voir sur GBIF ↗</a>"""

    # Construire les lignes taxonomiques
    taxo_rows = ""
    taxo_data = [
        ("Règne",    regne),
        ("Division", division),
        ("Classe",   classe),
        ("Ordre",    ordre),
        ("Famille",  famille),
        ("Genre",    genre),
    ]
    for label, valeur in taxo_data:
        if valeur:
            if label == "Genre":
                taxo_rows += f'<div class="taxo-row"><dt>{label}</dt><dd><em>{valeur}</em></dd></div>\n'
            else:
                taxo_rows += f'<div class="taxo-row"><dt>{label}</dt><dd>{valeur}</dd></div>\n'

    famille_tag = famille or "Indéterminée"

    # ── Badge toxicité ──────────────────────────────────────────
    if est_toxique:
        badge_toxicite = '<span class="badge badge--toxic">✕ Toxique</span>'
    else:
        badge_toxicite = '<span class="badge badge--safe">✓ Non toxique</span>'

    # ── Section précautions adaptée ─────────────────────────────
    if est_toxique:
        precaution_toxique = """
            <div class="precaution-card precaution-card--danger">
              <span class="precaution-ico">☠️</span>
              <div><strong>Plante toxique</strong><br/>
              Cette espèce est considérée comme toxique. Ne pas ingérer et tenir hors de portée des enfants et des animaux.</div>
            </div>"""
    else:
        precaution_toxique = """
            <div class="precaution-card precaution-card--safe">
              <span class="precaution-ico">✅</span>
              <div><strong>Non toxique</strong><br/>
              Cette espèce n'est pas répertoriée comme toxique. Toutefois, consultez un professionnel avant tout usage.</div>
            </div>"""

    # ── Thème rouge injecté en inline si toxique ───────────────
    if est_toxique:
        style_toxique = """
  <style>
    /* ── Surcharge thème toxique ── */
    :root {
      --bg:           #0f0808;
      --card:         #1a0d0d;
      --border:       rgba(180, 60, 60, 0.25);
      --accent:       #e74c3c;
      --accent-dark:  #c0392b;
      --accent-pale:  #3d1010;
      --text:         #d4b8b8;
      --text-muted:   #8a6060;
    }
    body { background: var(--bg); color: var(--text); }
    nav  { background: rgba(15,8,8,0.97); border-color: var(--border); }
    .nav-logo em { color: var(--accent); }
    .nav-links a:hover { color: var(--accent); }
    .plant-header { background: radial-gradient(ellipse at 50% 100%, rgba(192,57,43,0.12) 0%, transparent 60%); }
    .plant-family-tag { background: var(--accent-pale); color: var(--accent); border-color: var(--accent-dark); }
    .badge--toxic { background: #c0392b; color: #fff; }
    .plant-sci-name { color: #f0d8d8; }
    .section-heading { color: var(--accent); border-color: var(--border); }
    .sh-num { color: var(--accent-dark); }

    /* ── Sidebar : bordures adoucies ── */
    .plant-sidebar { border-color: rgba(180,60,60,0.15); background: var(--card); }
    .sidebar-title {
      color: var(--accent);
      border-bottom: 1px solid rgba(180,60,60,0.15);
      padding-bottom: 0.5rem;
    }
    .sidebar-divider { border-color: rgba(180,60,60,0.12); }

    /* ── Liens TOC ── */
    .toc-link { color: #a07070; }
    .toc-link:hover, .toc-link--active { color: var(--accent); }

    /* ── Précautions ── */
    .precaution-card--danger { border-left: 4px solid #c0392b; background: #1a0d0d; }
    .precaution-card--info { border-color: var(--border); background: var(--card); }

    /* ── Divers ── */
    .plant-divider { color: var(--accent-dark); opacity: 0.5; }
    footer { border-color: var(--border); background: var(--bg); color: var(--text-muted); }
    .breadcrumb-bar { background: rgba(15,8,8,0.95); border-color: var(--border); }
    .breadcrumb-inner a { color: var(--accent); }

    /* ── Bloc GBIF sidebar : beige → rouge clair ── */
    .sg-label {
      color: #a07070;
      font-size: 0.78rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }
    .sg-id {
      color: #e08080;
      font-size: 1.4rem;
      font-family: 'Cormorant SC', serif;
    }
    .sg-link { color: #c06060 !important; text-decoration: underline; text-underline-offset: 3px; }
    .sg-link:hover { color: var(--accent) !important; }

    /* ── Placeholder image : fond sombre ── */
    .plant-img-placeholder {
      background: var(--card) !important;
      border: 1px solid rgba(180,60,60,0.2) !important;
    }
    .placeholder-icon { opacity: 0.25 !important; }
    .placeholder-text { color: #7a4040 !important; }

    /* ── Bandeau danger ── */
    .warning-banner {
      background: #c0392b;
      color: #fff;
      text-align: center;
      padding: 0.65rem 2rem;
      font-size: 0.88rem;
      letter-spacing: 0.07em;
      font-family: 'EB Garamond', serif;
    }
  </style>"""
        warning_banner = """
  <!-- ══ BANDEAU DANGER ══ -->
  <div class="warning-banner">
    ⚠ <strong>Plante toxique</strong> — Ne pas ingérer · Tenir hors de portée des enfants et des animaux
  </div>"""
    else:
        style_toxique  = ""
        warning_banner = ""

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{nom} — Herbarium</title>
  <meta name="description" content="{nom} — fiche botanique : description, famille {famille_tag}, usages et précautions. Encyclopédie Herbarium." />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Playfair+Display:ital,wght@0,600;0,700;1,600&family=Cormorant+SC:wght@400;500;600&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="../../style.css" />
  <link rel="stylesheet" href="../../plant.css" />{style_toxique}
</head>
<body>
{warning_banner}
  <!-- ══ NAVIGATION ══ -->
  <nav>
    <a class="nav-logo" href="../../index.html"><em>H</em>erbarium</a>
    <ul class="nav-links" id="nav-links">
      <li><a href="../../encyclopedie/index_encyclopedie.html">Encyclopédie</a></li>
      <li><a href="../../toxique.html">Toxicité</a></li>
      <li><a href="../../sommaire.html">Sommaire</a></li>
      <li><a href="#">Boutique</a></li>
      <li><a href="#">À propos</a></li>
    </ul>
    <button class="hamburger" id="hamburger" aria-label="Menu">
      <span></span><span></span><span></span>
    </button>
  </nav>

  <!-- ══ FIL D'ARIANE ══ -->
  <div class="breadcrumb-bar">
    <div class="breadcrumb-inner">
      <a href="../../index.html">Accueil</a>
      <span class="bc-sep">›</span>
      <a href="../../encyclopedie/index_encyclopedie.html">Encyclopédie</a>
      <span class="bc-sep">›</span>
      <a href="../../encyclopedie/F.html">Espèces en « F »</a>
      <span class="bc-sep">›</span>
      <span class="bc-current"><em>{nom}</em></span>
    </div>
  </div>

  <main class="plant-main">

    <!-- ══ EN-TÊTE ══ -->
    <header class="plant-header">
      <div class="plant-header-inner">

        <!-- Colonne texte -->
        <div class="plant-header-text">
          <div class="plant-meta-row">
            <span class="plant-family-tag">{famille_tag}</span>
            <span class="plant-badges">{badge_toxicite}</span>
          </div>

          <h1 class="plant-sci-name">{nom}</h1>

          <p class="plant-common-names">
            <span class="common-label">Noms communs :</span>
            <span class="common-list">{nom}</span>
          </p>

          <dl class="plant-taxo">
            {taxo_rows}
          </dl>
        </div>

        <!-- Image -->
        <div class="plant-image-wrap">
          <div class="plant-image-frame">
            <div class="plant-img-placeholder" id="img-placeholder">
              <span class="placeholder-icon">🌿</span>
              <span class="placeholder-text">Image non disponible</span>
            </div>
          </div>
          <div class="img-deco img-deco--tl"></div>
          <div class="img-deco img-deco--br"></div>
        </div>

      </div>

      <div class="header-ornament">
        <svg viewBox="0 0 400 20" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <line x1="0" y1="10" x2="160" y2="10" stroke="currentColor" stroke-width="0.5" opacity="0.35"/>
          <path d="M180 10 Q190 2 200 10 Q210 18 220 10" stroke="currentColor" stroke-width="0.8" fill="none" opacity="0.5"/>
          <circle cx="200" cy="10" r="2" fill="currentColor" opacity="0.4"/>
          <line x1="240" y1="10" x2="400" y2="10" stroke="currentColor" stroke-width="0.5" opacity="0.35"/>
        </svg>
      </div>
      <!-- ── Fondu bas du header vers le background ── -->
      <div style="height:60px;background:linear-gradient(to bottom,transparent,var(--bg,#0d0b09));pointer-events:none;margin-top:-20px;"></div>
    </header>

    <!-- ══ CORPS ══ -->
    <div class="plant-body-wrap">
      <div class="plant-body-inner">

        <!-- Description -->
        <section class="plant-section" id="description">
          <h2 class="section-heading">
            <span class="sh-num">I.</span> Description botanique
          </h2>
          <div class="plant-desc-text">
            <p><em>{nom}</em> est une espèce végétale de la famille des {famille_tag}.</p>
            <p>Les données détaillées sur cette espèce sont en cours de rédaction dans notre encyclopédie.</p>
          </div>
        </section>

        <div class="plant-divider"><span>✦</span></div>

        <!-- Précautions -->
        <section class="plant-section" id="precautions">
          <h2 class="section-heading">
            <span class="sh-num">II.</span> Précautions &amp; Informations
          </h2>
          <div class="precaution-grid">
            {precaution_toxique}
            <div class="precaution-card precaution-card--info">
              <span class="precaution-ico">💊</span>
              <div><strong>Usage médical</strong><br/>
              Consulter un professionnel de santé avant tout usage thérapeutique.</div>
            </div>
            <div class="precaution-card precaution-card--info">
              <span class="precaution-ico">🌿</span>
              <div><strong>Identification</strong><br/>
              Assurez-vous de l'identification correcte de l'espèce avant toute utilisation.</div>
            </div>
          </div>
        </section>

      </div><!-- /plant-body-inner -->

      <!-- Sidebar -->
      <aside class="plant-sidebar">
        <div class="sidebar-sticky">
          <div class="sidebar-title">Sommaire</div>
          <nav class="sidebar-toc">
            <a href="#description" class="toc-link toc-link--active">I. Description</a>
            <a href="#precautions" class="toc-link">II. Précautions</a>
          </nav>

          <div class="sidebar-divider"></div>

          <div class="sidebar-gbif">
            {gbif_block}
          </div>
        </div>
      </aside>

    </div><!-- /plant-body-wrap -->
  </main>

  <!-- ══ FOOTER ══ -->
  <footer>
    <strong>Herbarium</strong> — Encyclopédie botanique &nbsp;·&nbsp;
    Données <a href="https://www.gbif.org" target="_blank" rel="noopener" style="color:var(--accent)">GBIF</a> &nbsp;·&nbsp;
    <em>Usage informatif uniquement — ne remplace pas un avis médical</em>
    &nbsp;·&nbsp;
    <a href="../../encyclopedie/J.html" style="color:var(--accent)">← Retour aux espèces en J</a>
  </footer>

  <script src="../../plant.js"></script>
  <script>
    document.getElementById('hamburger').addEventListener('click', function () {{
      this.classList.toggle('open');
      document.getElementById('nav-links').classList.toggle('open');
    }});
  </script>
</body>
</html>"""


# ══════════════════════════════════════════════
#  LOG
# ══════════════════════════════════════════════

def charger_log():
    if Path(LOG_FILE).exists():
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def sauvegarder_log(log):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


# ══════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════

def main():
    print("═" * 55)
    print("  Herbarium — Génération pages HTML Lettre U")
    print("═" * 55)

    # Vérifier cohérence : toutes les toxiques sont dans PLANTES
    noms_plantes = set(p.strip() for p in PLANTES if p.strip())
    inconnues = TOXIQUES_SET - noms_plantes
    if inconnues:
        print("\n⚠️  ATTENTION — Ces noms sont dans PLANTES_TOXIQUES")
        print("   mais absents de PLANTES (vérifier la casse) :")
        for n in sorted(inconnues):
            print(f"   · {n}")
        print()

    afficher_stats_toxicite()
    print()

    dossier = Path(DOSSIER_SORTIE)
    dossier.mkdir(parents=True, exist_ok=True)

    log = charger_log()
    total = len(PLANTES)
    print(f"📋 {total} plantes à traiter\n")

    compteurs = {"ok": 0, "skip": 0, "erreur": 0, "toxiques": 0}

    for i, nom in enumerate(PLANTES, 1):
        nom = nom.strip()
        if not nom:
            continue

        slug = slugify(nom)
        nom_fichier = f"{slug}.html"
        chemin = dossier / nom_fichier
        est_toxique = nom in TOXIQUES_SET

        icone_tox = "☠️ " if est_toxique else "🌿"
        print(f"[{i}/{total}] {icone_tox} {nom}")

        if log.get(nom_fichier) == "ok" and chemin.exists():
            print(f"  ⏭  Déjà généré")
            compteurs["skip"] += 1
            continue

        # Récupérer infos GBIF
        gbif = recuperer_gbif(nom)
        if gbif.get("famille"):
            print(f"  📗 {gbif['famille']}")
        else:
            print(f"  ⚠  Famille non trouvée sur GBIF")

        # Générer et sauvegarder
        html = generer_html(nom, slug, gbif, est_toxique=est_toxique)
        chemin.write_text(html, encoding="utf-8")

        log[nom_fichier] = "ok"
        sauvegarder_log(log)
        compteurs["ok"] += 1
        if est_toxique:
            compteurs["toxiques"] += 1

        time.sleep(0.2)  # Respecter l'API GBIF

    print("\n" + "═" * 55)
    print(f"  ✅ {compteurs['ok']} générées  |  "
          f"⏭  {compteurs['skip']} ignorées  |  "
          f"✗ {compteurs['erreur']} erreurs")
    print(f"  ☠  {compteurs['toxiques']} pages toxiques générées (thème rouge)")
    print(f"  📂 Fichiers dans : {DOSSIER_SORTIE}")
    print("═" * 55)


if __name__ == "__main__":
    main()
