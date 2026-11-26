import { RURAL_HEALTH_COLLECTIONS } from './ruralHealth.js'
import { ASI_COLLECTION } from './advancedSystemsInstitute.js'
import { groupSpecimen } from './groupedSpecimens.js'
import { bearAwareSpecimens } from './bearAware.js'
import { fireSmartSpecimens } from './fireSmart.js'
import { ecosystemsAtRiskSpecimens } from './ecosystemsAtRisk.js'
import { resWestSpecimens } from './resWest.js'
import { educationProvinceWordmark } from '../initiatives/educationProvinceArtwork.js'
import { environmentYouthCorpsSpecimens } from '../initiatives/environmentYouthCorpsArtwork.js'
import { COLLECTED_BODIES, COLLECTED_SPECIMENS } from './collectedData.js'
import { EXPANDED_IDENTITY_BODIES } from './expandedIdentityData.js'
import { MUNICIPAL_IDENTITY_BODIES } from './municipalIdentityData.js'
import { RECOVERED_IDENTITY_BODIES } from './recoveredIdentityData.js'
import { POSTSECONDARY_IDENTITY_BODIES } from './postsecondaryIdentityData.js'
import { HEALTH_COUNCIL_BODIES } from './healthCouncilHistory.js'
import { AGRICULTURAL_PARTNER_BODIES } from './agriculturalPartners.js'
import { TOURISM_PARTNER_BODIES } from './tourismPartners.js'
import { AIRPORT_BODIES } from '../airports/airportArtwork.js'
import { NORTHERN_TRAVEL_GUIDE_ARTWORK } from './northernTravelGuides.js'
import { withStrongerBCGuide } from './strongerBC.js'
import { buyBCSpecimens } from './buyBC.js'
import { YOUTH_BODY } from './bcYouth.js'
import { FAMILY_COUNCIL_BODY } from './councilForTheFamily.js'
import { ALCOHOL_AND_DRUG_COMMISSION_BODY } from './alcoholAndDrugCommission.js'
import { IUS_BODY } from './iusCollectionData.js'
import { SCHOOL_IDENTITY_BODIES } from '../schools/integration.js'
import { REGIONAL_DISTRICT_BODIES } from './regionalDistricts.js'

import { SURVEY_AND_LIBRARY_BODIES } from './geologicalSurveyAndLibrary.js'
import { ENDORSED_2019 } from './endorsed2019.js'
import { CLEANBC_BODY } from './cleanbc.js'
import { LEGISLATIVE_ASSEMBLY_BODY } from './legislativeAssembly.js'
import { FORREX_COLLECTION, SIFERP_COLLECTION } from './forrex.js'
import { FOREST_GENETICS_BODIES } from './forestGenetics.js'
import { ACQUIRED_VECTORS } from './acquiredVectorData.js'
import { COLLECTED_VECTOR_VARIANTS } from './collectedVectorVariants.js'
import { withVectorRecovery } from './vectorRecovery.js'

import { PARKS_FOUNDATION_BODY } from './bcParksFoundation.js'

const additionalBodies = [
  ...RURAL_HEALTH_COLLECTIONS,
  ASI_COLLECTION,
  PARKS_FOUNDATION_BODY,
  ...AGRICULTURAL_PARTNER_BODIES,
  ...TOURISM_PARTNER_BODIES,
  ...AIRPORT_BODIES,
  ...FOREST_GENETICS_BODIES,
  SIFERP_COLLECTION,
  FORREX_COLLECTION,
  ...SURVEY_AND_LIBRARY_BODIES,
  CLEANBC_BODY, ENDORSED_2019,
  LEGISLATIVE_ASSEMBLY_BODY,
  ...EXPANDED_IDENTITY_BODIES.filter(({ id }) => id !== 'metro-vancouver'),
  ...REGIONAL_DISTRICT_BODIES, ...MUNICIPAL_IDENTITY_BODIES, ...RECOVERED_IDENTITY_BODIES,
  ...SCHOOL_IDENTITY_BODIES, ...POSTSECONDARY_IDENTITY_BODIES, IUS_BODY, YOUTH_BODY, ...HEALTH_COUNCIL_BODIES, FAMILY_COUNCIL_BODY, ALCOHOL_AND_DRUG_COMMISSION_BODY
]

const withArtworkVersions = (record) => ({
  ...record,
  assets: (record.assets ?? []).flatMap((design) => {
    const recovery = ACQUIRED_VECTORS[design.id]
    if (!recovery) return [design]

    const { asset, alternates = [], prefer, designLabel = design.designLabel ?? design.label } = recovery
    return [
      {
        ...design,
        label: recovery.designLabel ?? design.label,
        designLabel,
        versionLabel: design.versionLabel ?? 'Published image',
        ...(prefer && !design.preferredVector ? { preferredVector: asset.id } : {})
      },
      ...[asset, ...alternates].map((version) => ({
        evidenceType: 'native-pdf-vector-extraction',
        ...version,
        variantOf: design.id,
        format: 'svg',
        isVector: true,
        reconstruction: false,
        observedDate: '2026-11-25'
      }))
    ]
  }).flatMap((asset) => {
    const treatment = COLLECTED_VECTOR_VARIANTS[asset.id]
    return treatment ? [{ ...asset, ...treatment.overrides }, ...treatment.versions] : [asset]
  }).map(groupSpecimen)
})

export const ALL_COLLECTED_BODIES = withVectorRecovery([...COLLECTED_BODIES, ...additionalBodies].map((record) => {
  const guideArtwork = NORTHERN_TRAVEL_GUIDE_ARTWORK[record.id]
  return withArtworkVersions(guideArtwork ? { ...record, assets: [...record.assets, ...guideArtwork] } : record)
}))
export const ALL_COLLECTED_SPECIMENS = [...COLLECTED_SPECIMENS, buyBCSpecimens, fireSmartSpecimens, ecosystemsAtRiskSpecimens, resWestSpecimens, bearAwareSpecimens, environmentYouthCorpsSpecimens]
  .map((record) => withArtworkVersions(record.program === 'stronger-bc' ? withStrongerBCGuide(record) : record))

// Individual program specimens are shelved separately from bodies but share the display pipeline.
export const allCollectedAssets = () => [...ALL_COLLECTED_BODIES, ...ALL_COLLECTED_SPECIMENS]
  .flatMap((record) => record.assets)

// Initiatives can use the same display pipeline for artwork held only in Initiatives.
export const allCollectedDisplayAssets = () => [...allCollectedAssets(), educationProvinceWordmark, ...[
  'drc-dogwood-oval-1970', 'drc-fw-oval-1973', 'drc-fw-lockup-1973'
].map((id) => ({ id, format: 'svg', file: `identity-recreation-conservation/${id}.svg` }))]
