// Ministry names whose line breaks have been seen in the Province's own artwork.
//
// The rules in currentLayout.js reproduce every name here but two, and they are what sets a name
// the Province never published. But a rule is a guess about why a mark was broken where it was, and
// the next mark found may be the exception that proves it wrong. So a name listed here is set as
// the Province set it whatever the rules say: improving the rules for one mark can never quietly
// move another that is already known.
//
// Add a name the moment a published mark confirms it, with where it was seen. Keep the evidence
// in artwork/ when it is not already there. currentLayout.test.js then says whether the rules
// agree; an entry they do not reproduce is an exception, and it is listed there so a new one shows
// up as a failing test rather than being absorbed silently.
//
// Hand-maintained, unlike ministries.js: nothing regenerates it.

/** Where each confirmation was seen. */
export const SOURCES = {
  'marks-2025': 'BC Government Ministry Marks, V4, July 2025 (artwork/current/ministry-marks.pdf), read off the drawn artwork. ' +
    'The English Infrastructure mark is drawn in French there, so its breaks come from the text layer.',
  flnrord: 'Ministry of Forests, Lands, Natural Resource Operations and Rural Development mark, 2017–2022 ' +
    '(artwork/current/lifted/flnrord.svg, and in colour, artwork/current/confirmed/flnrord.png)',
  jedi: 'Ministry of Jobs, Economic Development and Innovation mark (artwork/current/confirmed/jedi.png)',
  'env-ccs': 'Ministry of Environment and Climate Change Strategy mark (artwork/current/confirmed/env-ccs.png)',
  'wlrs-2022': 'Ministry of Water, Land and Resource Stewardship mark (artwork/current/confirmed/wlrs.png)',
  tran: 'Ministry of Transportation and Infrastructure mark (artwork/current/confirmed/tran.png)',
  emli: 'Ministry of Energy, Mines and Low Carbon Innovation mark, reversed (artwork/current/confirmed/emli.png)'
}

/**
 * Every confirmed name, as the lines its mark draws. `key` is `<code>-<language>` for a current
 * ministry and a short name otherwise; the same wording may be confirmed by more than one source.
 */
export const CONFIRMED = [
  { key: 'af-en', language: 'en', source: 'marks-2025', lines: ["Ministry of","Agriculture","and Food"] },
  { key: 'af-fr', language: 'fr', source: 'marks-2025', lines: ["Ministère de","l’Agriculture et de","l’Alimentation"] },
  { key: 'ag-en', language: 'en', source: 'marks-2025', lines: ["Ministry of","Attorney General"] },
  { key: 'ag-fr', language: 'fr', source: 'marks-2025', lines: ["Ministère du","Procureur général"] },
  { key: 'cfd-en', language: 'en', source: 'marks-2025', lines: ["Ministry of","Children and Family","Development"] },
  { key: 'cfd-fr', language: 'fr', source: 'marks-2025', lines: ["Ministère du","Développement de l’enfance","et de la famille"] },
  { key: 'citz-en', language: 'en', source: 'marks-2025', lines: ["Ministry of","Citizens’ Services"] },
  { key: 'citz-fr', language: 'fr', source: 'marks-2025', lines: ["Ministère des","Services aux citoyens"] },
  { key: 'ecc-en', language: 'en', source: 'marks-2025', lines: ["Ministry of","Education and","Child Care"] },
  { key: 'ecc-fr', language: 'fr', source: 'marks-2025', lines: ["Ministère de","l’Éducation et des","Services à la petite enfance"] },
  { key: 'emcr-en', language: 'en', source: 'marks-2025', lines: ["Ministry of","Emergency Management","and Climate Readiness"] },
  { key: 'emcr-fr', language: 'fr', source: 'marks-2025', lines: ["Ministère de","la Gestion des urgences","et de la Préparation au climat"] },
  { key: 'ecs-en', language: 'en', source: 'marks-2025', lines: ["Ministry of","Energy and","Climate Solutions"] },
  { key: 'ecs-fr', language: 'fr', source: 'marks-2025', lines: ["Ministère de","l’Énergie et des","Solutions climatiques"] },
  { key: 'env-en', language: 'en', source: 'marks-2025', lines: ["Ministry of","Environment","and Parks"] },
  { key: 'env-fr', language: 'fr', source: 'marks-2025', lines: ["Ministère de","l’Environnement","et des Parcs"] },
  { key: 'fin-en', language: 'en', source: 'marks-2025', lines: ["Ministry of","Finance"] },
  { key: 'fin-fr', language: 'fr', source: 'marks-2025', lines: ["Ministère des","Finances"] },
  { key: 'for-en', language: 'en', source: 'marks-2025', lines: ["Ministry of","Forests"] },
  { key: 'for-fr', language: 'fr', source: 'marks-2025', lines: ["Ministère des","Forêts"] },
  { key: 'hlth-en', language: 'en', source: 'marks-2025', lines: ["Ministry of","Health"] },
  { key: 'hlth-fr', language: 'fr', source: 'marks-2025', lines: ["Ministère de","la Santé"] },
  { key: 'hma-en', language: 'en', source: 'marks-2025', lines: ["Ministry of","Housing and","Municipal Affairs"] },
  { key: 'hma-fr', language: 'fr', source: 'marks-2025', lines: ["Ministère du","Logement et des","Affaires municipales"] },
  { key: 'irr-en', language: 'en', source: 'marks-2025', lines: ["Ministry of","Indigenous Relations","and Reconciliation"] },
  { key: 'irr-fr', language: 'fr', source: 'marks-2025', lines: ["Ministère des","Relations avec les Autochtones","et de la Réconciliation"] },
  { key: 'inf-en', language: 'en', source: 'marks-2025', lines: ["Ministry of","Infrastructure"] },
  { key: 'inf-fr', language: 'fr', source: 'marks-2025', lines: ["Ministère de","l’Infrastructure"] },
  { key: 'jeg-en', language: 'en', source: 'marks-2025', lines: ["Ministry of","Jobs and","Economic Growth"] },
  { key: 'jeg-fr', language: 'fr', source: 'marks-2025', lines: ["Ministère des","Emplois et de la","Croissance économique"] },
  { key: 'lbr-en', language: 'en', source: 'marks-2025', lines: ["Ministry of","Labour"] },
  { key: 'lbr-fr', language: 'fr', source: 'marks-2025', lines: ["Ministère du","Travail"] },
  { key: 'mcm-en', language: 'en', source: 'marks-2025', lines: ["Ministry of","Mining and","Critical Minerals"] },
  { key: 'mcm-fr', language: 'fr', source: 'marks-2025', lines: ["Ministère des","Mines et des","Minéraux critiques"] },
  { key: 'psfs-en', language: 'en', source: 'marks-2025', lines: ["Ministry of","Post-Secondary Education","and Future Skills"] },
  { key: 'psfs-fr', language: 'fr', source: 'marks-2025', lines: ["Ministère de","l’Éducation postsecondaire","et des Compétences futures"] },
  { key: 'pssg-en', language: 'en', source: 'marks-2025', lines: ["Ministry of","Public Safety and","Solicitor General"] },
  { key: 'pssg-fr', language: 'fr', source: 'marks-2025', lines: ["Ministère de","la Sécurité publique","et du Solliciteur général"] },
  { key: 'sdpr-en', language: 'en', source: 'marks-2025', lines: ["Ministry of","Social Development","and Poverty Reduction"] },
  { key: 'sdpr-fr', language: 'fr', source: 'marks-2025', lines: ["Ministère du","Développement social","et de la Réduction de la pauvreté"] },
  { key: 'tacs-en', language: 'en', source: 'marks-2025', lines: ["Ministry of","Tourism, Arts,","Culture and Sport"] },
  { key: 'tacs-fr', language: 'fr', source: 'marks-2025', lines: ["Ministère du","Tourisme, des Arts, de","la Culture et du Sport"] },
  { key: 'tt-en', language: 'en', source: 'marks-2025', lines: ["Ministry of","Transportation","and Transit"] },
  { key: 'tt-fr', language: 'fr', source: 'marks-2025', lines: ["Ministère des","Transports et du","Transport en commun"] },
  { key: 'wlrs-en', language: 'en', source: 'marks-2025', lines: ["Ministry of","Water, Land and","Resource Stewardship"] },
  { key: 'wlrs-fr', language: 'fr', source: 'marks-2025', lines: ["Ministère de","l’Intendance de l’eau, des terres","et des ressources"] },
  { key: 'flnrord-en', language: 'en', source: 'flnrord', lines: ['Ministry of', 'Forests, Lands, Natural', 'Resource Operations', 'and Rural Development'] },
  { key: 'jedi-en', language: 'en', source: 'jedi', lines: ['Ministry of', 'Jobs, Economic Development', 'and Innovation'] },
  { key: 'env-ccs-en', language: 'en', source: 'env-ccs', lines: ['Ministry of', 'Environment and', 'Climate Change Strategy'] },
  { key: 'wlrs-2022-en', language: 'en', source: 'wlrs-2022', lines: ['Ministry of', 'Water, Land and', 'Resource Stewardship'] },
  { key: 'tran-en', language: 'en', source: 'tran', lines: ['Ministry of', 'Transportation', 'and Infrastructure'] },
  { key: 'emli-en', language: 'en', source: 'emli', lines: ['Ministry of', 'Energy, Mines and', 'Low Carbon Innovation'] }
]

/**
 * The form a name is looked up in: one space between words, and the apostrophe the marks set.
 * Line breaks count as spaces, so "Ministry of\nHealth" and "Ministry of Health" are one name.
 */
export const confirmedKey = (text) => String(text).replace(/'/g, '’').replace(/\s+/g, ' ').trim()

const byName = { en: new Map(), fr: new Map() }
for (const entry of CONFIRMED) {
  const name = confirmedKey(entry.lines.join(' '))
  const seen = byName[entry.language].get(name)
  // Two sources disagreeing is exactly the kind of exception this list exists to catch.
  if (seen && seen.join('\n') !== entry.lines.join('\n')) {
    throw new Error(`confirmedBreaks: ${entry.key} disagrees with an earlier entry for "${name}"`)
  }
  byName[entry.language].set(name, entry.lines)
}

/** The published lines for a name, or undefined if no mark has confirmed it. */
export const confirmedLines = (text, language = 'en') => {
  const lines = byName[language]?.get(confirmedKey(text))
  return lines ? [...lines] : undefined
}
