"""
PBA Event Monitor
Watches https://www.ticketnet.com.ph/event-detail/PBA for new events.
Sends a macOS notification (and optional Slack message) when new events appear.

Usage:
    python3 pba_monitor.py

Schedule with cron (every hour):
    crontab -e
    0 * * * * /usr/bin/python3 /path/to/pba_monitor.py >> /path/to/pba_monitor.log 2>&1
"""

import json
import os
import subprocess
from datetime import datetime
from playwright.sync_api import sync_playwright

# --- Config ---
URL = "https://www.ticketnet.com.ph/event-detail/PBA"
SNAPSHOT_FILE = os.path.join(os.path.dirname(__file__), "pba_events_snapshot.json")
SLACK_WEBHOOK_URL = ""  # Optional: paste your Slack webhook URL here to get Slack alerts

# Selectors to try (in order) for event cards on the page.
# Run the script once with DEBUG=True to see what's on the page and refine these.
EVENT_SELECTORS = [
    ".event-card",
    ".event-item",
    ".event-list-item",
    "[class*='event']",
    ".card",
]

DEBUG = False  # Set to True to print full page HTML for debugging selectors


def notify_macos(title: str, message: str):
    """Send a macOS notification."""
    script = f'display notification "{message}" with title "{title}"'
    subprocess.run(["osascript", "-e", script])


def notify_slack(message: str):
    """Send a Slack message via webhook."""
    if not SLACK_WEBHOOK_URL:
        return
    import urllib.request
    payload = json.dumps({"text": message}).encode("utf-8")
    req = urllib.request.Request(
        SLACK_WEBHOOK_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    urllib.request.urlopen(req)


def load_snapshot() -> list:
    if not os.path.exists(SNAPSHOT_FILE):
        return []
    with open(SNAPSHOT_FILE, "r") as f:
        return json.load(f)


def save_snapshot(events: list):
    with open(SNAPSHOT_FILE, "w") as f:
        json.dump(events, f, indent=2)


def scrape_events() -> list:
    events = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )

        print(f"[{datetime.now()}] Loading {URL} ...")
        page.goto(URL, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(2000)  # Extra wait for lazy-loaded content

        if DEBUG:
            print("=== PAGE HTML ===")
            print(page.content()[:5000])
            print("=================")

        # Try each selector until we find event cards
        for selector in EVENT_SELECTORS:
            cards = page.query_selector_all(selector)
            if cards:
                print(f"Found {len(cards)} elements with selector: {selector}")
                for card in cards:
                    text = card.inner_text().strip()
                    if text:
                        events.append(text)
                break
        else:
            # Fallback: capture the full visible text of the main content area
            print("No event cards found with known selectors. Falling back to full page text.")
            body_text = page.inner_text("body")
            # Store as a single item for diff comparison
            events = [body_text.strip()]

        browser.close()

    return events


def find_new_events(old: list, new: list) -> list:
    old_set = set(old)
    return [e for e in new if e not in old_set]


def main():
    print(f"[{datetime.now()}] PBA Monitor starting...")

    current_events = scrape_events()

    if not current_events:
        print("No events found. The page may have changed structure or blocked the request.")
        return

    print(f"Found {len(current_events)} event(s) on page.")

    previous_events = load_snapshot()

    if not previous_events:
        # First run - just save the snapshot
        save_snapshot(current_events)
        print("First run. Snapshot saved. No notifications sent.")
        return

    new_events = find_new_events(previous_events, current_events)

    if new_events:
        print(f"NEW EVENTS DETECTED: {len(new_events)}")
        for event in new_events:
            print(f"  - {event[:100]}")

        message = f"{len(new_events)} new PBA event(s) on TicketNet!\n" + "\n".join(
            e[:120] for e in new_events
        )

        notify_macos("PBA Events Alert", f"{len(new_events)} new event(s) on TicketNet!")
        notify_slack(f":basketball: *PBA Events Alert*\n{message}\n{URL}")

        save_snapshot(current_events)
    else:
        print("No new events detected.")

    print(f"[{datetime.now()}] Done.")


if __name__ == "__main__":
    main()
