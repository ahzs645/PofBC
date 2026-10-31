// How the collecting shelf's list is read out of the government atlas (scripts/build-collecting.mjs).

export const COLLECTED_KINDS = ['crown-corporation', 'health-authority']

const yearOf = (value) => (value ? Number(String(value).slice(0, 4)) : null)

/**
 * Today's bodies and the atlas's history, as one list: a body in both is today's, and so is one the
 * history leaves open. A former body whose end no source traces keeps a null `to` with `untraced`,
 * so it is never shown as standing today.
 */
export const collectingFrom = (current, history) => {
  const byId = new Map()
  for (const body of history) {
    if (!COLLECTED_KINDS.includes(body.kind) || !body.name) continue
    // No end and none untraced is a body that stands today, as the atlas draws it.
    const untraced = !body.ended && (body.endStatus === 'untraced' || body.endStatus === 'occurred_date_unknown')
    byId.set(body.id, {
      id: body.id, name: body.name, ...(body.shortName ? { shortName: body.shortName } : {}), kind: body.kind,
      from: yearOf(body.established), to: yearOf(body.ended), current: !body.ended && !untraced,
      ...(untraced ? { untraced: true } : {})
    })
  }
  for (const body of current) {
    if (!COLLECTED_KINDS.includes(body.kind)) continue
    const held = byId.get(body.id)
    byId.set(body.id, {
      id: body.id, name: body.name, ...(body.shortName ? { shortName: body.shortName } : {}), kind: body.kind,
      from: yearOf(body.established) ?? held?.from ?? null, to: null, current: true
    })
  }
  return [...byId.values()].sort((a, b) => Number(b.current) - Number(a.current) || a.kind.localeCompare(b.kind) || (a.from ?? 9999) - (b.from ?? 9999) || a.name.localeCompare(b.name))
}
