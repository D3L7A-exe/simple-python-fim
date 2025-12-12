# Simple Python FIM (File Integrity Monitor)

Detta är ett säkerhetsverktyg skrivet i Python som övervakar filer i en mapp för att upptäcka förändringar.

## Funktioner
1. **Skapa Baseline:** Räknar ut SHA-256 hash (fingeravtryck) för alla filer.
2. **Övervakning:** Kollar kontinuerligt om filer ändras, tas bort eller om nya filer tillkommer.

## Hur man använder det
1. Kör `python main.py`.
2. Välj alternativ **1** för att skapa en baseline.
3. Välj alternativ **2** för att starta övervakningen.