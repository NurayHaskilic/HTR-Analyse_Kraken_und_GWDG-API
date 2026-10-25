"""
Handschriftenerkennung (HTR) mit Kraken.

Liest alle Bilder aus daten/bilder/, segmentiert sie (Baseline-Segmentierung)
und erkennt den Text mit dem CATMuS-Medieval-Modell. Für jedes Bild entsteht
eine Textdatei <Bildname>_transkription.txt in daten/transkriptionen/.
"""

import subprocess
from pathlib import Path


PROJEKTORDNER = Path(__file__).resolve().parent

MODELL = PROJEKTORDNER / "modelle" / "catmus-medieval-1.6.0.mlmodel"

BILDORDNER = PROJEKTORDNER / "daten" / "bilder"
ERGEBNISORDNER = PROJEKTORDNER / "daten" / "transkriptionen"
ERGEBNISORDNER.mkdir(parents=True, exist_ok=True)  


MODUS = "alle"  # "alle" = alle Bilder im Ordner, "einzeln" = nur EINZELBILD

EINZELBILD = "beispiel.jpg"  # Dateiname des Bildes, wenn MODUS = "einzeln"

BILDENDUNGEN = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}


if MODUS == "alle":
    bilder = sorted(
        datei for datei in BILDORDNER.iterdir()
        if datei.suffix.lower() in BILDENDUNGEN
    )
elif MODUS == "einzeln":
    bilder = [BILDORDNER / EINZELBILD]
else:
    raise ValueError('MODUS muss "alle" oder "einzeln" sein.')

if not MODELL.exists():
    raise FileNotFoundError(
        f"Modell nicht gefunden: {MODELL}\n"
        "Bitte das CATMuS-Medieval-Modell herunterladen und in den Ordner 'modelle' legen "
        "(siehe README, Abschnitt 'Modell herunterladen')."
    )

print(f"{len(bilder)} Bild(er) werden verarbeitet.")

for bild in bilder:
    ausgabe = ERGEBNISORDNER / f"{bild.stem}_transkription.txt"
    print(f"Verarbeite {bild.name} -> {ausgabe.name}")
    subprocess.run(
        ["kraken", "-i", str(bild), str(ausgabe), "segment", "-bl", "ocr", "-m", str(MODELL)]
    )

print("Fertig.")
