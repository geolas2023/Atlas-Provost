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
  "Étienne Provost naît à Chambly, sur le Richelieu, le 21 décembre 1785. Il est le premier enfant du troisième mariage d'Albert Provost, cultivateur prospère, père d'une quinzaine d'enfants, et de Marie-Anne Mainard (Ménard). Son père meurt quand il a onze ans ; il ne saura jamais lire ni écrire. On ne sait presque rien de sa jeunesse ; il n'a pas vingt ans, écrit Denis Vaugeois, quand il choisit la traite des fourrures et le Far West, avec Saint-Louis pour base.",
  f"{VA} ; {BOU} ; {TYU} ; {ROQ}",
  "Date du jour d'après Vaugeois ; Tykal et Hafen donnent seulement 1785. La photothèque de la Utah State Historical Society propose 1782. Point à l'église Saint-Joseph de Chambly.")
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
L(24, "Saint-Louis : mariage avec Marie-Rose Lambert, belle-fille de Lambert Salé dit Lajoie (4 août 1829)", 'famille', '1829-08-04', -90.1857, 38.6243, 'c',
  "Rentré à Saint-Louis le 27 juillet 1829, Provost apprend que Marie-Rose Lambert, belle-fille de son associé Lambert Salé dit Lajoie, de douze ans sa cadette, est veuve depuis l'automne ; il la connaît depuis 1826 au moins. Le mariage est fixé au 4 août et béni par le jésuite Joseph Anthony Lutz ; les témoins sont Lambert Salé, Marie Ménard et « Mr J. Laberge », sans doute Joseph-Marie La Barge, père du futur pilote. Provost achète pour la noce couvertures, casinette, étoffe écarlate et dentelle d'argent. L'union a aussi une dimension commerciale ; dès l'été 1829, Marie-Rose apparaît comme créditrice dans les registres de la compagnie.",
  f"{HAV}, p. 339-340 ; {TYU} ; {VA} ; {BOU} ; registre des sépultures de la vieille cathédrale de Saint-Louis, 4 juillet 1850, d'après {AA}",
  "La date de Havard, tirée des registres paroissiaux et des comptes de l'AFC, règle la question : Vaugeois, qui donne à l'épouse 31 ans et à Provost 46, plaçait le mariage vers 1831-1832. Les noms varient : « Marie Rose Salle Dupuis » (Vaugeois), « Marie-Rose La Salle » (De remarquables oubliés), « Maria Rose Lombard » (registre de 1850). Point à la vieille cathédrale.")
L(25, "Saint-Louis : naissance de Mary Rose, « fille d'Étienne Provo » (1er mai 1830)", 'famille', '1830-05-01', -90.1860, 38.6255, 'a',
  "Le certificat de décès de Mary Rose Pillsbury (1913) la dit née à Saint-Louis le 1er mai 1830, fille d'« Etienne Provo », né au Canada. La date tombe un an après le mariage : ce serait la fille unique connue du couple, qu'Audubon voit à bord du vapeur en 1843.",
  "Missouri State Board of Health, certificat de décès n° 27938, Mary Rose Pillsbury, Saint-Louis, 8 août 1913 (Drive de l'auteur) ; " + AUD,
  "Le certificat nomme la mère « Madelin Delor », nom qui ne correspond à aucune forme connue de l'épouse. Filiation à vérifier dans les registres de baptême de la vieille cathédrale. Point schématique dans la vieille ville.")
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
  "À vérifier : l'entrée d'Étienne dans l'annuaire de 1847 (p. 153). Le quartier est aussi celui de Moïse Lamoureux, natif de Chambly.")
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
  "Point à la vieille cathédrale (basilique Saint-Louis-Roi-de-France).")

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
  "Audubon ne nomme pas ce beau-frère. Provost avait épousé en 1829 Marie-Rose Lambert, belle-fille de Lambert Salé dit Lajoie (fiche L24) ; il pourrait s'agir d'un frère ou demi-frère de Marie-Rose, mais rien ne le confirme ici.")

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
  "Mary Rose Pillsbury, veuve, sans doute de James A. Pillsbury, meurt à 83 ans au 4231 South 37th Street ; elle est inhumée au cimetière Calvary le 11 août 1913. Son certificat de décès la dit fille d'« Etienne Provo », né au Canada.",
  "Missouri State Board of Health, certificat de décès n° 27938, Mary Rose Pillsbury, 8 août 1913 (Drive de l'auteur)", "")
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
