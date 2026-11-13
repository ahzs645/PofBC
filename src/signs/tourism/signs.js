// The welcome signs: their parts, where each sits in its drawing, and what the panel says. Data only,
// in the same format as the Forest Service's signs (see ../forest-service/signs.js).
//
// The Super, Natural sign is assembled from this site's own parts: the Spirit of BC flag the
// generator draws (src/assets/flagMark.js) and the Termes outlines the BC Hydro signatures are set
// in (src/hydro/serif.js). Its source package is artwork/signs/super-natural/.

import { SIGNS } from '../catalogue.js'

const DESTINATION_BC = {
  label: 'Destination BC, “Who we are”: the Super, Natural British Columbia brand and its stewards',
  href: 'https://destinationbc.ca/who-we-are/'
}

const BRAND_FAMILY = {
  label: 'Destination BC, 2025 brand launch toolkit: the Super, Natural British Columbia® brand family',
  href: 'https://www.destinationbc.ca/content/uploads/2025/09/2025-Brand-Launch-Toolkit-Rainforest-to-Rockies-v4.pdf'
}

const BC_BUSINESS = {
  label: 'BC Business, on the agency team behind Super, Natural British Columbia from 1979 to 1992',
  href: 'https://www.bcbusiness.ca/?p=45472'
}

const BEST_PLACE = {
  label: 'Global News, “B.C. no longer ‘best place on earth’ as slogan gets replaced”',
  href: 'https://globalnews.ca/news/163800/b-c-no-longer-best-place-on-earth-as-slogan-gets-replaced/'
}

const FLAG_LINKS = [
  {
    label: 'The flag identity',
    note: 'Logos · the generator’s Flag lockup: BC beside the same twelve shapes, with a ministry',
    to: { view: 'generator' }
  },
  {
    label: 'The flag, still flying in 2008',
    note: 'Logos · BC Transit: the provincial flag angled above the name on its service plans',
    to: { view: 'gallery', logos: 'bc-transit' }
  }
]

const TOURISM_LINKS = [
  {
    label: 'Ministry of Tourism, 1980',
    note: 'Government · the ministry in office through the flag’s first years',
    to: { view: 'government', year: 1984, node: 'ministry-of-tourism-1980' }
  },
  {
    label: 'Tourism British Columbia, 1997–2010',
    note: 'Government · the Crown corporation that marketed the brand',
    to: { view: 'government', year: 2005, node: 'tourism-bc' }
  }
]

export const SUPER_NATURAL = {
  id: 'super-natural',
  spotlight: { keep: ['panel'] },
  // The panel comes first so the parts drawn on it sit over it: clicking bare white opens the board.
// The three lines are found by their boxes, not their ink, so a click between thin serif letters
// still opens the line rather than the board behind it.
  regions: ['panel', 'stripes', 'flag', 'slogan', 'province', 'welcome'],
  parts: {
    overview: {
      label: 'Whole sign',
      box: SIGNS['super-natural'].view,
      pad: 0.05,
      panel: {
        eyebrow: 'Province of British Columbia · welcome sign',
        heading: 'Super, Natural British Columbia welcomes you',
        lede: 'A white roadside board: the Spirit of BC flag waving off its top right corner, its red and navy stripes running the width of the board, and the province’s tourism slogan set in three lines of navy serif beneath.',
        blocks: [
          'Two of the Province’s identities meet on one board. The flag is the government’s own logo of the 1980s and 1990s; the words are the tourism slogan that outlived it and is still in use. Everything here is rebuilt from parts this site already draws, so the sign can be taken apart the same way.',
          { facts: [
            ['Wording', 'Super, Natural / British Columbia / welcomes you'],
            ['Mark', 'the Spirit of BC flag, the Province’s logo from about 1983'],
            ['Date', 'not established; the flag dates it to roughly 1983–2001'],
            ['Rebuilt from', 'one photograph, 364 × 161 pixels'],
            ['Drawing', '1200 × 1150 units: 12 flag shapes, 3 stripes, 39 letters, all outlined']
          ] },
          { palette: [
            { name: 'Navy', value: '#013366' },
            { name: 'Red', value: '#AD0000' },
            { name: 'Gold', value: '#FCBA19' },
            { name: 'Board', value: '#FFFFFF' }
          ] },
          { note: 'This is a reconstruction, not an original master. The photograph does not settle the sign’s typeface, the exact cut of the board, its size, or its paint: the colours are the navy, red and gold the flag artwork was supplied in, not a sign specification, and the lettering is a stand-in serif fitted to the photograph. No part of it was traced.' },
          { h: 'Where the parts come from' },
          { links: [...FLAG_LINKS, {
            label: 'Another sign',
            note: 'Signs · British Columbia Forest Service, LOOKOUT',
            to: { view: 'signs', sign: 'lookout' }
          }] }
        ]
      }
    },
    flag: {
      label: 'Spirit of BC flag',
      hint: 'off the top corner',
      box: { x: 705, y: 8, w: 485, h: 375 },
      pad: 0.12,
      layer: '#existing-spirit-of-bc-flag',
      hit: 'shape',
      panel: {
        eyebrow: 'The mark',
        heading: 'The Spirit of BC flag',
        em: 'twelve shapes, unchanged',
        lede: 'The provincial flag drawn waving: the Union flag over a setting sun, with the waves below it streaming out into stripes. Around 1983 it became the government’s main logo, and it stayed through two changes of government.',
        blocks: [
          'These are the same twelve paths the generator’s Flag lockup draws, not a redrawing: one uniform scale and one move put them on the board, and a check confirms every path string and fill is identical to the site’s own.',
          'The flag has no white of its own. Its white is whatever it sits on, which on paper is the page and here is the board. The flag waves up above the board’s top edge, so the board is cut along the flag’s upper outline to keep that white behind it.',
          { facts: [
            ['Shapes', '12, in navy, red and gold'],
            ['Placed at', 'half the source size, top right'],
            ['In use', 'about 1983 to 2001, as this site dates it']
          ] },
          { h: 'A dating aside' },
          'Every ministry named across the flag documents this site was built from existed at the same time in only one year: 1986, Expo year, which is what the flag was made for. The sign is undated, but the flag on it narrows it to the same era.',
          { links: FLAG_LINKS }
        ]
      }
    },
    stripes: {
      label: 'Three stripes',
      hint: 'red and navy, across the top',
      box: { x: 36, y: 194, w: 704, h: 186 },
      pad: 0.1,
      layer: '#geometric-stripe-extensions',
      hit: 'shape',
      panel: {
        eyebrow: 'The header',
        heading: 'Three stripes',
        em: 'the flag’s waves, run out straight',
        lede: 'A red band over two navy bands, running from the flag’s trailing edge to the left of the board, so the flag seems to stream across the whole sign.',
        blocks: [
          'The stripes are the only new geometry on the board: three straight bands, each ending on the vertices of the flag’s own left edge. They overlap the flag by a few units so no hairline of white shows at the join, and the flag itself is not reshaped.',
          'The device gives a symbol drawn for letterheads the width of a highway sign without stretching it: the mark stays its own size in the corner, and the stripes carry it.',
          { facts: [
            ['Bands', 'red #AD0000, then navy #013366 twice'],
            ['Run', 'from 40 units in from the left edge to the flag'],
            ['Construction', 'straight-sided, ending on the flag’s own vertices']
          ] }
        ]
      }
    },
    slogan: {
      label: 'Super, Natural',
      hint: 'the slogan, with its comma',
      box: { x: 95, y: 470, w: 1000, h: 212 },
      pad: 0.1,
      layer: '#super-natural',
      panel: {
        eyebrow: 'The slogan',
        heading: 'Super, Natural',
        em: 'one comma, two meanings',
        lede: 'The comma is the joke. Without it the line reads “supernatural”; with it, “super” and “natural” are two separate claims about the province, and the line still sounds like the one word.',
        blocks: [
          'The slogan comes from the Province’s tourism advertising, which was running it by the late 1970s. The second and longest-serving agency team carried the campaign from 1979 to 1992, and its creative director has said that when it started, all it had was the slogan and some photographs.',
          'It has outlasted most of what stood beside it. Tourism British Columbia, a Crown corporation, marketed it from 1997 to 2010; the government’s own “Best Place on Earth” line came and went in the meantime; and Destination BC still runs Super, Natural British Columbia as the province’s tourism brand, relaunched as a family of regional brands in 2025.',
          { facts: [
            ['Line width', '990 of the board’s 1200 units'],
            ['Comma', 'its tail shortened to 0.7 to match the photograph'],
            ['p', 'its descender shortened to half']
          ] },
          { h: 'Who carried it' },
          { links: TOURISM_LINKS },
          { sources: [BC_BUSINESS, DESTINATION_BC, BRAND_FAMILY, BEST_PLACE] }
        ]
      }
    },
    province: {
      label: 'British Columbia',
      hint: 'the widest line',
      box: { x: 40, y: 682, w: 1120, h: 190 },
      pad: 0.1,
      layer: '#british-columbia',
      panel: {
        eyebrow: 'The lettering',
        heading: 'British Columbia',
        em: 'a stand-in serif',
        lede: 'The name in full, nearly edge to edge. It sets the scale for the lines around it: each of the three is fitted to its own measured width, so the letters are condensed by different amounts.',
        blocks: [
          'The sign’s own typeface is not known. The letters here are TeX Gyre Termes, a free relative of Times, taken from the outlines this site already uses for the BC Hydro signatures, whose original serif was never recovered either. The real sign’s letters are heavier and narrower, so the outlines are squeezed to between 62 and 69 percent of their width and given a thin stroke of their own colour for weight.',
          'Every letter remains the committed glyph path. The weight, the condensing and the shortened descenders are all done by grouping, scaling and clipping around it, so the adjustment can be undone without redrawing anything.',
          { facts: [
            ['Typeface', 'TeX Gyre Termes Regular, a substitute'],
            ['Condensed to', '62% (this line), 69% and 66% (the others)'],
            ['Extra weight', 'a 16-unit stroke, in the font’s units'],
            ['Letters', '15 here; 39 on the board']
          ] },
          { links: [{
            label: 'The same serif on BC Hydro',
            note: 'Logos · BC Hydro: the signatures this substitute was first set for',
            to: { view: 'gallery', logos: 'bc-hydro' }
          }] }
        ]
      }
    },
    welcome: {
      label: 'welcomes you',
      hint: 'in lower case',
      box: { x: 165, y: 874, w: 870, h: 220 },
      pad: 0.1,
      layer: '#welcomes-you',
      panel: {
        eyebrow: 'The greeting',
        heading: 'welcomes you',
        em: 'all in lower case',
        lede: 'The last line drops the capitals, so the sign reads as one sentence: Super, Natural British Columbia welcomes you.',
        blocks: [
          'The three lines are set tight, with almost no space between them. On the photograph the descenders are short, so the reconstruction shortens them too: the y of “you” to two thirds and the p of “Super” to half, which keeps the tightly set lines from running into each other.',
          'The wording is the whole message, and it is short because a roadside sign is read once, in passing: three lines, one mark, no small print.',
          { facts: [
            ['Line width', '860 units, the narrowest of the three'],
            ['y', 'its descender shortened to 0.65'],
            ['Letters', '11']
          ] }
        ]
      }
    },
    panel: {
      label: 'Board',
      hint: 'the white face',
      box: { x: 0, y: 0, w: 1200, h: 1150 },
      pad: 0.04,
      layer: '#panel',
      hit: 'shape',
      panel: {
        eyebrow: 'The panel',
        heading: 'The board',
        lede: 'A plain white rectangle with the flag breaking out above its top edge, cut along the flag’s outline so the waving mark stands clear of the sky.',
        blocks: [
          'In the photograph the board stands on two white posts at the roadside, against pale sky and dark forest. The raised edge behind the flag is the least certain part of the reconstruction: the sky behind it is nearly as pale as the paint, so the backing here follows the flag’s own silhouette with a small white allowance rather than a traced edge.',
          { facts: [
            ['Face', '1200 × 960 units, from 190 units down'],
            ['Backing', 'the flag’s upper outline, with a white margin'],
            ['Size', 'not inferred; the units are construction units']
          ] },
          { note: 'The reference photograph, a scaled comparison and an overlay of the vector on the photograph were supplied with the drawing and are described in its source package (artwork/signs/super-natural). The photograph is not kept on the site.' }
        ]
      }
    }
  },
  order: ['overview', 'flag', 'stripes', 'slogan', 'province', 'welcome', 'panel']
}

export const TOURISM_SIGNS = { 'super-natural': SUPER_NATURAL }
