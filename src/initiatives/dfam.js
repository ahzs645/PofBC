const sources = [
  { id: 'sheet', title: 'DFAM Forest Health Technical Information Sheet', publisher: 'B.C. Ministry of Forests', date: 'April 2003', url: 'https://digitalcollections.llbc.leg.bc.ca/handle/123456789/302306' },
  { id: 'bill', title: 'Forests Statutes Amendment Act (No. 2), 2003, section 2', publisher: 'Legislative Assembly of British Columbia', url: 'https://www.bclaws.gov.bc.ca/civix/document/id/lc/billsprevious/4th37th%3Agov44-3' },
  { id: 'table', title: 'Forest Act, Table of Legislative Changes', publisher: 'BC Laws', url: 'https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/e4tlc96157' },
  { id: 'arrow', title: 'Arrow Timber Supply Area timber supply review data package', publisher: 'Arrow TSA DFAM Group', date: 'February 2004, finalized March 4', url: 'https://data.nrs.gov.bc.ca/TSR_Historical/TSA/Arrow_01/TSR_2005/Data_Package/Arrow_TSA_20032004_Data_Pack_v3.4.pdf' },
  { id: 'report', title: '2004/05 annual service plan report', publisher: 'B.C. Ministry of Forests', url: 'https://www.bcbudget.gov.bc.ca/annual_reports/2004_2005/for/Ministry_Role_and_Services.htm' }
]

export const dfamDetail = (entry) => ({
  id: entry.id, title: entry.title, sources,
  hero: { title: entry.title, eyebrow: entry.subtitle, description: entry.summary, image: entry.cover, caption: entry.cover.caption },
  relatedLinks: [{ label: 'BC Timber Sales logo history', to: { view: 'gallery', logos: 'bcts' } }],
  sections: [
    { id: 'marks', label: 'Logo', type: 'records', layout: 'marks', title: 'The DFAM emblem', records: [
      { id: 'five-trees', title: 'Defined Forest Area Management', kind: 'program-identity',
        description: 'The rounded frame joins the lower curve of the D. One conifer shares its upright stroke and four smaller trees stand above FAM. The original appears on the same cover as the separate Forest Service emblem. The published artwork consists of raster strips. The supplied reconstruction provides editable paths.',
        image: { ...entry.cover, sourceId: 'sheet', sourcePage: 2, date: '2003-04', evidenceType: 'vector-reconstruction' },
        specimens: [{ file: 'initiatives/dfam/april-2003.png', alt: 'DFAM mark as printed in April 2003', caption: 'Published cover detail', sourceId: 'sheet', sourcePage: 2, evidenceType: 'printed-source-crop' }],
        links: [{label: 'Compare the drawing with the printed emblem', url: 'initiatives/dfam/comparison.png', note: 'Grey shows shared ink, rust the publication alone and blue the reconstruction alone. After aligning the foreground bounds, the two ink masks overlap by 92.3% of their union at a darkest-channel threshold of 160.'}],
        sourceRefs: [{sourceId: 'sheet', page: 2}] }
    ] },
    { id: 'history', label: 'History', type: 'timeline', title: 'The proposal and its implementation', records: [
      { id: 'proposal', date: 'April 2003', title: 'A proposed forest health program', description: 'The ministry outlined regional strategies, bark beetle detection and treatment, and annual reporting for licence holders and BC Timber Sales. The ministry would retain provincial oversight.', sourceRefs: [{sourceId: 'sheet', locator: 'Printed pages 1 and 7–8'}] },
      { id: 'act', date: 'October 2003', title: 'The legislature provides for joint responsibilities', description: 'Section 2 of the amendment act provided for new Forest Act sections 10.1–10.5. The legislative table lists those sections as awaiting commencement through November 17, 2026.', sourceRefs: [{sourceId: 'bill'}, {sourceId: 'table'}] },
      { id: 'arrow', date: 'March 2004', title: 'Voluntary work in the Arrow Timber Supply Area', description: 'The Arrow DFAM group prepared timber supply review data. The chief forester retained the allowable annual cut decision. The ministry subsequently reported that it had retained forest health responsibilities.', sourceRefs: [{sourceId: 'arrow'}, {sourceId: 'report'}] }
    ] },
    { id: 'sources', label: 'Sources', type: 'sources', title: 'Publications and legislation', records: sources }
  ]
})
