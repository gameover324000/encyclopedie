#!/usr/bin/env python3
"""
Herbarium — Générateur de pages HTML pour les plantes X
Génère une page HTML par plante avec le même template que les pages Y.
Utilise l'API GBIF pour récupérer famille et taxonomie.
"""

import re
import time
import json
import requests
from pathlib import Path

# ══════════════════════════════════════════════
#  CONFIGURATION
# ══════════════════════════════════════════════

DOSSIER_SORTIE  = "./X_Plante_page"
LETTRE          = "X"
LETTRE_HTML     = "X.html"
LOG_FILE        = "generation_log_pages_X.json"
HEADERS         = {"User-Agent": "Herbarium-Bot/1.0"}

# ══════════════════════════════════════════════
#  LISTE DES PLANTES
# ══════════════════════════════════════════════

PLANTES = """Xantheranthemum igneum
Xantheranthemum Lindau
Xanthidium
Xanthidium acanthophorum
Xanthidium aculeatum
Xanthidium antilopaeum
Xanthidium armatum
Xanthidium basidentatum
Xanthidium bifidum
Xanthidium brebissonii
Xanthidium concinnum
Xanthidium controversum
Xanthidium cristatum
Xanthidium Ehrenberg ex Ralfs, 1848
Xanthidium fasciculatum
Xanthidium forcipatum
Xanthidium fragile
Xanthidium hastiferum
Xanthidium impar
Xanthidium mamillosum
Xanthidium nordstedtii
Xanthidium pensylvanicum
Xanthidium polygonum
Xanthidium regulare
Xanthidium robinsonianum
Xanthidium smithii
Xanthidium subhastiferum
Xanthidium tenuissimum
Xanthidium tetracentrotum
Xanthidium trilobum
Xanthidium variabile
Xanthisma arenarium
Xanthisma blephariphyllum
Xanthisma coloradoense
Xanthisma crutchfieldii
Xanthisma DC.
Xanthisma gracile
Xanthisma gracilis
Xanthisma grindelioides
Xanthisma gymnocephalum
Xanthisma gypsophilum
Xanthisma johnstonii
Xanthisma junceum
Xanthisma paradoxum
Xanthisma pseudorestiforme
Xanthisma restiforme
Xanthisma rhizomatum
Xanthisma scabrellum
Xanthisma spinulosum
Xanthisma stenolobum
Xanthisma tenuilobum
Xanthisma texanum
Xanthisma viscidum
Xanthisma wigginsii
Xanthium almerae
Xanthium anatolicum
Xanthium annuum
Xanthium basilei
Xanthium bushii
Xanthium catalaunicum
Xanthium faurae
Xanthium humile
Xanthium L.
Xanthium microcarpum
Xanthium numidicum
Xanthium occidentale
Xanthium orientale
Xanthium orientale x Xanthium strumarium
Xanthium revelieri
Xanthium sallentii
Xanthium shullii
Xanthium spinosum
Xanthium strumarium
Xanthium vayredae
Xanthium widderi
Xanthocephalum benthamianum
Xanthocephalum centauroides
Xanthocephalum durangense
Xanthocephalum gymnospermoides
Xanthocephalum humile
Xanthocephalum Willd.
Xanthoceras sorbifolia
Xanthoceras sorbifolium
Xanthocercis Baill.
Xanthocercis rabiensis
Xanthocercis zambesiaca
Xanthochloa (Krivot.) Tzvelev, 2006
Xanthocyparis Farjon & T.H.Nguyên
Xanthocyparis nootkatensis
Xanthocyparis vietnamensis
Xanthogalum purpurascens
Xanthogalum sachokianum
Xanthogalum tatianae
Xanthomyrtus angustifolia
Xanthomyrtus arfakensis
Xanthomyrtus bryophila
Xanthomyrtus cardiophylla
Xanthomyrtus compacta
Xanthomyrtus Diels
Xanthomyrtus diplycosifolia
Xanthomyrtus flavida
Xanthomyrtus grandiflora
Xanthomyrtus hienghenensis
Xanthomyrtus humilis
Xanthomyrtus kanalaensis
Xanthomyrtus koebrensis
Xanthomyrtus lanceolata
Xanthomyrtus leeuwenii
Xanthomyrtus montis-sucklingii
Xanthomyrtus montivaga
Xanthomyrtus ovata
Xanthomyrtus papuana
Xanthomyrtus schlechteri
Xanthomyrtus scolopacina
Xanthomyrtus splendens
Xanthopappus subacaulis
Xanthophyllum adenotus
Xanthophyllum albicaulis
Xanthophyllum ancolanum
Xanthophyllum andamanicum
Xanthophyllum angustigemma
Xanthophyllum annamense
Xanthophyllum beccarianum
Xanthophyllum bicolor
Xanthophyllum borneense
Xanthophyllum bracteatum
Xanthophyllum brigittae
Xanthophyllum bullatum
Xanthophyllum burkillii
Xanthophyllum celebicum
Xanthophyllum ceraceifolium
Xanthophyllum chartaceum
Xanthophyllum clovis
Xanthophyllum cochinchinense
Xanthophyllum cockburnii
Xanthophyllum colubrinum
Xanthophyllum contractum
Xanthophyllum cucullatum
Xanthophyllum discolor
Xanthophyllum eberhardtii
Xanthophyllum ecarinatum
Xanthophyllum ellipticum
Xanthophyllum erythrostachyum
Xanthophyllum eurhynchum
Xanthophyllum ferrugineum
Xanthophyllum flavescens
Xanthophyllum fragrans
Xanthophyllum geesinkii
Xanthophyllum griffithii
Xanthophyllum havilandii
Xanthophyllum heterophyllum
Xanthophyllum hildebrandii
Xanthophyllum incertum
Xanthophyllum ionanthum
Xanthophyllum korthalsianum
Xanthophyllum laeve
Xanthophyllum lanceatum
Xanthophyllum lateriflorum
Xanthophyllum lineare
Xanthophyllum longum
Xanthophyllum macrophyllum
Xanthophyllum malayanum
Xanthophyllum montanum
Xanthophyllum monticola
Xanthophyllum neglectum
Xanthophyllum ngii
Xanthophyllum nigricans
Xanthophyllum novoguinense
Xanthophyllum obscurum
Xanthophyllum octandrum
Xanthophyllum oliganthum
Xanthophyllum ovatifolium
Xanthophyllum pachycarpon
Xanthophyllum palawanense
Xanthophyllum papuanum
Xanthophyllum parvifolium
Xanthophyllum pauciflorum
Xanthophyllum pedicellatum
Xanthophyllum petiolatum
Xanthophyllum philippinense
Xanthophyllum pomiferum
Xanthophyllum pseudoadenotus
Xanthophyllum pubescens
Xanthophyllum pulchrum
Xanthophyllum punctatum
Xanthophyllum ramiflorum
Xanthophyllum rectum
Xanthophyllum reflexum
Xanthophyllum resupinatum
Xanthophyllum retinerve
Xanthophyllum rheophilum
Xanthophyllum rufum
Xanthophyllum schixocarpon
Xanthophyllum schizocarpon
Xanthophyllum stipitatum
Xanthophyllum subcoriaceum
Xanthophyllum suberosum
Xanthophyllum sulphureum
Xanthophyllum sylvestre
Xanthophyllum tardicrescens
Xanthophyllum tenue
Xanthophyllum tenuipetalum
Xanthophyllum urophyllum
Xanthophyllum velutinum
Xanthophyllum virens
Xanthophyllum vitellinum
Xanthophyllum wrayi
Xanthophyllum yunnanense
Xanthophyllum zeylanicum
Xanthophytum alopecurum
Xanthophytum attopevense
Xanthophytum balansae
Xanthophytum borneense
Xanthophytum brookei
Xanthophytum calycinum
Xanthophytum chinense
Xanthophytum cylindricum
Xanthophytum ferrugineum
Xanthophytum foliaceum
Xanthophytum fruticulosum
Xanthophytum glabrum
Xanthophytum glomeratum
Xanthophytum grandifolium
Xanthophytum kinabaluense
Xanthophytum kwangtungense
Xanthophytum longipedunculatum
Xanthophytum magnisepalum
Xanthophytum minus
Xanthophytum nitens
Xanthophytum olivaceum
Xanthophytum papuanum
Xanthophytum polyanthum
Xanthophytum pubistylosum
Xanthophytum Reinw. ex Blume
Xanthophytum sessile
Xanthophytum setosum
Xanthorhiza simplicissima
Xanthorrhoea acanthostachya
Xanthorrhoea acaulis
Xanthorrhoea arenaria
Xanthorrhoea australis
Xanthorrhoea bracteata
Xanthorrhoea brevistyla
Xanthorrhoea brunonis
Xanthorrhoea caespitosa
Xanthorrhoea Cape-Bedford
Xanthorrhoea concava
Xanthorrhoea drummondii
Xanthorrhoea fulva
Xanthorrhoea glauca
Xanthorrhoea gracilis
Xanthorrhoea hastile
Xanthorrhoea johnsonii
Xanthorrhoea latifolia
Xanthorrhoea macronema
Xanthorrhoea malacophylla
Xanthorrhoea media
Xanthorrhoea minor
Xanthorrhoea nana
Xanthorrhoea platyphylla
Xanthorrhoea preissii
Xanthorrhoea pumilio
Xanthorrhoea quadrangulata
Xanthorrhoea resinosa
Xanthorrhoea semiplana
Xanthorrhoea thorntonii
Xanthorrhoeaceae
Xanthoselinum alsaticum
Xanthoselinum Schur
Xanthosia atkinsoniana
Xanthosia candida
Xanthosia dissecta
Xanthosia fruticulosa
Xanthosia hederifolia
Xanthosia huegelii
Xanthosia kochii
Xanthosia leiophylla
Xanthosia peduncularis
Xanthosia pilosa
Xanthosia rotundifolia
Xanthosia Rudge
Xanthosia scopulicola
Xanthosia singuliflora
Xanthosia stellata
Xanthosia tasmanica
Xanthosia ternifolia
Xanthosia tomentosa
Xanthosia tridentata
Xanthosoma
Xanthosoma acevedoi
Xanthosoma acutilobum
Xanthosoma acutum
Xanthosoma akkermansii
Xanthosoma alversonii
Xanthosoma amacayacuense
Xanthosoma anderssonii
Xanthosoma anisotomum
Xanthosoma aristeguietae
Xanthosoma asplundii
Xanthosoma auriculatum
Xanthosoma australe
Xanthosoma baguense
Xanthosoma bakhuisense
Xanthosoma barbacoasense
Xanthosoma barbourii
Xanthosoma barinasense
Xanthosoma belophyllum
Xanthosoma berlinii
Xanthosoma betancurii
Xanthosoma bilineatum
Xanthosoma bolivaranum
Xanthosoma brasiliense
Xanthosoma brevispathaceum
Xanthosoma brownii
Xanthosoma buntingianum
Xanthosoma caladioides
Xanthosoma calcaense
Xanthosoma camposii
Xanthosoma caquetense
Xanthosoma caracu
Xanthosoma caucavallense
Xanthosoma caulotuberculatum
Xanthosoma ceronii
Xanthosoma cerrosapense
Xanthosoma chaparense
Xanthosoma cinchonaense
Xanthosoma conspurcatum
Xanthosoma contractum
Xanthosoma cordatum
Xanthosoma cordifolium
Xanthosoma corentynense
Xanthosoma crassilaminum
Xanthosoma crassinervium
Xanthosoma cundinamarcense
Xanthosoma daguense
Xanthosoma danielsii
Xanthosoma daulense
Xanthosoma davidsmithii
Xanthosoma davidsonii
Xanthosoma debelliae
Xanthosoma delannayi
Xanthosoma eggersii
Xanthosoma epipetricum
Xanthosoma flavomaculatum
Xanthosoma fonnegrae
Xanthosoma foreroi
Xanthosoma galianoi
Xanthosoma giraldoi
Xanthosoma gonzalezii
Xanthosoma granvillei
Xanthosoma gratiae
Xanthosoma guaramacalense
Xanthosoma guayaquilense
Xanthosoma guttatum
Xanthosoma hammelii
Xanthosoma hannoniae
Xanthosoma harlingianum
Xanthosoma helleborifolium
Xanthosoma herrerae
Xanthosoma huilense
Xanthosoma hylaeae
Xanthosoma jaramilloi
Xanthosoma jatunsachense
Xanthosoma jorgeramosii
Xanthosoma killipii
Xanthosoma knappiae
Xanthosoma kressii
Xanthosoma kvistii
Xanthosoma lagunaense
Xanthosoma laselvaense
Xanthosoma latestigmatum
Xanthosoma liesneri
Xanthosoma lindenii
Xanthosoma linganii
Xanthosoma lojaense
Xanthosoma lojtnantii
Xanthosoma longepedunculum
Xanthosoma longilobum
Xanthosoma lucens
Xanthosoma luteynii
Xanthosoma macarenense
Xanthosoma mafaffoides
Xanthosoma mansellii
Xanthosoma mariquitense
Xanthosoma maroae
Xanthosoma mashpiense
Xanthosoma maximiliani
Xanthosoma mendozae
Xanthosoma mexicanum
Xanthosoma monteagudoi
Xanthosoma muluwataya
Xanthosoma munchiquense
Xanthosoma nambiense
Xanthosoma nangaritzense
Xanthosoma narinoense
Xanthosoma nestorpazii
Xanthosoma nitidum
Xanthosoma nodosum
Xanthosoma nunezii
Xanthosoma ollgaardii
Xanthosoma orinocense
Xanthosoma ortizii
Xanthosoma pailaense
Xanthosoma palaciosii
Xanthosoma palenquense
Xanthosoma panguiense
Xanthosoma paradoxum
Xanthosoma paruimaense
Xanthosoma peltatum
Xanthosoma pennellii
Xanthosoma pentaphyllum
Xanthosoma perssonii
Xanthosoma petaquillense
Xanthosoma pichinchense
Xanthosoma platylobum
Xanthosoma plowmanii
Xanthosoma poecile
Xanthosoma poeppigii
Xanthosoma pubescens
Xanthosoma pulcachense
Xanthosoma pulchrum
Xanthosoma purpureomaculatum
Xanthosoma reinae
Xanthosoma reticulatum
Xanthosoma riedelianum
Xanthosoma rupununiense
Xanthosoma sagittifolium
Xanthosoma saguasense
Xanthosoma sandiaense
Xanthosoma sanintiae
Xanthosoma scherberichii
Xanthosoma Schott
Xanthosoma seideliae
Xanthosoma silverstonei
Xanthosoma sinnamaryense
Xanthosoma sizemoreae
Xanthosoma stenospathum
Xanthosoma stergiosii
Xanthosoma striatipes
Xanthosoma striolatum
Xanthosoma syngoniifolium
Xanthosoma tachiraense
Xanthosoma taioba
Xanthosoma tarapotense
Xanthosoma thompsoniae
Xanthosoma trichophyllum
Xanthosoma trinitense
Xanthosoma tuberquiae
Xanthosoma ucumariense
Xanthosoma ulei
Xanthosoma undipes
Xanthosoma vargasii
Xanthosoma villaricense
Xanthosoma viviparum
Xanthosoma weeksii
Xanthosoma wendlandii
Xanthosoma wurdackii
Xanthosoma yarumalense
Xanthosoma yucatanense
Xanthosoma zamoraense
Xanthostemon arenarius
Xanthostemon aurantiacus
Xanthostemon Bolt-Head
Xanthostemon bracteatus
Xanthostemon carlii
Xanthostemon chrysanthus
Xanthostemon confertiflorus
Xanthostemon crenulatus
Xanthostemon eucalyptoides
Xanthostemon F.Muell.
Xanthostemon ferrugineus
Xanthostemon formosus
Xanthostemon francii
Xanthostemon fruticosus
Xanthostemon graniticus
Xanthostemon grisii
Xanthostemon gugerlii
Xanthostemon lateriflorus
Xanthostemon laurinus
Xanthostemon longipes
Xanthostemon melanoxylon
Xanthostemon multiflorus
Xanthostemon myrtifolius
Xanthostemon novaguineensis
Xanthostemon Obiri-Rock
Xanthostemon oppositifolius
Xanthostemon paradoxus
Xanthostemon petiolatus
Xanthostemon philippinensis
Xanthostemon psidioides
Xanthostemon pubescens
Xanthostemon ruber
Xanthostemon sebertii
Xanthostemon speciosus
Xanthostemon sulfureus
Xanthostemon umbrosus
Xanthostemon velutinus
Xanthostemon verdugonianus
Xanthostemon verticillatus
Xanthostemon verus
Xanthostemon vieillardii
Xanthostemon whitei
Xanthostemon xerophilus
Xanthostemon youngii
Xanthoxalis Small
Xanthoxylon Spreng.
Xanthoxylum fagara
Xanthoxylum J.F.Gmel.
Xanthoxylum Mill.
Xantolis assamica
Xantolis baranensis
Xantolis boniana
Xantolis burmanica
Xantolis cambodiana
Xantolis hookeri
Xantolis longispinosa
Xantolis maritima
Xantolis parvifolia
Xantolis racemosa
Xantolis Raf.
Xantolis shweliensis
Xantolis stenosepala
Xantolis tomentosa
Xantonnea Pierre ex Pit.
Xatardia Meisn. ex Zeyh.
Xatardia scabra
Xenacanthus Bremek.
Xenocephalozia navicularis
Xenochila integrifolia
Xenocladia C.A.Arnold, 1940
Xenophya Schott
Xenophyton Hick, 1892
Xenopoma Willd.
Xenoscapa (Goldblatt) Goldblatt & J.C.Manning
Xenoscapa fistulosa
Xenoscapa grandiflora
Xenoscapa uliginosa
Xenostegia alatipes
Xenostegia D.F.Austin & Staples
Xenostegia lomamiensis
Xenostegia medium
Xenostegia pinnata
Xenostegia sapinii
Xenostegia tridentata
Xenothallus R.M.Schust.
Xenothallus vulcanicola
Xenotheca devonica
Xenotheca E.A.N.Arber & R.H.Goode, 1915
Xenoxylon W.Gothan, 1905
Xeranthemum annuum
Xeranthemum cylindraceum
Xeranthemum fragrans
Xeranthemum inapertum
Xeranthemum inapterum
Xeranthemum L.
Xeranthemum longepapposum
Xeranthemum neumayeri
Xeranthemum squarrosum
Xeroaloysia Tronc.
Xerobotrys Nutt.
Xerocarpus Guill. & Perr.
Xerochlamys Baker
Xerochlamys bojeriana
Xerochlamys coriacea
Xerochlamys diospyroidea
Xerochlamys elliptica
Xerochlamys itremoensis
Xerochlamys tampoketsensis
Xerochlamys undulata
Xerochlamys villosa
Xerochloa barbata
Xerochloa imberbis
Xerochloa laniflora
Xerochloa R.Br.
Xerochlorella K.Fucüková, P.O.Lewis & L.A.Lewis, 2014
Xerochrysum alpinum
Xerochrysum andrewiae
Xerochrysum banksii
Xerochrysum berarngutta
Xerochrysum bicolor
Xerochrysum boreale
Xerochrysum bracteatum
Xerochrysum Chinchilla
Xerochrysum collierianum
Xerochrysum copelandii
Xerochrysum frutescens
Xerochrysum Glencoe
Xerochrysum gudang
Xerochrysum hispidum
Xerochrysum interiore
Xerochrysum macranthum
Xerochrysum macsweeneyorum
Xerochrysum milliganii
Xerochrysum Mt-Merino
Xerochrysum murapan
Xerochrysum New-England
Xerochrysum palustre
Xerochrysum papillosum
Xerochrysum Point-Lookout
Xerochrysum strictum
Xerochrysum subundulatum
Xerochrysum Tin-Can-Bay
Xerochrysum Tzvelev
Xerochrysum viscosum
Xerochrysum wilsonii
Xerocladia viridiramis
Xeroderris Roberty
Xerodraba colobanthoides
Xerodraba lycopodioides
Xerodraba monantha
Xerodraba patagonica
Xerodraba Skottsb.
Xerogona Raf.
Xeromphis Raf.
Xeronema Brongn. & Gris
Xeronema callistemon
Xeronema moorei
Xeropetalum Delile
Xerophyllum asphodeloides
Xerophyllum tenax
Xerophyta acuminata
Xerophyta adendorffii
Xerophyta analavelonensis
Xerophyta andringitrensis
Xerophyta ankaranensis
Xerophyta arabica
Xerophyta argentea
Xerophyta aymoninii
Xerophyta brevifolia
Xerophyta calcicola
Xerophyta capillaris
Xerophyta cauliflora
Xerophyta concolor
Xerophyta connata
Xerophyta croatii
Xerophyta dasylirioides
Xerophyta decaryi
Xerophyta demeesmaekeriana
Xerophyta eglandulosa
Xerophyta elegans
Xerophyta equisetoides
Xerophyta eylesii
Xerophyta goetzei
Xerophyta hereroensis
Xerophyta hirtiflora
Xerophyta humbertii
Xerophyta humilis
Xerophyta isaloensis
Xerophyta jouyiana
Xerophyta junodii
Xerophyta Juss.
Xerophyta kirkii
Xerophyta leandrii
Xerophyta lewisiae
Xerophyta longicaulis
Xerophyta monroi
Xerophyta naegelsbachii
Xerophyta nutans
Xerophyta parviflora
Xerophyta pauciramosa
Xerophyta pectinata
Xerophyta pinifolia
Xerophyta purpurascens
Xerophyta rakotomalazae
Xerophyta rehmannii
Xerophyta retinervis
Xerophyta rippsteinii
Xerophyta rosea
Xerophyta scabrida
Xerophyta schlechteri
Xerophyta schnizleinia
Xerophyta seinei
Xerophyta sessiliflora
Xerophyta setosa
Xerophyta simulans
Xerophyta spekei
Xerophyta splendens
Xerophyta squarrosa
Xerophyta stenophylla
Xerophyta suaveolens
Xerophyta tabulare
Xerophyta trichophylla
Xerophyta tulearensis
Xerophyta velutina
Xerophyta villosa
Xerophyta viscosa
Xerophyta wentzeliana
Xerophyta zimbabwensis
Xerorchis amazonica
Xerorchis trichorhiza
Xerosicyos danguyi
Xerosicyos decaryi
Xerosicyos hirtellus
Xerosicyos pubescens
Xerosicyos tripartitus
Xerosiphon Turcz.
Xerospermum Blume
Xerospermum bonii
Xerospermum laevigatum
Xerospermum macrophyllum
Xerospermum noronhianum
Xerospiraea hartwegiana
Xerospiraea Henrickson
Xerotecoma J.C.Gomes
Xerotes R.Br.
Xerothamnella C.T.White
Xerothamnella herbacea
Xerothamnella parvifolia
Xerxes J.R.Grant
Xestaea Griseb.
Xilopia Juss., 1789
Ximenesia Cav.
Ximenia aegyptiaca
Ximenia americana
Ximenia caffra
Ximenia coriacea
Ximenia glauca
Ximenia horrida
Ximenia intermedia
Ximenia parviflora
Ximenia roigii
Ximeniaceae
Xiphidium Aubl.
Xiphidium caeruleum
Xiphidium pontederiiflorum
Xiphium Mill.
Xiphochaeta aquatica
Xiphochaeta Poepp. & Endl.
Xiphopterella alternidens
Xiphopterella corneri
Xiphopterella govidjoaensis
Xiphopterella gracilis
Xiphopterella hecistophylla
Xiphopterella hieronymusii
Xiphopterella murudensis
Xiphopterella nudicarpa
Xiphopterella Parris
Xiphopterella parva
Xiphopterella sparsipilosa
Xiphopteris apoensis
Xiphosiphonia ardreana
Xiphotheca canescens
Xiphotheca cordifolia
Xiphotheca elliptica
Xiphotheca fruticosa
Xiphotheca lanceolata
Xiphotheca phylicoides
Xiphotheca reflexa
Xiphotheca rosmarinifolia
Xiphotheca tecta
Xipotheca lanceolata
Xiquexique frewenii
Xiquexique gounellei
Xiquexique heptagonus
Xiquexique Lavor, Calvente & Versieux
Xiquexique tuberculatus
Xizangia bartsioides
Xochiquetzallia balsensis
Xochiquetzallia hannibalii
Xochiquetzallia magnifolia
Xochiquetzallia mortoniana
Xochiquetzallia thadhowardii
Xolantha Raf.
Xolisma Raf.
Xx
Xx viridissimus
Xylanche G.Beck von Mannagetta, 1893
Xylanthemum fisherae
Xylanthemum gilletii
Xylanthemum lingulatum
Xylanthemum macropodum
Xylanthemum paghmanense
Xylanthemum paleaceum
Xylanthemum pamiricum
Xylanthemum Tzvelev
Xylia africana
Xylia evansii
Xylia fraterna
Xylia ghesquierei
Xylia hoffmannii
Xylia mendoncae
Xylia schliebenii
Xylia torreana
Xylia xylocarpa
Xylobium aurantiacum
Xylobium bractescens
Xylobium buchtienianum
Xylobium chapadense
Xylobium coelia
Xylobium colleyi
Xylobium corrugatum
Xylobium dusenii
Xylobium elatum
Xylobium foveatum
Xylobium hyacinthinum
Xylobium leontoglossum
Xylobium Lindl.
Xylobium miliaceum
Xylobium ornatum
Xylobium ortizianum
Xylobium pallidiflorum
Xylobium palmifolium
Xylobium papillosum
Xylobium serratum
Xylobium squalens
Xylobium stanhopeifolium
Xylobium subintegrum
Xylobium sulfurinum
Xylobium undulatum
Xylobium varicosum
Xylobium variegatum
Xylobium wilhelminae
Xylobium zarumense
Xylocalyx aculeolatus
Xylocalyx asper
Xylocalyx Balf.f.
Xylocalyx carterae
Xylocalyx recurvus
Xylocarpus granatum
Xylocarpus J.Koenig
Xylocarpus moluccensis
Xylocarpus rumphii
Xylochloris J.Neustupa, M.Eliáš & P.Škaloud, 2011
Xylococcus Nutt.
Xylolejeunea aquarius
Xylolejeunea crenata
Xylolejeunea grolleana
Xylolejeunea pellucidissima
Xylolejeunea X.L.He & Grolle
Xylomastixia lusatica
Xylomelum angustifolium
Xylomelum benthamii
Xylomelum occidentale
Xylomelum pyriforme
Xylomelum salicinum
Xylomelum scottianum
Xylomelum Sm.
Xylon hypoleucum
Xylonagra arborea
Xylonagra Donn.Sm. & Rose
Xylonymus Kalkman ex Ding Hou
Xylonymus versteeghii
Xyloolaena Baill.
Xyloolaena humbertii
Xyloolaena perrieri
Xyloolaena sambiranensis
Xylophacos Rydb.
Xylophragma claussenii
Xylophragma corchoroides
Xylophragma harleyi
Xylophragma heterocalyx
Xylophragma myrianthum
Xylophragma platyphyllum
Xylophragma pratense
Xylophragma seemanniana
Xylophragma Sprague
Xylophragma unifoliolatum
Xylophylla L.
Xylophylla latifolia
Xylopia acunae
Xylopia acutiflora
Xylopia aethiopica
Xylopia africana
Xylopia altissima
Xylopia ambanjensis
Xylopia amplexicaulis
Xylopia annoniflora
Xylopia anomala
Xylopia ardua
Xylopia arenaria
Xylopia aromatica
Xylopia atlantica
Xylopia aurantiiodora
Xylopia australis
Xylopia barbata
Xylopia batesii
Xylopia beananensis
Xylopia beccarii
Xylopia benthamii
Xylopia blancoi
Xylopia brasiliensis
Xylopia buxifolia
Xylopia calophylla
Xylopia calva
Xylopia capuronii
Xylopia carinata
Xylopia caudata
Xylopia cayennensis
Xylopia championii
Xylopia chivantinensis
Xylopia chocoensis
Xylopia columbiana
Xylopia congolensis
Xylopia conjungens
Xylopia coriifolia
Xylopia crinita
Xylopia cupularis
Xylopia cuspidata
Xylopia danguyella
Xylopia decorticans
Xylopia degeneri
Xylopia densiflora
Xylopia densifolia
Xylopia dibaccata
Xylopia dielsii
Xylopia discreta
Xylopia egleriana
Xylopia elliotii
Xylopia elliptica
Xylopia emarginata
Xylopia erythrodactyla
Xylopia excellens
Xylopia fananehanensis
Xylopia ferruginea
Xylopia flamignii
Xylopia flexuosa
Xylopia frutescens
Xylopia fusca
Xylopia galokothamna
Xylopia ghesquiereana
Xylopia gilbertii
Xylopia glauca
Xylopia globosa
Xylopia gracilipes
Xylopia hastarum
Xylopia heterotricha
Xylopia humblotiana
Xylopia hypolampra
Xylopia hypolampsa
Xylopia javanica
Xylopia kalabenonensis
Xylopia katangensis
Xylopia keniensis
Xylopia kuchingensis
Xylopia L.
Xylopia laevigata
Xylopia lamarckii
Xylopia lamii
Xylopia lanceolata
Xylopia langsdorfiana
Xylopia lastelliana
Xylopia latipetala
Xylopia le-testui
Xylopia lemurica
Xylopia lenombe
Xylopia ligustrifolia
Xylopia lokobensis
Xylopia longirostra
Xylopia lukei
Xylopia maasiana
Xylopia maccraei
Xylopia maccreae
Xylopia maccreai
Xylopia macrantha
Xylopia madagascariensis
Xylopia magna
Xylopia maingayi
Xylopia malayana
Xylopia marojejyana
Xylopia micans
Xylopia micrantha
Xylopia microcalyx
Xylopia microphylla
Xylopia mildbraedii
Xylopia monticola
Xylopia multiflora
Xylopia muricata
Xylopia mwasumbii
Xylopia neglecta
Xylopia nervosa
Xylopia ngii
Xylopia nigricans
Xylopia nilotica
Xylopia nitida
Xylopia niyomdhamii
Xylopia obtusifolia
Xylopia ochrantha
Xylopia orestera
Xylopia orinocensis
Xylopia pacifica
Xylopia pallescens
Xylopia panamensis
Xylopia pancheri
Xylopia paniculata
Xylopia papuana
Xylopia parviflora
Xylopia patoniae
Xylopia peekelii
Xylopia perrierii
Xylopia peruviana
Xylopia phloiodora
Xylopia pierrei
Xylopia piratae
Xylopia pittieri
Xylopia platycarpa
Xylopia platypetala
Xylopia polyantha
Xylopia pseudolemurica
Xylopia pulchella
Xylopia pulcherrima
Xylopia pynaertii
Xylopia quintasii
Xylopia ravelonarivoi
Xylopia retusa
Xylopia richardii
Xylopia rigidiflora
Xylopia rubescens
Xylopia sahafariensis
Xylopia sclerophylla
Xylopia sericea
Xylopia sericolampra
Xylopia sericophylla
Xylopia sessiliflora
Xylopia shirensis
Xylopia spec.
Xylopia spruceana
Xylopia staudtii
Xylopia subdehiscens
Xylopia surinamensis
Xylopia talbotii
Xylopia tanganyikensis
Xylopia tenuipetala
Xylopia tomentosa
Xylopia torrei
Xylopia toussaintii
Xylopia trichostemon
Xylopia unguiculata
Xylopia uniflora
Xylopia venezuelana
Xylopia vieillardii
Xylopia vielana
Xylopia villosa
Xylopia vitiensis
Xylopia wilwerthii
Xylopia xylantha
Xylopodia klaprothioides
Xylopodia laurensis
Xylopteris J.Frenguelli, 1943
Xylorhiza cognata
Xylorhiza confertifolia
Xylorhiza cronquistii
Xylorhiza frutescens
Xylorhiza glabriuscula
Xylorhiza linearifolia
Xylorhiza Nutt.
Xylorhiza orcuttii
Xylorhiza tortifolia
Xylorhiza venusta
Xylorhiza wrightii
Xylosalsola arbuscula
Xylosalsola chiwensis
Xylosalsola paletzkiana
Xylosalsola richteri
Xylosalsola Tzvelev
Xyloselinum laoticum
Xyloselinum leonidii
Xyloselinum vietnamense
Xylosma acunae
Xylosma avilae
Xylosma bahamense
Xylosma benthamii
Xylosma bernardiana
Xylosma brachystachys
Xylosma buxifolia
Xylosma Cape-Melville
Xylosma capillipes
Xylosma celastrina
Xylosma characantha
Xylosma chiapensis
Xylosma chlorantha
Xylosma ciliatifolia
Xylosma cinerea
Xylosma claraensis
Xylosma confusa
Xylosma controversa
Xylosma cordata
Xylosma coriacea
Xylosma domingensis
Xylosma dothioense
Xylosma dothioensis
Xylosma elegans
Xylosma flexuosa
Xylosma gigantifolia
Xylosma glaberrima
Xylosma glaucescens
Xylosma hawaiense
Xylosma hispidula
Xylosma horrida
Xylosma iberiensis
Xylosma inaequinervia
Xylosma intermedia
Xylosma J.R.Forst. & G.Forst.
Xylosma kaalaensis
Xylosma lancifolia
Xylosma longifolia
Xylosma longipedicellata
Xylosma longipetiolata
Xylosma lucida
Xylosma luzonensis
Xylosma martinicensis
Xylosma molesta
Xylosma Mt-Lewis
Xylosma nelsonii
Xylosma nervosa
Xylosma nitida
Xylosma oligandra
Xylosma orbiculata
Xylosma ovata
Xylosma pachyphylla
Xylosma palawanensis
Xylosma panamensis
Xylosma pancheri
Xylosma papuana
Xylosma parvifolia
Xylosma paucinervosa
Xylosma peltata
Xylosma pininsulare
Xylosma pininsularis
Xylosma prockia
Xylosma proctorii
Xylosma prunifolium
Xylosma pubescens
Xylosma quichense
Xylosma racemosum
Xylosma raimondii
Xylosma rhombifolia
Xylosma roigiana
Xylosma rubicundum
Xylosma ruiziana
Xylosma rusbyana
Xylosma samoensis
Xylosma sanctae-annae
Xylosma schaefferioides
Xylosma schroederi
Xylosma schwaneckeana
Xylosma senticosa
Xylosma serrata
Xylosma shaferi
Xylosma simulans
Xylosma smithiana
Xylosma spiculifera
Xylosma suaveolens
Xylosma subsessilifolia
Xylosma suluensis
Xylosma sumatrana
Xylosma terrae-reginae
Xylosma tessmannii
Xylosma tuberculata
Xylosma tweediana
Xylosma velutina
Xylosma venosa
Xylosma vincentii
Xylosma zongoi
Xylosteon Mill.
Xylosteum Ruppius
Xylothamia G.L.Nesom, Y.B.Suh, D.R.Morgan & B.B.Simpson
Xylotheca Hochst.
Xylotheca kraussiana
Xylotheca tettensis
Xymalos monospora
Xymaloxylon P.Louvet, 1975
Xyphidium Steud., 1841
Xyridaceae
Xyridion (Tausch) Fourr.
Xyris aberdarica
Xyris acrophila
Xyris affinis
Xyris albescens
Xyris almae
Xyris ambigua
Xyris americana
Xyris amorimii
Xyris anamariae
Xyris anceps
Xyris andina
Xyris angularis
Xyris angustifolia
Xyris anisophylla
Xyris apureana
Xyris aquatica
Xyris aracamunae
Xyris arachnoidea
Xyris araracuarae
Xyris archeri
Xyris aristata
Xyris asperula
Xyris asterotricha
Xyris atrata
Xyris atriceps
Xyris atrospicata
Xyris atrovirida
Xyris bahiana
Xyris baldwiniana
Xyris bampsii
Xyris bancana
Xyris bialata
Xyris bicarinata
Xyris bicephala
Xyris bicostata
Xyris blanchetiana
Xyris blepharophylla
Xyris boliviana
Xyris borneensis
Xyris brachysepala
Xyris bracteata
Xyris bracteicaulis
Xyris brevifolia
Xyris cachimbensis
Xyris calcicola
Xyris caparaoensis
Xyris capensis
Xyris capillaris
Xyris capnoides
Xyris carinata
Xyris caroliniana
Xyris chapmanii
Xyris cheumatophila
Xyris chimantae
Xyris ciliata
Xyris cipoensis
Xyris complanata
Xyris concinna
Xyris confusa
Xyris congensis
Xyris connosepala
Xyris consanguinea
Xyris consolida
Xyris contracta
Xyris correlliorum
Xyris cryptantha
Xyris cuatrecasana
Xyris culmenicola
Xyris curassavica
Xyris cyperoides
Xyris dardanoi
Xyris dawsonii
Xyris decipiens
Xyris decussata
Xyris delicatula
Xyris densa
Xyris desquamata
Xyris diamantinae
Xyris diaphanobracteata
Xyris difformis
Xyris dilatatiscapa
Xyris dissimilis
Xyris dissitifolia
Xyris disticha
Xyris drummondii
Xyris ednae
Xyris ekmanii
Xyris elegantula
Xyris eleocharoides
Xyris elliottii
Xyris erosa
Xyris erubescens
Xyris esmeraldae
Xyris exigua
Xyris fallax
Xyris ferreirae
Xyris festucifolia
Xyris fibrosa
Xyris filifolia
Xyris filiformis
Xyris fimbriata
Xyris flexifolia
Xyris flexuosa
Xyris floridana
Xyris foliolata
Xyris formosana
Xyris fragilis
Xyris fredericoi
Xyris frequens
Xyris friesii
Xyris frondosa
Xyris fugaciflora
Xyris fuliginea
Xyris gerrardii
Xyris glandacea
Xyris glaziowii
Xyris globosa
Xyris gongylospica
Xyris gossweileri
Xyris goyazensis
Xyris gracilis
Xyris gracillima
Xyris graminosa
Xyris grandiceps
Xyris grandis
Xyris graniticola
Xyris graomogolensis
Xyris grisebachii
Xyris Gronov. ex L.
Xyris Gronovius
Xyris guaranitica
Xyris guianensis
Xyris guillenii
Xyris harleyi
Xyris hatschbachii
Xyris hilariana
Xyris huberi
Xyris huillensis
Xyris humpatensis
Xyris hymenachne
Xyris hystrix
Xyris inaequalis
Xyris indica
Xyris indivisa
Xyris insignis
Xyris intersita
Xyris involucrata
Xyris irwinii
Xyris itambensis
Xyris itatiayensis
Xyris jataiana
Xyris juncea
Xyris juncifolia
Xyris jupicai
Xyris kibaraensis
Xyris kornasiana
Xyris kradungensis
Xyris kukenaniana
Xyris kundelungensis
Xyris labatii
Xyris lacerata
Xyris laevigata
Xyris lagoinhae
Xyris lanata
Xyris laniceps
Xyris lanuginosa
Xyris laxiflora
Xyris laxifolia
Xyris lejolyana
Xyris leonensis
Xyris leptocaulis
Xyris liesneri
Xyris linifolia
Xyris lithophila
Xyris lobbii
Xyris lomatophylla
Xyris lonchophylla
Xyris longibracteata
Xyris longifolia
Xyris longiscapa
Xyris longisepala
Xyris lucida
Xyris luetzelburgii
Xyris lugubris
Xyris lutescens
Xyris macbrideana
Xyris machrisiana
Xyris madagascariensis
Xyris makuensis
Xyris mallocephala
Xyris malmeana
Xyris mantuensis
Xyris maparecida
Xyris marginata
Xyris maxima
Xyris melanovaginata
Xyris mello-barretoi
Xyris membranibracteata
Xyris metallica
Xyris mexiae
Xyris mexicana
Xyris mima
Xyris minarum
Xyris montana
Xyris moraesii
Xyris morii
Xyris mucujensis
Xyris nanuzae
Xyris natalensis
Xyris navicularis
Xyris neblinae
Xyris neglecta
Xyris nervata
Xyris nigra
Xyris nigrescens
Xyris nigricans
Xyris nilssonii
Xyris nivea
Xyris nubigena
Xyris obcordata
Xyris oblata
Xyris obscura
Xyris obtusiuscula
Xyris oligantha
Xyris operculata
Xyris organensis
Xyris ornithoptera
Xyris oxylepis
Xyris paleacea
Xyris panacea
Xyris pancheri
Xyris paradisiaca
Xyris paraensis
Xyris parvula
Xyris pauciflora
Xyris pectinata
Xyris phaeocephala
Xyris pilosa
Xyris piranii
Xyris pirapamae
Xyris piraquarae
Xyris piresiana
Xyris plantaginea
Xyris platylepis
Xyris platystachya
Xyris poculipoda
Xyris popeana
Xyris porcata
Xyris porphyrea
Xyris pranceana
Xyris prolificans
Xyris ptariana
Xyris pterygoblephara
Xyris pulchella
Xyris pumila
Xyris ramboi
Xyris regnellii
Xyris rehmannii
Xyris reitzii
Xyris retrorsifimbriata
Xyris rhodolepis
Xyris rigida
Xyris rigidaeformis
Xyris rigidiformis
Xyris riopretensis
Xyris roraimae
Xyris rostrata
Xyris roycei
Xyris rubella
Xyris rubrolimbata
Xyris rubromarginata
Xyris rupicola
Xyris sanguinea
Xyris savanensis
Xyris sceptrifera
Xyris schizachne
Xyris schliebenii
Xyris schneeana
Xyris serrana
Xyris setigera
Xyris seubertii
Xyris shepherdiana
Xyris sincorana
Xyris smalliana
Xyris sororia
Xyris sparsifolia
Xyris spathacea
Xyris spathifolia
Xyris spectabilis
Xyris sphaerocephala
Xyris spinulosa
Xyris spruceana
Xyris stenocephala
Xyris stenophylla
Xyris stenophylloides
Xyris stenostachya
Xyris stenotera
Xyris straminea
Xyris stricta
Xyris subasperula
Xyris subglabrata
Xyris submetallica
Xyris subtilis
Xyris subulata
Xyris sulcatifolia
Xyris surinamensis
Xyris symoensii
Xyris tasmanica
Xyris teinosperma
Xyris tenella
Xyris tennesseensis
Xyris teres
Xyris teretifolia
Xyris terrestris
Xyris thysanolepis
Xyris toronoana
Xyris torta
Xyris tortilis
Xyris tortula
Xyris trachyphylla
Xyris trachysperma
Xyris trichocephala
Xyris trichophylla
Xyris tristis
Xyris tuberosa
Xyris uleana
Xyris uninervis
Xyris unistriata
Xyris ustulata
Xyris vacillans
Xyris valdeapiculata
Xyris valida
Xyris velutina
Xyris veruina
Xyris vestita
Xyris villosicarinata
Xyris vivipara
Xyris wallichii
Xyris wawrae
Xyris welwitschii
Xyris witsenioides
Xyris wurdackii
Xyris xiphophylla
Xyroides Thouars
Xyropteris K.U.Kramer
Xyropteris stortii
Xyroschoenus hornei
Xyroschoenus Larridon
Xysmalobium acerateoides
Xysmalobium alatum
Xysmalobium andongense
Xysmalobium asperum
Xysmalobium baurii
Xysmalobium brownianum
Xysmalobium congoense
Xysmalobium convallariiflorum
Xysmalobium fluviale
Xysmalobium fraternum
Xysmalobium gerrardii
Xysmalobium gomphocarpoides
Xysmalobium gossweileri
Xysmalobium gramineum
Xysmalobium heudelotianum
Xysmalobium holubii
Xysmalobium involucratum
Xysmalobium kaessneri
Xysmalobium membraniferum
Xysmalobium orbiculare
Xysmalobium parviflorum
Xysmalobium patulum
Xysmalobium pearsonii
Xysmalobium prunelloides
Xysmalobium rhodesianum
Xysmalobium rhomboideum
Xysmalobium samoritourei
Xysmalobium stockenstromense
Xysmalobium tysonianum
Xysmalobium undulatum
Xysmalobium woodii""".strip().split("\n")

# ══════════════════════════════════════════════
#  UTILITAIRES
# ══════════════════════════════════════════════

def slugify(nom):
    """Convertit un nom de plante en nom de fichier HTML."""
    s = nom.lower()
    # Remplacer les caractères spéciaux
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


def generer_html(nom, slug, gbif):
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
            if label in ("Genre",):
                taxo_rows += f'<div class="taxo-row"><dt>{label}</dt><dd><em>{valeur}</em></dd></div>\n'
            else:
                taxo_rows += f'<div class="taxo-row"><dt>{label}</dt><dd>{valeur}</dd></div>\n'

    famille_tag = famille or "Indéterminée"

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
  <link rel="stylesheet" href="../../plant.css" />
</head>
<body>

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
      <a href="../../encyclopedie/X.html">Espèces en « X »</a>
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
            <span class="plant-badges"><span class="badge badge--safe">✓ Non toxique</span></span>
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
    <a href="../../encyclopedie/Q.html" style="color:var(--accent)">← Retour aux espèces en X</a>
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
    print("  Herbarium — Génération pages HTML Lettre X")
    print("═" * 55)

    dossier = Path(DOSSIER_SORTIE)
    dossier.mkdir(parents=True, exist_ok=True)

    log = charger_log()
    total = len(PLANTES)
    print(f"\n📋 {total} plantes à traiter\n")

    compteurs = {"ok": 0, "skip": 0, "erreur": 0}

    for i, nom in enumerate(PLANTES, 1):
        nom = nom.strip()
        if not nom:
            continue

        slug = slugify(nom)
        nom_fichier = f"{slug}.html"
        chemin = dossier / nom_fichier

        print(f"[{i}/{total}] {nom}")

        if log.get(nom_fichier) == "ok" and chemin.exists():
            print(f"  ⏭  Déjà généré")
            compteurs["skip"] += 1
            continue

        # Récupérer infos GBIF
        gbif = recuperer_gbif(nom)
        if gbif.get("famille"):
            print(f"  🌿 {gbif['famille']}")
        else:
            print(f"  ⚠  Famille non trouvée sur GBIF")

        # Générer et sauvegarder
        html = generer_html(nom, slug, gbif)
        chemin.write_text(html, encoding="utf-8")

        log[nom_fichier] = "ok"
        sauvegarder_log(log)
        compteurs["ok"] += 1

        time.sleep(0.2)  # Respecter l'API GBIF

    print("\n" + "═" * 55)
    print(f"  ✅ {compteurs['ok']} générées  |  "
          f"⏭  {compteurs['skip']} ignorées  |  "
          f"✗ {compteurs['erreur']} erreurs")
    print(f"  📂 Fichiers dans : {DOSSIER_SORTIE}")
    print("═" * 55)


if __name__ == "__main__":
    main()
