import { COLLECTED_BODIES, COLLECTED_SPECIMENS } from './collectedData.js'
import { EXPANDED_IDENTITY_BODIES } from './expandedIdentityData.js'
import { MUNICIPAL_IDENTITY_BODIES } from './municipalIdentityData.js'
import { RECOVERED_IDENTITY_BODIES } from './recoveredIdentityData.js'
import { POSTSECONDARY_IDENTITY_BODIES } from './postsecondaryIdentityData.js'
import { FAMILY_COUNCIL_BODY } from './councilForTheFamily.js'
import { ALCOHOL_AND_DRUG_COMMISSION_BODY } from './alcoholAndDrugCommission.js'
import { IUS_BODY } from './iusCollectionData.js'
import { SCHOOL_IDENTITY_BODIES } from '../schools/integration.js'

const additionalBodies = [
  ...EXPANDED_IDENTITY_BODIES, ...MUNICIPAL_IDENTITY_BODIES, ...RECOVERED_IDENTITY_BODIES,
  ...SCHOOL_IDENTITY_BODIES, ...POSTSECONDARY_IDENTITY_BODIES, IUS_BODY, FAMILY_COUNCIL_BODY, ALCOHOL_AND_DRUG_COMMISSION_BODY
]

export const ALL_COLLECTED_BODIES = [...COLLECTED_BODIES, ...additionalBodies]

// Individual program specimens are shelved separately from bodies but share the display pipeline.
export const allCollectedAssets = () => [...COLLECTED_BODIES, ...COLLECTED_SPECIMENS, ...additionalBodies]
  .flatMap((record) => record.assets ?? [])
