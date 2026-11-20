"""Re-typeset historical applications with outlined type and vector components.
Uncertain microcopy and handwritten marks are not silently invented.
"""
from pathlib import Path
import json
from vector_utils import *

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'svg'
INK='#1D1D1B';PAPER='#F2ECD9';ROSE='#BD606A'
manifest=[]
def save(name,w,h,body,title,desc,sources,status='reconstructed-application',physical=None):
    (OUT/(name+'.svg')).write_text(svg_doc(w,h,body,title,desc,physical))
    manifest.append(dict(id=name,title=title,width=w,height=h,description=desc,
                         sources=sources,status=status,svg='svg/'+name+'.svg'))

def stationery_head():
    return rect(0,0,368,6,ROSE,'rose-top-band')+place_svg(OUT/'ius-print-vertical.svg',367,4,90,153,'vertical-letterhead-logo')

def center_line(t,y,h=7.4,font='mono',width=None,ident='line'):
    return text_paths(t,306,y,h,font=font,align='center',fill=INK,width=width,ident=ident)

def letterhead():
    save('ius-letterhead-template',612,792,stationery_head(),
         'Interior University Society - letterhead template',
         'Source-derived stationery template with vertical IUS mark and rose-red top rule. US Letter is a convenient output format, not a verified original paper size. Uncertain original small address block is omitted, leaving an editable blank area. Transparent page background.',
         ['IMG_7950.jpeg','IMG_7947.jpeg'],physical=('8.5in','11in'))

def invitation():
    body=rect(0,0,612,792,PAPER,'paper-stock')+stationery_head()
    lines=['YOU ARE CORDIALLY','INVITED TO','A','WINE & CHEESE PARTY','AT THE',
           'COAST INN OF THE NORTH','ON','JUNE 8, 1988','TO MEET',
           'DR. URBAN DAHLLOFF','OF UPPSALA, SWEDEN.']
    for i,t in enumerate(lines):body+=center_line(t,195+i*18,7.2,ident='invitation-line-'+str(i+1))
    for i,t in enumerate(['Dr. Dahlloff is the Senior Consultant','to the Feasibility Study for the','INTERIOR UNIVERSITY SOCIETY']):
        body+=center_line(t,423+i*21,7.4,ident='consultant-line-'+str(i+1))
    body+=center_line('Time:  4:00 p.m. to 6:00 p.m.',522,7.4,ident='event-time')
    body+=center_line('R.S.V.P.  562-6868',555,7.4,ident='historic-rsvp')
    save('ius-invitation-1988-retypeset',612,792,body,'IUS invitation - 8 June 1988 re-typeset study',
         'Re-typeset from the supplied photograph of the invitation dated June 8, 1988. The visible invitation body is reproduced in outlined substitute type. The photographed spelling DAHLLOFF / Dahlloff is retained. The uncertain small header address and handwritten oval around RSVP are omitted. This is a reconstructed study, not an original scan or exact facsimile. Contact details are historical.',
         ['IMG_7950.jpeg'],physical=('8.5in','11in'))

def fundraising():
    body=rect(0,0,612,792,PAPER,'paper-stock')+stationery_head()
    body+=center_line('What can you get for $100 ?',190,12,'serif-bold',ident='fundraising-question')
    for i,t in enumerate(['A UNIVERSITY FOR','PRINCE GEORGE','NOT KELOWNA']):
        body+=center_line(t,230+i*25,18,'serif-bold-italic',ident='fundraising-headline-'+str(i+1))
    body+=center_line('What will we do with your $100 ?',329,11,'serif-bold',ident='fundraising-subhead')
    for i,t in enumerate(['Your business cheque for $100 together with other businesses will help the',
                          'campaign to get a University for the Interior. The enclosed brochure sets out our',
                          'objectives, but we need your support now.']):
        body+=text_paths(t,62,368+i*13,7.6,font='serif',ident='business-letter-body-'+str(i+1))
    body+=center_line('WE NEED A UNIVERSITY',430,16,'serif-bold-italic',ident='we-need-a-university')
    body+=center_line('Send your business cheque to:',470,9,'serif',ident='send-cheque-line')
    for i,t in enumerate(['Interior University Society,','2666 Queensway Street','Prince George, B.C.,','V2L 1N2']):
        body+=center_line(t,500+i*15,9,'serif-bold' if i==0 else 'serif',ident='historic-address-'+str(i+1))
    body+=text_paths('Yours faithfully,',62,606,9,font='serif',ident='closing')
    body+=text_paths('INTERIOR UNIVERSITY SOCIETY',62,632,9,font='serif',ident='society-signoff')
    save('ius-fundraising-letter-retypeset',612,792,body,'IUS business fundraising letter - re-typeset study',
         'Source-derived re-typesetting of the visible $100 business appeal and address. Font audit v1.1 restores the italic display headlines with Nimbus Roman Bold Italic outlines; questions and body remain upright. Line breaks and exact typeface are reconstructed; obscured salutation and signature are omitted. Historical address and amounts are documentary content, not a current donation request. US Letter canvas is nominal.',
         ['IMG_7955(1).jpeg','IMG_7947.jpeg'],physical=('8.5in','11in'))
    h=''
    for i,t in enumerate(['A UNIVERSITY FOR','PRINCE GEORGE','NOT KELOWNA']):
        h+=text_paths(t,600,10+i*105,76,font='serif-bold-italic',align='center',ident='slogan-'+str(i+1))
    save('ius-university-for-prince-george',1200,310,h,'A university for Prince George - campaign headline',
         'Re-typeset campaign wording from the supplied fundraising letter. Font audit v1.1 restores the visibly italic display treatment using outlined Nimbus Roman Bold Italic; original font identity remains unconfirmed. This is a lettering component, not a separate verified historical logo.',
         ['IMG_7955(1).jpeg'],'component')

def cover():
    body=rect(0,0,420,890,PAPER,'paper-stock')
    body+=place_svg(OUT/'ius-print-colour.svg',138,28,266,157,'cover-logo')
    body+=place_svg(OUT/'ius-graduates-interpretive.svg',22,235,376,491,'cover-graduates')
    body+=place_svg(OUT/'support-campaign-wording.svg',227,790,174,62,'cover-title')
    save('ius-support-campaign-cover-interpretive',420,890,body,'IUS Support Campaign - reconstructed brochure cover',
         'Reconstructed cover layout with source-print logo, support campaign wording and a new manually drawn ten-graduate vector interpretation. The illustration preserves the broad composition, not original facial details or original artist strokes. This is not an exact facsimile. Canvas proportions and paper colour are estimated.',
         ['IMG_7953(1).jpeg'],'interpretive-application')

def petition_spread():
    body=rect(0,0,1520,635,'#F0D88E','yellow-petition-stock')
    body+=text_paths('YOUR PERSONAL, $5 SUPPORTER PETITION IS VITAL!',36,32,17,font='sans',width=686,ident='petition-headline')
    lines=[
      "You've probably heard that we're petitioning Victoria for a university",
      'centred in Prince George. We need every person of voting age on',
      "that petition - but there's a hitch...",
      '',
      "We're asking you to contribute $5 to make your signature really",
      '"talk" - in a loud, clear voice - to our elected representatives. An',
      'independent university makes excellent sense for us:',
      '',
      '  - it will encourage our kids to remain in the North',
      '  - it will be a major factor in Northern economic development',
      '  - it will encourage more of our young people to attain a',
      '    university education designed for employment in the North',
      '',
      'Call the Interior University Society at 562-6868 if you have any',
      'questions OR, PLEASE COMPLETE AND RETURN THIS PETITION',
      'ALONG WITH YOUR CHEQUE FOR $5 PAYABLE TO THE INTERIOR',
      'UNIVERSITY SOCIETY.',
      '',
      'The City of Prince George and the staff at City Hall are helping',
      'us with our campaign and will forward it to us.',
    ]
    for i,t in enumerate(lines):
        if t:body+=text_paths(t,36,75+i*22,12.4,font='sans',ident='petition-copy-'+str(i+1))
    body+=text_paths('Our thanks',700,566,14,font='sans',align='right',ident='petition-thanks')
    body+=place_svg(OUT/'ius-supporter-card-reconstructed.svg',760,0,760,635,'petition-form-panel')
    save('ius-supporter-petition-spread-reconstructed',1520,635,body,'IUS supporter petition - reconstructed spread',
         'Source-derived re-typesetting of the visible petition panel with the reconstructed supporter form. Body wording is interpreted across the supplied photographs, which contain reflections and partial occlusion; punctuation and line breaks are modern reconstruction choices, not a certified diplomatic transcription. Unreadable fine-print statement on the form is omitted. Historical phone, amount and campaign wording are archival content.',
         ['IMG_7955(1).jpeg','IMG_7952.jpeg','IMG_7947.jpeg'],'reconstructed-application')

if __name__=='__main__':
    letterhead();invitation();fundraising();cover();petition_spread()
    (ROOT/'source'/'application_manifest.json').write_text(json.dumps(manifest,indent=2))
    print('Built',len(manifest),'vector applications and components')
