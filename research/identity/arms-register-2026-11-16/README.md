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

Images shown in the view are copies of Wikimedia Commons files, in `src/arms/images/`, each credited
on its page with its author and licence: the Lieutenant Governor’s flag (public domain), UBC’s shield
(public domain) and UVic’s shield (Robin S. Taylor, CC BY-SA 4.0). Licences and authors were read
from each Commons file page and confirmed through the Commons API
([`commons-images.json`](commons-images.json)).

Four more Commons files were identified but not downloaded, because Wikimedia rate-limited the
download. Each needs a `src/arms/images/` file and an `image` entry in `src/arms/holders.js`:

| Holder | Commons file | Licence |
| --- | --- | --- |
| Simon Fraser University | `Simon_Fraser_University_Achievement.png` | CC BY-SA 4.0, Robin S. Taylor |
| University of Northern B.C. | `University_of_Northern_British_Columbia_Escutcheon.png` | CC BY-SA 4.0, Robin S. Taylor |
| Royal Roads University | `Royal_Roads_University_Escutcheon.png` | CC BY-SA 4.0, Robin S. Taylor |
| Vancouver Island University | `Coat_of_Arms_of_Vancouver_Island_University.png` | CC BY 4.0, SheLikesHeraldry | The Province’s arms are drawn from this repository’s own
vector (`src/assets/crestMark.js`). No Commons file was found for the other bodies. The Sheriff
Service’s Commons file was not used, because its “own work” claim is doubtful.
