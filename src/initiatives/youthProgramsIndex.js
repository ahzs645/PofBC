// Three separately administered programs discussed in the youth estimates and debates of 1989.
export const ADVANCED_EDUCATION_1986 = 'ministry-of-advanced-education-and-job-training-1986'
export const EDUCATION_1979 = 'ministry-of-education-1979'
export const ENVIRONMENT_1988 = 'ministry-of-environment-1988'
export const SOCIAL_SERVICES_1986 = 'ministry-of-social-services-and-housing-1986'

export const YOUTH_PROGRAMS = [
  {
    id: 'challenge-89',
    title: 'Challenge ’89',
    subtitle: 'British Columbia Summer Employment Program',
    summary: 'In 1989 the province offered to share wages with employers creating summer jobs for young British Columbians. The program combined federal and provincial funding.',
    cover: {
      file: 'initiatives/challenge-89/employer-ad-1989.jpg',
      alt: 'Challenge ’89 summer employment advertisement offering employers help with wages',
      caption: 'Employer notice in the Gulf Islands Driftwood, March 29, 1989, p. A22'
    },
    tags: ['Summer jobs', 'Advertisement', 'Timeline'],
    searchTerms: ['Challenge 89', 'Challenge 1989', 'BC Youth', 'Student employment', 'Wage sharing', 'Stanley Hagen'],
    relatedBodyIds: [ADVANCED_EDUCATION_1986]
  },
  {
    id: 'passport-to-apprenticeship',
    title: 'Passport to Apprenticeship',
    subtitle: 'Education · Advanced Education and Job Training',
    summary: 'B.C. introduced this program in 1989 to give high-school trades students experience with employers before they left school.',
    tags: ['Apprenticeship', 'Secondary education', 'Timeline'],
    searchTerms: ['BC Youth', 'Stanley Hagen', 'Trades training', 'Work experience'],
    relatedBodyIds: [ADVANCED_EDUCATION_1986, EDUCATION_1979]
  },
  {
    id: 'environment-youth-corps',
    title: 'Environment Youth Corps',
    subtitle: 'Environment · Social Services and Housing',
    summary: 'Young people aged 16–24 worked on local conservation projects in a provincial employment and training program established in 1989.',
    tags: ['Youth employment', 'Conservation', 'Timeline'],
    searchTerms: ['BC Youth', 'Environmental youth services', 'Habitat restoration', 'Job training', 'Environment ministry'],
    relatedBodyIds: [ENVIRONMENT_1988, SOCIAL_SERVICES_1986]
  }
]
