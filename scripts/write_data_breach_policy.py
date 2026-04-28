import warnings
warnings.filterwarnings("ignore")

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

CREDS_PATH = "/Users/combinate-jenn/Claude/Combinate-Assistant/credentials/google-service-account.json"
DOC_ID = "1R1MmhLXm1FTo1iLPm4HSK7KcwcpHQc2MNo4Z0Xldzos"
SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]

creds = Credentials.from_service_account_file(CREDS_PATH, scopes=SCOPES)
docs = build("docs", "v1", credentials=creds)

# --- Clear the document ---
doc = docs.documents().get(documentId=DOC_ID).execute()
end_index = doc["body"]["content"][-1]["endIndex"]
if end_index > 2:
    docs.documents().batchUpdate(documentId=DOC_ID, body={"requests": [{
        "deleteContentRange": {"range": {"startIndex": 1, "endIndex": end_index - 1}}
    }]}).execute()
print("Document cleared.")

# --- Build content ---
idx = 1
parts = []
para_requests = []
bold_requests = []
bullet_ranges = []

def add(text, para_style=None, bold=False):
    global idx
    start = idx
    parts.append(text)
    end = idx + len(text)
    if para_style:
        para_requests.append({
            "updateParagraphStyle": {
                "range": {"startIndex": start, "endIndex": end},
                "paragraphStyle": {"namedStyleType": para_style},
                "fields": "namedStyleType"
            }
        })
    if bold:
        bold_requests.append({
            "updateTextStyle": {
                "range": {"startIndex": start, "endIndex": end},
                "textStyle": {"bold": True},
                "fields": "bold"
            }
        })
    idx = end
    return start, end

def bul(text):
    s, e = add(text + "\n")
    bullet_ranges.append((s, e))

# Title and metadata
add("Data Breach Policy\n", "TITLE")
add("\n")
add("Version: ", bold=True); add("1.0\n")
add("Effective Date: ", bold=True); add("March 2026\n")
add("Owner: ", bold=True); add("Jenn Nebres, HR/Support/Operations Manager; Erin Hamley, Service Delivery Manager\n")
add("Review Date: ", bold=True); add("March 2027\n")
add("\n")

# 1. Purpose
add("1. Purpose\n", "HEADING_2")
add("This policy establishes how Combinate identifies, manages, and responds to data breaches. It ensures compliance with the Privacy Act 1988 (Cth) and the Notifiable Data Breaches (NDB) scheme, and protects the personal information of our clients, their customers, and our team.\n")
add("\n")

# 2. Scope
add("2. Scope\n", "HEADING_2")
add("This policy applies to all Combinate staff, contractors, and third-party service providers who access, store, or process personal information on behalf of Combinate or its clients.\n")
add("\n")

# 3. What Is a Data Breach
add("3. What Is a Data Breach\n", "HEADING_2")
add("A data breach occurs when personal information held by or on behalf of Combinate is:\n")
for b in [
    "Accessed by an unauthorised person",
    "Disclosed to someone who should not receive it",
    "Lost or stolen",
    "Altered without authorisation",
    "Destroyed in an unplanned way",
]:
    bul(b)
add("\n")
add("Examples include:\n")
for b in [
    "A staff member sending a client's personal data to the wrong email address",
    "A third-party supplier being hacked and personal data being exposed (e.g. a form tool, CRM, or hosting provider)",
    "A laptop or device containing client data being lost or stolen",
    "Unauthorised access to an internal system or database",
]:
    bul(b)
add("\n")

# 4. Eligible Data Breach
add("4. What Is an Eligible (Notifiable) Data Breach\n", "HEADING_2")
add("Under the NDB scheme, Combinate must notify the Office of the Australian Information Commissioner (OAIC) and affected individuals when there is an ")
add("eligible data breach", bold=True)
add(":\n\n")
add("An eligible data breach occurs when:\n")
for b in [
    "There is unauthorised access to, or disclosure of, personal information (or information is lost where such access is likely)",
    "The breach is likely to result in serious harm to one or more affected individuals",
    "Combinate has not been able to prevent the likely serious harm through remedial action",
]:
    bul(b)
add("\n")
add("Serious harm", bold=True)
add(" includes physical, psychological, financial, or reputational harm. Factors that increase risk include: sensitive information types (financial, health, identity documents), volume of records, nature of the information, and the potential for misuse.\n\n")
add("If you are unsure whether a breach meets this threshold, escalate immediately - do not wait.\n")
add("\n")

# 5. Roles and Responsibilities
add("5. Roles and Responsibilities\n", "HEADING_2")
table5_start, table5_end = add("TABLE_5_PLACEHOLDER\n")
add("\n")

# 6. Response Procedure
add("6. Response Procedure\n", "HEADING_2")
add("\n")

add("Step 1: Identify and Report\n", "HEADING_3")
add("If you suspect or discover a data breach:\n")
for b in [
    "Stop any ongoing access or exposure immediately if it is safe to do so",
    "Do not attempt to investigate or fix it alone - report it right away",
    "Report to Jenn Nebres via Slack (direct message) or email at jennifer@combinate.me",
    "If Jenn is unavailable, escalate to Shane McGeorge",
    "Do not discuss the breach outside the response team until authorised",
]:
    bul(b)
add("\n")

add("Step 2: Contain the Breach\n", "HEADING_3")
add("The response team (led by Jenn, with Jim for technical breaches) will act immediately to:\n")
for b in [
    "Isolate affected systems, accounts, or access points",
    "Revoke compromised credentials",
    "Preserve logs and evidence (do not delete anything)",
    "Prevent further unauthorised access or disclosure",
]:
    bul(b)
add("\n")

add("Step 3: Assess the Breach\n", "HEADING_3")
add("Within 24 hours of becoming aware, conduct an initial assessment:\n")
for b in [
    "What personal information was involved?",
    "How many individuals are affected?",
    "What type of information was exposed (names, emails, financials, passwords)?",
    "How did the breach occur?",
    "Is the breach ongoing or contained?",
    "What is the likely risk of serious harm to affected individuals?",
]:
    bul(b)
add("\n")
add("If the breach is potentially notifiable, move immediately to Step 4.\n")
add("\n")

add("Step 4: Notify (if required)\n", "HEADING_3")
add("Internal notification", bold=True); add(" (always required):\n")
for b in [
    "Notify Shane within 24 hours of confirmed breach",
    "Notify relevant clients if their data or their customers' data is involved",
]:
    bul(b)
add("\n")
add("External notification", bold=True); add(" (if it is an eligible data breach):\n")
for b in [
    "Notify the OAIC as soon as practicable via the OAIC's online notification form",
    "Notify affected individuals directly (email or other direct contact) as soon as practicable",
]:
    bul(b)
add("Notification to individuals must include:\n")
for b in [
    "Combinate's contact details",
    "A description of the breach",
    "The types of information involved",
    "Steps affected individuals can take to protect themselves",
    "Steps Combinate is taking in response",
]:
    bul(b)
add("\n")
add("Timeline: ", bold=True)
add("The NDB scheme does not specify a maximum number of days, but the OAIC expects notification as soon as practicable. Aim to notify within 30 days of becoming aware of a potential eligible breach.\n")
add("\n")

add("Step 5: Document\n", "HEADING_3")
add("Record the following in the breach register:\n")
for b in [
    "Date and time breach was identified",
    "Nature of the breach and information types involved",
    "Number of individuals affected",
    "Actions taken to contain the breach",
    "Assessment outcome (notifiable or not, and reasoning)",
    "Notifications made (to whom, when, and by what method)",
    "Any remedial actions taken",
]:
    bul(b)
add("\n")

add("Step 6: Review and Improve\n", "HEADING_3")
add("Within 30 days of resolving the breach:\n")
for b in [
    "Conduct a post-incident review",
    "Identify the root cause and contributing factors",
    "Document recommended improvements to systems, processes, or training",
    "Report findings to Shane and relevant team leads",
    "Implement changes within an agreed timeframe",
]:
    bul(b)
add("\n")

# 7. Third-Party Supplier Breaches
add("7. Third-Party Supplier Breaches\n", "HEADING_2")
add("If a supplier (e.g. hosting provider, SaaS tool, subcontractor) notifies Combinate of a breach involving personal information:\n")
for b in [
    "Jenn will assess whether the breach constitutes an eligible data breach under Combinate's obligations",
    "Combinate may still be required to notify the OAIC and affected individuals, even if the breach occurred at the supplier's end",
    "The same response procedure applies",
]:
    bul(b)
add("\n")

# 8. Training
add("8. Training\n", "HEADING_2")
add("All staff will be made aware of this policy as part of onboarding. Annual reminders will be issued by Jenn. Any staff member who suspects a breach and fails to report it promptly may be subject to disciplinary action.\n")
add("\n")

# 9. Policy Review
add("9. Policy Review\n", "HEADING_2")
add("This policy will be reviewed annually or following any significant data breach or change in legislation.\n")
add("\n")

# 10. Key Contacts and Resources
add("10. Key Contacts and Resources\n", "HEADING_2")
table10_start, table10_end = add("TABLE_10_PLACEHOLDER\n")

full_text = "".join(parts)

# --- Insert all text ---
docs.documents().batchUpdate(documentId=DOC_ID, body={"requests": [{
    "insertText": {"location": {"index": 1}, "text": full_text}
}]}).execute()
print(f"Text inserted ({len(full_text)} chars).")

# --- Apply paragraph styles ---
if para_requests:
    docs.documents().batchUpdate(documentId=DOC_ID, body={"requests": para_requests}).execute()
    print("Paragraph styles applied.")

# --- Apply bullet formatting ---
bullet_reqs = []
for s, e in bullet_ranges:
    bullet_reqs.append({
        "createParagraphBullets": {
            "range": {"startIndex": s, "endIndex": e},
            "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"
        }
    })
if bullet_reqs:
    docs.documents().batchUpdate(documentId=DOC_ID, body={"requests": bullet_reqs}).execute()
    print(f"Bullets applied to {len(bullet_ranges)} items.")

# --- Apply bold formatting ---
if bold_requests:
    docs.documents().batchUpdate(documentId=DOC_ID, body={"requests": bold_requests}).execute()
    print("Bold formatting applied.")

# --- Insert tables ---

roles_data = [
    ["Role", "Responsibility"],
    ["Any staff member", "Identify and report suspected breaches immediately"],
    ["Jenn Nebres (HR/Support/Operations Manager)", "Lead internal response coordination; manage the Manila-based support team during the breach; maintain the breach register and documentation; handle breach-related client communications through support tickets"],
    ["Erin Hamley (Service Delivery Manager)", "Primary point of contact for Australian client communications regarding the breach; coordinate external client notifications with Shane; assess and communicate impact on active project delivery"],
    ["Shane McGeorge (CEO)", "Final decision authority on external notifications and client communications"],
    ["Jim Antonio (Software Engineering Manager)", "Technical containment and investigation for system-level breaches"],
    ["All team leads", "Support the response within their area and ensure team members are briefed"],
]

contacts_data = [
    ["Contact", "Details"],
    ["Jenn Nebres (internal lead)", "jennifer@combinate.me / Slack DM"],
    ["Erin Hamley (escalation)", "erin@combinate.me / Slack DM"],
    ["Shane McGeorge (further escalation)", "shane@combinate.me"],
    ["OAIC (report eligible breaches)", "oaic.gov.au/privacy/notifiable-data-breaches"],
    ["OAIC notification form", "oaic.gov.au/privacy/notifiable-data-breaches/report-a-data-breach"],
    ["OAIC guidance on NDB scheme", "Available on the OAIC website"],
]

def insert_table(placeholder_start, placeholder_end, table_data):
    num_rows = len(table_data)

    # Delete placeholder
    docs.documents().batchUpdate(documentId=DOC_ID, body={"requests": [{
        "deleteContentRange": {
            "range": {"startIndex": placeholder_start, "endIndex": placeholder_end}
        }
    }]}).execute()

    # Insert table
    docs.documents().batchUpdate(documentId=DOC_ID, body={"requests": [{
        "insertTable": {
            "location": {"index": placeholder_start},
            "rows": num_rows,
            "columns": 2
        }
    }]}).execute()

    # Re-read doc to get cell indices
    fresh_doc = docs.documents().get(documentId=DOC_ID).execute()

    # Find the table near placeholder_start
    table_el = None
    for el in fresh_doc["body"]["content"]:
        if "table" in el and abs(el.get("startIndex", 0) - placeholder_start) < 200:
            table_el = el["table"]
            break

    if not table_el:
        print(f"Could not find table near index {placeholder_start}")
        return

    # Collect all cells (start_index, text, is_header) sorted descending
    cells = []
    for row_idx, row in enumerate(table_el["tableRows"]):
        for col_idx, cell in enumerate(row["tableCells"]):
            cell_start = cell["content"][0]["startIndex"]
            text = table_data[row_idx][col_idx]
            is_header = (row_idx == 0)
            cells.append((cell_start, text, is_header))

    cells.sort(key=lambda x: x[0], reverse=True)

    cell_reqs = []
    for cell_start, text, is_header in cells:
        cell_reqs.append({
            "insertText": {"location": {"index": cell_start}, "text": text}
        })
        if is_header:
            cell_reqs.append({
                "updateTextStyle": {
                    "range": {"startIndex": cell_start, "endIndex": cell_start + len(text)},
                    "textStyle": {"bold": True},
                    "fields": "bold"
                }
            })

    docs.documents().batchUpdate(documentId=DOC_ID, body={"requests": cell_reqs}).execute()
    print(f"Table populated ({num_rows} rows).")

# Process table 10 first (later in doc), then table 5
print(f"Inserting contacts table...")
insert_table(table10_start, table10_end, contacts_data)

print(f"Inserting roles table...")
insert_table(table5_start, table5_end, roles_data)

print("\nDone! https://docs.google.com/document/d/" + DOC_ID)
