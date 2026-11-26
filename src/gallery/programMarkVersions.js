// A program layout can have differently drawn reversals. Each choice selects its
// own published paths. A theme default applies until the reader picks a version.
const labels = {
  positive: 'Colour positive', reverse: 'Colour reverse', black: 'Solid black',
  'grey-positive': 'Greyscale positive', 'grey-reverse': 'Greyscale reverse',
  'blue-positive': 'Solid blue positive', white: 'Solid white', 'cmyk-positive': 'CMYK-labelled positive'
}

export function programMarkVersion(id, designId, treatment, darkVariant) {
  const darkBackground = ['reverse', 'grey-reverse', 'white'].includes(treatment)
  return {
    id, versionLabel: labels[treatment], darkBackground, sourceGround: darkBackground ? 'dark' : 'light',
    ...(id !== designId ? { variantOf: designId } : {}),
    ...(id === designId && darkVariant ? { darkVariant } : {})
  }
}
