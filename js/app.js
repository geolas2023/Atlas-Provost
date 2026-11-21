// Atlas Étienne Provost — carte MapLibre + timeline + journal de bord
// Les entités ont des attributs numériques « debut » et « fin » (années décimales : 1697.68 = début septembre 1697).
// La timeline affiche toutes les entités commencées avant la date choisie (affichage cumulatif).
//
// Échelle de la timeline en deux segments :
//   - 1785 à 1813, par année (jeunesse, peu documentée), en segment compressé ;
//   - 1814 à 1850, par mois.
// La dernière position (max) = « toutes les dates ».
// Langue de la page : <html lang="en"> (index-en.html) affiche l'interface et les données en anglais.
const EN = document.documentElement.lang === 'en';
const L = (fr, en) => EN ? en : fr;
const AN_DEBUT = 1785, AN_DETAIL = 1814, AN_FIN = 1851;
const NB_ANNEES = AN_DETAIL - AN_DEBUT;                       // 29 positions annuelles
const POS_MAX = NB_ANNEES + (AN_FIN - AN_DETAIL) * 12;        // 29 + 444 = 473
const MOIS = EN ? ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
             : ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'];
const TOUTES = L('Toutes les dates', 'All dates');
function lirePosition(v) {
  v = Number(v);
  if (v >= POS_MAX) return { libelle: TOUTES, borne: null };
  if (v < NB_ANNEES) return { libelle: `${AN_DEBUT + v}`, borne: AN_DEBUT + v + 1 };
  const m = v - NB_ANNEES;
  return { libelle: `${MOIS[m % 12]} ${AN_DETAIL + Math.floor(m / 12)}`, borne: AN_DETAIL + (m + 1) / 12 };
}

// Grandes périodes de la vie d'Étienne Provost, pour situer chaque entrée du journal
const CHAPITRES = EN ? [
  [1814.0, 'I · Chambly, a Canadien youth'],
  [1821.5, 'II · St. Louis and the Spanish prisons'],
  [1826.6, 'III · Taos and the Great Basin: the man of the Salt Lake'],
  [1838.5, 'IV · The American Fur Company, the rendezvous'],
  [1850.6, 'V · Guide, recruiter and St. Louis tavern keeper'],
  [9999, 'VI · Legacy']
] : [
  [1814.0, 'I · Chambly, la jeunesse canadienne'],
  [1821.5, 'II · Saint-Louis et les prisons espagnoles'],
  [1826.6, 'III · Taos et le Grand Bassin : l\'homme du lac Salé'],
  [1838.5, 'IV · L\'American Fur Company, les rendez-vous'],
  [1850.6, 'V · Guide, recruteur et tavernier de Saint-Louis'],
  [9999, 'VI · Postérité']
];
const chapitre = t => CHAPITRES.find(([fin]) => t < fin)[1];

const VERSION = new URL(document.currentScript.src).searchParams.get('v') || '';

const carte = new maplibregl.Map({
  container: 'carte',
  style: 'https://tiles.openfreemap.org/styles/positron',
  center: [-100, 37],
  zoom: 4,
  attributionControl: { compact: true }
});
carte.addControl(new maplibregl.NavigationControl(), 'top-left');
if (typeof installerStreetView === 'function') installerStreetView(carte, EN);
carte.addControl(new maplibregl.ScaleControl({ unit: 'imperial' }), 'bottom-left');
// Légende en cartouche dans le coin supérieur droit (contenu défini dans index.html)
carte.addControl({
  onAdd() { const el = document.getElementById('legende-carte'); el.classList.add('maplibregl-ctrl'); return el; },
  onRemove() {}
}, 'top-right');
new ResizeObserver(() => carte.resize()).observe(document.getElementById('carte'));

// Couleurs d'encre par catégorie de lieu
const COULEURS = { combat: '#9a3322', prison: '#2f4d63', rendezvous: '#7a4f16', traite: '#6b5a3c', guide: '#3f5a2a',
                   famille: '#6d3f5c', posterite: '#5b6a66', naissance: '#1f2f3a', vie: '#1f2f3a', mort: '#1f2f3a' };
const couleurCategorie = ['match', ['get', 'categorie'], ...Object.entries(COULEURS).flat(), '#1f2f3a'];
const NOMS_CATEGORIE = EN ? { combat: 'battle, massacre', prison: 'arrest, prison', rendezvous: 'rendezvous, meeting', traite: 'fur trade, commerce',
                              guide: 'guide, expedition', famille: 'family', posterite: 'legacy, memory', naissance: 'birth', vie: 'life', mort: 'death' }
  : { combat: 'combat, massacre', prison: 'arrestation, prison', rendezvous: 'rendez-vous, rencontre', traite: 'traite, commerce',
      guide: 'guide, expédition', famille: 'famille', posterite: 'postérité, mémoire', naissance: 'naissance', vie: 'vie', mort: 'mort' };
const NOMS_MODE = EN ? { cheval: 'on horseback, on foot', canot: 'canoe, barge, boat', vapeur: 'steamboat' }
                     : { cheval: 'à cheval, à pied', canot: 'canot, barge, bateau', vapeur: 'bateau à vapeur' };
const ENCRE_MER = '#9a3322', ENCRE_TERRE = '#1f2f3a';
const estMer = ['in', ['get', 'mode'], ['literal', ['canot', 'vapeur']]];

carte.on('load', async () => {
  const [lieux, trajets] = await Promise.all([
    fetch(`data/lieux${L('', '-en')}.geojson?v=${VERSION}`).then(r => r.json()),
    fetch(`data/trajets${L('', '-en')}.geojson?v=${VERSION}`).then(r => r.json())
  ]);
  window.DONNEES = { lieux, trajets }; // utilisé par la visite animée (visite.js)
  const couchesDeBase = carte.getStyle().layers.map(l => l.id);
  carte.addSource('lieux', { type: 'geojson', data: lieux });
  carte.addSource('trajets', { type: 'geojson', data: trajets });

  // Fond satellite (Esri World Imagery), masqué par défaut
  carte.addSource('satellite', {
    type: 'raster', tileSize: 256, maxzoom: 19,
    tiles: ['https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'],
    attribution: L('Imagerie © Esri, Maxar, Earthstar Geographics et contributeurs', 'Imagery © Esri, Maxar, Earthstar Geographics and contributors')
  });
  carte.addLayer({ id: 'satellite', type: 'raster', source: 'satellite', layout: { visibility: 'none' } });

  // Routes : encre rouge et tirets pour la mer, encre brune et points pour les terres et les rivières.
  // Une ligne claire dessous détache le tracé du fond.
  carte.addLayer({
    id: 'trajets-halo', type: 'line', source: 'trajets',
    layout: { 'line-cap': 'round', 'line-join': 'round' },
    paint: { 'line-color': '#eff0e4', 'line-width': 5, 'line-opacity': ['case', ['==', ['get', 'certitude'], 'hypothetique'], 0.35, 0.6] }
  });
  carte.addLayer({
    id: 'trajets-mer', type: 'line', source: 'trajets', filter: estMer,
    layout: { 'line-join': 'round' },
    paint: { 'line-color': ENCRE_MER, 'line-width': ['case', ['==', ['get', 'certitude'], 'hypothetique'], 1.6, 2.4],
             'line-dasharray': [3, 2], 'line-opacity': ['case', ['==', ['get', 'certitude'], 'hypothetique'], 0.6, 0.95] }
  });
  carte.addLayer({
    id: 'trajets-terre', type: 'line', source: 'trajets', filter: ['!', estMer],
    layout: { 'line-cap': 'round', 'line-join': 'round' },
    paint: { 'line-color': ENCRE_TERRE, 'line-width': ['case', ['==', ['get', 'certitude'], 'hypothetique'], 2, 2.8],
             'line-dasharray': [0.1, 2], 'line-opacity': ['case', ['==', ['get', 'certitude'], 'hypothetique'], 0.6, 0.95] }
  });
  // Trajet sélectionné
  carte.addLayer({
    id: 'trajet-actif', type: 'line', source: 'trajets', filter: ['==', ['get', 'id'], ''],
    layout: { 'line-cap': 'round', 'line-join': 'round' },
    paint: { 'line-color': '#c8903e', 'line-width': 6, 'line-opacity': 0.55 }
  }, 'trajets-halo');

  // Lieux : pastille d'encre pleine si localisation certaine, cerclée sur vélin sinon
  carte.addLayer({
    id: 'lieux', type: 'circle', source: 'lieux',
    paint: {
      'circle-radius': ['interpolate', ['linear'], ['zoom'], 2, 4.5, 8, 7.5],
      'circle-color': ['case', ['==', ['get', 'certitude'], 'certaine'], couleurCategorie, '#eff0e4'],
      'circle-stroke-color': couleurCategorie,
      'circle-stroke-width': ['case', ['==', ['get', 'certitude'], 'certaine'], 1.5, 2.5]
    }
  });
  // Les combats sont marqués d'un anneau supplémentaire
  carte.addLayer({
    id: 'lieux-anneau', type: 'circle', source: 'lieux', filter: ['==', ['get', 'categorie'], 'combat'],
    paint: { 'circle-radius': ['interpolate', ['linear'], ['zoom'], 2, 7.5, 8, 11.5], 'circle-color': 'rgba(0,0,0,0)',
             'circle-stroke-color': '#9a3322', 'circle-stroke-width': 1, 'circle-stroke-opacity': 0.8 }
  }, 'lieux');
  carte.addLayer({
    id: 'lieux-noms', type: 'symbol', source: 'lieux',
    layout: { 'text-field': ['get', 'nom'], 'text-size': ['interpolate', ['linear'], ['zoom'], 2, 10.5, 8, 13],
              'text-offset': [0, 1.1], 'text-anchor': 'top', 'text-font': ['Noto Sans Italic'], 'text-max-width': 9,
              'text-optional': true, 'symbol-sort-key': ['get', 'debut'] },
    paint: { 'text-color': '#1f2f3a', 'text-halo-color': '#eff0e4', 'text-halo-width': 1.6 }
  });

  ['lieux', 'trajets-mer', 'trajets-terre'].forEach(id => {
    carte.on('click', id, e => {
      const f = e.features[0];
      afficherFiche(f.properties, f.geometry.type);
      zoomerSur(f);
    });
    carte.on('mouseenter', id, () => { carte.getCanvas().style.cursor = 'pointer'; });
    carte.on('mouseleave', id, () => { carte.getCanvas().style.cursor = ''; });
  });

  // clic ailleurs que sur un lieu ou une route : le journal se referme
  carte.on('click', e => {
    if (!carte.queryRenderedFeatures(e.point, { layers: ['lieux', 'trajets-mer', 'trajets-terre'] }).length) fermerFiche();
  });

  appliquerFond = installerFonds(carte, couchesDeBase, 'satellite');
  await appliquerFond('parchemin');
  appliquerDate(curseur.value);

  // Cadrer la carte sur l'ensemble des données
  const b = new maplibregl.LngLatBounds();
  [...lieux.features, ...trajets.features].forEach(f => {
    (f.geometry.type === 'Point' ? [f.geometry.coordinates] : f.geometry.coordinates).forEach(xy => b.extend(xy));
  });
  window.LIMITES_DONNEES = b;
  carte.fitBounds(b, { padding: { top: 50, bottom: 50, left: 170, right: 270 }, duration: 0 });
  lireAncre();
  window.addEventListener('hashchange', lireAncre);
});

function lireAncre() {
  const m = decodeURIComponent(location.hash || '').match(/(?:lieu|trajet)=([LT]\d+)/);
  if (!m || !window.DONNEES) return;
  const f = [...window.DONNEES.lieux.features, ...window.DONNEES.trajets.features].find(x => x.properties.id === m[1]);
  if (f) { afficherFiche(f.properties, f.geometry.type); zoomerSur(f); }
}

// ---------- Timeline ----------
const curseur = document.getElementById('curseur');
const sortie = document.getElementById('date-affichee');
const btnLecture = document.getElementById('lecture');
function appliquerDate(v) {
  const { libelle, borne } = lirePosition(v);
  sortie.textContent = libelle;
  const f = borne === null ? null : ['<', ['get', 'debut'], borne];
  const et = base => f ? ['all', base, f] : base;
  ['lieux', 'lieux-noms'].forEach(id => carte.setFilter(id, f));
  carte.setFilter('lieux-anneau', et(['==', ['get', 'categorie'], 'combat']));
  carte.setFilter('trajets-halo', f);
  carte.setFilter('trajets-mer', et(estMer));
  carte.setFilter('trajets-terre', et(['!', estMer]));
}
curseur.max = POS_MAX;
curseur.value = POS_MAX;
curseur.addEventListener('input', () => appliquerDate(curseur.value));

// Graduation : segment 1661-1685 compressé (par année), puis une année tous les 12 mois
(function graduer() {
  const g = document.getElementById('graduation');
  const POUCE = 18; // largeur du bouton du curseur (voir style.css)
  const position = v => `calc(${v / POS_MAX} * (100% - ${POUCE}px) + ${POUCE / 2}px)`;
  const trait = (v, cls) => { const t = document.createElement('span'); t.className = cls; t.style.left = position(v); g.appendChild(t); };
  const annee = (v, texte) => {
    const a = document.createElement('span');
    a.className = 'annee'; a.textContent = texte; a.style.left = position(v);
    a.title = L(`Aller à ${texte}`, `Go to ${texte}`);
    a.addEventListener('click', () => { curseur.value = v; appliquerDate(v); });
    g.appendChild(a);
  };
  const bande = document.createElement('span');
  bande.className = 'segment-compresse'; bande.style.left = position(0);
  bande.style.width = `calc(${(NB_ANNEES - 0.5) / POS_MAX} * (100% - ${POUCE}px))`;
  bande.title = L('1785-1813 : échelle compressée (une position par année)', '1785-1813: compressed scale (one step per year)');
  g.appendChild(bande);
  for (let v = 0; v < NB_ANNEES; v++) trait(v, (AN_DEBUT + v) % 5 === 0 || v === 0 ? 'trait' : 'trait mineur');
  annee(0, '1785'); annee(15, '1800');
  trait(NB_ANNEES - 0.5, 'trait coupure');
  for (let v = NB_ANNEES; v < POS_MAX; v += 6) {
    const m = v - NB_ANNEES, a = AN_DETAIL + m / 12;
    trait(v, m % 12 === 0 ? 'trait' : 'trait mineur');
    if (m % 12 === 0 && a % 4 === 2) annee(v, `${a}`);
  }
})();

let minuterie = null;
btnLecture.addEventListener('click', () => {
  // « Suivre Provost » coché : visite animée (visite.js) ; sinon, simple défilement de la timeline
  if (document.getElementById('suivi').checked && typeof Visite !== 'undefined') { Visite.basculer(); return; }
  if (minuterie) { clearInterval(minuterie); minuterie = null; btnLecture.textContent = '▶'; return; }
  if (Number(curseur.value) >= Number(curseur.max)) curseur.value = curseur.min;
  btnLecture.textContent = '❚❚';
  minuterie = setInterval(() => {
    const v = Number(curseur.value) + 1;
    curseur.value = v; appliquerDate(v);
    if (v >= Number(curseur.max)) btnLecture.click();
  }, 250);
});

// ---------- Couches ----------
let appliquerFond = null;
document.querySelectorAll('input[name=fond]').forEach(r => r.addEventListener('change', e => { if (appliquerFond) appliquerFond(e.target.value); }));
document.getElementById('c-lieux').addEventListener('change', e => {
  ['lieux', 'lieux-anneau', 'lieux-noms'].forEach(id => carte.setLayoutProperty(id, 'visibility', e.target.checked ? 'visible' : 'none'));
});
document.getElementById('c-trajets').addEventListener('change', e => {
  ['trajets-halo', 'trajets-mer', 'trajets-terre', 'trajet-actif'].forEach(id => carte.setLayoutProperty(id, 'visibility', e.target.checked ? 'visible' : 'none'));
});

// ---------- Journal de bord (panneau documentaire) ----------
const echapper = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const NOMS_CERTITUDE = EN ? { certaine: 'location certain', approximative: 'approximate', hypothetique: 'hypothetical' }
                         : { certaine: 'localisation certaine', approximative: 'approximative', hypothetique: 'hypothétique' };
// Date EDTF -> date lisible (« 1697-09-05 » -> « 5 septembre 1697 » ; « ~ » = vers)
function dateLisible(edtf) {
  if (!edtf) return '';
  return String(edtf).split('/').map(d => {
    const approx = /[~?]/.test(d), [a, m, j] = d.replace(/[~?]/g, '').split('-').map(Number);
    const txt = j ? (EN ? `${MOIS[m - 1]} ${j}, ${a}` : `${j === 1 ? '1er' : j} ${MOIS[m - 1]} ${a}`) : m ? `${MOIS[m - 1]} ${a}` : `${a}`;
    return approx ? `${L('vers', 'c.')} ${txt}` : txt;
  }).join(' – ');
}

const ZOOM_POINT = 7;
function zoomerSur(f) {
  if (f.geometry.type === 'Point') {
    carte.flyTo({ center: f.geometry.coordinates, zoom: Math.max(carte.getZoom(), ZOOM_POINT), speed: 1.4, essential: true });
    return;
  }
  const b = new maplibregl.LngLatBounds();
  f.geometry.coordinates.forEach(xy => b.extend(xy));
  carte.fitBounds(b, { padding: { top: 60, bottom: 60, left: 60, right: 260 }, maxZoom: 7, essential: true });
}

// Découpures de presse liées à une fiche (propriété « presse » : liste de {src, legende, article}),
// chacune renvoyant à son article dans la salle de lecture.
function vignettes(liste, titre) {
  let pr = liste;
  if (typeof pr === 'string') { try { pr = JSON.parse(pr); } catch (e) { pr = []; } }
  if (!Array.isArray(pr) || !pr.length) return '';
  return `<div class="presse"><strong>${titre}</strong>${pr.map(d =>
    `<a href="salle-de-lecture.html#${echapper(d.article)}" target="_blank" rel="noopener" title="${echapper(d.legende)}"><img src="${echapper(d.src)}" alt="${echapper(d.legende)}" loading="lazy"><span>${echapper(d.legende)}</span></a>`).join('')}</div>`;
}
function presseFiche(p) {
  return vignettes(p.registres, L('Dans les registres :', 'In the registers:')) + vignettes(p.presse, L('Dans les journaux :', 'In the newspapers:'));
}
function afficherFiche(p, geom) {
  const estTrajet = geom === 'LineString' || p.type === 'trajet';
  if (carte.getLayer('trajet-actif')) carte.setFilter('trajet-actif', ['==', ['get', 'id'], estTrajet ? p.id : '']);
  const genre = estTrajet ? (NOMS_MODE[p.mode] || L('route', 'route')) : (NOMS_CATEGORIE[p.categorie] || '');
  const panneau = document.getElementById('panneau');
  panneau.innerHTML = `
    <button type="button" class="fermer" aria-label="${L('Fermer le journal', 'Close the journal')}" title="${L('Fermer (Échap)', 'Close (Esc)')}">✕</button>
    <p class="chapitre">${echapper(chapitre(Number(p.debut)))}</p>
    <h2>${echapper(p.nom)}</h2>
    <div class="filet" aria-hidden="true">★</div>
    <p class="entree-date">${echapper(dateLisible(p.date_edtf))}</p>
    <p class="meta">
      ${genre ? `<span class="badge genre ${echapper(estTrajet ? p.mode : p.categorie)}">${echapper(genre)}</span>` : ''}
      <span class="badge ${echapper(p.certitude)}">${echapper(NOMS_CERTITUDE[p.certitude] || p.certitude)}</span>
    </p>
    ${p.description ? `<p class="description">${echapper(p.description)}</p>` : ''}
    ${p.note ? `<p class="note"><strong>${L('Note critique :', 'Critical note:')}</strong> ${echapper(p.note)}</p>` : ''}
    ${presseFiche(p)}
    <div class="sources"><strong>${L('Source :', 'Source:')}</strong> ${echapper(p.sources)}</div>`;
  panneau.querySelector('.fermer').addEventListener('click', fermerFiche);
  panneau.classList.add('ouvert');
  panneau.scrollTop = 0;
}
// Texte d'introduction (bouton « À propos » de la légende)
function afficherApropos() {
  if (carte.getLayer('trajet-actif')) carte.setFilter('trajet-actif', ['==', ['get', 'id'], '']);
  const panneau = document.getElementById('panneau');
  panneau.innerHTML = EN ? `
    <button type="button" class="fermer" aria-label="Close" title="Close (Esc)">✕</button>
    <h2>The Man of the Mountains</h2>
    <div class="filet" aria-hidden="true">★</div>
    <p class="description">Étienne Provost (Chambly, 1785 – St. Louis, 1850): this atlas follows his whole life, from the Richelieu valley to St. Louis, from the prisons of Santa Fe to the Great Salt Lake basin, where the river and the city of Provo bear his name, then from the Rocky Mountain rendezvous to the American Fur Company forts on the upper Missouri, where he guided Nicollet and Audubon, and finally to his St. Louis tavern.</p>
    <p>Click a place or a route to open its entry. The timeline moves by year from 1785 to 1813 (his youth, poorly documented), then by month from 1814 to 1850; legacy entries (after 1850) appear only under “All dates.” The ▶ button starts the journey: the rider or the canoe follows each route and the map stops at each place.</p>
    <p class="avertissement">Routes are schematic; dotted lines mark a hypothetical route. Many episodes (Philibert 1814, the 1824 massacre, the discovery of the Great Salt Lake, South Pass, the first Crow wife) are debated: each entry cites its sources (Tykal 1989 and his Utah History Encyclopedia article, Hafen, Chittenden, Dale, Morgan, Audubon, Vaugeois…) and flags the uncertainties. The descriptions are summaries written for the atlas and translated from the French. The atlas is part of the <a href="https://geolas2023.github.io/atlas-les-canadiens-fran-ais-de-l-ouest/provost-en.html">French Canadians of the West</a> network.</p>
    <div class="sources">Olivier J. Caron, Department of Geography, UQAM.</div>` : `
    <button type="button" class="fermer" aria-label="Fermer" title="Fermer (Échap)">✕</button>
    <h2>L'homme des montagnes</h2>
    <div class="filet" aria-hidden="true">★</div>
    <p class="description">Étienne Provost (Chambly, 1785 – Saint-Louis, 1850) : cet atlas suit toute sa vie, de la vallée du Richelieu à Saint-Louis, des prisons de Santa Fe au bassin du Grand Lac Salé, où la rivière et la ville de Provo portent son nom, puis des rendez-vous des Rocheuses aux forts de l'American Fur Company sur le haut Missouri, où il guide Nicollet et Audubon, jusqu'à sa taverne de Saint-Louis.</p>
    <p>Cliquez sur un lieu ou une route pour ouvrir son entrée. La timeline avance par année de 1785 à 1813 (jeunesse, peu documentée), puis par mois de 1814 à 1850 ; les fiches de postérité (après 1850) n'apparaissent qu'à « Toutes les dates ». Le bouton ▶ lance le voyage : le cavalier ou le canot suit chaque route et la carte s'arrête à chaque lieu.</p>
    <p class="avertissement">Les routes sont schématiques ; le pointillé signale un tracé hypothétique. Beaucoup d'épisodes (Philibert 1814, massacre de 1824, découverte du Grand Lac Salé, col du Sud, première épouse crow) sont discutés : chaque entrée cite ses sources (Tykal 1989 et sa notice de l'Utah History Encyclopedia, Hafen, Chittenden, Dale, Morgan, Audubon, Vaugeois…) et signale les incertitudes. Les descriptions sont des résumés rédigés pour l'atlas. L'atlas fait partie du réseau <a href="https://geolas2023.github.io/atlas-les-canadiens-fran-ais-de-l-ouest/provost.html">Les Canadiens français de l'Ouest</a>.</p>
    <div class="sources">Olivier J. Caron, Département de géographie, UQAM.</div>`;
  panneau.querySelector('.fermer').addEventListener('click', fermerFiche);
  panneau.classList.add('ouvert');
  panneau.scrollTop = 0;
}
document.getElementById('btn-apropos').addEventListener('click', afficherApropos);
function fermerFiche() {
  const panneau = document.getElementById('panneau');
  panneau.classList.remove('ouvert');
  if (carte.getLayer('trajet-actif')) carte.setFilter('trajet-actif', ['==', ['get', 'id'], '']);
}
document.addEventListener('keydown', e => { if (e.key === 'Escape') fermerFiche(); });
