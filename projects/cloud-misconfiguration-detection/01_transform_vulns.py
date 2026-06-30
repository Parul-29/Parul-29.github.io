#!/usr/bin/env python3
import json, re, sys
from pathlib import Path
import pandas as pd

INPUT = Path("CLOUD_VULRABILITES_DATASET.jsonl")
OUTPUT = Path("processed_vulns.csv")

# REMOVED 'misconfiguration' from keyword_groups to prevent leakage
keyword_groups = {
    "public_exposure": ["public", "exposed", "unauthenticated", "publicly", "open to the internet"],
    "privilege_escalation": ["privilege", "escalation", "sudo", "assume role"],
    "data_exposure": ["data exposure", "data leak", "sensitive data", "secrets", "credentials"],
    "dos": ["denial of service", "dos", "ddos"],
    "unencrypted": ["unencrypted", "no encryption", "plaintext"],
    "iam": ["iam", "policy", "role", "permission"],
    "s3_bucket": ["s3", "bucket", "storage bucket"],
    "ssrf_rce": ["ssrf", "remote code execution", "command injection"]
}

def pick_field(d, names):
    for name in names:
        if name in d and d[name]:
            return d[name]
        for k in d.keys():
            if k.lower() == name.lower():
                return d[k]
    return ""

rows = []
with open(INPUT, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line: continue
        obj = json.loads(line)

        title = pick_field(obj, ["title", "name"])
        desc = pick_field(obj, ["description", "details"])
        category = pick_field(obj, ["category", "type"])
        provider = pick_field(obj, ["cloud_provider", "provider"])
        poc = pick_field(obj, ["poc", "exploit"])
        ref = pick_field(obj, ["source", "reference"])

        combined = " ".join([str(title), str(desc), str(category), str(poc), str(ref)]).lower()

        # Create features (WITHOUT misconfiguration in features)
        feats = {k: int(any(kw in combined for kw in v)) for k,v in keyword_groups.items()}

        # Calculate severity
        severity = (
            feats["public_exposure"]*30 + feats["unencrypted"]*25 +
            feats["privilege_escalation"]*25 + feats["data_exposure"]*25 +
            feats["dos"]*10 + feats["ssrf_rce"]*20
        )

        # Create target variable SEPARATELY
        # This should be based on different logic than features
        is_misconfig = int(
            "misconfigur" in combined or 
            "incorrectly configured" in combined or
            "default" in combined or
            category.lower() in ["misconfiguration", "configuration error"]
        )

        row = {
            "title": str(title)[:400],
            "description": str(desc)[:1000],
            "category": category,
            "cloud_provider": provider,
            "severity": min(max(severity,0),100),
            "is_misconfiguration": is_misconfig  # Target
        }
        row.update(feats)  # Add all features
        rows.append(row)

df = pd.DataFrame(rows)
df.to_csv(OUTPUT, index=False)
print(f"Saved: {OUTPUT}")
print(f"Total rows: {len(df)}")
print(f"Misconfiguration rate: {df['is_misconfiguration'].mean():.2%}")