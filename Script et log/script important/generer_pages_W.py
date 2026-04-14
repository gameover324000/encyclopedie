#!/usr/bin/env python3
"""
Herbarium — Générateur de pages HTML pour les plantes W
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

DOSSIER_SORTIE  = "./W_Plante_page"              # ← Dossier de sortie         ex: "./V_Plante_page"
LETTRE          = "W"                            # ← Lettre courante            ex: "V"
LETTRE_HTML     = "W.html"                       # ← Fichier index de la lettre ex: "V.html"
LOG_FILE        = "generation_log_pages_W.json"  # ← Fichier log                ex: "generation_log_pages_V.json"
HEADERS         = {"User-Agent": "Herbarium-Bot/1.0"}

# ══════════════════════════════════════════════
#  LISTE DES PLANTES
#  ⚠ À REMPLACER à chaque nouvelle lettre
#  → Coller ici toutes les plantes de la lettre,
#    une par ligne, sans numérotation.
# ══════════════════════════════════════════════

PLANTES = """Wachendorfia brachyandra
Wachendorfia Burm.
Wachendorfia Burm. ex L.
Wachendorfia multiflora
Wachendorfia paniculata
Wachendorfia thyrsiflora
Waddingtonia coquimbana
Wadithamnus artemisioides
Wadithamnus T.Hammer & R.W.Davis
Waernia mirabilis
Waernia R.T.Wilce, C.A.Maggs & J.R.Sears, 2003
Wahlbergella Fr.
Wahlenbergia abyssinica
Wahlenbergia acaulis
Wahlenbergia acicularis
Wahlenbergia acuminata
Wahlenbergia adamsonii
Wahlenbergia adpressa
Wahlenbergia akaroa
Wahlenbergia albens
Wahlenbergia albicaulis
Wahlenbergia albomarginata
Wahlenbergia androsacea
Wahlenbergia angustifolia
Wahlenbergia annua
Wahlenbergia annularis
Wahlenbergia annuliformis
Wahlenbergia appressifolia
Wahlenbergia arcta
Wahlenbergia aridicola
Wahlenbergia asparagoides
Wahlenbergia asperifolia
Wahlenbergia axillaris
Wahlenbergia banksiana
Wahlenbergia berteroi
Wahlenbergia Blume
Wahlenbergia brachiata
Wahlenbergia brachycarpa
Wahlenbergia brachyphylla
Wahlenbergia brasiliensis
Wahlenbergia brevisquamifolia
Wahlenbergia buseriana
Wahlenbergia caffra
Wahlenbergia calcarea
Wahlenbergia calycina
Wahlenbergia campanuloides
Wahlenbergia candolleana
Wahlenbergia candollei
Wahlenbergia capensis
Wahlenbergia capillacea
Wahlenbergia capillaris
Wahlenbergia capillata
Wahlenbergia capillifolia
Wahlenbergia capitata
Wahlenbergia cartilaginea
Wahlenbergia caryophylloides
Wahlenbergia cephalodina
Wahlenbergia cernua
Wahlenbergia cinerea
Wahlenbergia clavata
Wahlenbergia collomioides
Wahlenbergia congesta
Wahlenbergia congestifolia
Wahlenbergia constricta
Wahlenbergia cooperi
Wahlenbergia cordata
Wahlenbergia cordiformis
Wahlenbergia corymbosa
Wahlenbergia costata
Wahlenbergia cuspidata
Wahlenbergia debilis
Wahlenbergia decipiens
Wahlenbergia densicaulis
Wahlenbergia densifolia
Wahlenbergia denticulata
Wahlenbergia denudata
Wahlenbergia depressa
Wahlenbergia desmantha
Wahlenbergia dichotoma
Wahlenbergia dieterlenii
Wahlenbergia dilatata
Wahlenbergia divaricata
Wahlenbergia divergens
Wahlenbergia doleritica
Wahlenbergia dunantii
Wahlenbergia ecklonii
Wahlenbergia elongata
Wahlenbergia ensifolia
Wahlenbergia epacridea
Wahlenbergia erecta
Wahlenbergia ericoidella
Wahlenbergia exilis
Wahlenbergia fasciculata
Wahlenbergia fernandeziana
Wahlenbergia filipes
Wahlenbergia flexuosa
Wahlenbergia floribunda
Wahlenbergia fluminalis
Wahlenbergia fruticosa
Wahlenbergia galpiniae
Wahlenbergia globularis
Wahlenbergia gloriosa
Wahlenbergia gracilenta
Wahlenbergia gracilis
Wahlenbergia grandiflora
Wahlenbergia graniticola
Wahlenbergia hirsuta
Wahlenbergia hookeri
Wahlenbergia humbertii
Wahlenbergia huttonii
Wahlenbergia ingrata
Wahlenbergia insulae-howei
Wahlenbergia intermedia
Wahlenbergia islensis
Wahlenbergia itatiaiensis
Wahlenbergia juncea
Wahlenbergia krebsii
Wahlenbergia larrainii
Wahlenbergia lasiocarpa
Wahlenbergia laxiflora
Wahlenbergia levynsiae
Wahlenbergia limnophylax
Wahlenbergia linarioides
Wahlenbergia linearis
Wahlenbergia linifolia
Wahlenbergia litticola
Wahlenbergia littoralis
Wahlenbergia littoricola
Wahlenbergia lobelioides
Wahlenbergia lobulata
Wahlenbergia loddigesii
Wahlenbergia longifolia
Wahlenbergia luteola
Wahlenbergia lycopodioides
Wahlenbergia macrostachys
Wahlenbergia madagascariensis
Wahlenbergia magaliesbergensis
Wahlenbergia malaissei
Wahlenbergia marginata
Wahlenbergia marunguensis
Wahlenbergia masafuerae
Wahlenbergia massonii
Wahlenbergia matthewsii
Wahlenbergia melanops
Wahlenbergia meyeri
Wahlenbergia microphylla
Wahlenbergia minuta
Wahlenbergia mollis
Wahlenbergia multicaulis
Wahlenbergia namaquana
Wahlenbergia nana
Wahlenbergia napiformis
Wahlenbergia neorigida
Wahlenbergia neostricta
Wahlenbergia nodosa
Wahlenbergia obovata
Wahlenbergia oligantha
Wahlenbergia oocarpa
Wahlenbergia orae
Wahlenbergia oxyphylla
Wahlenbergia pallidiflora
Wahlenbergia paludicola
Wahlenbergia paniculata
Wahlenbergia parvifolia
Wahlenbergia patula
Wahlenbergia paucidentata
Wahlenbergia peduncularis
Wahlenbergia perrieri
Wahlenbergia perrottetii
Wahlenbergia persimilis
Wahlenbergia peruviana
Wahlenbergia petraea
Wahlenbergia pinifolia
Wahlenbergia pinnata
Wahlenbergia planiflora
Wahlenbergia polyantha
Wahlenbergia polycephala
Wahlenbergia polyclada
Wahlenbergia polytrichifolia
Wahlenbergia preissii
Wahlenbergia procumbens
Wahlenbergia prostrata
Wahlenbergia psammophila
Wahlenbergia pseudoandrosacea
Wahlenbergia pseudonudicaulis
Wahlenbergia pulchella
Wahlenbergia pulvillus-gigantis
Wahlenbergia pusilla
Wahlenbergia pygmaea
Wahlenbergia pyrophila
Wahlenbergia queenslandica
Wahlenbergia ramifera
Wahlenbergia ramosa
Wahlenbergia ramosissima
Wahlenbergia reflexa
Wahlenbergia rhytidosperma
Wahlenbergia riversdalensis
Wahlenbergia rivularis
Wahlenbergia roelliflora
Wahlenbergia roxburghii
Wahlenbergia rubens
Wahlenbergia rubioides
Wahlenbergia rudis
Wahlenbergia rupestris
Wahlenbergia rupicola
Wahlenbergia saxicola
Wahlenbergia schimperi
Wahlenbergia schistacea
Wahlenbergia schlechteri
Wahlenbergia Schrad. ex Roth
Wahlenbergia Schumach.
Wahlenbergia schwackeana
Wahlenbergia scopella
Wahlenbergia scottii
Wahlenbergia serpentina
Wahlenbergia sessiliflora
Wahlenbergia sessilis
Wahlenbergia silenoides
Wahlenbergia solitaria
Wahlenbergia sonderi
Wahlenbergia songeana
Wahlenbergia spinulosa
Wahlenbergia squamifolia
Wahlenbergia squarrosa
Wahlenbergia stellarioides
Wahlenbergia stricta
Wahlenbergia subaphylla
Wahlenbergia subfusiformis
Wahlenbergia subpilosa
Wahlenbergia subrosulata
Wahlenbergia subulata
Wahlenbergia suffruticosa
Wahlenbergia tenella
Wahlenbergia tenuiloba
Wahlenbergia thulinii
Wahlenbergia thunbergiana
Wahlenbergia thunbergii
Wahlenbergia tibestica
Wahlenbergia tomentosula
Wahlenbergia tortilis
Wahlenbergia transvaalensis
Wahlenbergia tuberosa
Wahlenbergia tumidifructa
Wahlenbergia umbellata
Wahlenbergia undulata
Wahlenbergia unidentata
Wahlenbergia upembensis
Wahlenbergia urcosensis
Wahlenbergia variabilis
Wahlenbergia verbascoides
Wahlenbergia vernicosa
Wahlenbergia victoriensis
Wahlenbergia violacea
Wahlenbergia virgata
Wahlenbergia virgulta
Wahlenbergia wittei
Wahlenbergia wyleyana
Wahpia C.D.Walcott, 1919
Wairarapaia mildenhallii
Waireia D.L.Jones, Molloy & M.A.Clem.
Waireia stenopetala
Waitzia acuminata
Waitzia aurea
Waitzia corymbosa
Waitzia fitzgibbonii
Waitzia nitida
Waitzia podolepis
Waitzia steetziana
Waitzia suaveolens
Wajira albescens
Wajira danissana
Wajira grahamiana
Wajira praecox
Wajira Thulin
Wajira virescens
Walafrida E.Mey.
Walchia longifolius
Walchia Sternberg, 1825
Walchiaceae
Walchianthus cylindraceus
Walchiopremnon R.Florin, 1940
Walchiopremnon valdajolense
Walchiostrobus Florin, 1940
Waldenburgia corynepteroides
Waldheimia Kar. & Kir.
Waldoia antillana
Waldoia W.R.Taylor, 1962
Waldsteinia Willd.
Walkera integrifolia
Walkeripollis J.A.Doyle, C.L.Hotton & J.V.Ward, 1990
Walkomia australis
Wallacea insignis
Wallacea multiflora
Wallaceodendron celebicum
Wallaceodendron Koord.
Wallaceodoxa raja-ampat
Wallenia apiculata
Wallenia aquifolia
Wallenia bumelioides
Wallenia calyptrata
Wallenia crassifolia
Wallenia ekmanii
Wallenia elliptica
Wallenia erythrocarpa
Wallenia fawcettii
Wallenia gracilis
Wallenia hughsonii
Wallenia ilicifolia
Wallenia jacquinioides
Wallenia lamarckiana
Wallenia laurifolia
Wallenia maestrensis
Wallenia punctulata
Wallenia purdieana
Wallenia subverticillata
Wallenia Sw.
Wallenia sylvestris
Wallenia urbaniana
Wallenia venosa
Wallenia xylosteoides
Wallenia yunquensis
Walleria gracilis
Walleria J.Kirk
Walleria mackenziei
Walleria mackenzii
Walleria nutans
Wallia Alef.
Wallichia caryotoides
Wallichia DC.
Wallichia disticha
Wallichia gracilis
Wallichia lidiae
Wallichia marianneae
Wallichia marianniae
Wallichia nana
Wallichia oblongifolia
Wallichia Reinw. ex Blume
Wallichia Roxb.
Wallichia triandra
Wallisia (Regel) É.Morren
Wallisia anceps
Wallisia cyanea
Wallisia duvalii
Wallisia lindeniana
Wallisia pretiosa
Wallrothia Spreng.
Walshia kendallii
Walsholaria calcarea
Walsholaria cuneifolia
Walsholaria magniflora
Walsholaria muelleri
Walsura candollei
Walsura decipiens
Walsura dehiscens
Walsura gardneri
Walsura monophylla
Walsura oxycarpa
Walsura pachycaulon
Walsura pinnata
Walsura poilanei
Walsura robusta
Walsura Roxb.
Walsura sarawakensis
Walsura temrifolia
Walsura trichostemon
Walsura trifoliata
Walsura trifoliolata
Walsura tubulata
Walsura villosa
Walteranthus erectus
Waltheria ackermanniana
Waltheria acuminata
Waltheria albicans
Waltheria arenaria
Waltheria arenicola
Waltheria bahamensis
Waltheria belizensis
Waltheria berteroi
Waltheria bicolor
Waltheria biribiriensis
Waltheria brachypetala
Waltheria bracteosa
Waltheria calcicola
Waltheria capitata
Waltheria cinerascens
Waltheria cinerescens
Waltheria collina
Waltheria communis
Waltheria coriacea
Waltheria excelsa
Waltheria fauriei
Waltheria flavovirens
Waltheria fryxellii
Waltheria glabra
Waltheria glabribracteata
Waltheria glazioviana
Waltheria glomerata
Waltheria hoehnei
Waltheria incana
Waltheria indica
Waltheria involucrata
Waltheria ladewii
Waltheria lanceolata
Waltheria longifolia
Waltheria macrophylla
Waltheria madagascariensis
Waltheria marielleae
Waltheria maritima
Waltheria martiana
Waltheria matogrossensis
Waltheria melochioides
Waltheria microphylla
Waltheria operculata
Waltheria ovata
Waltheria polyantha
Waltheria pringlei
Waltheria procumbens
Waltheria regnellii
Waltheria rotundifolia
Waltheria saundersiae
Waltheria scabra
Waltheria surinamensis
Waltheria terminans
Waltheria tomentosa
Waltheria tridentata
Waltheria vernonioides
Waltheria virgata
Waltheria viscosissima
Waltillia hatschbachii
Waltzispora F.L.Staplin, 1960
Walwhalleya jacobsiana
Walwhalleya proluta
Walwhalleya subxerophila
Wamalchitamia appressipila
Wamalchitamia aurantiaca
Wamalchitamia dionysi
Wamalchitamia strigosa
Wamalchitamia Strother
Wamalchitamia williamsii
Wandersong exserta
Wandersong seminervis
Wangenheimia lima
Wangenheimia Moench
Wangsania insolens
Wankiea bondii
Waputikia ramosa
Warburgia elongata
Warburgia Engl.
Warburgia salutaris
Warburgia stuhlmannii
Warburgia ugandensis
Warburgiella bistrumosa
Warburgiella celebensis
Warburgiella circinata
Warburgiella cuspidatifolia
Warburgiella falcatula
Warburgiella filicuspis
Warburgiella hygrophila
Warburgiella isopterygioides
Warburgiella kjelbergii
Warburgiella leptocarpos
Warburgiella leptorhynchoides
Warburgiella leptorrhyncha
Warburgiella leucocytus
Warburgiella Müll.Hal.
Warburgiella perfalcata
Warburgiella perviridis
Warburgiella pycnophylla
Warburgiella subleptorrhyncha
Warburgiella subpycnophylla
Warburgina Eig
Warczewiczella amazonica
Warczewiczella candida
Warczewiczella discolor
Warczewiczella guianensis
Warczewiczella ionoleuca
Warczewiczella lipscombiae
Warczewiczella lobata
Warczewiczella marginata
Warczewiczella palatina
Warczewiczella Rchb.f.
Warczewiczella timbiensis
Warczewiczella wailesiana
Wardensheppeya Eyde, 1970
Wardia Harv. & Hook.
Wardia hygrometrica
Wardia White, 1904
Wardiaphyllum daturaefolium
Warea amplexifolia
Warea carteri
Warea cuneifolia
Warea Nutt.
Warea sessilifolia
Warionia Benth. & Coss.
Warionia saharae
Warmingia buchtienii
Warmingia eugenii
Warmingia Rchb.f.
Warmingia zamorana
Warneckea albiflora
Warneckea amaniensis
Warneckea anomala
Warneckea atrovirens
Warneckea austrooccidentalis
Warneckea bebaiensis
Warneckea bequaertii
Warneckea bullata
Warneckea cinnamomoides
Warneckea cordiformis
Warneckea erubescens
Warneckea fascicularis
Warneckea floribunda
Warneckea Gilg
Warneckea gilletii
Warneckea golaensis
Warneckea guineensis
Warneckea jasminoides
Warneckea lecomteana
Warneckea madagascariensis
Warneckea melindensis
Warneckea membranifolia
Warneckea memecyloides
Warneckea microphylla
Warneckea mouririfolia
Warneckea ngutiensis
Warneckea peculiaris
Warneckea pulcherrima
Warneckea pulviniflora
Warneckea reygaertii
Warneckea sansibarica
Warneckea sapinii
Warneckea schliebenii
Warneckea sessilicarpa
Warneckea sousae
Warneckea trinervis
Warneckea urschii
Warneckea walikalensis
Warneckea wildeana
Warneckea yangambensis
Warneckia
Warneria Mill.
Warnockia M.W.Turner
Warnockia scutellarioides
Warnstorfia fluitans
Warnstorfia fontinaliopsis
Warnstorfia Loeske
Warnstorfia pseudostraminea
Warrea costaricensis
Warrea hookeriana
Warrea Lindl.
Warrea rubroglossa
Warrea warreana
Warreella cyanea
Warreella Schltr.
Warrenia comosa
Warrenia Harvey ex F.Schmitz & Hauptfleisch, 1897
Warreopsis colorata
Warreopsis pardina
Warreopsis parviflora
Warreopsis purpurea
Warscaea Szlach.
Warscewiczella
Warscewiczia
Warsteinia N.P.Rowe, 1997
Warszewiczia ambigua
Warszewiczia coccinea
Warszewiczia elata
Warszewiczia Klotzsch
Warszewiczia longistaminea
Warszewiczia peltata
Warszewiczia schwackei
Warszewiczia tomentosa
Warszewiczia uxpanapensis
Wasabia Matsum.
Wasatchia M.E.Jones
Washingtonia filibusta
Washingtonia filifera
Washingtonia H.Wendl.
Washingtonia Raf.
Washingtonia robusta
Watanabea N.Hanagata, I.Karube, M.Chihara & P.C.Silva, 1998
Wataria K.Terada & M.Suzuki, 1998
Watsonia
Watsonia aletroides
Watsonia amabilis
Watsonia amatolae
Watsonia angusta
Watsonia bachmannii
Watsonia bella
Watsonia Boehm.
Watsonia borbonica
Watsonia canaliculata
Watsonia coccinea
Watsonia densiflora
Watsonia distans
Watsonia dubia
Watsonia elsiae
Watsonia emiliae
Watsonia fergusoniae
Watsonia fourcadei
Watsonia fulgens
Watsonia galpinii
Watsonia gladioloides
Watsonia humilis
Watsonia hybr
Watsonia hysterantha
Watsonia iridifolia
Watsonia knysnana
Watsonia laccata
Watsonia latifolia
Watsonia lepida
Watsonia marginata
Watsonia meriana
Watsonia Mill.
Watsonia minima
Watsonia mtamvunae
Watsonia paucifolia
Watsonia pillansii
Watsonia pondoensis
Watsonia pulchra
Watsonia rogersii
Watsonia rourkei
Watsonia schlechteri
Watsonia spectabilis
Watsonia stenosiphon
Watsonia stricta
Watsonia strictiflora
Watsonia strubeniae
Watsonia tabularis
Watsonia tubulosa
Watsonia vanderspuyae
Watsonia vicschuettei
Watsonia watsonioides
Watsonia wilmaniae
Watsonia zeyheri
Wattakaka Hassk.
Wattia texana
Wattieza F.Stockmans, 1968
Weatherbya Copel.
Webera corymbosa
Webera Cramer
Webera denticostata
Webera firmo-acuminata
Webera Hedw.
Webera Schreb.
Webera striatidens
Webera synoica
Webera taylorii
Webera tetrandra
Weberbauera arequipa
Weberbauera ayacuchoensis
Weberbauera bracteata
Weberbauera cymosa
Weberbauera densifolia
Weberbauera dillonii
Weberbauera herzogii
Weberbauera incisa
Weberbauera minutipila
Weberbauera perforata
Weberbauera peruviana
Weberbauera rosulans
Weberbauera smithii
Weberbauera spathulifolia
Weberbauera trichocarpa
Weberbauera violacea
Weberbauerella brongniartioides
Weberbauerella raimondiana
Weberbauerocereus albus
Weberbauerocereus Backeb.
Weberbauerocereus callanus
Weberbauerocereus cephalomacrostibas
Weberbauerocereus cuzcoensis
Weberbauerocereus rauhii
Weberbauerocereus weberbaueri
Weberbauerocereus winterianus
Weberella F.Schmitz, 1896
Weberocereus bradei
Weberocereus Britton & Rose
Weberocereus frohningiorum
Weberocereus glaber
Weberocereus imitans
Weberocereus rosei
Weberocereus trichophorus
Weberocereus tunilla
Webervanbossea G.De Toni, 1936
Webervanbossea kaliformis
Webervanbossea splachnoides
Webervanbossea tasmanensis
Websteria S.H.Wright
Weda fragarioides
Weda lutea
Weda Welzen
Weddellina squamulosa
Wedelia acapulcensis
Wedelia aequitoreale
Wedelia aggregata
Wedelia alagoensis
Wedelia albicaulis
Wedelia almedae
Wedelia ambigens
Wedelia andersonii
Wedelia angustifolia
Wedelia asperrima
Wedelia attenuata
Wedelia aurantiaca
Wedelia avilensis
Wedelia bahamensis
Wedelia bahiensis
Wedelia baorucana
Wedelia bishopii
Wedelia bishoplecta
Wedelia bonplandiana
Wedelia calycina
Wedelia camporum
Wedelia cardenasii
Wedelia chihuahuana
Wedelia comaxillaris
Wedelia cordiformis
Wedelia cronquistii
Wedelia cylindrocephala
Wedelia diffusiflora
Wedelia ehrenbergii
Wedelia elata
Wedelia elliptica
Wedelia elottiana
Wedelia episcopalis
Wedelia equatorialis
Wedelia filipes
Wedelia floribunda
Wedelia foliacea
Wedelia forbesii
Wedelia frioana
Wedelia fructicosa
Wedelia frustrata
Wedelia frutescens
Wedelia fruticosa
Wedelia gardneri
Wedelia gaudichaudii
Wedelia gentryi
Wedelia gonzaleziarum
Wedelia goyazensis
Wedelia grandiflora
Wedelia grayi
Wedelia greenmanii
Wedelia hassleriana
Wedelia heringeri
Wedelia heringeriana
Wedelia hintoniorum
Wedelia hispidula
Wedelia hoffmanniana
Wedelia holwayi
Wedelia homogama
Wedelia hookeriana
Wedelia iners
Wedelia isolepis
Wedelia Jacq.
Wedelia jugata
Wedelia karwinskiana
Wedelia keilii
Wedelia kerrii
Wedelia kirkbridei
Wedelia laevissima
Wedelia leucanthema
Wedelia leucoglossa
Wedelia ligulifolia
Wedelia longifolia
Wedelia loxensis
Wedelia lundii
Wedelia macedoi
Wedelia macrodonta
Wedelia martii
Wedelia mexicana
Wedelia modesta
Wedelia mollis
Wedelia monantha
Wedelia montevidensis
Wedelia oligocephala
Wedelia ovalifolia
Wedelia oxylepis
Wedelia pallida
Wedelia pascalioides
Wedelia pauciflora
Wedelia penninervia
Wedelia pertenuis
Wedelia phyllostachya
Wedelia pimana
Wedelia podophylla
Wedelia procumbens
Wedelia pseudoyedaea
Wedelia puberula
Wedelia purpurea
Wedelia radiosa
Wedelia reflexa
Wedelia reticulata
Wedelia riedellii
Wedelia rosei
Wedelia rudis
Wedelia rugosa
Wedelia saltensis
Wedelia scandens
Wedelia serrata
Wedelia serrulata
Wedelia silphioides
Wedelia simpsoniae
Wedelia simsioides
Wedelia souzae
Wedelia squarrosa
Wedelia strigosa
Wedelia strigulosa
Wedelia stuebelii
Wedelia subalpestris
Wedelia subpetiolata
Wedelia subvelutina
Wedelia tambilloana
Wedelia tehuantepecana
Wedelia tenuicaulis
Wedelia tenuifolia
Wedelia tomentosa
Wedelia trichostephia
Wedelia triloba
Wedelia urbanii
Wedelia urticaefolia
Wedelia vauthieri
Wedelia veadeirosensis
Wedelia vexata
Wedelia vieirae
Wedelia villosa
Wedelia warmingii
Wedelia xylopoda
Wedeliella Cockerell
Weeksia coccinea
Weeksia howellii
Weeksia reticulata
Weeksia Setchell, 1901
Weeksiaceae
Wehlia F.Muell.
Weichselia ludovicae
Weichselia Stiehler, 1857
Weigela
Weigela amabilis
Weigela candida
Weigela coraeensis
Weigela decora
Weigela floribunda
Weigela florida
Weigela fujisanensis
Weigela hakonensis
Weigela hortensis
Weigela hybrida
Weigela japonica
Weigela maximowiczii
Weigela middendorffiana
Weigela middendorfiana
Weigela styriaca
Weigela suavis
Weigela subsessilis
Weigela Thunb.
Weigela wagneri
Weigelia amagiensis
Weigelia floribunda
Weigelia hybrida
Weigelia Pers., 1805
Weigeltia A.DC.
Weihea Eckl.
Weihea natalica
Weihea Spreng.
Weingaertneria Bernh.
Weingaertneria deschampsiodes
Weingartia arenacea
Weingartia azurduyensis
Weingartia breviflora
Weingartia canigueralii
Weingartia cardenasiana
Weingartia cylindrica
Weingartia fidaiana
Weingartia glomeriseta
Weingartia krugerae
Weingartia lanata
Weingartia margarethae
Weingartia mentosa
Weingartia neocumingii
Weingartia neumanniana
Weingartia oligacantha
Weingartia pulchra
Weingartia purpurea
Weingartia steinbachii
Weingartia tiraquensis
Weingartia vasqueziana
Weingartia Werderm.
Weingartneria Benth., 1881
Weinmannia anisophylla
Weinmannia apurimacensis
Weinmannia auriculata
Weinmannia auriformis
Weinmannia baccariniana
Weinmannia balbisana
Weinmannia bangii
Weinmannia biviniana
Weinmannia boliviensis
Weinmannia bradfordiana
Weinmannia burserifolia
Weinmannia chryseis
Weinmannia cinerea
Weinmannia cochensis
Weinmannia cogolloi
Weinmannia condorensis
Weinmannia cordata
Weinmannia corocoroensis
Weinmannia costulata
Weinmannia crassifolia
Weinmannia cundinamarcensis
Weinmannia cymbifolia
Weinmannia davidsonii
Weinmannia descendens
Weinmannia discolor
Weinmannia dzieduszyckii
Weinmannia elliptica
Weinmannia epicae
Weinmannia fagaroides
Weinmannia geometrica
Weinmannia glabra
Weinmannia glomerata
Weinmannia guyanensis
Weinmannia haenkeana
Weinmannia heterophylla
Weinmannia horrida
Weinmannia humblotii
Weinmannia humilis
Weinmannia ibaguensis
Weinmannia ilutepuiensis
Weinmannia integrifolia
Weinmannia jahnii
Weinmannia jelskii
Weinmannia karsteniana
Weinmannia kunthiana
Weinmannia L.
Weinmannia lansbergiana
Weinmannia latifolia
Weinmannia laxiramea
Weinmannia lechleriana
Weinmannia lentiscifolia
Weinmannia lesquereuxi
Weinmannia lopezana
Weinmannia loxensis
Weinmannia lyrata
Weinmannia machupicchuensis
Weinmannia macrophylla
Weinmannia macrostachya
Weinmannia madagascariensis
Weinmannia mariquitae
Weinmannia mauritiana
Weinmannia microphylla
Weinmannia multijuga
Weinmannia obtusifolia
Weinmannia organensis
Weinmannia ovata
Weinmannia oxapampana
Weinmannia parviflora
Weinmannia parvifoliolata
Weinmannia paullinifolia
Weinmannia paulliniifolia
Weinmannia pentaphylla
Weinmannia pinnata
Weinmannia piurensis
Weinmannia polyphylla
Weinmannia portlandiana
Weinmannia pubescens
Weinmannia reticulata
Weinmannia rhodoxylon
Weinmannia rhoifolia
Weinmannia rollottii
Weinmannia silvicola
Weinmannia sorbifolia
Weinmannia spruceana
Weinmannia stenocarpa
Weinmannia subsessiliflora
Weinmannia ternata
Weinmannia testudineata
Weinmannia tinctoria
Weinmannia tomentosa
Weinmannia trianae
Weinmannia trianaea
Weinmannia trichosperma
Weinmannia trifoliata
Weinmannia ulei
Weinmannia velutina
Weinmannia vulcanicola
Weinmannia wurdackii
Weinmannia yungasensis
Weinmanniaphyllum bernardii
Weinmannioxylon B.Petriella, 1972
Weinmannioxylon multiperforatum
Weinmannioxylon pluriradiatum
Weisiopsis anomala
Weisiopsis Broth.
Weisiopsis nigeriana
Weisiopsis norrisii
Weisiopsis oblonga
Weisiopsis plicata
Weissia abbreviata
Weissia angustifolia
Weissia argentinica
Weissia armata
Weissia artocosana
Weissia ayresii
Weissia balansae
Weissia balansaeana
Weissia balansana
Weissia bizotii
Weissia borbonica
Weissia brachycarpa
Weissia brachypoma
Weissia breutelii
Weissia caespitosa
Weissia condensa
Weissia controversa
Weissia cucullata
Weissia dieterlenii
Weissia diffidentia
Weissia edentula
Weissia erythrogona
Weissia exserta
Weissia felipponei
Weissia fornicata
Weissia francii
Weissia ghatensis
Weissia Hedw.
Weissia humicola
Weissia inoperculata
Weissia jamaicensis
Weissia jamesonii
Weissia japonica
Weissia kentuckiense
Weissia kunzeana
Weissia latiuscula
Weissia leiodonta
Weissia leptocarpa
Weissia leratii
Weissia levieri
Weissia ligulaefolia
Weissia ligulifolia
Weissia longidens
Weissia longifolia
Weissia lorentzii
Weissia ludoviciana
Weissia macrocarpa
Weissia micacea
Weissia minuta
Weissia mittenii
Weissia muhlenbergiana
Weissia neocaledonica
Weissia newcomeri
Weissia norkettii
Weissia occidentalis
Weissia ovalis
Weissia ovatifolia
Weissia parajaponica
Weissia patula
Weissia perpusilla
Weissia perssonii
Weissia phascopsis
Weissia platystegia
Weissia ricciae
Weissia riograndensis
Weissia rostellata
Weissia rutilans
Weissia semidiaphana
Weissia semiinvoluta
Weissia sharpii
Weissia socotrana
Weissia squarrosa
Weissia sterilis
Weissia subacaulis
Weissia termitidarum
Weissia veviridis
Weissia waymouthii
Weissia welwitschii
Weissia willisiana
Weissia wilsonii
Weissia wimmerana
Weissia wimmeriana
Weissiaceae
Weissiodicranum insularum
Welchiodendron longivalve
Welchiodendron Paul G.Wilson & J.T.Waterh.
Weldenia candida
Weldenia Schult.f.
Weldenia volcanica
Welfia alfredii
Welfia regia
Wellingtonia Meisn.
Wellstedia dinteri
Wellstedia filtuensis
Wellstedia laciniata
Wellstedia socotrana
Wellstedia somalensis
Weltrichia C.F.W.Braun, 1847
Weltrichia mirabilis
Welwitschia mirabilis
Welwitschia Rchb.
Welwitschiaceae
Welwitschiapites Bolkhovitina
Welwitschiella neriifolia
Welwitschiella O.Hoffm.
Welwitschiophyllum D.L.Dilcher, M.E.Bernardes de Oliveira, D.Pons & T.A.Lott, 2005
Welwitschiostrobus D.L.Dilcher, M.E.Bernardes de Oliveira, D.Pons & T.A.Lott, 2005
Wenchengia alternifolia
Wenchengia C.Y.Wu & S.Chow
Wendelboa Soest
Wendlandia aberrans
Wendlandia acuminata
Wendlandia amocana
Wendlandia andamanica
Wendlandia appendiculata
Wendlandia arabica
Wendlandia arborescens
Wendlandia augustini
Wendlandia bicuspidata
Wendlandia bouvardioides
Wendlandia brachyantha
Wendlandia brevipaniculata
Wendlandia brevituba
Wendlandia buddleacea
Wendlandia budleioides
Wendlandia burkillii
Wendlandia cambodiana
Wendlandia cavaleriei
Wendlandia connata
Wendlandia coriacea
Wendlandia dasythyrsa
Wendlandia densiflora
Wendlandia erythroxylon
Wendlandia ferruginea
Wendlandia formosana
Wendlandia fulva
Wendlandia gamblei
Wendlandia glabrata
Wendlandia guangdongensis
Wendlandia heyneana
Wendlandia heynei
Wendlandia inclusa
Wendlandia jingdongensis
Wendlandia junghuhniana
Wendlandia lauterbachii
Wendlandia laxa
Wendlandia ligustrina
Wendlandia ligustroides
Wendlandia litseifolia
Wendlandia longidens
Wendlandia longipedicellata
Wendlandia luzoniensis
Wendlandia merrilliana
Wendlandia myriantha
Wendlandia nervosa
Wendlandia nitens
Wendlandia nobilis
Wendlandia notoniana
Wendlandia oligantha
Wendlandia ovata
Wendlandia paedicalyx
Wendlandia paniculata
Wendlandia pendula
Wendlandia philippinensis
Wendlandia proxima
Wendlandia psychotrioides
Wendlandia puberula
Wendlandia pubigera
Wendlandia salicifolia
Wendlandia scabra
Wendlandia sibuyanensis
Wendlandia sikkimensis
Wendlandia speciosa
Wendlandia subalpina
Wendlandia syringoides
Wendlandia ternifolia
Wendlandia teysmanniana
Wendlandia thorelii
Wendlandia thyrsoidea
Wendlandia tinctoria
Wendlandia tonkiniana
Wendlandia urceolata
Wendlandia uvariifolia
Wendlandia villosa
Wendlandia wallichii
Wendlandia Willd.
Wendlandiella Dammer
Wendlandiella gracilis
Wendtia aphanifolia
Wendtia calycina
Wendtia gracilis
Wendtia Meyen
Wendtia miniata
Wendya incisa
Wenzelia archboldiana
Wenzelia brevipes
Wenzelia dolichophylla
Wenzelia kambarae
Wenzelia melanesica
Wenzelia platysperma
Wenzelia tenuifolia
Werauhia acuminata
Werauhia ampla
Werauhia anitana
Werauhia apiculata
Werauhia attenuata
Werauhia balanophora
Werauhia barii
Werauhia bicolor
Werauhia boliviana
Werauhia bracteosa
Werauhia broadwayi
Werauhia brunei
Werauhia burgeri
Werauhia camptoclada
Werauhia capitata
Werauhia comata
Werauhia cowellii
Werauhia dalstroemii
Werauhia diantha
Werauhia dodsonii
Werauhia gibba
Werauhia gigantea
Werauhia gladioliflora
Werauhia graminifolia
Werauhia guadelupensis
Werauhia haberi
Werauhia hainesiorum
Werauhia haltonii
Werauhia haplostachya
Werauhia hygrometrica
Werauhia insignis
Werauhia J.R.Grant
Werauhia kathyae
Werauhia kupperiana
Werauhia latissima
Werauhia laxa
Werauhia leucophylla
Werauhia luctuosa
Werauhia luis-gomezii
Werauhia lutheri
Werauhia lyman-smithii
Werauhia macrantha
Werauhia macrochlamys
Werauhia maculata
Werauhia millennia
Werauhia montana
Werauhia moralesii
Werauhia noctiflorens
Werauhia notata
Werauhia nutans
Werauhia ochracea
Werauhia orjuelae
Werauhia ororiensis
Werauhia osaensis
Werauhia panamaensis
Werauhia paniculata
Werauhia patzeltii
Werauhia paupera
Werauhia pectinata
Werauhia pedicellata
Werauhia picta
Werauhia pittieri
Werauhia pycnantha
Werauhia ringens
Werauhia rubra
Werauhia rugosa
Werauhia sanguinolenta
Werauhia singuliflora
Werauhia sintenisii
Werauhia stenophylla
Werauhia subsecunda
Werauhia tarmaensis
Werauhia tiquirensis
Werauhia tonduziana
Werauhia umbrosa
Werauhia urbaniana
Werauhia uxoris
Werauhia vanhyningii
Werauhia vietoris
Werauhia viridiflora
Werauhia viridis
Werauhia vittata
Werauhia vulcanicola
Werauhia werckleana
Werauhia williamsii
Werauhia woodsoniana
Wercklea cocleana
Wercklea ferox
Wercklea flavovirens
Wercklea grandiflora
Wercklea horrida
Wercklea hottensis
Wercklea insignis
Wercklea intermedia
Wercklea lutea
Wercklea magnibracteata
Wercklea Pittier & Standl.
Wercklea pseudoferox
Wercklea tulipiflora
Wercklea woodsonii
Werdermannia pubescens
Werneria acerosa
Werneria amblydactyla
Werneria ciliolata
Werneria crassa
Werneria dactylophylla
Werneria decora
Werneria digitata
Werneria esquilachensis
Werneria funkiana
Werneria humilis
Werneria incisa
Werneria juniperina
Werneria Kunth
Werneria lorochaqui
Werneria marcida
Werneria nana
Werneria plantaginifolia
Werneria poposa
Werneria pseudodigitata
Werneria rigida
Werneria rosea
Werneria rosenii
Werneria sotarensis
Werneria staffordiae
Werneria weddellii
Westella botryoides
Westella De Wildeman, 1897
Westia Vahl
Westonia Spreng.
Westoniella barqueroana
Westoniella chirripoensis
Westoniella Cuatrec.
Westoniella eriocephala
Westoniella kohkemperi
Westoniella lanuginosa
Westoniella triunguifolia
Westringia amabilis
Westringia angustifolia
Westringia blakeana
Westringia brevifolia
Westringia capitonia
Westringia cephalantha
Westringia cheelii
Westringia crassifolia
Westringia cremnophila
Westringia dampieri
Westringia davidii
Westringia discipulorum
Westringia eremicola
Westringia fitzgeraldensis
Westringia fruticosa
Westringia glabra
Westringia grandifolia
Westringia longifolia
Westringia lucida
Westringia parvifolia
Westringia rigida
Westringia rosmariniformis
Westringia rupicola
Westringia saxatilis
Westringia Sm.
Westringia tenuicaulis
Westringia triphylla
Westringia viminalis
Wetherbeella australica
Wetherbeella foliosa
Wetherbeella G.W.Saunders & G.T.Kraft, 2002
Wetheredella A.Wood, 1948
Wetherellia marylandicus
Wetherellia variabilis
Wetria australiensis
Wetria insignis
Wettinia aequalis
Wettinia aequatorialis
Wettinia anomala
Wettinia augusta
Wettinia castanea
Wettinia disticha
Wettinia donosoensis
Wettinia drudei
Wettinia fascicularis
Wettinia hirsuta
Wettinia kalbreyeri
Wettinia lanata
Wettinia longipetala
Wettinia maynensis
Wettinia microcarpa
Wettinia minima
Wettinia oxycarpa
Wettinia panamensis
Wettinia Poepp.
Wettinia praemorsa
Wettinia quinaria
Wettinia radiata
Wettinia verruculosa
Wettsteinia densiretis
Wettsteinia inversa
Wettsteinia rotundifolia
Wettsteinia Schiffn.
Wettsteinia schusteriana
Wettsteiniola accorsii
Wettsteiniola apipensis
Wettsteiniola pinnata
Wettsteiniola Suess.
Wexfordia hookense
Weylandites D.C.Bharadwaj & S.C.Srivastava, 1969
Weymouthia Broth.
Weymouthia cochlearifolia
Weymouthia mollis
Wheeleroxylon atascosense
Whidbeyella cartilaginea
Whipplea modesta
Whitefieldia Nees, 1847
Whiteheadia Harv.
Whiteochloa airoides
Whiteochloa biciliata
Whiteochloa C.E.Hubb.
Whiteochloa capillipes
Whiteochloa cymbiformis
Whiteochloa Hann-River
Whiteochloa multiciliata
Whiteodendron moultonianum
Whiteodendron Steenis
Whitfieldia brazzaei
Whitfieldia colorata
Whitfieldia elongata
Whitfieldia Hook.
Whitfieldia lateritia
Whitfieldia latiflos
Whitfieldia laurentii
Whitfieldia liebrechtsiana
Whitfieldia orientalis
Whitfieldia preussii
Whitfieldia rutilans
Whitfieldia stuhlmannii
Whitfordiodendron Elmer
Whitfordiodendron erianthum
Whitfordiodendron nieuwenhuisii
Whitfordiodendron scandens
Whitfordiodendron sumatranum
Whitlavia Harv.
Whitmorea grandiflora
Whitneya A.Gray
Whittieria L.B.Zhang & L.Zhang, 2022
Whittleseya elegans
Whittleseya Newberry, 1853
Whittonia guianensis
Whyanbeelia terrae-reginae
Whytockia chiritiflora
Whytockia gongshanensis
Whytockia hekouensis
Whytockia purpurascens
Whytockia sasakii
Whytockia tsiangiana
Whytockia W.W.Sm.
Whytockia wilsonii
Wibelia Bernh.
Wiborgia armella
Wiborgia fusca
Wiborgia incurvata
Wiborgia leptoptera
Wiborgia monoptera
Wiborgia mucronata
Wiborgia obcordata
Wiborgia sericea
Wiborgia tenuifolia
Wiborgia tetraptera
Wiborgia Thunb.
Wiborgiella argentea
Wiborgiella Boatwr. & B.-E.van Wyk
Wiborgiella bowieana
Wiborgiella dahlgrenii
Wiborgiella fasciculata
Wiborgiella humilis
Wiborgiella inflata
Wiborgiella leipoldtiana
Wiborgiella mucronata
Wiborgiella sessilifolia
Wiborgiella vlokii
Wickstroemia Rchb., 1828
Widdringtonia cedarbergensis
Widdringtonia complanata
Widdringtonia linguaefolia
Widdringtonia nodiflora
Widdringtonia schwarzii
Widdringtonia whytei
Widdringtonioxylon P.Greguss, 1967
Widdringtonites Endlicher, 1847
Widdringtonites fasciculatus
Widdringtonites gracilis
Widdringtonites subtilis
Widdringtonites ungeri
Widgrenia Malme
Widjajachloa K.M.Wong & S.Dransf.
Widjajachloa producta
Wiedemannia Fisch. & C.A.Mey.
Wielandia angustifolia
Wielandia Baill.
Wielandia bemarensis
Wielandia bojeriana
Wielandia danguyana
Wielandia elegans
Wielandia fadenii
Wielandia laureola
Wielandia leandriana
Wielandia mimosoides
Wielandia oblongifolia
Wielandia platyrachis
Wielandia ranavalonae
Wielandia tanalorum
Wielandia unifex
Wielandiella A.G.Nathorst, 1910
Wiesnerella denudata
Wiesnerella fasciaria
Wiesneria filifolia
Wiesneria triandra
Wietersdorfia E.Knobloch & D.H.Mai, 1984
Wiganda St.-Lag.
Wigandia brevistyla
Wigandia ecuadorensis
Wigandia Kunth
Wigandia pruritiva
Wigandia urens
Wigandia wurdackiana
Wigginsia D.M.Porter
Wigginsia sessiflora
Wightia borneensis
Wightia speciosissima
Wijkia alboalaris
Wijkia annamensis
Wijkia baculifera
Wijkia bessonii
Wijkia carlottae
Wijkia ceylonensis
Wijkia clastobryoides
Wijkia comosa
Wijkia concavifolia
Wijkia cuynetii
Wijkia deflexifolia
Wijkia dentigera
Wijkia extenuata
Wijkia filifera
Wijkia filipendula
Wijkia flagellifera
Wijkia flagelliformis
Wijkia gracilis
Wijkia H.A.Crum
Wijkia hornschuchii
Wijkia jungneri
Wijkia laxa
Wijkia laxitexta
Wijkia lepida
Wijkia letestui
Wijkia macgregorii
Wijkia madagassa
Wijkia monodii
Wijkia nivea
Wijkia pallida
Wijkia pendula
Wijkia penicillata
Wijkia pinnata
Wijkia polymorpha
Wijkia protensa
Wijkia radiculosa
Wijkia rutenbergii
Wijkia subnitida
Wijkia surcularis
Wijkia tanytricha
Wijkia tanytrichoides
Wijkia trichocolea
Wijkia trichocoleoides
Wijkiella kenyae
Wikstroemia alberti
Wikstroemia albiflora
Wikstroemia alternifolia
Wikstroemia androsaemifolia
Wikstroemia angustifolia
Wikstroemia angustiloba
Wikstroemia anhuiensis
Wikstroemia aurantiaca
Wikstroemia axillaris
Wikstroemia baimashanensis
Wikstroemia bokorensis
Wikstroemia brachyantha
Wikstroemia canescens
Wikstroemia capitata
Wikstroemia capitellata
Wikstroemia chamaedaphne
Wikstroemia chuii
Wikstroemia cochlearifolia
Wikstroemia coriacea
Wikstroemia delavayi
Wikstroemia dolichantha
Wikstroemia domkeana
Wikstroemia Endl.
Wikstroemia fargesii
Wikstroemia farreri
Wikstroemia forbesii
Wikstroemia fragrans
Wikstroemia fuminensis
Wikstroemia furcata
Wikstroemia ganpi
Wikstroemia gemmata
Wikstroemia genkwa
Wikstroemia glabra
Wikstroemia gracilis
Wikstroemia guanxianensis
Wikstroemia hainanensis
Wikstroemia hanalei
Wikstroemia haoi
Wikstroemia holosericea
Wikstroemia indica
Wikstroemia jiulongensis
Wikstroemia johnplewsii
Wikstroemia kudoi
Wikstroemia lamatsoensis
Wikstroemia lanceolata
Wikstroemia leptophylla
Wikstroemia leuconeura
Wikstroemia liangii
Wikstroemia lichiangensis
Wikstroemia linoides
Wikstroemia meyeniana
Wikstroemia micrantha
Wikstroemia monnula
Wikstroemia mononectaria
Wikstroemia monticola
Wikstroemia myrtilloides
Wikstroemia nutans
Wikstroemia oahuensis
Wikstroemia ohsumiensis
Wikstroemia ovata
Wikstroemia pachyrachis
Wikstroemia pauciflora
Wikstroemia paxiana
Wikstroemia penicillata
Wikstroemia phymatoglossa
Wikstroemia pilosa
Wikstroemia poilanei
Wikstroemia polyantha
Wikstroemia pulcherrima
Wikstroemia raiateensis
Wikstroemia reginaldi-farreri
Wikstroemia retusa
Wikstroemia ridleyi
Wikstroemia rosmarinifolia
Wikstroemia salicina
Wikstroemia sandwicensis
Wikstroemia sandwichensis
Wikstroemia Schrad.
Wikstroemia scytophylla
Wikstroemia sikokiana
Wikstroemia sinoparviflora
Wikstroemia skottsbergiana
Wikstroemia souliei
Wikstroemia Spreng.
Wikstroemia stenophylla
Wikstroemia subcyclolepidota
Wikstroemia subspicata
Wikstroemia taiwanensis
Wikstroemia techinensis
Wikstroemia tenuiflora
Wikstroemia tenuiramis
Wikstroemia thibetensis
Wikstroemia trichotoma
Wikstroemia uva-ursi
Wikstroemia venosa
Wikstroemia villosa
Wikstroemia yakushimensis
Wikstroemia zhouana
Wilbrandia ebracteata
Wilbrandia glaziovii
Wilbrandia hibiscoides
Wilbrandia longisepala
Wilbrandia Silva Manso
Wilbrandia verticillata
Wilckea Scop.
Wilckia Scop.
Wilcoxia Britton & Rose
Wilczekra congolensis
Wilczekra gabonica
Wilczekra M.P.Simmons
Wildemania amplissima
Wildemania De Toni, 1890
Wildemania miniata
Wildemania occidentalis
Wildemania tenuissima
Wilhelmsia physodes
Wilhelmsia Rchb.
Wilkesia A.Gray
Wilkesia gymnoxiphium
Wilkesia hobdyi
Wilkiea angustifolia
Wilkiea cordata
Wilkiea F.Muell.
Wilkiea foremanii
Wilkiea huegeliana
Wilkiea hugeliana
Wilkiea hylandii
Wilkiea kaarruana
Wilkiea longipes
Wilkiea macrophylla
Wilkiea McDowall-Range
Wilkiea pubescens
Wilkiea rigidifolia
Wilkiea smithii
Willardia mexicana
Willdenovia J.F.Gmel.
Willdenowia arescens
Willdenowia bolusii
Willdenowia glomerata
Willdenowia humilis
Willdenowia incurvata
Willdenowia pilleata
Willdenowia purpurea
Willdenowia rugosa
Willdenowia stokoei
Willdenowia sulcata
Willdenowia teres
Willdenowia Thunb.
Willea
Willea apiculata
Willea crucifera
Willea irregularis
Willea neglecta
Willea rectangularis
Willea saguei
Willea Schmidle, 1900
Willea truncata
Willea vilhelmii
Willeella brachyclados
Willeella Børgesen, 1930
Willemetia Cass.
Willemetia stipitata
Willemetia tuberosa
Willia Müll.Hal.
Williamodendron cinnamomeum
Williamodendron glaucophyllum
Williamodendron itamarajuense
Williamodendron Kubitzki & Richter
Williamodendron quadrilocellatum
Williamodendron spectabile
Williamsonia gallinacea
Williamsonia gigas
Williamsonia marylandica
Williamsonia phoenicopsoides
Williamsonia texana
Williamsonia virginiensis
Williamsoniaceae
Williamsonianthus R.Kräusel & F.Schaarschmidt, 1966
Williamsoniella H.H.Thomas, 1915
Williamsoniella valdensis
Willisia arekaliana
Willisia rentonensis
Willisia selaginoides
Willkommia annua
Willkommia Hack.
Willkommia sarmentosa
Willkommia texana
Willoughbya coriacea
Willoughbya Neck. ex Ktze.
Willsiostrobus L.Grauvogel-Stamm & F.Schaarschmidt, 1978
Willugbaeya Neck.
Willugbaeya ranunculifolia
Willughbeia angustifolia
Willughbeia anomala
Willughbeia beccariana
Willughbeia cirrhifera
Willughbeia coriacea
Willughbeia edulis
Willughbeia flavescens
Willughbeia gigantea
Willughbeia globosa
Willughbeia grandiflora
Willughbeia javanica
Willughbeia kontumensis
Willughbeia lanceolata
Willughbeia oblonga
Willughbeia Roxb.
Willughbeia sarawacensis
Willughbeia Scop.
Willughbeia tenuiflora
Willungia maslinensis
Willungia oppositifolia
Wilsonaea dictyuroides
Wilsonaea F.Schmitz, 1893
Wilsonara Hort., 1916
Wilsonia backhousei
Wilsonia humilis
Wilsonia rotundifolia
Wilsonia sericea
Wilsoniella blindioides
Wilsoniella crispidens
Wilsoniella decipiens
Wilsoniella flaccida
Wilsoniella jardinii
Wilsoniella karsteniana
Wilsoniella Müll.Hal.
Wilsoniella subvaginans
Wilsoniella tonkinensis
Wilsonipites S.K.Srivastava, 1969
Wilsonites R.M.Kosanke, 1959
Wilsonosiphonia D.E.Bustamante, B.Y.Won & T.O.Cho, 2017
Wilsonosiphonia fujiae
Wilsonoxylon N.Boonchai & S.R.Manchester, 2012
Wimmeranthus inopinatus
Wimmerella arabidea
Wimmerella bifida
Wimmerella frontidentata
Wimmerella giftbergensis
Wimmerella hederacea
Wimmerella hedyotidea
Wimmerella longitubus
Wimmerella mariae
Wimmerella pygmaea
Wimmerella secunda
Wimmerella Serra, M.B.Crespo & Lammers
Wimmeria acuminata
Wimmeria bartlettii
Wimmeria concolor
Wimmeria confusa
Wimmeria cyclocarpa
Wimmeria excoriata
Wimmeria lanceolata
Wimmeria lundelliana
Wimmeria mexicana
Wimmeria microphylla
Wimmeria montana
Wimmeria obtusifolia
Wimmeria persicifolia
Wimmeria pubescens
Wimmeria Schltdl. & Cham.
Wimmeria sternii
Windsoria Nutt.
Windsorina guianensis
Windwardia crookallii
Wingatea plumosa
Wingia H.Wang & D.L.Dilcher, 2018
Winifredia sola
Winika M.A.Clem., D.L.Jones & Molloy
Winklera Regel
Winklerella dichotoma
Winslowia M.T.Dunn, P.Atkinson, J.Lacefield & M.Rischbieter, 2012
Winteraceae
Winterana aromatica
Winthropteris I.M.Miller & L.J.Hickey, 2008
Wireroadia X.Zhang, Y.Wang, D.L.Dilcher & S.R.Manchester, 2020
Wirtgenia abyssinica
Wirtgenia frutescens
Wislizenia Engelm.
Wislouchia E.A.Molinari-Novoa & M.D.Guiry, 2021
Wislouchiella planctonica
Wislouchiella Skvortzov, 1925
Wisneria Micheli, 1881
Wissadula amplissima
Wissadula andina
Wissadula cardenasii
Wissadula caribea
Wissadula contracta
Wissadula costaricensis
Wissadula cruziana
Wissadula cuspidata
Wissadula decora
Wissadula delicata
Wissadula densiflora
Wissadula ecuadoriensis
Wissadula excelsior
Wissadula fadyenii
Wissadula glechomatifolia
Wissadula glechomifolia
Wissadula grandifolia
Wissadula gymnanthemum
Wissadula hernandioides
Wissadula indivisa
Wissadula krapovickasiana
Wissadula Medik.
Wissadula microcalyx
Wissadula microcarpa
Wissadula parviflora
Wissadula parvifolia
Wissadula pavonii
Wissadula peredoi
Wissadula periplocifolia
Wissadula setifera
Wissadula sordida
Wissadula stellata
Wissadula stipulata
Wissadula subpeltata
Wissadula tucumanensis
Wissadula wissadifolia
Wisteria brachybotrya
Wisteria brachybotrys
Wisteria consequana
Wisteria floribunda
Wisteria formosa
Wisteria frutescens
Wisteria macrobotrys
Wisteria Nutt.
Wisteria sinensis
Wisteria ventusa
Wisteriopsis championii
Wisteriopsis eurybotrya
Wisteriopsis japonica
Wisteriopsis kiangsiensis
Wisteriopsis reticulata
Withania
Withania adpressa
Withania adunensis
Withania aristata
Withania begoniifolia
Withania coagulans
Withania frutescens
Withania grisea
Withania Pauquy
Withania qaraitica
Withania riebeckii
Withania somnifera
Witheringia asterotricha
Witheringia bristaniana
Witheringia coccoloboides
Witheringia hunzikeri
Witheringia L'Hér.
Witheringia laxissima
Witheringia macrophylla
Witheringia maculata
Witheringia meiantha
Witheringia mexicana
Witheringia mortonii
Witheringia solanacea
Witheringia stellata
Witheringia synanthera
Witheringia wurdackiana
Witsenia maura
Witsenia partita
Witsenia Thunb.
Wittia
Wittia K.Schum.
Wittmackanthus Kuntze
Wittmackanthus stanleyanus
Wittmackia abbreviata
Wittmackia altocaririensis
Wittmackia amorimii
Wittmackia andersoniana
Wittmackia antillana
Wittmackia bicolor
Wittmackia brasiliensis
Wittmackia burle-marxii
Wittmackia canaliculata
Wittmackia carvalhoi
Wittmackia caymanensis
Wittmackia distans
Wittmackia eriostachya
Wittmackia fawcettii
Wittmackia froesii
Wittmackia gregaria
Wittmackia guedesiae
Wittmackia incompta
Wittmackia inermis
Wittmackia ituberaensis
Wittmackia jamaicana
Wittmackia laesslei
Wittmackia laevigata
Wittmackia lingulata
Wittmackia lingulatoides
Wittmackia linharesiorum
Wittmackia maranguapensis
Wittmackia mesoamericana
Wittmackia Mez
Wittmackia negrilensis
Wittmackia neoregelioides
Wittmackia patentissima
Wittmackia penduliflora
Wittmackia pendulispica
Wittmackia pernambucentris
Wittmackia polycephala
Wittmackia portoricensis
Wittmackia rohan-estyi
Wittmackia silvana
Wittmackia spinulosa
Wittmackia sulbahianensis
Wittmackia tentaculifera
Wittmackia turbinocalyx
Wittmackia urbaniana
Wittrockia cyathiformis
Wittrockia flavipetala
Wittrockia gigantea
Wittrockia Lindm.
Wittrockia superba
Wittrockia tenuisepala
Wittrockiella amphibia
Wittrockiella lyallii
Wittrockiella salina
Wittrockiella Wille, 1909
Wittrockiellaceae
Wittsteinia F.Muell.
Wittsteinia papuana
Woburnia porosa
Wodyetia A.K.Irvine
Wodyetia bifurcata
Woelkerlingia G.Alongi, M.Cormaci & G.Furnari, 2007
Wolfeniana randolphensis
Wolffia angusta
Wolffia arrhiza
Wolffia australiana
Wolffia borealis
Wolffia brasiliensis
Wolffia columbiana
Wolffia cylindracea
Wolffia elongata
Wolffia globosa
Wolffia Horkel ex Schleid
Wolffia Horkel ex Scleid.
Wolffia microscopica
Wolffia neglecta
Wolffiella caudata
Wolffiella denticulata
Wolffiella gladiata
Wolffiella Hegelm.
Wolffiella hyalina
Wolffiella lingulata
Wolffiella neotropica
Wolffiella oblonga
Wolffiella repanda
Wolffiella rotunda
Wolffiella welwitschii
Wolfia
Wolfia Schreb.
Wolfiella
Wolfiophyllum D.L.Dilcher & H.S.Wang, 2006
Wollastonia biflora
Wollastonia DC. ex Decne.
Wollastonia elongata
Wollastonia glabrata
Wollastonia javana
Wollastonia lifuana
Wollastonia repens
Wollastonia uniflora
Wollastoniella mucronata
Wollastoniella myriophylloides
Wollemia W.G.Jones, K.D.Hill & J.M.Allen
Wollemiaster cordatus
Womerleyella
Womersleya monanthos
Womersleya Papenfuss, 1956
Womersleyella Hollenberg, 1967
Womersleyella setacea
Woodburnia penduliflora
Woodfordia fruticosa
Woodfordia uniflora
Woodia mucronata
Woodia Schltr.
Woodia singularis
Woodia verruculosa
Woodiellantha Rauschert
Woodiellantha sympetala
Woodsia alpina
Woodsia alpina × ilvensis
Woodsia andersonii
Woodsia asiatica
Woodsia burgessiana
Woodsia cycloloba
Woodsia glabella
Woodsia gorovoii
Woodsia gracilis
Woodsia guizhouensis
Woodsia hancockii
Woodsia ilvensis
Woodsia kansana
Woodsia kungiana
Woodsia lanosa
Woodsia macrochlaena
Woodsia macrospora
Woodsia oblonga
Woodsia okamotoi
Woodsia pallida
Woodsia pilosa
Woodsia polystichoides
Woodsia pseudopolystichoides
Woodsia pulchella
Woodsia R.Br.
Woodsia rosthorniana
Woodsia shensiensis
Woodsia sinica
Woodsia subcordata
Woodsia taigischensis
Woodsia taishanensis
Woodsia tryonis
Woodsimatium abbeae
Woodvillea incrassata
Woodwardia
Woodwardia arctica
Woodwardia auriculata
Woodwardia columbiana
Woodwardia crenata
Woodwardia fimbriata
Woodwardia florissantia
Woodwardia harlandii
Woodwardia intermedia
Woodwardia izuensis
Woodwardia J.E.Sm.
Woodwardia japonica
Woodwardia kempii
Woodwardia latiloba
Woodwardia lunulata
Woodwardia magnifica
Woodwardia martinezii
Woodwardia maxima
Woodwardia maxonii
Woodwardia omeiensis
Woodwardia orientalis
Woodwardia preareolata
Woodwardia prolifera
Woodwardia radicans
Woodwardia spinulosa
Woodwardia unigemmata
Woodwardites H.R.Göppert, 1836
Woodwardites microlobus
Woodworthia arizonica
Wooleya farinosa
Woollsia F.Muell.
Woollsia pungens
Wootonella Standl.
Wormia Rottb.
Wormia Vahl
Wormskioldia Sprengel, 1827
Wormskioldia Thonn.
Worsdellia bonettiae
Worsleya procera
Wrangelia abietina
Wrangelia argus
Wrangelia australis
Wrangelia bicuspidata
Wrangelia C.Agardh, 1828
Wrangelia clavigera
Wrangelia dumontii
Wrangelia gordoniae
Wrangelia halurus
Wrangelia nobilis
Wrangelia penicillata
Wrangelia plumosa
Wrangelia princeps
Wrangelia tanegana
Wrangelia velutina
Wrangelia wattsii
Wrangeliaceae
Wrightia angustifolia
Wrightia antidysenterica
Wrightia arborea
Wrightia calcicola
Wrightia coccinea
Wrightia collettii
Wrightia coraia
Wrightia demartiniana
Wrightia dubia
Wrightia filipendula
Wrightia flavidorosea
Wrightia hanleyi
Wrightia indica
Wrightia karaketii
Wrightia laevis
Wrightia lanceolata
Wrightia lecomtei
Wrightia natalensis
Wrightia novobritannica
Wrightia palawanensis
Wrightia poomae
Wrightia puberula
Wrightia pubescens
Wrightia R.Br.
Wrightia religiosa
Wrightia saligna
Wrightia saligna x Wrightia versicolor
Wrightia siamensis
Wrightia sikkimensis
Wrightia tinctoria
Wrightia tokiae
Wrightia versicolor
Wrightiella blodgetti
Wrightiella tumanowiczii
Wuacanthus microdontus
Wulfenia blecicii
Wulfenia carinthiaca
Wulfenia glanduligera
Wulfenia Jacq.
Wulfenia orientalis
Wulfenia schwarzii
Wulfeniopsis amherstiana
Wulfeniopsis nepalensis
Wulffia Neck. ex Cass.
Wulffia Neck., 1790
Wulffia stenoglossa
Wulfhorstia C.DC.
Wullschlaegelia aphylla
Wullschlaegelia calcarata
Wullschlaegelia Rchb.f.
Wunderlichia azulensis
Wunderlichia bahiensis
Wunderlichia cruelsiana
Wunderlichia crulsiana
Wunderlichia glaziovii
Wunderlichia insignis
Wunderlichia mirabilis
Wunderlichia Riedel ex Benth. & Hook.f.
Wunderlichia senaeii
Wurdastom B.Walln.
Wurdastom bullata
Wurdastom cuatrecasasii
Wurdastom dorrii
Wurdastom dudleyi
Wurdastom ecuadorense
Wurdastom hexamera
Wurdastom sneidernii
Wurdastom subglabra
Wurdemannia Harvey, 1853
Wurdemannia miniata
Wurdemanniaceae
Wurfbainia aromatica
Wurfbainia biflora
Wurfbainia blumeana
Wurfbainia compacta
Wurfbainia elegans
Wurfbainia glabrifolia
Wurfbainia gracilis
Wurfbainia graminea
Wurfbainia hedyosma
Wurfbainia jainii
Wurfbainia longiligularis
Wurfbainia micrantha
Wurfbainia microcarpa
Wurfbainia mindanaensis
Wurfbainia mollis
Wurfbainia neoaurantiaca
Wurfbainia quadratolaminaris
Wurfbainia schmidtii
Wurfbainia staminidiva
Wurfbainia tenella
Wurfbainia testacea
Wurfbainia uliginosa
Wurfbainia vera
Wurfbainia villosa
Wurmbaea Steud., 1841
Wurmbea angustifolia
Wurmbea australis
Wurmbea biglandulosa
Wurmbea burrowsii
Wurmbea burttii
Wurmbea capensis
Wurmbea centralis
Wurmbea compacta
Wurmbea decumbens
Wurmbea Denham-Pool
Wurmbea dioica
Wurmbea dolichantha
Wurmbea drummondii
Wurmbea elatior
Wurmbea fluviatilis
Wurmbea glassii
Wurmbea graniticola
Wurmbea Great-Victoria-Desert
Wurmbea hiemalis
Wurmbea inflata
Wurmbea inframediana
Wurmbea inusta
Wurmbea kraussii
Wurmbea latifolia
Wurmbea marginata
Wurmbea monantha
Wurmbea monopetala
Wurmbea murchisoniana
Wurmbea nilpinna
Wurmbea novae-zelandiae
Wurmbea odorata
Wurmbea punctata
Wurmbea purpurea
Wurmbea pusilla
Wurmbea robusta
Wurmbea saccata
Wurmbea sinora
Wurmbea spicata
Wurmbea stellata
Wurmbea stigmosa
Wurmbea stricta
Wurmbea tenella
Wurmbea tenuis
Wurmbea Thunb.
Wurmbea tubulosa
Wurmbea uniflora
Wurmbea Upper-Murchison
Wurmbea variabilis
Wydleria DC.
Wyethia amplexicaulis
Wyethia angustifolia
Wyethia arizonica
Wyethia cusickii
Wyethia glabra
Wyethia helenioides
Wyethia helianthoides
Wyethia mollis
Wyethia Nutt.
Wyethia sagittata
Wynneophycus S.Y.Jeong, B.Y.Won, Fredericq & T.O.Cho, 2016
Wyomingia A.Nelson""".strip().split("\n")

# ══════════════════════════════════════════════
#  LISTE DES PLANTES TOXIQUES
#  ⚠ À REMPLACER à chaque nouvelle lettre
#  → Mettre ici uniquement les noms présents
#    dans PLANTES qui sont toxiques.
#    Le nom doit être identique (même casse).
#  → Si aucune plante toxique : laisser []
# ══════════════════════════════════════════════

PLANTES_TOXIQUES = """Wikstroemia alberti
Wikstroemia albiflora
Wikstroemia alternifolia
Wikstroemia androsaemifolia
Wikstroemia angustifolia
Wikstroemia angustiloba
Wikstroemia anhuiensis
Wikstroemia aurantiaca
Wikstroemia axillaris
Wikstroemia baimashanensis
Wikstroemia bokorensis
Wikstroemia brachyantha
Wikstroemia canescens
Wikstroemia capitata
Wikstroemia capitellata
Wikstroemia chamaedaphne
Wikstroemia chuii
Wikstroemia cochlearifolia
Wikstroemia coriacea
Wikstroemia delavayi
Wikstroemia dolichantha
Wikstroemia domkeana
Wikstroemia Endl.
Wikstroemia fargesii
Wikstroemia farreri
Wikstroemia forbesii
Wikstroemia fragrans
Wikstroemia fuminensis
Wikstroemia furcata
Wikstroemia ganpi
Wikstroemia gemmata
Wikstroemia genkwa
Wikstroemia glabra
Wikstroemia gracilis
Wikstroemia guanxianensis
Wikstroemia hainanensis
Wikstroemia hanalei
Wikstroemia haoi
Wikstroemia holosericea
Wikstroemia indica
Wikstroemia jiulongensis
Wikstroemia johnplewsii
Wikstroemia kudoi
Wikstroemia lamatsoensis
Wikstroemia lanceolata
Wikstroemia leptophylla
Wikstroemia leuconeura
Wikstroemia liangii
Wikstroemia lichiangensis
Wikstroemia linoides
Wikstroemia meyeniana
Wikstroemia micrantha
Wikstroemia monnula
Wikstroemia mononectaria
Wikstroemia monticola
Wikstroemia myrtilloides
Wikstroemia nutans
Wikstroemia oahuensis
Wikstroemia ohsumiensis
Wikstroemia ovata
Wikstroemia pachyrachis
Wikstroemia pauciflora
Wikstroemia paxiana
Wikstroemia penicillata
Wikstroemia phymatoglossa
Wikstroemia pilosa
Wikstroemia poilanei
Wikstroemia polyantha
Wikstroemia pulcherrima
Wikstroemia raiateensis
Wikstroemia reginaldi-farreri
Wikstroemia retusa
Wikstroemia ridleyi
Wikstroemia rosmarinifolia
Wikstroemia salicina
Wikstroemia sandwicensis
Wikstroemia sandwichensis
Wikstroemia Schrad.
Wikstroemia scytophylla
Wikstroemia sikokiana
Wikstroemia sinoparviflora
Wikstroemia skottsbergiana
Wikstroemia souliei
Wikstroemia Spreng.
Wikstroemia stenophylla
Wikstroemia subcyclolepidota
Wikstroemia subspicata
Wikstroemia taiwanensis
Wikstroemia techinensis
Wikstroemia tenuiflora
Wikstroemia tenuiramis
Wikstroemia thibetensis
Wikstroemia trichotoma
Wikstroemia uva-ursi
Wikstroemia venosa
Wikstroemia villosa
Wikstroemia yakushimensis
Wikstroemia zhouana
Wisteria brachybotrya
Wisteria brachybotrys
Wisteria consequana
Wisteria floribunda
Wisteria formosa
Wisteria frutescens
Wisteria macrobotrys
Wisteria Nutt.
Wisteria sinensis
Wisteria ventusa""".strip().split("\n")

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
