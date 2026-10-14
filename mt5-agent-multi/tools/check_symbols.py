"""Verifica (sola lettura) che i 5 simboli esistano sul broker MT5.

Uso:  python check_symbols.py
Richiede il terminale MT5 aperto e il pacchetto MetaTrader5 (pip install MetaTrader5).
Non apre, modifica o chiude nulla.
"""
import MetaTrader5 as mt5

WANTED = ["XAUUSD", "EURUSD", "GBPUSD", "BTCUSD", "ETHUSD"]
SEARCH = {"XAUUSD": "*XAU*", "EURUSD": "*EURUSD*", "GBPUSD": "*GBPUSD*",
          "BTCUSD": "*BTC*", "ETHUSD": "*ETH*"}

if not mt5.initialize():
    raise SystemExit(f"MT5 initialize fallito: {mt5.last_error()}")

acc = mt5.account_info()
print(f"Conto {acc.login} server={acc.server} demo={acc.trade_mode == mt5.ACCOUNT_TRADE_MODE_DEMO}\n")

for name in WANTED:
    info = mt5.symbol_info(name)
    if info is not None:
        print(f"OK   {name:8} trade_mode={info.trade_mode} volume_min={info.volume_min} digits={info.digits}")
    else:
        alts = [s.name for s in (mt5.symbols_get(SEARCH[name]) or [])]
        print(f"MANCA {name:8} alternative sul broker: {alts or 'nessuna'}")

mt5.shutdown()
