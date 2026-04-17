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

DOSSIER_SORTIE  = "./Z_Plante_page"              # ← Dossier de sortie         ex: "./V_Plante_page"
LETTRE          = "Z"                            # ← Lettre courante            ex: "V"
LETTRE_HTML     = "Z.html"                       # ← Fichier index de la lettre ex: "V.html"
LOG_FILE        = "generation_log_pages_Z.json"  # ← Fichier log                ex: "generation_log_pages_V.json"
HEADERS         = {"User-Agent": "Herbarium-Bot/1.0"}

# ══════════════════════════════════════════════
#  LISTE DES PLANTES
#  ⚠ À REMPLACER à chaque nouvelle lettre
#  → Coller ici toutes les plantes de la lettre,
#    une par ligne, sans numérotation.
# ══════════════════════════════════════════════

PLANTES = """Zabelia (Rehder) Makino
Zabelia biflora
Zabelia corymbosa
Zabelia densipila
Zabelia dielsii
Zabelia integrifolia
Zabelia parvifolia
Zabelia triflora
Zabelia tyaihyoni
Zabelia umbellata
Zacintha Mill.
Zacyntha Adans., 1763
Zagrosia persica
Zahlbrucknera Rchb.
Zahora ait-atta
Zalacca Rumph. ex Blume
Zaleya Burm.f.
Zaleya camillii
Zaleya decandra
Zaleya galericulata
Zaleya pentandra
Zaleya redimita
Zaluzania angusta
Zaluzania augusta
Zaluzania delgadoana
Zaluzania discoidea
Zaluzania durangensis
Zaluzania grayana
Zaluzania megacephala
Zaluzania mollissima
Zaluzania montagnaefolia
Zaluzania montagnifolia
Zaluzania parthenioides
Zaluzania Pers.
Zaluzania pringlei
Zaluzania subcordata
Zaluzania triloba
Zaluzanskya
Zaluzianskia Neck.
Zaluzianskya acutiloba
Zaluzianskya affinis
Zaluzianskya angustifolia
Zaluzianskya bella
Zaluzianskya benthamiana
Zaluzianskya capensis
Zaluzianskya chasmanthiflora
Zaluzianskya chrysops
Zaluzianskya cohabitans
Zaluzianskya collina
Zaluzianskya crocea
Zaluzianskya diandra
Zaluzianskya divaricata
Zaluzianskya elgonensis
Zaluzianskya F.W.Schmidt
Zaluzianskya glareosa
Zaluzianskya gracilis
Zaluzianskya inflata
Zaluzianskya kareebergensis
Zaluzianskya karrooica
Zaluzianskya katharinae
Zaluzianskya maritima
Zaluzianskya marlothii
Zaluzianskya microsiphon
Zaluzianskya minima
Zaluzianskya mirabilis
Zaluzianskya natalensis
Zaluzianskya nemesioides
Zaluzianskya ovata
Zaluzianskya pachyrrhiza
Zaluzianskya parviflora
Zaluzianskya peduncularis
Zaluzianskya pilosa
Zaluzianskya pulvinata
Zaluzianskya pumila
Zaluzianskya pusilla
Zaluzianskya regalis
Zaluzianskya rubrostellata
Zaluzianskya sanorum
Zaluzianskya schmitziae
Zaluzianskya spathacea
Zaluzianskya synaptica
Zaluzianskya tropicalis
Zaluzianskya vallispiscis
Zaluzianskya venusta
Zaluzianskya villosa
Zaluzianskya violacea
Zameioscirpus atacamensis
Zameioscirpus Dhooge & Goetgh.
Zameioscirpus muticus
Zamia acuminata
Zamia amplifolia
Zamia angustifolia
Zamia boliviana
Zamia brasiliensis
Zamia chigua
Zamia cremnophila
Zamia cunaria
Zamia cycadifolia
Zamia debilis
Zamia decumbens
Zamia dressleri
Zamia elegantissima
Zamia encephalartoides
Zamia fairchildiana
Zamia feneonis
Zamia fischeri
Zamia furfuracea
Zamia gentryi
Zamia gigas
Zamia gomeziana
Zamia grijalvensis
Zamia hamannii
Zamia herrerae
Zamia horrida
Zamia huilensis
Zamia imperialis
Zamia incognita
Zamia inermis
Zamia integrifolia
Zamia ipetiensis
Zamia katzeriana
Zamia lacandona
Zamia latifolia
Zamia lecointei
Zamia lindenii
Zamia lindleyi
Zamia lindosensis
Zamia loddigesii
Zamia lucayana
Zamia macrochiera
Zamia manicata
Zamia media
Zamia melanorrhachis
Zamia montana
Zamia monticola
Zamia multidentata
Zamia muricata
Zamia nana
Zamia nesophila
Zamia neurophyllidia
Zamia obliqua
Zamia oligodonta
Zamia onan-reyesii
Zamia oreillyi
Zamia paucifoliolata
Zamia paucijuga
Zamia poeppigiana
Zamia portoricensis
Zamia prasina
Zamia pseudomonticola
Zamia pseudoparasitica
Zamia pumila
Zamia purpurea
Zamia pygmaea
Zamia pyrophylla
Zamia restrepoi
Zamia roezlii
Zamia sandovalii
Zamia skinneri
Zamia soconuscensis
Zamia spartea
Zamia spiralis
Zamia splendens
Zamia standleyi
Zamia stevensonii
Zamia stricta
Zamia taxina
Zamia tridentata
Zamia tuerckheimii
Zamia ulei
Zamia urep
Zamia variegata
Zamia verschaffeltii
Zamia wallisii
Zamia wilcoxensis
Zamioculcas zamiifolia
Zamiophyllum A.G.Nathorst, 1890
Zamiophyllum buchianum
Zamiopsis Fontaine, 1889
Zamiopsis laciniata
Zamiopsis petiolata
Zamiopteris glossopteroides
Zamiopteris J.Schmalhausen, 1879
Zamiostrobus emmonsi
Zamiostrobus mirabilis
Zamiostrobus virginiensis
Zamites A.T.Brongniart, 1828
Zamites acutipennis
Zamites alaskana
Zamites apertus
Zamites arcticus
Zamites borealis
Zamites brevifolius
Zamites carruthersii
Zamites crassinervis
Zamites distans
Zamites dowellii
Zamites lanceolatus
Zamites manoniae
Zamites montana
Zamites montanensis
Zamites nicolae
Zamites occidentalis
Zamites powelli
Zamites tatianae
Zamites tenuinervis
Zamites tenuistriatus
Zamites truncatus
Zamites vogesiacus
Zamites wendyellisae
Zanardinia J.G.Agardh, 1876
Zanardinula andersoniana
Zanardinula De Toni, 1936
Zanardinula mexicana
Zandera andersoniae
Zandera blakei
Zandera hartmanii
Zanderella purpurea
Zanderia octoblepharis
Zanha africana
Zanha golungensis
Zanha Hiern
Zanha suaveolens
Zanichellia Roth, 1793
Zannichellia aschersoniana
Zannichellia contorta
Zannichellia obtusifolia
Zannichellia P.Micheli ex L.
Zannichellia palustris
Zannichellia pedicellata
Zannichellia peltata
Zannichellia polycarpa
Zanonia indica
Zanonia L.
Zantedeschia aethiopica
Zantedeschia albomaculata
Zantedeschia elliottiana
Zantedeschia jucunda
Zantedeschia odorata
Zantedeschia pentlandii
Zantedeschia rehmannii
Zantedeschia Spreng.
Zantedeschia valida
Zantenia borneensis
Zantenia denticulata
Zantenia karstenii
Zantenia prionophylla
Zanthorhiza L'Hér.
Zanthorhiza simplicissima
Zanthoxilon Franch. & Sav.
Zanthoxylaceae
Zanthoxylon Walter
Zanthoxylum acanthopodium
Zanthoxylum aculeatissimum
Zanthoxylum acuminatum
Zanthoxylum ailanthoides
Zanthoxylum alatum
Zanthoxylum albiflorum
Zanthoxylum albuquerquei
Zanthoxylum amamiense
Zanthoxylum amapaense
Zanthoxylum americanum
Zanthoxylum amplicalyx
Zanthoxylum anadenium
Zanthoxylum andinum
Zanthoxylum anison
Zanthoxylum anthyllidifolium
Zanthoxylum apiculatum
Zanthoxylum arborescens
Zanthoxylum armatum
Zanthoxylum asiaticum
Zanthoxylum atchoum
Zanthoxylum australe
Zanthoxylum austrosinense
Zanthoxylum avicennae
Zanthoxylum backeri
Zanthoxylum beecheyanum
Zanthoxylum bifoliolatum
Zanthoxylum bissei
Zanthoxylum bonifaziae
Zanthoxylum bonifazieae
Zanthoxylum bouetense
Zanthoxylum brachyacanthum
Zanthoxylum brisasanum
Zanthoxylum brisoferox
Zanthoxylum budrunga
Zanthoxylum bungeanum
Zanthoxylum burkillianum
Zanthoxylum calcicola
Zanthoxylum campicola
Zanthoxylum canalense
Zanthoxylum capense
Zanthoxylum caribaeum
Zanthoxylum caudatum
Zanthoxylum chalybaeum
Zanthoxylum chevalieri
Zanthoxylum chocoense
Zanthoxylum chuquisaquense
Zanthoxylum ciliatum
Zanthoxylum claessensii
Zanthoxylum clava-herculis
Zanthoxylum coco
Zanthoxylum collinsae
Zanthoxylum collinsiae
Zanthoxylum comosum
Zanthoxylum compactum
Zanthoxylum complexum
Zanthoxylum conspersipunctatum
Zanthoxylum cucullatipetalum
Zanthoxylum davyi
Zanthoxylum decaryi
Zanthoxylum delagoense
Zanthoxylum deremense
Zanthoxylum dimorphophyllum
Zanthoxylum dinklagei
Zanthoxylum dipetalum
Zanthoxylum dissitum
Zanthoxylum diversifolium
Zanthoxylum djalma-batistae
Zanthoxylum dumosum
Zanthoxylum echinocarpum
Zanthoxylum eichleri
Zanthoxylum ekmanii
Zanthoxylum elegantissimum
Zanthoxylum eliasii
Zanthoxylum esquirolii
Zanthoxylum externum
Zanthoxylum fagara
Zanthoxylum falcifolia
Zanthoxylum fauriei
Zanthoxylum finlaysonianum
Zanthoxylum flavum
Zanthoxylum foliolosum
Zanthoxylum forbesii
Zanthoxylum formiciferum
Zanthoxylum gardneri
Zanthoxylum gentryi
Zanthoxylum ghiesbreghtii
Zanthoxylum gillespieanum
Zanthoxylum gilletii
Zanthoxylum glomeratum
Zanthoxylum grandifolium
Zanthoxylum haitiense
Zanthoxylum harrisii
Zanthoxylum hawaiiense
Zanthoxylum heitzii
Zanthoxylum heterophyllum
Zanthoxylum holtzianum
Zanthoxylum huberi
Zanthoxylum humile
Zanthoxylum impressinervium
Zanthoxylum insulare
Zanthoxylum integrifoliolum
Zanthoxylum integrifolium
Zanthoxylum iwahigense
Zanthoxylum kallunkiae
Zanthoxylum kauaense
Zanthoxylum khasianum
Zanthoxylum kleinii
Zanthoxylum kwangsiensis
Zanthoxylum L.
Zanthoxylum laetum
Zanthoxylum laurentii
Zanthoxylum leiboicum
Zanthoxylum lemairei
Zanthoxylum lenticellosum
Zanthoxylum lepidopteriphilum
Zanthoxylum leprieurii
Zanthoxylum leratii
Zanthoxylum limoncello
Zanthoxylum limonifolium
Zanthoxylum lindense
Zanthoxylum macranthum
Zanthoxylum madagascariense
Zanthoxylum magnifasciculatum
Zanthoxylum magnifructum
Zanthoxylum mananarense
Zanthoxylum mantaro
Zanthoxylum maranionense
Zanthoxylum marionense
Zanthoxylum martinicense
Zanthoxylum mauriifolium
Zanthoxylum megistophyllum
Zanthoxylum melanostictum
Zanthoxylum mezoneurispinosum
Zanthoxylum micranthum
Zanthoxylum mildbraedii
Zanthoxylum molle
Zanthoxylum mollissimum
Zanthoxylum monogynum
Zanthoxylum motuoense
Zanthoxylum multijugum
Zanthoxylum myriacanthum
Zanthoxylum myrianthum
Zanthoxylum nadeaudii
Zanthoxylum nashii
Zanthoxylum nebuletorum
Zanthoxylum nemorale
Zanthoxylum neocaledonicum
Zanthoxylum nigrum
Zanthoxylum nitidum
Zanthoxylum novoguineense
Zanthoxylum oahuense
Zanthoxylum obtusifolium
Zanthoxylum oreophilum
Zanthoxylum ovalifolium
Zanthoxylum ovatifoliolatum
Zanthoxylum oxyphyllum
Zanthoxylum panamense
Zanthoxylum pancheri
Zanthoxylum paniculatum
Zanthoxylum paracanthum
Zanthoxylum parvifoliolum
Zanthoxylum parvum
Zanthoxylum paulae
Zanthoxylum pentandrum
Zanthoxylum petenense
Zanthoxylum petiolare
Zanthoxylum phyllopterum
Zanthoxylum pilosiusculum
Zanthoxylum pilosulum
Zanthoxylum pimpinelloides
Zanthoxylum pinnatum
Zanthoxylum piperitum
Zanthoxylum pluviatile
Zanthoxylum pluvimontanum
Zanthoxylum poggei
Zanthoxylum psammophilum
Zanthoxylum pteracanthum
Zanthoxylum pucro
Zanthoxylum punctatum
Zanthoxylum quassiifolium
Zanthoxylum quinduense
Zanthoxylum renieri
Zanthoxylum retroflexum
Zanthoxylum retusum
Zanthoxylum rhetsa
Zanthoxylum rhodoxylon
Zanthoxylum rhoifolium
Zanthoxylum rhombifoliolatum
Zanthoxylum riedelianum
Zanthoxylum rigidum
Zanthoxylum rubescens
Zanthoxylum rufescens
Zanthoxylum sambucirhachis
Zanthoxylum sapindoides
Zanthoxylum sarasinii
Zanthoxylum scandens
Zanthoxylum schinifolium
Zanthoxylum schlechteri
Zanthoxylum schreberi
Zanthoxylum setulosum
Zanthoxylum simplicifolium
Zanthoxylum simulans
Zanthoxylum spinosum
Zanthoxylum sprucei
Zanthoxylum stelligerum
Zanthoxylum stenophyllum
Zanthoxylum stipitatum
Zanthoxylum subspicatum
Zanthoxylum syncarpum
Zanthoxylum taediosum
Zanthoxylum tahitense
Zanthoxylum tenuipedicellatum
Zanthoxylum tetraphyllum
Zanthoxylum tetraspermum
Zanthoxylum thomense
Zanthoxylum thorncroftii
Zanthoxylum thouvenotii
Zanthoxylum tidorense
Zanthoxylum tingoassuiba
Zanthoxylum tomentellum
Zanthoxylum tragodes
Zanthoxylum trijugum
Zanthoxylum tsihanimposa
Zanthoxylum undulatifolium
Zanthoxylum unifoliolatum
Zanthoxylum usambarense
Zanthoxylum usitatum
Zanthoxylum verrucosum
Zanthoxylum viride
Zanthoxylum vitiense
Zanthoxylum wutaiense
Zanthoxylum xichouense
Zanthoxylum yakumontanum
Zanthoxylum yuanjiangense
Zanthoxylum zanthoxyloides
Zantorrhiza Steud.
Zapania Lam.
Zapoteca aculeata
Zapoteca alinae
Zapoteca amazonica
Zapoteca andina
Zapoteca balsasensis
Zapoteca caracasana
Zapoteca costaricensis
Zapoteca filipes
Zapoteca formosa
Zapoteca gracilis
Zapoteca H.M.Hern.
Zapoteca lambertiana
Zapoteca media
Zapoteca microcephala
Zapoteca mollis
Zapoteca nervosa
Zapoteca portoricensis
Zapoteca ravenii
Zapoteca scutellifera
Zapoteca sousae
Zapoteca tehuana
Zapoteca tetragona
Zappania Zuccagni, 1806
Zaqiqah mucronata
Zataria multiflora
Zauschneria C.Presl
Zauschneria canescens
Zauschneria eastwoodiae
Zauschneria glandulosa
Zazintha Hall.
Zea diploperennis
Zea hybr
Zea L.
Zea luxurians
Zea mays
Zea mexicana
Zea nicaraguensis
Zea perennis
Zealandia Testo & A.R.Field
Zearamosus elleria
Zebrasporites W.Klaus, 1960
Zebrina Schnizl.
Zehnderia microgyna
Zehneria angolensis
Zehneria anomala
Zehneria backeri
Zehneria bodinieri
Zehneria boholensis
Zehneria brevirostris
Zehneria capillacea
Zehneria clemensiae
Zehneria cunninghamii
Zehneria elbertii
Zehneria emirnensis
Zehneria Endl.
Zehneria erythrobacca
Zehneria filipes
Zehneria gilletii
Zehneria grandibracteata
Zehneria guamensis
Zehneria hallii
Zehneria hermaphrodita
Zehneria idenburgensis
Zehneria immarginata
Zehneria japonica
Zehneria keayana
Zehneria lancifolia
Zehneria leucocarpa
Zehneria liukiuensis
Zehneria longepedunculata
Zehneria longiflora
Zehneria macrantha
Zehneria macrosepala
Zehneria madagascariensis
Zehneria marlothii
Zehneria maysorensis
Zehneria microsperma
Zehneria minutiflora
Zehneria monocarpa
Zehneria morobensis
Zehneria mucronata
Zehneria neocaledonica
Zehneria neorensis
Zehneria nesophila
Zehneria odorata
Zehneria oligosperma
Zehneria pallidinervia
Zehneria parvifolia
Zehneria pedicellata
Zehneria peneyana
Zehneria pentaphylla
Zehneria perrieri
Zehneria pisifera
Zehneria polycarpa
Zehneria racemosa
Zehneria repanda
Zehneria ridens
Zehneria rizalensis
Zehneria rutenbergiana
Zehneria scaberrima
Zehneria scabra
Zehneria somalensis
Zehneria sphaerosperma
Zehneria subcoriacea
Zehneria tahitensis
Zehneria tenuispica
Zehneria thwaitesii
Zehneria trichocarpa
Zehneria trullifolia
Zehneria tuberifera
Zehneria viridifolia
Zehneria wallichii
Zeia Lunell
Zeilleria delicatula
Zeites R.Caspary ex H.Conwentz, 1886
Zelenkoa onusta
Zelkova abelicea
Zelkova carpinifolia
Zelkova keaki
Zelkova schneideriana
Zelkova serrata
Zelkova sicula
Zelkova sinica
Zelkova ungeri
Zelkova verschaffeltii
Zellera G.Martens, 1866
Zellera tawallina
Zelometeorium allionii
Zelometeorium ambiguum
Zelometeorium Manuel
Zelometeorium patens
Zelometeorium patulum
Zelometeorium recurvifolium
Zeltnera abramsii
Zeltnera arizonica
Zeltnera beyrichii
Zeltnera calycosa
Zeltnera davyi
Zeltnera exaltata
Zeltnera G.Mans.
Zeltnera gentryi
Zeltnera glandulifera
Zeltnera madrensis
Zeltnera martinii
Zeltnera maryanniana
Zeltnera muhlenbergii
Zeltnera multicaulis
Zeltnera namatophila
Zeltnera namophila
Zeltnera nevadensis
Zeltnera nudicaulis
Zeltnera pusilla
Zeltnera quitensis
Zeltnera setacea
Zeltnera stricta
Zeltnera texensis
Zeltnera trichantha
Zeltnera venusta
Zeltnera wigginsii
Zemisia discolor
Zemisia thomasii
Zenia Chun
Zenia insignis
Zenkerella capparidacea
Zenkerella citrina
Zenkerella egregia
Zenkerella grotei
Zenkerella parviflora
Zenkerella perplexa
Zenkerella schliebenii
Zenkeria Arn.
Zenkeria elegans
Zenkeria obtusiflora
Zenkeria stapfii
Zenkeria Trin.
Zenkerodendron bipindense
Zenobia D.Don
Zenobia pulverulenta
Zeocriton Wolf
Zephybranthus castellanosii
Zephybranthus morrisii
Zephyra compacta
Zephyra elegans
Zephyranthes
Zephyranthes advena
Zephyranthes ajax
Zephyranthes alba
Zephyranthes albolilacina
Zephyranthes americana
Zephyranthes ananuca
Zephyranthes andalgalensis
Zephyranthes andersonii
Zephyranthes andina
Zephyranthes andinus
Zephyranthes araguaiensis
Zephyranthes araucana
Zephyranthes arenicola
Zephyranthes atamasca
Zephyranthes atamasco
Zephyranthes aurea
Zephyranthes bagnoldii
Zephyranthes bahiensis
Zephyranthes bakeri
Zephyranthes barrosiana
Zephyranthes berteroana
Zephyranthes bifida
Zephyranthes blumenavia
Zephyranthes botumirimensis
Zephyranthes brachyandra
Zephyranthes brevipes
Zephyranthes briquetii
Zephyranthes caerulea
Zephyranthes candida
Zephyranthes capivarina
Zephyranthes cardinalis
Zephyranthes carinata
Zephyranthes carminea
Zephyranthes cearensis
Zephyranthes chacoensis
Zephyranthes chichimeca
Zephyranthes chlorosolen
Zephyranthes chrysantha
Zephyranthes ciceroana
Zephyranthes cisandina
Zephyranthes citrina
Zephyranthes clintiae
Zephyranthes coerulea
Zephyranthes colonum
Zephyranthes comunelloi
Zephyranthes concolor
Zephyranthes contermina
Zephyranthes conzattii
Zephyranthes correntina
Zephyranthes crassibulba
Zephyranthes crociflora
Zephyranthes cubensis
Zephyranthes depauperata
Zephyranthes diluta
Zephyranthes drummondii
Zephyranthes duarteana
Zephyranthes elegans
Zephyranthes elwesii
Zephyranthes erubescens
Zephyranthes estensis
Zephyranthes filifolia
Zephyranthes flaggii
Zephyranthes flavissima
Zephyranthes floryi
Zephyranthes fosteri
Zephyranthes gameleirensis
Zephyranthes gilliesiana
Zephyranthes goiana
Zephyranthes graciliflora
Zephyranthes gracilifolia
Zephyranthes gracilis
Zephyranthes gratissima
Zephyranthes guatemalensis
Zephyranthes Herb.
Zephyranthes hondurensis
Zephyranthes howardii
Zephyranthes hybr
Zephyranthes immaculata
Zephyranthes insularum
Zephyranthes irwiniana
Zephyranthes ischihualasta
Zephyranthes ita-andivi
Zephyranthes itaobina
Zephyranthes jamesonii
Zephyranthes jonesii
Zephyranthes jujuyensis
Zephyranthes katheriniae
Zephyranthes lactea
Zephyranthes laeta
Zephyranthes lagesiana
Zephyranthes lagopaivae
Zephyranthes latissimifolia
Zephyranthes leonensis
Zephyranthes leptandra
Zephyranthes leucantha
Zephyranthes lineata
Zephyranthes longifolia
Zephyranthes longipes
Zephyranthes longistyla
Zephyranthes longituba
Zephyranthes lucida
Zephyranthes lutrae
Zephyranthes macrosiphon
Zephyranthes maculata
Zephyranthes magnoi
Zephyranthes martinezii
Zephyranthes medinae
Zephyranthes mendocensis
Zephyranthes mesochloa
Zephyranthes mexicana
Zephyranthes microcarpa
Zephyranthes microstigma
Zephyranthes millarensis
Zephyranthes minima
Zephyranthes minor
Zephyranthes minuta
Zephyranthes miradorensis
Zephyranthes moctezumae
Zephyranthes moelleri
Zephyranthes monantha
Zephyranthes montana
Zephyranthes morrisclintii
Zephyranthes nelsonii
Zephyranthes nervosa
Zephyranthes neumannii
Zephyranthes nymphaea
Zephyranthes oranensis
Zephyranthes orellanae
Zephyranthes pantanalensis
Zephyranthes paranaensis
Zephyranthes parvula
Zephyranthes pedunculosa
Zephyranthes philadelphica
Zephyranthes phycelloides
Zephyranthes picta
Zephyranthes plumieri
Zephyranthes popetana
Zephyranthes primulina
Zephyranthes proctorii
Zephyranthes pseudoconcolor
Zephyranthes puertoricensis
Zephyranthes pulchella
Zephyranthes purpurea
Zephyranthes refugiensis
Zephyranthes reginae
Zephyranthes riojana
Zephyranthes robusta
Zephyranthes rosea
Zephyranthes rubra
Zephyranthes ruizlealii
Zephyranthes ruthiae
Zephyranthes sanavirone
Zephyranthes sarae
Zephyranthes schulziana
Zephyranthes sessilis
Zephyranthes simpsonii
Zephyranthes smallii
Zephyranthes solisii
Zephyranthes spectabilis
Zephyranthes splendens
Zephyranthes spofforthiana
Zephyranthes sprekeliopsis
Zephyranthes stellaris
Zephyranthes stellatorosea
Zephyranthes steyermarkii
Zephyranthes subflava
Zephyranthes susatana
Zephyranthes sylvatica
Zephyranthes tenuiflora
Zephyranthes tepicensis
Zephyranthes texana
Zephyranthes traubii
Zephyranthes treatiae
Zephyranthes tubispatha
Zephyranthes uruguaianica
Zephyranthes versicolor
Zephyranthes vittata
Zephyranthes zapotecana
Zeravschania aucheri
Zeravschania ferulifolia
Zeravschania kopetdaghensis
Zeravschania latifolia
Zeravschania membranacea
Zeravschania minjanensis
Zeravschania pastinacifolia
Zeravschania pauciradiata
Zeravschania regeliana
Zeravschania scabrifolia
Zeravschania sola
Zeravschania stricticaulis
Zerdana anchonioides
Zerdana Boiss.
Zergabriella B.Granier, 1989
Zerna
Zeugandra iranica
Zeugandra iranshahrii
Zeugites americanus
Zeugites capillaris
Zeugites guanchezii
Zeugites hackelii
Zeugites latifolius
Zeugites munroanus
Zeugites P.Browne
Zeugites pittieri
Zeugites sagittatus
Zeugites smilacifolius
Zeugophyllites elongatus
Zeuktophyllum calycinum
Zeuktophyllum suppositum
Zeuxanthe Ridl.
Zeuxine affinis
Zeuxine africana
Zeuxine agyokuana
Zeuxine amboinensis
Zeuxine baliensis
Zeuxine bifalcifera
Zeuxine blatteri
Zeuxine boninensis
Zeuxine bougainvilleana
Zeuxine cambodiana
Zeuxine clandestina
Zeuxine cordata
Zeuxine diversifolia
Zeuxine elatior
Zeuxine elmeri
Zeuxine elongata
Zeuxine erimae
Zeuxine exilis
Zeuxine flava
Zeuxine gengmanensis
Zeuxine gilgiana
Zeuxine glandulosa
Zeuxine goodyeroides
Zeuxine gracilis
Zeuxine hahensis
Zeuxine integrilabella
Zeuxine kantokeiensis
Zeuxine kutaiensis
Zeuxine lancifolia
Zeuxine lindleyana
Zeuxine longilabris
Zeuxine lunulata
Zeuxine mamiefoglianiae
Zeuxine marivelensis
Zeuxine membranacea
Zeuxine mindanaensis
Zeuxine nervosa
Zeuxine oblonga
Zeuxine odorata
Zeuxine ovata
Zeuxine palawensis
Zeuxine papillosa
Zeuxine parvifolia
Zeuxine petakensis
Zeuxine philippinensis
Zeuxine plantaginea
Zeuxine pseudogracilis
Zeuxine purpurascens
Zeuxine regia
Zeuxine reginasilvae
Zeuxine rolfeana
Zeuxine rupestris
Zeuxine samoensis
Zeuxine stammleri
Zeuxine stenophylla
Zeuxine strateumatica
Zeuxine subquadrata
Zeuxine tenuifolia
Zeuxine tjiampeana
Zeuxine tonkinensis
Zeuxine triangula
Zeuxine vietnamica
Zeuxine violascens
Zeuxine viridiflora
Zeuxine weberi
Zeuxine wenzelii
Zexmenia aurea
Zexmenia brachylepis
Zexmenia buphtalmiflora
Zexmenia caracasana
Zexmenia fasciculata
Zexmenia foliosa
Zexmenia goyazensis
Zexmenia helianthoides
Zexmenia La Llave
Zexmenia oyedaeoides
Zexmenia perymenioides
Zexmenia serrata
Zexmenia stenantha
Zexmenia virgulta
Zeydora J.de Loureiro ex B.A.Gomes, 1868
Zeyhera DC.
Zeyherella (Engl.) Pierre ex Aubrév. & Pellegr.
Zeyheria Mart.
Zeyheria montana
Zeyheria tuberculosa
Zeylanidium barberi
Zeylanidium crustaceum
Zeylanidium lichenoides
Zeylanidium manasiae
Zeylanidium olivaceum
Zeylanidium sessile
Zeylanidium subulatum
Zhengyia shennongensis
Zhukowskia Szlach., R.González & Rutk.
Zichia Steud., 1841
Zichya Hügel
Zichya molly
Zieria abscondita
Zieria adenodonta
Zieria alata
Zieria arborescens
Zieria aspalathoides
Zieria bifida
Zieria boolbunda
Zieria buxijugum
Zieria caducibracteata
Zieria chevalieri
Zieria collina
Zieria compacta
Zieria covenyi
Zieria distans
Zieria eungellaensis
Zieria euthadenia
Zieria exsul
Zieria floydii
Zieria fordii
Zieria formosa
Zieria fraseri
Zieria furfuracea
Zieria graniticola
Zieria granulata
Zieria gymnocarpa
Zieria hindii
Zieria inexpectata
Zieria ingramii
Zieria insularis
Zieria involucrata
Zieria laevigata
Zieria lasiocaulis
Zieria laxiflora
Zieria littoralis
Zieria madida
Zieria minutiflora
Zieria minutiflora x Zieria smithii
Zieria montana
Zieria murphyi
Zieria nubicola
Zieria obcordata
Zieria obovata
Zieria octandra
Zieria odorifera
Zieria oreocena
Zieria pilosa
Zieria prostrata
Zieria rimulosa
Zieria robertsiorum
Zieria robusta
Zieria scopulus
Zieria Sm.
Zieria smithii
Zieria southwellii
Zieria spec.
Zieria tenuis
Zieria tuberculata
Zieria vagans
Zieria veronicea
Zieria wilhelminae
Zietenia Gled.
Zigadenus glaberrimus
Zigadenus glaucus
Zigadenus Michx.
Zilla macroptera
Zilla spinosa
Zimmermannia Pax
Zimmermannioxylon multangulare
Zingela pooleyorum
Zingeria P.A.Smirn.
Zingiber
Zingiber acuminatum
Zingiber aguingayae
Zingiber albiflorum
Zingiber album
Zingiber anamalayanum
Zingiber apoense
Zingiber arunachalensis
Zingiber atroporphyreum
Zingiber atrorubens
Zingiber aurantiacum
Zingiber banhaoense
Zingiber barbatum
Zingiber brachystachys
Zingiber bradleyanum
Zingiber brevifolium
Zingiber bulusanense
Zingiber calcicola
Zingiber callianthum
Zingiber campanulatum
Zingiber capitatum
Zingiber cardiocheilum
Zingiber cernuum
Zingiber chengii
Zingiber chlorobracteatum
Zingiber chrysostachys
Zingiber citriodorum
Zingiber clarkei
Zingiber cochleariforme
Zingiber coloratum
Zingiber confine
Zingiber cornigerum
Zingiber cornubracteatum
Zingiber cylindricum
Zingiber densissimum
Zingiber discolor
Zingiber eberhardtii
Zingiber eborinum
Zingiber elatius
Zingiber elatum
Zingiber ellipticum
Zingiber engganoense
Zingiber fallax
Zingiber flagelliforme
Zingiber flammeum
Zingiber flavofusiforme
Zingiber flavomaculosum
Zingiber flavovirens
Zingiber fragile
Zingiber fraseri
Zingiber gracile
Zingiber gramineum
Zingiber griffithii
Zingiber guangxiense
Zingiber idae
Zingiber incomptum
Zingiber integrilabrum
Zingiber integrum
Zingiber intermedium
Zingiber isanense
Zingiber jiewhoei
Zingiber junceum
Zingiber kawagoii
Zingiber kelabitianum
Zingiber kerrii
Zingiber kunstleri
Zingiber lambii
Zingiber laoticum
Zingiber larsenii
Zingiber leptostachyum
Zingiber ligulatum
Zingiber lingyunense
Zingiber longibracteatum
Zingiber longiligulatum
Zingiber longipedunculatum
Zingiber macradenium
Zingiber macrocephalum
Zingiber macroglossum
Zingiber macrorrhynchus
Zingiber malaysianum
Zingiber marginatum
Zingiber martini
Zingiber mekongense
Zingiber Mill.
Zingiber mioga
Zingiber mizoramense
Zingiber molle
Zingiber monglaense
Zingiber montanum
Zingiber multibracteatum
Zingiber nanlingense
Zingiber neesanum
Zingiber neglectum
Zingiber neotruncatum
Zingiber nimmonii
Zingiber niveum
Zingiber odoriferum
Zingiber officinale
Zingiber oligophyllum
Zingiber olivaceum
Zingiber pachysiphon
Zingiber panduratum
Zingiber papuanum
Zingiber pellitum
Zingiber pendulum
Zingiber petiolatum
Zingiber phillippsiae
Zingiber pleiostachyum
Zingiber plicatum
Zingiber pseudopungens
Zingiber pseudosquarrosum
Zingiber puberulum
Zingiber purpureum
Zingiber pyroglossum
Zingiber raja
Zingiber recurvatum
Zingiber reflexum
Zingiber roseum
Zingiber rubens
Zingiber sadakornii
Zingiber shuanglongense
Zingiber shuanglongensis
Zingiber simaoense
Zingiber singapurense
Zingiber smilesianum
Zingiber spectabile
Zingiber squarrosum
Zingiber stenostachys
Zingiber striolatum
Zingiber sulphureum
Zingiber tenuifolium
Zingiber tenuiscapus
Zingiber thorelii
Zingiber ultralimitale
Zingiber velutinum
Zingiber vinosum
Zingiber viridiflavum
Zingiber wandingense
Zingiber wightianum
Zingiber wrayi
Zingiber yersinii
Zingiber yingjiangense
Zingiber zerumbet
Zingiber zerumbetmagnum
Zingiberaceae
Zingiberales
Zingiberites dubius
Zingiberites Heer, 1859
Zingiberopsis isonervosa
Zingiberopsis L.J.Hickey, 1977
Zinnia acerosa
Zinnia ambigua
Zinnia americana
Zinnia angustifolia
Zinnia anomala
Zinnia barrancae
Zinnia bicolor
Zinnia citrea
Zinnia darwinii
Zinnia discolor
Zinnia elegans
Zinnia flavicoma
Zinnia ghiesbreghtii
Zinnia grandiflora
Zinnia guanajuatensis
Zinnia haageana
Zinnia haageniana
Zinnia haegeana
Zinnia juniperifolia
Zinnia L.
Zinnia leucoglossa
Zinnia liebmannii
Zinnia maritima
Zinnia marylandica
Zinnia microglossa
Zinnia oligantha
Zinnia pauciflora
Zinnia peruviana
Zinnia purpusii
Zinnia tenella
Zinnia tenuis
Zinnia venusta
Zinnia zamudiana
Zinnia zinnioides
Zinovaea acanthocarpa
Zinovaea M.J.Wynne, 1970
Zinowiewia australis
Zinowiewia aymardii
Zinowiewia integerrima
Zinowiewia intergerrima
Zinowiewia madsenii
Zinowiewia pallida
Zinowiewia pauciflora
Zinowiewia rubra
Zinowiewia sulphurea
Zinowiewia Turcz.
Zippelia begoniifolia
Zippelia Blume
Zippelia engeli
Zittelina E.Munier-Chalmas ex L.Morellet & J.Morellet, 1913
Zittelina elegans
Zizania aquatica
Zizania latifolia
Zizania palustris
Zizaniopsis bonariensis
Zizaniopsis Döll & Asch.
Zizaniopsis killipii
Zizaniopsis longhi-wagnerae
Zizaniopsis microstachya
Zizaniopsis miliacea
Zizaniopsis villanensis
Zizia aptera
Zizia aurea
Zizia trifoliata
Zizia W.D.J.Koch
Ziziphora acinoides
Ziziphora aragonensis
Ziziphora brantii
Ziziphora capitata
Ziziphora clinopodioides
Ziziphora hispanica
Ziziphora intermedia
Ziziphora interrupta
Ziziphora L.
Ziziphora pamiroalaica
Ziziphora pedicellata
Ziziphora persica
Ziziphora puschkinii
Ziziphora raddei
Ziziphora subnivalis
Ziziphora taurica
Ziziphora tenuior
Ziziphora vichodceviana
Ziziphus abyssinica
Ziziphus affinis
Ziziphus angustifolia
Ziziphus apetala
Ziziphus attopensis
Ziziphus baenchia
Ziziphus borneensis
Ziziphus brunoniana
Ziziphus calophylla
Ziziphus cambodiana
Ziziphus crebrivenosa
Ziziphus cumingiana
Ziziphus dalanta
Ziziphus djamuensis
Ziziphus djsmuensis
Ziziphus elegans
Ziziphus fungii
Ziziphus funiculosa
Ziziphus glabrata
Ziziphus guaranitica
Ziziphus hajarensis
Ziziphus hamur
Ziziphus havilandii
Ziziphus heguertii
Ziziphus hoaensis
Ziziphus horrida
Ziziphus horsfieldii
Ziziphus hutchinsonii
Ziziphus hysudricus
Ziziphus incurva
Ziziphus javanensis
Ziziphus jujuba
Ziziphus kunstleri
Ziziphus laui
Ziziphus leucodermis
Ziziphus linnaei
Ziziphus lotus
Ziziphus mairei
Ziziphus mauritiana
Ziziphus Mill.
Ziziphus montana
Ziziphus mucronata
Ziziphus napeca
Ziziphus nummularia
Ziziphus oenoplia
Ziziphus oenopolia
Ziziphus oligantha
Ziziphus otanesii
Ziziphus oxyphylla
Ziziphus papuana
Ziziphus parvifolia
Ziziphus pernettyoides
Ziziphus poilanei
Ziziphus pubescens
Ziziphus pubinervis
Ziziphus quadrilocularis
Ziziphus rivularis
Ziziphus robertsoniana
Ziziphus rubiginosa
Ziziphus rugosa
Ziziphus spina-christi
Ziziphus subquinquenervia
Ziziphus suluensis
Ziziphus talanae
Ziziphus timoriensis
Ziziphus trinervis
Ziziphus truncata
Ziziphus wynadensis
Ziziphus xylopyrus
Ziziphus zeyheriana
Zizkaea tuerckheimii
Zizyphoides ezoensis
Zizyphoides flabella
Zizyphoides Seward & Conway, 1935
Zizyphus Adans., 1763
Zizyphus beckwithii
Zizyphus dakotensis
Zizyphus elegans
Zizyphus falcatus
Zizyphus lamarensis
Zizyphus laurifolius
Zizyphus lesquereuxii
Zizyphus lewisiana
Zizyphus longifolia
Zizyphus meekii
Zizyphus Miller, 1758
Zizyphus miocenicus
Zizyphus obtusa
Zizyphus paliurifolius
Zizyphus piperoides
Zizyphus townsendi
Zlivisporis blanensis
Zlivisporis Pacltová
Zoegea crinita
Zoegea L.
Zoegea leptaurea
Zoegea purpurea
Zoisia J.M.Black, 1943
Zollernia cowanii
Zollernia glabra
Zollernia glaziovii
Zollernia grandifolia
Zollernia ilicifolia
Zollernia kanukuensis
Zollernia magnifica
Zollernia modesta
Zollernia paraensis
Zollernia surinamensis
Zollernia Wied-Neuw. & Nees
Zollikoferia DC.
Zollingeria dongnaiensis
Zollingeria Kurz
Zollingeria laotica
Zombia antillarum
Zomicarpa pythonium
Zomicarpa Schott
Zomicarpa steigeriana
Zomicarpella amazonica
Zomicarpella maculata
Zomicarpella N.E.Br.
Zonallapollenites segmentatus
Zonallapollenites trilobatus
Zonaria Steud., 1840
Zonariophila Stegenga & Kemperman, 1996
Zonopteris goepperti
Zonotriche (C.E.Hubb.) J.B.Phipps
Zonotriche brunnea
Zonotriche decora
Zonotriche inamoena
Zoochlorella K.Brandt, 1881
Zoopsidella antillana
Zoopsidella caledonica
Zoopsidella cynosurandra
Zoopsidella integrifolia
Zoopsidella serra
Zoopsis (Hook.f. & Taylor) Gottsche, Lindenb. & Nees
Zoopsis argentea
Zoopsis bicruris
Zoopsis ceratophylla
Zoopsis leitgebiana
Zoopsis liukiuensis
Zoopsis macrophylla
Zoopsis nitida
Zoopsis setigera
Zoopsis setulosa
Zootrophion aguirrei
Zootrophion alvaroi
Zootrophion argus
Zootrophion atropurpureum
Zootrophion beloglottis
Zootrophion dayanum
Zootrophion dodsonii
Zootrophion eburneum
Zootrophion endresianum
Zootrophion erlangense
Zootrophion fenestratum
Zootrophion gracilentum
Zootrophion griffin
Zootrophion hirtzii
Zootrophion hypodiscus
Zootrophion ildephonsi
Zootrophion lappaceum
Zootrophion machaqway
Zootrophion muliebre
Zootrophion niveum
Zootrophion oblongifolium
Zootrophion serpentinum
Zootrophion vasquezii
Zootrophion vulturiceps
Zootrophion williamsii
Zornia acuta
Zornia afranoi
Zornia albiflora
Zornia albolutescens
Zornia angustifolia
Zornia areolata
Zornia B.Senowbari-Daryan & P.Di Stefano, 2001
Zornia bracteata
Zornia brasiliensis
Zornia brevipes
Zornia burkartii
Zornia capensis
Zornia cearensis
Zornia chaetophora
Zornia confusa
Zornia contorta
Zornia cryptantha
Zornia curvata
Zornia Darwin
Zornia decussata
Zornia dichotoma
Zornia diphylla
Zornia disticha
Zornia durumuensis
Zornia dyctiocarpa
Zornia echinocarpa
Zornia filifoliola
Zornia floribunda
Zornia gardneriana
Zornia gibbosa
Zornia glabra
Zornia glaziouvii
Zornia glaziovii
Zornia glochidiata
Zornia grandiflora
Zornia guanipensis
Zornia harmsiana
Zornia hebecarpa
Zornia herbacea
Zornia intecta
Zornia J.F.Gmel.
Zornia laevis
Zornia lasiocarpa
Zornia latifolia
Zornia leptophylla
Zornia linearis
Zornia macdonaldii
Zornia maritima
Zornia megistocarpa
Zornia microphylla
Zornia milneana
Zornia mitziana
Zornia muelleriana
Zornia multinervosa
Zornia muriculata
Zornia myriadena
Zornia oligantha
Zornia orbiculata
Zornia pallida
Zornia papuensis
Zornia pardina
Zornia piurensis
Zornia pratensis
Zornia prostrata
Zornia puberula
Zornia punctatissima
Zornia quilonensis
Zornia ramboiana
Zornia ramosa
Zornia reptans
Zornia reticulata
Zornia sericea
Zornia setosa
Zornia sinaloensis
Zornia stirlingii
Zornia subsessilis
Zornia tenuifolia
Zornia thymifolia
Zornia trachycarpa
Zornia ulei
Zornia vaughaniana
Zornia venosa
Zornia vichadana
Zornia villosa
Zornia virgata
Zornia walkeri
Zornia zollingeri
Zosima absinthiifolia
Zosima gilliana
Zosima Hoffm.
Zosima korovinii
Zosima radians
Zostera angustifolia
Zostera asiatica
Zostera caespitosa
Zostera capensis
Zostera capricorni
Zostera caulescens
Zostera japonica
Zostera kiewiensis
Zostera L.
Zostera marina
Zostera muelleri
Zostera nigricaulis
Zostera noltii
Zostera novazelandica
Zostera polychlamys
Zostera tasmanica
Zosteraceae
Zosterites A.T.Brongniart, 1823
Zosterophyllanthos Szlach. & Marg.
Zosterophyllum D.P.Penhallow, 1892
Zosterophyllum divaricatum
Zosterophyllum myretonianum
Zosterophyllum undefined
Zotovia acicularis
Zotovia colensoi
Zotovia thomsonii
Zoutpansbergia Hutch.
Zoysia hondana
Zoysia japonica
Zoysia macrantha
Zoysia macrostachya
Zoysia matrella
Zoysia minima
Zoysia pauciflora
Zoysia seslerioides
Zoysia sinica
Zoysia Willd.
Zozimia DC., 1830
Zuberia barrealensis
Zuberia feistmanteli
Zuberia sahnii
Zuccagnia Cav.
Zuccarelloa ceramoides
Zuccarinia Blume
Zuccarinia macrophylla
Zuccarinia Spreng., 1827
Zuckertia Baill.
Zuckertia cordata
Zuckertia manuelii
Zuckia Standl.
Zuelania A.Rich.
Zuloagaea Bess
Zuloagaea bulbosa
Zuloagocardamum jujuyensis
Zulustylis hygrophila
Zulustylis variegata
Zunilia Lundell
Zuvanda (Dvořák) Askerova
Zuvanda crenulata
Zuvanda exacoides
Zuvanda meyeri
Zwackhia Sendtn.
Zwingera Hofer
Zygadenus S.F.L.Endlicher, 1836
Zygia ampla
Zygia andaquiensis
Zygia bangii
Zygia basijuga
Zygia biflora
Zygia bifoliola
Zygia brenesii
Zygia cataractae
Zygia cauliflora
Zygia claviflora
Zygia coccinea
Zygia cognata
Zygia collina
Zygia confusa
Zygia conzattii
Zygia cupirensis
Zygia dinizii
Zygia discifera
Zygia dissitiflora
Zygia engelsingii
Zygia eperuetorum
Zygia hernandezii
Zygia heteroneura
Zygia inaequalis
Zygia juruana
Zygia lathetica
Zygia latifolia
Zygia lehmannii
Zygia longifolia
Zygia macbridei
Zygia megistocarpa
Zygia multipunctata
Zygia nubigena
Zygia obolingoides
Zygia ocumarensis
Zygia odoratissima
Zygia P.Browne
Zygia palmana
Zygia paucijugata
Zygia peckii
Zygia picramnioides
Zygia pithecolobioides
Zygia potaroensis
Zygia racemosa
Zygia rhytidocarpa
Zygia selloi
Zygia steyermarkii
Zygia tetragona
Zygia transamazonica
Zygia trunciflora
Zygia turneri
Zygia unifoliolata
Zygia vasquezii
Zygnema anomalum
Zygnema carinthiacum
Zygnema chalybeospermum
Zygnema chalybeosporum
Zygnema conspicuum
Zygnema cruciatum
Zygnema cyanosporum
Zygnema cylindricum
Zygnema decussatum
Zygnema excompressum
Zygnema javanicum
Zygnema leiospermum
Zygnema littoreum
Zygnema oveidanum
Zygnema parvulum
Zygnema pawneanum
Zygnema pectinatum
Zygnema peliosporum
Zygnema ralfsii
Zygnema rostratum
Zygnema stellinum
Zygnema sterile
Zygnema subcruciatum
Zygnema tenue
Zygnemataceae
Zygnematales
Zygnematophyceae
Zygnemopsis (H.Skuja) E.N.Transeau, 1934
Zygocactus K.Schum.
Zygocarpum caeruleum
Zygocarpum coeruleum
Zygocarpum gillettii
Zygocarpum rectangulare
Zygocarpum somalense
Zygocarpum yemenense
Zygocaste Hort., 1946
Zygochloa paradoxa
Zygochloa S.T.Blake
Zygocolax leopardinum
Zygodia Benth.
Zygodon acutifolius
Zygodon altarensis
Zygodon anomalus
Zygodon apiculatus
Zygodon barbuloides
Zygodon brevipes
Zygodon brevisetus
Zygodon campylophyllus
Zygodon catarinoi
Zygodon cernuus
Zygodon conoideus
Zygodon cylindricus
Zygodon dentatus
Zygodon dioicus
Zygodon ehrenbergii
Zygodon elatus
Zygodon erosus
Zygodon fasciculatus
Zygodon fragilifolius
Zygodon fragilis
Zygodon gracilis
Zygodon Hook. & Taylor
Zygodon hookeri
Zygodon insularum
Zygodon intermedius
Zygodon jaffuelii
Zygodon johnstonii
Zygodon laxifolius
Zygodon leptocarpus
Zygodon liebmannii
Zygodon longicellularis
Zygodon lukasii
Zygodon macrocarpus
Zygodon macrophyllus
Zygodon magellanicus
Zygodon microgemmaceus
Zygodon nivalis
Zygodon obovalis
Zygodon ochraceus
Zygodon oeneus
Zygodon orientalis
Zygodon perichaetialis
Zygodon perreflexus
Zygodon peruvianus
Zygodon petrophilus
Zygodon pichinchensis
Zygodon pilosulus
Zygodon podocarpi
Zygodon polyptychus
Zygodon quitensis
Zygodon reinwardtii
Zygodon robustus
Zygodon rubrigemmius
Zygodon rufescens
Zygodon runcinatus
Zygodon rupestris
Zygodon schenckii
Zygodon schimperi
Zygodon semitortus
Zygodon seriatus
Zygodon sibiricus
Zygodon sordidus
Zygodon squarrosus
Zygodon stenocarpus
Zygodon stirtonii
Zygodon strictus
Zygodon subrecurvifolius
Zygodon subsquarrosus
Zygodon tetragonostomus
Zygodon trichomitrius
Zygodon venezuelensis
Zygodon viridissimus
Zygodon wightii
Zygodon yuennanensis
Zygogonium ericetorum
Zygogonium Kützing, 1843
Zygogynum acsmithii
Zygogynum amplexicaule
Zygogynum archboldianum
Zygogynum argenteum
Zygogynum bicolor
Zygogynum bullatum
Zygogynum calophyllum
Zygogynum calothyrsum
Zygogynum clemensiae
Zygogynum comptonii
Zygogynum crassifolium
Zygogynum cruminatum
Zygogynum fraterculus
Zygogynum glaucum
Zygogynum gracile
Zygogynum haplopus
Zygogynum howeanum
Zygogynum ledermannii
Zygogynum longifolium
Zygogynum mackeei
Zygogynum megacarpum
Zygogynum montanum
Zygogynum oligocarpum
Zygogynum oligostigma
Zygogynum pachyanthum
Zygogynum pancheri
Zygogynum pauciflorum
Zygogynum polyneurum
Zygogynum pomiferum
Zygogynum queenslandianum
Zygogynum schlechteri
Zygogynum schramii
Zygogynum semecarpoides
Zygogynum sororium
Zygogynum staufferianum
Zygogynum stipitatum
Zygogynum sylvestre
Zygogynum tanyostigma
Zygogynum tieghemii
Zygogynum umbellatum
Zygogynum vinkii
Zygomitus reticulatus
Zygopabstia veitchii
Zygopetalum clayi
Zygopetalum crinitum
Zygopetalum ghillanyi
Zygopetalum graminifolium
Zygopetalum maculatum
Zygopetalum maxillare
Zygopetalum microphytum
Zygopetalum mosenianum
Zygopetalum pabstii
Zygopetalum reginae
Zygopetalum sedenii
Zygopetalum sellowii
Zygopetalum silvanum
Zygopetalum triste
Zygophlebia L.E.Bishop
Zygophyllaceae
Zygophyllales
Zygophyllidium Small
Zygophyllum atriplicoides
Zygophyllum betpakdalense
Zygophyllum borissovae
Zygophyllum brachypterum
Zygophyllum burcharicum
Zygophyllum carnosum
Zygophyllum cuspidatum
Zygophyllum dregeanum
Zygophyllum eichwaldii
Zygophyllum fabago
Zygophyllum fabagoides
Zygophyllum furcatum
Zygophyllum gobicum
Zygophyllum gontscharovii
Zygophyllum heterocladum
Zygophyllum jaxarticum
Zygophyllum kansuense
Zygophyllum karatavicum
Zygophyllum kaschgaricum
Zygophyllum kegense
Zygophyllum kopalense
Zygophyllum L.
Zygophyllum lehmannianum
Zygophyllum loczyi
Zygophyllum macracanthum
Zygophyllum macropodum
Zygophyllum maximiliani
Zygophyllum miniatum
Zygophyllum mucronatum
Zygophyllum neglectum
Zygophyllum obliquum
Zygophyllum ovigerum
Zygophyllum oxianum
Zygophyllum oxycarpum
Zygophyllum pinnatum
Zygophyllum potaninii
Zygophyllum pterocarpum
Zygophyllum ramosissimum
Zygophyllum rosowii
Zygophyllum sinkiangense
Zygophyllum sonderi
Zygophyllum stenopterum
Zygophyllum steropterum
Zygophyllum subtrijugum
Zygophyllum turcomanicum
Zygophyllum xanthoxylum
Zygopteridaceae
Zygopteris brongniarti
Zygopteris Corda, 1845
Zygoruellia richardii
Zygosepalum (Rchb.f.) Rchb.f.
Zygosepalum angustilabium
Zygosepalum ballii
Zygosepalum labiosum
Zygosepalum lindeniae
Zygosepalum marginatum
Zygosepalum revolutum
Zygosepalum tatei
Zygosicyos Humbert
Zygostates alleniana
Zygostates apiculata
Zygostates bradei
Zygostates castellensis
Zygostates chaparensis
Zygostates cornigera
Zygostates cornuta
Zygostates dasyrhiza
Zygostates grandiflora
Zygostates ligulata
Zygostates lunata
Zygostates nectarifera
Zygostates obliqua
Zygostates octavioreisii
Zygostates ovatipetala
Zygostates papillosa
Zygostates pellucida
Zygostates pustulata
Zygostates riefenstahliae
Zygostelma Benth.
Zygostigma australe
Zygostigma Griseb.
Zygotritonia atropurpurea
Zygotritonia bongensis
Zygotritonia nyassana
Zygotritonia praecox
Zygoxanthium Ehrenberg
Zymurgia chondriopsidea
Zymurgia J.A.Lewis & G.T.Kraft, 1992
Zyrphelis burchellii
Zyrphelis capensis
Zyrphelis Cass.
Zyrphelis ciliaris
Zyrphelis corymbosa
Zyrphelis crenata
Zyrphelis decumbens
Zyrphelis ecklonis
Zyrphelis foliosa
Zyrphelis fruticosa
Zyrphelis glabra
Zyrphelis hirsuta
Zyrphelis lasiocarpa
Zyrphelis leiocarpa
Zyrphelis levis
Zyrphelis microcephala
Zyrphelis montana
Zyrphelis nervosa
Zyrphelis pilosella
Zyrphelis spathulata
Zyrphelis taxifolia
Zyzygium Brongn., 1843
Zyzyura mayana
Zyzyxia Strother""".strip().split("\n")

# ══════════════════════════════════════════════
#  LISTE DES PLANTES TOXIQUES
#  ⚠ À REMPLACER à chaque nouvelle lettre
#  → Mettre ici uniquement les noms présents
#    dans PLANTES qui sont toxiques.
#    Le nom doit être identique (même casse).
#  → Si aucune plante toxique : laisser []
# ══════════════════════════════════════════════

PLANTES_TOXIQUES = """Zantedeschia aethiopica
Zantedeschia albomaculata
Zantedeschia elliottiana
Zantedeschia jucunda
Zantedeschia odorata
Zantedeschia pentlandii
Zantedeschia rehmannii
Zantedeschia Spreng.
Zantedeschia valida""".strip().split("\n")

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
      <a href="../../encyclopedie/Z.html">Espèces en « Z »</a>
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
