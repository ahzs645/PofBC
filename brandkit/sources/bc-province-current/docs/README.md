# Province of British Columbia: the BC mark, 2011 to the present (reference kit)

**Not issued by the Government of British Columbia, and not a source of approved marks.** The
Province’s guidelines say its marks must be used exactly as provided: for official work, use the
Province’s own files.

The BC mark, the sun over mountains and sea, beside each ministry’s name: PofBC’s current era as a
brandkit brand.

- **`artwork/ministry-marks/`: every published ministry mark, exactly.** The mark is the drawing
  PofBC lifted unchanged from the Province’s ministry-marks PDF; each name is set in the alphabet
  recovered from the marks themselves (Adobe Garamond Pro, kerned and tracked −10/1000 em). Every
  ministry, in English and French, in the four colourways of the Province’s colour-accessibility
  guidance: Colour, Reverse, Solid black and Solid white. `index.json` lists them.
- **An editable ministry mark**, for names no published mark has shown: the mark, the gold divider
  and the name where PofBC’s layout puts them, the last line on the wordmark’s baseline. The
  Province’s serif is licensed, so the name is set in **EB Garamond**, an open revival that differs
  in its letterforms (see `fonts/eb-garamond/FONT-NOTICE.txt`). Line breaks follow PofBC’s rules
  for every listed ministry.
- **The colourways are the Province’s own.** Reverse lightens the mountains to BC Blue 60% and turns
  the type white; the solid colourways drop the white knockout behind the sun’s rays so the ground
  shows through, rather than ringing the mark in white. The editable mark leaves the knockout out
  in every colourway (brandkit paints a one-ink logo by giving every part the same colour, which
  would fill the rays in solid), so its Reverse shows the ground between the rays; the published
  `*-reverse.svg` files keep the white knockout, as the Province draws it.
- **Screen colours** are the guidance’s `#234075` (BC Blue) and `#e3a82b` (BC Gold); the PDF itself
  draws the marks in CMYK-native `#053673` and `#fdb913`.

Not included: BC Sans, the Province’s screen typeface, and the Best Place on Earth marks of
2005–2011, which PofBC keeps in its gallery.

Rebuild with `npm run brandkit:build -- bc-province-current` in PofBC.
