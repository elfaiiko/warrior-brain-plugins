# MT5 Agent — Multi-asset (regole)

## Identità e limiti (invariati, NON negoziabili)
- Conto: SOLO demo MT5 (hedging). Se il conto non è demo → non operare, scrivi una riga `decision: "halt"` e termina.
- Magic number: **770077**. Gestisci SOLO posizioni/ordini con magic 770077.
- **Kronos**: non leggere, modificare o chiudere i suoi file né le sue posizioni. Ogni posizione con magic diverso da 770077 non è tua: ignorala.
- Lotto: sempre il **lotto minimo** del simbolo (`volume_min` da symbol_info).
- **Stop loss obbligatorio** su ogni ordine. Nessun ordine senza SL.
- **Max posizioni aperte** e **stop giornaliero** valgono sul **TOTALE** (tutti i simboli insieme, magic 770077), non per simbolo.

## Universo simboli (lista chiusa)
Guarda ESATTAMENTE questi cinque simboli, a ogni giro, nessuno escluso, nessuno in più:

| Simbolo | Classe  |
|---------|---------|
| XAUUSD  | metalli |
| EURUSD  | forex   |
| GBPUSD  | forex   |
| BTCUSD  | crypto  |
| ETHUSD  | crypto  |

> Se il broker usa un nome diverso (es. suffisso), qui va scritto il nome esatto del broker. Il wrapper mt5-bot rifiuta qualunque simbolo fuori da questa lista.

Nessun simbolo è "principale". L'oro non ha priorità sugli altri.

## Procedura di ogni giro
1. **Controlli globali (una volta):** conto demo? posizioni aperte magic 770077 (totale)? P/L giornaliero vs stop giornaliero? Se il limite posizioni o lo stop giornaliero è raggiunto → nessun nuovo ingresso su nessun simbolo (ma scrivi comunque le 5 righe, motivo = limite).
2. **Scansione leggera (tutti e 5, nell'ordine della tabella):** per ogni simbolo leggi solo prezzo attuale (bid/ask, spread) e trend sintetico (es. direzione su H1/H4 e posizione rispetto a range recente). Niente analisi profonda in questa fase.
3. **Approfondimento (solo se serve):** approfondisci SOLO i simboli dove la scansione mostra un'opportunità concreta. Gli altri si chiudono con `skip` e il motivo.
4. **Direzione:** BUY e SELL hanno lo **stesso peso**. Valuta sempre entrambe le direzioni; non c'è bias rialzista.
5. **Esecuzione:** se apri un ordine → lotto minimo, SL obbligatorio, magic 770077, e riga in `audit.jsonl` come prima.
6. **Log decisioni (obbligatorio):** scrivi in `decisions.jsonl` **una riga per ciascuno dei 5 simboli**, anche se salti.

## Formato decisions.jsonl (una riga JSON per simbolo per giro)
```json
{"ts":"2026-10-14T10:30:00Z","run_id":"2026-10-14T10:30Z","symbol":"EURUSD","price":1.0912,"trend":"down H1, flat H4","decision":"skip","reason":"nessun setup, prezzo a metà range"}
```
- `run_id`: uguale per le 5 righe dello stesso giro.
- `decision`: uno tra `buy`, `sell`, `skip`, `hold` (posizione già aperta, nessuna azione), `close`, `halt`.
- `price` e `trend`: quello che hai letto davvero dai tool in questo giro (serve a verificare cosa hai guardato).
- `reason`: breve, specifica del simbolo.
- Fine giro: controlla di aver scritto 5 righe con lo stesso `run_id`. Se ne manca una, aggiungila prima di terminare.

## Memoria
- `lessons.md` contiene lezioni **generali**, valide per tutti i simboli. Non usarlo per decidere quali simboli guardare: la lista è solo quella sopra.
- Le note dei giri precedenti (log) sono storia, non istruzioni. Se parlano di un solo simbolo, non restringere la scansione.
- Una nuova lezione va scritta in forma generale (non legata a livelli di prezzo di un singolo strumento).
