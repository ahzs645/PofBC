// The plates' timeline arithmetic, apart from React so Node's test runner can check it
// (plates.test.js). A design's `period` is PlateForge's [first, last] year, inclusive: the years it
// was issued or valid.

/** The years every design together spans: the axis both timelines share. */
export const spanOf = (formats) => [
  Math.min(...formats.map((format) => format.period[0])),
  Math.max(...formats.map((format) => format.period[1]))
]

/** Whether a design was issued or valid in `year`. */
export const inUse = (format, year) => format.period[0] <= year && year <= format.period[1]

/** The designs packed into as few lanes as never overlap, oldest first. */
export const lanesOf = (formats) => {
  const lanes = []
  for (const format of [...formats].sort((a, b) => a.period[0] - b.period[0] || a.period[1] - b.period[1])) {
    const lane = lanes.find((candidate) => candidate.end < format.period[0])
    if (lane) { lane.formats.push(format); lane.end = format.period[1] } else lanes.push({ formats: [format], end: format.period[1] })
  }
  return lanes.map((lane) => lane.formats)
}

/** The years worth stopping at: a design began, or the year after one ended. */
export const changeYears = (formats, [first, last]) => [...new Set(formats.flatMap((format) => [format.period[0], format.period[1] + 1]))]
  .filter((year) => year >= first && year <= last)
  .sort((a, b) => a - b)
