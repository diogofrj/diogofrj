#!/usr/bin/env python3
"""Fetch the public contribution calendar and write data/contributions.json.

Uses the unauthenticated HTML fragment the profile page itself loads
(https://github.com/users/<user>/contributions). No token needed.
Exits non-zero when the markup is not what we expect, so the workflow
never commits a broken graph.
"""
import json
import os
import re
import sys

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GH_PROFILE_USER", "diogofrj")
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "contributions.json")


def fetch_days():
    resp = requests.get(URL, headers={"User-Agent": "profile-readme-bot/1.0"}, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    days = []
    for td in soup.select("td.ContributionCalendar-day"):
        date = td.get("data-date")
        if not date:
            continue
        tip = soup.find("tool-tip", attrs={"for": td.get("id")}) if td.get("id") else None
        match = re.match(r"(\d+)\s+contribution", tip.get_text(strip=True)) if tip else None
        days.append({
            "date": date,
            "count": int(match.group(1)) if match else 0,
            "level": int(td.get("data-level") or 0),
        })

    if not days:
        sys.exit("no calendar cells found: GitHub markup may have changed")
    days.sort(key=lambda d: d["date"])

    if sum(d["count"] for d in days) == 0 and any(d["level"] > 0 for d in days):
        sys.exit("cells have levels but no counts parsed: tooltip markup may have changed")
    return days


def longest_streak(days):
    best = run = 0
    for d in days:
        run = run + 1 if d["count"] > 0 else 0
        best = max(best, run)
    return best


def main():
    days = fetch_days()
    data = {
        "username": USERNAME,
        "total_contributions": sum(d["count"] for d in days),
        "active_days": sum(1 for d in days if d["count"] > 0),
        "longest_streak": longest_streak(days),
        "days": days,
    }
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(data, f, indent=2)
    print(f"{len(days)} days, {data['total_contributions']} contributions, "
          f"longest streak {data['longest_streak']}")


if __name__ == "__main__":
    main()
