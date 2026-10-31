// Long explanations as steps: a passage split at its sentences and packed into short runs, read one
// at a time (StoryText.jsx), the way a poster's story steps through its parts.
//
// Pure, so it can be tested without a browser.

// A full stop that ends one of these does not end the sentence: initials and abbreviations the
// notes use ("B.C.", "U.S.", "c. 53", "s. 351", "No. 4", "St. Paul").
const ABBREVIATION = /(?:\b(?:[A-Za-z]\.){2,}|\b(?:c|s|ss|cc|no|nos|st|mt|ft|dr|mr|mrs|ms|jr|sr|ltd|inc|co|corp|dept|govt|vol|pp|p|ch|art|sec|ed|eds|approx|ca|cf|vs|al|e\.g|i\.e|etc|jan|feb|mar|apr|aug|sept|sep|oct|nov|dec)\.)$/i

/** A passage's sentences, in order; a sentence is never cut at an abbreviation's full stop. */
export const sentencesOf = (text) => {
  const sentences = []
  let current = ''
  // A candidate break: a full stop, question or exclamation mark (and any closing quote or bracket)
  // followed by space and a capital, digit or opening quote.
  for (const piece of String(text).trim().split(/(?<=[.!?][’”"')\]]?)\s+(?=[A-Z0-9“‘"(])/)) {
    current = current ? `${current} ${piece}` : piece
    if (!ABBREVIATION.test(current)) {
      sentences.push(current)
      current = ''
    }
  }
  if (current) sentences.push(current)
  return sentences
}

/**
 * A passage as steps of whole sentences, each up to about `size` characters and as even as the
 * sentences allow, since every step takes the room of the longest; a sentence longer than `size` is
 * a step of its own. A passage no longer than `under` is one step: short enough to read as it is.
 */
export const storySteps = (text, { size = 220, under = 280 } = {}) => {
  const passage = String(text ?? '').trim()
  if (!passage) return []
  if (passage.length <= under) return [passage]
  // The length each step aims at: the passage shared evenly among as few steps as `size` allows.
  const target = passage.length / Math.ceil(passage.length / size)
  const steps = []
  for (const sentence of sentencesOf(passage)) {
    const last = steps.at(-1)
    const joined = last ? last.length + 1 + sentence.length : Infinity
    // A sentence joins the step before when that brings the step nearer the target than it was.
    if (joined <= size && Math.abs(joined - target) < Math.abs(last.length - target)) steps[steps.length - 1] = `${last} ${sentence}`
    else steps.push(sentence)
  }
  return steps
}
