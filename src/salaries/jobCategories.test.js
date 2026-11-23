import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { gunzipSync } from 'node:zlib'
import { isJobCategory, JOB_CATEGORIES, jobCategory, jobCategoryCounts, jobCategoryLabel } from './jobCategories.js'
import { keyedTitles, titleKey } from './positions.js'

// Titles as employers disclosed them, read the way the index keys them.
const of = (title) => jobCategory(titleKey(title))

const EXPECTED = {
  executive: ['Executive Director', 'Deputy Minister or Associate Deputy Minister', 'Chief Administrative Officer', 'Chief Financial Officer', 'CFO', 'President & CEO', 'Assistant Deputy Minister', 'ADM, Corporate Services', 'City Manager', 'General Manager, Engineering Services', 'Chief Medical Health Officer', 'Chief Information Officer'],
  elected: ['Mayor', 'Councillor', 'Councilor', 'Member of the Legislative Assembly', 'Premier or Minister', 'School Trustee', 'Trustee', 'Vice Chair', 'Board Chair', 'Member', 'Tribunal Member'],
  nursing: ['Registered Nurse', 'RN', 'Registered NurseCritical Care', 'LPN', 'Licensed Practical Nurse', 'Nurse Practitioner', 'Public Health Nurse', 'Clinical Nurse Educator', 'Manager, Nursing Services'],
  medical: ['Physician', 'Salaried Physician', 'Medical Health Officer', 'Medical Advisor II', 'Psychiatrist', 'Consultant Pathologist'],
  allied: ['Pharmacist', 'Paramedic', 'Licensed Psychologist', 'Speech Language Pathologist', 'Speech and Language Pathologist', 'Physiotherapist 1', 'Occupational Therapist', 'Respiratory Therapist', 'Medical Laboratory Technologist', 'Dietitian'],
  social: ['Child Protection Worker', 'CYMH Clinician', 'Mental Health Clinician', 'Guardianship Worker', 'Social Worker', 'Counsellor', 'Resource Worker', 'Adoption Worker', 'Recreation Programmer II', 'Youth Worker'],
  education: ['Teacher', 'Teachers', 'Teacher Elementary', 'Teaching Staff', 'Instructor', 'Professor', 'Assistant Professor', 'Principal', 'Vice Principal', 'Elementary Principal', 'District Principal', 'Librarian I', 'Faculty', 'Special Education Sec', 'Dean'],
  police: ['Police Constable', 'Constable', 'Sergeant', 'Staff Sergeant', 'Correction Serv 18 Adlt Cust', 'Correctional Officer', 'Deputy Sheriff', 'Probation Officer', 'Assistant Deputy Warden', 'Police Inspector', 'Deputy Chief Constable', 'Detective'],
  fire: ['Firefighter', 'Fire Fighter 1st Class', 'Fire Captain', 'Fire Chief', 'Deputy Fire Chief', 'Battalion Chief', 'Captain', 'Lieutenant', 'Platoon Captain', 'Wildfire Technician', 'Forest Protection Officer', 'Fire Prevention Inspector'],
  legal: ['Crown Counsel', 'Legal Counsel Level 3', 'Judge', 'Solicitor III', 'Paralegal', 'Arbitrator', 'Adjudicator', 'Coroner', 'Judicial Case Manager', 'Lawyer'],
  inspection: ['Conservation Officer', 'Occupational Safety Officer', 'Investigator', 'Building Inspector', 'District Plumbing and Gas Inspector', 'Bylaw Enforcement Officer', 'Senior Lic Auth Officer', 'Building Official III', 'Ombudsperson Officer'],
  engineering: ['Civil Engineer II', 'Engineering Assistant IV', 'Engineering Technologist', 'Senior Project Engineer', 'Principal Engineer', 'Bridge Engineer', 'Landscape Architect'],
  it: ['Business Analyst', 'System Analyst II', 'Computer Programmer Analyst', 'Database Administrator', 'Software Engineer', 'Network Engineer', 'Senior Security Analyst', 'GIS Analyst', 'Director, Clinical Informatics', 'Solution Architect', 'Data Scientist'],
  science: ['Practice Forester', 'Senior Biologist', 'Land and Resource Specialist', 'Stewardship Officer', 'Woodland Supervisor', 'Research Scientist', 'Hydrologist', 'Forest Pathologist', 'Arborist'],
  finance: ['Senior Auditor', 'Financial Analyst', 'Accountant', 'Director of Finance', 'Payroll Manager', 'Manager, Payroll', 'Senior Tax Auditor', 'Buyer II', 'Procurement Specialist', 'Portfolio Manager', 'Claim Examiner', 'Injury Adjuster'],
  hr: ['Human Resource Consultant III', 'HR Advisor', 'Industrial Relation Officer', 'Employer Adviser', 'Recruiter', 'Manager, Labour Relations', 'Health and Safety Advisor'],
  policy: ['Senior Policy Analyst', 'Policy Analyst', 'Public Affairs Officer', 'Planner II', 'Senior Economist', 'Social Planner I', 'Communications Manager', 'Senior Advisor', 'Ministerial Advisor', 'Graphic Designer', 'Program Analyst'],
  trades: ['Electrician', 'Trade Electrician', 'Journeyman Mechanic', 'Carpenter', 'Bus Operator', 'Truck Driver III', 'Operation Worker II', 'Equipment Operator III', 'Labourer 2', 'Third Engineer', 'Chief Engineer', 'Deckhand', 'Master', 'Custodian', 'Maintenance Technician II'],
  management: ['Director', 'Manager', 'Team Leader', 'Director of Operations', 'Senior Project Manager', 'Program Manager', 'Regional Director', 'Superintendent I', 'Administrator', 'Section Head'],
  admin: ['Executive Assistant', 'Administrative Assistant', 'Administrative Coordinator', 'Clerk IV', 'Support Staff', 'Excluded Staff', 'Ministry Representative', 'Ministerial Assistant', 'Receptionist', 'City Clerk', 'Assistant to the Mayor'],
  other: ['Coast Mountain Bus Company', 'B.C. Rapid Transit Company', 'South Coast B.C. Transportation Authority', '', 'Civilian']
}

test('representative disclosed titles land in their kind of work', () => {
  const wrong = Object.entries(EXPECTED).flatMap(([category, titles]) => titles
    .filter((title) => of(title) !== category).map((title) => `${title} → ${of(title)}, expected ${category}`))
  assert.deepEqual(wrong, [])
})

test('the order decides between kinds deliberately', () => {
  // Fire and police ranks are theirs, not executive or inspection.
  assert.equal(of('Fire Chief'), 'fire')
  assert.equal(of('Police Inspector'), 'police')
  assert.equal(of('Inspector'), 'inspection')
  // Seniority beats field for chief officers; a director or manager is filed by the field named.
  assert.equal(of('Chief Financial Officer'), 'executive')
  assert.equal(of('Director, Clinical Informatics'), 'it')
  assert.equal(of('Director of Nursing'), 'nursing')
  assert.equal(of('Manager, Finance'), 'finance')
  assert.equal(of('Director of Operations'), 'management')
  // An executive's assistant is clerical; a deputy minister is not a minister; a deputy mayor is.
  assert.equal(of('Executive Assistant'), 'admin')
  assert.equal(of('Deputy Minister'), 'executive')
  assert.equal(of('Deputy Mayor'), 'elected')
  // A school's principal is teaching; a principal engineer or consultant is not.
  assert.equal(of('Elementary Vice Principal'), 'education')
  assert.equal(of('Principal Engineer'), 'engineering')
  assert.equal(of('Principal Consultant'), 'policy')
  // Workplace safety inspectors enforce; an employer's own safety advisor is HR.
  assert.equal(of('Occupational Safety Officer'), 'inspection')
  assert.equal(of('Occupational Health and Safety Advisor'), 'hr')
  // A ship's engineer is a marine trade, a speech pathologist allied health, a forest pathologist science.
  assert.equal(of('Third Engineer'), 'trades')
  assert.equal(of('Speech Language Pathologist'), 'allied')
  assert.equal(of('Forest Pathologist'), 'science')
})

test('the categories are listed once each, with labels, and unknown values read as other', () => {
  const values = JOB_CATEGORIES.map(({ value }) => value)
  assert.equal(new Set(values).size, values.length)
  assert.equal(values.at(-1), 'other')
  assert.ok(JOB_CATEGORIES.every(({ label }) => label))
  assert.equal(jobCategoryLabel('fire'), 'Fire & emergency')
  assert.equal(jobCategoryLabel('nonsense'), 'Other')
  assert.equal(isJobCategory('nursing'), true)
  assert.equal(isJobCategory('all'), false)
  assert.equal(jobCategory(null), 'other')
})

test('counts cover every title once', () => {
  const titles = ['teacher', 'firefighter', 'fire captain', 'coast mountain bus company'].map((key) => ({ key }))
  const counts = jobCategoryCounts(titles)
  assert.equal(counts.all, 4)
  assert.equal(counts.education, 1)
  assert.equal(counts.fire, 2)
  assert.equal(counts.other, 1)
  assert.equal(JOB_CATEGORIES.reduce((sum, { value }) => sum + counts[value], 0), 4)
})

test('the published index: most records are filed under a kind of work', () => {
  const index = JSON.parse(gunzipSync(readFileSync(new URL('../../public/salaries/positions/index.json.gzip', import.meta.url))))
  const titles = keyedTitles(index)
  const total = titles.reduce((sum, title) => sum + title.rows, 0)
  const other = titles.filter((title) => jobCategory(title.key) === 'other').reduce((sum, title) => sum + title.rows, 0)
  assert.ok(1 - other / total > 0.85, `only ${((1 - other / total) * 100).toFixed(1)}% of records categorized`)
})
