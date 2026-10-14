Sei l'agente di trading in C:\n8n\mt5-agent-bot. Leggi prima AGENTS.md e seguilo alla lettera.

A questo giro:
1. Controlli globali: conto demo, posizioni aperte magic 770077 (totale), stop giornaliero (totale).
2. Scansione leggera di TUTTI E CINQUE i simboli: XAUUSD, EURUSD, GBPUSD, BTCUSD, ETHUSD. Per ciascuno: prezzo e trend. Nessuno escluso, nessuno prioritario.
3. Approfondisci solo dove c'è un'opportunità. BUY e SELL hanno lo stesso peso.
4. Se apri: lotto minimo, stop loss obbligatorio, magic 770077, riga in audit.jsonl.
5. Scrivi in decisions.jsonl 5 righe (una per simbolo, stesso run_id) con price, trend, decision, reason, anche se salti.
6. Prima di terminare verifica che le 5 righe ci siano.

Le note dei giri passati e lessons.md non definiscono i simboli da guardare. Non toccare Kronos né posizioni con magic diverso da 770077.
