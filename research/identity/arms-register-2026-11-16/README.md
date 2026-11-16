# British Columbia public bodies in the Canadian Heraldic Authority register

**108 registrations, retrieved 16 November 2026.** This is the data behind the Coats of Arms view
(`?view=arms`). [`register.json`](register.json) holds one record per register entry.

| Group | Entries |
| --- | --- |
| Crown | 2: the Province (1990 registration of the 1906 and 1987 College of Arms grants) and the Lieutenant Governor’s flag of office |
| Universities and colleges | 19 |
| Public bodies | 14: the B.C. Sheriff Service, the Conservation Officer Service, Metro Vancouver Transit Police, ten municipal police services, and Engineers and Geoscientists B.C. |
| Municipalities and regional districts | 73, including historic and merged municipalities and the Union of B.C. Municipalities |

## Method

The register’s search and listing pages sit behind a JavaScript challenge, but each entry’s own page
(`https://www.gg.ca/en/heraldry/public-register/project/<id>`) loads normally. Every project ID from 1
to 3960 was fetched; IDs above 3857 were empty. Entries were kept where the location is British
Columbia and the recipient type is “Civil Institution”. Private bodies, schools, churches, clubs,
companies and First Nations governments were left out.

The entries for the Crown, universities and public bodies carry the register’s wording: what was
granted or registered, the date, volume and page, motto, blazon and symbolism for each element, the
Canada Gazette notice, creator and painter, and the register notes. They also carry a short
plain-English description, a motto translation with its source, links to earlier entries for bodies
that were renamed, and a `note` for anything uncertain. Municipal entries carry the name, date, volume,
what is registered, the motto and the register notes.

Three entries were checked by hand against the live register (the Lieutenant Governor, UBC and
Penticton) and matched.

## Not in the register

These have no entry: the Legislative Assembly, the Speaker or Mace, the Great Seal of B.C., the B.C.
courts, BC Hydro, ICBC, BC Ferries, WorkSafeBC, the Law Society of B.C., the Royal BC Museum, the
B.C. Archives, BC Ambulance, B.C. Corrections, the health authorities, TransLink itself, RCMP “E”
Division, Camosun, Douglas, Selkirk, North Island, Northern Lights and Coast Mountain colleges, the
Nicola Valley Institute of Technology and Vancouver Community College.

## Open points

- **UBC**’s arms were recorded at the College of Arms on 23 September 1915 and registered in Canada in
  2015. Its 2015 coat-of-arms policy (in `sources`) gives the history.
- **Simon Fraser University** has two entries on the same day in 2007. One registers its 1965 Lyon
  Court arms with one book; the other is a new grant with three books, one for each campus.
- **Royal Roads**: the register gives two mottoes, “HUĆIST TŦE S,HELI ŁTE” and “LIVING OUR LEARNING”.
  The university’s own page could not be read to confirm the language’s name. A 2014 convocation
  programme gives the grant year as 1997; the register gives 24 March 1998.
- **Okanagan College**: the register translates the motto only into French. The English translation in
  the record is ours and is marked as such.
- **UVic**: the register has no symbolism and no earlier College of Arms date. The motto translation
  is from uvic.ca.
- **Excluded but in the register under B.C.**: the Maritime Museum of B.C., the B.C. Medical and
  Pharmacy associations, the Association of Municipal Chiefs of Police, the B.C. Law Enforcement
  Memorial Foundation, the First Nations Tax Commission, the Nisga’a Nation, the Kamloops Indian Band,
  and the Franco-Columbian flag (project 3092).

## Images

The artwork shown in the view comes from the 16 November 2026 arms acquisition,
[`../arms-acquisition-2026-11-16`](../arms-acquisition-2026-11-16/README.md): 422 renderings for every
holder here (all but the Town of Kinnaird have a picture), including the Simon Fraser, UNBC, Royal
Roads and Vancouver Island University Commons files this folder could not download earlier. Each is
credited on its page with its artist, licence and source.

Three Wikimedia Commons files stay in `src/arms/images/`: the Lieutenant Governor's flag (public
domain), which still leads that page, and UBC's and UVic's shields (public domain; Robin S. Taylor,
CC BY-SA 4.0), shown with the acquired artwork. Their licences and authors were read from each Commons
file page and confirmed through the Commons API ([`commons-images.json`](commons-images.json)). The
Sheriff Service's Commons file was not used, because its "own work" claim is doubtful.
