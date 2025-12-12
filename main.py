import os
import hashlib
import time

# --- HJÄLPFUNKTION: Räkna ut hashen för en fil ---
def calculate_file_hash(filepath):
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            # Vi läser filen bit för bit så minnet inte tar slut
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        return None

# --- FUNKTION 1: Skapa Baseline ---
def create_baseline():
    # Ta bort gammal baseline om den finns
    if os.path.exists("baseline.txt"):
        os.remove("baseline.txt")

    print("Beräknar hash för alla filer...")
    
    files_hashed = 0
    with open("baseline.txt", "w") as f:
        # Gå igenom alla mappar och filer där vi är
        for root, dirs, files in os.walk("."):
            for file in files:
                filepath = os.path.join(root, file)
                
                # Hoppa över själva scriptet och baseline-filen
                if file == "baseline.txt" or file == "main.py":
                    continue

                file_hash = calculate_file_hash(filepath)
                if file_hash:
                    # Spara som: ./mapp/fil.txt|hashvärde
                    f.write(f"{filepath}|{file_hash}\n")
                    files_hashed += 1

    print(f"\nKlar! Ny baseline skapad med {files_hashed} filer.")

# --- FUNKTION 2: Starta Övervakning ---
def start_monitoring():
    print("\nLaddar baseline...")
    baseline_dic = {}
    
    # 1. Läs in vår baseline till minnet
    try:
        with open("baseline.txt", "r") as f:
            for line in f:
                parts = line.strip().split("|")
                if len(parts) == 2: # Kolla att raden är hel
                    filvag, sparad_hash = parts
                    baseline_dic[filvag] = sparad_hash
    except FileNotFoundError:
        print("FEL: Ingen baseline hittades! Kör alternativ 1 först.")
        return

    print(f"Övervakning startad! (Avbryt med Ctrl + C)")
    print("Letar efter ändringar...")

    # 2. Evighetsloop som kollar filerna
    while True:
        time.sleep(2) # Pausa lite så datorn får vila
        
        # Gå igenom alla filer igen
        for root, dirs, files in os.walk("."):
            for file in files:
                filepath = os.path.join(root, file)
                
                # Ignorera scriptet och baseline
                if file == "baseline.txt" or file == "main.py":
                    continue

                # Räkna ut nuvarande hash
                ny_hash = calculate_file_hash(filepath)

                # KOLL 1: Är filen helt ny? (Finns inte i vår lista)
                if filepath not in baseline_dic:
                    print(f"[VARNING] Ny fil upptäckt: {filepath}")
                    # Lägg till den i minnet så vi inte varnar igen direkt
                    baseline_dic[filepath] = ny_hash
                
                # KOLL 2: Har filen ändrats? (Hashen stämmer inte)
                elif baseline_dic[filepath] != ny_hash:
                    print(f"[LARM] Fil ändrad: {filepath}")
                    baseline_dic[filepath] = ny_hash # Uppdatera minnet

# --- HUVUDMENY ---
if __name__ == "__main__":
    print("\n********* FIM - SÄKERHETSSPECIALISTEN *******")
    print("1. Skapa ny Baseline (Normalläge)")
    print("2. Starta Övervakning (Monitorering)")
    print("*********************************************")

    val = input("Välj ett alternativ (1 eller 2): ")

    if val == "1":
        create_baseline()
    elif val == "2":
        start_monitoring()
    else:
        print("Ogiltigt val.")