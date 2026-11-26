import './ui.css'

export const TabList = ({ idPrefix, label, tabs, selected, onChange }) => {
  const onKeyDown = (event) => {
    const index = tabs.findIndex(({ id }) => id === selected)
    const nextIndex = {
      ArrowRight: (index + 1) % tabs.length,
      ArrowLeft: (index + tabs.length - 1) % tabs.length,
      Home: 0,
      End: tabs.length - 1
    }[event.key]
    if (nextIndex === undefined) return
    event.preventDefault()
    onChange(tabs[nextIndex].id)
    event.currentTarget.querySelectorAll('[role="tab"]')[nextIndex]?.focus()
  }

  return (
    <div className="ui-tabs" role="tablist" aria-label={label} onKeyDown={onKeyDown}>
      {tabs.map(({ id, label: tabLabel }) => (
        <button key={id} type="button" role="tab" id={`${idPrefix}-tab-${id}`} aria-controls={`${idPrefix}-panel-${id}`}
          aria-selected={selected === id} tabIndex={selected === id ? 0 : -1} onClick={() => onChange(id)}>
          {tabLabel}
        </button>
      ))}
    </div>
  )
}
