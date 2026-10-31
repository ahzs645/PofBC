// A long explanation read a step at a time (storySteps.js): one short run of sentences on screen,
// arrows and dots to move through the rest, as a poster's story moves through its parts. A passage
// short enough to read as it is stays a plain paragraph.
//
// Every step is laid in the same grid cell, so the box is as tall as the longest and does not jump
// as the steps change; the ones not showing are hidden from sight and from screen readers.

import { useState } from 'react'
import { storySteps } from './storySteps.js'

export const StoryText = ({ text, label = 'Note', className = '', lead = null }) => {
  const steps = storySteps(text)
  const [state, setState] = useState({ text, step: 0 })
  // A new passage starts at its first step.
  const step = state.text === text ? Math.min(state.step, steps.length - 1) : 0
  const go = (next) => setState({ text, step: Math.max(0, Math.min(steps.length - 1, next)) })

  if (!steps.length) return null
  if (steps.length === 1) return <span className={`gov-story gov-story--plain ${className}`}>{lead}{steps[0]}</span>

  return (
    <span className={`gov-story ${className}`} role="group" aria-roledescription="story" aria-label={`${label}, ${steps.length} steps`}>
      <span className="gov-story__steps" aria-live="polite">
        {steps.map((passage, index) => (
          <span key={index} className="gov-story__step" data-shown={index === step || undefined} aria-hidden={index !== step || undefined}>
            {index === 0 && lead}{passage}
          </span>
        ))}
      </span>
      <span className="gov-story__nav">
        <button type="button" className="gov-story__arrow" disabled={step === 0} onClick={() => go(step - 1)} aria-label="Previous step">‹</button>
        <span className="gov-story__dots">
          {steps.map((_, index) => (
            <button key={index} type="button" className="gov-story__dot" aria-current={index === step || undefined} onClick={() => go(index)} aria-label={`Step ${index + 1} of ${steps.length}`} />
          ))}
        </span>
        <span className="gov-story__count" aria-hidden="true">{step + 1} / {steps.length}</span>
        <button type="button" className="gov-story__arrow" disabled={step === steps.length - 1} onClick={() => go(step + 1)} aria-label="Next step">›</button>
      </span>
    </span>
  )
}
