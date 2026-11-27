const sources = [
  { id: 'bc-guidelines', title: 'Joint Emergency Preparedness Program Guidelines', publisher: 'Ministry of Attorney General, Provincial Emergency Program', date: 'July 1993', url: 'https://www.publicsafety.gc.ca/lbrr/archives/ua%20929.c2%20b75%201993-eng.pdf' },
  { id: 'commons', title: 'House of Commons Debates, sitting 189, reply to Question No. 992', publisher: 'Parliament of Canada', url: 'https://www.ourcommons.ca/Content/House/411/Debates/189/HAN189-E.PDF' },
  { id: 'outdoor-guide', title: 'Risk Management for Outdoor Programs: A Guide for Students', publisher: 'Centre for Curriculum, Transfer and Technology and BC Adventure Tourism Programs Articulation Committee', date: '2003', url: 'https://www.nic.bc.ca/_resources/pdf/adventure-guiding-risk-guide.pdf' }
]

export const jeppDetail = (entry) => ({
  id: entry.id, title: entry.title, sources,
  hero: { title: entry.title, eyebrow: 'Emergency preparedness', description: entry.summary, image: entry.cover, caption: entry.cover.caption },
  relatedLinks: [{ label: 'Provincial Emergency Program logos and SVG downloads', to: { view: 'gallery', logos: 'specimens-provincial-emergency-program', mark: 'pep-striped-ink' } }],
  sections: [
    { id: 'marks', label: 'Logos', type: 'records', layout: 'marks', title: 'Two marks on the 1993 cover', records: [
      { id: 'jepp-cover', title: 'Joint Emergency Preparedness Program', kind: 'program-identity',
        description: 'Four upright, striped initials sit inside a screened square frame. The cover identifies the joint funding program above the provincial ministry and PEP signatures.',
        image: { ...entry.cover, sourceId: 'bc-guidelines', sourcePage: 2, date: '1993-07', evidenceType: 'printed-source-crop' },
        sourceRefs: [{ sourceId: 'bc-guidelines', page: 2 }] },
      { id: 'pep-cover', title: 'Provincial Emergency Program', kind: 'program-identity',
        description: 'PEP’s slanted initials cross a striped disc. The July 1993 cover has lighter lettering than the 2003 guide. The gallery reconstruction follows the heavier design.',
        image: { file: 'initiatives/jepp/pep-1993-cover.png', alt: 'PEP monogram beside the three-line Provincial Emergency Program name', caption: 'Provincial signature from the same July 1993 cover', sourceId: 'bc-guidelines', sourcePage: 2, date: '1993-07', evidenceType: 'printed-source-crop' },
        sourceRefs: [{ sourceId: 'bc-guidelines', page: 2 }, { sourceId: 'outdoor-guide', page: 1 }] }
    ] },
    { id: 'history', label: 'History', type: 'timeline', title: 'How the joint program operated', records: [
      { id: 'jepp-established', date: '1980', title: 'Federal cost sharing begins', description: 'Canada helped provinces and territories build emergency response capacity through planning, training and specialized equipment.', sourceRefs: [{ sourceId: 'commons' }] },
      { id: 'bc-delivery', date: 'July 1993', title: 'British Columbia revises its guidelines', description: 'Emergency Preparedness Canada administered JEPP federally. B.C. designated PEP as its sole agency for applications, claims and negotiations. Provincial ministries, incorporated municipalities and regional districts could apply. The contribution ratio was negotiable.', sourceRefs: [{ sourceId: 'bc-guidelines', locator: 'Chapter 1, sections 1.2–1.4' }] },
      { id: 'jepp-end', date: 'March 31, 2013', title: 'JEPP concludes', description: 'The federal government identified this as the end date in its written answer to the House of Commons.', sourceRefs: [{ sourceId: 'commons' }] }
    ] },
    { id: 'sources', label: 'Sources', type: 'sources', title: 'Guidelines, publications and parliamentary evidence', records: sources }
  ]
})
