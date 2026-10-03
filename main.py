"""Simple Python FIM - ett enkelt File Integrity Monitor.
 
Skapar en baseline med SHA-256-hashar och övervakar sedan en mapp.
Larmar vid NYA, ÄNDRADE och BORTTAGNA filer - i terminalen och (valfritt)
via Discord-webhook.
"""
import hashlib
import json
import os
import sys
import time
import urllib.request
from datetime import datetime
 
BASELINE_FIL = "baseline.txt"
INTERVALL = 2  # sekunder mellan varje kontroll
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")  # sätts i miljön, aldrig i koden
SKIPPA_FILER = {BASELINE_FIL, os.path.basename(__file__)}
 
 
# --- HJÄLPFUNKTION: Räkna ut hashen för en fil ---
def calculate_file_hash(filepath):
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            # Läs bit för bit så att stora filer inte fyller minnet
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except (FileNotFoundError, PermissionError):
        return None
 
 
# --- HJÄLPFUNKTION: Lista alla filer i mappen (och undermappar) ---
def hitta_filer(rotmapp):
    for root, dirs, files in os.walk(rotmapp):
        dirs[:] = [d for d in dirs if d != ".git"]  # hoppa över git-mappen
        for file in files:
            if file in SKIPPA_FILER:
                continue
            yield os.path.join(root, file)
 
 
# --- HJÄLPFUNKTION: Skicka larm till terminalen och Discord ---
def larma(nivå, meddelande):
    tid = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rad = f"[{nivå}] {meddelande}"
    print(f"{tid} {rad}")
    if not WEBHOOK_URL:
        return
    try:
        data = json.dumps({"content": f"**FIM** {tid}\n{rad}"}).encode("utf-8")
        req = urllib.request.Request(
            WEBHOOK_URL, data=data,
            headers={"Content-Type": "application/json", "User-Agent": "simple-python-fim"},
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception as e:
        # Ett trasigt larm ska aldrig stoppa övervakningen
        print(f"{tid} [VARNING] Kunde inte skicka till Discord: {e}")
 
 
# --- FUNKTION 1: Skapa Baseline ---
def create_baseline(rotmapp):
    print("Beräknar hash för alla filer...")
    antal = 0
    with open(BASELINE_FIL, "w") as f:
        for filepath in hitta_filer(rotmapp):
            file_hash = calculate_file_hash(filepath)
            if file_hash:
                # Spara som: ./mapp/fil.txt|hashvärde
                f.write(f"{filepath}|{file_hash}\n")
                antal += 1
    print(f"\nKlar! Ny baseline skapad med {antal} filer.")
 
 
# --- FUNKTION 2: Starta Övervakning ---
def start_monitoring(rotmapp):
    baseline = {}
    try:
        with open(BASELINE_FIL, "r") as f:
            for line in f:
                # rsplit så att sökvägar som innehåller "|" fungerar
                parts = line.rstrip("\n").rsplit("|", 1)
                if len(parts) == 2:
                    baseline[parts[0]] = parts[1]
    except FileNotFoundError:
        print("FEL: Ingen baseline hittades! Skapa en först (alternativ 1).")
        return
 
    print(f"Övervakning startad av '{rotmapp}' ({len(baseline)} filer i baseline).")
    print("Discord-larm: " + ("PÅ" if WEBHOOK_URL else "AV (sätt DISCORD_WEBHOOK_URL)"))
    print("Avbryt med Ctrl + C\n")
 
    try:
        while True:
            time.sleep(INTERVALL)
            nuvarande = set()
 
            for filepath in hitta_filer(rotmapp):
                ny_hash = calculate_file_hash(filepath)
                if ny_hash is None:
                    continue  # filen försvann eller gick inte att läsa just nu
                nuvarande.add(filepath)
 
                if filepath not in baseline:
                    larma("NY FIL", filepath)
                    baseline[filepath] = ny_hash  # uppdatera minnet så vi inte larmar igen
                elif baseline[filepath] != ny_hash:
                    larma("ÄNDRAD", filepath)
                    baseline[filepath] = ny_hash
 
            # Filer som fanns i baseline men inte längre finns
            for filepath in [p for p in baseline if p not in nuvarande]:
                larma("BORTTAGEN", filepath)
                del baseline[filepath]
    except KeyboardInterrupt:
        print("\nÖvervakningen avslutad.")
 
 
# --- HUVUDMENY ---
if __name__ == "__main__":
    rotmapp = sys.argv[1] if len(sys.argv) > 1 else "."
    print("\n********* FIM - SÄKERHETSSPECIALISTEN *******")
    print(f"Mapp: {rotmapp}")
    print("1. Skapa ny Baseline (Normalläge)")
    print("2. Starta Övervakning (Monitorering)")
    print("*********************************************")
 
    val = input("Välj ett alternativ (1 eller 2): ")
    if val == "1":
        create_baseline(rotmapp)
    elif val == "2":
        start_monitoring(rotmapp)
    else:
        print("Ogiltigt val.")
