"""
Schritt 2: Begriffssuche in den Transkriptionen mit einem Sprachmodell, hier: GWDG.

Liest alle .txt-Dateien aus daten/transkriptionen/, lässt ein Sprachmodell nach
den SUCHBEGRIFFEN (und deren Wortformen) suchen und speichert die Ergebnisse
als CSV (für Excel) und JSON in daten/ergebnisse/.


"""

import os
import sys
import glob
import csv
import json
from dotenv import load_dotenv
import requests


load_dotenv()
api_key = os.getenv("GWDG_API_KEY")
if not api_key:
    sys.exit(
        "Kein API-Schlüssel gefunden. Bitte eine Datei '.env' mit dem Eintrag\n"
        "GWDG_API_KEY=dein_schluessel anlegen (Vorlage: .env.example)."
    )

PROJEKTORDNER = os.path.dirname(os.path.abspath(__file__))
ORDNER = os.path.join(PROJEKTORDNER, "daten", "transkriptionen")   
BILDORDNER = os.path.join(PROJEKTORDNER, "daten", "bilder")        
AUSGABEORDNER = os.path.join(PROJEKTORDNER, "daten", "ergebnisse") 
os.makedirs(AUSGABEORDNER, exist_ok=True)

SUCHBEGRIFFE = [""] #Suchbegriffe, siehe README 

MODELL = "openai-gpt-oss-120b"

system_prompt = (
    ""
)

url = "https://chat-ai.academiccloud.de/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}


def passendes_bild_finden(txt_dateiname):
    """Sucht ein Bild, dessen Name zur .txt-Datei passt (z.B. 231R_transkription.txt -> 231r.jpg)."""
    basis = os.path.splitext(txt_dateiname)[0]
    basis = basis.replace("_transkription", "")
    for endung in [".jpg", ".JPG", ".jpeg", ".JPEG", ".png", ".PNG"]:
        kandidat = os.path.join(BILDORDNER, basis + endung)
        if os.path.exists(kandidat):
            return kandidat
    # Falls nicht gefunden: nochmal ohne Beachtung von Groß-/Kleinschreibung suchen
    for datei in glob.glob(os.path.join(BILDORDNER, "*.*")):
        name_ohne_endung = os.path.splitext(os.path.basename(datei))[0]
        if name_ohne_endung.lower() == basis.lower():
            return datei
    return None  # kein passendes Bild gefunden


# Alle .txt-Dateien im Transkriptionen-Ordner finden
dateipfade = sorted(glob.glob(os.path.join(ORDNER, "*.txt")))
print(f"{len(dateipfade)} Dateien gefunden.")

ergebnisse = []

for pfad in dateipfade:
    dateiname = os.path.basename(pfad)
    with open(pfad, "r", encoding="utf-8") as f:
        transkriptionstext = f.read()

    bildpfad = passendes_bild_finden(dateiname)
    if bildpfad is None:
        print(f"  Warnung: Kein passendes Bild gefunden für {dateiname}")

    suchbegriffe_text = ", ".join(f'"{b}"' for b in SUCHBEGRIFFE)
    user_prompt = f"""Durchsuche die folgende Transkription nach einem dieser Begriffe (oder Wortformen davon): {suchbegriffe_text}.
Falls einer oder mehrere vorkommen: Nenne welche(r) Begriff(e) gefunden wurde(n) und gib die Fundstelle im Kontext (kurzer umgebender Satz) an.
Falls keiner vorkommt: Antworte nur mit "kein Treffer".

Transkription:
{transkriptionstext}
"""

    data = {
        "model": MODELL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }

    print(f"Durchsuche: {dateiname} ...")
    try:
        response = requests.post(url, headers=headers, json=data, timeout=300)
        if response.status_code == 200:
            antwort = response.json()["choices"][0]["message"]["content"]
        else:
            print(f"  Fehler (Status {response.status_code}), überspringe diese Datei.")
            antwort = f"FEHLER (Status {response.status_code})"
    except Exception as e:
        print(f"  Unerwarteter Fehler: {e}")
        antwort = "FEHLER (Ausnahme)"

    ergebnisse.append({
        "Dateiname": dateiname,
        "Bildpfad": os.path.relpath(bildpfad, PROJEKTORDNER) if bildpfad else "",
        "Treffer": antwort,
        "Transkription": transkriptionstext
    })

csv_datei = os.path.join(AUSGABEORDNER, "suchergebnisse.csv")
with open(csv_datei, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=["Dateiname", "Bildpfad", "Treffer", "Transkription"],
                            delimiter=";", quoting=csv.QUOTE_ALL)
    writer.writeheader()
    writer.writerows(ergebnisse)

json_datei = os.path.join(AUSGABEORDNER, "suchergebnisse.json")
with open(json_datei, "w", encoding="utf-8") as f:
    json.dump(ergebnisse, f, ensure_ascii=False, indent=2)

print(f"Gespeichert in:\n  {csv_datei}\n  {json_datei}")
