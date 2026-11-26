# Entering British Columbia lettering editions

The five plates use the shapes, colours and proportions illustrated in the B.C. Ministry of
Transportation and Highways’ [September 2000 sign manual, printed page 6.12 (PDF page 162)][manual].
Each pair of SVGs retains the source panel, pictogram and tourism wordmark paths and sets the sign's
other lettering anew. The speed panel borders are also kept from the manual.

| Sign | Lettering | Basis |
| --- | --- | --- |
| I-180, square | [Lobster Regular][lobster] | Closest of four script candidates compared by overlap at the sign’s text bounds. The original script face is unidentified. The uppercase forms differ visibly. |
| I-180X and I-180B | Times New Roman Bold Italic | Named as `/TimesNewRoman,BoldItalic` in the PDF page resources. The greeting records use 9.8151 and 13.3566 pt respectively, with their original horizontal scale and letter origins. |
| I-181, seat belts | Arial Narrow Bold | Approximation of the condensed four-line legend. Each line is fitted to the source ink with its own spacing. |
| I-182, Thinkmetric | [Overpass][overpass] 800 and 900, Arial Bold | Overpass best matched the title and speed numerals in a comparison of condensed, grotesque and highway-inspired font candidates. Arial Bold is used for the units. The original faces are unidentified. |

The outlined SVGs are self-contained and keep each typeset glyph as a vector path. The editable
SVGs retain live text. Install the indicated fonts before opening an editable file. The two Times
greetings use per-character x positions to retain the PDF’s spacing. The outlined editions use the
manual’s artwork dimensions rather than scaling the illustrations to the posted sign dimensions.

Rebuild with Python, `fonttools` and `uharfbuzz`. Pass the pinned Google Fonts files below and a
directory holding the installed Microsoft TTFs. On macOS that directory defaults to
`/System/Library/Fonts/Supplemental`.

```sh
uv run --with fonttools --with uharfbuzz artwork/signs/entering-bc/build_type.py \
  --lobster /path/to/Lobster-Regular.ttf --overpass '/path/to/Overpass[wght].ttf'
```

- [Lobster Regular TTF][lobster-font], SHA-256 `d6568e697fd50cedc0be04d8aae4127fe95add607e7bff954ca88604be80c205`.
- [Overpass variable TTF][overpass-font], SHA-256 `970717df17a7f9911dee45f60695d05bfa9d745fa0a11fc5c348371fa21f0073`.

[manual]: https://www2.gov.bc.ca/assets/gov/driving-and-transportation/transportation-infrastructure/engineering-standards-and-guidelines/traffic-engineering-and-safety/traffic-engineering/traffic-signs-and-pavement-markings/manual_signs_pavement_marking.pdf#page=162
[lobster]: https://fonts.google.com/specimen/Lobster
[overpass]: https://fonts.google.com/specimen/Overpass
[lobster-font]: https://raw.githubusercontent.com/google/fonts/98f1d55df3f7718f16334ab6f4356421fe2b7576/ofl/lobster/Lobster-Regular.ttf
[overpass-font]: https://raw.githubusercontent.com/google/fonts/d8f31106ea0af85ee2f3a3d38a2fe155de0d716c/ofl/overpass/Overpass%5Bwght%5D.ttf
