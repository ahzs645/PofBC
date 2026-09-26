// What the historical BC Hydro identity manual says, transcribed.
//
// Five pages of a manual whose date, edition and page numbers are unknown: the corporate colours,
// the Gas Operations colours, the general background standards, the identification signs and the
// vehicle signatures, supplied as screenshots and not kept in this repository. Everything below is
// what they state, with each rule's source page named, and — kept apart from it — what they leave
// unsaid, so the view can say where a rule ends and a reconstruction begins.
//
// Not current BC Hydro brand guidance.

export const HYDRO_STANDARDS = {
  "schema": "bc-hydro-historical-standards/v2",
  "status": "Transcribed from five user-supplied historical manual screenshots. Date, edition, and original page numbers are not supplied. Not current BC Hydro brand guidance.",
  "sources": [
    {
      "title": "Corporate colours",
      "filename": "Screenshot 2026-09-24 at 2.23.48 PM.png",
      "key": "corporate-colours"
    },
    {
      "title": "Gas Operations colours",
      "filename": "Screenshot 2026-09-24 at 2.23.56 PM.png",
      "key": "gas-colours"
    },
    {
      "title": "General background standards",
      "filename": "Screenshot 2026-09-24 at 2.24.04 PM.png",
      "key": "general-backgrounds"
    },
    {
      "title": "Identification signs",
      "filename": "Screenshot 2026-09-24 at 2.25.30 PM.png",
      "key": "identification-signs"
    },
    {
      "title": "Vehicle signatures",
      "filename": "Screenshot 2026-09-24 at 2.25.42 PM.png",
      "key": "vehicle-signatures"
    }
  ],
  "colours": {
    "green": {
      "nonProcessSystem": "376",
      "processCoated": {
        "C": 50,
        "M": 0,
        "Y": 100,
        "K": 0
      },
      "processUncoated": {
        "C": 50,
        "M": 0,
        "Y": 100,
        "K": 0
      },
      "sourceLiteral": "100% yellow; 50% cyan",
      "source": "corporate-colours"
    },
    "blue": {
      "nonProcessSystem": "314",
      "processCoated": {
        "C": 90,
        "M": 20,
        "Y": 25,
        "K": 0
      },
      "processUncoated": {
        "C": 90,
        "M": 15,
        "Y": 25,
        "K": 0
      },
      "source": "corporate-colours"
    },
    "black": {
      "process": {
        "C": 0,
        "M": 0,
        "Y": 0,
        "K": 100
      },
      "sourceLiteral": "Standard 100% black",
      "source": "corporate-colours"
    },
    "interpretation": "CMYK tuples put the listed process percentages into C/M/Y/K order; unlisted components are entered as zero. The supplied page calls the other specification \"Non-process system\"; no system name or modern C/U suffix is added.",
    "screenPreview": {
      "green": "#00af00",
      "blue": "#0069a2",
      "black": "#000000",
      "basis": "Approximate median RGB values sampled from interior regions of the supplied corporate-colour screenshot; NOT colourimetric matches, print recipes, or authenticated digital brand values."
    },
    "productionCaution": "The manual asks suppliers to use separate fidelity swatches and says the small printed manual samples are inadequate for production testing. This app exports RGB SVG/PNG; metadata does not create CMYK separations or spot inks."
  },
  "identity": {
    "corporate": "In the multicolour signature, green and blue occur in the symbol only; the logotype is black.",
    "gas": "The asymmetric shape is the Gas Operations flame. Its central stylized H always matches the flame in colour and value. In the multicolour signature both are corporate blue; the logotype is black.",
    "singleColour": "The entire signature is one colour in positive/reverse versions. Reverse interiors are unprinted/transparent, not white-filled disks."
  },
  "generalBackgrounds": {
    "preferred": "Black signature on white.",
    "blackOnTint": {
      "backgroundValueMax": 20,
      "enlargement": "Enlarge compared with black on white; no numerical factor supplied."
    },
    "colouredInkAlternative": {
      "background": "white",
      "inkValueMin": 70,
      "condition": "Only where black is unavailable; the manual calls this the least desirable positive form."
    },
    "reversePreferred": {
      "foreground": "white",
      "background": "black",
      "enlargement": "Considerable enlargement; no numerical factor supplied."
    },
    "reverseMinimum": {
      "backgroundValueMin": 80,
      "enlargement": "Enlarge further relative to white on black; no numerical factor supplied."
    },
    "intermediateValues": "No general single-colour treatment is prescribed by these examples for background values 21–79. Do not substitute the vehicle rule.",
    "source": "general-backgrounds"
  },
  "vehicles": {
    "positiveBackgroundValue": [
      0,
      30
    ],
    "reverseBackgroundValue": [
      31,
      100
    ],
    "sameLogotypeHeightForGivenVehicleType": true,
    "source": "vehicle-signatures"
  },
  "identificationSigns": {
    "fullSignature": true,
    "facilityName": "Immediately below the signature.",
    "sideBorderCapHeights": 0.5,
    "standardTopBorderCapHeights": 0.5,
    "gasTopBorderCapHeights": 1,
    "bottomBorderCapHeights": 0.5,
    "signatureBaselineToNameTopXHeights": 1,
    "multiline": "No additional line spacing; descenders should just clear the following line.",
    "source": "identification-signs",
    "exampleNames": [
      "Huntingdon Freight Office",
      "Liquefied\nNatural Gas\nPlant"
    ],
    "implementation": "Border offsets use the signature cap top/baseline and the facility name last baseline, matching the example diagrams. Cap height and x-height are measured from the substitute serif; line clearance is 0.015 signature cap heights, an implementation choice, not a specified historical number."
  },
  "limitations": [
    "The historical \"value\" percentage is entered explicitly by the user; it is not inferred from a HEX colour, RGB luminance, or WCAG contrast.",
    "No absolute minimum size or exact enlargement factor appears on these pages.",
    "TeX Gyre Termes (the free derivative of Nimbus Roman, which the reconstruction was fitted against) remains a visual substitute; these pages do not identify the historical typeface.",
    "Vector shapes and optical wordmark adjustments remain reconstructions, not recovered production masters.",
    "Custom wording, screen colours, and geometric edits can depart from the historical examples."
  ]
}
