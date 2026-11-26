export const bearAwareId = 'bear-aware-1997'
export const bearAwareTitle = 'Revelstoke Bear Awareness Program'
export const bearAwareFolder = 'initiatives/bear-aware-1997/'
export const bearAwareReport = 'https://a100.gov.bc.ca/pub/acat/documents/r40226/Rev_Bear_Aware_1997_1385746991273_5746493974.pdf'
export const bearAwareArchive = 'https://a100.gov.bc.ca/pub/acat/public/viewReport.do?reportId=40226'

export const bearAwareWindowId = 'we-are-bear-aware-window-sign'
export const bearAwareWindowTitle = 'We Are Bear Aware'
export const bearAwareWindowView = { x: 0, y: 0, w: 764, h: 1000 }
export const bearAwareWindowMeta = {
  title: bearAwareWindowTitle,
  when: 'Documented in 1997 · vector reconstruction',
  format: 'Window sign', made: 'vector',
  view: bearAwareWindowView,
  page: { w: 7.64, h: 10 }
}

export const bearAwareWindowSvg = bearAwareFolder + 'svg/01-we-are-bear-aware-window-sign.svg'
export const bearAwareWindowScan = bearAwareFolder + 'scans/01-we-are-bear-aware-window-sign.png'
export const bearAwareMarkId = 'be-bear-aware-paw-lockup'
export const bearAwareGalleryId = 'specimens-bear-aware-1997'

export const bearAwareIndex = {
  id: bearAwareId, title: bearAwareTitle, subtitle: 'Revelstoke · 1997',
  summary: 'Revelstoke’s Bear Awareness Program used window signs, checklists and newspaper ads to help residents and businesses keep bear attractants off their properties.',
  cover: {
    file: bearAwareWindowScan,
    alt: 'We Are Bear Aware lettering and a five-clawed paw in a black oval, with sponsor logos below',
    caption: 'Original window-sign scan from the 1997 final report'
  },
  tags: ['Wildlife', 'Signs', 'Newspaper advertising'],
  searchTerms: ['Be Bear Aware', 'We Are Bear Aware', 'Times Review', 'Unique', 'Columbia Basin Fish & Wildlife Compensation Program'],
  exploreLabel: 'Explore the 1997 window sign, checklists and newspaper ads'
}
