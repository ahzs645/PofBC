const plan = 'https://www.bchydro.com/toolbar/about/strategies-plans-regulatory/supply-operations/power-smart-plan.html'
const forum = 'https://www.bchydro.com/content/dam/BCHydro/customer-portal/documents/power-smart/ps-forum/ps-forum-archive-program-2013.pdf'

export const POWER_SMART_SOURCES = [
  { id: 'bc-hydro-power-smart-plan', title: 'Power Smart 2.0 plan', publisher: 'BC Hydro', url: plan,
    note: 'BC Hydro dates the original program to 1989 and its Power Smart 2.0 plan to May 2026.' },
  { id: 'bc-hydro-power-smart-forum-2013', title: 'Power Smart Forum 2013 program', publisher: 'BC Hydro',
    url: forum, note: 'The cover places the reversed Power Smart wordmark below the BC Hydro mark.' }
]

export const powerSmartDetail = (entry) => ({
  id: entry.id,
  title: entry.title,
  hero: { eyebrow: 'BC Hydro initiative', title: entry.title, description: entry.summary, image: entry.cover, caption: entry.cover.caption },
  stats: [{ value: 1989, label: 'program launched' }],
  sources: POWER_SMART_SOURCES,
  relatedLinks: [
    { label: 'Power Smart wordmark and source evidence', to: { view: 'gallery', logos: 'collected-power-smart', mark: 'source-recovered-power-smart-reversed-wordmark' } },
    { label: 'BC Hydro’s corporate logos', to: { view: 'gallery', logos: 'bc-hydro' } }
  ],
  sections: [
    {
      id: 'timeline', label: 'Timeline', type: 'timeline', eyebrow: 'Energy efficiency',
      title: 'Power Smart in BC Hydro’s records',
      description: 'The program launch, a documented logo specimen, and the later plan are separate events.',
      records: [
        { id: 'launch-1989', date: '1989', dateRole: 'program launch', title: 'BC Hydro launches Power Smart',
          description: 'Power Smart promotes using electricity more efficiently in homes and businesses.',
          sourceRefs: [{ sourceId: 'bc-hydro-power-smart-plan' }] },
        { id: 'forum-2013', date: '2013-10-22', dateRole: 'dated specimen', title: 'Power Smart Forum cover',
          description: 'The forum program shows a reversed Power Smart wordmark. This documents use, not when the design was adopted.',
          sourceRefs: [{ sourceId: 'bc-hydro-power-smart-forum-2013', page: 1 }] },
        { id: 'plan-2026', date: '2026-05', dateRole: 'plan release', title: 'BC Hydro releases its Power Smart 2.0 plan',
          description: 'The plan covers energy efficiency and demand response. Its release is not a date for the forum logo.',
          sourceRefs: [{ sourceId: 'bc-hydro-power-smart-plan' }] }
      ]
    },
    { id: 'sources', label: 'Sources', type: 'sources', eyebrow: 'Evidence', title: 'BC Hydro’s records', records: POWER_SMART_SOURCES }
  ]
})
