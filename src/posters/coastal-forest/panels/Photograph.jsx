import { Facts, Item, Reveal } from '../../ui/Reveal.jsx'
import creditDetail from '../credit_detail.png'

export function Photograph() {
  return (
    <Reveal>
      <Item as="p" className="pv-eyebrow">Part 1 of 5 · The photograph</Item>
      <Item as="h2">Light through a coastal stand</Item>
      <Item as="p" className="pv-lede">Mist, backlit conifers and a low sun. The copy beneath describes this forest: Douglas fir, Sitka spruce, western hemlock and western red cedar, in stands averaging sixty metres tall.</Item>
      <Item as="p">This is the one part of the poster that is still a picture rather than a drawing. The supplied image was embedded unaltered, then clipped slightly at the bottom to fit the original photo window. Nothing was resampled, sharpened or generated.</Item>
      <Facts rows={[
        ['Source image', '1122 × 1402 pixels'],
        ['Window', '2085 × 2459 units, rounded corners, thin cream keyline'],
        ['At 24 × 36 in', 'about 54 pixels per inch'],
        ['Credit', 'PHOTO: ALAN McONIE/IMAGE FINDERS']
      ]} />
      <Item as="h3">The credit line</Item>
      <Item as="p">For a long time this was the one line the reconstruction left blank: in the photograph of the framed print it reads as small type but not as words, and inventing a name was worse than omitting one. A close-up of that corner was supplied, and the line is now transcribed and reset as lettering of its own, right-aligned in the black margin under the picture.</Item>
      <Facts rows={[
        ['Set in', 'Bookman BT Roman, 13 units'],
        ['Anchored', 'right edge at x = 2232, baseline y = 2646'],
        ['In the drawing', 'its own layer, outlines in the master'],
        ['Standing', 'transcribed from the close-up, not verified authorship']
      ]} />
      <Item as="figure" className="pv-figure">
        <img src={creditDetail} alt="Enlarged crop of the poster below the photograph, showing the credit line in small capitals at the right" loading="lazy" />
        <figcaption>The credit as it now stands, enlarged from the vector master. On a 24 × 36 inch print its capitals stand about two and a half millimetres tall.</figcaption>
      </Item>
      <Item as="div" className="pv-note"><p>Reading a credit is not confirming it. The wording comes from one supplied close-up of one printed copy, so it identifies the line on the poster rather than establishing who took the photograph. It also belongs to this image: substituting another photograph means changing the credit with it.</p></Item>
    </Reveal>
  )
}
