export const CNC_SUBJECT = 'college-of-new-caledonia'

const college = 'https://www.cnc.bc.ca'
const calendar = (years, version) =>
  `${college}/docs/calendars/academiccalendar-${years}.pdf?sfvrsn=${version}_1#page=1`

export const CNC_BRAND_RESOURCES = [
  { label: 'CNC brand hub', url: `${college}/about/brand` },
  { label: 'Brand Guidelines v1.5 · sign-in', url: 'https://cnc.bc.ca/docs/internal/marketing-and-events/college-of-new-caledonia-_brand-guidelines_v1-5.pdf' },
  { label: 'Digital Design System Guide · sign-in', url: `${college}/design-system-guide` },
  { label: 'Public brand policy', url: `${college}/docs/policies/cnc-brand.pdf?sfvrsn=e8704e30_1` },
  { label: 'Official media logo · PNG', url: `${college}/images/graphics/logos/cnc/cnc-logo-header.png?sfvrsn=572ac51f_1` }
]

const specimen = (file, width, height, label, alt, credit, url) => ({
  file: `identity-editorial/cnc/${file}`, width, height, label, alt, credit, url,
  format: file.endsWith('.svg') ? 'Vector excerpt' : 'Raster excerpt'
})

export const CNC_CURRENT_MARKS = [
  specimen('stacked.svg', 122, 111, 'Primary stacked logo',
    'College of New Caledonia in charcoal above a red rule and CNC initials on pale green',
    '2019–20 course calendar, cover', calendar('2019-2020', '5df38d8d')),
  specimen('stacked-reverse.svg', 122, 111, 'Primary stacked logo in reverse',
    'White college name above red rule and initials on charcoal',
    '2020–21 course calendar, cover', calendar('2020-2021', 'e87fafaf')),
  specimen('horizontal.webp', 512, 155, 'Primary horizontal logo',
    'Red CNC initials and bar beside the full college name on two lines',
    'Education Council agenda, March 11, 2025, p. 1', 'https://collegeofnewcaledonia.civicweb.net/document/127737/#page=1'),
  specimen('enclosed-red.svg', 101, 101, 'Secondary red square',
    'White bar and CNC initials inside a red square',
    'Equity, Diversity, Inclusion and Belonging Strategy 2026–31, cover',
    `${college}/docs/public/governance/initiatives-and-reports/edib-plan-webc11b7f00c64742fcab13ad7e24a05a14.pdf?sfvrsn=aa5c3de8_1#page=1`),
  specimen('enclosed-white.svg', 109, 109, 'Secondary white square on teal',
    'White square with the teal background showing through the bar and initials',
    '2026–27 course calendar, cover', calendar('2026-2027', 'a1e410a2'))
]

export const CNC_HISTORICAL_MARKS = [
  specimen('early-monogram.webp', 495, 512, 'Early broad CNC monogram',
    'White geometric CNC monogram over the college name on the black cover',
    '1970–71 course calendar, cover', calendar('1970-1971', '9faebca7')),
  specimen('early-shield.webp', 512, 366, 'Early shield and college name',
    'Shield with crosses, trees, and a motto scroll next to the geometric CNC mark and a band naming the college and institute',
    '1978–79 course calendar, cover', calendar('1978-1979', '316e7b7c')),
  specimen('early-monogram-orange.webp', 512, 338, 'Broad CNC monogram in orange',
    'Orange geometric CNC monogram below the cover illustration',
    '1981–82 course calendar, cover', calendar('1981-1982', '3da5e70e')),
  specimen('calendar-wordmark.webp', 512, 273, 'Bold calendar wordmark in green',
    'Green College of New Caledonia lettering on a yellow calendar cover',
    '1998–99 course calendar, cover', calendar('1998-1999', '24ef1519')),
  specimen('calendar-wordmark-red.webp', 512, 259, 'Bold calendar wordmark in red',
    'Red College of New Caledonia lettering over a blue and photographic calendar cover',
    '2000–01 course calendar, cover', calendar('2000-2001', '2285fefb')),
  specimen('interlocking-stacked.svg', 153, 155, 'Interlocking monogram above the name',
    'White interlocking geometric monogram over the college name and web address on burgundy',
    'Institutional Accountability Plan and Report 2016–17, cover',
    `${college}/docs/public/governance/accountability-reports/accountability-report-2016-2017.pdf?sfvrsn=fd66ef46_3#page=1`),
  specimen('interlocking-horizontal.svg', 270, 103, 'Interlocking monogram beside the name',
    'The college name and web address sit to the left of the white interlocking monogram on green',
    '2018–19 course calendar, cover', calendar('2018-2019', '555cc94c')),
  specimen('anniversary.webp', 512, 252, '50th anniversary lockup',
    'The stacked college logo beside a bold 50th Anniversary wordmark',
    'CNC 50th anniversary announcement, September 4, 2019',
    `${college}/news/article/2019/09/04/cnc-welcomes-students-back-for-milestone-50th-year`)
]

export const cncCover = (theme) => CNC_CURRENT_MARKS[theme === 'dark' ? 1 : 0]
