// The supplied v1.2 kit is modern reconstructed artwork. Its owner is the campaign society;
// neither the university's own source-vector coverage nor its institutional names inherit it.
import assets from '../../research/identity/unbc-origins/assets.json' with { type: 'json' }

export const IUS_ID = 'interior-university-society'
export const UNBC_ID = 'university-of-northern-bc'
export const IUS_COLLECTION_ID = `collected-${IUS_ID}`
export const IUS_ASSETS = assets
export const IUS_HIGHLIGHTS = [
  'ius-print-colour', 'ius-enamel-pin', 'northern-u-button', 'say-yes-button',
  'i-support-interior-university-sticker', 'ius-invitation-1988-retypeset',
  'ius-membership-card-reconstructed', 'ius-support-campaign-cover-interpretive'
].map((id) => assets.find((asset) => asset.id === id)).filter(Boolean)

export const IUS_BODY = {
  id: IUS_ID,
  name: 'Interior University Society',
  shortName: 'Interior University Society',
  kind: 'advocacy-society',
  graphNode: null,
  from: 1987,
  to: 1993,
  current: false,
  notes: 'Campaign identity from the movement that helped create UNBC. These 26 designs are modern vector reconstructions, re-typeset documents and interpretive studies from the supplied version 1.2 kit. Society dates are distinct from artwork dates.',
  assets: assets.map((asset) => ({
    id: `ius-${asset.id}`,
    label: asset.label,
    publisher: 'Supplied Interior University Society vector brand kit, version 1.2',
    file: `unbc-origins/${asset.svg}`,
    format: 'svg',
    isVector: true,
    supplied: true,
    reconstruction: true,
    fidelity: 'partially compared',
    observedDate: '2026-11-19',
    sourceFile: `IUS_Vector_Brand_Kit(1).zip · ${asset.svg}`,
    sha256: asset.svgSha256,
    darkBackground: asset.id === 'ius-print-white',
    notes: `${asset.status}. ${asset.note}`,
    fidelityNote: 'Supplied vector reconstruction checked against the kit manifest. Exact historical typefaces, colour specifications and physical dimensions remain unconfirmed. The graduate illustration and sweatshirt are interpretive.',
    ...(asset.id === 'ius-invitation-1988-retypeset' ? {
      sourceDate: '1988-06-08',
      dateNote: 'The photographed invitation bears this date. This modern re-typesetting is not an original 1988 vector file; the date does not establish the identity’s adoption.'
    } : {
      dateNote: 'The 1987–1993 society lifespan does not date this artwork. Version 1.2 is a contemporary reconstruction release.'
    }),
    downloads: [
      { file: `unbc-origins/${asset.pdf}`, label: 'Download PDF' },
      { file: 'unbc-origins/README.md', label: 'Reconstruction notes' }
    ]
  }))
}
