// The preview surface is independent of the site's theme and the exported artwork.
export const PreviewBackground = ({ white, onToggle, children }) => (
  <div className="gallery-preview" data-white={white || undefined}>
    <button type="button" className="gallery-preview__background" aria-label="White background" aria-pressed={white}
      onClick={onToggle} title={white ? 'Restore automatic preview background' : 'Use a white preview background'}>
      <span aria-hidden="true" />
    </button>
    {children}
  </div>
)
