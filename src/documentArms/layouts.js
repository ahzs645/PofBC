// Document layouts are observations and studies, not a recovered government standard.
// Keep these small definitions separate from the detailed engraving and outlined lettering.
export const DOCUMENT_ARMS_LAYOUT_ORDER = [
  'emblem', 'split-serif', 'government', 'split-blackletter'
]

export const DOCUMENT_ARMS_LAYOUTS = {
  emblem: {
    label: 'Arms alone',
    description: 'The shared PlateForge arms study, without a heading.',
    hint: 'A provisional vector study reused from the 1919 cardboard plate. Its drawing is not a verified historical master.'
  },
  'split-serif': {
    label: 'Split serif',
    description: 'BRITISH and COLUMBIA beside the arms, following the supplied document heading.',
    hint: 'The layout follows the supplied heading. Noto Serif Bold is a modern stand-in; the original lettering has not been identified.'
  },
  government: {
    label: 'Government heading',
    description: 'The arms over THE GOVERNMENT OF / THE PROVINCE OF BRITISH COLUMBIA.',
    hint: 'The stacked wording is visible on the supplied 1978 order. Barlow Condensed Bold is a modern stand-in.'
  },
  'split-blackletter': {
    label: 'Crown grant heading',
    description: 'British and Columbia in blackletter beside the arms, following the supplied crown grant heading.',
    hint: 'UnifrakturMaguntia is a modern blackletter stand-in. The supplied crown grant’s original lettering has not been identified.'
  }
}

export const DEFAULT_DOCUMENT_ARMS_LAYOUT = 'split-serif'

export const DOCUMENT_ARMS_PROVENANCE = 'Provisional historical-layout study. The arms reuse PlateForge’s vector conversion of a generated master, not a verified historical or official drawing. The supplied document engravings differ. Lettering uses modern open-font stand-ins; the original typefaces have not been identified.'
