#!/usr/bin/env python3
"""
Herbarium — Générateur de pages HTML pour les plantes Q
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

DOSSIER_SORTIE  = "./Q_Plante_page"
LETTRE          = "Q"
LETTRE_HTML     = "Q.html"
LOG_FILE        = "generation_log_pages_Q.json"
HEADERS         = {"User-Agent": "Herbarium-Bot/1.0"}

# ══════════════════════════════════════════════
#  LISTE DES PLANTES
# ══════════════════════════════════════════════

PLANTES = """Qasimia C.R.Hill, R.H.Wagner & A.A.El-Khayal, 1985
Qiongzhuea Hsueh f. & T.P.Yi
Quadraditum F.H.Cramer, 1964
Quadraeculina V.S.Maljavkina, 1949
Quadraplanus brossus
Quadrasia Elmer
Quadrella angustifolia
Quadrella antonensis
Quadrella asperifolia
Quadrella calciphila
Quadrella cynophallophora
Quadrella domingensis
Quadrella dressleri
Quadrella ferruginea
Quadrella filipes
Quadrella incana
Quadrella indica
Quadrella isthmensis
Quadrella J.Presl
Quadrella lindeniana
Quadrella lundellii
Quadrella mirifica
Quadrella morenoi
Quadrella odoratissima
Quadrella pringlei
Quadrella quintanarooensis
Quadrella singularis
Quadrella steyermarkii
Quadribractea moluccana
Quadrichloris Fott, 1959
Quadricoccus ellipticus
Quadricoccus euryhalinicus
Quadricoccus Fott, 1948
Quadricoccus laevis
Quadricoccus verrucosus
Quadricolpites reticulatus
Quadrigula chodatii
Quadrigula closterioides
Quadrigula closteroides
Quadrigula korshikovii
Quadrigula korsikovii
Quadrigula pfitzeri
Quadriplatanus georgianus
Quadrispermum E.M.Friis, K.R.Pedersen & P.R.Crane, 2013
Quadrocladus K.Mädler, 1957
Quaestora G.Mapes & G.W.Rothwell, 1980
Qualea acuminata
Qualea amapaensis
Qualea amoena
Qualea Aubl.
Qualea brasiliana
Qualea brevipedicellata
Qualea caerulea
Qualea calophylla
Qualea clavata
Qualea coerulea
Qualea cordata
Qualea cryptantha
Qualea cyanea
Qualea cymulosa
Qualea decorticans
Qualea densiflora
Qualea dinizii
Qualea elegans
Qualea gestasiana
Qualea gracilior
Qualea grandiflora
Qualea hannekesaskiarum
Qualea homosepala
Qualea impexa
Qualea ingens
Qualea insignis
Qualea johannabakkerae
Qualea labouriauana
Qualea lundii
Qualea macropetala
Qualea marioniae
Qualea megalocarpa
Qualea mori-boomii
Qualea muelleriana
Qualea multiflora
Qualea panamensis
Qualea paraensis
Qualea parviflora
Qualea polychroma
Qualea rosea
Qualea rupicola
Qualea schomburgkiana
Qualea selloi
Qualea tessmannii
Qualea themistoclesii
Qualea tricolor
Qualea tuberculata
Qualea wurdackii
Qualisaspora J.B.Richardson, J.H.Ford & F.Parker, 1984
Quamoclidion angulatum
Quamoclit cardinalis
Quamoclit Mill.
Quamoclit pennata
Quamoclit rodriguesii
Quamoclit sloteri
Quamoclita Raf.
Quapoya Aubl.
Quapoya littoralis
Quararibea alversonii
Quararibea amazonica
Quararibea angustifolia
Quararibea aristeguietae
Quararibea asterolepis
Quararibea Aubl.
Quararibea bilobata
Quararibea cacao
Quararibea caldasiana
Quararibea calycoptera
Quararibea casasecae
Quararibea cogolloi
Quararibea costaricensis
Quararibea cryptantha
Quararibea duckei
Quararibea floribunda
Quararibea foenigraeca
Quararibea funebris
Quararibea gigantiflora
Quararibea glazovii
Quararibea gomeziana
Quararibea grandifolia
Quararibea guatemalteca
Quararibea guianensis
Quararibea magnifica
Quararibea martini
Quararibea mayanum
Quararibea mayarum
Quararibea nigrescens
Quararibea obovalifolia
Quararibea parviflora
Quararibea pendula
Quararibea pendulifera
Quararibea penduliflora
Quararibea platyphylla
Quararibea pterocalyx
Quararibea pumila
Quararibea rangelii
Quararibea reflexipetala
Quararibea ruiziana
Quararibea sessiliflora
Quararibea similis
Quararibea spatulata
Quararibea stenophylla
Quararibea steyermarkii
Quararibea tessmannii
Quararibea tulekunae
Quararibea turbinata
Quararibea velutina
Quararibea villanuevae
Quararibea yunckeri
Quartinia A.Rich.
Quartinia Endl.
Quasiantennaria linearifolia
Quasisequoia V.Srinivasan & E.M.Friis, 1989
Quassia amara
Quassia arnhemensis
Quaternella confusa
Quaternella ephedroides
Quaternella glabratoides
Quechua glabrescens
Quechualia cardenasii
Quechualia fulta
Quechualia smithii
Quechualia trixioides
Quedlinburgia E.Knobloch & D.H.Mai, 1984
Quekettia jenmanii
Quekettia Lindl.
Quekettia microscopica
Quekettia papillosa
Quekettia pygmaea
Quekettia theresiae
Quekettia vermeuleniana
Quelchia bracteata
Quelchia cardonae
Quelchia conferta
Quelchia eriocaulis
Quelchia grandifolia
Quercifilix Copel.
Quercinium knowltoni
Quercinium lamarense
Quercinium Unger, 1842
Quercites H.A.C.Berger, 1832
Quercophyllum chinkapinense
Quercophyllum Fontaine, 1889
Quercophyllum grossedentatum
Quercophyllum platanoides
Quercophyllum wyomingense
Quercoxylon E.Hofmann, 1929
Quercus abnormalis
Quercus acatenangensis
Quercus acerifolia
Quercus acrodonta
Quercus aculcingensis
Quercus acuta
Quercus acutidens
Quercus acutifolia
Quercus acutissima
Quercus aerea
Quercus afares
Quercus affinis
Quercus agrifolia
Quercus ajoensis
Quercus alaskana
Quercus alba
Quercus albescens
Quercus albicaulis
Quercus albocincta
Quercus aliena
Quercus alienocrispula
Quercus alienoserratoides
Quercus alnifolia
Quercus alpescens
Quercus alpestris
Quercus alvordiana
Quercus ambigens
Quercus americana
Quercus amherstiana
Quercus amissaeloba
Quercus andegavensis
Quercus andrewsii
Quercus anguste-lepidosa
Quercus anguste-lepidota
Quercus angustiloba
Quercus annulata
Quercus arbutifolia
Quercus arenicola
Quercus argentata
Quercus argyrotricha
Quercus aristata
Quercus arizonica
Quercus arkansana
Quercus arrimatensis
Quercus ashei
Quercus asymmetrica
Quercus atlantica
Quercus aucheri
Quercus audleyensis
Quercus augustini
Quercus aurea
Quercus austrina
Quercus austrocochinchinensis
Quercus auzandrii
Quercus auzendei
Quercus avellaniformis
Quercus baenitzii
Quercus balaninorum
Quercus baloot
Quercus bambusifolia
Quercus baniensis
Quercus banksiaefolia
Quercus baolamensis
Quercus baronii
Quercus barrancana
Quercus basaseachicensis
Quercus bawanglingensis
Quercus beadlei
Quercus bebbiana
Quercus beckyae
Quercus beguinotii
Quercus bella
Quercus benderi
Quercus benthamii
Quercus berberidifolia
Quercus bernardensis
Quercus berryi
Quercus beturica
Quercus bibbiana
Quercus bicolor
Quercus bicornis
Quercus bidoupensis
Quercus bimundorum
Quercus bivoniana
Quercus blakei
Quercus blaoensis
Quercus blufftonensis
Quercus borosii
Quercus bourgaei
Quercus boweniana
Quercus boyntonii
Quercus braianensis
Quercus brandegeei
Quercus brandisiana
Quercus brantii
Quercus breedloveana
Quercus brenesii
Quercus brevicalyx
Quercus breviradiata
Quercus brittonii
Quercus browni
Quercus buckleyi
Quercus burnetensis
Quercus bushii
Quercus caduca
Quercus calophylla
Quercus cambodiensis
Quercus campitica
Quercus camusiae
Quercus canariensis
Quercus canbyi
Quercus cantabrica
Quercus capesii
Quercus carbonensis
Quercus carduchorum
Quercus carmenensis
Quercus carolinensis
Quercus carrissoana
Quercus castanea
Quercus castaneifolia
Quercus castaneopsis
Quercus castanopseifolia
Quercus catesbaeifolia
Quercus cedrosensis
Quercus centenaria
Quercus cerrioides
Quercus cerris
Quercus cerris x Quercus petraea
Quercus chamissonis
Quercus championii
Quercus chaneyi
Quercus chapmanii
Quercus charcasana
Quercus chartacea
Quercus chenii
Quercus chevalieri
Quercus chiapensis
Quercus chihuahuensis
Quercus chimaltenangana
Quercus chrysocalyx
Quercus chrysolepis
Quercus chrysotricha
Quercus chungii
Quercus ciliaris
Quercus clarnensis
Quercus clementei
Quercus coahuilensis
Quercus coccifera
Quercus cocciferoides
Quercus coccinea
Quercus cocksii
Quercus coffeaecolor
Quercus coffeicolor
Quercus cognatus
Quercus collettii
Quercus columnaris
Quercus comptoniae
Quercus conduplicans
Quercus conferta
Quercus confertifolia
Quercus congesta
Quercus conjungens
Quercus consanguinea
Quercus convallata
Quercus convexa
Quercus conzattii
Quercus copeyensis
Quercus coriacea
Quercus cornelius-muelleri
Quercus cornelius-mulleri
Quercus corrugata
Quercus cortesii
Quercus costaricensis
Quercus coutinhoi
Quercus crassifolia
Quercus crassipes
Quercus cravenensis
Quercus crenata
Quercus crispifolia
Quercus crispipilis
Quercus crispula
Quercus crossii
Quercus cualensis
Quercus culveri
Quercus dacica
Quercus daimingshanensis
Quercus dakotensis
Quercus dalechampii
Quercus dallii
Quercus dawsonii
Quercus dayana
Quercus deamii
Quercus decipiens
Quercus declinata
Quercus delavayi
Quercus deleiensis
Quercus delicatula
Quercus deliquescens
Quercus demareei
Quercus densifolia
Quercus dentata
Quercus dentoni
Quercus dentosa
Quercus depressa
Quercus depressipes
Quercus deserticola
Quercus dilacerata
Quercus dilatata
Quercus dinghuensis
Quercus disciformis
Quercus discreta
Quercus distincta
Quercus diversifolia
Quercus diversiloba
Quercus dolicholepis
Quercus doljensis
Quercus donnaiensis
Quercus douglasii
Quercus drummondii
Quercus drymeja
Quercus dryophyllopsis
Quercus dschorochensis
Quercus dubia
Quercus dumosa
Quercus durata
Quercus durifolia
Quercus duriuscula
Quercus dysophylla
Quercus eamesi
Quercus edithae
Quercus edithiae
Quercus eduardi
Quercus edwardsae
Quercus edwardsiae
Quercus egglestonii
Quercus elaena
Quercus elaenoides
Quercus elegans
Quercus elevaticostata
Quercus ellipsoidalis
Quercus elliptica
Quercus ellisiana
Quercus ellsworthianus
Quercus elmeri
Quercus elongata
Quercus elwyni
Quercus emoryi
Quercus engelmannii
Quercus engleriana
Quercus eoxalapensis
Quercus estremadurensis
Quercus eumorpha
Quercus ewanii
Quercus exacta
Quercus fabrei
Quercus faginea
Quercus falcata
Quercus fangshanensis
Quercus faxonii
Quercus fenestrata
Quercus fernaldii
Quercus filialis
Quercus fimbriata
Quercus firmurensis
Quercus fisheriana
Quercus floccosa
Quercus flocculenta
Quercus floribunda
Quercus fontana
Quercus fontanesii
Quercus fontqueri
Quercus franchetii
Quercus fraxinifolia
Quercus frutex
Quercus fulva
Quercus furcinervis
Quercus furfuracea
Quercus furuhjelmi
Quercus fusiformis
Quercus gaharuensis
Quercus galeanensis
Quercus gallaecica
Quercus gambelii
Quercus gambleana
Quercus ganderi
Quercus garlandensis
Quercus garryana
Quercus gaudini
Quercus gemelliflora
Quercus geminata
Quercus georgiana
Quercus germana
Quercus ghiesbreghtii
Quercus giffordii
Quercus gilbertii
Quercus gilva
Quercus glabrescens
Quercus glauca
Quercus glaucescens
Quercus glaucoides
Quercus glomerata
Quercus godeti
Quercus goepperti
Quercus gomeziana
Quercus gracilenta
Quercus grahamii
Quercus gravesii
Quercus greeneana
Quercus greggii
Quercus griffithii
Quercus grisea
Quercus groenlandica
Quercus grossidentata
Quercus guadalupensis
Quercus guayabalana
Quercus guyavifolia
Quercus handeliana
Quercus harbisonii
Quercus hartwissiana
Quercus hastingsii
Quercus hatcheri
Quercus haugi
Quercus havardii
Quercus hawkinsiae
Quercus hawkinsii
Quercus haydeni
Quercus haynaldiana
Quercus helferiana
Quercus helvetica
Quercus hemisphaerica
Quercus hesperia
Quercus heterophylla
Quercus hexagona
Quercus hieracifolia
Quercus hillii
Quercus hinckleyi
Quercus hintonii
Quercus hintoniorum
Quercus hirtifolia
Quercus hispanica
Quercus hollickii
Quercus holmesii
Quercus honbaensis
Quercus hondae
Quercus hopeiensis
Quercus horniana
Quercus hosiana
Quercus howellii
Quercus hui
Quercus huicholensis
Quercus humboldtii
Quercus humidicola
Quercus hybr
Quercus hypargyrea
Quercus hypoleucoides
Quercus hypophaea
Quercus hypoxantha
Quercus idahoensis
Quercus idzuensis
Quercus ilex
Quercus ilicifolia
Quercus iltisii
Quercus imbricaria
Quercus imbricariaefolia
Quercus incana
Quercus incomita
Quercus inconstans
Quercus inermis
Quercus infectoria
Quercus inopina
Quercus insignis
Quercus intricata
Quercus introgressa
Quercus invaginata
Quercus ithaburensis
Quercus jackiana
Quercus jahnii
Quercus jenseniana
Quercus john-tuckeri
Quercus johnstrupi
Quercus jolonensis
Quercus jonesii
Quercus joorii
Quercus judithae
Quercus kelloggii
Quercus kerneri
Quercus kerrii
Quercus kewensis
Quercus kinseliae
Quercus kiukiangensis
Quercus knoblochii
Quercus knowltoniana
Quercus kotschyana
Quercus kouangsiensis
Quercus L.
Quercus laceyi
Quercus laeta
Quercus laevis
Quercus lambertensis
Quercus lamellosa
Quercus lanata
Quercus lanceaefolia
Quercus lancifolia
Quercus langbianensis
Quercus latifolia
Quercus laurifolia
Quercus laurina
Quercus leana
Quercus lehmani
Quercus lenticellata
Quercus lesquereuxiana
Quercus leucotrichophora
Quercus liaoi
Quercus libanerris
Quercus libani
Quercus liboensis
Quercus liebmannii
Quercus lineata
Quercus litseoides
Quercus lobata
Quercus lobbii
Quercus lobulata
Quercus lodicosa
Quercus lonchitis
Quercus longinux
Quercus longispica
Quercus lousae
Quercus lowii
Quercus lucana
Quercus ludoviciana
Quercus lungmaiensis
Quercus lusitanica
Quercus lyrata
Quercus lyratiformis
Quercus maccormickoserrata
Quercus macdanielii
Quercus macdonaldii
Quercus macdougallii
Quercus macnabiana
Quercus macneilii
Quercus macranthera
Quercus macrocalyx
Quercus macrocarpa
Quercus macvaughii
Quercus magnoliifolia
Quercus magnosquamata
Quercus mannifera
Quercus manzanillana
Quercus margaretiae
Quercus margaretta
Quercus margarettae
Quercus marilandica
Quercus marlipoensis
Quercus mas
Quercus mccormickii
Quercus mcvaughii
Quercus megaleia
Quercus melissae
Quercus mellichampii
Quercus merriami
Quercus merrillii
Quercus mespilifolia
Quercus mexiae
Quercus mexicana
Quercus michauxii
Quercus microdentata
Quercus microphylla
Quercus milleri
Quercus minima
Quercus minor
Quercus miovariabilis
Quercus miyagii
Quercus mohriana
Quercus mongolica
Quercus mongolicodentata
Quercus mongolika
Quercus monimotricha
Quercus monnula
Quercus montana
Quercus montanensis
Quercus morehus
Quercus morii
Quercus morisii
Quercus morrisoniana
Quercus motuoensis
Quercus moultonensis
Quercus mudgii
Quercus muehlenbergii
Quercus mulleri
Quercus multinervis
Quercus munzii
Quercus mutabilis
Quercus myrsinaefolia
Quercus myrsinifolia
Quercus myrtifolia
Quercus nanchuanica
Quercus negundoides
Quercus neomairei
Quercus neomexicana
Quercus neopalmeri
Quercus neotharpii
Quercus nessiana
Quercus nevadensis
Quercus ngochoaensis
Quercus nigra
Quercus nigrescens
Quercus ningangensis
Quercus nipponica
Quercus nivea
Quercus novaecaesareae
Quercus novagrenobii
Quercus numantina
Quercus obconicus
Quercus oblongifolia
Quercus obtusa
Quercus obtusanthera
Quercus obtusata
Quercus obtusifolia
Quercus ocoteaefolia
Quercus oglethorpensis
Quercus oidocarpa
Quercus olafseni
Quercus oleoides
Quercus oocarpa
Quercus opaca
Quercus ophiosquamata
Quercus organensis
Quercus oviedoensis
Quercus oxyodon
Quercus oxyphylla
Quercus pachucana
Quercus pachyloma
Quercus pacifica
Quercus pagoda
Quercus pagodaefolia
Quercus palaeolithicola
Quercus palmeri
Quercus palmeriana
Quercus paludosa
Quercus palustris
Quercus palustris x rubra
Quercus panamandinaea
Quercus pannosa
Quercus parceserrata
Quercus parvula
Quercus pastorensis
Quercus paucidentata
Quercus pauciradiata
Quercus paui
Quercus paxtalensis
Quercus payettensis
Quercus peduncularis
Quercus pedunculata
Quercus penasii
Quercus penhallowi
Quercus peninsularis
Quercus pennivenia
Quercus pentacycla
Quercus percoriacea
Quercus peritula
Quercus perpallida
Quercus perseaefolia
Quercus persica
Quercus petraea
Quercus petraea x pubescens
Quercus petraea x robur
Quercus phanera
Quercus phellos
Quercus phillyraeoides
Quercus phillyreoides
Quercus phillyrioides
Quercus pinbianensis
Quercus pinnatifida
Quercus pinnativenulosa
Quercus planipocula
Quercus platanoides
Quercus platycalyx
Quercus pliopalmeri
Quercus poilanei
Quercus polymorpha
Quercus pongtungensis
Quercus pontica
Quercus porphyrogenita
Quercus potosina
Quercus praeco
Quercus praegilva
Quercus praenigra
Quercus prasina
Quercus pratti
Quercus previrginiana
Quercus primordialis
Quercus pringlei
Quercus prinoides
Quercus protosalicina
Quercus pseudinfectoria
Quercus pseudoalba
Quercus pseudoalnus
Quercus pseudocastanea
Quercus pseudocerris
Quercus pseudococcifera
Quercus pseudocornea
Quercus pseudodalechampii
Quercus pseudodchorochensis
Quercus pseudolyrata
Quercus pseudomargaretta
Quercus pseudomyrsinaefolia
Quercus pseudosemicarpifolia
Quercus pseudoverticillata
Quercus pseudowestfalica
Quercus pubens
Quercus pubescens
Quercus pubescens x robur
Quercus puentei
Quercus pumila
Quercus pungens
Quercus purulhana
Quercus pyrenaica
Quercus quangtriensis
Quercus radiata
Quercus raineri
Quercus ramaleyi
Quercus ramsbottomii
Quercus ratonensis
Quercus reflexa
Quercus rehderi
Quercus rehderiana
Quercus rekonis
Quercus repanda
Quercus resinosa
Quercus rex
Quercus rhamnoides
Quercus rhodopea
Quercus richteri
Quercus rineharticena
Quercus riparia
Quercus robbinsii
Quercus robur
Quercus robur x Quercus rubra
Quercus rolfsii
Quercus rosa-pintii
Quercus rosacea
Quercus rotundifolia
Quercus rubra
Quercus rubramenta
Quercus rudkinii
Quercus rugosa
Quercus runcinata
Quercus runcinatifolia
Quercus rupestris
Quercus rustii
Quercus rysophylla
Quercus sadleriana
Quercus saei
Quercus sagraeana
Quercus sagrana
Quercus salcedoi
Quercus salicifolia
Quercus salicina
Quercus saltillensis
Quercus salvadorensis
Quercus salzmanniana
Quercus sanchezcolinii
Quercus sapotifolia
Quercus sarahmariae
Quercus saravanensis
Quercus sargentii
Quercus sartorii
Quercus saulii
Quercus schochiana
Quercus schottkyana
Quercus scudderi
Quercus scytophylla
Quercus sebifera
Quercus seemannii
Quercus segoviensis
Quercus semecarpifolia
Quercus semiserrata
Quercus semiserratoides
Quercus senescens
Quercus senneniana
Quercus serra
Quercus serrata
Quercus sessilifolia
Quercus setulosa
Quercus shennongii
Quercus shingjenensis
Quercus shumardii
Quercus sichourensis
Quercus sicula
Quercus sideroxyla
Quercus similis
Quercus simplex
Quercus simulata
Quercus sinuata
Quercus skinneri
Quercus sororia
Quercus spinosa
Quercus spurioilex
Quercus stantoni
Quercus steenisii
Quercus steenstrupiana
Quercus stellata
Quercus stenophylloides
Quercus sterilis
Quercus sterrettii
Quercus stewardiana
Quercus stramineus
Quercus streimii
Quercus striatula
Quercus subconvexa
Quercus suber
Quercus suberoides
Quercus subfalcata
Quercus subglaucescens
Quercus subintegra
Quercus suboccolta
Quercus subsericea
Quercus subspathulata
Quercus substellata
Quercus subvariabilis
Quercus succulenta
Quercus sullyi
Quercus sumatrana
Quercus sumterensis
Quercus supranitida
Quercus suspecta
Quercus tabajdiana
Quercus takatorensis
Quercus tarahumara
Quercus tardifolia
Quercus tarokoensis
Quercus texana
Quercus tharpii
Quercus thorelii
Quercus tiaoloshanica
Quercus tingitana
Quercus tinkhamii
Quercus tlemcenensis
Quercus tomentella
Quercus tomentosinervis
Quercus tonduzii
Quercus toumeyi
Quercus townei
Quercus toxicodendrifolia
Quercus toza
Quercus trabutii
Quercus transiens
Quercus treubiana
Quercus tridentata
Quercus trojana
Quercus trungkhanhensis
Quercus tsinglingensis
Quercus tuberculata
Quercus tuitensis
Quercus tungmaiensis
Quercus turbinella
Quercus turneri
Quercus undulata
Quercus ungeri
Quercus urbani
Quercus urticifolia
Quercus utilis
Quercus uxoris
Quercus vacciniifolia
Quercus vaga
Quercus valdensis
Quercus valdinervosa
Quercus variabilis
Quercus vaseyana
Quercus velutina
Quercus venulosa
Quercus verde
Quercus vertesiensis
Quercus viburnifolia
Quercus vicentensis
Quercus viminea
Quercus virginiana
Quercus viridis
Quercus viveri
Quercus voyana
Quercus vulcanica
Quercus wagneri
Quercus walteriana
Quercus warburgii
Quercus wardiana
Quercus warei
Quercus washingtonensis
Quercus weedii
Quercus welshii
Quercus whitei
Quercus willdenowiana
Quercus wislizeni
Quercus wutaishanica
Quercus xalapensis
Quercus xanthoclada
Quercus xanthotricha
Quercus xuanlienensis
Quercus xylina
Quercus yanceyi
Quercus yiwuensis
Quercus yokohamensis
Quercus yongchunana
Quercus yulensis
Quereuxia angulata
Queria chilensis
Quesnelia alborosea
Quesnelia alvimii
Quesnelia arvensis
Quesnelia augustocoburgi
Quesnelia blanda
Quesnelia clavata
Quesnelia conquistensis
Quesnelia dubia
Quesnelia edmundoi
Quesnelia Gaudich.
Quesnelia georgiizizkae
Quesnelia humilis
Quesnelia imbricata
Quesnelia indecora
Quesnelia koltesii
Quesnelia lateralis
Quesnelia liboniana
Quesnelia marmorata
Quesnelia morreniana
Quesnelia quesneliana
Quesnelia skinneri
Quesnelia strobilispica
Quesnelia testudo
Quesnelia tubifolia
Quesnelia vasconcelosiana
Quesnelia violacea
Quetzalia areolata
Quetzalia contracta
Quetzalia ilicina
Quetzalia Lundell
Quetzalia occidentalis
Quetzalia pauciflora
Quetzalia schiedeana
Quetzalia stipitata
Quezeliantha tibestica
Quiabentia verticillata
Quiabentia zehntneri
Quiina amazonica
Quiina attenuata
Quiina Aubl.
Quiina berryi
Quiina cruegeriana
Quiina decastyla
Quiina florida
Quiina gentryi
Quiina glaziouvii
Quiina glaziovii
Quiina grandifolia
Quiina guianensis
Quiina integrifolia
Quiina jamaicensis
Quiina longifolia
Quiina macrophylla
Quiina magellano-gomezii
Quiina maguirei
Quiina negrensis
Quiina obovata
Quiina oiapocensis
Quiina paraensis
Quiina parvifolia
Quiina pteridophylla
Quiina rhytidopus
Quiina sessilis
Quiina tinifolia
Quiina wurdackii
Quiina yatuensis
Quiinaceae
Quillaja brasiliensis
Quillaja Molina
Quillaja saponaria
Quillaja smegmadermis
Quinaria Raf.
Quinchamala Willd.
Quinchamalium araucanum
Quinchamalium chilense
Quinchamalium Juss., 1789
Quinchamalium linifolium
Quincula lobata
Quincula Raf.
Quinetia urvillei
Quinqueremulus linearis
Quinquina Boehm.
Quintinia A.DC.
Quintinia acutifolia
Quintinia apoensis
Quintinia brassii
Quintinia elliptica
Quintinia epiphytica
Quintinia fawkneri
Quintinia hyehenensis
Quintinia kuborensis
Quintinia lanceolata
Quintinia ledermannii
Quintinia macgregorii
Quintinia macrophylla
Quintinia major
Quintinia media
Quintinia minor
Quintinia montiswilhelmii
Quintinia nutantiflora
Quintinia nutantifora
Quintinia oreophila
Quintinia quatrefagesii
Quintinia rigida
Quintinia schlechteriana
Quintinia sieberi
Quintinia tasmanensis
Quintinia verdonii
Quintiniapollis D.C.Mildenhall & D.T.Pocknall, 1989
Quintiniapollis striatulosa
Quiotania amazonica
Quipuanthus epipetricus
Quisqualis L.
Quisqueya Dod
Quisqueya ekmanii
Quisqueya holdridgei
Quisqueya karstii
Quisqueya rosea
Quivisia Comm. ex Juss.
Quivisianthe Baill.
Quivisianthe papinae
Quoya atriplicina
Quoya cuneata
Quoya dilatata
Quoya loxocarpa
Quoya oldfieldii
Quoya paniculata
Quoya verbascina""".strip().split("\n")

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
      <a href="../../encyclopedie/Q.html">Espèces en « Q »</a>
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
    <a href="../../encyclopedie/Q.html" style="color:var(--accent)">← Retour aux espèces en Q</a>
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
    print("  Herbarium — Génération pages HTML Lettre Q")
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
