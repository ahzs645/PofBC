// Downloaded artwork and supplied originals retain their own format and source.
// A date on a report is a sighting, never an inferred logo adoption date.
import { COLLECTED_BODIES, COLLECTED_SPECIMENS } from './collectedData.js'

export const assetUrl = (path, base = import.meta.env?.BASE_URL ?? '/') =>
  `${base.replace(/\/?$/, '/')}${path.replace(/^\//, '')}`

/** A collected file as a gallery entry; `timeline` places a program's specimen on its timeline. */
const collectedEntry = (asset, timeline) => ({
  id: asset.id,
  kind: 'collected',
  ...(timeline ? { timeline } : {}),
  label: asset.label,
  note: asset.notes,
  years: asset.sourceDate ? `Seen ${asset.sourceDate}` : 'Logo dates unestablished',
  asset,
  identity: {
    provenance: asset.reconstruction ? 'third_party_reconstruction' : asset.supplied ? 'original_supplied' : asset.isVector ? 'published_vector' : 'published_raster',
    fidelity: 'source compared',
    fidelityNote: asset.fidelityNote,
    applicability: {
      kind: asset.sourceDate ? 'dated_specimen' : 'unknown',
      years: asset.sourceDate || 'undated',
      note: asset.sourceDate
        ? 'This is the date of the cited specimen, not a verified first use or adoption date. ' + (asset.dateNote || '')
        : `Collected on ${asset.observedDate}. A retrieval date does not establish when the design was adopted.`,
    },
    rights: {
      status: 'unresolved',
      note: 'The mark belongs to its respective owner. No permission to reproduce it here has been sought or documented.',
    },
  },
})

export const COLLECTED_COLLECTIONS = COLLECTED_BODIES.filter((body) => body.assets.length).map((body) => ({
  id: `collected-${body.id}`,
  shelf: 'bodies',
  graphNode: body.id,
  fileCollection: true,
  label: body.shortName || body.name,
  body: `${body.current ? 'Current' : 'Former'} ${body.kind === 'health-authority' ? 'health organization' : 'Crown corporation'}`,
  years: `${body.from ?? '?'}–${body.current ? 'present' : body.to ?? '?'}`,
  intro: 'Collected artwork with its source recorded for each file. The organization’s dates above are not the dates of its logo. ' +
    (body.notes || ''),
  entries: body.assets.map((asset) => collectedEntry(asset)),
}))

// The one-off programs' published specimens (WorkBC, WelcomeBC, StrongerBC, Canada Starts Here, Where
// ideas work). They are not bodies of the inventory: each program's collection is not shelved, and
// its files are reached from the eras of its timeline (timelines.js), which they keep in view.
export const SPECIMEN_COLLECTIONS = COLLECTED_SPECIMENS.map(({ program, assets }) => ({
  id: `specimens-${program}`,
  shelf: 'specimens',
  fileCollection: true,
  label: assets[0]?.publisher ?? program,
  intro: 'Published vector specimens, each with its source recorded. A capture or document date is a sighting, not an adoption date.',
  entries: assets.map((asset) => collectedEntry(asset, program))
}))

export const COLLECTION_RESEARCH = new Map(COLLECTED_BODIES.map((body) => [body.id, body]))

export const researchLabel = (record) => {
  if (record?.status === 'source-found') return 'Source located · artwork wanted'
  if (record?.status === 'unresolved') return 'Wanted · searched'
  return 'Wanted'
}
