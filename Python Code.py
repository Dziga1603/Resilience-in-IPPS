import pandas as pd
from pathlib import Path

# === SETTINGS ===
# Direct path to your Scopus CSV file
CSV_FILE = Path to file
OUTPUT_FILE = CSV_FILE.parent / "Planning_Resilience_Capabilities_3rdRound.csv"

# === LOAD THE CSV FILE ===
if not CSV_FILE.exists():
    raise FileNotFoundError(f"CSV file not found: {CSV_FILE}")

df = pd.read_csv(CSV_FILE)

# Optional: drop duplicates if EID is present
if "EID" in df.columns:
    df = df.drop_duplicates(subset="EID")

# === PREPARE TEXT FIELD (TITLE + ABSTRACT) ===
for col in ["Title", "Abstract"]:
    if col not in df.columns:
        raise KeyError(f"Column '{col}' not found in CSV. "
                       f"Current columns: {df.columns.tolist()}")

df["Title"] = df["Title"].fillna("")
df["Abstract"] = df["Abstract"].fillna("")
df["full_text"] = (df["Title"] + " " + df["Abstract"]).str.lower()

capability_patterns = {
    "Flexibility": [
        "flexibil"                   
    ],
    "Redundancy": [
        "redundan"                   
    ],
    "Velocity": [
        "velocit",                   
    ],
    "Visibility_Transparency": [
        "visibil",                   
        "traceab",                   
        "transparen",                
    ],
    "Awareness_Alertness": [
        "awareness",
        "aware",
        "alertness",
        "alert",
        "monitoring",
    ],
    "Collaboration": [
        "collaborat",                
        "cooperat",                  
        "coordination",              
        "joint decision",            
        "cross-functional",          
    ],
    "Robustness": [
        "robust",                    
        "stabilit",                  
        "resist",                    
    ],
    "Adaptability_Reconfigurability": [
        "adaptab",                   
        "reconfigurab",              
        "adjustab",                  
        "modif",                    
    ],
    "Recoverability": [
        "recoverab",                 
        "restorab",                  
        "repairab",                  
    ],
    "Resilience": [
        "resilien",
    ],
    "Forecasting": [
        "forecast", 
        "predict",
        "prognos",
    ],


}

# === TAG CAPABILITIES (BOOLEAN COLUMNS) ===
for cap, patterns in capability_patterns.items():
    # Build regex pattern "pat1|pat2|pat3"
    regex_pattern = "|".join(patterns)
    df[cap] = df["full_text"].str.contains(regex_pattern, case=False, regex=True)

# === BUILD HUMAN-READABLE LIST OF CAPABILITIES FOUND ===
cap_cols = list(capability_patterns.keys())

def collect_caps(row):
    found = [cap for cap in cap_cols if bool(row[cap])]
    return "; ".join(found)

df["Capabilities_found"] = df.apply(collect_caps, axis=1)

# Keep only papers where at least one capability is found
df_filtered = df[df["Capabilities_found"] != ""].copy()

# === SELECT OUTPUT COLUMNS ===
required_cols = ["Authors", "Title", "Year", "Source title", "Cited by"]
missing = [c for c in required_cols if c not in df_filtered.columns]
if missing:
    raise KeyError(f"Missing expected columns in CSV: {missing}")

# Add capability columns + aggregated list
output_cols = required_cols + cap_cols + ["Capabilities_found"]
df_out = df_filtered[output_cols]

# === SAVE RESULT ===
df_out.to_csv(OUTPUT_FILE, index=False)
print(f"Done. Saved {len(df_out)} papers to:\n{OUTPUT_FILE}")
