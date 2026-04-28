#!/usr/bin/env python3
"""
Bulk-add 45 Ortto contacts to the Insites CRM.
Excludes Dexus contacts and Autopilot contacts (as instructed).
"""

import os, subprocess, json, sys, time

INTRANET_URL = os.environ.get("COMBINATE_INTRANET_URL", "")
INTRANET_KEY = os.environ.get("COMBINATE_INTRANET_KEY", "")

if not INTRANET_URL or not INTRANET_KEY:
    print("ERROR: COMBINATE_INTRANET_URL and COMBINATE_INTRANET_KEY must be set")
    sys.exit(1)

CONTACTS = [
    {"first_name": "Shane",        "last_name": "McGeorge",      "email": "ssmcgeorge@gmail.com"},
    {"first_name": "Nadine",       "last_name": "Bence",         "email": "sales@arcticipc.com.au"},
    {"first_name": "Nicholas",     "last_name": "Emini",         "email": "emini@ascotwealthmanagement.com.au"},
    {"first_name": "Patrick",      "last_name": "Mobbs",         "email": "pmobbs@britishchamber.com"},
    {"first_name": "Francesca",    "last_name": "Webster",       "email": "francesca@brazilianbeauty.com.au"},
    {"first_name": "Toby",         "last_name": "Stanford",      "email": "toby.stanford@brooklynunderwriting.com.au"},
    {"first_name": "Peter",        "last_name": "Virtue",        "email": "sales@virtueconcepts.com.au"},
    {"first_name": "Shane",        "last_name": "McGeorge",      "email": "hello@chameleoncocktails.com"},
    {"first_name": "Click",        "last_name": "Therapy",       "email": "info@clicktherapy.com.au"},
    {"first_name": "Julia",        "last_name": "Loughlin",      "email": "julia.loughlin@fmhgroup.com.au",        "job_title": "Group Chief Marketing and Communications Officer"},
    {"first_name": "Tracey",       "last_name": "Kurz",          "email": "connect@demandpower.com.au",            "work_phone_number": "0400938561", "job_title": "Business Development"},
    {"first_name": "Dalia",        "last_name": "Joudeh",        "email": "dalia.joudeh@nationaldentalcare.com.au"},
    {"first_name": "Zoe",          "last_name": "Clements",      "email": "zoe.clements@nationaldentalcare.com.au"},
    {"first_name": "Simon",        "last_name": "Lockyer",       "email": "simon.lockyer@fivegoodfriends.com.au"},
    {"first_name": "Tim",          "last_name": "Humphries",     "email": "thumphries@homestyleagedcare.com.au"},
    {"first_name": "Benjamin",     "last_name": "Galea",         "email": "benjamin.galea@eucharist28.org"},
    {"first_name": "Sebastian",    "last_name": "Condon",        "email": "sebastian.condon@eucharist28.org"},
    {"first_name": "Rommel",       "last_name": "Gutierrez",     "email": "rommel@jepto.com"},
    {"first_name": "Adrian",       "last_name": "Rayco",         "email": "adrian@jepto.com"},
    {"first_name": "Orelia",       "last_name": "Bello",         "email": "oreliab@lungfoundation.com.au",         "work_phone_number": "0732513674",  "job_title": "Lung Cancer Screening Lead"},
    {"first_name": "Harry",        "last_name": "Martin",        "email": "harrym@lungfoundation.com.au"},
    {"first_name": "Brigitta",     "last_name": "Rose",          "email": "brigittar@lungfoundation.com.au"},
    {"first_name": "Edward",       "last_name": "Kaleel",        "email": "info@marcedward.com.au"},
    {"first_name": "Scott",        "last_name": "Bell",          "email": "s.bell@nexushospitals.com.au"},
    {"first_name": "Nataly",       "last_name": "Rubio",         "email": "n.rubio@oncobeta.com",                  "work_phone_number": "0428613046",  "job_title": "Office Manager - Asia Pacific"},
    {"first_name": "Mandy",        "last_name": "Loi",           "email": "m.loi@oncobeta.com"},
    {"first_name": "Danielle",     "last_name": "Rapa",          "email": "pjswaste@hotmail.com"},
    {"first_name": "Danielle",     "last_name": "Rapa",          "email": "info@pjswaste.com.au"},
    {"first_name": "Mari",         "last_name": "Yammas",        "email": "info@peapilates.com.au"},
    {"first_name": "Melissa",      "last_name": "Quirk",         "email": "m.quirk@randw.com.au"},
    {"first_name": "Cam",          "last_name": "Davis",         "email": "info@rawprovideo.com",                  "work_phone_number": "61421247720"},
    {"first_name": "Oliver",       "last_name": "Garas",         "email": "marketing@rentaspace.com.au"},
    {"first_name": "Joanne",       "last_name": "Rogers",        "email": "joanne.rogers@shepherdcentre.org.au"},
    {"first_name": "Jim",          "last_name": "Hungerford",    "email": "jim.hungerford@shepherdcentre.org.au"},
    {"first_name": "Jo",           "last_name": "Wallace",       "email": "jo.wallace@shepherdcentre.org.au"},
    {"first_name": "Mitchell",     "last_name": "McAlister",     "email": "m.mcalister@stratumra.com"},
    {"first_name": "Kathleen",     "last_name": "Smith",         "email": "kathleen.smith@sydneyfestival.org.au"},
    {"first_name": "Patrick",      "last_name": "O'Sullivan",    "email": "patrick@atomdigital.com.au"},
    {"first_name": "John",         "last_name": "Csaki",         "email": "john@theoutsourceplace.com.au"},
    {"first_name": "Andrew",       "last_name": "Andriopoulos",  "email": "andrew@vicstarplumbing.com.au"},
    {"first_name": "Heath",        "last_name": "",              "email": "heath@wpperk.com"},
    {"first_name": "Watt",         "last_name": "Export",        "email": "wattsfresh@wattexport.com.au"},
    {"first_name": "Adam",         "last_name": "Watt",          "email": "awatt@wattexport.com.au"},
    {"first_name": "Sarah",        "last_name": "Nadenbousch",   "email": "sarah.nadenbousch@dulux.com.au"},
    {"first_name": "Andrew",       "last_name": "Paterson",      "email": "andrew.paterson@fdca.com.au",           "job_title": "CEO"},
]

created = []
failed = []

for i, c in enumerate(CONTACTS, 1):
    payload = {k: v for k, v in c.items() if v}
    payload_json = json.dumps(payload)
    cmd = [
        "curl", "-s", "-X", "POST",
        "-H", f"Authorization: {INTRANET_KEY}",
        "-H", "Accept: application/json",
        "-H", "Content-Type: application/json",
        "-d", payload_json,
        f"{INTRANET_URL}/crm/api/v2/contacts"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        resp = json.loads(result.stdout)
    except Exception:
        failed.append((c["email"], "invalid JSON response"))
        print(f"[{i:2}/{len(CONTACTS)}] FAIL  {c['email']} — bad response")
        continue

    if resp.get("uuid"):
        created.append((c["email"], resp["uuid"], resp.get("name", "")))
        print(f"[{i:2}/{len(CONTACTS)}] OK    {c['email']}  uuid={resp['uuid']}")
    elif resp.get("errors"):
        errs = resp["errors"]
        failed.append((c["email"], str(errs)))
        print(f"[{i:2}/{len(CONTACTS)}] FAIL  {c['email']} — {errs}")
    else:
        failed.append((c["email"], result.stdout[:120]))
        print(f"[{i:2}/{len(CONTACTS)}] FAIL  {c['email']} — {result.stdout[:120]}")

    time.sleep(0.2)  # stay well under rate limit

print(f"\n{'='*60}")
print(f"DONE  Created: {len(created)}  Failed: {len(failed)}")
if failed:
    print("\nFailed contacts:")
    for email, reason in failed:
        print(f"  {email}: {reason}")

# Write UUIDs for reference
if created:
    with open("scripts/ortto-crm-created-uuids.txt", "w") as f:
        for email, uuid, name in created:
            f.write(f"{uuid}\t{email}\t{name}\n")
    print(f"\nUUIDs written to scripts/ortto-crm-created-uuids.txt")
