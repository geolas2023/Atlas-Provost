# Génère data/lieux.geojson et data/trajets.geojson de l'Atlas Étienne Provost (1785-1850).
# Usage : python3 scripts/build_provost.py .
# Sources réunies dans le Google Drive de l'auteur (dossiers HISTOIRE, ETIENNE_PROVOST, ETIENNE_PROVOST_AUDUBON)
# et dans l'atlas « Les Canadiens français de l'Ouest » (fiches Hafen MM, PV-, DRV-, AU43-, HF54-…).
import json, sys, datetime
OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
CERT = {'c': 'certaine', 'a': 'approximative', 'h': 'hypothetique'}

# ---- Sources
TYU = "Tykal, Jack B., « Provost, Etienne », Utah History Encyclopedia, Salt Lake City, University of Utah Press, 1994 (copie du Drive de l'auteur, t_000690.pdf ; uen.org)"
TY = "Tykal, Jack B. (1989), Etienne Provost: Man of the Mountains, Liberty (Utah), Eagle's View"
def HF(p): return f"Hafen, LeRoy R., « Etienne Provost », dans Hafen (dir.), The Mountain Men and the Fur Trade of the Far West, Glendale, Arthur H. Clark, vol. 6 (1968), p. 371-386 ; mention p. {p}"
HU = "Hafen, LeRoy R. (1968), « Etienne Provost, Mountain Man and Utah Pioneer », Utah Historical Quarterly, vol. 36, n° 2"
NI = "Nichols, Jeffrey D. (1995), « Fellow Trappers Called Etienne Provost “The Man of the Mountains” », History Blazer, Utah State Historical Society, août 1995 (historytogo.utah.gov)"
VA = "Vaugeois, Denis, « Provost, Québec - Provo, Salt Lake, Utah ? Des liens historiques et généalogiques », Le Devoir, 16-17 février 2002 (coupure du Drive de l'auteur, dossier ETIENNE_PROVOST_AUDUBON)"
BOU = "Bouchard, Serge et Marie-Christine Lévesque (2014), Ils ont couru l'Amérique. De remarquables oubliés, t. 2, Montréal, Lux, chap. « Hommes des montagnes : Provost, Chalifoux, Robidoux » (epub du Drive de l'auteur)"
ROQ = "« Étienne Provost et le Grand Lac Salé », fiche de la série De remarquables oubliés (Serge Bouchard), document du Drive de l'auteur (etienne_provost.pdf)"
def CH(p, v=1): return f"Chittenden, Hiram Martin (1902), The American Fur Trade of the Far West, New York, Francis P. Harper, vol. {v}, p. {p} (archive.org)"
def DA(p): return f"Dale, Harrison C. (1918), The Ashley-Smith Explorations and the Discovery of a Central Route to the Pacific, 1822-1829, Cleveland, Arthur H. Clark, p. {p} (archive.org)"
def HA(p): return f"Harris, W. R. (1909), The Catholic Church in Utah, Salt Lake City, Intermountain Catholic Press, p. {p} (archive.org)"
def BA(p): return f"Bancroft, Hubert Howe (1889), History of Utah, 1540-1886, San Francisco, The History Company, p. {p} (archive.org)"
def DOL(p): return f"Dolin, Eric Jay (2010), Fur, Fortune, and Empire: The Epic History of the Fur Trade in America, New York, W. W. Norton, PDF p. {p} (Drive de l'auteur)"
def GIT(p): return f"Gitlin, Jay (2010), The Bourgeois Frontier: French Towns, French Traders, and American Expansion, New Haven, Yale University Press, PDF p. {p} (Drive de l'auteur)"
def NEL(p): return f"Nelson, Jack William (2003), Forgotten Pathfinders Along the North Branch of the Old Spanish Trail, 1650-1850, PDF p. {p} (Drive de l'auteur)"
NEL96 = "Nelson, Jack William (1996), « The North Branch of the “Old Spanish Trail” », Journal of the Western Slope, vol. 11, n° 4, PDF p. 37 (Drive de l'auteur)"
ROY = "Roy, Alain, « Sur la piste de Santa Fe, 1721-1880 », dans Frenette, Yves, Étienne Rivard et Marc St-Hilaire (dir.) (2012), La francophonie nord-américaine, Québec, PUL, coll. « Atlas historique du Québec », p. 103"
OSF = "Old Santa Fe: A Magazine of History, Archaeology, Genealogy and Biography, vol. 1, Santa Fe, 1913-1914, p. 375 (archive.org)"
HF54 = "Hafen, LeRoy R. (1954), « When Was Bent's Fort Built? », The Colorado Magazine, vol. 31, n° 2, p. 107-108 ; lettre publiée par Dale L. Morgan, Provo, Pioneer Mormon City (1942), p. 24-25"
AUD = "Audubon, Maria R. (éd.) (1897), Audubon and his Journals, New York, Scribner, vol. 2, p. 30-65"
HAV = "Havard, Gilles (2019), L'Amérique fantôme. Les aventuriers francophones du Nouveau Monde, Paris, Flammarion, ch. 8 « L'homme des montagnes : Étienne Provost », p. 323-379 (PDF du Drive de l'auteur, dossier GILLES_HAVARD, lu intégralement le 19 nov. 2026)"
AA = "enquête d'O. J. Caron pour l'Atlas Aubry (2026), versée dans l'atlas « Les Canadiens français de l'Ouest » (fiches PV-01 à PV-05)"
UTG = "« Etienne Provost », historytogo.utah.gov (Utah State Historical Society), consulté en novembre 2026"
NIC = "Nicollet, Joseph-Nicolas (1841), Report Intended to Illustrate a Map of the Hydrographical Basin of the Upper Mississippi River, Sénat, 26e Congrès, 2e session, doc. 237, p. 42-50 (Drive de l'auteur)"
NPS = "National Park Service (1964), The Fur Trade: Significant Sites, National Survey of Historic Sites and Buildings, vol. 1, PDF p. 49 (Drive de l'auteur)"

def dec(d, fin=False):
    d = d.replace('~', '').replace('?', '')
    p = [int(x) for x in d.split('-')]
    if len(p) == 1:
        return p[0] + (0.999 if fin else 0.0)
    if len(p) == 2:
        a, m = p
        return round(a + (m - (0 if fin else 1)) / 12 - (0.001 if fin else 0), 4)
    a, m, j = p
    jour = datetime.date(a, m, j).timetuple().tm_yday
    return round(a + (jour - 1) / 365, 4)

def prec(edtf):
    d = edtf.split('/')[0]
    if '~' in d: return 'circa'
    return ['annee', 'mois', 'jour'][d.count('-')]

lieux = []
def L(n, nom, cat, edtf, lon, lat, cert, desc, src, note=''):
    a, b = (edtf.split('/') + [edtf])[:2]
    lieux.append({'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [lon, lat]},
                  'properties': {'id': f'L{n:02d}', 'nom': nom, 'debut': dec(a), 'fin': dec(b, True) if '/' in edtf else dec(a),
                                 'date_edtf': edtf, 'precision': prec(edtf), 'certitude': CERT[cert], 'categorie': cat,
                                 'description': desc, 'sources': src, 'note': note, 'type': 'lieu'}})

# ---- I. Chambly (1785-1813)
L(1, "Chambly : naissance d'Étienne Provost", 'naissance', '1785-12-21', -73.2858, 45.4486, 'c',
  "Étienne Provost naît à Chambly, sur le Richelieu, le 21 décembre 1785. Il est le premier enfant du troisième mariage d'Albert Provost, cultivateur, fils de Gabriel Provost et de Marie-Anne Bourassa, et de Marie-Anne Mainard (Ménard). Albert s'est marié trois fois à Chambly : avec Marie-Louise Paquet en 1770, qui lui donne huit enfants ; avec Magdeleine Lebeau en 1783 ; avec Marie-Anne Mainard le 25 janvier 1785. Étienne grandit donc entre six demi-frères et demi-sœurs aînés et cinq frères cadets : Toussaint (1787), Julien (1789), Antoine (1790), et deux petits Raphaël et François morts au berceau. L'acte de baptême, rédigé le jour même par le curé Ménard, lui donne pour parrain Étienne Frichet, qui signe, et pour marraine Thérèse Laroque, veuve Mainard, qui déclare ne savoir signer. Son père est inhumé à Chambly le 5 mars 1796, à 46 ans : Étienne a dix ans ; il ne saura jamais lire ni écrire. On ne sait presque rien de sa jeunesse ; il n'a pas vingt ans, écrit Denis Vaugeois, quand il choisit la traite des fourrures et le Far West, avec Saint-Louis pour base.",
  f"Registre de la paroisse Saint-Joseph de Chambly, baptêmes de 1785, f. 39, acte du 21 décembre 1785 (photographie au presbytère de Chambly, Etienne_Provost.jpg du Drive de l'auteur) ; {VA} ; {BOU} ; {TYU} ; {ROQ} ; Drouin, Quebec, Canada, Vital and Church Records (Drouin Collection), 1621-1968, paroisse Saint-Joseph de Chambly (Ancestry, consulté le 20 novembre 2026) : mariages de 1770, 1783 et 1785, baptêmes de 1771-1792, sépulture d'Albert Provost du 5 mars 1796",
  "Date confirmée par l'acte de baptême (« né le même jour ») ; date du jour aussi chez Vaugeois ; Tykal et Hafen donnent seulement 1785. La photothèque de la Utah State Historical Society propose 1782. Point à l'église Saint-Joseph de Chambly. La famille complète, avec chaque acte, est dans l'arbre Ancestry « Étienne Provost (1785-1850) – Atlas Provost » et dans l'onglet « L'arbre de la famille » de la salle de lecture.")
L(2, "Québec : l'ancêtre Martin Prévost et Marie-Olivier Manitouabeouich (1644)", 'famille', '1644', -71.2074, 46.8139, 'c',
  "Vaugeois rattache Étienne à Martin Prévost, premier du nom en Nouvelle-France, qui épousa à Québec en 1644 Marie-Olivier Sylvestre Manitouabeouich, fille adoptive de Champlain issue d'une famille huronne-wendate et algonquine : un des tout premiers mariages franco-autochtones consacrés dans la colonie.",
  VA, "Fiche généalogique, hors de la vie d'Étienne : elle s'affiche dès le début de la timeline. La filiation détaillée Martin → Étienne reste à établir dans les registres.")

# ---- II. Saint-Louis et les prisons espagnoles (1814-1821)
L(3, "Saint-Louis : un Canadien dans la capitale de la traite", 'vie', '1814~/1850', -90.1860, 38.6270, 'a',
  "Provost fait de Saint-Louis sa base pendant trente-cinq ans environ, entre deux campagnes dans l'Ouest. Il y arrive au plus tard en 1814-1815, dans une ville encore largement francophone, dominée par les Chouteau, les Pratte et les Berthold, pour qui il travaillera.",
  f"{TYU} ; {ROQ} ; {GIT(139)}",
  "La fiche De remarquables oubliés date l'installation de 1815 ; Tykal le fait partir pour l'Arkansas dès 1814. Point sur le front de rivière de la vieille ville.")
L(4, "Haut Arkansas : l'expédition de Joseph Philibert (1814)", 'prison', '1814', -104.61, 38.26, 'h',
  "En 1814, Provost fait partie de la brigade de Joseph Philibert, Montréalais établi à Saint-Louis, qui compte dix-huit Canadiens et se joint sur l'Arkansas à la troupe d'Ezekiel Williams ; le journal de Williams nomme Provost, Pierre Lespérance, Joseph Bissonnette dit Bijou, François Leclerc, Joseph Livernois, Charles Beaubien, Duchesne, Grenier, Lalande, Ledoux, Leroux et Nolan. En septembre, à Taos, ils sont arrêtés, emprisonnés à Santa Fe et expulsés, sans leurs marchandises. Philibert rentre à Saint-Louis en laissant neuf hommes, dont Provost, chasser dans les montagnes.",
  f"{TYU} ; {BOU}", "Point schématique sur le haut Arkansas (près de l'actuelle Pueblo). L'emprisonnement de 1814-1815 n'est connu que par Tykal ; les hommes de Philibert passent ensuite au service de Chouteau et De Mun.")
L(47, "Huerfano : le rendez-vous manqué de 1815", 'traite', '1815', -104.83, 37.73, 'h',
  "Philibert avait donné rendez-vous à ses neuf hommes, pour 1815, au Huerfano, près de la Purgatoire. Revenu avec Auguste-Pierre Chouteau et Jules de Mun, à qui il vend sa compagnie en route, il ne les y trouve pas : affamés, ils s'étaient réfugiés à Taos des mois plus tôt. Chouteau et De Mun gardent ce noyau d'hommes dans les montagnes ; la troupe de Provost est attaquée par les Arapahos.",
  BOU, "Point à la butte du Huerfano (Colorado), schématique.")
L(5, "Taos : Chouteau et De Mun en territoire espagnol (1816)", 'traite', '1816', -105.5745, 36.4075, 'a',
  "Partis de Saint-Louis en septembre 1815, Auguste-Pierre Chouteau et Jules de Mun montent trapper sur le haut Arkansas avec une quarantaine d'hommes, dont Provost. Ils obtiennent d'abord des autorités espagnoles la permission de chasser, notamment autour de Taos.",
  f"{ROY} ; {TYU}", "Point à Taos.")
L(6, "Île Chouteau : le refuge sur l'Arkansas", 'combat', '1816', -101.20, 37.93, 'a',
  "Au retour, la troupe de Chouteau, Provost et De Mun est attaquée et se retranche sur une île de l'Arkansas, rebaptisée depuis île Chouteau. Le lieu devient un repère de la future piste de Santa Fe.",
  ROY, "L'île a disparu avec les divagations du lit ; point près de l'actuelle Lakin (Kansas).")
L(7, "Santa Fe : « Ettinne Provott » en prison (1817)", 'prison', '1817-05/1817-07', -105.9384, 35.6875, 'c',
  "En mai 1817, la troupe est arrêtée par les soldats espagnols, qui l'accusent de chasser et de commercer sur leur territoire. Les hommes sont conduits à Santa Fe et enfermés plusieurs semaines ; leurs fourrures et leurs marchandises, d'une valeur de 30 000 $ selon De Mun, sont confisquées. Les vingt et un Canadiens restent captifs quarante-huit jours ; la liste des archives militaires de Santa Fe compte parmi eux Toussaint Charbonneau, l'ancien guide de Lewis et Clark. « Ettinne Provott » signe la déclaration des prisonniers avant d'être relâché et renvoyé aux États-Unis.",
  f"{OSF} ; {ROY} ; {TYU} ; {VA} ; {BOU}",
  "Montant et durée de la détention d'après la plainte de Chouteau et De Mun, résumée par l'Atlas historique du Québec et Old Santa Fe. Point au palais des gouverneurs.")

# ---- III. Taos et le Grand Bassin (1822-1826)
L(8, "Taos : le retour, au lendemain de l'indépendance mexicaine", 'traite', '1822~', -105.5745, 36.4075, 'a',
  "Fort de ce qu'il a appris du pays, Provost revient au Nouveau-Mexique vers 1822, dès l'ouverture du commerce de Santa Fe par le Mexique indépendant. Taos devient sa base : il y rencontre Antoine Robidoux, avec qui il travaillera par la suite dans le pays de la Uinta.",
  f"{TYU} ; {VA} ; {NEL(41)} ; {UTG}",
  "Vaugeois date le retour de 1821, Nelson de 1823. La fiche De remarquables oubliés lui prête la fondation, en 1822, de la Rocky Mountain Fur Company : c'est une confusion avec l'entreprise d'Ashley et Henry, à laquelle Provost n'a jamais appartenu.")
L(9, "Taos : « Provoe & Leclere » (lettre de Céran St. Vrain, 21 avril 1824)", 'traite', '1824-04-21', -105.5745, 36.4075, 'c',
  "Arrivé à Taos en mars 1824, Céran St. Vrain écrit le 21 avril à Bernard Pratte que les affaires sont mauvaises, mais qu'il compte vendre ses marchandises à « Provoe & Leclere » à leur retour de chasse. C'est la première trace écrite de l'association de Provost avec François Leclerc.",
  HF54, "L'identité de Leclerc (François ?) est proposée par Hafen.")
L(10, "Bassin de la Uinta : la chasse de Provost et Leclerc (1824)", 'traite', '1824/1825-04', -109.67, 40.08, 'a',
  "Associés, Provost et Leclerc quittent Taos par la branche nord de la Vieille Piste espagnole pour trapper le bassin de la Uinta et la Green River. Après le massacre d'octobre, Provost passe l'hiver 1824-1825 dans la région des rivières White et Green.",
  f"{TYU} ; {NEL96} ; {DA('94-95, 103')}",
  "Point au confluent de la White et de la Green (actuelle Ouray, Utah).")
L(11, "Rivière Jordan : le massacre de Bad Gocha (octobre 1824)", 'combat', '1824-10', -111.92, 40.55, 'h',
  "En octobre 1824, la troupe campe près du lac Utah, sans doute sur la Jordan. Un chef shoshone que les Blancs nomment « Bad Gocha » propose de fumer le calumet, à condition qu'aucune arme ni objet de métal ne soit à portée. Les trappeurs déposent leurs fusils ; à un signal, les Shoshones tirent les couteaux cachés. Provost s'échappe avec deux à quatre compagnons par les monts Wasatch, vers le nord-est.",
  f"{TYU} ; {UTG} ; {VA} ; {CH('261-280')} ; {HA('259-262')}",
  "Le nombre de morts varie selon les sources : huit (Tykal), huit à dix (Vaugeois), quinze (Nelson 1996), dix-sept (Harris). Le lieu aussi : Jordan près du Grand Lac Salé (Tykal), embouchure de la Provo (Harris). Peter Skene Ogden apprendra en 1825 que la troupe d'Alexander Ross avait auparavant volé et tué des Shoshones, ce qui expliquerait cette vengeance.")
L(12, "Grand Lac Salé : « le premier Blanc » ? (1824)", 'traite', '1824-10~', -112.25, 41.05, 'h',
  "Provost passe pour le premier Blanc à avoir vu le Grand Lac Salé, à l'automne 1824, quelques semaines avant Jim Bridger, à qui l'on attribue traditionnellement la découverte (hiver 1824-1825). Les indices sont indirects mais concordants.",
  f"{TYU} ; {UTG} ; {DOL('note 47')} ; {DA('94-95, 103')}",
  "Découverte disputée : Bancroft évoque même un passage antérieur à 1824, sans preuve. Point schématique sur la rive est du lac.")
L(13, "Lac Utah : postes de traite temporaires (1824-1825)", 'traite', '1824-11~/1825-04', -111.76, 40.24, 'h',
  "Survivant du massacre, Provost établit des postes de traite temporaires sur les rives du lac Utah et du Grand Lac Salé. La rivière qui se jette dans le lac Utah, puis la ville fondée sur ses bords, porteront son nom.",
  f"{TYU} ; {ROQ} ; {CH('626, 796', '2-3')}",
  "Emplacements inconnus. La fiche De remarquables oubliés parle de huit postes, chiffre que les biographes ne reprennent pas.")
L(14, "Mountain Green (canyon de la Weber) : Ogden face aux Américains (mai 1825)", 'rendezvous', '1825-05', -111.79, 41.14, 'a',
  "En mai 1825, dans le canyon de la Weber, Provost croise la brigade de la Compagnie de la baie d'Hudson menée par Peter Skene Ogden, et assiste à l'affrontement entre Ogden et Johnson Gardner, lieutenant d'Ashley, qui pousse les engagés d'Ogden à déserter. Ironie relevée par Tykal : de tous les hommes présents, seul Provost, venu de Taos sous licence mexicaine, avait le droit de chasser dans ce territoire encore mexicain.",
  f"{TYU} ; {UTG} ; {DA('94-95, 103')}",
  "Point à Mountain Green (Utah).")
L(15, "Fruitland : Provost rencontre William Ashley (juin 1825)", 'rendezvous', '1825-06', -110.83, 40.21, 'a',
  "Après une descente désastreuse de la Green River en bateaux de peau, William H. Ashley tombe sur des trappeurs de Provost qui le conduisent à son camp. En juin 1825, près de l'actuelle Fruitland, Provost accepte de le guider, par la Duchesne et le ruisseau Strawberry, puis au nord vers le lieu du premier rendez-vous. Il ne devient pas pour autant un employé d'Ashley.",
  f"{TYU} ; {NEL(40)} ; {NI} ; Contributions to the Historical Society of Montana, vol. 9 (1923), p. 324-325",
  "Dellenbaugh (1902) et Dale (1918) rapportent aussi un camp de Provost à Brown's Hole, plein de vivres et de chevaux à l'arrivée des hommes affamés d'Ashley ; Dale juge ce récit douteux.")
L(16, "Henry's Fork : le premier rendez-vous des Rocheuses (juillet 1825)", 'rendezvous', '1825-07', -109.93, 41.02, 'a',
  "Guidé par Provost, Ashley atteint l'Henry's Fork de la Green River, où se tient au début de juillet 1825 le premier rendez-vous annuel des trappeurs : Ashley y échange ses marchandises contre les fourrures des chasseurs dispersés dans les montagnes. Les Canadiens présents se tournent vers Provost comme vers leur guide naturel.",
  f"{TYU} ; {NI} ; Hebard, Grace Raymond et E. A. Brininstool (1922), The Bozeman Trail, vol. 1, p. 38",
  "Point près de Burntfork (Wyoming).")
L(17, "Col du Sud : une découverte attribuée à Provost", 'traite', '1824~', -108.90, 42.35, 'h',
  "Plusieurs auteurs anciens font de Provost le découvreur du col du Sud (South Pass), le passage facile des Rocheuses que suivront les émigrants vers l'Oregon et la Californie : les Annals of Wyoming le datent de 1822, Chittenden et Harris de 1823, Bartlett de 1824. Les historiens retiennent aujourd'hui la « redécouverte » du col par Jedediah Smith et Thomas Fitzpatrick au printemps 1824, sur l'indication des Crows.",
  f"Annals of Wyoming, vol. 1 (1923), p. 756 ; {CH('261-280')} ; {HA('259-262')} ; Bartlett, I. S. (dir.) (1918), History of Wyoming, vol. 1, p. 478 ; {ROQ}",
  "Attribution traditionnelle, non démontrée ; aucune source contemporaine ne place Provost au col.")
L(18, "Lac Utah : Provost ravitaille les hommes de Jedediah Smith ?", 'rendezvous', '1825~/1826~', -111.80, 40.20, 'h',
  "Bancroft rapporte qu'une troupe menée par Provost aurait nourri et remonté en chevaux les hommes affamés de Jedediah Smith près du lac Utah.",
  BA('22, n. 4'), "Épisode isolé, de date incertaine ; à vérifier dans Morgan (1953).")
L(19, "Fort Lookout : la descente du Missouri (1826)", 'traite', '1826-08~', -99.40, 43.95, 'a',
  "Après le rendez-vous de 1826, auquel Jim Beckwourth le dit présent sans certitude, Provost redescend vers les États-Unis par le Missouri ; la notice de Hafen le signale au fort Lookout, poste de la vallée du Missouri.",
  f"{HF(376)} ; {HU}", "Point au fort Lookout (Dakota du Sud).")
L(20, "Saint-Louis : « l'âme des chasseurs dans les montagnes » (septembre 1826)", 'traite', '1826-09', -90.1840, 38.6280, 'c',
  "En septembre 1826, Provost est de retour à Saint-Louis et traite avec B. Pratte & Company. Barthélemy Berthold, associé de la maison, écrit cette année-là qu'il est « l'âme des chasseurs dans les montagnes ». Il entre au service de l'American Fur Company d'Astor, dont la maison Pratte-Chouteau est le Département de l'Ouest.",
  f"{HU} ; {TYU}", "Point près de la levée, où se trouvaient les magasins des Chouteau et des Pratte.")

# ---- IV. L'American Fur Company (1827-1838)
L(21, "Saint-Louis : la taverne et l'épicerie", 'traite', '1827~/1850', -90.1895, 38.6180, 'h',
  "À partir de 1827 environ, Provost tient à Saint-Louis une taverne et une épicerie (« grocery »), entre ses saisons dans l'Ouest. Il est associé, selon Vaugeois, à son beau-frère Clément Salle dit Lajoie. Bon vivant, il est célèbre pour son goût de la bonne chère et de la bouteille.",
  f"{TYU} ; {VA} ; {GIT(139)} ; {AA}",
  "Adresse inconnue ; point dans le Frenchtown de la rue Second, où Havard situe Provost. L'annuaire de 1845 place un « Clement Lambert, coffee-house » à l'angle des rues Second et Lombard (voir L36).")
L(22, "Fort Floyd (futur fort Union) : McKenzie envoie Provost chercher les trappeurs libres (automne 1828)", 'guide', '1828-09~', -104.0405, 47.9994, 'c',
  "À l'automne 1828, Kenneth McKenzie, chargé par Astor d'entamer le commerce des Rocheuses, envoie Provost, « ancien homme d'Ashley », dans les montagnes annoncer aux trappeurs libres que l'American Fur Company achète leurs fourrures à bon prix. Provost ramène au poste de l'embouchure de la Yellowstone des trappeurs de la Rocky Mountain Fur Company.",
  f"{DOL(325)} ; {CH('305-306, 328')} ; {HF(377)}",
  "Le fort Floyd est rebaptisé fort Union vers 1830.")
L(23, "Pays crow : la première épouse et le fils Nicolas (hypothèse)", 'famille', '1828~', -107.6, 45.6, 'h',
  "Avant son mariage à Saint-Louis, Provost aurait eu d'une femme autochtone, crow selon la tradition familiale, un fils nommé Nicolas ; Bouchard et Lévesque placent cette liaison à l'hiver 1828. Un petit-fils, Michel, serait né au Canada.",
  f"{VA} ; {BOU} ; {ROQ}",
  "Union attestée seulement par la tradition rapportée par Vaugeois et De remarquables oubliés ; date et lieu inconnus. Point placé par l'atlas dans le pays crow (Bighorn-Yellowstone), que parcouraient les trappeurs libres recherchés en 1828-1829.")
L(24, "Saint-Louis : mariage avec Marie-Rose Lambert, fille de Lambert Salé dit Lajoie (4 août 1829)", 'famille', '1829-08-04', -90.1857, 38.6243, 'c',
  "Rentré à Saint-Louis le 27 juillet 1829, Provost apprend que Marie-Rose Lambert, fille de son associé Lambert Salé dit Lajoie et de Madeleine Delor, de douze ans sa cadette, est veuve depuis l'automne ; il la connaît depuis 1826 au moins. Le mariage est fixé au 4 août et béni par le jésuite Joseph Anthony Lutz ; l'acte, que Provost signe d'une croix, dit l'épouse « fille de Lambert Salé, dit Lajoy, et Magdeleine Delor » ; parmi les témoins signent son père (« Lajoye ») et son frère Clément Lambert, Marie Ménard fait sa marque, et « Mr J. Laberge », sans doute Joseph-Marie La Barge, père du futur pilote. Provost achète pour la noce couvertures, casinette, étoffe écarlate et dentelle d'argent. L'union a aussi une dimension commerciale ; dès l'été 1829, Marie-Rose apparaît comme créditrice dans les registres de la compagnie.",
  f"{HAV}, p. 339-340 ; {TYU} ; {VA} ; {BOU} ; registre des sépultures de la vieille cathédrale de Saint-Louis, 4 juillet 1850, d'après {AA} ; Drouin, U.S., French Catholic Church Records (Drouin Collection), 1695-1954, Saint-Louis (vieille cathédrale), registre des mariages 1828-1836, acte du 4 août 1829 (image 15 sur 117, Ancestry, lue le 20 novembre 2026)",
  "La date de Havard, tirée des registres paroissiaux et des comptes de l'AFC, règle la question : Vaugeois, qui donne à l'épouse 31 ans et à Provost 46, plaçait le mariage vers 1831-1832. Les noms varient : « Marie Rose Salle Dupuis » (Vaugeois), « Marie-Rose La Salle » (De remarquables oubliés), « Maria Rose Lombard » (registre de 1850). Point à la vieille cathédrale. Havard écrit « belle-fille » de Lambert Salé ; l'acte de mariage règle la question : Marie-Rose est sa fille. Par son père, elle est petite-fille de María Rosa Villalpando, captive enlevée à Taos en 1760 (fiche L71) ; par sa mère, petite-fille de Clément Delor de Tréget, fondateur de Carondelet (fiche L70).")
L(25, "Saint-Louis : naissance de Mary Rose, « fille d'Étienne Provo » (1er mai 1830)", 'famille', '1830-05-01', -90.1860, 38.6255, 'a',
  "Le certificat de décès de Mary Rose Pillsbury (1913) la dit née à Saint-Louis le 1er mai 1830, fille d'« Etienne Provo », né au Canada. La date tombe un an après le mariage : ce serait la fille unique connue du couple, qu'Audubon voit à bord du vapeur en 1843.",
  "Missouri State Board of Health, certificat de décès n° 27938, Mary Rose Pillsbury, Saint-Louis, 8 août 1913 (Drive de l'auteur) ; " + AUD,
  "Le certificat nomme la mère « Madelin Delor », née à Saint-Louis. Ce n'est pas la mère de Mary Rose mais sa grand-mère maternelle : l'acte de mariage de 1829 dit Marie-Rose « fille de Lambert Salé, dit Lajoy, et Magdeleine Delor ». L'informateur de 1913, Charles G. Grimm, mari de la petite-fille de la défunte, a sauté une génération (voir l'onglet « L'arbre de la famille » de la salle de lecture). Les recensements confirment la lignée : en 1860, Mary Rose vit avec son mari James A. H. Pillsbury et leur fille Mary Frances ; en 1900 et 1910, elle habite chez sa fille et son gendre Charles G. Grimm. Le baptême n'a pas été trouvé dans l'index Drouin de Saint-Louis. Point schématique dans la vieille ville.")
L(26, "Fort Union : chasseur et batelier de la compagnie (1830-1831)", 'traite', '1830/1831', -104.0405, 47.9994, 'a',
  "En 1830, Provost compte parmi les chasseurs du fort Union ; en 1831, le rôle de l'American Fur Company l'inscrit comme batelier. Le fort, bâti par McKenzie au confluent de la Yellowstone et du Missouri, devient le pivot de la traite du haut Missouri.",
  HF('378-379'), "")
L(27, "Bayou Salade : guide de Fontenelle et Drips (1834)", 'guide', '1834-05~', -105.85, 39.10, 'a',
  "Au printemps 1834, Provost guide Lucien Fontenelle et Andrew Drips, chefs de partie de l'American Fur Company, jusqu'au Bayou Salade (South Park, Colorado), vaste parc d'altitude riche en gibier.",
  HF(379), "Hafen date l'épisode de 1833-1834 ; la date de 1834 suit le résumé biographique de Hafen repris par Prabook.")
L(28, "Ham's Fork : le rendez-vous de 1834", 'rendezvous', '1834-07', -110.00, 41.65, 'a',
  "En juillet 1834, Provost mène une troupe de l'American Fur Company au rendez-vous de la Ham's Fork, affluent de la Black's Fork (Green River). Jusqu'en 1838, il convoie ainsi les caravanes de la compagnie vers les rendez-vous annuels. Le voyageur William Marshall Anderson, qu'il guide en 1834, gardera en mémoire ses ordres en français, « Fumez la pipe ! » pour la halte, « Gardez aux rames ! », et lui fait ses adieux à la fin de son journal.",
  f"{HF('379-380')} ; {TYU} ; {BOU} ; Morgan, Dale L. et Eleanor T. Harris (éd.) (1967), The Rocky Mountain Journals of William Marshall Anderson", "Point près de Granger (Wyoming).")
L(29, "Bellevue : la barge des fourrures (1834)", 'traite', '1834-09~', -95.89, 41.137, 'c',
  "À la fin de la saison 1834, Provost conduit sur le Missouri la barge qui porte les fourrures de la compagnie jusqu'au poste de Bellevue, tenu par Lucien Fontenelle puis Peter Sarpy, en route pour Saint-Louis.",
  f"{CH(475)} ; {HF(380)}", "Point à Bellevue (Nebraska).")
L(30, "Fort William (Laramie) : avec les caravanes de 1836", 'guide', '1836', -104.558, 42.203, 'a',
  "En 1836, Provost passe au fort William, sur la Laramie, que l'American Fur Company vient de racheter, avec la caravane qui monte de Liberty (Missouri) et du poste de Council Bluffs vers le rendez-vous.",
  HF(381), "Point au fort Laramie (Wyoming).")
L(31, "Horse Creek (Green River) : Alfred Jacob Miller peint « Proveau » (rendez-vous de 1837)", 'rendezvous', '1837-07', -110.07, 42.87, 'c',
  "Au printemps 1837, Provost dirige une caravane d'une trentaine de charrettes où voyage le peintre Alfred Jacob Miller, engagé par le capitaine écossais William Drummond Stewart. Au rendez-vous, Miller croque Provost, toujours sur sa mule, chapeau à large bord et carabine Hawken. On le reconnaît dans Threatened Attack, sur une mule, et dans Catching Up, debout près du feu, les mains en porte-voix. Miller lui prête un corps « rond comme un marsouin » ; un autre voyageur le dit « adipeux et rotond, engraissant la terre maigre où il passe ».",
  f"{VA} ; {TYU} ; {BOU}", "Point au confluent de Horse Creek et de la Green River (près de Daniel, Wyoming).")
L(32, "Saint-Louis : Provost annonce l'épidémie de variole (24 février 1838)", 'traite', '1838-02-24', -90.1840, 38.6285, 'c',
  "Le 24 février 1838, Provost arrive à Saint-Louis, tard en saison, du haut pays : il apporte la nouvelle de l'épidémie de variole qui ravage depuis l'été 1837 les nations du haut Missouri (Mandans, Arikaras, Assiniboines, Pieds-Noirs), dont la compagnie l'avait chargé de constater l'étendue. Au printemps 1838, il assiste à son dernier rendez-vous et ne retournera plus dans les Rocheuses.",
  f"{CH('626', '2-3')} ; {HA('259-262')} ; {BOU}", "")

# ---- V. Guide, recruteur et tavernier (1839-1850)
L(33, "Fort Pierre : chef des hommes de Nicollet et Frémont (1er-3 juillet 1839)", 'guide', '1839-07-01/1839-07-03', -100.385, 44.395, 'c',
  "En 1839, l'American Fur Company prête Provost à Joseph-Nicolas Nicollet, qui cartographie les plateaux entre le Missouri et le haut Mississippi avec le jeune John C. Frémont. Nicollet écrit avoir amené de Saint-Louis cinq hommes qui « en valaient certainement dix », dont « Étienne Provost, connu comme l'homme des montagnes », qu'il promeut chef de ses hommes. Le 1er juillet, Provost vient annoncer que l'équipement est prêt ; la caravane, dix-neuf personnes, dix charrettes et trente chevaux, traverse le Missouri gonflé les 1er et 2 juillet et monte le 3 sur le coteau du Missouri.",
  f"{NIC} ; {TYU} ; {UTG} ; {HF(382)}", "Point au fort Pierre.")
L(34, "Lac du Diable : terme de l'expédition Nicollet (29 juillet-7 août 1839)", 'guide', '1839-07-29/1839-08-07~', -98.95, 48.05, 'a',
  "Par le coteau du Missouri et la rivière à Jacques (James), le convoi atteint le 29 juillet 1839 le lac du Diable (Mini-wakan), où il reste neuf jours, près d'un camp que viennent de quitter les Métis de la rivière Rouge, avant de redescendre vers le sud-est.",
  f"{NIC} ; {TYU}", "Point au lac du Diable (Dakota du Nord).")
L(35, "Saint-Louis : recruteur et convoyeur de l'American Fur Company (1839-1849)", 'traite', '1839/1849', -90.1835, 38.6290, 'a',
  "De 1839 à sa mort, Provost recrute chaque hiver les nouveaux engagés de la compagnie et les conduit au printemps à leurs postes du Missouri. La compagnie loue aussi ses services de guide à des expéditions privées : officiers britanniques en garnison à Montréal qu'il mène chasser le bison jusqu'aux plaines du Texas en 1840, Audubon en 1843, la troupe du comte d'Otrante, fils du ministre de la Police de Napoléon, en 1844, sans doute son client le plus exigeant.",
  f"{TYU} ; {VA} ; {BOU}", "Point sur la levée de Saint-Louis. Selon Bouchard et Lévesque, le St. Louis Weekly Reveille signale le retour du comte d'Otrante, chargé de trophées.")
L(36, "Saint-Louis : le Frenchtown de la rue Second", 'vie', '1840/1847', -90.1890, 38.6165, 'a',
  "Gilles Havard situe Provost dans le Frenchtown, au sud de la vieille cathédrale (rues Second et Third, entre Poplar et Lombard), d'après l'annuaire de 1847 et le recensement municipal de 1845. Les annuaires de 1840-1841 et 1845 placent un « H. N. Provost », épicier, à l'angle sud-ouest des rues Second et Lombard, en face du café de Clément Lambert ; mais l'annuaire de 1851 inscrit encore un « Henry N. Provost, mountain trader » : sans doute un parent.",
  f"{HAV}, notes 87, 130 et 138 ; Green's St. Louis Directory for 1845, p. 103 et 144 ; Green's St. Louis Directory for 1851, p. 281 ; {AA}",
  "L'emplacement exact de la maison de Provost, à l'angle sud-ouest de Second et Lombard, est établi dans la fiche L73. À vérifier : l'entrée d'Étienne dans l'annuaire de 1847 (p. 153). Le quartier est aussi celui de Moïse Lamoureux, natif de Chambly.")
L(37, "Fort Union : le vieux Provost, chasseur d'Audubon (juin-août 1843)", 'guide', '1843-06-12/1843-08-16', -104.0405, 47.9994, 'c',
  "Arrivé au fort Union le 12 juin 1843 avec Audubon sur le vapeur Omega, le « vieux » Provost, qui a emmené sa fille, dirige les chasseurs de l'expédition : il part avant l'aube de l'autre côté du Missouri, rapporte cerfs et antilopes, prépare la saumure des peaux, porte des messages au fort rival et fabrique des appeaux imitant le bêlement des faons. Audubon admire l'habileté de ses chasseurs canadiens, Bonaventure Le Brun, Charles Primeau, Alexis Bombardier, et note leurs canadianismes.",
  f"{AUD} ; {VA}", "")
L(38, "Saint-Charles : « le vieux Provost » rentre à pied (18 octobre 1843)", 'vie', '1843-10-18', -90.4812, 38.7839, 'c',
  "Au retour, à Saint-Charles, Audubon note le départ à pied de Provost, complètement ivre, pour Saint-Louis, où l'attendent sa femme, sa fille et son beau-frère Clément Salle dit Lajoie. Pour près de cinq mois de service, cet « homme fort respectable » reçoit 214 $ d'Audubon et 78,33 $ de l'Upper Missouri Outfit.",
  f"{VA} ; {AUD}", "")
L(39, "Fort Pierre : les dernières remontées du Missouri (1845-1849)", 'guide', '1845/1849', -100.385, 44.395, 'a',
  "Jusqu'à la fin des années 1840, Provost remonte chaque printemps le Missouri jusqu'aux postes de la compagnie ; Vaugeois le dit encore actif comme guide entre Fort Pierre et Saint-Louis. Son dernier voyage dans le haut pays, en 1848 ou 1849, se fait à bord du vapeur de son ami le capitaine Joseph LaBarge ; LaBarge et Henri Picotte entretiendront sa légende.",
  f"{TYU} ; {VA} ; {HF(384)} ; {BOU}", "")
L(40, "Saint-Louis : mort et inhumation (3-4 juillet 1850)", 'mort', '1850-07-03/1850-07-04', -90.1857, 38.6243, 'c',
  "Rentré en 1849 dans sa maison de la rue Lombard, Étienne Provost meurt subitement, d'une crise cardiaque selon Bouchard et Lévesque, à Saint-Louis le 3 juillet 1850, à 64 ans, sans savoir que les Mormons viennent de donner son nom à une ville de l'Utah. Il est inhumé le lendemain depuis la vieille cathédrale, dont le registre l'inscrit comme époux de « Maria Rose Lombard ».",
  f"{TYU} ; {UTG} ; {HAV} ; {BOU} ; registre des sépultures de la vieille cathédrale, 4 juillet 1850, d'après {AA}",
  "Point à la vieille cathédrale (basilique Saint-Louis-Roi-de-France). La maison mortuaire, au coin des rues Lombard et Second, est la fiche L73.")

# ---- Havard (2019), ch. 8, lu intégralement
L(48, "Montréal : contrat de voyageur, « milieu » et hivernant pour les dépendances du Sud (25 janvier 1805)", 'vie', '1805-01-25', -73.5540, 45.5080, 'c',
  "À 19 ans, Étienne Provost signe d'une croix, à Montréal, un contrat de voyageur : « milieu » (avironneur du centre du canot) et « hivernant », pour 500 livres, avec un « équipement double ordinaire » (deux ceintures de portage, deux couvertures, deux chemises de coton, deux paires de mocassins, double ration de tabac). Il doit passer par Michillimakinac et hiverner dans les « dépendances du Sud », c'est-à-dire notamment le pays des Illinois. On ne le revoit plus ensuite dans les actes de Chambly, où sa mère et ses trois frères apparaissent souvent.",
  f"{HAV}, p. 328-329 (BAnQ-Montréal, CN601, S185)",
  "Point au vieux Montréal (greffes notariaux). Audubon, qui le dit en 1843 « dans la traite depuis 29 ans », place plutôt ses débuts vers 1814.")
L(49, "Fort Tecumseh : la carabine Hawken et les peaux refusées à McKenzie (9 juillet 1829)", 'traite', '1829-07-09', -100.3500, 44.3800, 'c',
  "De retour de sa chasse de printemps chez les Corbeaux, Provost se présente au fort Tecumseh le 9 juillet 1829 mais refuse de vendre ses peaux à Kenneth McKenzie, pressé d'en tirer meilleur prix à Saint-Louis. McKenzie, admiratif de sa carabine à percussion faite par les frères Hawken, en commande deux semblables à Pierre Chouteau Jr. : Provost est l'un des premiers trappeurs à utiliser cette arme, quand la plupart portent encore le long fusil à silex de Pennsylvanie. En octobre, de retour au fort comme associé de l'« aventure d'Étienne Provost » financée à moitié par l'AFC, il obtient du commis Jacob Halsey 232,52 dollars d'articles avant de regagner le pays crow.",
  f"{HAV}, p. 339-341",
  "Point au fort Tecumseh, en face de l'actuelle Pierre (Dakota du Sud).")
L(50, "Saint-Louis : naissance et mort de Marianne, choléra de 1834", 'famille', '1833-09-21/1834-06', -90.1862, 38.6250, 'c',
  "Après avoir conduit de Fort Union à Fort Pierre la caravane de Fontenelle et Drips (120 mules et chevaux, 60 paquets de castor), Provost convoie les peaux jusqu'à Saint-Louis, où naît sa deuxième fille, Marianne, le 21 septembre 1833. Elle meurt du choléra en juin 1834, comme son cousin Jean-Baptiste Provost et l'épouse de celui-ci, Agnès, emportés au cours de l'été. Provost avait été témoin au mariage de Jean-Baptiste le 2 octobre 1826, en signant d'une croix.",
  f"{HAV}, p. 337, 344, 349",
  "Point schématique dans la vieille ville. Avec Mary Rose (L25), c'est la seconde fille connue du couple.")
L(51, "Poste de Cabanné : le jeune La Barge rencontre « le vétéran montagnard » (été 1833)", 'vie', '1833-07~', -95.9700, 41.3800, 'a',
  "Selon les souvenirs dictés dans sa vieillesse par le pilote Joseph La Barge, alors commis au poste de Jean-Pierre Cabanné dirigé par Joshua Pilcher, il y croise à l'été 1833 Provost, qu'il appelle un « vieil homme » (il a 47 ans) et dont il dit qu'« il connaissait probablement l'Ouest mieux qu'aucun autre homme vivant ». Havard juge l'anecdote douteuse mais révélatrice : La Barge, devenu son intime, est le seul passeur de la légende de Provost.",
  f"{HAV}, p. 335-336",
  "Point au poste de Cabanné, au nord de l'actuelle Omaha (Nebraska), approximatif.")
L(52, "Council Bluffs : l'enquête sur la variole pour l'American Fur Company (décembre 1837-février 1838)", 'guide', '1837-12/1838-02-24', -95.8600, 41.2600, 'c',
  "En décembre 1837, la compagnie dépêche Provost à Council Bluffs pour porter des lettres et recueillir toutes les informations sur l'épidémie qui ravage le haut Missouri. À son retour (24 février 1838), il dresse pour le comptable James A. Hamilton un bilan tribu par tribu : 31 Mandanes survivants, Assiniboines réclamant vengeance contre les traiteurs, 51 cas au fort McKenzie ; il estime la récolte de robes à venir (1 600 chez les Sioux, peu touchés, 800 chez les Pieds-Noirs, 300 chez les Corbeaux et autant chez les Assiniboines).",
  f"{HAV}, p. 352-353",
  "Point à Council Bluffs (Iowa). Complète L32.")
L(53, "Independence : guide des officiers Warre et Fairholme, « Man on a Mule » (août-novembre 1840)", 'guide', '1840-08-22/1840-11', -94.4155, 39.0911, 'c',
  "Engagé sur la recommandation de Kenneth McKenzie, qui le tient pour « l'un des meilleurs conducteurs de l'American Fur Company », Provost guide pour 80 dollars par mois deux officiers britanniques, Henry James Warre et William Fairholme, dans les plaines du Kansas. Il recrute sept Canadiens, dont deux neveux ; Constant Provost sert de valet à Warre, Jean-Baptiste Tabeau à Fairholme. La caravane (trois chariots, une vingtaine de chevaux, dix-sept hommes) quitte Saint-Louis le 22 août pour Independence. Warre, d'abord méfiant (« un vieil ivrogne » en ville), ne s'en plaint plus ; son croquis Man on a Mule semble représenter Provost.",
  f"{HAV}, p. 359-363",
  "Point à Independence (Missouri), départ de la caravane. Complète L35 (le « voyage au Texas » de 1840).")
L(54, "Le vapeur Trapper : contremaître de 150 engagés vers Fort Union (11 avril 1842)", 'guide', '1842-04-11/1842-07', -90.1840, 38.6260, 'c',
  "Le 11 avril 1842, Provost quitte à l'aube sa maison de l'angle des rues Lombard et Second pour embarquer sur le Trapper, vapeur de l'AFC commandé par Joseph A. Sire, à destination de Fort Union. Payé 50 dollars par mois, il sert de contremaître : prévenir les désertions et apaiser les querelles de 150 engagés. Un mois plus tôt, il a obtenu une licence d'aubergiste ; c'est Marie-Rose qui tient le saloon et loue les chambres.",
  f"{HAV}, p. 363-364",
  "Point à la levée de Saint-Louis.")
L(55, "Cimetière catholique de Rock Springs : la sépulture et la succession (juillet 1850)", 'mort', '1850-07-04', -90.2560, 38.6220, 'a',
  "Après les obsèques à la cathédrale, Provost est enterré au cimetière catholique de Rock Springs, dans la périphérie ouest de Saint-Louis. Il laisse à Marie-Rose une maison en ville et des parcelles dans l'Iowa et le Tennessee ; ses meubles valent 78,95 dollars et il laisse 102,70 dollars en liquide, aussitôt absorbés par les taxes foncières et les funérailles (54 dollars le cercueil, 1,50 le corbillard). Marie-Rose meurt en 1873. Aujourd'hui, rien ne rappelle son souvenir à Saint-Louis.",
  f"{HAV}, p. 378-379",
  "Le cimetière de Rock Springs a disparu ; point approximatif dans l'ancien secteur de Rock Spring (avenue Vandeventer).")

L(56, "Bellevue : le beau-frère du « vieux Provost », commis chez Sarpy (9 mai 1843)", 'famille', '1843-05-09', -95.89, 41.137, 'c',
  "Lors de l'escale de l'Omega à Bellevue, le 9 mai 1843, Audubon trouve au poste de Peter Sarpy, absent comme l'agent des Indiens, partis sur la Platte, « le beau-frère du vieux Provost », qui tient le magasin comme commis. Le poste paraît modeste mais fait un bon commerce avec les Indiens de la Platte ; Audubon voit payer huit cordes de bois avec cinq tasses de sucre et trois de café. Provost, qui voyage sur le même vapeur, retrouve ainsi un parent de sa femme.",
  "Audubon, Maria R. (éd.) (1897), Audubon and his Journals, New York, Scribner, vol. 1, p. 477 (PDF p. 537 ; Drive de l'auteur)",
  "Audubon ne nomme pas ce beau-frère. Provost avait épousé en 1829 Marie-Rose Lambert, fille de Lambert Salé dit Lajoie et de Madeleine Delor (fiche L24) ; il pourrait s'agir d'un frère de Marie-Rose (Clément, ou un autre fils Salé) ou du mari d'une de ses sœurs, mais rien ne le confirme ici.")

L(57, "Rivière Charbonneau (Yellowstone) : la chasse au castor manquée avec Squires (16-19 juillet 1843)", 'traite', '1843-07-16/1843-07-19', -103.96, 47.86, 'a',
  "Pendant l'excursion d'Audubon à la Yellowstone, Provost, le rameur Basile et le jeune Lewis Squires sont laissés au camp pour chasser la loutre et le castor. Provost pilote l'esquif qui descend la Yellowstone, plus rapide et plus boueuse que le Missouri, jusqu'à l'embouchure de la rivière Charbonneau. Il enseigne à Squires à tendre les pièges : trouver une berge, couper deux perches sèches, entrer dans l'eau, creuser la vase en demi-cercle. Il conclut qu'il n'y a qu'un seul castor, un mâle, que les pièges ne prennent pas. Il tue une biche, pêche seize grosses barbues et pousse jusqu'aux Mauvaises Terres pour chasser le mouflon. Revenu à Fort Union le 19 juillet par Fort Mortimer, il est, selon Audubon, « déconfit » de l'échec.",
  "Audubon, Maria R. (éd.) (1897), Audubon and his Journals, New York, Scribner, vol. 2, p. 95-102 (récit de Squires ; PDF p. 111-118, Drive de l'auteur)",
  "Point placé à l'embouchure de la rivière (Charbonneau Creek), en aval de Fort Union sur la Yellowstone.")
L(58, "Fort Mortimer : messager d'Audubon chez l'Opposition, connu des métis du Nord (juin-août 1843)", 'guide', '1843-06-17/1843-08-07', -104.025, 47.985, 'a',
  "Audubon envoie souvent « le vieux Provost » au fort rival de l'Opposition, Fort Mortimer, voisin de Fort Union : il s'y enquiert des lettres de Cutting, d'un renard véloce venu de la Yellowstone, des nouvelles arrivées d'en bas, des bisons ou d'un porc-épic. Le 24 juillet, six métis venus du Nord-Est avec onze têtes de bétail demandent tous de ses nouvelles. En août, il va chercher Boucherville pour une chasse au mouflon. Il raconte aussi à Audubon les mœurs du castor, du loup et du bison, et l'âge d'or des trappeurs, où un paquet de soixante-dix peaux valait cinq cents dollars.",
  "Audubon, Maria R. (éd.) (1897), Audubon and his Journals, New York, Scribner, vol. 2, p. 37-133 (PDF p. 51-151, Drive de l'auteur)",
  "Point placé à l'emplacement approximatif de Fort Mortimer (ancien fort William), à environ 3 km en aval de Fort Union.")

# ---- VI. Postérité
L(41, "Rivière Provo : la « Provost Fork » des cartes de Frémont (1845)", 'posterite', '1845', -111.73, 40.24, 'a',
  "Le récit de l'expédition de Frémont publié en 1845, auquel Kit Carson a servi de guide, nomme « Provost Fork » la rivière qui descend au lac Utah. Le nom du trappeur s'imprime ainsi sur les cartes avant l'arrivée des Mormons ; la Jordan a aussi été appelée Proveau's Fork.",
  VA, "Point à l'embouchure de la Provo dans le lac Utah.")
L(42, "Provo : la ville porte, écourté, le nom de Provost (1849)", 'posterite', '1849-03/1849-10', -111.6585, 40.2338, 'c',
  "Au printemps 1849, une trentaine de familles mormones conduites par John S. Higbee bâtissent le fort Utah sur la rivière de la vallée d'Utah. Le trappeur Barney Ward leur apprend qu'on l'appelle aussi la Provo, d'après Provost ; en octobre 1849, la conférence de l'Église ordonne d'y fonder la ville de Provo. Provost y a laissé, note Vaugeois, les deux dernières lettres de son nom.",
  f"{UTG} ; {VA} ; {GIT(139)} ; {DOL(325)}", "")
L(43, "Saint-Louis : mort de Mary Rose Pillsbury, fille de Provost (1913)", 'famille', '1913-08-08', -90.2585, 38.5845, 'a',
  "Mary Rose Pillsbury, veuve, sans doute de James A. Pillsbury, meurt à 83 ans au 4231 South 37th Street ; elle est inhumée au cimetière Calvary le 11 août 1913. Son certificat de décès la dit fille d'« Etienne Provo », né au Canada. L'avis de décès du St. Louis Star and Times la dit mère de Mme Chas. G. Grimm et d'un fils prénommé Étienne Pillsbury (le prénom du grand-père), grand-mère d'une religieuse du couvent du Bon-Pasteur (sans doute l'une des quatre filles Grimm recensées en 1900 et 1910 : Mary E., Clara E., Margaret M. A. ou Agnes Maria) ; les funérailles partent le lundi 11 août de sa résidence du 4221 South Thirty-seventh pour l'église St. Thomas of Aquin, puis le cimetière Calvary.",
  "Missouri State Board of Health, certificat de décès n° 27938, Mary Rose Pillsbury, 8 août 1913 (Drive de l'auteur) ; avis de décès « Pillsbury », The St. Louis Star and Times, 10 août 1913, p. 17 (coupure du Drive de l'auteur, clipping_7501912.pdf)", "Le certificat donne le 4231, l'avis le 4221 South 37th Street ; les débuts de lignes de l'avis sont coupés sur la coupure.")
L(44, "Salt Lake City : Provost sur le monument This Is the Place (1947)", 'posterite', '1947-07-24', -111.8155, 40.7527, 'c',
  "Pour le centenaire de l'arrivée des Mormons, le monument This Is the Place, à l'entrée du canyon d'Emigration, rend hommage aux explorateurs qui les ont précédés : Provost y figure parmi les trappeurs.",
  "Wikipédia, « Étienne Provost », consulté en novembre 2026 ; " + NPS, "")
L(45, "Montréal : Denis Vaugeois rend Provost aux Québécois (Le Devoir, 2002)", 'posterite', '2002-02-16', -73.5617, 45.5089, 'c',
  "Dans Le Devoir, l'historien et éditeur Denis Vaugeois raconte la vie de Provost, du Richelieu au Grand Lac Salé, et s'amuse que la ville mormone garde le nom d'un joyeux tavernier catholique, uni d'abord à une Autochtone.",
  VA, "L'atlas « Les Canadiens français de l'Ouest » date un article semblable de 2008 (fiche PVM-01) ; la coupure du Drive, qui mentionne l'année 2002, semble être la même. Point au siège du Devoir.")
L(46, "Fort Union : Les Crépuscules de la Yellowstone (Louis Hamelin, 2020)", 'posterite', '2020', -104.0405, 47.9994, 'c',
  "Le romancier québécois Louis Hamelin fait de la remontée du Missouri par Audubon en 1843 un roman-fleuve, où Étienne Provost sert de guide et de contrepoint au naturaliste.",
  "Hamelin, Louis (2020), Les Crépuscules de la Yellowstone, roman, Montréal, Boréal (Drive de l'auteur)", "Œuvre de fiction.")

# ---- Trajets
traj = []
def T(n, nom, mode, edtf, coords, cert, desc, src, note=''):
    a, b = (edtf.split('/') + [edtf])[:2]
    traj.append({'type': 'Feature', 'geometry': {'type': 'LineString', 'coordinates': coords},
                 'properties': {'id': f'T{n:02d}', 'nom': nom, 'debut': dec(a), 'fin': dec(b, True) if '/' in edtf else dec(a),
                                'date_edtf': edtf, 'certitude': CERT[cert], 'mode': mode, 'description': desc,
                                'sources': src, 'note': note, 'type': 'trajet'}})

# ---- Presse ancienne (Newspapers.com, dépouillement du 20 novembre 2026 ; voir salle-de-lecture.html#journaux)
NP = "Newspapers.com (abonnement de l'auteur), consulté le 20 novembre 2026"
L(59, "Saint-Louis : la maison du coin des rues Lombard et Second (1843-1850)", 'vie', '1831/1850-07-03', -90.1885, 38.6190, 'a',
  "Les listes fiscales de la ville situent les terrains de Provost dans le premier quartier : un lot bordant la rue Third dès 1831, puis des lots dans les îlots 49 (rue Lombard) et 76 (rue Cedar), voisins de ceux des Cailloux, Dufresne, Papin et Hernandez. Le 18 mai 1835, Étienne Provot et Marie Rose, sa femme, vendent la moitié d'un lot de l'îlot 76 à Sarah Ann Langley. L'avis de décès de 1850 confirme qu'il vivait « au coin des rues Lombard et Second ».",
  f"Missouri Republican, 8 mars et 19 avril 1831 ; 14 oct. 1834 ; Weekly Jefferson Inquirer, 29 juin 1843 ; St Louis Republic, 21-27 oct. 1843 ; déc. 1845 ; 5-25 févr. 1873 ; Tri-Weekly Missouri Republican, 4 juillet 1850 ; {NP}.",
  "Position approximative de l'angle des rues Lombard et Second dans l'ancien Frenchtown, aujourd'hui sous les échangeurs au sud de l'arche.")
L(60, "Comté de Lee (Iowa) : Provost parmi les requérants de la « Half-Breed Tract » (1840-1852)", 'traite', '1840-04-14/1852-11', -91.40, 40.52, 'a',
  "Le 14 avril 1840, Josiah Spalding, Archibald Gamble, Patrick Walsh, « Etienne Prevost », John B. Sarpy, Antoine Leclaire et d'autres demandent à la cour de district du comté de Lee le partage de la « Half-Breed tract », 119 000 acres entre le Mississippi et la rivière Des Moines réservées en 1824 aux Métis sauks et renards. Provost y détenait donc des droits, sans doute acquis comme créancier ou par sa famille. En 1852, après sa mort, une vente du shérif exécute encore un jugement en faveur des mêmes requérants.",
  f"The Hawk-Eye and Iowa Patriot (Burlington), 2 juillet-10 sept. 1840 ; Democratic Banner (Davenport), 26 mars-19 nov. 1852 ; {NP}.",
  "Point au centre de l'ancienne réserve (entre Keokuk et Fort Madison). L'origine des droits de Provost reste à établir.")
L(61, "Crow Creek : Provost impose le respect aux Yanktons (1847)", 'guide', '1847-06~', -99.33, 44.03, 'a',
  "Lors du premier voyage de Joseph La Barge comme capitaine de son propre vapeur, en 1847, les Yanktons de Crow Creek refusent le bois préparé pour le bateau et fouettent les hommes d'équipage qui tentent de le charger. Selon le récit publié en 1903 par la société historique du Dakota du Sud, Étienne Provost, « un frontalier intrépide dont les Indiens avaient peur », intervient et le bois est chargé. Le soir, l'attaque reprend et un batelier est tué.",
  f"Minneapolis Journal, 7 sept. 1903, p. 11 (« Row with Redskins », dépêche de Pierre) ; repris par l'Argus-Leader et d'autres ; {NP}.",
  "Embouchure du Crow Creek sur le Missouri (comté de Buffalo, Dakota du Sud), position approximative.")
L(62, "Village mandan : le tour du maïs joué au savant d'Audubon (1843)", 'guide', '1843-06~', -101.27, 47.26, 'h',
  "Joseph La Barge raconte qu'un des assistants d'Audubon se vantait de reconnaître n'importe quelle plante à sa feuille et à sa tige. Provost, qui servait de guide, cueille près d'un camp de Mandans une jeune pousse de maïs, n'en montre qu'une feuille et laisse le savant chercher en vain dans ses livres avant de lui révéler le grain resté à la racine. L'homme devient la risée de l'équipage.",
  f"Récit syndiqué dans une vingtaine d'hebdos du Montana et de l'Utah, 25 déc. 1919-23 janv. 1920 (ex. Cascade Courier, 26 déc. 1919) ; {NP}.",
  "Point aux villages mandans près de Fort Clark ; l'anecdote ne précise pas le lieu exact.")
L(63, "Kansas City : le monument de Jim Bridger rappelle le parti de Provost (1904)", 'posterite', '1904-12', -94.474, 39.082, 'c',
  "En décembre 1904, l'inauguration du monument de Jim Bridger au cimetière Mount Washington est l'occasion d'articles dans plusieurs grands journaux : à l'automne 1823, Ashley envoie un nouveau parti sous Étienne Provost, « trappeur et traiteur réputé », par la Bighorn et la Wind jusqu'à la Green ; Bridger en fait partie et ce parti découvre le col du Sud.",
  f"St. Louis Globe-Democrat, 18 déc. 1904 ; Kansas City Star, 23 déc. 1904 ; Salt Lake Herald et Omaha Bee, 25 déc. 1904 ; {NP}.",
  "Cimetière Mount Washington, Independence (Missouri).")
L(64, "Salt Lake City : plaque des Filles de la Révolution américaine (1926)", 'posterite', '1926-08-26', -111.8975, 40.7855, 'h',
  "Pour le centenaire de l'arrivée des premiers trappeurs, le chapitre Spirit of Liberty des Daughters of the American Revolution dévoile un monument avec plaque en l'honneur de James Bridger, Jedediah Smith et Étienne Provot, « au nouveau parc municipal en face de l'hôpital St. Mark's ». La femme du gouverneur Dern dévoile le monument et J. Cecil Alter retrace la vie des trois hommes.",
  f"Salt Lake Tribune, 26-27 août 1926 ; Ogden Standard-Examiner, 27 août 1926 ; Deseret News, 28 août 1926 ; dépêche United Press, 16-18 sept. 1926 ; {NP}.",
  "Position hypothétique : en face de l'ancien hôpital St. Mark's (803 North 200 West). L'emplacement actuel de la plaque reste à vérifier.")
L(65, "Ogden : l'alcôve où Provost aurait hiverné (1824-1825)", 'traite', '1824-11~/1825-03~', -111.96, 41.27, 'h',
  "D'après J. Cecil Alter, cité par l'Ogden Standard-Examiner en 1941, une alcôve abritée juste au nord du site actuel d'Ogden aurait servi de refuge d'hiver à Étienne Provot et à ses hommes en 1824-1825, puis de quartier d'hiver aux trappeurs d'Ashley en 1825-1826 et de site au rendez-vous de 1826.",
  f"Ogden Standard-Examiner, 13 juillet 1941 (« Ogden Locale for Trapper Confabs »), repris en 1942 et 1946 ; {NP}.",
  "Hypothèse d'Alter ; la plupart des historiens placent l'hiver de Provost près du lac Utah (L13). Point schématique au nord d'Ogden.")
L(66, "Provo : une statue de Provot dans le hall de la State Bank (1960)", 'posterite', '1960-05', -111.6590, 40.2343, 'a',
  "En 1960, la State Bank of Provo, fondée en 1902, inaugure un immeuble moderniste dont le hall abrite une statue contemporaine d'Étienne Provot, « le trappeur canadien-français dont la rivière et la ville de Provo tiennent leur nom ».",
  f"Salt Lake Tribune, 27 mai 1960 ; {NP}.",
  "Position approximative au centre-ville de Provo ; on ignore si la statue existe encore.")

# ---- Généalogie (arbre Ancestry, 20 novembre 2026)
L(67, "Chambly : la famille d'Albert Provost, trois mariages et quatorze enfants (1770-1813)", 'famille', '1770-01-29/1813-08-09', -73.2875, 45.4475, 'a',
  "Les registres de Saint-Joseph de Chambly permettent de reconstituer la famille d'Étienne. Son père Albert, fils de Gabriel Provost et de Marie-Anne Bourassa, épouse Marie-Louise Paquet le 29 janvier 1770 : naissent Marie-Louise (1771, morte en 1773), Isabelle (1773), Albert (1774), Joseph (1776), Charles (1778), Marie-Angélique (1779), Pierre (1781) et François-Marie (1782, mort en 1784). Veuf, il épouse Magdeleine Lebeau le 2 juin 1783, puis, veuf de nouveau, Marie-Anne Mainard le 25 janvier 1785. De ce dernier lit naissent Étienne (1785), Toussaint (1787), Julien (1789), Antoine (1790), Raphaël (1791) et François (1792), ces deux derniers morts en bas âge. Albert est inhumé le 5 mars 1796. Ses frères cadets restent au pays : Toussaint épouse Émilie Robert en 1806, Julien, Josephte Fréchette en 1813, alors qu'Étienne a sans doute déjà pris la route de l'Ouest.",
  "Drouin, Quebec, Canada, Vital and Church Records (Drouin Collection), 1621-1968, paroisse Saint-Joseph de Chambly (Ancestry, consulté le 20 novembre 2026) ; arbre Ancestry « Étienne Provost (1785-1850) – Atlas Provost » (O. J. Caron, 2026)",
  "Mêmes registres que la fiche L01 ; le point est décalé de l'église pour ne pas la masquer. La mère de Marie-Louise Paquet et celle de Magdeleine Lebeau, comme la date de mort de chaque épouse, restent à chercher.")
L(68, "Saint-Louis : Mary Rose Provost épouse James A. H. Pillsbury (1857-1880)", 'famille', '1857/1880', -90.1865, 38.6290, 'h',
  "Le 27 mai 1857, Mary Rose, fille d'Étienne, épouse à la cathédrale, devant le Rév. S. A. Paris, James A. H. Pillsbury, né vers 1827 au New Hampshire ; le Missouri Republican annonce le mariage de « Miss Mary R. Provat ». En 1860, le recensement les trouve dans le 3e quartier de Saint-Louis : il est épicier ; avec eux vivent leur fille Mary Frances, née vers 1860, et une Celestine Pillsbury de douze ans, dont le lien reste à établir. Un fils, Etienne A., naît vers 1862 : il porte le prénom du grand-père. En 1880, James, courtier retiré, et sa famille habitent au 900 Third Street. Etienne A. épouse Elizabeth Amplemen en décembre 1883. James meurt le 18 novembre 1889, à 62 ans, dans sa maison du 901 South Second Street, à deux pas de l'ancienne maison des Provost, rues Lombard et Second ; ses funérailles ont lieu à l'église de l'Annonciation.",
  "Recensements des États-Unis de 1860 (St. Louis Ward 3) et de 1880 (Saint-Louis), Ancestry ; Missouri Republican, 1er juin 1857 ; St. Louis Republic, 25 décembre 1883 ; St. Louis Globe-Democrat, 19 novembre 1889 et 31 août 1913 ; arbre Ancestry « Étienne Provost (1785-1850) – Atlas Provost »",
  "Point hypothétique : le 3e quartier de 1860 et le 900 Third Street sont placés dans le vieux Saint-Louis, près du fleuve, sans géocodage précis de l'adresse.")
L(69, "Saint-Louis : la descendance Grimm, de la 14e rue à l'avenue Virginia (1881-1913)", 'famille', '1881~/1913', -90.2475, 38.5790, 'c',
  "Vers 1881, Mary Frances Pillsbury, petite-fille d'Étienne, épouse Charles G. Grimm, né vers 1858 au Missouri, caissier d'une brasserie en 1910. Le couple a cinq enfants recensés : Mary E. (vers 1885), Clara E. (vers 1888), Margaret M. A. (vers 1894), Ferdinand (vers 1898) et Agnes Maria (1900). En 1900, ils vivent au 1322, 14e rue ; en 1910, au 4231 Virginia Avenue, dans le sud de la ville. Mary Rose, veuve, vit avec eux et meurt en 1913 tout près, au 4231 South 37th Street (fiche L43). L'avis de décès de 1913 nomme ses petits-enfants : sœur Mary of the Visitation, sœur Lucy du couvent du Bon-Pasteur, Margaret, Ferdinand et Agnes Grimm. Son fils Etienne A. Pillsbury meurt à Saint-Louis le 6 octobre 1927, laissant deux fils, Charles et Philip Pillsbury.",
  "Recensements des États-Unis de 1900 et de 1910 (Saint-Louis), Ancestry ; St. Louis Star and Times, 10 août 1913, p. 17 ; St. Louis Globe-Democrat, 9 août 1913 ; St. Louis Post-Dispatch, 7 octobre 1927 ; arbre Ancestry « Étienne Provost (1785-1850) – Atlas Provost »",
  "Point au 4231 Virginia Avenue (Dutchtown), position approximative. La 14e rue de 1900 n'est pas géocodée.")
L(70, "Carondelet : les Delor de Tréget, famille maternelle de l'épouse de Provost (1767-1837)", 'famille', '1767/1837-02-03', -90.2560, 38.5560, 'c',
  "La grand-mère de Mary Rose Provost s'appelle Madeleine Delor. Elle est la fille de Clément Delor de Tréget, « ancien officier au service du roi très chrétien », originaire de Cahors, qui quitte Sainte-Geneviève en 1767 pour fonder sur le Mississippi, au sud de Saint-Louis, le village qu'on appellera Carondelet, ou Vide-Poche, et de Catherine Marin. Le 31 décembre 1781, à Saint-Louis, Madeleine épouse en premières noces François Cailhol, de Marseille. Elle devient ensuite la femme de Lambert Salé dit Lajoie, dont elle a au moins Marie-Gertrude (1794), Caroline, Clément et Marie-Rose, la future Mme Provost. Elle est inhumée à Saint-Louis le 3 février 1837, « âgée de 78 ans ». En 1913, son nom reparaît, sous la forme « Madelin Delor », sur le certificat de décès de son arrière-petite-fille, comme celui de la mère de Mary Rose.",
  "Drouin, U.S., French Catholic Church Records (Drouin Collection), 1695-1954, Saint-Louis (vieille cathédrale) : mariage Cailhol – Delor, 31 décembre 1781 (registre des mariages 1781-1828, image 3) ; mariage Provost – Lambert, 4 août 1829 ; sépulture de « Mme Lambert Lajoie », 3 février 1837 (sépultures 1832-1847, image 27), Ancestry, lus le 20 novembre 2026 ; Missouri, U.S., Compiled Marriages, 1754-1850 ; Missouri State Board of Health, certificat de décès n° 27938 (1913) ; Chemins de la francophonie, « Carondelet, a Fathers' Rendez-vous » (en ligne)",
  "Point au cœur de l'ancien village de Carondelet. La date de naissance de Madeleine reste incertaine : 78 ans à sa sépulture donnerait vers 1759, alors que les arbres généalogiques en ligne retiennent le 4 août 1766 à Sainte-Geneviève, sans source citée. La date de son mariage avec Lambert Salé et le sort de François Cailhol restent à trouver.")
L(71, "Taos : l'enlèvement de María Rosa Villalpando, arrière-grand-mère de Mary Rose (1760)", 'famille', '1760-08-04', -105.6080, 36.3590, 'c',
  "Le 4 août 1760, des Comanches attaquent l'estancia de Pablo Villalpando, près de Taos, au Nouveau-Mexique, tuent les défenseurs et emmènent une cinquantaine de femmes et d'enfants. Parmi eux, María Rosa Villalpando, dont le jeune fils échappe au raid. Revendue aux Pawnees, elle y rencontre le traiteur Jean Salé dit Lajoie, qui l'emmène à Saint-Louis avec leur fils Lambert, né en 1768 ; ils s'y marient en 1770. Lambert est le père de Marie-Rose, l'épouse d'Étienne Provost : Mary Rose Provost est donc l'arrière-petite-fille de la captive de Taos. María Rosa meurt à Saint-Louis en juillet 1830 ; le registre de la vieille cathédrale l'inhume le 28 juillet, « femme de Jean Salé », âgée selon lui de cent quatre ans. Le mariage de Provost avec sa petite-fille avait eu lieu un an plus tôt. Un autre de ses petits-fils, Antoine Leroux, fils d'Hélène Salé, deviendra un guide célèbre du Sud-Ouest et se fixera à Taos.",
  "Tykal, Jack B. (1990), « Taos to St. Louis: The Journey of Maria Rosa Villalpando », New Mexico Historical Review, 65 (2), p. 162-167 ; Brooks, James F. (2002), Captives and Cousins, Chapel Hill, University of North Carolina Press ; Wikipédia, « Maria Rosa Villalpando » (consulté le 20 novembre 2026) ; New Mexico Historic Women, « Maria Rosa Villapando » (en ligne) ; Drouin, U.S., French Catholic Church Records (Drouin Collection), 1695-1954, Saint-Louis (vieille cathédrale), sépultures 1781-1832, acte du 28 juillet 1830 (image 168) ; mariage Provost – Lambert, 4 août 1829 ; Missouri, U.S., Compiled Marriages, 1754-1850 (Hélène Salé × Benjamin Leroux, 7 janvier 1792)",
  "Fiche généalogique hors de la vie d'Étienne, comme L02. Point à Ranchos de Taos. L'âge de 104 ans au registre est exagéré : les historiens placent sa naissance vers 1738. Jack B. Tykal, biographe de Provost, a aussi publié l'étude de référence sur María Rosa Villalpando. Antoine Leroux est donc le cousin germain de l'épouse de Provost.")

L(72, "Saint-Louis : Provost se porte caution pour la succession de son beau-père Lambert Salé dit Lajoie (22 février 1837)", 'famille', '1837-02-22', -90.1893, 38.6255, 'c',
  "Le 22 février 1837, devant la cour du comté de Saint-Louis, Clément Sallé dit Lajoie, frère de Marie-Rose, prend la charge d'administrateur « de bonis non, avec le testament annexé » de la succession de son père, Lambert Sallé dit Lajoie, mort en 1834. Il doit s'engager pour 1 000 $ envers l'État du Missouri, garantis par deux cautions : Étienne Provost (« Etienne Provos »), son beau-frère, et John B. Sarpy, l'un des associés de Pierre Chouteau Jr. & Co., qui emploie alors Provost. Clément signe ; Provost, qui ne sait pas écrire, trace une croix entre « his » et « mark », comme sur son acte de mariage de 1829. L'acte est enregistré le 1er mars 1837 par le greffier Henry Chouteau. La formule « de bonis non » désigne l'administration des biens qui restent à régler quand le premier exécuteur ne peut plus agir : la veuve, Madeleine Delor, avait été inhumée dix-neuf jours plus tôt, le 3 février (fiche L70). Quelques semaines plus tard, Provost repart vers les montagnes avec la caravane de la compagnie (fiche L31).",
  "Cautionnement (« Know All Men by These Presents… ») de Clément Sallé alias Lajoie, administrateur de la succession de Lambert Sallé dit Lajoie, avec Étienne Provos et John B. Sarpy pour cautions, Saint-Louis, 22 février 1837, enregistré le 1er mars 1837 (Henry Chouteau, greffier), cour du comté de Saint-Louis ; Missouri, U.S., Wills and Probate Records, succession de Lambert Salle, Saint-Louis (dossier n° 1153), document fourni par l'auteur de l'atlas",
  "Point au palais de justice de Saint-Louis (site de l'actuel Old Courthouse, rues Fourth et Market), où siégeait la cour de comté. Le formulaire porte le mot « Execut[rix] » biffé : il visait un exécuteur précédent, sans doute la veuve. Que Madeleine Delor ait été l'exécutrice testamentaire de son mari reste une déduction, que le testament de Lambert (non lu) permettrait de vérifier. Le document confirme que Provost est le beau-frère de Clément, que l'American Fur Company soutient ses affaires de famille, et qu'il est à Saint-Louis à la fin de l'hiver 1837.")
L(73, "Saint-Louis : la maison du coin des rues Lombard et Second (vers 1840-1916)", 'vie', '1843/1916', -90.19038, 38.61662, 'c',
  "La maison où Étienne Provost meurt le 3 juillet 1850 se trouvait « au coin des rues Lombard et Second », dans le Frenchtown, au sud de la vieille ville. Le rôle d'impôt de 1843 le place à l'extrémité est de l'îlot 49, du côté sud de la rue Lombard ; les annuaires de 1840-1845 inscrivent un « H. N. Provost », épicier, à l'angle sud-ouest de Second et Lombard ; le plan de Hutawa (1850) montre l'îlot 49 à cet angle précis. Après la numérotation de 1866, la maison d'angle devient le 901 South Second Street : la famille y reste au moins jusqu'en 1889. Mary Frances Grimm, petite-fille d'Étienne, y perd un enfant en 1882 ; des Maskow, parents de Mary Rose, y vivent en 1884 et 1888 ; James A. H. Pillsbury, son mari, y meurt en 1889. La carte Sanborn de 1908 y montre un immeuble de brique de deux étages avec commerce au rez-de-chaussée ; il est encore habité en 1916. L'angle est aujourd'hui traversé par la voie ferrée d'accès au pont MacArthur, dans le quartier de Chouteau's Landing.",
  "St. Louis Republic, liste fiscale, 24 octobre 1843 (îlots 49 et 76) ; Green's St. Louis Directory, 1840-1845, d'après " + AA + " ; Tri-Weekly Missouri Republican, 4 juillet 1850 ; Hutawa, Julius (1850), Plan of the City of St. Louis, Missouri Historical Society, version géoréférencée de la St. Louis Genealogical Society ; St. Louis Post-Dispatch, 21 juillet 1882 ; St. Louis Republic, 13 septembre 1884 ; St. Louis Globe-Democrat, 24 septembre 1888 et 19 novembre 1889 ; Sanborn Map Co., St. Louis, décembre 1908, feuilles 74 et 76 (MU Digital Library) ; St. Louis Republic, 30 mai 1916 ; OpenStreetMap (2026)",
  "Point à l'angle sud-ouest de l'intersection actuelle de Lombard Street et South 2nd Street (38,61662 N ; 90,19038 O ; intersection : 38,616765 N ; 90,190243 O). On ignore si l'immeuble de 1908 est la maison de Provost ou un bâtiment plus récent, et la date exacte de sa démolition, sans doute liée aux approches ferroviaires du pont MacArthur, mises en service en 1928. Voir l'onglet « La maison de la rue Lombard » de la salle de lecture.")


def JX(fichier, legende, article):
    return {"src": f"images/journaux/{fichier}", "legende": legende, "article": article}
def RG(fichier, legende):
    return {"src": f"images/arbre/{fichier}", "legende": legende, "article": "mere", "type": "registre"}
def TS(fichier, legende):
    return {"src": f"images/testament/{fichier}", "legende": legende, "article": "testament", "type": "registre"}
def MS(fichier, legende):
    return {"src": f"images/maison/{fichier}", "legende": legende, "article": "maison", "type": "registre"}
REGISTRES = {
  'L73': [MS("1908-sanborn-feuille-74-ilot-49-901-s-2nd.jpg", "Carte Sanborn, décembre 1908, feuille 74 : le 901 South 2nd Street, à l'angle de Lombard"),
          MS("1850-plan-hutawa-geo-stlgs-lombard-second.jpg", "Plan de Hutawa (1850) géoréférencé : l'îlot 49 à l'angle sud-ouest de Second et Lombard"),
          TS("1839-testament-p1-b.jpg", "Testament d'Étienne Provot, 1er avril 1839 : « on the Corner of Lombard and Second Streets… it being the same on which I now reside »"),
          TS("1850-08-01-inventaire-a.jpg", "Inventaire de la succession, 1er août 1850 : îlot 49, 50 pieds sur Second, 150 sur Lombard, borné à l'ouest par Papin et au sud par Pilcher")],
  'L40': [TS("1850-07-24-rejet-du-testament.jpg", "Le juge des successions rejette le testament d'Étienne, ses trois témoins étant morts, 24 juillet 1850"),
          TS("1850-07-04-facture-cercueil-lynch.jpg", "Facture des pompes funèbres Wm. A. Lynch & Co. : cercueil de velours, corbillard et cinq voitures, 4 juillet 1850")],
  'L60': [TS("1850-08-01-inventaire-b.jpg", "Inventaire de 1850 : plus de 600 acres et une douzaine de lots à Keokuk et Nashville, comté de Lee (Iowa), issus de la réserve métisse")],
  'L24': [RG("1829-08-04-mariage-provost-lambert.jpg", "Acte de mariage d'Étienne Provost et de Marie Lambert, « fille de Lambert Salé, dit Lajoy, et Magdeleine Delor », Saint-Louis, 4 août 1829")],
  'L25': [RG("1829-08-04-mariage-provost-lambert.jpg", "Le mariage de 1829 nomme Magdeleine Delor, la « Madelin Delor » du certificat de 1913")],
  'L70': [RG("1781-12-31-mariage-cailhol-delor.jpg", "Mariage de François Cailhol et de « demoiselle Madeleine de Lord, fille légitime de Clément Delord, ancien officier au service du roi très chrétien, et de dame Catherine Marin », 31 décembre 1781"),
          RG("1837-02-03-sepulture-madeleine-delor.jpg", "Sépulture de « feue Mme Lambert Lajoie, âgée de 78 ans », 3 février 1837")],
  'L72': [RG("1837-02-22-cautionnement-succession-lambert-sale.jpg", "Cautionnement de Clément Sallé alias Lajoie, administrateur de la succession de Lambert Sallé dit Lajoie, avec pour cautions « Etienne Provos » (sa marque) et John B. Sarpy, Saint-Louis, 22 février 1837")],
  'L71': [RG("1830-07-28-sepulture-maria-rosa-villalpando.jpg", "Sépulture de « Marie Rose […] femme de Jean Salé », âgée de cent quatre ans, Saint-Louis, 28 juillet 1830")],
}
PRESSE = {
  'L03': [JX("1827-11-08-missouri-republican-lettres-etienne-proveau.jpg", "Missouri Republican, 8 nov. 1827 : lettre en souffrance pour « Etienne Proveau »", "jx-1827")],
  'L21': [JX("1834-05-01-missouri-republican-licence-taverne-provost.jpg", "Missouri Republican, 1er mai 1834 : licences de « Provost, Etien », marchand et tavernier", "jx-1834")],
  'L28': [JX("1834-08-26-missouri-republican-from-the-mountains.jpg", "Missouri Republican, 26 août 1834 : « From the Mountains »", "jx-1834b")],
  'L36': [JX("1843-listes-fiscales-lots-provost-lombard-cedar.jpg", "Listes fiscales de 1843 : les lots voisins de Provost, rues Lombard et Cedar", "jx-quartier"),
          JX("1846-01-14-st-louis-republic-cour-de-circuit-provost.jpg", "St Louis Republic, 14 janv. 1846 : procès contre Provost et ses voisins", "jx-quartier")],
  'L37': [JX("1891-04-12-post-dispatch-la-barge-trip-in-43.jpg", "St. Louis Post-Dispatch, 12 avril 1891 : La Barge, « A Trip in '43 »", "jx-1843")],
  'L38': [JX("1891-04-12-post-dispatch-la-barge-trip-in-43.jpg", "St. Louis Post-Dispatch, 12 avril 1891 : Audubon redescend accompagné d'« Etienne Proveau »", "jx-1843")],
  'L39': [JX("1903-09-07-minneapolis-journal-row-with-redskins.jpg", "Minneapolis Journal, 7 sept. 1903 : « Row with Redskins »", "jx-1847")],
  'L40': [JX("1850-07-04-tri-weekly-missouri-republican-avis-de-deces.jpg", "Tri-Weekly Missouri Republican, 4 juillet 1850 : avis de décès", "jx-1850"),
          JX("1850-07-30-missouri-republican-succession-etienne-provot.jpg", "Missouri Republican, 30 juillet 1850 : avis de l'administratrice Mary Provot", "jx-1850")],
  'L17': [JX("1902-06-24-nebraska-city-weekly-morton-col-du-sud.jpg", "Nebraska City Weekly, 24 juin 1902 : la tradition attribue le col du Sud à Provost", "jx-colsud"),
          JX("1904-12-25-salt-lake-herald-monument-bridger-provost.jpg", "Salt Lake Herald, 25 déc. 1904 : le parti de Provost, 1823", "jx-colsud")],
  'L11': [JX("1912-07-24-deseret-news-the-coming-of-provot.jpg", "Deseret News, 24 juillet 1912 : « The Coming of Provot »", "jx-massacre"),
          JX("1955-12-08-idaho-state-journal-bd-frontier-scout-provot.jpg", "Idaho State Journal, 8 déc. 1955 : la bande dessinée Dan'l Hale", "jx-massacre")],
  'L42': [JX("1909-01-30-intermountain-catholic-etienne-provot.jpg", "Intermountain Catholic, 30 janv. 1909 : Provot, et non Provost", "jx-nom"),
          JX("1924-02-26-provo-daily-herald-he-named-provo.jpg", "The Daily Herald (Provo), 26 févr. 1924 : « He Named Provo »", "jx-nom"),
          JX("1934-01-24-watson-two-names-on-utahs-map.jpg", "Elmo Scott Watson, « Two Names on Utah's Map », 1934", "jx-nom")],
  'L43': [JX("1913-08-31-globe-democrat-mort-de-mary-rose-pillsbury.jpg", "St. Louis Globe-Democrat, 31 août 1913 : mort de Mary Rose Pillsbury", "jx-1913"),
          JX("1913-08-09-globe-democrat-avis-deces-mary-rose-pillsbury.jpg", "St. Louis Globe-Democrat, 9 août 1913 : avis de décès de Mary Rose Pillsbury", "mere")],
  'L68': [JX("1857-06-01-missouri-republican-mariage-pillsbury-provat.jpg", "Missouri Republican, 1er juin 1857 : mariage de James A. H. Pillsbury et de « Miss Mary R. Provat »", "mere"),
          JX("1889-11-19-globe-democrat-deces-james-a-pillsbury.jpg", "St. Louis Globe-Democrat, 19 novembre 1889 : mort de James A. Pillsbury", "mere")],
  'L69': [JX("1927-10-07-post-dispatch-deces-etienne-pillsbury.jpg", "St. Louis Post-Dispatch, 7 octobre 1927 : mort d'Etienne Pillsbury", "mere")],
  'L44': [JX("1946-12-15-sunday-herald-statue-this-is-the-place.jpg", "Sunday Herald (Provo), 15 déc. 1946 : la statue remplace Kit Carson", "jx-monuments"),
          JX("1947-07-24-deseret-news-devoilement-petit-neveu.jpg", "Deseret News, 24 juillet 1947 : un petit-neveu au dévoilement", "jx-monuments")],
  'L35': [JX("1880-07-18-globe-democrat-mort-de-louis-st-onge.jpg", "St. Louis Globe-Democrat, 18 juillet 1880 : Provost parmi les pionniers du haut Missouri", "jx-1880")],
  'L59': [JX("1850-07-04-tri-weekly-missouri-republican-avis-de-deces.jpg", "4 juillet 1850 : « from his late residence on the corner of Lombard and Second streets »", "jx-1850"),
          JX("1873-02-05-st-louis-republic-acte-1835-provot-marie-rose.jpg", "St Louis Republic, 5 févr. 1873 : l'acte de 1835 d'Étienne Provot et Marie Rose", "jx-quartier")],
  'L60': [JX("1840-hawk-eye-burlington-half-breed-tract.jpg", "Hawk-Eye and Iowa Patriot, juillet 1840 : la requête en partage", "jx-1840")],
  'L61': [JX("1903-09-07-minneapolis-journal-row-with-redskins.jpg", "Minneapolis Journal, 7 sept. 1903 : « Row with Redskins »", "jx-1847")],
  'L62': [JX("1919-12-25-montana-provost-et-le-savant-prou.jpg", "Dépêche de décembre 1919 : Provost et le savant", "jx-1843")],
  'L63': [JX("1904-12-25-salt-lake-herald-monument-bridger-provost.jpg", "Salt Lake Herald, 25 déc. 1904 : « Tribute to the Discoverer of Salt Lake »", "jx-colsud")],
  'L64': [JX("1926-08-26-salt-lake-tribune-monument-trail-breakers.jpg", "Salt Lake Tribune, 26 août 1926 : « Honor Is Given in Monument to Trail Breakers »", "jx-monuments")],
  'L65': [JX("1941-07-13-ogden-standard-examiner-refuge-hiver-1824.jpg", "Ogden Standard-Examiner, 13 juillet 1941 : « Ogden Locale for Trapper Confabs »", "jx-ogden")],
  'L66': [JX("1960-05-27-salt-lake-tribune-statue-banque-provo.jpg", "Salt Lake Tribune, 27 mai 1960 : la statue de la State Bank of Provo", "jx-monuments")],
}
NOTE_PRESSE = {
  'L03': " Dès novembre 1827, le Missouri Republican annonce une lettre en souffrance à la poste pour « Etienne Proveau ».",
  'L21': " Les listes de licences municipales publiées par le Missouri Republican (17 mai 1833, 1er mai 1834) inscrivent « Provost, E. » ou « Provost, Etien » comme vendeur de marchandises et tenancier de taverne.",
  'L28': " Le Missouri Republican du 26 août 1834 rassure les familles : le parti de « M. Provost (de l'American Fur Company) » n'a pas été attaqué par les Pawnees ; il comptait quitter le rendez-vous de la Ham's Fork vers la mi-juillet.",
  'L40': " Le 29 juillet 1850, Mary Provot obtient les lettres d'administration de la succession ; l'avis aux créanciers paraît dans le Missouri Republican jusqu'au 20 septembre.",
  'L43': " Nécrologie dans le St. Louis Globe-Democrat du 31 août 1913 : « Miss Mary Rose Provost, daughter of Etienne Provost, an attaché of the American Fur Company with the reputation of being a daring explorer ».",
  'L44': " Selon le Sunday Herald de Provo (15 déc. 1946), la statue de Provot a pris la place prévue pour Kit Carson, jugé moins lié à l'histoire de l'Utah. Au dévoilement du 24 juillet 1947, un petit-neveu, l'évêque E. Orval Provost, officie avec Charles Washakie.",
  'L37': " Joseph La Barge, dans le Post-Dispatch du 12 avril 1891, rappelle qu'Audubon redescendit le Missouri en mackinaw « accompagné d'Etienne Proveau, le célèbre trappeur et chasseur ».",
}
for f_ in lieux:
    p = f_['properties']
    if p['id'] in PRESSE:
        p['presse'] = PRESSE[p['id']]
    if p['id'] in REGISTRES:
        p['registres'] = REGISTRES[p['id']]
    if p['id'] in NOTE_PRESSE:
        p['note'] = (p['note'] + NOTE_PRESSE[p['id']]).strip()
    if p['id'] in PRESSE and 'Newspapers.com' not in p['sources']:
        p['sources'] += f" ; presse : {NP}"

P = {f['properties']['id']: f['geometry']['coordinates'] for f in lieux}
T(1, "De Chambly à Saint-Louis par le saut Sainte-Marie, Détroit et Chicago", 'canot', '1806~/1810~', [P['L01'], [-73.55, 45.51], [-76.0, 45.6], [-79.4, 46.3], [-81.5, 46.0], [-84.35, 46.5], [-84.0, 45.3], [-82.5, 43.0], [-83.05, 42.33], [-86.4, 41.9], [-87.62, 41.88], [-88.9, 41.2], [-89.6, 40.7], [-90.18, 38.95], P['L03']], 'h',
  "Entre 1806 et 1810, Provost aurait quitté la vallée du Saint-Laurent avec une brigade de canots par l'Outaouais jusqu'au saut Sainte-Marie, puis bifurqué vers Détroit, le portage de Chicago, la rivière des Illinois et Peoria, et enfin le Mississippi jusqu'à Saint-Louis, où vivaient déjà des oncles et cousins Provost et Ménard.",
  f"{BOU} ; {VA} ; {TYU}", "Itinéraire proposé par Bouchard et Lévesque ; tracé schématique.")
T(2, "Avec Philibert vers le haut Arkansas", 'cheval', '1814', [P['L03'], [-94.4, 38.9], [-98.6, 38.35], [-101.2, 37.93], P['L04']], 'h',
  "La troupe de Joseph Philibert gagne le haut Arkansas, par le Missouri puis les plaines du Kansas.", TYU, "Tracé schématique.")
T(3, "L'expédition Chouteau-De Mun", 'cheval', '1815-09/1816', [P['L03'], [-94.4, 38.9], [-98.6, 38.35], P['L06'], [-103.5, 38.05], [-104.61, 38.26], [-105.0, 37.17], P['L05']], 'a',
  "Partis de Saint-Louis en septembre 1815, Chouteau et De Mun suivent l'Arkansas jusqu'aux montagnes, puis descendent vers Taos.", f"{ROY} ; {TYU}", "Tracé schématique le long de l'Arkansas.")
T(4, "Prisonniers jusqu'à Santa Fe", 'cheval', '1817-05', [[-104.61, 38.26], [-105.0, 37.17], P['L05'], P['L07']], 'a',
  "Arrêtés en mai 1817, les hommes de Chouteau et De Mun sont conduits sous escorte à Santa Fe.", f"{ROY} ; {OSF}", "Le lieu exact de l'arrestation, sur le haut Arkansas, est approximatif.")
T(5, "Relâchés : le retour à Saint-Louis", 'cheval', '1817-07/1817-09', [P['L07'], [-104.6, 37.0], [-103.0, 37.6], P['L06'], [-98.6, 38.35], [-94.4, 38.9], P['L03']], 'h',
  "Dépouillés de leurs fourrures, les prisonniers libérés regagnent Saint-Louis par les plaines.", ROY, "Tracé schématique.")
T(6, "De Saint-Louis à Taos par la piste de Santa Fe", 'cheval', '1822~', [P['L03'], [-94.4, 38.9], [-96.5, 38.66], [-98.6, 38.35], [-101.2, 37.93], [-103.5, 38.05], [-104.6, 37.0], P['L08']], 'h',
  "Vers 1822, Provost revient au Nouveau-Mexique par la piste de Santa Fe, que Becknell vient d'ouvrir.", TYU, "Tracé schématique (branche de la montagne).")
T(7, "De Taos au bassin de la Uinta par la branche nord de la Vieille Piste espagnole", 'cheval', '1824-05~/1824-08~', [P['L09'], [-106.0, 37.47], [-106.9, 38.5], [-108.0, 38.7], [-108.55, 39.06], [-109.3, 39.55], P['L10']], 'a',
  "Provost et Leclerc gagnent le pays de la Uinta par la vallée de San Luis, le Gunnison et la vallée du Colorado, la route des trappeurs de Taos.",
  f"{NEL96} ; {NEL('40-41')}", "Tracé schématique de la branche nord.")
T(8, "De la Uinta au lac Utah", 'cheval', '1824-09~/1824-10', [P['L10'], [-110.4, 40.17], [-111.0, 40.17], [-111.35, 40.3], [-111.6, 40.33], P['L13'], P['L11']], 'h',
  "La troupe passe à l'ouest par la Duchesne et le Strawberry, puis descend vers le lac Utah et la Jordan.", f"{TYU} ; {UTG}", "Tracé hypothétique.")
T(9, "La fuite par les Wasatch", 'cheval', '1824-10/1824-11', [P['L11'], [-111.7, 40.75], [-111.4, 40.95], [-110.9, 40.75], [-110.2, 40.4], P['L10']], 'h',
  "Les survivants du massacre s'échappent vers le nord-est par les Wasatch, puis regagnent la région de la Green et de la White pour l'hiver.", f"{UTG} ; {NEL96}", "Tracé hypothétique.")
T(10, "Printemps 1825 : vers la Weber", 'cheval', '1825-04/1825-05', [P['L10'], [-110.4, 40.6], [-111.0, 40.85], [-111.4, 41.05], P['L14']], 'h',
  "Au printemps, Provost reprend la chasse vers la Weber, où il croise Ogden.", TYU, "Tracé hypothétique.")
T(11, "De la Weber à Fruitland", 'cheval', '1825-05/1825-06', [P['L14'], [-111.4, 40.95], [-111.0, 40.5], P['L15']], 'h',
  "Provost revient vers le sud-est, dans le bassin de la Duchesne, où il rencontre Ashley.", TYU, "Tracé hypothétique.")
T(12, "Avec Ashley vers le premier rendez-vous", 'cheval', '1825-06/1825-07', [P['L15'], [-110.5, 40.5], [-110.3, 40.7], [-110.05, 40.85], P['L16']], 'a',
  "Provost guide Ashley par la Duchesne et le Strawberry, puis au nord à travers les Uinta, jusqu'à l'Henry's Fork.", f"{TYU} ; {NEL(40)}", "Tracé schématique.")
T(13, "Le retour par le Missouri", 'canot', '1826-07~/1826-09', [P['L16'], [-108.9, 42.35], [-106.3, 42.85], [-104.0, 43.9], [-102.0, 44.2], P['L19'], [-97.4, 42.87], [-95.9, 41.26], [-94.6, 39.1], [-92.2, 38.6], P['L20']], 'h',
  "De la Green River, Provost gagne le Missouri et le descend jusqu'à Saint-Louis, où il est de retour en septembre 1826.", f"{HF(376)} ; {HU}", "Tracé hypothétique ; le passage par le fort Lookout vient de la notice de Hafen.")
T(14, "Saint-Louis – fort Floyd : au service de McKenzie", 'canot', '1828-04~/1828-08~', [P['L20'], [-92.2, 38.6], [-94.6, 39.1], [-95.9, 41.26], [-97.4, 42.87], P['L19'], [-100.38, 44.4], [-101.4, 47.3], P['L22']], 'a',
  "Provost remonte le Missouri jusqu'au poste de McKenzie à l'embouchure de la Yellowstone.", f"{DOL(325)} ; {HF(377)}", "Tracé schématique le long du Missouri.")
T(15, "À la recherche des trappeurs libres", 'cheval', '1828-09~/1829-04~', [P['L22'], [-105.8, 46.4], [-107.5, 45.6], [-108.4, 43.2], [-108.9, 42.35]], 'h',
  "De l'embouchure de la Yellowstone, Provost remonte vers le pays crow et les montagnes pour rallier les trappeurs libres à l'American Fur Company.", f"{DOL(325)} ; {CH('305-306')}", "Tracé hypothétique.")
T(16, "Avec Fontenelle et Drips : Bayou Salade et Ham's Fork", 'cheval', '1834-04~/1834-07', [P['L29'], [-98.4, 40.7], [-101.0, 41.1], [-103.0, 40.6], [-104.99, 39.74], P['L27'], [-106.5, 40.8], [-107.8, 41.6], [-109.2, 41.6], P['L28']], 'h',
  "Partie du Missouri, la caravane de l'American Fur Company gagne le Bayou Salade, puis le rendez-vous de la Ham's Fork.", HF('379-380'), "Tracé hypothétique.")
T(17, "La barge des fourrures descend vers Bellevue", 'canot', '1834-08~/1834-09~', [P['L28'], [-108.9, 42.35], [-106.3, 42.85], [-104.56, 42.2], [-102.0, 41.1], [-99.5, 40.7], [-96.5, 41.0], P['L29']], 'h',
  "Les fourrures de la saison descendent vers Bellevue, par la Platte puis le Missouri.", f"{CH(475)}", "Tracé hypothétique ; la Platte est peu navigable et les fourrures voyagent souvent à dos de mulet jusqu'au Missouri.")
T(18, "La caravane de 1837 vers le rendez-vous de Horse Creek", 'cheval', '1837-05/1837-07', [P['L03'], [-94.42, 39.25], [-96.5, 40.4], [-98.6, 40.7], [-101.0, 41.1], [-103.0, 41.7], P['L30'], [-106.3, 42.85], [-108.9, 42.35], P['L31']], 'a',
  "Chef en second de la caravane de l'American Fur Company, Provost suit la route de la Platte et du col du Sud jusqu'au rendez-vous de la Green River, avec le peintre Miller.", f"{VA} ; {TYU}", "Tracé schématique (route de l'Oregon).")
T(19, "Avec Nicollet, du fort Pierre au lac du Diable", 'cheval', '1839-07-03/1839-07-28', [P['L33'], [-99.6, 45.0], [-98.7, 45.9], [-98.6, 46.9], P['L34']], 'a',
  "L'expédition de Nicollet et Frémont traverse le coteau du Missouri et remonte la James jusqu'au lac du Diable.", f"{NIC} ; {TYU}", "Tracé schématique.")
T(20, "Avec Audubon sur l'Omega, de Saint-Louis au fort Union", 'vapeur', '1843-04-25/1843-06-12', [P['L03'], [-92.2, 38.6], [-94.6, 39.1], [-95.9, 41.26], [-97.4, 42.87], [-99.4, 43.95], [-100.38, 44.4], [-101.4, 47.3], P['L37']], 'c',
  "Le vapeur Omega de l'American Fur Company emmène Audubon, ses compagnons et ses chasseurs, avec Provost et sa fille, jusqu'au fort Union en sept semaines.", f"{AUD} ; {VA}", "Tracé schématique le long du Missouri.")
T(21, "La descente du Missouri en mackinaw", 'canot', '1843-08-16/1843-10-18', [P['L37'], [-101.4, 47.3], [-100.38, 44.4], [-99.4, 43.95], [-97.4, 42.87], [-95.9, 41.26], [-94.6, 39.1], [-92.2, 38.6], P['L38']], 'c',
  "Audubon et sa troupe redescendent le Missouri en barque (mackinaw) jusqu'à Saint-Charles, où Provost débarque le 18 octobre.", f"{VA} ; {AUD}", "Tracé schématique.")
T(22, "Le dernier bout de chemin, à pied", 'cheval', '1843-10-18', [P['L38'], [-90.33, 38.70], P['L36']], 'c',
  "Ivre et joyeux, Provost fait à pied la trentaine de kilomètres de Saint-Charles à Saint-Louis.", VA, "Mode : à pied.")

for nom, fs in (('lieux', lieux), ('trajets', traj)):
    json.dump({'type': 'FeatureCollection', 'features': fs}, open(f'{OUT}/data/{nom}.geojson', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(lieux), 'lieux,', len(traj), 'trajets')
