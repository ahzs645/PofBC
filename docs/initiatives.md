# Initiatives

Initiatives connect websites, campaigns, visual identities, publications and their
sources across organizations. Each initiative has an index entry and a detail model
rendered by the shared initiative view. Tourism is the first documented initiative.
There are no placeholder entries for prospective subjects.

## Registry and lazy loading

[`src/initiatives/initiatives.js`](../src/initiatives/initiatives.js) exports:

- `INITIATIVES`: lightweight metadata for the index and search.
- `initiativeById(id)`: metadata for a stable ID, or `null` for an unknown ID.
- `loadInitiative(id)`: an asynchronous detail loader, also returning `null` for an
  unknown ID.

The metadata contains `id`, `title`, `subtitle`, `summary`, `cover`, `tags`,
`searchTerms` and `relatedBodyIds`. A cover has a local `file` path relative to
`public/`, meaningful `alt` text and a source-aware `caption`. Search terms are
curated names of actual records and brands; they are not a dump of every historical
address or email in an inventory.

Keep the registry independent of full source datasets. Each entry has a loader
with a literal dynamic import, so viewing the index does not load every
initiative's evidence. Tourism loads the existing generated
[`tourismData.js`](../src/gallery/tourismData.js) and adapts it to the shared model.
The adapter references the existing source, record, timeline, lead and inventory
arrays directly. It creates no duplicate or invented evidence records and makes
no editorial changes to the source data.

## Detail model

The loaded object contains these fields:

| Field | Purpose |
| --- | --- |
| `id`, `title` | Stable initiative identity and reader-facing title. |
| `hero` | `eyebrow`, `title`, `description`, `image` and `caption`. The image includes `file` and `alt`, and can retain its complete specimen provenance. A title may contain a newline. |
| `stats` | An array of `{ value, label }`, with values derived from the underlying records. |
| `sources` | The source registry resolved by each record's `sourceRefs`. |
| `domainNote` | Optional context for documented addresses, including what their dates establish. |
| `relatedLinks` | `{ label, to }` links using the site's `SiteLink` parameter objects. |
| `sections` | Ordered sections supported by the shared renderer. |

Each section has `id`, `label`, `type`, `eyebrow`, `title` and `description`.
Supported types are:

| Type | Content and options |
| --- | --- |
| `records` | `records` opens specimen details. Optional `searchable: true`, `featuredId`, `layout: 'marks'` and a plain-text `notice` control the presentation. |
| `timeline` | `records` contains events with their source-supported dates and date meanings. |
| `publications` | `records` contains documented publications or publication leads. Optional `leads` adds further research records. |
| `sources` | Uses the detail's source registry; `records` may reference that same array. An optional `inventory` adds a searchable, downloadable source inventory. |

An inventory contains `title`, `description`, `entries`, `sourceId`,
`downloadTitle`, `filename`, `dateLabel` and `matchingNote`. Tourism uses the
complete 2013 address transcription, including repeated entries and email
addresses. Its 193 listed entries are not 193 distinct or working websites.

Sections and inventories are optional. A future initiative with a documented
timeline and publications can supply those sections without empty website or
domain tabs. Only include a `featuredId` that identifies a real record in that
section, and only include statistics supported by the supplied data.

## Evidence and organizational identity

Records retain their existing `id`, `title`, `description`, `status`,
`statusLabel`, `sourceRefs`, `links` and relevant subject fields. Image specimens
retain source IDs and URLs, source-page locators, evidence types, checksums, image
dimensions, date meanings, captions and alternative text. Native vectors, original
publisher images and crops from printed sources remain distinguishable. The
renderer can show a documented record without an image; a name or a listed domain
does not justify invented artwork or a reconstructed screenshot.

Publication dates, screenshot capture dates, website launches, logo adoption dates
and corporate events are separate claims. Preserve their supplied precision and
uncertainty. A publication lead remains a lead until a specific issue or specimen
is held. Reader-facing descriptions explain what is documented and what is still
sought; implementation tasks belong in contributor notes.

An initiative can span several custodians without merging their legal histories.
Tourism links Tourism BC and Destination BC, keeps both government nodes and
artwork ownership intact, and does not add a legal rename to the gallery's
`CONTINUATIONS` list. Its Tourism BC government link selects 2009, when that body
was still active.

The [tourism research record](../research/identity/tourism-asset-transfer-2013/README.md)
documents the underlying catalogue, manifests, transcription and deterministic
build. Source corrections belong there and are regenerated into the existing
dataset; they should not be patched into the initiative adapter.

## Stable links

Use these routes:

- Index: `?view=initiatives`
- Initiative: `?view=initiatives&initiative=tourism`
- Section: `?view=initiatives&initiative=tourism&section=websites`
- Record: `?view=initiatives&initiative=tourism&section=websites&record=hellobc`

Initiative, section and record IDs are URL identifiers. Preserve them when changing
labels or copy. Related links use `SiteLink` objects such as
`{ view: 'government', node: 'tourism-bc', year: 2009 }`, allowing normal navigation,
copied links and opening in a new tab. Selection is resolved against the loaded
initiative; an unknown section or record should use the shared route model's
fallback instead of creating a placeholder record.

## Adding a real initiative

1. Gather and document the source material first. Keep its records, specimens and
   source registry in a dedicated dataset with reproducible provenance.
2. Add one lightweight metadata entry with a stable ID, a sourced cover when one
   is available, curated search terms and real related-body IDs.
3. Add a literal dynamic import to `LOADERS` and an adapter that returns the shared
   detail shape. Reference the existing dataset arrays instead of copying or
   rewriting their records.
4. Include only the section types supported by the available evidence. Extend the
   shared renderer for a genuinely new presentation requirement rather than
   copying a complete initiative-specific page.
5. Validate identifiers, source references, specimen paths, section selection and
   direct links. Check the index and detail at desktop and mobile widths, including
   any record dialog and optional inventory.

Do not add speculative initiatives to the live registry to demonstrate the
pattern. Development examples should remain inert documentation until their
records and sources are ready for readers.
