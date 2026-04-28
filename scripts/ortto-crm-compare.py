#!/usr/bin/env python3
"""
Cross-reference Ortto contacts against the Insites CRM.
Reports: contacts in Ortto missing from CRM, and which Ortto contacts look like
internal/test/junk records that should be excluded from the marketing list.
"""

import os, subprocess, json, sys

INTRANET_URL = os.environ.get("COMBINATE_INTRANET_URL", "")
INTRANET_KEY = os.environ.get("COMBINATE_INTRANET_KEY", "")

if not INTRANET_URL or not INTRANET_KEY:
    print("ERROR: COMBINATE_INTRANET_URL and COMBINATE_INTRANET_KEY must be set")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Ortto contacts extracted from the export (email, name, account/company, tags)
# Blank-email rows (anonymous website sessions) are excluded.
# ---------------------------------------------------------------------------
ORTTO_CONTACTS = [
    ("mitchell@avob.org.au", "Mitchell McAlister", "AVOB"),
    ("ben@demandpower.com.au", "Ben Kurz", "Demand Power"),
    ("cyrus@combinate.me", "Cyrus Bonzon", "Combinate"),
    ("katelyn@autopilothq.com", "Katelyn", "Autopilot"),
    ("dale@jepto.com", "Dale McGeorge", "Jepto"),
    ("gei@insites.io", "Gei Bernabe", "Insites"),
    ("yso@combinate.me", "Yso Nocon", "Combinate"),
    ("asd@sfd.me", "", ""),  # junk
    ("dalia.joudeh@nationaldentalcare.com.au", "Dalia Joudeh", "Dentist Jobs Australia"),
    ("dale@thejoinary.com", "Dale McGeorge", "The Joinary"),
    ("marketing@rentaspace.com.au", "Oliver Garas", "Rent A Space"),
    ("sales@virtueconcepts.com.au", "Peter Virtue", "Caulking Mate"),
    ("william@clearchoiceproducts.com", "William Spiers", "ClearChoice"),
    ("benjamin.galea@eucharist28.org", "Benjamin Galea", "International Eucharistic Congress"),
    ("mike@autopilothq.com", "Michael", "Autopilot"),
    ("ben.hughes@dexus.com", "Ben Hughes", "Dexus"),
    ("nicoleb@tamperevident.com.au", "Nicole Brady", "Tamper Evident"),
    ("colby@colbycool.com.au", "Coleman Levin", "Colbycool"),
    ("hello@chameleoncocktails.com", "Shane McGeorge", "Chameleon Cocktails"),
    ("staff@cbo.me", "CBO", ""),  # internal
    ("rommel@jepto.com", "Rommel Gutierrez", "Jepto"),
    ("sarah.nadenbousch@dulux.com.au", "Sarah Nadenbousch", "Dulux"),
    ("ryan.moloney@hpxgroup.com.au", "Ryan Moloney", "The Fold Legal"),
    ("andrew.paterson@fdca.com.au", "Andrew Paterson", "Family Day Care Australia"),
    ("francesca@brazilianbeauty.com.au", "Francesca Webster", "Brazilian Beauty"),
    ("riza@combinate.me", "Riza Galicinao", "Combinate"),
    ("sarah@colbycool.com.au", "Sarah Bailey", "Colbycool"),
    ("matt@colbycool.com.au", "Matt Kenney", "Colbycool"),
    ("ellen@autopilothq.com", "Ellen de Vries", "Autopilot"),
    ("georgia.quinn@halogroupholdings.com.au", "Georgia Quinn", "Hamilton Locke"),
    ("chris@insites.io", "Chris Clerke", "Insites"),
    ("zoe.clements@nationaldentalcare.com.au", "Zoe Clements", "Dentist Jobs Australia"),
    ("trevor.griffiths@dulux.com.au", "Trevor Griffiths", "Dulux"),
    ("john@theoutsourceplace.com.au", "John Csaki", "The Outsource Place"),
    ("marc@combinate.me", "Marc Aldrin Dela Cruz", "Combinate"),
    ("connect@demandpower.com.au", "Tracey Kurz", "Demand Power"),
    ("michael@thejoinary.com", "Michael Lucas", "The Joinary"),
    ("gem@insites.io", "Gem Villafuerte", "Insites"),
    ("nicholas.santana@grandyachtcrew.com", "Nicholas Santana-Rodaway", "Grand Yacht Crew"),
    ("victoria.day@dexus.com", "Victoria Day", "Dexus"),
    ("josephine.nuku@fdca.com.au", "Josephine Nuku", "Family Day Care Australia"),
    ("software@cbo.me", "", ""),  # internal
    ("sam.e@autopilothq.com", "Sam Eather", "Autopilot"),
    ("info@rawprovideo.com", "Cam Davis", "Raw Pro Video"),
    ("azeliaj@brooklynunderwriting.com.au", "Azelia Jackson", "Brooklyn Underwriting"),
    ("matthewgollings@bigpond.com", "Matthew Gollings", ""),
    ("ivory@combinate.me", "Ivy Santos", "Combinate"),
    ("timi@insites.io", "Timi Manching", "Insites"),
    ("patrick@atomdigital.com.au", "Patrick O'Sullivan", "Tamper Evident"),
    ("smckinney@ascotpartners.com.au", "Sussann McKinney", "Ascot Partners"),
    ("thumphries@homestyleagedcare.com.au", "Tim Humphries", "Homestyle Aged Care"),
    ("m.quirk@randw.com.au", "Melissa Quirk", "R&W"),
    ("wattsfresh@wattexport.com.au", "Watt Export", "Watt Export"),
    ("toby.stanford@brooklynunderwriting.com.au", "Toby Stanford", "Brooklyn Underwriting"),
    ("laraneville1972@gmail.com", "Lara Neville", "Rudolf Horvat And Associates"),
    ("enrique@insites.io", "Eric Tanada", "Insites"),
    ("awatt@wattexport.com.au", "Adam Watt", "Watt Export"),
    ("shane@insites.io", "Shane McGeorge", "Insites"),
    ("mitchellm@salientoperationsgroup.com", "Mitchell McAlister", "Salient Operations Group"),
    ("m.mcalister@stratumra.com", "Mitchell McAlister", "Stratum Risk Advisors"),
    ("info@peapilates.com.au", "Mari Yammas", "Pea Pilates"),
    ("erica@colbycool.com.au", "Erica Levin", "Colbycool"),
    ("monica.booker@dexus.com", "Monica Booker", "Dexus"),
    ("david.cripps@dulux.com.au", "David Cripps", "Dulux"),
    ("m.mcalister@stratumriskadvisors.com", "Mitchell McAlister", "Stratum Risk Advisors"),
    ("julia.loughlin@fmhgroup.com.au", "Julia Loughlin", "CouriersPlease"),
    ("john@clearchoiceproducts.com", "John Spiers", "ClearChoice"),
    ("callum.sinclair@dexus.com", "Callum Sinclair", "Dexus"),
    ("kathy.langsford@dexus.com", "Kathy Langsford", "Dexus"),
    ("davidp@brooklynunderwriting.com.au", "David Porteous", "Brooklyn Underwriting"),
    ("sean@fdca.com.au", "Sean Ross", "Family Day Care Australia"),
    ("jennifer.luk@dexus.com", "Jennifer Luk", "Dexus"),
    ("megan.connellan@dexus.com", "Megan Connellan", "Dexus"),
    ("shawn@autopilothq.com", "Shawn", "Autopilot"),
    ("joanne.rogers@shepherdcentre.org.au", "Joanne Rogers", "Shepherd Centre"),
    ("ruth.hendy@dexus.com", "Ruth Hendy", "Dexus"),
    ("matthew.asmanas@fdca.com.au", "Matthew Asmanas", "Family Day Care Australia"),
    ("maiks@combinate.me", "Maiks Ardona", "Combinate"),
    ("info@marcedward.com.au", "Edward Kaleel", "Marc Edward Agency"),
    ("n.rubio@oncobeta.com", "Nataly Rubio", "OncoBeta"),
    ("shalini.raj@reia.com.au", "Shalini Raj", "REIA"),
    ("jim.hungerford@shepherdcentre.org.au", "Jim Hungerford", "Shepherd Centre"),
    ("peter@my-breakthru.com.au", "Peter Schafer", "Breakthru"),
    ("jessica.dowery@axaxl.com", "Jessica Dowery", "AXA XL"),
    ("luke.bywater@couriersplease.com.au", "Luke Bywater", "Couriers Please"),
    ("pmobbs@britishchamber.com", "Patrick Mobbs", "Australian British Chamber of Commerce"),
    ("victoria.peisley@reia.com.au", "Victoria Peisley", "REIA"),
    ("rachelle.kells@dexus.com", "Rachelle Kells", "Dexus"),
    ("andrew.sullivan@dulux.com.au", "Andrew Sullivan", "Dulux"),
    ("adrian@jepto.com", "Adrian Rayco", "Jepto"),
    ("roccop@gsaib.com.au", "Rocco Pirrello", "GSA"),
    ("info@clicktherapy.com.au", "Click Therapy", "Click Therapy"),
    ("rrishard@rudolfhorvat.com.au", "Reyaz Rishard", "Rudolf Horvat And Associates"),
    ("jobelle@insites.io", "Jobelle Sarmiento", "Insites"),
    ("scott.rollason@reia.com.au", "Scott Rollason", "REIA"),
    ("andrew@vicstarplumbing.com.au", "Andrew Andriopoulos", "Vic Star Plumbing"),
    ("di@wattexport.com.au", "Dianne Watt", "Watt Export"),
    ("shane@combinate.me", "Shane McGeorge", "Combinate"),
    ("brooke.boardman@dexus.com", "Brooke Boardman", "Dexus"),
    ("nelia322@outlook.com", "Nelia Dasilva", "A Secret Luxury Spa"),
    ("erin@combinate.me", "Erin Hamley", "Combinate"),
    ("thesh.fernando@gmail.com", "Theshan Fernando", ""),
    ("felicityl@thefoldlegal.com.au", "Felicity Lyall", "The Fold Legal"),
    ("matt@wattexport.com.au", "Matt Robert Watt", "Watt Export"),
    ("oscullard@britishchamber.com", "Olivia Scullard", "Australian British Chamber of Commerce"),
    ("elise@clearchoiceproducts.com", "Elise Spiers", "ClearChoice"),
    ("tim.jamieson@dulux.com.au", "Tim Jamieson", "Dulux"),
    ("virtue.construction@bigpond.com", "Peter Virtue", "Virtue Concepts"),
    ("kimberly.kim@osstem.com.au", "Kimberly Kim", "Osstem"),
    ("lowell@insites.io", "Lowell Llames", "Insites"),
    ("oreliab@lungfoundation.com.au", "Orelia Bello", "Lung Learning Hub"),
    ("simon.lockyer@fivegoodfriends.com.au", "Simon Lockyer", "Five Good Friends"),
    ("raechelle.inman@dexus.com", "Raechelle Inman", "Dexus"),
    ("nicole.daoud@halogroupholdings.com.au", "Nicole Daoud", "The Fold Legal"),
    ("mark@insites.io", "Mark Anthony Yusi", "Insites"),
    ("sebastian.condon@eucharist28.org", "Sebastian Condon", "International Eucharistic Congress"),
    ("tim@autopilothq.com", "Tim Howard", "Autopilot"),
    ("harrym@lungfoundation.com.au", "Harry Martin", "Lung Learning Hub"),
    ("lee@combinate.me", "Lee Agosila", "Combinate"),
    ("nicolem@gsaib.com.au", "Nicole Mellick", "GSA"),
    ("brad.parsons@fdca.com.au", "Brad Parsons", "Family Day Care Australia"),
    ("ssmcgeorge@gmail.com", "Shane McGeorge", ""),
    ("edward@marcedward.com.au", "Edward Kaleel", "Marc Edward Agency"),
    ("tom.contino@finalsprint.com.au", "Thomas Contino", "Final Sprint"),
    ("info@vergamemorials.com.au", "John Verga", "Verga Memorials"),
    ("cecilia.palmero@dexus.com", "Cecilia Palmero", "Dexus"),
    ("pjswaste@hotmail.com", "Danielle Rapa", "PJ's Waste"),
    ("jo.wallace@shepherdcentre.org.au", "Jo Wallace", "Shepherd Centre"),
    ("admin@vicstarplumbing.com.au", "Natasha Ghorbani", "Vic Star Plumbing"),
    ("alex.fuller@aycc.org.au", "Alex Fuller", "Powershift"),
    ("info@pjswaste.com.au", "Danielle Rapa", "PJs Waste"),
    ("kathleen.smith@sydneyfestival.org.au", "Kathleen Smith", "Sydney Festival"),
    ("faizal@combinate.me", "Faiza Djulianto", "Combinate"),
    ("s.bell@nexushospitals.com.au", "Scott Bell", "Nexus Hospitals"),
    ("heath@wpperk.com", "Heath", "WP Perk"),
    ("tonyr@tamperevident.com.au", "Tony Renkin", "Tamper Evident"),
    ("steve@insites.io", "Steve Suyam", "Insites"),
    ("thomas.seselja@eucharist28.org", "Thomas Seselja", "International Eucharistic Congress"),
    ("ross@sprayshopsupplies.com.au", "Ross McClunie", "Spray Shop Supplies"),
    ("kristin@clicktherapy.com.au", "Kristin McGuckin", "Click Therapy"),
    ("brigittar@lungfoundation.com.au", "Brigitta Rose", "Lung Learning Hub"),
    ("emini@ascotwealthmanagement.com.au", "Nicholas Emini", "Ascot Wealth Management"),
    ("tracey@xpandonline.com.au", "Tracey Jarvis", "Xpand Online"),
    ("sales@arcticipc.com.au", "Nadine Bence", "Arctic IPC"),
    ("tfoot@crescentcap.com.au", "Todd Foot", "Crescent Capital"),
    ("v.steadman@oncobeta.com", "Victoria Steadman", "OncoBeta"),
    ("ijaouww@gmail.com", "", ""),  # junk
    ("alyssa@combinate.me", "Alyssa Venturanza", "Combinate"),
    ("ezekiel@insites.io", "Ezekiel Mojica", "Insites"),
    ("lori.schmidt@dexus.com", "Lori Schmidt", "Dexus"),
    ("lkamberi@ascotwealthmanagement.com.au", "Lindim Kamberi", "Ascot Wealth Management"),
    ("jennifer@combinate.me", "Jenn Nebres", "Combinate"),
    ("jim@combinate.me", "Jim Antonio", "Combinate"),
    ("m.loi@oncobeta.com", "Mandy Loi", "OncoBeta"),
]

# Domains/emails to treat as internal/junk (excluded from "missing" report)
INTERNAL_DOMAINS = {"combinate.me", "insites.io", "cbo.me"}
JUNK_EMAILS = {"asd@sfd.me", "ijaouww@gmail.com"}

# ---------------------------------------------------------------------------
# Pull all CRM contacts (paginated)
# ---------------------------------------------------------------------------
def fetch_crm_emails():
    crm_emails = set()
    page = 1
    size = 100
    while True:
        cmd = [
            "curl", "-s",
            "-H", f"Authorization: {INTRANET_KEY}",
            "-H", "Accept: application/json",
            f"{INTRANET_URL}/crm/api/v2/contacts?page={page}&size={size}"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)
        contacts = data.get("results", [])
        if not contacts:
            break
        for c in contacts:
            email = (c.get("email") or "").strip().lower()
            if email:
                crm_emails.add(email)
        total = data.get("total_entries", 0)
        fetched = (page - 1) * size + len(contacts)
        print(f"  Fetched {fetched}/{total} CRM contacts...", file=sys.stderr)
        if fetched >= total:
            break
        page += 1
    return crm_emails


print("Pulling CRM contacts...", file=sys.stderr)
crm_emails = fetch_crm_emails()
print(f"Total unique CRM emails: {len(crm_emails)}", file=sys.stderr)

# ---------------------------------------------------------------------------
# Compare
# ---------------------------------------------------------------------------
ortto_emails = {email.lower(): (name, company) for email, name, company in ORTTO_CONTACTS if email}

missing_from_crm = []
in_crm = []
internal_or_junk = []

for email, (name, company) in ortto_emails.items():
    domain = email.split("@")[-1] if "@" in email else ""
    if email in JUNK_EMAILS or not name:
        internal_or_junk.append((email, name, company, "junk/anonymous"))
    elif domain in INTERNAL_DOMAINS:
        internal_or_junk.append((email, name, company, "internal staff"))
    elif email in crm_emails:
        in_crm.append((email, name, company))
    else:
        missing_from_crm.append((email, name, company))

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
print(f"\n{'='*60}")
print(f"ORTTO vs CRM COMPARISON  ({len(ortto_emails)} unique Ortto emails)")
print(f"{'='*60}")

print(f"\n--- IN CRM ({len(in_crm)}) ---")
for email, name, company in sorted(in_crm, key=lambda x: x[2]):
    print(f"  {name:<30} {email:<45} {company}")

print(f"\n--- MISSING FROM CRM ({len(missing_from_crm)}) ---")
for email, name, company in sorted(missing_from_crm, key=lambda x: x[2]):
    print(f"  {name:<30} {email:<45} {company}")

print(f"\n--- INTERNAL/JUNK (excluded from marketing list) ({len(internal_or_junk)}) ---")
for email, name, company, reason in sorted(internal_or_junk, key=lambda x: x[3]):
    label = name or "(no name)"
    print(f"  [{reason}]  {label:<28} {email}")

print(f"\nSUMMARY")
print(f"  Ortto contacts total:     {len(ortto_emails)}")
print(f"  In CRM:                   {len(in_crm)}")
print(f"  Missing from CRM:         {len(missing_from_crm)}")
print(f"  Internal/junk (excluded): {len(internal_or_junk)}")
