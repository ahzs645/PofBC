// Where each view's code comes from.
//
// Every view but the generator is its own chunk, fetched when it is first opened (App.jsx). The
// menu also asks for a view's chunk as soon as its item is pointed at or focused, so that by the
// time the click lands the download is under way or done.

export const VIEW_LOADERS = {
  // The gallery's marks are drawn from their own artwork and renderers, which the generator never needs.
  gallery: () => import('../gallery/GalleryView.jsx'),
  airports: () => import('../airports/AirportsView.jsx'),
  initiatives: () => import('../initiatives/InitiativesView.jsx'),
  'school-districts': () => import('../schools/SchoolDistrictsView.jsx'),
  parties: () => import('../parties/PartiesView.jsx'),
  // The government diagram carries a century and a half of ministries with it.
  government: () => import('../government/GovernmentView.jsx'),
  internal: () => import('../internal/InternalLogosView.jsx'),
  // The posters carry their own drawings, photographs and stage.
  posters: () => import('../posters/PostersView.jsx'),
  signs: () => import('../signs/SignsView.jsx'),
  cards: () => import('../cards/CardsView.jsx'),
  certificates: () => import('../certificates/CertificatesView.jsx'),
  stickers: () => import('../stickers/StickersView.jsx'),
  pins: () => import('../pins/PinsView.jsx'),
  // The patch library and digitizer come from the Patcher submodule (vendor/patcher).
  patches: () => import('../patches/PatchesView.jsx'),
  badges: () => import('../patches/PatchesView.jsx'),
  // Paper models fold in PackCAD's own viewer (vendor/packcad), framed; this chunk is only the chrome.
  'paper-models': () => import('../paper-models/PaperModelsView.jsx'),
  // Licence plates are drawn by PlateForge (vendor/plateforge), with its B.C. region data and fonts.
  plates: () => import('../plates/PlatesView.jsx'),
  arms: () => import('../arms/ArmsView.jsx'),
  guides: () => import('../guides/GuidesView.jsx'),
  // The stationery brings brandkit's template engine and studio (vendor/brandkit).
  stationery: () => import('../stationery/StationeryView.jsx'),
  salaries: () => import('../salaries/SalariesView.jsx'),
  'health-map': () => import('../health/HealthStoryView.jsx')
}

/** Starts fetching a view's code, if it has any of its own. A failure is left for the real load to report. */
export const preloadView = (id) => { VIEW_LOADERS[id]?.().catch(() => {}) }
