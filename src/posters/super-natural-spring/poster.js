const overview = { x: 0, y: 0, w: 1462, h: 1021 }

const sources = [
  {
    label: 'ADCC archive: 1985 Gold, Consumer Magazine Ad, and full creative credits',
    href: 'https://theadcc.ca/archive/so-many-of-our-visitors_1985_gold_consumer-magazine-ad'
  },
  {
    label: 'BCBusiness, 2 August 2018: the 1984 ad and its creative team',
    href: 'https://bcbusiness.ca/lifestyle/tourism/the-bcbusiness-2018-tourism-status-report-branding/'
  },
  {
    label: 'Concordia University, 3 December 2021: Alvin Wasserman and the campaign',
    href: 'https://www.concordia.ca/cunews/offices/advancement/2021/12/02/-concordia-very-formative--in-lives-of-ad-agency-founder-and-chi.html'
  }
]

export const SPRING_POSTER = {
  spotlight: { keep: ['spring-paper'] },
  order: ['overview', 'photograph', 'headline', 'copy', 'wordmark'],
  regions: ['photograph', 'headline', 'copy', 'wordmark'],
  parts: {
    overview: {
      label: 'Whole advertisement', box: overview,
      story: ['Three orcas surface against a mountain coast. The line below makes their return the invitation: British Columbia is a place worth coming back to.'],
      panel: {
        eyebrow: 'Super, Natural British Columbia · 1984',
        heading: 'So many of our visitors return in Spring.',
        lede: 'A 1984 tourism advertisement by McKim Advertising Vancouver, written by Alvin Wasserman, designed by Bill Cozens and photographed by Peter Thomas.',
        blocks: [
          { facts: [
            ['Date', '1984, identified in BCBusiness’s account with the creative team'],
            ['Award', 'ADCC Gold, Consumer Magazine Ad, 1985'],
            ['Client', 'Tourism B.C., as credited by ADCC'],
            ['Writing and creative direction', 'Alvin Wasserman'],
            ['Design and art direction', 'Bill Cozens'],
            ['Original photograph', 'Peter Thomas'],
            ['Agency', 'McKim Advertising Vancouver'],
            ['Reconstruction', 'Supplied scene images and outlined lettering; one tiny reply-code fragment retained from the reference'],
            ['Export size', '14.62 × 10.21 inches; a working size based on the uploaded crop, not the original page dimensions']
          ] },
          { note: 'The two scene choices are modern supplied recreations. The Original and Overlay controls retain the uploaded historical reference crop for comparison. The exact original font has not been verified. The complete headline is restored inside the page instead of reproducing the scan’s clipped endpoints.' },
          { sources }
        ]
      }
    },
    photograph: {
      label: 'The whale scene', hint: 'Orcas, water and a mountain coast',
      layer: '#spring-photo-vintage, #spring-photo-gemini',
      box: { x: 0, y: 113, w: 1462, h: 908 },
      story: ['The mountains fill the horizon, while three dorsal fins interrupt the water in front. The animals give the headline its second meaning: these visitors also return.'],
      panel: {
        eyebrow: 'The photograph', heading: 'Returning visitors',
        lede: 'The reconstruction uses the supplied clean whale scenes, fitted beneath the narrow white copy strip in the larger uploaded reference.',
        blocks: [
          { facts: [
            ['Primary scene', 'Vintage Orcas in British Columbia Waters.png, 1635 × 962 pixels'],
            ['Alternate scene', 'Gemini_Generated_Image_6ia0526ia0526ia0.jpeg, 2516 × 1696 pixels'],
            ['Original photograph', 'Peter Thomas, credited in the ADCC award archive']
          ] },
          { note: 'Both clean scenes differ from the historical reference in image detail. Peter Thomas’s credit applies to the original advertisement photograph; the supplied scenes are modern recreation material.' },
          { sources: [sources[0]] }
        ]
      }
    },
    headline: {
      label: 'The headline', hint: 'The invitation across the water',
      layer: '#spring-headline', hit: 'letters',
      box: { x: 10, y: 875, w: 1442, h: 124 },
      story: ['“So many of our visitors return in Spring.” runs almost edge to edge in white. Its large, closely spaced serif letters join the whales and the tourism invitation in one sentence.'],
      panel: {
        eyebrow: 'The headline', heading: 'A reason to return',
        lede: 'The words use the project’s existing TeX Gyre Termes Regular outlines, with size, proportions and optical spacing fitted to the supplied reference.',
        blocks: [
          { facts: [
            ['Reconstruction font', 'TeX Gyre Termes Regular'],
            ['Lettering', 'Native glyph outlines with fitted proportions and spacing'],
            ['Historical typeface', 'Unconfirmed; the published credits do not identify it']
          ] },
          'The narrow Times-family treatment is a visual reconstruction choice. The headline, main body copy and campaign signature remain vector outlines, without a runtime font dependency.',
          { note: 'The font fit does not establish which typeface or typesetting equipment was used for the 1984 advertisement.' }
        ]
      }
    },
    copy: {
      label: 'The small copy', hint: 'Two columns above the photograph',
      layer: '#spring-copy',
      box: { x: 8, y: 14, w: 1446, h: 92 },
      story: ['The small copy moves from the whales to the human visitor: scenery, spring activities and an invitation to ask for travel information. It is set apart from the photograph in a white strip.'],
      panel: {
        eyebrow: 'The copy strip', heading: 'An invitation in two columns',
        lede: 'The compact text is re-typeset in TeX Gyre Termes Regular, with darker copy, the reference’s two-column arrangement and its narrow white header.',
        blocks: [
          'The tiny reply code immediately after “Dept.” could not be read confidently. That short fragment is retained from the original raster reference instead of supplying a guessed code. The surrounding text is outlined.',
          'The larger uploaded crop guides the layout and wording, with the lower-resolution full reference used to check clipped right-hand content. The minister credit belongs beneath the address in the right column. Read the Original view alongside the reconstruction when assessing fine letterforms and punctuation.'
        ]
      }
    },
    wordmark: {
      label: 'The campaign signature', hint: 'Super, Natural British Columbia',
      layer: '#spring-wordmark',
      box: { x: 1058, y: 77, w: 390, h: 31 },
      story: ['Super, Natural British Columbia closes the copy strip at the right. Its understated serif signature leaves the scene and the sentence to carry the advertisement.'],
      panel: {
        eyebrow: 'The campaign', heading: 'Super, Natural British Columbia',
        lede: 'The signature is reconstructed in the treatment visible on this advertisement. It remains distinct from the later tourism marks held elsewhere in the collection.',
        blocks: [
          { links: [
            { label: 'Our good ferries', note: 'The island-crossing advertisement in the same ADCC campaign', to: { view: 'posters', poster: 'super-natural-ferries' } },
            { label: 'Take away our great hotels', note: 'The lake advertisement in the same ADCC campaign', to: { view: 'posters', poster: 'super-natural-lake' } },
            { label: 'Tourism BC & Destination BC', note: 'The tourism identity collection and its later documented marks', to: { view: 'gallery', logos: 'tourism-bc-destination-bc' } },
            { label: 'Super, Natural welcome sign', note: 'A related use of the tourism phrase', to: { view: 'signs', sign: 'super-natural' } }
          ] },
          { sources }
        ]
      }
    }
  }
}
