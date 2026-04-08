#!/usr/bin/env python3
"""
Herbarium — Générateur de pages HTML pour les plantes U
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

DOSSIER_SORTIE  = "./U_Plante_page"              # ← Dossier de sortie         ex: "./V_Plante_page"
LETTRE          = "U"                            # ← Lettre courante            ex: "V"
LETTRE_HTML     = "U.html"                       # ← Fichier index de la lettre ex: "V.html"
LOG_FILE        = "generation_log_pages_U.json"  # ← Fichier log                ex: "generation_log_pages_V.json"
HEADERS         = {"User-Agent": "Herbarium-Bot/1.0"}

# ══════════════════════════════════════════════
#  LISTE DES PLANTES
#  ⚠ À REMPLACER à chaque nouvelle lettre
#  → Coller ici toutes les plantes de la lettre,
#    une par ligne, sans numérotation.
# ══════════════════════════════════════════════

PLANTES = """Uapaca acuminata
Uapaca ambanjensis
Uapaca amplifolia
Uapaca Baill.
Uapaca bojeri
Uapaca corbisieri
Uapaca densifolia
Uapaca ferruginea
Uapaca guineensis
Uapaca heudelotii
Uapaca kirkiana
Uapaca lissopyrena
Uapaca littoralis
Uapaca mole
Uapaca niangadoumae
Uapaca nitida
Uapaca pilosa
Uapaca pynaertii
Uapaca robynsii
Uapaca sansibarica
Uapaca teusczii
Uapaca thouarsii
Uapaca togoensis
Uapaca vanhouttei
Ubiquitoxylon E.A.Wheeler, 2019
Udora Nutt.
Udotea argentea
Udotea caribaea
Udotea conglutinata
Udotea cyathiformis
Udotea dixonii
Udotea dotyi
Udotea fibrosa
Udotea flabelliformis
Udotea flabellum
Udotea geppii
Udotea geppiorum
Udotea J.V.F.Lamouroux, 1812
Udotea javensis
Udotea looensis
Udotea luna
Udotea orientalis
Udotea palmetta
Udotea polychotomis
Udotea spinulosa
Udotea unistratea
Udoteaceae
Uebelinia Hochst.
Uebelmannia Buining
Uebelmannia buiningii
Uebelmannia gummifera
Uebelmannia pectinifera
Uechtritzia Freyn
Ugamia angrenica
Ugena Cav.
Ugni candollei
Ugni molinae
Ugni myricoides
Ugni selkirkii
Ugni Turcz.
Uittienia modesta
Ulea Müll.Hal.
Ulea palmicola
Ulea paraguensis
Uleanthus erythrinoides
Uleanthus Harms
Ulearum donburnsii
Ulearum Engl.
Ulearum sagittatum
Uleastrum octoblephare
Uleiorchis Hoehne
Uleiorchis longipedicellata
Uleiorchis ulei
Uleobryum Broth.
Uleobryum naganoi
Uleobryum occultum
Uleobryum peruvianum
Uleophytum scandens
Ulex argenteus
Ulex australis
Ulex baeticus
Ulex borgiae
Ulex breoganii
Ulex canescens
Ulex cantabricus
Ulex dalilae
Ulex densus
Ulex eriocladus
Ulex europaeus
Ulex europaeus x Ulex gallii
Ulex gallii
Ulex genistoides
Ulex jussiaei
Ulex L.
Ulex lagrezii
Ulex lucidus
Ulex lusitanicus
Ulex micranthus
Ulex minor
Ulex parviflorus
Ulex provincialis
Ulex revurvatus
Ulex richteri
Ulex spicatus
Ulex welwitschianus
Ullmanniaceae
Ullucus Caldas
Ullucus tuberosus
Ulmaceae
Ulmaria Hill
Ulmaria Mill.
Ulminium Unger, 1842
Ulmiphyllum brookense
Ulmites microphylla
Ulmophyllum densinerve
Ulmus affinis
Ulmus alata
Ulmus americana
Ulmus androssowii
Ulmus arbuscula
Ulmus basicordata
Ulmus berandii
Ulmus bergmanniana
Ulmus betuloides
Ulmus boissieri
Ulmus brandisiana
Ulmus braunii
Ulmus castaneifolia
Ulmus changii
Ulmus chenmoui
Ulmus chumlia
Ulmus cornubiensis
Ulmus crassifolia
Ulmus dampieri
Ulmus davidiana
Ulmus effusa
Ulmus elliptica
Ulmus elongata
Ulmus erosa
Ulmus erythrocarpa
Ulmus exoniensis
Ulmus gaussenii
Ulmus glabra
Ulmus glabra x minor
Ulmus glaucescens
Ulmus harbinensis
Ulmus hilliae
Ulmus hollandica
Ulmus intermedia
Ulmus ismaelis
Ulmus kunmingensis
Ulmus L.
Ulmus laciniata
Ulmus laevis
Ulmus lamellosa
Ulmus lanceifolia
Ulmus longifolia
Ulmus macrocarpa
Ulmus mesocarpa
Ulmus mexicana
Ulmus microcarpa
Ulmus minima
Ulmus minor
Ulmus newberryi
Ulmus orbicularis
Ulmus parschlugiana
Ulmus parvifolia
Ulmus pendula
Ulmus pitteursii
Ulmus plurinervia
Ulmus procera
Ulmus prunifolia
Ulmus pseudofulva
Ulmus pseudopropinqua
Ulmus pumila
Ulmus rhamnifolia
Ulmus rubra
Ulmus rugosa
Ulmus sativa
Ulmus scabra
Ulmus serotina
Ulmus sibirica
Ulmus sorbifolia
Ulmus speciosa
Ulmus szechuanica
Ulmus tenuinervis
Ulmus thomasii
Ulmus uyematsui
Ulmus villosa
Ulmus viminalis
Ulmus wallichiana
Ulmus wardii
Ulmus × notha Wilhelm & G.Ware
Ulodendron Lindley & W.Hutton, 1832
Ulodendron majus
Ulosarcina Gontcharov et al., 2022
Ulospermum Pomel, 1849
Ulota angustissima
Ulota aurantiaca
Ulota barclayi
Ulota billbuckii
Ulota bruchii
Ulota calvescens
Ulota coarctata
Ulota crispa
Ulota crispula
Ulota curvifolia
Ulota D.Mohr
Ulota delicata
Ulota drummondii
Ulota ecklonii
Ulota eurystoma
Ulota fuegiana
Ulota germana
Ulota gigantospora
Ulota glabella
Ulota hutchinsiae
Ulota intermedia
Ulota japonica
Ulota longifolia
Ulota lutea
Ulota luteola
Ulota macrocalycina
Ulota macrospora
Ulota magellanica
Ulota maltana
Ulota megalospora
Ulota membranata
Ulota morrisonensis
Ulota obtusiuscula
Ulota panchengiana
Ulota perbreviseta
Ulota perichaetialis
Ulota pusilla
Ulota pycnophylla
Ulota reptans
Ulota rhytiore
Ulota robusta
Ulota rubella
Ulota schmidii
Ulota ventricosa
Ulota viridis
Ulota yakushimensis
Ulota yunnanensis
Ulothrix
Ulothrix aequalis
Ulothrix cylindrica
Ulothrix flacca
Ulothrix implexa
Ulothrix Kützing, 1833
Ulothrix laetevirens
Ulothrix mucosa
Ulothrix palusalsa
Ulothrix rorida
Ulothrix speciosa
Ulothrix subflaccida
Ulothrix tenerrima
Ulothrix tenuissima
Ulothrix zonata
Ulotrichaceae
Ulotrichales
Ulva
Ulva Adans.
Ulva adhaerens
Ulva angusta
Ulva aragoensis
Ulva arasakii
Ulva arbuscula
Ulva ardreana
Ulva australis
Ulva batuffolosa
Ulva belangeri
Ulva brisbanensis
Ulva californica
Ulva chaetomorphoides
Ulva clathrata
Ulva compressa
Ulva costata
Ulva croatica
Ulva enteromorpha
Ulva expansa
Ulva fenestrata
Ulva finissima
Ulva flexuosa
Ulva gigantea
Ulva hookeriana
Ulva intestinalis
Ulva intestinaloides
Ulva kylinii
Ulva lacinulata
Ulva lactuca
Ulva limnetica
Ulva Linnaeus, 1753
Ulva linza
Ulva linzoides
Ulva lobata
Ulva meridionalis
Ulva ohnoi
Ulva olivacens
Ulva paradoxa
Ulva parva
Ulva paschima
Ulva pennata
Ulva pilifera
Ulva piritoka
Ulva planiramosa
Ulva pluriramosa
Ulva polyclada
Ulva prolifera
Ulva proliferoides
Ulva pseudocurvata
Ulva pseudolinza
Ulva pseudorotundata
Ulva radiata
Ulva ralfsii
Ulva reticulata
Ulva rigida
Ulva sapora
Ulva schousboei
Ulva scolopendra
Ulva siganiphyllia
Ulva sordida
Ulva spinulosa
Ulva splitiana
Ulva spumosa
Ulva stenophylla
Ulva stenophylloides
Ulva taeniata
Ulva tanneri
Ulva tenera
Ulva tentaculosa
Ulva tepida
Ulva torta
Ulva uncialis
Ulva vexata
Ulvaceae
Ulvales
Ulvaria obscura
Ulvaria Ruprecht, 1850
Ulvaria shepherdii
Ulvaria splendens
Ulvella
Ulvella calcicola
Ulvella cingens
Ulvella cladophorae
Ulvella endostraca
Ulvella heteroclada
Ulvella inflata
Ulvella lens
Ulvella leptochaete
Ulvella operculata
Ulvella P.L.Crouan & H.M.Crouan, 1859
Ulvella pachypes
Ulvella perfurcata
Ulvella ramulosa
Ulvella repens
Ulvella reticulata
Ulvella scutata
Ulvella setchellii
Ulvella testarum
Ulvella viridis
Ulvella wittrockii
Ulvophyceae
Umaltolepis coleoptera
Umbellaphyllites E.S.Rasskazova, 1961
Umbellaphyllites neuburgianus
Umbellifera Honigberger
Umbelliferae
Umbelliferospermum latahense
Umbellula K.B.Korde
Umbellularia californica
Umbellularia Nutt.
Umbilicus affinis
Umbilicus botryoides
Umbilicus chloranthus
Umbilicus DC.
Umbilicus heylandianus
Umbilicus horizontalis
Umbilicus luteus
Umbilicus mirus
Umbilicus oppositifolius
Umbilicus paniculiformis
Umbilicus parviflorus
Umbilicus patens
Umbilicus rupestris
Umbilicus schmidtii
Umbilicus tropaeolifolius
Umbonatisporites F.A.Hibbert & W.S.Lacey, 1969
Umbraria microphylla
Umbraria veronicoides
Umbraulva amamiensis
Umbraulva dangeardii
Umbraulva E.H.Bae & I.K.Lee, 2001
Umbraulva japonica
Umbraulva kuaweuweu
Umkomasia H.H.Thomas, 1931
Umkomasia macleani
Umkomasia polycarpa
Umkomasiaceae
Umtiza listeriana
Unanuea Ruiz & Pav. ex Pennell
Uncaria acida
Uncaria africana
Uncaria angolensis
Uncaria attenuata
Uncaria bernaysii
Uncaria borneensis
Uncaria Burch.
Uncaria callophylla
Uncaria canescens
Uncaria cordata
Uncaria donisii
Uncaria elliptica
Uncaria gambir
Uncaria guianensis
Uncaria hirsuta
Uncaria homomalla
Uncaria jasminiflora
Uncaria kunstleri
Uncaria laevigata
Uncaria lanosa
Uncaria longiflora
Uncaria macrophylla
Uncaria nervosa
Uncaria orientalis
Uncaria ovata
Uncaria perrottetii
Uncaria pilosa
Uncaria rhynchophylla
Uncaria roxburghiana
Uncaria scandens
Uncaria schlenckerae
Uncaria Schreb.
Uncaria sessilifolia
Uncaria sessilifructus
Uncaria sinensis
Uncaria speciosa
Uncaria sterrophylla
Uncaria tomentosa
Uncaria velutina
Uncarina abbreviata
Uncarina ankaranensis
Uncarina decaryi
Uncarina grandidieri
Uncarina ihlenfeldtiana
Uncarina leandrii
Uncarina leptocarpa
Uncarina peltata
Uncarina perrieri
Uncarina platycarpa
Uncarina roeoesliana
Uncarina sakalava
Uncarina stellulifera
Uncifera acuminata
Uncifera dalatensis
Uncifera lancifolia
Uncifera Lindl.
Uncifera obtusifolia
Uncifera thailandica
Uncinia brevicaulis
Unclejackia crispifolia
Unclejackia longisetula
Undulatisporites H.D.Pflug, 1953
Undulatisporites sinuosis
Undulatisporites undulapolus
Undulifilum symbioticum
Ungdarella stellata
Ungdarella V.P.Maslov, 1956
Ungdarellaceae
Ungeria floribunda
Ungeria Schott & Endl.
Ungernia Bunge
Ungernia ferganica
Ungernia flava
Ungernia oligostroma
Ungernia sewerzowii
Ungernia spiralis
Ungernia tadshicorum
Ungernia tadshikorum
Ungernia trisphaera
Ungnadia Endl.
Ungnadia speciosa
Ungulipetalum filipendulum
Ungulipetalum Moldenke
Unifolium bifolium
Unigenes E.Wimm.
Unigenes humifusa
Uniola condensata
Uniola L.
Uniola paniculata
Uniola peruviana
Uniola pittieri
Uniola virgata
Uniyala anamallica
Uniyala anceps
Uniyala bourneana
Uniyala comorinensis
Uniyala gossypina
Uniyala multibracteata
Uniyala ramaswamii
Uniyala salviifolia
Uniyala wightiana
Unkown
Unona acuminata
Unona glauca
Unona L.f., 1782
Unona longifolia
Unona sumatrana
Unonopsis asterantha
Unonopsis aurantiaca
Unonopsis aviceps
Unonopsis axillaris
Unonopsis bahiensis
Unonopsis bauxitae
Unonopsis colombiana
Unonopsis costanensis
Unonopsis darienensis
Unonopsis elegantissima
Unonopsis esmeraldae
Unonopsis floribunda
Unonopsis glaucopetala
Unonopsis guatterioides
Unonopsis hammelii
Unonopsis heterotricha
Unonopsis longipes
Unonopsis macrocarpa
Unonopsis magnifolia
Unonopsis megalophylla
Unonopsis megalosperma
Unonopsis mexicana
Unonopsis monticola
Unonopsis onychopetaloides
Unonopsis osae
Unonopsis panamensis
Unonopsis penduliflora
Unonopsis perrottetii
Unonopsis peruviana
Unonopsis pittieri
Unonopsis R.E.Fr.
Unonopsis renati
Unonopsis renatoi
Unonopsis rufescens
Unonopsis sanctae-teresae
Unonopsis sericea
Unonopsis stevensii
Unonopsis stipitata
Unonopsis storkii
Unonopsis veneficiorum
Unxia camphorata
Unxia Kunth
Unxia suffruticosa
Upuna borneensis
Upuna Symington
Uragoga
Uragoga Baill.
Uragoga chasaliodes
Uragoga involucrans
Uragoga lateralis
Uragoga macrophylla
Uragoga pulvinigera
Uragoga silvicola
Uragoga subromota
Uragoga subsessilifolia
Uragoga tertiaria
Uragoga trichostachys
Uragoga viburnifolia
Uralepis Nutt.
Uralia E.F.Tschirkova-Zalesskaja, 1957
Urandra Thwaites
Uranthoecium Stapf
Uranthoecium truncatum
Uraria acaulis
Uraria campanulata
Uraria candida
Uraria cochinchinensis
Uraria cordifolia
Uraria crinita
Uraria Desv.
Uraria gossweileri
Uraria lacei
Uraria lagopodioides
Uraria lagopodoides
Uraria lagopus
Uraria Litchfield
Uraria oblonga
Uraria picta
Uraria pierrei
Uraria poilanei
Uraria pseudoacuminata
Uraria rotundata
Uraria rufescens
Uraria sinensis
Urariopsis brevissima
Urariopsis Schindl.
Urasphaera capitalis
Urbanella Pierre
Urbanodendron bahiense
Urbanodendron macrophyllum
Urbanodendron Mez
Urbanodendron verrucosum
Urbanolophium Melch.
Urbinella palmeri
Urceocharis clibranii
Urceocharis edentata
Urceola brachysepala
Urceola densiflora
Urceola huaitingii
Urceola javanica
Urceola laevigata
Urceola laevis
Urceola latifolia
Urceola linearicarpa
Urceola lucida
Urceola micrantha
Urceola minutiflora
Urceola napeensis
Urceola polymorpha
Urceola polyneura
Urceola quintaretii
Urceola rosea
Urceola Roxb.
Urceola torulosa
Urceola tournieri
Urceola xylinabariopsoides
Urceolaria Molina, 1810
Urceolina amazonica
Urceolina astrophiala
Urceolina ayacucensis
Urceolina bakeriana
Urceolina bonplandii
Urceolina bouchei
Urceolina candida
Urceolina castelnaeana
Urceolina caucana
Urceolina corynandra
Urceolina cyaneosperma
Urceolina formosa
Urceolina fulva
Urceolina grandiflora
Urceolina hartwegiana
Urceolina korsakoffii
Urceolina lehmannii
Urceolina microcrater
Urceolina moorei
Urceolina oxyandra
Urceolina plicata
Urceolina Rchb.
Urceolina ruthiana
Urceolina sanderi
Urceolina subedentata
Urceolina tenera
Urceolina ulei
Urceolina urceolata
Uredo abietina
Uredo abscondita
Uredo alchorneae
Uredo antarctica
Uredo anthurii
Uredo aurea
Uredo caricina
Uredo carnosa
Uredo compositarum
Uredo cypericola
Uredo dalbergiae
Uredo eupatoriicola
Uredo filicum
Uredo glechonis
Uredo guarapiensis
Uredo gynandrearum
Uredo hyptidis
Uredo ilicis
Uredo licaniae
Uredo longipedis
Uredo lynchii
Uredo machaerii
Uredo myrsines
Uredo nidularii
Uredo peribebuyensis
Uredo Persoon, 1801
Uredo phyllireae
Uredo pithecolobii
Uredo potentillae
Uredo pruni
Uredo psychotriicola
Uredo salviae
Uredo senecionis
Urelytrum agropyroides
Urelytrum annuum
Urelytrum auriculatum
Urelytrum digitatum
Urelytrum giganteum
Urelytrum Hack.
Urelytrum muricatum
Urena armitiana
Urena australiensis
Urena L.
Urena lobata
Urena procumbens
Urena repanda
Urena schultzii
Urera acuminata
Urera altissima
Urera aurantiaca
Urera baccifera
Urera bequaertii
Urera cannabina
Urera capitata
Urera caracasana
Urera chlorocarpa
Urera corallina
Urera corralensis
Urera echinata
Urera elata
Urera fenestrata
Urera filiformis
Urera Gaudich.
Urera glabriuscula
Urera guanacastensis
Urera kaalae
Urera killipiana
Urera laciniata
Urera martiniana
Urera masafuerae
Urera morifolia
Urera nitida
Urera pacifica
Urera rzedowskii
Urera simplex
Urera sinuata
Urera verrucosa
Uretia Raf.
Urginavia Speta
Urginea berylloides
Urginea flexuosa
Urginea grandiflora
Urginea nyasae
Urginea pancration
Urginea porphyrostachys
Urginea segetalis
Urginea Steinh.
Urginea unifolia
Urgineopsis Compton
Urginia Kunth, 1843
Uribea Dugand & Romero
Uribea tamarindoides
Urmenetea atacamensis
Urnatopteris R.Kidston, 1884
Urobotrya congolana
Urobotrya floresensis
Urobotrya gabonensis
Urobotrya latisquama
Urobotrya longipes
Urobotrya siamensis
Urobotrya sparsiflora
Urobotrya Stapf
Urocarpidium albiflorum
Urocarpidium Ulbr.
Urochlaena Nees
Urochloa adspersa
Urochloa advena
Urochloa albicoma
Urochloa argentea
Urochloa arida
Urochloa arizonica
Urochloa arrecta
Urochloa atrisola
Urochloa bovonei
Urochloa brachyura
Urochloa brevispicata
Urochloa brizantha
Urochloa burmanica
Urochloa caboverdiana
Urochloa chusqueoides
Urochloa ciliatissima
Urochloa clavipila
Urochloa comata
Urochloa deflexa
Urochloa dictyoneura
Urochloa distachyoides
Urochloa distachyos
Urochloa dura
Urochloa echinolaenoides
Urochloa eminii
Urochloa falcifera
Urochloa foliosa
Urochloa fusca
Urochloa fusiformis
Urochloa gilesii
Urochloa glumaris
Urochloa holosericea
Urochloa jaliscana
Urochloa jubata
Urochloa kurzii
Urochloa lachnantha
Urochloa lata
Urochloa leersioides
Urochloa lorentziana
Urochloa megastachya
Urochloa meziana
Urochloa mollis
Urochloa multiculma
Urochloa mutica
Urochloa nigropedata
Urochloa notochthona
Urochloa oblita
Urochloa occidentalis
Urochloa oligobrachiata
Urochloa oligotricha
Urochloa ophryodes
Urochloa orthostachys
Urochloa ovalis
Urochloa P.Beauv.
Urochloa panicoides
Urochloa pauciflora
Urochloa paucispicata
Urochloa piligera
Urochloa plantaginea
Urochloa platynota
Urochloa platyphylla
Urochloa polyphylla
Urochloa polystachya
Urochloa praetervisa
Urochloa pubigera
Urochloa ramosa
Urochloa reptans
Urochloa reticulata
Urochloa rudis
Urochloa rugulosa
Urochloa semiundulata
Urochloa semiverticillata
Urochloa serrata
Urochloa serrifolia
Urochloa setigera
Urochloa stigmatisata
Urochloa subquadripara
Urochloa subulifolia
Urochloa tanimbarensis
Urochloa texana
Urochloa trichopodioides
Urochloa trichopus
Urochloa turbinata
Urochloa villosa
Urochloa whiteana
Urochloa wittei
Urochloa xantholeuca
Urochondra C.E.Hubb.
Urochondra setulosa
Urococcus insignis
Urococcus Kützing, 1849
Urodon capitatus
Urodon dasyphyllus
Urodon Narkal
Urodon Turcz.
Urolepis (A.DC.) R.M.King & H.Rob.
Urolepis hecatantha
Uromyrtus allisoniana
Uromyrtus archboldiana
Uromyrtus artensis
Uromyrtus australis
Uromyrtus baumanii
Uromyrtus brassii
Uromyrtus Burret
Uromyrtus emarginatus
Uromyrtus metrosideros
Uromyrtus nekouana
Uromyrtus ngoyensis
Uromyrtus novoguineensis
Uromyrtus paulotchensis
Uromyrtus sarawakensis
Uromyrtus sunshinensis
Uromyrtus supraaxillaris
Uromyrtus tenella
Uromyrtus thymifolia
Uronema confervicola
Uronema elongatum
Uronema gigas
Uronema intermedium
Uronema Lagerheim, 1887
Uronema marinum
Uronema trentonense
Uronemataceae
Uropappus Nutt.
Uropappus pruinosus
Uropetalon minimum
Uropetalum becazzeanum
Uropetalum Burch., 1822
Urophyllum acuminatissimum
Urophyllum angustifolium
Urophyllum annamense
Urophyllum arboreum
Urophyllum argenteum
Urophyllum assahanicum
Urophyllum attenuatum
Urophyllum bidoupense
Urophyllum bismarckii-montis
Urophyllum borneense
Urophyllum bracteolatum
Urophyllum britannicum
Urophyllum bullatum
Urophyllum calycinum
Urophyllum capitatum
Urophyllum capituliflorum
Urophyllum castaneum
Urophyllum cephalotes
Urophyllum ceylanicum
Urophyllum chinense
Urophyllum chlamydanthum
Urophyllum clemensiorum
Urophyllum coffeoides
Urophyllum congestiflorum
Urophyllum corniculatum
Urophyllum corymbosum
Urophyllum crassum
Urophyllum deliense
Urophyllum ellipticum
Urophyllum elliptifolium
Urophyllum elmeri
Urophyllum endertii
Urophyllum enneandrum
Urophyllum ferrugineum
Urophyllum fuscum
Urophyllum glabrum
Urophyllum glaucescens
Urophyllum glomeratum
Urophyllum grandifolium
Urophyllum griffithianum
Urophyllum halconense
Urophyllum heteromerum
Urophyllum hexandrum
Urophyllum hirsutum
Urophyllum holectomium
Urophyllum johannis-winkleri
Urophyllum K.Koch
Urophyllum kinabaluense
Urophyllum korthalsii
Urophyllum lanaense
Urophyllum lecomtei
Urophyllum leucocarpum
Urophyllum leucophlaeum
Urophyllum leytense
Urophyllum lineatum
Urophyllum longidens
Urophyllum longifolium
Urophyllum longipes
Urophyllum longipetalum
Urophyllum macrophyllum
Urophyllum macrurum
Urophyllum magnifolium
Urophyllum maingayi
Urophyllum memecyloides
Urophyllum micranthum
Urophyllum mindorense
Urophyllum minutiflorum
Urophyllum moluccanum
Urophyllum neriifolium
Urophyllum nigricans
Urophyllum oblongum
Urophyllum oligophlebium
Urophyllum olivaceum
Urophyllum opacum
Urophyllum oresitrophum
Urophyllum pallidum
Urophyllum panayense
Urophyllum paniculatum
Urophyllum parvistipulum
Urophyllum peltistigma
Urophyllum pilosum
Urophyllum platyphyllum
Urophyllum polyneurum
Urophyllum pseudoschmidtii
Urophyllum pulchristipulum
Urophyllum rahmatii
Urophyllum reticulatum
Urophyllum rostratum
Urophyllum salicifolium
Urophyllum sandahanicum
Urophyllum schmidtii
Urophyllum sessiliflorum
Urophyllum sintangense
Urophyllum streptopodium
Urophyllum strigosum
Urophyllum subanurum
Urophyllum subglabrum
Urophyllum talangense
Urophyllum trifurcum
Urophyllum tsaianum
Urophyllum umbelliferum
Urophyllum umbellulatum
Urophyllum urdanetense
Urophyllum vulcanicum
Urophyllum Wall.
Urophyllum wichmannii
Urophyllum wollastonii
Urophyllum woodii
Urophyllum yatesii
Urophyllum zenkeri
Urophyllum zeylanicum
Urophysa henryi
Urophysa rockii
Urophysa Ulbr.
Uroskinnera almedae
Uroskinnera flavida
Uroskinnera hirtiflora
Uroskinnera Lindl.
Uroskinnera spectabilis
Urospatha angustiloba
Urospatha antisylleptica
Urospatha caribaea
Urospatha caudata
Urospatha edwallii
Urospatha grandis
Urospatha loefgreniana
Urospatha lofgreniana
Urospatha riedeliana
Urospatha sagittifolia
Urospatha Schott
Urospatha somnolenta
Urospatha wurdackii
Urospathites H.-J.Gregor & J.Bogner, 1984
Urospermum
Urospermum dalechampii
Urospermum delachampii
Urospermum picroides
Urospermum siljakiae
Urospora bangioides
Urospora grandis
Urospora penicilliformis
Urospora wormskioldii
Urostachys (E.Pritz.) Herter
Urostachys erectus
Urostachys malfuluensis
Urostachys sampaioanus
Urostigma Gasp.
Urostigma subglaucinum
Ursinia abrotanifolia
Ursinia albicaulis
Ursinia alpina
Ursinia anethoides
Ursinia anthemoides
Ursinia arida
Ursinia brachyloba
Ursinia cakilefolia
Ursinia caledonica
Ursinia calenduliflora
Ursinia chamomillaefolia
Ursinia chrysanthemoides
Ursinia coronopifolia
Ursinia dentata
Ursinia discolor
Ursinia dregeana
Ursinia eckloniana
Ursinia filicaulis
Ursinia filipes
Ursinia frutescens
Ursinia glandulosa
Ursinia heterodonta
Ursinia hispida
Ursinia kamiesbergensis
Ursinia laciniata
Ursinia macropoda
Ursinia merxmuelleri
Ursinia montana
Ursinia nana
Ursinia nudicaulis
Ursinia odorata
Ursinia oreogena
Ursinia paleacea
Ursinia paradoxa
Ursinia pedunculosa
Ursinia pilifera
Ursinia pinnata
Ursinia punctata
Ursinia pygmaea
Ursinia quinquepartita
Ursinia radicans
Ursinia rigidula
Ursinia saxatilis
Ursinia scariosa
Ursinia sericea
Ursinia serrata
Ursinia speciosa
Ursinia subflosculosa
Ursinia tenuifolia
Ursinia tenuiloba
Ursinia trifida
Ursinia tripartita
Ursiniopsis E.Phillips
Ursodendron G.P.Radczenko, 1960
Ursulaea macvaughii
Urtica amoena
Urtica ardens
Urtica aspera
Urtica atrichocaulis
Urtica atrovirens
Urtica australis
Urtica bianorii
Urtica cannabina
Urtica chamaedryoides
Urtica circularis
Urtica copeyana
Urtica cordata
Urtica crenato
Urtica dioica
Urtica dioica × kioviensis
Urtica domingensis
Urtica echinata
Urtica fernandeziana
Urtica ferox
Urtica finlaysoniana
Urtica fissa
Urtica flabellata
Urtica fragilis
Urtica freireaeformis
Urtica frutescens
Urtica galeopsifolia
Urtica globulifera
Urtica glomerulaeflora
Urtica glomeruliflora
Urtica gracilenta
Urtica gracilis
Urtica grandidentata
Urtica heterophylla
Urtica hispida
Urtica hyperborea
Urtica incisa
Urtica kioviensis
Urtica lalibertadensis
Urtica laurifolia
Urtica leptophylla
Urtica lilloi
Urtica lobata
Urtica lobulata
Urtica longispica
Urtica macbridei
Urtica macrostachya
Urtica magellanica
Urtica mairei
Urtica massaica
Urtica membranacea
Urtica membranifolia
Urtica mexicana
Urtica minutifolia
Urtica naucliflora
Urtica neubaueri
Urtica papuana
Urtica parietariifolia
Urtica parviflora
Urtica perconfusa
Urtica peruviana
Urtica pilulifera
Urtica platyphylla
Urtica portosanctana
Urtica pubescens
Urtica pulchella
Urtica rubricaulis
Urtica rupestris
Urtica saxicola
Urtica simensis
Urtica spatulata
Urtica spiralis
Urtica spirealis
Urtica stachyoides
Urtica subinermis
Urtica superba
Urtica taiwaniana
Urtica thunbergiana
Urtica tremolsii
Urtica triangularis
Urtica trichantha
Urtica urens
Urtica wallichiana
Urticaceae
Urvillea DC., 1824
Urvillea andersonii
Urvillea berteroana
Urvillea chacoensis
Urvillea cuchujaquensis
Urvillea glabra
Urvillea intermedia
Urvillea Kunth
Urvillea laevis
Urvillea oliveirae
Urvillea paucidentata
Urvillea peruviana
Urvillea procumbens
Urvillea pterocarpa
Urvillea rufescens
Urvillea stipitata
Urvillea triphylla
Urvillea ulmacea
Urvillea uniloba
Urvillea venezuelana
Urvillea venezuelensis
Ushia A.A.Kolakovsky, 1965
Uskatia Neuburg
Usteria Dennst.
Usteria guianensis
Usteria guineensis
Utania austromalayensis
Utania cuspidata
Utania G.Don
Utania maingayi
Utania montana
Utania philippinensis
Utania racemosa
Utania spicata
Utania stenophylla
Utania teysmannii
Utania volubilis
Uteria encrinella
Utleya costaricensis
Utrechtiaceae
Utricularia adpressa
Utricularia albertiana
Utricularia albiflora
Utricularia albocoerulea
Utricularia alpina
Utricularia ameliae
Utricularia amethystina
Utricularia amotape-huancabambensis
Utricularia andongensis
Utricularia antennifera
Utricularia appendiculata
Utricularia arenaria
Utricularia arnhemica
Utricularia asplundii
Utricularia aurea
Utricularia aureomaculata
Utricularia australis
Utricularia babui
Utricularia barkeri
Utricularia beaugleholei
Utricularia benjaminiana
Utricularia biceps
Utricularia bidentata
Utricularia bifida
Utricularia biflora
Utricularia biloba
Utricularia biovularioides
Utricularia bisquamata
Utricularia bosminifera
Utricularia brachiata
Utricularia bracteata
Utricularia bremii
Utricularia brennanii
Utricularia breviscapa
Utricularia buntingiana
Utricularia byrneana
Utricularia caerulea
Utricularia calycifida
Utricularia campbelliana
Utricularia capilliflora
Utricularia cecilii
Utricularia cheiranthos
Utricularia choristotheca
Utricularia christopheri
Utricularia chrysantha
Utricularia circumvoluta
Utricularia compressa
Utricularia cornigera
Utricularia cornuta
Utricularia corynephora
Utricularia costata
Utricularia cowiei
Utricularia cucullata
Utricularia cymbantha
Utricularia delicatula
Utricularia delphinioides
Utricularia delphinoides
Utricularia determannii
Utricularia dichotoma
Utricularia dimorphantha
Utricularia disjuncta
Utricularia dunstaniae
Utricularia endresii
Utricularia erectiflora
Utricularia fenshamii
Utricularia fibrosa
Utricularia firmula
Utricularia fistulosa
Utricularia flaccida
Utricularia floridana
Utricularia foliosa
Utricularia forrestii
Utricularia foveolata
Utricularia fulva
Utricularia furcellata
Utricularia fusifora
Utricularia gaagudju
Utricularia garrettii
Utricularia geminiscapa
Utricularia geoffrayi
Utricularia georgei
Utricularia gibba
Utricularia glazioviana
Utricularia globulariaefolia
Utricularia graminifolia
Utricularia grampiana
Utricularia guyanensis
Utricularia hamata
Utricularia heterochroma
Utricularia heterosepala
Utricularia hirta
Utricularia hispida
Utricularia humboldtii
Utricularia huntii
Utricularia hydrocarpa
Utricularia inaequalis
Utricularia incisa
Utricularia inflata
Utricularia inflexa
Utricularia intermedia
Utricularia inthanonensis
Utricularia involvens
Utricularia irwinica
Utricularia jamesoniana
Utricularia japonica
Utricularia jaramacaru
Utricularia jobsonii
Utricularia julianae
Utricularia juncea
Utricularia kamienskii
Utricularia kenneallyi
Utricularia kimberleyensis
Utricularia kumaonensis
Utricularia laciniata
Utricularia lasiocaulis
Utricularia lateriflora
Utricularia laxa
Utricularia lazulina
Utricularia leptoplectra
Utricularia letestui
Utricularia limmenensis
Utricularia limosa
Utricularia livida
Utricularia lloydii
Utricularia longeciliata
Utricularia longiciliata
Utricularia longifolia
Utricularia lowriei
Utricularia lunaris
Utricularia macrocheilos
Utricularia macrorhiza
Utricularia magna
Utricularia mangshanensis
Utricularia mannii
Utricularia menziesii
Utricularia meyeri
Utricularia microcalyx
Utricularia micropetala
Utricularia minor
Utricularia minutissima
Utricularia mirabilis
Utricularia Mt-Brookes
Utricularia muelleri
Utricularia multicaulis
Utricularia multifida
Utricularia multispinosa
Utricularia myriocista
Utricularia nana
Utricularia naviculata
Utricularia neglecta
Utricularia nelumbifolia
Utricularia neottioides
Utricularia nephrophylla
Utricularia nervosa
Utricularia nigrescens
Utricularia ochroleuca
Utricularia odorata
Utricularia olivacea
Utricularia oliveriana
Utricularia orbiculata
Utricularia palatina
Utricularia panamensis
Utricularia pantaneira
Utricularia papilliscapa
Utricularia parthenopipes
Utricularia paulineae
Utricularia perversa
Utricularia petersoniae
Utricularia petertaylorii
Utricularia phusoidaoensis
Utricularia physoceras
Utricularia pierrei
Utricularia pobeguinii
Utricularia poconensis
Utricularia podadena
Utricularia polygaloides
Utricularia praelonga
Utricularia praeterita
Utricularia praetermissa
Utricularia prehensilis
Utricularia pubescens
Utricularia pulchra
Utricularia punctata
Utricularia purpurea
Utricularia pusilla
Utricularia quelchii
Utricularia quinquedentata
Utricularia racemosa
Utricularia radiata
Utricularia raynalii
Utricularia recta
Utricularia reflexa
Utricularia reniformis
Utricularia resupinata
Utricularia reticulata
Utricularia rhododactylos
Utricularia rigida
Utricularia rostrata
Utricularia sandersonii
Utricularia sandwithii
Utricularia scandens
Utricularia schultesii
Utricularia simmonsii
Utricularia simplex
Utricularia simulans
Utricularia smithiana
Utricularia spinomarginata
Utricularia spiralis
Utricularia spruceana
Utricularia stanfieldii
Utricularia steenisii
Utricularia stellaris
Utricularia steyermarkii
Utricularia striata
Utricularia striatula
Utricularia subulata
Utricularia sunilii
Utricularia tenella
Utricularia tenuicaulis
Utricularia tenuissima
Utricularia terrae-reginae
Utricularia Theda
Utricularia tortilis
Utricularia Towns-River
Utricularia trichophylla
Utricularia tricolor
Utricularia tridactyla
Utricularia tridentata
Utricularia triflora
Utricularia triloba
Utricularia tubulata
Utricularia uliginosa
Utricularia uniflora
Utricularia unifolia
Utricularia violacea
Utricularia viscosa
Utricularia vitellina
Utricularia volubilis
Utricularia vulgaris
Utricularia wannanii
Utricularia warburgii
Utricularia warmingii
Utricularia welwitschii
Utricularia wightiana
Utriculariaceae
Utsetela gabonensis
Utsetela neglecta
Uva Playfair, 1914
Uva stellata
Uva-Ursi Duhamel du Monceau, 1755
Uvaesporites argentaeformis
Uvaria acuminata
Uvaria alba
Uvaria albertisii
Uvaria ambongensis
Uvaria ambongoensis
Uvaria amplexicaulis
Uvaria angolensis
Uvaria anonoides
Uvaria antsiranensis
Uvaria argentea
Uvaria bathiei
Uvaria baumannii
Uvaria beccarii
Uvaria bipindensis
Uvaria borneensis
Uvaria brevistipitata
Uvaria buchholzii
Uvaria cabindensis
Uvaria cabrae
Uvaria calamistrata
Uvaria callicarpa
Uvaria capuronii
Uvaria cardiophylla
Uvaria caroli-afzelii
Uvaria celebica
Uvaria chamae
Uvaria chariensis
Uvaria cherrevensis
Uvaria cinerascens
Uvaria clavata
Uvaria clementis
Uvaria combretifolia
Uvaria comperei
Uvaria concava
Uvaria cornuana
Uvaria cuanzensis
Uvaria cuneifolia
Uvaria curtisii
Uvaria dac
Uvaria dacremontii
Uvaria dasoclema
Uvaria decidua
Uvaria denhardtiana
Uvaria dinklagei
Uvaria discolor
Uvaria doeringii
Uvaria dulcis
Uvaria edulis
Uvaria excelsa
Uvaria farquharii
Uvaria faulknerae
Uvaria ferruginea
Uvaria flexuosa
Uvaria foetida
Uvaria furfuracea
Uvaria gabonensis
Uvaria glabra
Uvaria glabrata
Uvaria gracilipes
Uvaria grandiflora
Uvaria griffithii
Uvaria hahnii
Uvaria hamiltonii
Uvaria hasselti
Uvaria heterotricha
Uvaria hirsuta
Uvaria hispidocostata
Uvaria holtzei
Uvaria hookeri
Uvaria japonica
Uvaria javana
Uvaria javanica
Uvaria johannis
Uvaria kirkii
Uvaria klaineana
Uvaria klainei
Uvaria kurzii
Uvaria kweichowensis
Uvaria L.
Uvaria lancifolia
Uvaria lanuginosa
Uvaria larep
Uvaria lastoursvillensis
Uvaria laurentii
Uvaria lauterbachiana
Uvaria leichhardtii
Uvaria leptocladon
Uvaria leptopoda
Uvaria littoralis
Uvaria lobbiana
Uvaria longipes
Uvaria lucida
Uvaria lutea
Uvaria macclurei
Uvaria macropoda
Uvaria marenteria
Uvaria micrantha
Uvaria microcarpa
Uvaria mollis
Uvaria monticola
Uvaria muricata
Uvaria musaria
Uvaria narum
Uvaria ngounyensis
Uvaria nitida
Uvaria obanensis
Uvaria oligocarpa
Uvaria osmantha
Uvaria ovata
Uvaria panayensis
Uvaria pandensis
Uvaria papuasica
Uvaria pauciovulata
Uvaria pierrei
Uvaria piperita
Uvaria poggei
Uvaria puguensis
Uvaria pulchra
Uvaria relambo
Uvaria rivularis
Uvaria rosenbergiana
Uvaria rufa
Uvaria rupestris
Uvaria saboureaui
Uvaria sambiranensis
Uvaria sankowskyi
Uvaria scabrida
Uvaria scabridula
Uvaria schefferi
Uvaria scheffleri
Uvaria schelei
Uvaria schizocalyx
Uvaria schweinfurthii
Uvaria scortechinii
Uvaria semecarpifolia
Uvaria siamensis
Uvaria smithii
Uvaria sofa
Uvaria solanifolia
Uvaria stellata
Uvaria synsepala
Uvaria tanzaniae
Uvaria thomasii
Uvaria tomentosa
Uvaria tonkinensis
Uvaria topazensis
Uvaria tortilis
Uvaria uhrii
Uvaria unguiculata
Uvaria utteridgei
Uvaria verrucosa
Uvaria versicolor
Uvaria vietnamensis
Uvaria welwitschii
Uvaria wrayi
Uvaria yunnanensis
Uvaria zeylanica
Uvaria zippeliana
Uvaria zschokkei
Uvariastrum dependens
Uvariastrum Engl.
Uvariastrum germainii
Uvariastrum hexaloboides
Uvariastrum modestum
Uvariastrum neglectum
Uvariastrum pierreanum
Uvariastrum pynaertii
Uvariastrum zenkeri
Uvariodendron (Engl. & Diels) R.E.Fr.
Uvariodendron angustifolium
Uvariodendron anisatum
Uvariodendron calophyllum
Uvariodendron connivens
Uvariodendron fuscum
Uvariodendron giganteum
Uvariodendron gorgonis
Uvariodendron kirkii
Uvariodendron magnificum
Uvariodendron mbagoi
Uvariodendron mirabile
Uvariodendron molundense
Uvariodendron occidentale
Uvariodendron occidentalis
Uvariodendron oligocarpum
Uvariodendron pycnophyllum
Uvariodendron schmidtii
Uvariodendron usambarense
Uvariopsis bakeriana
Uvariopsis bisexualis
Uvariopsis citrata
Uvariopsis congolana
Uvariopsis dioica
Uvariopsis Engl.
Uvariopsis globiflora
Uvariopsis guineensis
Uvariopsis korupensis
Uvariopsis le-testui
Uvariopsis lovettiana
Uvariopsis noldeae
Uvariopsis sessiliflora
Uvariopsis solheidii
Uvariopsis submontana
Uvariopsis tripetala
Uvariopsis vanderystii
Uvariopsis zenkeri
Uvedalia clementii
Uvedalia linearis
Uvedalia R.Br.
Uvifera L. ex Kuntze
Uvularia floridana
Uvularia grandiflora
Uvularia grandifolia
Uvularia L.
Uvularia oppositifolia
Uvularia perfoliata
Uvularia puberula
Uvularia sessilifolia
Uvulifera Molinari-Novoa, 2016""".strip().split("\n")

# ══════════════════════════════════════════════
#  LISTE DES PLANTES TOXIQUES
#  ⚠ À REMPLACER à chaque nouvelle lettre
#  → Mettre ici uniquement les noms présents
#    dans PLANTES qui sont toxiques.
#    Le nom doit être identique (même casse).
#  → Si aucune plante toxique : laisser []
# ══════════════════════════════════════════════

PLANTES_TOXIQUES = """Ulex argenteus
Ulex australis
Ulex baeticus
Ulex borgiae
Ulex breoganii
Ulex canescens
Ulex cantabricus
Ulex dalilae
Ulex densus
Ulex eriocladus
Ulex europaeus
Ulex europaeus x Ulex gallii
Ulex gallii
Ulex genistoides
Ulex jussiaei
Ulex L.
Ulex lagrezii
Ulex lucidus
Ulex lusitanicus
Ulex micranthus
Ulex minor
Ulex parviflorus
Ulex provincialis
Ulex revurvatus
Ulex richteri
Ulex spicatus
Ulex welwitschianus
Urtica amoena
Urtica ardens
Urtica aspera
Urtica atrichocaulis
Urtica atrovirens
Urtica australis
Urtica bianorii
Urtica cannabina
Urtica chamaedryoides
Urtica circularis
Urtica copeyana
Urtica cordata
Urtica crenato
Urtica dioica
Urtica dioica × kioviensis
Urtica domingensis
Urtica echinata
Urtica fernandeziana
Urtica ferox
Urtica finlaysoniana
Urtica fissa
Urtica flabellata
Urtica fragilis
Urtica freireaeformis
Urtica frutescens
Urtica galeopsifolia
Urtica globulifera
Urtica glomerulaeflora
Urtica glomeruliflora
Urtica gracilenta
Urtica gracilis
Urtica grandidentata
Urtica heterophylla
Urtica hispida
Urtica hyperborea
Urtica incisa
Urtica kioviensis
Urtica lalibertadensis
Urtica laurifolia
Urtica leptophylla
Urtica lilloi
Urtica lobata
Urtica lobulata
Urtica longispica
Urtica macbridei
Urtica macrostachya
Urtica magellanica
Urtica mairei
Urtica massaica
Urtica membranacea
Urtica membranifolia
Urtica mexicana
Urtica minutifolia
Urtica naucliflora
Urtica neubaueri
Urtica papuana
Urtica parietariifolia
Urtica parviflora
Urtica perconfusa
Urtica peruviana
Urtica pilulifera
Urtica platyphylla
Urtica portosanctana
Urtica pubescens
Urtica pulchella
Urtica rubricaulis
Urtica rupestris
Urtica saxicola
Urtica simensis
Urtica spatulata
Urtica spiralis
Urtica spirealis
Urtica stachyoides
Urtica subinermis
Urtica superba
Urtica taiwaniana
Urtica thunbergiana
Urtica tremolsii
Urtica triangularis
Urtica trichantha
Urtica urens
Urtica wallichiana""".strip().split("\n")

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
    # On garde plant.css pour la structure, on surcharge juste
    # les variables CSS avec les couleurs rouges de toxique.css
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
    .plant-sidebar { border-color: var(--border); background: var(--card); }
    .sidebar-title { color: var(--accent); border-color: var(--border); }
    .toc-link:hover, .toc-link--active { color: var(--accent); }
    .precaution-card--danger { border-left: 4px solid #c0392b; background: #1a0d0d; }
    .precaution-card--info { border-color: var(--border); background: var(--card); }
    .plant-divider { color: var(--accent-dark); opacity: 0.5; }
    footer { border-color: var(--border); background: var(--bg); color: var(--text-muted); }
    .breadcrumb-bar { background: rgba(15,8,8,0.95); border-color: var(--border); }
    .breadcrumb-inner a { color: var(--accent); }
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
      <a href="../../encyclopedie/U.html">Espèces en « U »</a>
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
    <a href="../../encyclopedie/U.html" style="color:var(--accent)">← Retour aux espèces en U</a>
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
