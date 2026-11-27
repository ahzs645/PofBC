import { COLLECTED_SPECIMENS } from '../gallery/collectedData.js'
import { TIMELINES } from '../gallery/timelines.js'

export const pacificGatewayDetail = (entry) => {
  const { eras } = TIMELINES[entry.id]
  const { assets } = COLLECTED_SPECIMENS.find(({ program }) => program === entry.id)
  const sources = [...new Map(eras.flatMap(({ sources }) => sources)
    .map((source) => [source.url, { ...source, id: source.url }])).values()]

  return {
    id: entry.id, title: entry.title, sources,
    hero: { title: entry.title, eyebrow: entry.subtitle, description: entry.summary },
    relatedLinks: [
      { label: 'The earlier Pacific Gateway lockup', to: { view: 'gallery', logos: 'bc-mark', mark: 'pacific-gateway' } }
    ],
    sections: [
      {
        id: 'marks', label: 'Logos', type: 'records', layout: 'marks', title: 'Canada Starts Here',
        records: assets.map((asset) => ({
          id: asset.id,
          title: asset.id === 'vector-canada-starts-here-2012' ? 'Canada Starts Here' : 'Canada Starts Here with the BC Jobs Plan',
          kind: 'campaign-identity',
          description: 'The BC Jobs Plan printed this flat version of the shipping-container design in September 2012.',
          image: {
            file: asset.file, displayId: asset.id, alt: asset.label,
            evidenceType: asset.evidenceType, sourceId: asset.sourceUrl, sourcePage: 24, date: asset.sourceDate, dateLabel: 'Publication date'
          }
        }))
      },
      {
        id: 'timeline', label: 'Timeline', type: 'timeline', title: 'From Pacific Gateway to Canada Starts Here',
        records: eras.map((era) => ({
          id: era.id, title: era.label, date: era.years, description: era.note,
          sourceRefs: era.sources.map(({ url, locator }) => ({ sourceId: url, locator }))
        }))
      },
      { id: 'sources', label: 'Sources', type: 'sources', records: sources }
    ]
  }
}
