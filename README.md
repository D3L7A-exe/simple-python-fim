# Simple Python FIM (File Integrity Monitor)

Ett säkerhetsverktyg i Python som övervakar en mapp och larmar när filer **läggs till, ändras eller tas bort**. Larmen visas i terminalen och kan skickas till en Discord-kanal. Inga externa beroenden, bara Pythons standardbibliotek.

## Så fungerar det
1. **Baseline:** verktyget räknar ut en SHA-256-hash för varje fil och sparar dem i `baseline.txt`.
2. **Övervakning:** var 2:a sekund räknas hasharna om och jämförs med baseline.

| Händelse | Larm |
|---|---|
| Fil finns, men hashen skiljer sig | `ÄNDRAD` |
| Fil finns som inte fanns i baseline | `NY FIL` |
| Fil fanns i baseline men finns inte längre | `BORTTAGEN` |

Efter varje larm uppdateras minnesbilden så att samma händelse inte larmar om och om igen. `baseline.txt` ändras inte av övervakningen.

## Användning
```bash
python main.py            # övervakar aktuell mapp
python main.py /sökväg    # övervakar en annan mapp
```
Välj **1** för att skapa baseline (gör det när mappen är i ett känt gott skick) och **2** för att starta övervakningen. Avsluta med Ctrl + C.

### Discord-larm (valfritt)
1. Skapa en webhook i Discord: *Kanalinställningar → Integrationer → Webhooks*.
2. Sätt URL:en som miljövariabel, **aldrig i koden**:
   ```bash
   export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."   # Linux/macOS
   $env:DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."     # PowerShell
   ```
3. Starta övervakningen. Verktyget skriver `Discord-larm: PÅ` när det är aktivt. Om Discord inte svarar skrivs en varning och övervakningen fortsätter.

## Begränsningar (medvetna val och kända luckor)
- **Polling, inte realtid:** filer kontrolleras var 2:a sekund, så en ändring som görs och återställs mellan två kontroller missas. Ett skarpt system skulle använda `inotify` (Linux) eller `watchdog`.
- **Baseline skyddas inte:** den som kan ändra filerna kan också ändra `baseline.txt`. I skarp miljö ska baseline signeras eller lagras på annan plats.
- **Bara innehåll:** behörigheter, ägare och tidsstämplar övervakas inte, bara filinnehåll.
- Alla filer hashas om vid varje varv, vilket är dyrt för stora mappar.
- Verktyget ersätter inte ett riktigt HIDS som Wazuh (FIM-modulen) eller AIDE. Det är ett lärprojekt för att förstå principen.

## Idéer framåt
Konfigurationsfil med undantagslistor, loggning till fil/syslog, möjlighet att skicka larm till Wazuh, och att kunna köras som systemtjänst.
