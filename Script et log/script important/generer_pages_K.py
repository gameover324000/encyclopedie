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

DOSSIER_SORTIE  = "./K_Plante_page"              # ← Dossier de sortie         ex: "./V_Plante_page"
LETTRE          = "K"                            # ← Lettre courante            ex: "V"
LETTRE_HTML     = "K.html"                       # ← Fichier index de la lettre ex: "V.html"
LOG_FILE        = "generation_log_pages_K.json"  # ← Fichier log                ex: "generation_log_pages_V.json"
HEADERS         = {"User-Agent": "Herbarium-Bot/1.0"}

# ══════════════════════════════════════════════
#  LISTE DES PLANTES
#  ⚠ À REMPLACER à chaque nouvelle lettre
#  → Coller ici toutes les plantes de la lettre,
#    une par ligne, sans numérotation.
# ══════════════════════════════════════════════

PLANTES = """Kabulia Bor & C.E.C.Fisch.
Kabuyea hostifolia
Kachaikenia compuesta
Kachchhia M.N.Bose & J.Banerji, 1984
Kadenia dubia
Kadenia Lavrova & V.N.Tikhom.
Kadenia salina
Kadenicarpus horripilus
Kadenicarpus pseudomacrochele
Kadsura angustifolia
Kadsura borneensis
Kadsura celebica
Kadsura chinensis
Kadsura coccinea
Kadsura heteroclita
Kadsura induta
Kadsura japonica
Kadsura Kaempf. ex Juss.
Kadsura lanceolata
Kadsura lancilimba
Kadsura longepedunculata
Kadsura longipedunculata
Kadsura marmorata
Kadsura matsudae
Kadsura philippinensis
Kadsura renchangiana
Kadsura scandens
Kadsura verrucosa
Kadua
Kadua acuminata
Kadua affinis
Kadua axillaris
Kadua centranthoides
Kadua cordata
Kadua coriacea
Kadua degeneri
Kadua elatior
Kadua fluviatilis
Kadua flynnii
Kadua foggiana
Kadua foliosa
Kadua formosa
Kadua grantii
Kadua knudsenii
Kadua laxiflora
Kadua lichtlei
Kadua littoralis
Kadua lucei
Kadua munroi
Kadua nukuhivensis
Kadua parvula
Kadua raiateensis
Kadua rapensis
Kadua romanzoffiensis
Kadua tahuatensis
Kadua tryblium
Kaeleria Boiss., 1859
Kaempfera Houst.
Kaempferia aethiopica
Kaempferia albomaculata
Kaempferia alboviolacea
Kaempferia attapeuensis
Kaempferia champasakensis
Kaempferia cuneata
Kaempferia elegans
Kaempferia fallax
Kaempferia galanga
Kaempferia gigantiphylla
Kaempferia gilbertii
Kaempferia glauca
Kaempferia grandifolia
Kaempferia harmandiana
Kaempferia jenjittikuliae
Kaempferia koratensis
Kaempferia L.
Kaempferia laotica
Kaempferia marginata
Kaempferia minuta
Kaempferia nemoralis
Kaempferia nigerica
Kaempferia ovalifolia
Kaempferia pardi
Kaempferia parviflora
Kaempferia pascuorum
Kaempferia pulchra
Kaempferia roscoeana
Kaempferia rosea
Kaempferia rotunda
Kaempferia sawanensis
Kaempferia siamensis
Kaempferia simaoensis
Kaempferia spoliata
Kaempferia udonensis
Kaempferia undulata
Kaempferia xiengkhouangensis
Kafirnigania hissarica
Kageneckia angustifolia
Kageneckia lanceolata
Kageneckia oblonga
Kageneckia Ruiz & Pav.
Kaidacarpum W.Carruthers, 1868
Kailarsenia campanula
Kailarsenia hygrophila
Kailarsenia lineata
Kailarsenia stenosepala
Kailarsenia tentaculata
Kailarsenia Tirveng.
Kailashia bouffordii
Kailashia robusta
Kailashia xizangensis
Kairoa endressiana
Kairoa Philipson
Kairoa suberosa
Kairoa villosa
Kairothamnus phyllanthoides
Kaisupeea B.L.Burtt
Kaisupeea cyanea
Kaisupeea orthocarpa
Kajewskiella polyantha
Kajewskiella trichantha
Kakabekia Barghoorn, 1965
Kakahuia campbellii
Kalaharia Baill.
Kalaharia schaijesii
Kalaharia uncinata
Kalakia Alava
Kalakia marginata
Kalanchoe adelae
Kalanchoe alternans
Kalanchoe alticola
Kalanchoe angolensis
Kalanchoe antennifera
Kalanchoe apiifolia
Kalanchoe arborescens
Kalanchoe aromatica
Kalanchoe aubrevillei
Kalanchoe auriculata
Kalanchoe ballyi
Kalanchoe beauverdii
Kalanchoe beharensis
Kalanchoe benbothae
Kalanchoe bentii
Kalanchoe berevoensis
Kalanchoe bergeri
Kalanchoe bhidei
Kalanchoe bipartita
Kalanchoe blossfeldiana
Kalanchoe boisii
Kalanchoe boranae
Kalanchoe bouvetii
Kalanchoe brachyloba
Kalanchoe bracteata
Kalanchoe brevicalyx
Kalanchoe brevisepala
Kalanchoe briquetii
Kalanchoe calycinum
Kalanchoe campanulata
Kalanchoe cassiopeja
Kalanchoe ceratophylla
Kalanchoe chapototii
Kalanchoe chevalieri
Kalanchoe citrina
Kalanchoe crenata
Kalanchoe crouchii
Kalanchoe darainensis
Kalanchoe deficiens
Kalanchoe delagoensis
Kalanchoe densiflora
Kalanchoe dinklagei
Kalanchoe dyeri
Kalanchoe edwardii
Kalanchoe elizae
Kalanchoe ena
Kalanchoe eriophylla
Kalanchoe estrelae
Kalanchoe fadeniorum
Kalanchoe farinacea
Kalanchoe faustii
Kalanchoe fedtschenkoi
Kalanchoe fernandesii
Kalanchoe figureidoi
Kalanchoe floribunda
Kalanchoe gastonis-bonnieri
Kalanchoe germanae
Kalanchoe geroldii
Kalanchoe glaucescens
Kalanchoe globulifera
Kalanchoe gracilipes
Kalanchoe grandidieri
Kalanchoe hametiorum
Kalanchoe hildebrandtii
Kalanchoe houghtonii
Kalanchoe humifica
Kalanchoe humilis
Kalanchoe hummeliae
Kalanchoe hypseloleuce
Kalanchoe integra
Kalanchoe integrifolia
Kalanchoe jongmansii
Kalanchoe kewensis
Kalanchoe klopperae
Kalanchoe krigeae
Kalanchoe laciniata
Kalanchoe lanceolata
Kalanchoe lateritia
Kalanchoe latisepala
Kalanchoe laxiflora
Kalanchoe leblanciae
Kalanchoe lindmanii
Kalanchoe linearifolia
Kalanchoe lobata
Kalanchoe longiflora
Kalanchoe longifolia
Kalanchoe lubangensis
Kalanchoe luciae
Kalanchoe macrochlamys
Kalanchoe mandrarensis
Kalanchoe manginii
Kalanchoe marmorata
Kalanchoe marnieriana
Kalanchoe maromokotrensis
Kalanchoe migiurtinorum
Kalanchoe millotii
Kalanchoe miniata
Kalanchoe mitejea
Kalanchoe mortagei
Kalanchoe neglecta
Kalanchoe nyikae
Kalanchoe oberlanderi
Kalanchoe obtusa
Kalanchoe olivacea
Kalanchoe orgyalis
Kalanchoe paniculata
Kalanchoe pareikiana
Kalanchoe peltata
Kalanchoe peltigera
Kalanchoe petitiana
Kalanchoe pinnata
Kalanchoe poincarei
Kalanchoe porphyrocalyx
Kalanchoe prittwitzii
Kalanchoe prolifera
Kalanchoe pruinosa
Kalanchoe pseudocampanulata
Kalanchoe pubescens
Kalanchoe pumila
Kalanchoe quadrangularis
Kalanchoe quartiniana
Kalanchoe rebmannii
Kalanchoe rechingeri
Kalanchoe rhombopilosa
Kalanchoe richaudii
Kalanchoe robusta
Kalanchoe rolandi-bonapartei
Kalanchoe rosei
Kalanchoe rotundifolia
Kalanchoe rubella
Kalanchoe salazarii
Kalanchoe sampsonii
Kalanchoe sanctula
Kalanchoe scapigera
Kalanchoe schimperiana
Kalanchoe schizophylla
Kalanchoe sexangularis
Kalanchoe smithii
Kalanchoe sogae
Kalanchoe somaliensis
Kalanchoe spathulata
Kalanchoe steami
Kalanchoe streptantha
Kalanchoe suarezensis
Kalanchoe subrosulata
Kalanchoe synsepala
Kalanchoe tashiroi
Kalanchoe teixeirae
Kalanchoe tenuiflora
Kalanchoe tetramera
Kalanchoe tetraphylla
Kalanchoe tomentosa
Kalanchoe torrejacqii
Kalanchoe trageri
Kalanchoe uniflora
Kalanchoe usambarensis
Kalanchoe vadensis
Kalanchoe variifolia
Kalanchoe velutina
Kalanchoe verdoorniae
Kalanchoe viguieri
Kalanchoe waldheimii
Kalanchoe waterbergensis
Kalanchoe welwitschii
Kalanchoe wildii
Kalanchoe winteri
Kalanchoe yemensis
Kalappia celebica
Kalbfussia Sch.Bip.
Kalbreyera Burret
Kalbreyeracanthus Wassh.
Kalbreyeriella cabrerae
Kalbreyeriella Lindau
Kalenjinia gelatinosa
Kalenjinia L.Krienitz, C.Bock, K.Kotut & T.Pröschold, 2012
Kali Mill.
Kalidiopsis Aellen
Kalidium caspicum
Kalidium cuspidatum
Kalidium foliatum
Kalidium gracile
Kalidium juniperinum
Kalidium Moq.
Kalidium schrenkianum
Kalidium wagenitzii
Kalimeris (Cass.) Cass.
Kalimeris hispida
Kalimeris incisa
Kalimeris indica
Kalimeris integrifolia
Kalimeris pinnatifida
Kalimeris shimadai
Kalimeris yomena
Kalinia H.L.Bell & Columbus
Kalinia obtusiflora
Kaliphora Hook.f.
Kaliphora madagascariensis
Kaliphoraceae
Kallstroemia adscendens
Kallstroemia boliviana
Kallstroemia californica
Kallstroemia curta
Kallstroemia grandiflora
Kallstroemia hageri
Kallstroemia hintonii
Kallstroemia hirsutissima
Kallstroemia incana
Kallstroemia maxima
Kallstroemia mexicana
Kallstroemia parviflora
Kallstroemia peninsularis
Kallstroemia pennellii
Kallstroemia perennans
Kallstroemia pubescens
Kallstroemia rosei
Kallstroemia Scop.
Kallstroemia tucumanensis
Kallymenia brachycystidea
Kallymenia cribrosa
Kallymenia feldmannii
Kallymenia J.Agardh, 1842
Kallymenia lacinifolia
Kallymenia limminghei
Kallymenia morelii
Kallymenia multiloba
Kallymenia norrisii
Kallymenia oblongifructa
Kallymenia ornata
Kallymenia pacifica
Kallymenia patens
Kallymenia perforata
Kallymenia reniformis
Kallymenia rosea
Kallymenia rubra
Kallymenia setchellii
Kallymenia spinosa
Kallymenia tasmanica
Kallymenia tenuifolia
Kallymenia thompsonii
Kallymenia westii
Kallymeniaceae
Kallymenicola invisibilis
Kallymenicola penetrans
Kallymenicola superficialis
Kalmia angustifolia
Kalmia buxifolia
Kalmia cuneata
Kalmia elliptica
Kalmia ericoides
Kalmia hirsuta
Kalmia latifolia
Kalmia microphylla
Kalmia polifolia
Kalmia procumbens
Kalmiophyllum marcodurense
Kalmiopsis fragrans
Kalmiopsis leachiana
Kalopanax Miq.
Kalopanax septemlobus
Kaloxylon hookeri
Kaloxylon Williamson, 1875
Kalymma grandis
Kalymma Unger, 1856
Kalymmanthus D.L.Dilcher & P.R.Crane, 1985
Kamaraspermum E.M.Kern & H.N.Andrews, 1946
Kamaraspermum leeanum
Kamettia caryophyllata
Kamettia Kostel.
Kampochloa brachyphylla
Kanahia carlsbergiana
Kanahia laniflora
Kanahia R.Br.
Kanakomyrtus dawsoniana
Kanakomyrtus longipetiolata
Kanakomyrtus mcphersonii
Kanakomyrtus myrtopsidoides
Kanakomyrtus N.Snow
Kanakomyrtus prominens
Kanaloa kahoolawensis
Kanaloa Lorence & K.R.Wood
Kanapia Arriola & Alejandro
Kanapia wenzelii
Kanburia chlorantha
Kanburia tenasserimensis
Kandaea elodes
Kandaharia rechingerorum
Kandelia candel
Kandelia obovata
Kania eugenioides
Kania hirsutula
Kania microphylla
Kania platyphylla
Kania Schltr.
Kania urdanetensis
Kanimia Gardner
Kanimia strobilifera
Kankakeea grundyi
Kankakeea thallyformis
Kantia J.von Pia, 1912
Kantius trichomanis
Kantou Aubrév. & Pellegr.
Kaokochloa De Winter
Kaokochloa nigrirostris
Kaokoxylon R.Kräusel, 1956
Kaolakia borealis
Kappaphycopsis Dumilag & Zuccarello, 2022
Kappaphycus alvarezii
Kappaphycus Doty, 1988
Kappaphycus inermis
Kappaphycus malesianus
Kappaphycus striatus
Kapraunia A.M.Savoie & G.W.Saunders, 2018
Karatavia kultiassovii
Karawata depressa
Karawata gustavoi
Karawata hostilis
Karawata multiflora
Karawata nigribracteata
Karawata prasinata
Karawata saxicola
Kardiasperma S.R.Manchester, 1994
Kardomia granitica
Kardomia jucunda
Kardomia odontocalyx
Kardomia prominens
Kardomia silvestris
Kardomia squarrulosa
Karelinia caspia
Karelinia Less.
Karima Cheek & Riina
Karima scarciesii
Karimbolea Desc.
Karina taylorianum
Karinopteris M.Boersma, 1972
Karkenia cylindrica
Karkenia hauptmannii
Karkenia S.Archangelsky, 1965
Karnataka benthamii
Karomia Dop
Karomia fragrans
Karomia gigas
Karomia humbertii
Karomia macrocalyx
Karomia madagascariensis
Karomia microphylla
Karomia mira
Karomia speciosa
Karomia tettensis
Karpathia V.P.Maslov, 1962
Karpatiosorbus adamii
Karpatiosorbus adeana
Karpatiosorbus admonitor
Karpatiosorbus albensis
Karpatiosorbus alnifrons
Karpatiosorbus amici-petri
Karpatiosorbus andreanszkyana
Karpatiosorbus badensis
Karpatiosorbus bakonyensis
Karpatiosorbus balatonica
Karpatiosorbus barrandienica
Karpatiosorbus barthae
Karpatiosorbus bodajkensis
Karpatiosorbus bohemica
Karpatiosorbus borosiana
Karpatiosorbus bristoliensis
Karpatiosorbus carolipolitana
Karpatiosorbus concavifolia
Karpatiosorbus cordigastensis
Karpatiosorbus croceocarpa
Karpatiosorbus degenii
Karpatiosorbus devoniensis
Karpatiosorbus eugenii-kelleri
Karpatiosorbus eximia
Karpatiosorbus eystettensis
Karpatiosorbus fischeri
Karpatiosorbus franconica
Karpatiosorbus gayeriana
Karpatiosorbus gemella
Karpatiosorbus gerecseensis
Karpatiosorbus griseotormaria
Karpatiosorbus haesitans
Karpatiosorbus herbipolitana
Karpatiosorbus hoppeana
Karpatiosorbus houstoniae
Karpatiosorbus hybrida
Karpatiosorbus istriaca
Karpatiosorbus karpatii
Karpatiosorbus latifolia
Karpatiosorbus latisedes
Karpatiosorbus meierottii
Karpatiosorbus mergenthaleriana
Karpatiosorbus meyeri
Karpatiosorbus milensis
Karpatiosorbus moenofranconica
Karpatiosorbus omissa
Karpatiosorbus paxiana
Karpatiosorbus pelsoensis
Karpatiosorbus perlonga
Karpatiosorbus portae-bohemicae
Karpatiosorbus pseudobakonyensis
Karpatiosorbus pseudosemiincisa
Karpatiosorbus pseudovertesensis
Karpatiosorbus puellarum
Karpatiosorbus ratisbonensis
Karpatiosorbus redliana
Karpatiosorbus remensis
Karpatiosorbus rhodanthera
Karpatiosorbus rhombiformis
Karpatiosorbus schuwerkiorum
Karpatiosorbus sellii
Karpatiosorbus semiincisa
Karpatiosorbus Sennikov & Kurtto
Karpatiosorbus seyboldiana
Karpatiosorbus simonkaiana
Karpatiosorbus slavnicensis
Karpatiosorbus slovenica
Karpatiosorbus subcuneata
Karpatiosorbus tauricola
Karpatiosorbus tobani
Karpatiosorbus udvardyana
Karpatiosorbus vertesensis
Karrabina benthamiana
Karrabina biagiana
Karrabina Rozefelds & H.C.Hopkins
Karstenia Goeppert, 1836
Karstia raspacula
Kartalinia acaulis
Karvandarina cartilaginea
Karvandarina Rech.f.
Karwinskia bicolor
Karwinskia calderonii
Karwinskia californica
Karwinskia caloneura
Karwinskia colombiana
Karwinskia humboldtiana
Karwinskia johnstonii
Karwinskia oblongifolia
Karwinskia orbiculata
Karwinskia parvifolia
Karwinskia pluvialis
Karwinskia potrerilloana
Karwinskia rocana
Karwinskia rzedowskii
Karwinskia subcordata
Karwinskia tehuacana
Karwinskia umbellata
Karwinskia venturae
Karwinskia Zucc.
Kaschgaria brachanthemoides
Kaschgaria komarovii
Kaschgaria Poljakov
Kashmiria himalaica
Katapsuxis silaifolia
Katharinea A.D.Hawkes
Katinasia cabrerae
Kaufmannia semenovii
Kaunia camataguiensis
Kaunia endyta
Kaunia eucosmoides
Kaunia hosanensis
Kaunia lasiophthalma
Kaunia longipetiolata
Kaunia pachanoi
Kaunia R.M.King & H.Rob.
Kaunia rufescens
Kaunia saltensis
Kaviria aucheri
Kaviria azaurena
Kaviria cana
Kaviria gossypina
Kaviria lachnantha
Kaviria pycnophylla
Kaviria rubescens
Kaviria tomentosa
Kaviria vvedenskyi
Kayea assamica
Kayea beccariana
Kayea borneensis
Kayea calophylloides
Kayea catharinae
Kayea coriacea
Kayea daphnifolia
Kayea elegans
Kayea elmeri
Kayea eugeniifolia
Kayea floribunda
Kayea grandis
Kayea hexapetala
Kayea korthalsiana
Kayea kunstleri
Kayea lanceolata
Kayea larnachiana
Kayea lepidota
Kayea macrantha
Kayea macrophylla
Kayea manii
Kayea megalocarpa
Kayea meridionalis
Kayea myrtifolia
Kayea navesii
Kayea nervosa
Kayea oblongifolia
Kayea pacifica
Kayea paniculata
Kayea parviflora
Kayea philippinensis
Kayea racemosa
Kayea rosea
Kayea scalarinervosa
Kayea stylosa
Kayea Wall.
Kayea wrayi
Kearnemalvastrum D.M.Bates
Kearnemalvastrum lacteum
Kearnemalvastrum subtriflorum
Keayodendron bridelioides
Keayodendron Leandri
Kebirita Kramina & D.D.Sokoloff
Kebirita roudairei
Keckiella antirrhinoides
Keckiella breviflora
Keckiella cordifolia
Keckiella corymbosa
Keckiella lemmonii
Keckiella rothrockii
Keckiella Straw
Keckiella ternata
Kedarnatha garhwalica
Kedarnatha hameliana
Kedarnatha meifolia
Kedarnatha oreomyrrhiformis
Kedhalia flaviflora
Kedrostis abdallae
Kedrostis africana
Kedrostis capensis
Kedrostis cogniauxii
Kedrostis courtallensis
Kedrostis crassirostrata
Kedrostis elongata
Kedrostis foetidissima
Kedrostis gijef
Kedrostis heterophylla
Kedrostis hirta
Kedrostis hirtella
Kedrostis laxa
Kedrostis leloja
Kedrostis limpompensis
Kedrostis Medik.
Kedrostis monosperma
Kedrostis nana
Kedrostis perrieri
Kedrostis pseudogijef
Keenania Hook.f.
Keerlia DC.
Keetia abouabou
Keetia acuminata
Keetia angustifolia
Keetia bakossiorum
Keetia bridsoniae
Keetia carmichaelii
Keetia cornelia
Keetia davidii
Keetia E.Phillips
Keetia ferruginea
Keetia futa
Keetia gracilis
Keetia gueinzii
Keetia hispida
Keetia inaequilatera
Keetia koritschoneri
Keetia leucantha
Keetia lukei
Keetia lulandensis
Keetia mannii
Keetia molundensis
Keetia multiflora
Keetia mwasumbii
Keetia namoyae
Keetia obovata
Keetia ornata
Keetia procteri
Keetia purpurascens
Keetia ripae
Keetia rubens
Keetia rufivillosa
Keetia rwandensis
Keetia semsei
Keetia susu
Keetia tenuiflora
Keetia venosa
Keetia zanzibarica
Kefersteinia alata
Kefersteinia alba
Kefersteinia angustifolia
Kefersteinia aurorae
Kefersteinia bengasahra
Kefersteinia bismarckii
Kefersteinia elegans
Kefersteinia escobariana
Kefersteinia excentrica
Kefersteinia expansa
Kefersteinia gemma
Kefersteinia guacamayoana
Kefersteinia heideri
Kefersteinia hirtzii
Kefersteinia koechliniorum
Kefersteinia lactea
Kefersteinia lafontainei
Kefersteinia lojae
Kefersteinia maculosa
Kefersteinia microcharis
Kefersteinia niesseniae
Kefersteinia ocellata
Kefersteinia orbicularis
Kefersteinia oscarii
Kefersteinia parvilabris
Kefersteinia pastorellii
Kefersteinia pellita
Kefersteinia pulchella
Kefersteinia pusilla
Kefersteinia Rchb.f.
Kefersteinia retanae
Kefersteinia richardhegerlii
Kefersteinia ricii
Kefersteinia salustianae
Kefersteinia sanguinolenta
Kefersteinia stapelioides
Kefersteinia stevensonii
Kefersteinia taurina
Kefersteinia tolimensis
Kefersteinia trullata
Kefersteinia villenae
Kefersteinia villosa
Kefersteinia wercklei
Kegelia Rchb.f.
Kegeliella atropilosa
Kegeliella houtteana
Kegeliella kupperi
Kegeliella orientalis
Keiskea Miq.
Kelissa Ravenna
Kelita A.R.Bean
Kelleria bogongensis
Kelleria childii
Kelleria croizatii
Kelleria dieffenbachii
Kelleria Endl.
Kelleria laxa
Kelleria lyallii
Kelleria multiflora
Kelleria paludosa
Kelleria patula
Kelleria tessellata
Kelleria villosa
Kelleronia gillettiae
Kelleronia gillettii
Kelleronia revoilii
Kelleronia Schinz
Kelleronia splendens
Kellochloa brachyantha
Kellochloa verrucosa
Kelloggia chinensis
Kelloggia galioides
Kelloggia Torr. ex Benth. & Hook.f.
Kelseya (S.Watson) Rydb.
Kelseya uniflora
Kemulariella abchasica
Kemulariella caucasica
Kemulariella colchica
Kemulariella rosea
Kemulariella Tamamsch.
Kemulariella tuganiana
Kendrickia Hook.f.
Kendrickia walkeri
Kenella V.A.Samylina, 1968
Kengia Packer
Kengiochloa pubiflora
Kengyilia alatavica
Kengyilia batalinii
Kengyilia C.Yen & J.L.Yang
Kengyilia geminata
Kengyilia gobicola
Kengyilia grandiglumis
Kengyilia habahenensis
Kengyilia hirsuta
Kengyilia kaschgarica
Kengyilia kokonorica
Kengyilia kryloviana
Kengyilia laxiflora
Kengyilia melanthera
Kengyilia mutica
Kengyilia pamirica
Kengyilia pulcherrima
Kengyilia rigidula
Kengyilia stenachyra
Kengyilia tahelacana
Kengyilia thoroldiana
Keniochloa Melderis
Kennedia baumannii
Kennedia beckxiana
Kennedia Blackdown-Tableland
Kennedia coccinea
Kennedia eximia
Kennedia glabrata
Kennedia lateritia
Kennedia marryattae
Kennedia microphylla
Kennedia nigricans
Kennedia parviflora
Kennedia procurrens
Kennedia prorepens
Kennedia prostrata
Kennedia retrorsa
Kennedia rubicunda
Kennedia southcoast
Kennedia stirlingii
Kennedia tomentosa
Kennedia Vent.
Kennedya DC., 1825
Kentiopsis Brongn.
Kentranthus battandieri
Kentranthus Neck.
Kentrochrosia K.Schum. & Lauterb.
Kentrophyllum creticum
Kentrophyllum foliosum
Kentrophyllum Neck. ex DC.
Kentrophyllum trachycarpum
Kentrosphaera A.Borzì, 1883
Kentrosphaera gloeophila
Kentrothamnus weddellianus
Kenyacanthus ndorensis
Keraiaphyllum K.Frentzen, 1932
Keraiaphyllum suevicum
Keranthus Lour. ex Endl.
Keraocarpon T.Ohana, T.Kimura & S.Chitaley, 1999
Keratochlaena rigidifolia
Keratococcus bicaudatus
Keratococcus dispar
Keratococcus glareosus
Keratococcus rhaphidioides
Keratococcus suecicus
Keratosperma allenbyense
Keraunea capixaba
Keraunea confusa
Keraymonia cortiformis
Keraymonia nipaulensis
Kerbera eichleri
Keria Spreng.
Kerianthera J.H.Kirkbr.
Kerianthera longiflora
Kerianthera preclara
Kericodon crispus
Kermadecia bleasdalei
Kermadecia brinoniae
Kermadecia Brongn. & Gris
Kermadecia elliptica
Kermadecia pronyensis
Kermadecia rotundifolia
Kermadecia sinuata
Kermatia T.Kalina & M.Puncochárová, 1987
Kernera Medik.
Kernera saxatilis
Kerneria Moench
Kerria DC.
Kerria japonica
Kerriochloa C.E.Hubb.
Kerriochloa siamensis
Kerriodoxa J.Dransf.
Kerryia G.W.Rothwell & D.C.Wight, 1989
Kersia carnosa
Kersia foliosa
Kersia gossweileri
Kersia kalachariensis
Kersia laburnifolia
Kersia mossamedensis
Kersia paxii
Kersia suffruticosa
Kerstingiella Harms
Keteleeria Carrière
Keteleeria davidiana
Keteleeria evelyniana
Keteleeria ezoana
Keteleeria fortunei
Ketmia Mill.
Kewa acida
Kewa angrae-pequenae
Kewa arenicola
Kewa caespitosa
Kewa Christenh.
Kewa salsoloides
Kewa suffruticosa
Kewa trachysperma
Keysseria bellidiformis
Keysseria fasciculata
Keysseria gibbsiae
Keysseria helena
Keysseria Lauterb.
Keysseria pinguiculiformis
Keysseria radicans
Keysseria tomentella
Keysseria wollastonii
Khadia acutipetala
Khadia alticola
Khadia beswickii
Khadia borealis
Khadia carolinensis
Khadia media
Khaosokia D.A.Simpson, Chayam. & J.Parn.
Khasiaclunea oligocephala
Khasianthus subsessilis
Khaya A.Juss.
Khaya agboensis
Khaya anthotheca
Khaya euryphylla
Khaya grandifolia
Khaya grandifoliola
Khaya ivorensis
Khaya nyasica
Khaya senegalensis
Khmeriosicyos W.J.de Wilde & Duyfjes
Kiaeria I.Hagen
Kiaeria robusta
Kibara archboldiana
Kibara bullata
Kibara carrii
Kibara coriacea
Kibara elmeri
Kibara elongata
Kibara Endl.
Kibara ferox
Kibara flagelliformis
Kibara formicarum
Kibara fragrans
Kibara fugax
Kibara hartleyi
Kibara karengana
Kibara katikii
Kibara kostermansii
Kibara latifolia
Kibara laurifolia
Kibara leachii
Kibara microphylla
Kibara monticola
Kibara myrtoides
Kibara nitens
Kibara novobritanica
Kibara oblongata
Kibara obtusa
Kibara oligocarpella
Kibara papuana
Kibara polyantha
Kibara rennerae
Kibara roemeri
Kibara rosselensis
Kibara royenii
Kibara shungolensis
Kibara streimannii
Kibara sudestensis
Kibara symplocoides
Kibara versteeghii
Kibara warenensis
Kibaropsis caledonica
Kibaropsis Vieill. ex Guillaumin
Kibatalia arborea
Kibatalia blancoi
Kibatalia elmeri
Kibatalia G.Don
Kibatalia gitingensis
Kibatalia laurifolia
Kibatalia longifolia
Kibatalia macgregori
Kibatalia macrophylla
Kibatalia maingayi
Kibatalia merrilliana
Kibatalia puberula
Kibatalia villosa
Kibera Adans.
Kibessia DC.
Kickxia
Kickxia aegyptiaca
Kickxia arborea
Kickxia bibolophylla
Kickxia Blume
Kickxia cirrhosa
Kickxia collenetteana
Kickxia commutata
Kickxia confinis
Kickxia corallicola
Kickxia dentata
Kickxia elatine
Kickxia elatinoides
Kickxia floribunda
Kickxia gombaultii
Kickxia hartlii
Kickxia lanigera
Kickxia membranacea
Kickxia papillosa
Kickxia petiolata
Kickxia pseudoscoparia
Kickxia sabarum
Kickxia saccata
Kickxia scalarum
Kickxia spuria
Kidstonia heracleensis
Kielmeyera abdita
Kielmeyera albopunctata
Kielmeyera altissima
Kielmeyera anisosepala
Kielmeyera argentea
Kielmeyera bifaria
Kielmeyera carnea
Kielmeyera cataractae
Kielmeyera colibri
Kielmeyera coriacea
Kielmeyera corymbosa
Kielmeyera decipiens
Kielmeyera decipines
Kielmeyera doceana
Kielmeyera excelsa
Kielmeyera ferruginea
Kielmeyera ferruginosa
Kielmeyera gracilis
Kielmeyera grandiflora
Kielmeyera humifusa
Kielmeyera humilis
Kielmeyera inopinata
Kielmeyera juruenensis
Kielmeyera lathrophyton
Kielmeyera marauensis
Kielmeyera Mart.
Kielmeyera membranacea
Kielmeyera microphylla
Kielmeyera neglecta
Kielmeyera neriifolia
Kielmeyera obtecta
Kielmeyera occhioniana
Kielmeyera oreophila
Kielmeyera paniculata
Kielmeyera peruviana
Kielmeyera petiolaris
Kielmeyera pulcherrima
Kielmeyera pumila
Kielmeyera reticulata
Kielmeyera rizziniana
Kielmeyera rosea
Kielmeyera rubriflora
Kielmeyera rufotomentosa
Kielmeyera rugosa
Kielmeyera rupestris
Kielmeyera sigillata
Kielmeyera similis
Kielmeyera speciosa
Kielmeyera stevensii
Kielmeyera tomentosa
Kielmeyera trichophora
Kielmeyera variabilis
Kielmiera G.Don, 1831
Kiewia perakensis
Kiewia ridleyi
Kiewia teijsmannii
Kigelia africana
Kigelia DC.
Kigelia lutea
Kiggelaria africana
Kiggelaria L.
Kihansia jengiensis
Kihansia lovettii
Killickia grandiflora
Killickia pilosa
Killinga Adans.
Killinga T.Lestib.
Killingia Juss., 1789
Killipia Gleason
Killipiella A.C.Sm.
Killipiodendron Kobuski
Kinabaluchloa nebulosa
Kinabaluchloa wrayi
Kindbergia africana
Kindbergia arbuscula
Kindbergia brittoniae
Kindbergia Ochyra
Kindbergia oedogonia
Kindbergia oregana
Kindbergia praelonga
Kindbergia squarrifolia
Kindia Cheek
Kindia gangan
Kingdonia Balf.f. & W.Sm.
Kingella Tiegh.
Kinghamia angustifolia
Kinghamia engleriana
Kinghamia foliosa
Kinghamia macrocephala
Kinghamia nigritana
Kingia australis
Kingianthus H.Rob.
Kingianthus paniculatus
Kingianthus paradoxus
Kingiodendron Harms
Kingiolejeunea guayanensis
Kingiolejeunea H.Rob.
Kingsboroughia Liebm.
Kingstonia Hook.f. & Thomson
Kinostemon Kudô
Kintarosiphonia S.Uwai & M.Masuda, 1999
Kintokiocolax aggregatocerantha
Kintokiocolax T.Tanaka & Y.Nozawa, 1960
Kionophyton Garay
Kionophyton pollardianum
Kionophyton sawyeri
Kionophyton seminuda
Kippistia F.Muell.
Kippistia suaedifolia
Kirchara Hort., 1959
Kirchheimeria R.Kowalski, 2018
Kirchheimerisporites tenuiradiatus
Kirchneria C.F.W.Braun, 1854
Kirchneriella
Kirchneriella arcuata
Kirchneriella dianae
Kirchneriella incurvata
Kirchneriella irregularis
Kirchneriella lunaris
Kirchneriella major
Kirchneriella obesa
Kirchneriella pinguis
Kirchneriella roselata
Kirchneriella Schmidle, 1893
Kirchneriellosaccus A.K.M.N.Islam, 1969
Kirengeshoma palmata
Kirengeshoma Yatabe
Kirganelia Juss.
Kirilowia Bunge
Kirkbridea tetramera
Kirkia acuminata
Kirkia burgeri
Kirkia dewinteri
Kirkia leandrii
Kirkia Oliv.
Kirkia tenuifolia
Kirkia wilmsii
Kirkiaceae
Kirkianella Allan
Kirstea zinkeiseni
Kissenia arabica
Kissenia capensis
Kissenia R.Br. ex Endl.
Kissenia R.Br. ex T.Anderson
Kitagawia baicalensis
Kitagawia eryngiifolia
Kitagawia formosana
Kitagawia komarovii
Kitagawia litoralis
Kitagawia macilenta
Kitagawia pilifera
Kitagawia Pimenov
Kitagawia praeruptora
Kitagawia stepposa
Kitagawia terebinthacea
Kitaibela balansae
Kitaibela vitifolia
Kitaibela Willd.
Kitaibelia balansae
Kitaibelia Willd.
Kitamuria glehnii
Kitchingia Baker
Kixia Blume
Kjellbergiodendron Burret
Kjellbergiodendron celebicum
Klackenbergia condensata
Klackenbergia stricta
Klaineanthus gaboniae
Klaineanthus gabonii
Klaineanthus Pierre ex Prain
Klainedoxa gabonensis
Klainedoxa Pierre ex Engl.
Klainedoxa trillesii
Klaprothia fasciculata
Klaprothia Kunth
Klaprothia mentzelioides
Klarobelia anomala
Klarobelia cauliflora
Klarobelia Chatrou
Klarobelia lucida
Klarobelia napoensis
Klarobelia peruviana
Klarobelia rocioae
Klarobelia stipitata
Klarobelia subglobosa
Klasea algarbiensis
Klasea aphyllopoda
Klasea aznavouriana
Klasea baetica
Klasea biebersteiniana
Klasea boetica
Klasea bornmuelleri
Klasea bulgarica
Klasea cardunculus
Klasea centauroides
Klasea cerinthifolia
Klasea chartacea
Klasea coriacea
Klasea cretica
Klasea dissecta
Klasea erucifolia
Klasea flavescens
Klasea gracillima
Klasea grandifolia
Klasea hakkiarica
Klasea hastifolia
Klasea haussknechtii
Klasea integrifolia
Klasea khuzistanica
Klasea kotschyi
Klasea latifolia
Klasea legionensis
Klasea leptoclada
Klasea litwinowii
Klasea lycopifolia
Klasea lyratifolia
Klasea marginata
Klasea melanocheila
Klasea moreana
Klasea nudicaulis
Klasea oligocephala
Klasea pallida
Klasea pinnatifida
Klasea procumbens
Klasea pusilla
Klasea quinquefolia
Klasea radiata
Klasea serratuloides
Klasea sogdiana
Klasea suffruticulosa
Klasea suffulta
Klasea viciifolia
Klaseopsis chinensis
Klattia Baker
Klattia flava
Klattia stokoei
Klausipollenites J.Jansonius, 1962
Klausipollenites staplinii
Klebsormidiaceae
Klebsormidiophyceae
Klebsormidium
Klebsormidium bilatum
Klebsormidium crenulatum
Klebsormidium dissectum
Klebsormidium elegans
Klebsormidium flaccidum
Klebsormidium fluitans
Klebsormidium klebsii
Klebsormidium montanum
Klebsormidium mucosum
Klebsormidium nitens
Klebsormidium P.C.Silva, K.Mattox & W.Blackwell, 1972
Klebsormidium subtile
Kleinhovia L.
Kleinia abyssinica
Kleinia amaniensis
Kleinia anteuphorbium
Kleinia barbertonica
Kleinia caespitosa
Kleinia cephalophora
Kleinia chimanimaniensis
Kleinia cliffordiana
Kleinia Crantz
Kleinia curvata
Kleinia deflersii
Kleinia descoingsii
Kleinia dolichocoma
Kleinia fulgens
Kleinia galpinii
Kleinia gonoclada
Kleinia gracilis
Kleinia grandiflora
Kleinia grantii
Kleinia gregorii
Kleinia herreiana
Kleinia implexa
Kleinia Jacq.
Kleinia kleinioides
Kleinia leptophylla
Kleinia lunulata
Kleinia madagascariensis
Kleinia mccoyi
Kleinia Mill.
Kleinia mweroensis
Kleinia negrii
Kleinia neriifolia
Kleinia odora
Kleinia ogadensis
Kleinia oligodonta
Kleinia patriciae
Kleinia pendula
Kleinia petraea
Kleinia picticaulis
Kleinia polycotoma
Kleinia saginata
Kleinia schweinfurthii
Kleinia scottii
Kleinia semperviva
Kleinia squarrosa
Kleinia stapeliiformis
Kleinia suffruticosa
Kleinia triantha
Kleinia tuberculata
Kleinia venteri
Kleinia vermicularis
Kleinia walkeri
Kleioweisiopsis
Kleioweisiopsis denticulata
Klenzea rosmarinifolia
Klikovispermum E.Knobloch & D.H.Mai, 1984
Klippsteinia medullaris
Klitzschophyllites A.Lejal-Nicol, 1981
Klotzschia brasiliensis
Klotzschia glaziovii
Klotzschia rhizophylla
Klugia Schltdl.
Klugiodendron Britton & Killip
Klukia canadensis
Klukia exilis
Klukia M.Raciborski, 1890
Klukisporites foveolatus
Klukisporites labiatus
Klukisporites neovariegatus
Klukisporites R.A.Couper, 1958
Klukisporites variegatus
Kmeria Dandy
Knantia Hill
Knautia adriatica
Knautia alleizettei
Knautia ambigua
Knautia arvensis
Knautia arvensis x dipsacifolia
Knautia arvensis x Knautia basaltica var. foreziensis
Knautia arvernica
Knautia balcanica
Knautia baldensis
Knautia byzantina
Knautia calycina
Knautia carinthiaca
Knautia chassagnei
Knautia clementii
Knautia collina
Knautia dalmatica
Knautia degenii
Knautia dinarica
Knautia dipsacifolia
Knautia drymeia
Knautia fleischmannii
Knautia foreziensis
Knautia godetii
Knautia goecmenii
Knautia gracilis
Knautia granatensis
Knautia gussonei
Knautia hungarica
Knautia hybrida
Knautia illyrica
Knautia integrifolia
Knautia involucrata
Knautia kitaibelii
Knautia L.
Knautia latifolia
Knautia laxifoliata
Knautia lebrunii
Knautia legionensis
Knautia leucantha
Knautia longifolia
Knautia lucana
Knautia luteola
Knautia lyrophylla
Knautia macedonica
Knautia magnifica
Knautia mauritanica
Knautia midzorensis
Knautia mollis
Knautia nevadensis
Knautia norica
Knautia numantina
Knautia orientalis
Knautia orientalist
Knautia pancicii
Knautia pectinata
Knautia persicina
Knautia pontica
Knautia posoniensis
Knautia queraltii
Knautia rechingeri
Knautia ressmannii
Knautia rigidiuscula
Knautia rupicola
Knautia salvadoris
Knautia sambucifolia
Knautia serpentinicola
Knautia shepardii
Knautia slovaca
Knautia speciosa
Knautia subcanescens
Knautia subscaposa
Knautia tatarica
Knautia transalpina
Knautia travnicensis
Knautia velebitica
Knautia velutina
Knautia virgata
Knautia visianii
Kneiffia Spach
Knema andamanica
Knema angustifolia
Knema ashtonii
Knema attenuata
Knema austrosiamensis
Knema bengalensis
Knema casearioides
Knema celebica
Knema cinerea
Knema conferta
Knema conica
Knema curtisii
Knema elegans
Knema elmeri
Knema erratica
Knema furfuracea
Knema galeata
Knema glauca
Knema glaucescens
Knema globularia
Knema globulatericia
Knema glomerata
Knema hirtella
Knema hookerana
Knema hookeriana
Knema intermedia
Knema kinabaluensis
Knema korthalsii
Knema kostermansiana
Knema krusemaniana
Knema kunstleri
Knema lampongensis
Knema latericia
Knema lateritica
Knema latifolia
Knema laurina
Knema linguiformis
Knema linifolia
Knema longepilosa
Knema losirensis
Knema Lour.
Knema lunduensis
Knema luteola
Knema malayana
Knema mandaharan
Knema matanensis
Knema membranifolia
Knema minima
Knema mixta
Knema muscosa
Knema oblongata
Knema oblongifolia
Knema obovoidea
Knema pachycarpa
Knema patentinervia
Knema pectinata
Knema pedicellata
Knema percoriacea
Knema piriformis
Knema plumulosa
Knema poilanei
Knema pseudolaurina
Knema psilantha
Knema pubiflora
Knema pulchra
Knema retusa
Knema riangensis
Knema ridsdaleana
Knema rigidifolia
Knema rubens
Knema rufa
Knema saxatilis
Knema scortechinii
Knema sericea
Knema sessiflora
Knema squamulosa
Knema steenisii
Knema stellata
Knema stenophylla
Knema stylosa
Knema sumatrana
Knema tenuinervia
Knema tomentella
Knema tonkinensis
Knema tridactyla
Knema uliginosa
Knema woodii
Knesebeckia Klotzsch
Knightia excelsa
Knightia R.Br.
Knightiophyllum Ettingshausen, 1887
Knightiophyllum wilcoxianum
Kniphofia acraea
Kniphofia albescens
Kniphofia albomontana
Kniphofia angustifolia
Kniphofia ankaratrensis
Kniphofia benguellensis
Kniphofia bequaertii
Kniphofia breviflora
Kniphofia bruceae
Kniphofia buchananii
Kniphofia citrina
Kniphofia coddiana
Kniphofia coralligemma
Kniphofia corallina
Kniphofia crassifolia
Kniphofia drepanophylla
Kniphofia dubia
Kniphofia ensifolia
Kniphofia evansii
Kniphofia fibrosa
Kniphofia flammula
Kniphofia galpinii
Kniphofia goetzei
Kniphofia gracilis
Kniphofia grantii
Kniphofia hildebrandtii
Kniphofia hirsuta
Kniphofia hybr
Kniphofia hybrida
Kniphofia ichopensis
Kniphofia isoetifolia
Kniphofia kirkii
Kniphofia laxiflora
Kniphofia leucocephala
Kniphofia linearifolia
Kniphofia littoralis
Kniphofia marungensis
Kniphofia Moench
Kniphofia nana
Kniphofia nubigena
Kniphofia pallidiflora
Kniphofia paludosa
Kniphofia parviflora
Kniphofia pauciflora
Kniphofia porphyrantha
Kniphofia praecox
Kniphofia primulina
Kniphofia princeae
Kniphofia pumila
Kniphofia reflexa
Kniphofia reynoldsii
Kniphofia rigidifolia
Kniphofia ritualis
Kniphofia rooperi
Kniphofia rufa
Kniphofia sarmentosa
Kniphofia splendida
Kniphofia stricta
Kniphofia sumarae
Kniphofia tabularis
Kniphofia thodei
Kniphofia thomsonii
Kniphofia triangularis
Kniphofia typhoides
Kniphofia tysonii
Kniphofia umbrina
Kniphofia uvaria
Kniphofia vandeweghei
Knorria imbricata
Knorria Sternberg, 1825
Knorringia sibirica
Knowltonella maxoni
Knowltonia anemonoides
Knowltonia assisbrasiliana
Knowltonia balliana
Knowltonia bracteata
Knowltonia brevistylis
Knowltonia caffra
Knowltonia capensis
Knowltonia chilensis
Knowltonia cordata
Knowltonia crassifolia
Knowltonia fanninii
Knowltonia filia
Knowltonia helleborifolia
Knowltonia hepaticifolia
Knowltonia hootae
Knowltonia integrifolia
Knowltonia major
Knowltonia mexicana
Knowltonia moorei
Knowltonia Salisb.
Knowltonia sellowii
Knowltonia tenuifolia
Knowltonia transvaalensis
Knowltonia vesicatoria
Knowltonia whyteana
Knoxia brachycarpa
Knoxia brunonis
Knoxia hedyotoidea
Knoxia hookeri
Knoxia L.
Knoxia lineata
Knoxia manika
Knoxia mollis
Knoxia plantaginea
Knoxia platycarpa
Knoxia rosettifolia
Knoxia roxburghii
Knoxia scandens
Knoxia spicata
Knoxia stricta
Knoxia sumatrensis
Knoxia wightiana
Knoxisporites R.Potonié & G.O.W.Kremp, 1954
Koanophyllon adamantium
Koanophyllon albicaule
Koanophyllon andersonii
Koanophyllon Arruda
Koanophyllon atroglandulosum
Koanophyllon ayapanoides
Koanophyllon baccharifolium
Koanophyllon barahonense
Koanophyllon breviflorum
Koanophyllon bullescens
Koanophyllon cabaionum
Koanophyllon calcicola
Koanophyllon celtidifolia
Koanophyllon chabrense
Koanophyllon chalceorithales
Koanophyllon clementis
Koanophyllon coixtlahuacum
Koanophyllon concordianum
Koanophyllon conglobatum
Koanophyllon consanguineum
Koanophyllon constanzae
Koanophyllon correlliorum
Koanophyllon coulteri
Koanophyllon delpechianum
Koanophyllon dolicholepis
Koanophyllon dolphinii
Koanophyllon droserolepis
Koanophyllon eitenii
Koanophyllon ekmanii
Koanophyllon flavidulum
Koanophyllon flexile
Koanophyllon fuscum
Koanophyllon gabbii
Koanophyllon galeanum
Koanophyllon galeottii
Koanophyllon gibbosum
Koanophyllon gracilicaule
Koanophyllon gracilipes
Koanophyllon grandiceps
Koanophyllon grisebachianum
Koanophyllon gundlachii
Koanophyllon hammatocladum
Koanophyllon hardwarense
Koanophyllon helianthemoides
Koanophyllon heptaneurum
Koanophyllon hidrodes
Koanophyllon hintoniorum
Koanophyllon hondurensis
Koanophyllon hotteanum
Koanophyllon hylonomum
Koanophyllon hypomalaca
Koanophyllon isillumense
Koanophyllon iteophyllum
Koanophyllon jaegerianum
Koanophyllon jenssenii
Koanophyllon jinotegense
Koanophyllon juninense
Koanophyllon littorale
Koanophyllon lobatifolia
Koanophyllon longifolia
Koanophyllon maestrense
Koanophyllon mesoreopolum
Koanophyllon microchaetum
Koanophyllon minutifolium
Koanophyllon miragoanae
Koanophyllon monanthum
Koanophyllon montanum
Koanophyllon mornicola
Koanophyllon myrtilloides
Koanophyllon nervosum
Koanophyllon nudiflorum
Koanophyllon obtusissimum
Koanophyllon pachyneurum
Koanophyllon palmeri
Koanophyllon panamense
Koanophyllon paucicrenatum
Koanophyllon peninsulare
Koanophyllon picardae
Koanophyllon pitonianum
Koanophyllon pittieri
Koanophyllon polyodon
Koanophyllon polystictum
Koanophyllon porphyrocladum
Koanophyllon prinodes
Koanophyllon pseudoperfoliata
Koanophyllon puberulum
Koanophyllon quisqueyanum
Koanophyllon revealii
Koanophyllon reversum
Koanophyllon rhexioides
Koanophyllon richardsonii
Koanophyllon rubroviolaceum
Koanophyllon rzedowskii
Koanophyllon sagasteguii
Koanophyllon scabriusculum
Koanophyllon selleanum
Koanophyllon semicrenatum
Koanophyllon silvaticum
Koanophyllon simile
Koanophyllon simillimum
Koanophyllon sinaloensis
Koanophyllon solidaginifolium
Koanophyllon solidaginoides
Koanophyllon sorensenii
Koanophyllon standleyi
Koanophyllon subpurpureum
Koanophyllon tapeinanthum
Koanophyllon tatei
Koanophyllon tetranthum
Koanophyllon thysanolepis
Koanophyllon tinctorium
Koanophyllon tricephalotes
Koanophyllon tripartitum
Koanophyllon turquiensis
Koanophyllon villosum
Koanophyllon wetmorei
Koanophyllum Arruda ex H.Kost., 1817
Kobresia angusta
Kobresia curvata
Kobresia hookeri
Kobresia inflata
Kobresia koelzii
Kobresia reticularis
Kobresia schoenoides
Kobresia scirpina
Kobresia seticulmis
Kochia arenaria
Kochia diffusa
Kochia mollis
Kochia Roth
Kochummenia K.M.Wong
Kochummenia parviflora
Kochummenia stenopetala
Koeberlinia holacantha
Koeberlinia spinosa
Koeberlinia Zucc.
Koehleria Benth. & Hook.f., 1876
Koehneola repens
Koehneria madagascariensis
Koehneria S.A.Graham, Tobe & Baas
Koeleria
Koeleria altaica
Koeleria antarctica
Koeleria arduana
Koeleria arenaria
Koeleria argentea
Koeleria asiatica
Koeleria askoldensis
Koeleria barabensis
Koeleria barbinodis
Koeleria barrosii
Koeleria biebersteinii
Koeleria boliviensis
Koeleria brevis
Koeleria calderonii
Koeleria capensis
Koeleria carolii
Koeleria caucasica
Koeleria caudata
Koeleria cenisia
Koeleria cheesemanii
Koeleria colorata
Koeleria crassipes
Koeleria cristata
Koeleria cumingii
Koeleria delavignei
Koeleria dersu
Koeleria digorica
Koeleria drucei
Koeleria embergeri
Koeleria eriostachya
Koeleria fominii
Koeleria fueguina
Koeleria glauca
Koeleria grandis
Koeleria hirsuta
Koeleria hispanica
Koeleria hungarica
Koeleria inaequaliglumis
Koeleria inaequalis
Koeleria insubrica
Koeleria intermedia
Koeleria johnstonii
Koeleria kangdingensis
Koeleria karavajevii
Koeleria koidzumiana
Koeleria kurtzii
Koeleria lasiorhachis
Koeleria lepida
Koeleria ligulata
Koeleria loweana
Koeleria lucana
Koeleria luerssenii
Koeleria macrantha
Koeleria mendocinensis
Koeleria micans
Koeleria moldavica
Koeleria montana
Koeleria nancaguensis
Koeleria nitidula
Koeleria oreophila
Koeleria permollis
Koeleria Pers.
Koeleria preslii
Koeleria projecta
Koeleria pubescens
Koeleria pyramidata
Koeleria rhodopea
Koeleria rodriguez-graciae
Koeleria schroeteriana
Koeleria serpentina
Koeleria sibirica
Koeleria spicata
Koeleria splendens
Koeleria subalpestris
Koeleria tenella
Koeleria thonii
Koeleria tzvelevii
Koeleria vallesiana
Koeleria vaseyi
Koeleria ventanicola
Koeleria vurilochensis
Koellensteinia carraoensis
Koellensteinia dasilvae
Koellensteinia eburnea
Koellensteinia florida
Koellensteinia graminea
Koellensteinia hyacinthoides
Koellensteinia kellneriana
Koellensteinia lilijae
Koellensteinia Rchb.f.
Koellensteinia spiralis
Koellensteinia tricolor
Koellia fascicularis
Koellia huronensis
Koellia Moench
Koellia tullia
Koellikeria ovalifolia
Koellikeria Regel
Koelpinia linearis
Koelpinia macrantha
Koelpinia rhagadioloides
Koelpinia tenuissima
Koelpinia turanica
Koelreuteria annosa
Koelreuteria bipinnata
Koelreuteria elegans
Koelreuteria Laxm.
Koelreuteria paniculata
Koenigia ajanensis
Koenigia alpina
Koenigia amgensis
Koenigia bargusinensis
Koenigia brachytricha
Koenigia campanulata
Koenigia cathayana
Koenigia chaneyi
Koenigia chlorochrysea
Koenigia coriaria
Koenigia cyanandra
Koenigia davisiae
Koenigia delicatula
Koenigia divaricata
Koenigia fennica
Koenigia fertilis
Koenigia filicaulis
Koenigia forrestii
Koenigia hookeri
Koenigia islandica
Koenigia jurii
Koenigia L.
Koenigia lapathifolia
Koenigia lichiangensis
Koenigia limosa
Koenigia microcarpa
Koenigia middendorffii
Koenigia mollifolia
Koenigia mollis
Koenigia nepalensis
Koenigia nummularifolia
Koenigia ochreata
Koenigia ocreata
Koenigia panjutinii
Koenigia phytolaccifolia
Koenigia pilosa
Koenigia polystachya
Koenigia relicta
Koenigia rumicifolia
Koenigia sajanensis
Koenigia sericea
Koenigia songarica
Koenigia subsericea
Koenigia tortuosa
Koenigia tripterocarpa
Koenigia weyrichii
Koenigia yatagaiana
Koernickanthe L.Andersson
Koernickanthe orbiculata
Kogelbergia phylicoides
Kogelbergia Rourke
Kogelbergia verticillata
Kohautia amatymbica
Kohautia angolensis
Kohautia aspera
Kohautia caespitosa
Kohautia Cham. & Schltdl.
Kohautia coccinea
Kohautia confusa
Kohautia cynanchica
Kohautia dolichostyla
Kohautia gracilis
Kohautia grandiflora
Kohautia huillensis
Kohautia kimuenzae
Kohautia microflora
Kohautia nagporensis
Kohautia platyphylla
Kohautia ramosissima
Kohautia retrorsa
Kohautia subverticillata
Kohautia tenuis
Kohleria affinis
Kohleria allenii
Kohleria amabilis
Kohleria andina
Kohleria bella
Kohleria gigantea
Kohleria grandiflora
Kohleria hirsuta
Kohleria hondensis
Kohleria huilensis
Kohleria hypertrichosa
Kohleria inaequalis
Kohleria longicalyx
Kohleria lucianii
Kohleria neglecta
Kohleria peruviana
Kohleria Regel
Kohleria rugata
Kohleria spicata
Kohleria stubeliana
Kohleria tigridia
Kohleria trianae
Kohleria tubiflora
Kohleria villosa
Kohleria warszewiczii
Kohlrauschia Kunth
Koilodepas bantamense
Koilodepas brevipes
Koilodepas calycinum
Koilodepas cordisepalum
Koilodepas ferrugineum
Koilodepas frutescens
Koilodepas hainanense
Koilodepas laevigatum
Koilodepas longifolium
Koilodepas pectinatum
Koilodepas wallichianum
Koilosphenus B.Bohlin, 1971
Koilosphenus cuneifolius
Kokia cookei
Kokia drynarioides
Kokia lanceolata
Kokia Lewton
Kokoona coriacea
Kokoona littoralis
Kokoona ochracea
Kokoona ovatolanceolata
Kokoona reflexa
Kokoona sessilis
Kokoona zeylanica
Koliella antarctica
Koliella F.Hindák, 1963
Koliella longiseta
Koliella sempervirens
Koliella setiformis
Koliella spiculiformis
Koliella spiralis
Koliella spirotaenia
Koliellaceae
Koliellopsis G.M.Lokhorst, 2004
Kolkwitzia amabilis
Kolkwitzia Graebn.
Kolobopetalum chevalieri
Kolobopetalum Engl.
Kolobopetalum ovatum
Kolobopetalum synsepalum
Kolowratia C.Presl
Kolowratia eruciformis
Kolymella V.A.Samylina & G.G.Filippova, 1970
Komarekia appendiculata
Komarekia Fott, 1981
Komaroffia bucharica
Komaroffia integrifolia
Komaroffia Kuntze
Komaroviopsis anisosperma
Komaroviopsis Doweld
Komia Korde, 1952
Komlopteris cenozoicus
Komlopteris M.Barbacka, 1994
Koniga brunonis
Koniga R.Br.
Konigia Comm. ex Cav., 1787
Koninckopora G.W.Lee, 1912
Koompassia excelsa
Koompassia grandiflora
Koompassia malaccensis
Koompassia parviflora
Koompassioxylon elegans
Koompassioxylon K.Kramer, 1974
Koordersiochloa longiarista
Koordersiodendron Engl.
Koordersiodendron pinnatum
Koordersisdendron
Kopetdagaria sphaerica
Koponenia holoneuron
Koponeniella bolanderi
Koponeniella graminicolor
Koponeniella tenerrima
Kopsia angustipetala
Kopsia arborea
Kopsia Blume
Kopsia dasyrachis
Kopsia deverrei
Kopsia flavida
Kopsia fruticosa
Kopsia griffithii
Kopsia hainanensis
Kopsia harmandiana
Kopsia lapidilecta
Kopsia larutensis
Kopsia macrophylla
Kopsia pauciflora
Kopsia rajangensis
Kopsia rosea
Kopsia singapurensis
Kopsia sleeseniana
Kopsia sumatrana
Kopsia tenuis
Kopsia tonkinensis
Kopsiopsis hookeri
Kopsiopsis strobilacea
Kordephyton K.V.Radugin & M.V.Stepanova, 1964
Koretrophyllites G.P.Radczenko, 1955
Koretrophyllites mungaticus
Korkyrella ivanovici
Kornmannia C.Bliding, 1969
Kornmannia leptoderma
Kornmanniaceae
Korojonia dubiosa
Korolkowia Regel
Korschpalmella Fott, 1974
Korshikoviella limnetica
Korshikoviella michailovskoensis
Korshikoviella P.C.Silva, 1959
Korshinskia assyriaca
Korshinskia olgae
Korshinskia tianschanica
Korshinskya bupleuroides
Korshinskya kopetdaghensis
Korshinskya olgae
Korthalsella amentacea
Korthalsella arthroclada
Korthalsella breviarticulata
Korthalsella chilensis
Korthalsella clavata
Korthalsella complanata
Korthalsella cylindrica
Korthalsella dacrydii
Korthalsella degeneri
Korthalsella disticha
Korthalsella emersa
Korthalsella gaudichaudii
Korthalsella grayi
Korthalsella horneana
Korthalsella japonica
Korthalsella latissima
Korthalsella leucothrix
Korthalsella lindsayi
Korthalsella madagascarica
Korthalsella margaretae
Korthalsella papuana
Korthalsella platycaula
Korthalsella rapensis
Korthalsella remyana
Korthalsella rubescens
Korthalsella rubra
Korthalsella salicornioides
Korthalsella taeniodes
Korthalsella taenioides
Korthalsella Tiegh.
Korthalsia angustifolia
Korthalsia bejaudii
Korthalsia Blume
Korthalsia celebica
Korthalsia cheb
Korthalsia concolor
Korthalsia debilis
Korthalsia echinometra
Korthalsia ferox
Korthalsia flagellaris
Korthalsia furcata
Korthalsia furtadoana
Korthalsia hispida
Korthalsia jala
Korthalsia laciniosa
Korthalsia lanceolata
Korthalsia merrillii
Korthalsia minor
Korthalsia rigida
Korthalsia robusta
Korthalsia rogersii
Korthalsia rostrata
Korthalsia scaphigeroides
Korthalsia scortechinii
Korthalsia tenuissima
Korthalsia zippelii
Korupodendron songweanum
Koshicola Shin Watanabe, K.Fucíková & L.A.Lewis, 2016
Koskinobullina Cherchi & Schroeder, 1979
Koskinobullina socialis
Kosmogyrina K.Mädler, 1952
Kosmosiphon azureus
Kosteletskya Brongn., 1843
Kosteletzkya adoensis
Kosteletzkya batacensis
Kosteletzkya blanchardii
Kosteletzkya buettneri
Kosteletzkya C.Presl
Kosteletzkya depressa
Kosteletzkya diplocrater
Kosteletzkya flavicentrum
Kosteletzkya grantii
Kosteletzkya hispidula
Kosteletzkya madagascarensis
Kosteletzkya pentacarpos
Kosteletzkya racemosa
Kosteletzkya ramosa
Kosteletzkya reclinata
Kosteletzkya semota
Kosteletzkya thurberi
Kosteletzkya tubiflora
Kosteletzkya wetarensis
Kostermansia malayana
Kostermanthus heteropetalus
Kostermanthus malayanus
Kostermanthus Prance
Kostermanthus robustus
Kotchubaea duckei
Kotchubaea longiloba
Kotchubaea morilloi
Kotchubaea neblinensis
Kotchubaea Regel ex Benth. & Hook.f.
Kotchubaea urophylla
Kotschya aeschynomenoides
Kotschya africana
Kotschya bullockii
Kotschya capitulifera
Kotschya carsonii
Kotschya coalescens
Kotschya Endl.
Kotschya eurycalyx
Kotschya goetzei
Kotschya imbricata
Kotschya longiloba
Kotschya lutea
Kotschya micrantha
Kotschya ochreata
Kotschya oubanguiensis
Kotschya parvifolia
Kotschya perrieri
Kotschya platyphylla
Kotschya princeana
Kotschya prittwitzii
Kotschya recurvifolia
Kotschya scaberrima
Kotschya schweinfurthii
Kotschya strigosa
Kotschya strobilantha
Kotschya thymodora
Kotschya uguenensis
Kotschya uniflora
Kovalevskiella kovalevskiana
Kovalevskiella rapunculoides
Kovalevskiella rosea
Kovalevskiella zeravschanica
Koyamacalia maekawae
Koyamaea neblinensis
Koyamaea W.W.Thomas & G.Davidse
Koyamasia calcarea
Koyamasia curtisii
Kozlovia capnoides
Kozlovia laseroides
Kozlovia longiloba
Kozlovia paleacea
Kraeuselisporites Leschik
Kraftalia gracilis
Kraftalia Lagourgue & Payri, 2021
Kraftia dichotoma
Kralikella Coss. & Durieu
Krameria argentea
Krameria bahiana
Krameria bicolor
Krameria cistoidea
Krameria erecta
Krameria grandiflora
Krameria ixine
Krameria L.
Krameria lanceolata
Krameria lappacea
Krameria Loefl.
Krameria pauciflora
Krameria paucifolia
Krameria ramosissima
Krameria revoluta
Krameria secundiflora
Krameria tomentosa
Krameriaceae
Kraniopsis Raf.
Krapfia clypeata
Krapfia DC.
Krapfia gigas
Krapfia lechleri
Krapfia macropetala
Krapfia ranunculina
Krapfia weberbaueri
Krapovickasia flavescens
Krapovickasia Fryxell
Krapovickasia macrodon
Krapovickasia physaloides
Krapovickasia urticifolia
Krascheninikovia Turcz. ex Fenzl
Krascheninnikovia
Krascheninnikovia ceratoides
Krascheninnikovia ewersmanniana
Krascheninnikovia fruticulosa
Krascheninnikovia Gueldenst.
Krascheninnikovia lanata
Krassera O.Schwartz
Krausella H.J.Lam
Krauseola gillettii
Krauseola mosambicina
Kraussia floribunda
Kraussia Harv.
Kraussia kirkii
Kraussia Sch.Bip.
Kraussia socotrana
Kraussia speciosa
Kreidion chinensis
Kreidion gmelinii
Kreidion scopulorum
Kremeria Durieu
Kremeriella cordylocarpus
Kremeriella Maire
Krenakanthus (Leme, S.Heller & Zizka) Leme, Zizka & Paule
Krenakia claussenii
Krenakia comata
Krenakia cubensis
Krenakia humilis
Krenakia junciformis
Krenakia minarum
Krenakia polyphylla
Krenakia S.M.Costa
Krenakia subaphylla
Krenakia triquetra
Krenakia venezuelensis
Kreodanthus cajamarcae
Kreodanthus casillasii
Kreodanthus crispifolius
Kreodanthus curvatus
Kreodanthus ecuadorensis
Kreodanthus elatus
Kreodanthus Garay
Kreodanthus loxoglottis
Kreodanthus myrmex
Kreodanthus ovatilabius
Kreodanthus secundus
Kreodanthus simplex
Kreodanthus sytsmae
Kreysigia Rchb.
Krigia biflora
Krigia caespitosa
Krigia cespitosa
Krigia dandelion
Krigia montana
Krigia occidentalis
Krigia shinnersiana
Krigia virginica
Krigia wrightii
Krithodeophyton croftii
Kroenleinia grusonii
Krubera Hoffm.
Krubera peregrina
Krugiodendron acuminatum
Krugiodendron ferreum
Krugiodendron Urb.
Krukoviella A.C.Sm.
Krukoviella disticha
Krylovia Schischk.
Krynitzkia Fisch. & C.A.Mey.
Krynitzkia mixta
Kryptostoma (Summerh.) Geerinck
Kubitzkia mezii
Kubitzkia Werff, 1986
Kudoacanthus albonervosus
Kudrjaschevia korshinskyi
Kudrjaschevia nadinae
Kudrjaschevia Pojark.
Kuepferia caryophyllea
Kuepferia chateri
Kuepferia damyonensis
Kuepferia decorata
Kuepferia doxiongshangensis
Kuepferia hicksii
Kuepferia infelix
Kuepferia leucantha
Kuepferia masonii
Kuepferia otophora
Kuepferia otophoroides
Kuepferia sichitoensis
Kuerschneria laevigata
Kuetzingia angusta
Kuetzingia canaliculata
Kuetzingia Sonder, 1845
Kuhitangia Ovcz.
Kuhlia Kunth
Kuhlmanniodendron apterocarpum
Kuhlmanniodendron Fiaschi & Groppo
Kuhlmanniodendron macrocarpum
Kuhnia glutinosa
Kuhnia L.
Kuhniastera Kuntze, 1891
Kuhnistera Lam.
Kuloa ikonyokpe
Kuloa michelsonii
Kuloa usambarensis
Kulyisporites lunaris
Kulyisporites Potonié, 1956
Kumanoa abilii
Kumanoa amazonensis
Kumanoa ambigua
Kumanoa americana
Kumanoa capensis
Kumanoa cipoensis
Kumanoa equisetoidea
Kumanoa gibberosa
Kumanoa globospora
Kumanoa gracillima
Kumanoa intorta
Kumanoa montagnei
Kumanoa nodiflora
Kumanoa novaecaledonensis
Kumanoa procarpa
Kumanoa virgato-decaisneana
Kumara haemanthifolia
Kumara plicatilis
Kumlienia hystricula
Kummerowia Schindl.
Kummerowia stipulacea
Kummerowia striata
Kundasphaera Uutela, 1989
Kundmannia anatolica
Kundmannia Scop.
Kundmannia sicula
Kundmannia syriaca
Kunhardtia Maguire
Kunhardtia radiata
Kunhardtia rhodantha
Kuniwatsukia Pic.Serm.
Kunkeliella Stearn
Kunstlera King, 1887
Kunstleria curtisii
Kunstleria forbesii
Kunstleria geesinkii
Kunstleria keralensis
Kunstleria kingii
Kunstleria philippinensis
Kunstleria Prain
Kunstleria ridleyi
Kunstleria sarawakensis
Kuntheria pedunculata
Kunthia mexicana
Kunzea acicularis
Kunzea affinis
Kunzea affinis x Kunzea jucunda
Kunzea amathicola
Kunzea ambigua
Kunzea aristulata
Kunzea axillaris
Kunzea baxteri
Kunzea bracteolata
Kunzea bracteolata x Kunzea obovata
Kunzea caduca
Kunzea calida
Kunzea cambagei
Kunzea capitata
Kunzea ciliata
Kunzea cincinnata
Kunzea clavata
Kunzea corifolia
Kunzea dactylota
Kunzea dracopetrensis
Kunzea ericifolia
Kunzea ericoides
Kunzea eriocalyx
Kunzea flavescens
Kunzea form
Kunzea glabrescens
Kunzea glabrescens x Kunzea recurva
Kunzea graniticola
Kunzea jucunda
Kunzea juniperoides
Kunzea leptospermoides
Kunzea linearis
Kunzea micrantha
Kunzea micromera
Kunzea micromera x Kunzea montana
Kunzea micromera x Kunzea preissiana
Kunzea micromera x Kunzea recurva
Kunzea montana
Kunzea montana x Kunzea recurva
Kunzea muelleri
Kunzea newbeyi
Kunzea obovata
Kunzea occidentalis
Kunzea opposita
Kunzea parvifolia
Kunzea pauciflora
Kunzea petrophila
Kunzea pomifera
Kunzea praestans
Kunzea preissiana
Kunzea pulchella
Kunzea recurva
Kunzea recurva x Kunzea sulphurea
Kunzea robusta
Kunzea rosea
Kunzea rostrata
Kunzea rupestris
Kunzea salina
Kunzea salterae
Kunzea sericothrix
Kunzea similis
Kunzea sinclairii
Kunzea spathulata
Kunzea sprengelioides
Kunzea squarrosa
Kunzea strigosa
Kunzea sulphurea
Kunzea tenuicaulis
Kunzea triregensis
Kunzea truncata
Kunzea Wongan-Hills
Kunzia Spreng.
Kunzspermum hirakimata
Kupea jonii
Kupea martinetugei
Kupeantha Cheek
Kupeantha ebo
Kupeantha fosimondi
Kupeantha kupensis
Kupeantha pentamera
Kupeantha spathulata
Kuramosciadium corydalifolium
Kurrimia gracilis
Kurrimia luzonica
Kurrimia macrophylla
Kurrimia minor
Kurrimia paniculata
Kurrimia robusta
Kurrimia Wall.
Kurrimia Wall. ex Thwaites
Kurtziana cacheutensis
Kurtziana Frenguelli, 1942
Kurtziflora antherosa
Kuruna Attigala, Kaththr. & L.G.Clark
Kuruna debilis
Kuruna densifolia
Kuruna floribunda
Kuruna scandens
Kuruna serrulata
Kuruna walkeriana
Kuruna wightiana
Kurzamra pulchella
Kurzia
Kurzia abbreviata
Kurzia abietinella
Kurzia bisetula
Kurzia borneensis
Kurzia brasiliensis
Kurzia brevicalycina
Kurzia calcarata
Kurzia capillaris
Kurzia compacta
Kurzia cucullifolia
Kurzia flagellifera
Kurzia fragilifolia
Kurzia fragillima
Kurzia gonyotricha
Kurzia hawaica
Kurzia helophila
Kurzia hippurioides
Kurzia irregularis
Kurzia lateconica
Kurzia longicaulis
Kurzia makinoana
Kurzia mauiensis
Kurzia mollis
Kurzia moniliformis
Kurzia nemoides
Kurzia nivicola
Kurzia pallescens
Kurzia pallida
Kurzia pauciflora
Kurzia quinquespina
Kurzia reversa
Kurzia saddlensis
Kurzia setiformis
Kurzia sexfida
Kurzia sinensis
Kurzia sylvatica
Kurzia tasmanica
Kurzia tayloriana
Kurzia tenerrima
Kurzia trichoclados
Kurzia trilobata
Kurzia v.Martens
Kurziella gymnoclada
Kusibabella Szlach.
Kutchubaea duckei
Kutchubaea Fisch. ex DC.
Kutchubaea insignis
Kutchubaea micrantha
Kutchubaea montana
Kutchubaea neblinensis
Kutchubaea oocarpa
Kutchubaea palustris
Kutchubaea semisericea
Kutchubaea sericantha
Kutchubaea surinamensis
Kutchubaea urophylla
Kvacekispermum E.M.Friis, P.R.Crane & K.R.Pedersen, 2018
Kvaleya epilaeve
Kvaleya W.H.Adey & C.P.Sperapani, 1971
Kyandopollenites L.E.Stover, 1966
Kydia calycina
Kydia glabrescens
Kydia Roxb.
Kyhosia B.G.Baldwin
Kyhosia bolanderi
Kykloxylon B.Meyer-Berthaud, T.N.Taylor & E.L.Taylor, 1993
Kylicanthe arcuata
Kylicanthe bueae
Kylicanthe Descourv., Stévart & Droissart
Kylicanthe liae
Kylicanthe perezverae
Kylicanthe rohrii
Kylinga Roem. & Schult., 1817
Kylingia Stokes, 1812
Kylinia
Kylinia endophytica
Kylinia porphyrae
Kylinia Rosenvinge, 1909
Kylinia rosulata
Kylinia seriaspora
Kyliniella latvica
Kyliniella Skuja, 1926
Kyllinga albiceps
Kyllinga brevifolia
Kyllinga diflora
Kyllinga Rottb.
Kyllinga tetragona
Kyllinga triceps
Kyllingia L.f., 1782
Kyllingiella melanosperma
Kyllingiella R.W.Haines & Lye
Kymalithon M.Lemoine & J.Emberger, 1967
Kymatocalyx dominicensis
Kymatocalyx Herzog
Kymatocalyx madagascariensis
Kymatocalyx rhizomaticus
Kymatolejeunea bartlettii
Kyphocarpa (Fenzl) Lopr.
Kyphocarpa (Fenzl) Schinz
Kyphocarpa angustifolia
Kyphocarpa petersii
Kyphocarpa trichinoides
Kyphocarpa wilmsii
Kyphocarpa zeyheri
Kyrsteniopsis cymulifera
Kyrsteniopsis dibolii
Kyrsteniopsis heathiae
Kyrsteniopsis iltisii
Kyrsteniopsis nelsonii
Kyrsteniopsis perpetiolata
Kyrsteniopsis R.M.King & H.Rob.
Kyrsteniopsis spinaciifolia
Kyrtomisporis K.Mädler, 1964
Kyrtomisporites B.Agrali & E.Akyol, 1967""".strip().split("\n")

# ══════════════════════════════════════════════
#  LISTE DES PLANTES TOXIQUES
#  ⚠ À REMPLACER à chaque nouvelle lettre
#  → Mettre ici uniquement les noms présents
#    dans PLANTES qui sont toxiques.
#    Le nom doit être identique (même casse).
#  → Si aucune plante toxique : laisser []
# ══════════════════════════════════════════════

PLANTES_TOXIQUES = """Kalmia latifolia
Karwinskia bicolor
Karwinskia calderonii
Karwinskia californica
Karwinskia caloneura
Karwinskia colombiana
Karwinskia humboldtiana
Karwinskia johnstonii
Karwinskia oblongifolia
Karwinskia orbiculata
Karwinskia parvifolia
Karwinskia pluvialis
Karwinskia potrerilloana
Karwinskia rocana
Karwinskia rzedowskii
Karwinskia subcordata
Karwinskia tehuacana
Karwinskia umbellata
Karwinskia venturae
Karwinskia Zucc.""".strip().split("\n")

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
      <a href="../../encyclopedie/K.html">Espèces en « K »</a>
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
    <a href="../../encyclopedie/K.html" style="color:var(--accent)">← Retour aux espèces en K</a>
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
