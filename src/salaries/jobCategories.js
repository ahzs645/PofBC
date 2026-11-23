// The kind of work a position title names, so titles can be browsed by it: "Teacher Elementary" is
// teaching, "Fire Captain" fire, "Senior Policy Analyst" policy. Read from the title's key alone
// (positions.js titleKey: lower case, abbreviations written out, plurals made singular) by ordered
// keyword rules; the first rule that matches decides. Nothing is known of the employer here, so a
// title only an employer could explain ("Administrator", "Coast Mountain Bus Company") is filed by
// its words or left as Other.
//
// The order is deliberate:
// 1. A few exact titles whose words mislead ("Executive Assistant" is clerical, "Deputy Minister"
//    an executive, not a minister).
// 2. Elected and appointed office.
// 3. Fire, then police and corrections: their ranks use "chief", "captain" and "inspector", so a
//    "Fire Chief" is fire and a "Police Inspector" police, never executive or inspection.
// 4. Executive: chief officers, presidents, deputy ministers, general managers, executive directors.
//    Seniority beats field here, so a "Chief Financial Officer" is executive, not finance.
// 5. The fields, the more particular before the broader: "Clinical Nurse Educator" is nursing,
//    "Medical Laboratory Technologist" allied health, "Software Engineer" IT.
// 6. Management after every field: a manager, director or supervisor whose title names a field is
//    filed under that field ("Director, Clinical Informatics" is IT & informatics, "Manager, Payroll"
//    finance); only one that names none ("Director of Operations", "Team Leader") is management.
// 7. Clerical titles, then the generic professional ones (analyst, advisor, specialist, consultant,
//    project and program staff) as policy and programs, then Other.

/**
 * The kinds of work, in the order they are offered: leadership, then the public services (teaching,
 * health, social, safety and justice), the professions, the trades and the office. `short` names a
 * chip; `label` everywhere else. `other` is every title no rule reads.
 */
export const JOB_CATEGORIES = [
  { value: 'executive', label: 'Executive & senior leadership', short: 'Executive' },
  { value: 'elected', label: 'Elected & appointed officials', short: 'Elected & appointed' },
  { value: 'management', label: 'Management', short: 'Management' },
  { value: 'education', label: 'Teaching & education', short: 'Teaching' },
  { value: 'nursing', label: 'Nursing', short: 'Nursing' },
  { value: 'medical', label: 'Physicians & medical', short: 'Physicians' },
  { value: 'allied', label: 'Allied health', short: 'Allied health' },
  { value: 'social', label: 'Social & community services', short: 'Social services' },
  { value: 'police', label: 'Police & corrections', short: 'Police & corrections' },
  { value: 'fire', label: 'Fire & emergency', short: 'Fire' },
  { value: 'legal', label: 'Legal & justice', short: 'Legal' },
  { value: 'inspection', label: 'Inspection & enforcement', short: 'Inspection' },
  { value: 'engineering', label: 'Engineering', short: 'Engineering' },
  { value: 'it', label: 'IT & informatics', short: 'IT' },
  { value: 'science', label: 'Science & natural resources', short: 'Science & resources' },
  { value: 'finance', label: 'Finance & accounting', short: 'Finance' },
  { value: 'hr', label: 'Human resources', short: 'HR' },
  { value: 'policy', label: 'Policy, programs & communications', short: 'Policy & communications' },
  { value: 'trades', label: 'Trades & operations', short: 'Trades & operations' },
  { value: 'admin', label: 'Administration & clerical', short: 'Administration' },
  { value: 'other', label: 'Other', short: 'Other' }
]

const LABELS = new Map(JOB_CATEGORIES.map(({ value, label }) => [value, label]))
/** A category's label; Other's for one not known. */
export const jobCategoryLabel = (value) => LABELS.get(value) ?? LABELS.get('other')
/** Whether a value names a category (an address can hold anything). */
export const isJobCategory = (value) => LABELS.has(value)

// Each rule is a category and a pattern tried against the key with a space either side, so `\b` is a
// word edge and a pattern can name a phrase or, with ^ and $, a whole title. Employers abbreviate and
// join words ("nursecritical care", "engr", "mgmt"), so a few patterns take prefixes.
const RULES = [
  // 1. Exact or near-exact titles whose words point the wrong way.
  // Titles that name an employer, not a job ("Coast Mountain Bus Company"): nothing to read.
  ['other', /\b(company|authority|corporation) $/],
  ['admin', /\b(executive assistant|administrative assistant|admin assistant|office assistant|data entry|clerk typist|ministerial assistant|assistant to|ea to|executive coordinator to|trustee staff)\b/],
  ['executive', /\b(deputy minister)\b/],
  ['legal', /\b(judicial|public guardian)\b/],
  ['inspection', /\b(occupational safety|ombudsperson|occup hygiene|hygiene officer|weighmaster|building official)\b/],
  ['hr', /\b(health and safety|occ health|occupational health|worker s adviser|employer s adviser)\b/],
  ['finance', /\bclaim (examiner|exam|adjuster|officer|representative)\b/],
  ['policy', /\b(social planner|economist)\b/],
  ['science', /\b(forest|fish|plant|vet|avian|poultry|aquatic|insect)( \w+)? pathologist\b/],

  // 2. Elected and appointed office.
  ['elected', /\b(mayor|councill?or|council member|member of (the )?legislative assembly|mla|premier|cabinet minister|minister|speaker|trustee|board member|electoral area director|vice chair|vicechr|vice chairperson|tribunal member|parliamentary secretary|elected official|board of governor|board governor|commissioner|committee member)\b/],
  ['elected', /\bmember\b.*\btribunal\b|\btribunal\b.*\bmember\b/],
  ['elected', /^ (chair|chairperson|board chair|member|director electoral area|\w+ member) $/],

  // 3. Fire and emergency, then police and corrections.
  ['fire', /\b(fire|firefighter|firefighting|fighter|fireman|wildfire|battalion chief|platoon chief|platoon captain|forest protection|emergency (management|program|response|coordinator|planner|planning|operation)|ems|avalanche|search and rescue|initial attack|unit crew)\b/],
  ['fire', /^ (captain|lieutenant)\b/],
  ['police', /\b(police|constable|cst|sergeant|corporal|detective|rcmp|sheriff|correction|correctional|corrections|adlt|custody|warden|probation|parole|jail|prison|offender|peace officer|commissionaire|forensic identification|crime analyst)\b/],

  // 4. Executive and senior leadership.
  ['executive', /\b(chief( \w+){1,4} officer|chief of staff|ceo|cfo|cio|coo|cao|cto|cno|cmo|president|vp|adm|associate deputy minister|assistant deputy minister|assist deputy minister|general manager|gm|city manager|town manager|chief administrator|chief commissioner|chief judge|chief justice|chief coroner|auditor general|comptroller general|executive director|execdir|executive lead|execld|superintendent of (school|education)|school superintendent)\b/],
  // Ships' officers and crews (B.C. Ferries) before engineering: a "Third Engineer" is a marine trade.
  ['trades', /\b((first|second|third|fourth|1st|2nd|3rd|4th) (class )?engineer|(senior )?chief engineer|assistant engineer|(chief|first|second|third) officer|engine room|vessel|deckhand|ship|shipwright|marine|ferry|steward|boatswain|bosun)\b/],

  // 5. The fields. Nursing first: a nurse educator or nurse manager is nursing.
  ['nursing', /\b(\w*nurse\w*|nursing|nur|nrsg|rn\w*|lpn\w*|rpn|midwife|care aide|health care aide|health care assistant|resident care attendant)\b/],
  ['allied', /\b(speech\w*|mrt|diagmedsono\w*|echocardiograph\w*|veterinar\w*|veterninar\w*|medical (laboratory|radiation|device|imaging) \w+|laboratory technologist|lab technologist|radiation therap\w*|mri|ultrasound|sonographer|cardiology technologist|perfusionist|respiratory therap\w*)\b/],
  ['medical', /\b(physician|doctor|surgeon|surg\w*|psychiatrist|pathologist|radiologist|anesthesiologist|anaesthetist|anesthetist|hospitalist|pediatrician|paediatrician|oncologist|cardiologist|neurologist|dermatologist|obstetrician|internist|intensivist|dentist|orthodontist|medical officer|medical health officer|medical director|medical lead|family practice|general practitioner|resident physician|medical)\b/],
  ['allied', /\b(pharmacist|pharmacy|therapist|therapy|physiotherapist|physio|audiologist|optometrist|optician|chiropractor|dietitian|dietician|nutritionist|psychologist|psychometrist|paramedic|kinesiologist|lab(oratory)? tech\w*|laboratory|lab assistant|dental|hygienist|sterile processing|public health|health officer|health inspector)\b/],

  // Human resources before social services: "disability management" and "workplace wellness" are HR.
  ['hr', /\b(human resource|hr|bchr|recruiter|recruitment|recruit|staffing|talent|workforce|labour relation|labor relation|employee relation|industrial relation|compensation|classification|people and culture|organizational development|disability management|return to work|rtw|wellness|workplace|employer adviser|worker adviser|collective agreement|benefit)\b/],
  ['social', /\b(social|child protection|child welfare|family support|guardianship|adoption|permanency|foster|resource worker|youth worker|child and youth|child youth|cymh|cysn|mental health|mh|addiction|substance use|counsellor|counselor|counselling|clinician|case worker|caseworker|case manager|outreach|community (support|service|development|worker|liaison|navigator|program)|support worker|life skill|settlement|income assistance|employment and assistance|disability|housing|homeless|shelter|victim service|family justice|family service|welfare|navigator|care worker|recreation|leisure|lifeguard|aquatic|camp|program leader|childcare|child care|early childhood|youth|vocational|rehab|chaplain|advocate|direct care)\b/],

  // Teaching and education. A principal is only a school's when the title is little else.
  ['education', /^ ((vice|assistant|deputy|acting|elementary|secondary|middle|district|school|elem|elementary vice|secondary vice) )*(principal|viceprincipal)( (elementary|secondary|middle|school|i|ii|iii))? $/],
  ['education', /\b(teacher|teaching|educator|education|educ|edu|elementary|secondary|school|tutor|instructor|instructional|instr|inst|instruction|fac|ed|lecturer|archivist|curator|department chair|division chair|professor|prof|faculty|dean|academic|curriculum|curricular|librarian|library|vice principal|viceprincipal|learning|literacy|esl|english language|kindergarten|trainer|training)\b/],

  // Legal and justice.
  ['legal', /\b(counsel|crown|lawyer|solicitor|barrister|legal|paralegal|law|litigation|judge|justice|judicial|court|tribunal|arbitrator|adjudicator|adjudication|mediator|coroner|notary|articled|legislative drafter|appeal|hearing|prosecutor|registrar of)\b/],

  // Inspection, licensing and enforcement.
  ['inspection', /\b(inspector|inspection|insp|inspe|inspect|investigator|investigation|investigative|investg|bylaw|by law|enforcement|enf|compliance|compl|conservation officer|c and e|cvse|safety officer|ohs|licensing|lic|licence|license|authorization|auth|permit|permitting|examiner|regulatory|regulation|commercial vehicle|parking|animal control)\b/],

  // IT before engineering: a software or network engineer is IT.
  ['it', /\b(software|developer|programmer|programming|database|dba|network|system|systems|sys|application|app|it|information technology|informatics|information management|im|information system|cyber|cybersecurity|security analyst|security architect|data|digital|computer|web|ux|ui|gis|geospatial|spatial|desktop|help desk|service desk|technical support|devops|cloud|solution|solutions|enterprise architect|technical architect|informatic|technical analyst|technical specialist|business analyst|business system|sap|erp|scrum|agile|product owner|telecommunication|telecom|electronic|automation|technology)\b/],
  // The rest of health once the specific titles above, and IT ("Clinical Informatics"), have had their say.
  ['allied', /\b(clinical|clinic|patient|health)\b/],
  ['engineering', /\b(engineer\w*|engr|eng|engineering|technologist|surveyor|survey|geomatic|geotechnical|geotech|architect|architecture|drafting|draftsperson|cad|structural|mechanical|civil|hydraulic|bridge|construction|asset management|capital project|infrastructure)\b/],

  // Science and natural resources.
  ['science', /\b(scientist|science|biologist|ecologist|ecosystem|ecosy|geologist|geoscientist|hydrologist|hydrogeologist|chemist|chemistry|physicist|entomologist|agrologist|agri|agriculture|agricultural|botanist|forester|forestry|forest|silviculture|timber|woodland|range|rangeland|tenure|resource|land|habitat|fish|fishery|fisheries|wildlife|environmental|environment|environ|enviro|env|climate|conservation|stewardship|watershed|soil|mineral|mine|mining|petroleum|energy|meteorologist|weather|seed|invasive|vegetation|ranger|natural|carbon|contaminated|aquaculture|archaeologist|archaeology|heritage|arborist|arboriculture|horticulture|horticulturist)\b/],

  // Finance and accounting.
  ['finance', /\b(finance|financial|fin|financ|fiscal|accountant|accounting|acct|account|accounts|auditor|audit|payroll|budget|tax|taxation|revenue|treasurer|treasury|controller|comptroller|actuary|actuarial|investment|invest|portfolio|equity|credit|debt|banking|bank|pension|insurance|underwriter|adjuster|claim|estimator|procurement|procurement&contractspecialist|purchasing|purchaser|buyer|contract|contracting|risk|billing|collections? officer|collector|assessor|appraiser|valuation|pricing|costing|expenditure|grant|funding)\b/],

  // Policy, planning and communications, by their own words.
  ['policy', /\b(policy|pol|planner|planning|plng|strategic|strategy|strategist|strat|economic|economy|research|researcher|analytic|statistic\w*|evaluation|eval|performance|legislation|legislative|intergovernmental|intergov|igr|treaty|reconciliation|negotiator|negotiation|engagement|stakeholder|partnership|relation|relations|communication|comm|public affair|media|marketing|market|editor|writer|content|graphic|designer|publication|creative|brand|protocol|event|issue|correspondence|foi|freedom of information|privacy|records management|governance|transformation|innovation|change|lean|indigenous)\b/],

  // Trades and operations.
  ['trades', /^ (senior )?master( \w+)? $/],
  ['trades', /\b(electrician|electrical|mechanic|carpenter|plumber|plumbing|pipefitter|pipelayer|steamfitter|sprinkler|welder|welding|machinist|millwright|fabricator|metal|painter|glazier|mason|bricklayer|roofer|locksmith|hvac|refrigeration|boiler|instrumentation|instrument|lineman|powerline|lineperson|serviceperson|tradesperson|journeyperson|journeyman|apprentice|trade|leadhand|chargehand|foreman|foreperson|subforeman|labourer|laborer|operator|operating|equipment|driver|truck|bus|transit|vehicle|fleet|marine|vessel|ship|deckhand|mate|boatswain|terminal|ferry|oiler|maintenance|maint|maintainer|custodian|custodial|janitor|caretaker|cleaner|cleaning|groundskeeper|ground|gardener|landscape|landscaper|utility|water|wastewater|waterwork|wwtp|sewer|drainage|road|street|asphalt|concrete|sanitation|waste|refuse|recycling|garbage|collection|cemetery|warehouse|storekeeper|store|shipping|receiving|stock|inventory|logistic|dispatcher|dispatch|courier|mail|cook|chef|kitchen|food|baker|butcher|meat|bartender|housekeeping|laundry|security officer|guard|attendant|operation worker|crew|worker|technician|tech|chainsaw|public work|tradesman|wireman|rigger|insulator|repairer|pruner|keeper|utilityworker|partsperson|sign maker|shop|plant|production|signal|radio|traffic|flagger|scaling|scaler|pump|irrigation|arena|facility|building service|ice|airport|aviation|pilot|rail|track|park|parks|transportation|stage|theatre)\b/],

  // 6. Management: a manager, director or supervisor whose title names no field.
  ['management', /\b(manager|mgr|mgmt|mgt|mgmnt|mngmt|mgnt|management|director|dir|supervisor|supervising|spvr|supr|supt|sup|superintendent|administrator|head|lead|leader|tl|chief|executive|managing|operation|operations|ops)\b/],

  // 7. Clerical, then the generic professional titles.
  ['admin', /\b(clerk|clerical|secretary|secretariat|receptionist|administrative|admin|administration|office|assistant|assist|support staff|excluded staff|staff|record|registry|registration|registrar|typist|transcriptionist|scheduler|scheduling|customer service|client service|customer|client|front counter|frontcounter|representative|rep|agent|cashier|teller|intake|call centre|call center|contact centre|coordinator|coord|coor|support|aide|helper)\b/],
  ['policy', /\b(analyst|analysis|analy|advisor|adviser|adv|specialist|specialis|spec|consultant|consult|project|proj|program|prog|prg|prgm|initiative|init|officer|planner|plan|business|corporate|service|services|delivery|quality|improvement|liaison)\b/]
]

const cache = new Map()

/**
 * The kind of work a title key names: one of JOB_CATEGORIES' values. Pass a key from titleKey (or
 * keyedTitles); other text is read only as far as it already is one.
 */
export const jobCategory = (key) => {
  const text = ` ${String(key ?? '').trim()} `
  let found = cache.get(text)
  if (!found) {
    found = RULES.find(([, pattern]) => pattern.test(text))?.[0] ?? 'other'
    cache.set(text, found)
  }
  return found
}

/** How many titles each category holds, with `all` for every title. */
export const jobCategoryCounts = (titles) => {
  const counts = Object.fromEntries(JOB_CATEGORIES.map(({ value }) => [value, 0]))
  for (const title of titles) counts[jobCategory(title.key)] += 1
  return { all: titles.length, ...counts }
}
