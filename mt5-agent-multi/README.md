# mt5-agent-multi — installazione su C:\n8n\mt5-agent-bot

1. **Backup**: copia `AGENTS.md` e `lessons.md` attuali in `AGENTS.xauusd.bak.md` e `lessons.xauusd.bak.md`.
2. **Simboli**: `python tools\check_symbols.py` (MT5 aperto). Se un simbolo risulta `MANCA`, usa il nome alternativo mostrato in AGENTS.md, cron-prompt.md, symbols_allowlist.py e check_decisions.py.
3. **Regole**: copia `AGENTS.md` e `lessons.md` di questa cartella in `C:\n8n\mt5-agent-bot`. Riporta nel nuovo lessons.md le eventuali lezioni valide del vecchio, in forma generale.
4. **Wrapper mt5-bot**: copia `tools\symbols_allowlist.py` accanto al wrapper e chiama `check_symbol(symbol)` in ogni tool che riceve un simbolo (quote, rates, order, ecc.), prima della chiamata MT5.
   Riavvia il server MCP mt5-bot **da fuori** Hermes (non con `hermes gateway restart` lanciato da Hermes).
5. **Cron**: sostituisci il prompt del job `mt5-agent-xauusd` con `cron-prompt.md`. Se Hermes lo permette, rinominalo `mt5-agent-multi` tenendo la schedulazione ogni 30 minuti (modifica il job esistente, non crearne uno nuovo e non cancellarlo prima). Non toccare altro in config.yaml.
6. **Giro di prova**: lancia il job una volta a mano, poi `python tools\check_decisions.py C:\n8n\mt5-agent-bot\decisions.jsonl`. Exit 0 = tutti e 5 i simboli presenti.
