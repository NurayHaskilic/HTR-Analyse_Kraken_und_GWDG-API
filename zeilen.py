"""
Hilfsskript: Zeilennummern zu einer Textdatei hinzufügen.

Fundstellen werden in einer Transkription eindeutig zitiert.
"""

import sys
from pathlib import Path
 
 
def zeilennummern_hinzufuegen(eingabe_pfad: str, ausgabe_pfad: str | None = None) -> str:
    eingabe = Path(eingabe_pfad)
    if not eingabe.exists():
        raise FileNotFoundError(f"Datei nicht gefunden: {eingabe_pfad}")
 
    if ausgabe_pfad is None:
        ausgabe = eingabe.with_name(eingabe.stem + "_nummeriert" + eingabe.suffix)
    else:
        ausgabe = Path(ausgabe_pfad)
 
    zeilen = eingabe.read_text(encoding="utf-8").splitlines()
 
    breite = len(str(len(zeilen)))
 
    nummerierte_zeilen = [
        f"{i+1:>{breite}}: {zeile}" for i, zeile in enumerate(zeilen)
    ]
 
    ausgabe.write_text("\n".join(nummerierte_zeilen), encoding="utf-8")
    return str(ausgabe)
 
 
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Bitte gib die Eingabedatei an, z.B.:")
        print("python zeilen.py daten/transkriptionen/beispiel_transkription.txt")
        sys.exit(1)
 
    eingabe_pfad = sys.argv[1]
    ausgabe_pfad = sys.argv[2] if len(sys.argv) > 2 else None
 
    ergebnis_pfad = zeilennummern_hinzufuegen(eingabe_pfad, ausgabe_pfad)
    print(f"Done: {ergebnis_pfad}")
