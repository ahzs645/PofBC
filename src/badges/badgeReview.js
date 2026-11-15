// A photograph may be offered for visual comparison only when the catalogue records its
// provenance and native crop dimensions. The artwork hash is checked separately in the UI.
export function badgeReviewSources (patch, review) {
  if (review?.id !== patch.id || !Array.isArray(review?.sources)) return []
  const hash = /^[a-f0-9]{64}$/i
  return review.sources.filter((source) => source &&
    typeof source.occurrenceId === 'string' && source.occurrenceId.trim() &&
    typeof source.cropUrl === 'string' && source.cropUrl.trim() &&
    typeof source.url === 'string' && /^https?:\/\//.test(source.url) &&
    Number.isFinite(source.width) && source.width > 0 &&
    Number.isFinite(source.height) && source.height > 0 &&
    hash.test(source.sourceFileSha256 ?? '') && hash.test(source.cropSha256 ?? ''))
}

export const badgeReviewAssetUrl = (path, base) => !path ? null
  : /^https?:\/\//.test(path) ? path : `${base}${path.replace(/^\/+/, '')}`
