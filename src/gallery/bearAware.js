import { bearAwareFolder, bearAwareId, bearAwareMarkId, bearAwareReport } from '../initiatives/bearAwareArtwork.js'

const label = 'Be Bear Aware paw lockup'
const source = {
  label,
  publisher: 'Revelstoke Bear Awareness Program',
  creator: '1997 final report by Debby Robinson',
  sourceFile: 'Revelstoke Bear Awareness Program, 1997 Final Report',
  sourcePage: bearAwareReport + '#page=28',
  sourceLocator: 'PDF page 28, upper right of the Bear Aware Business Checklist',
  sourceDate: '1997',
  observedDate: '2026-11-25',
  role: 'historical'
}

export const bearAwareReconstructionId = bearAwareMarkId + '-reconstruction'

export const bearAwareSpecimens = {
  program: bearAwareId,
  assets: [
    {
      ...source, id: bearAwareMarkId, designLabel: label, versionLabel: 'Original scan',
      file: bearAwareFolder + 'scans/be-bear-aware-paw-lockup.png', format: 'png', isVector: false,
      evidenceType: 'printed-source-crop',
      fidelityNote: 'Unretouched crop of the business checklist scan. Original campaign production artwork is a lead for the Revelstoke Bear Aware Society or Revelstoke Museum & Archives.'
    },
    {
      ...source, id: bearAwareReconstructionId, variantOf: bearAwareMarkId, versionLabel: 'SVG reconstruction',
      file: bearAwareFolder + 'components/be-bear-aware-paw-lockup.svg', format: 'svg', isVector: true,
      sourceGround: 'light', reconstruction: true, evidenceType: 'vector-reconstruction',
      fidelityNote: 'Manually redrawn claw curves and outlined lettering, based on the published checklist. The lettering and proportions are approximate.'
    }
  ]
}
