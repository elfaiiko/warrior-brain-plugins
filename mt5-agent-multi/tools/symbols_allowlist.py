"""Allowlist dei simboli per il wrapper mt5-bot.

Uso nel wrapper (in ogni tool che riceve un `symbol`, prima di chiamare MT5):

    from symbols_allowlist import check_symbol
    check_symbol(symbol)  # solleva ValueError se il simbolo non è permesso

Se il broker usa nomi diversi (es. "BTCUSD.a"), cambia la lista qui sotto
con i nomi esatti restituiti da tools/check_symbols.py.
"""

ALLOWED_SYMBOLS = frozenset({
    "XAUUSD",
    "EURUSD",
    "GBPUSD",
    "BTCUSD",
    "ETHUSD",
})


def check_symbol(symbol: str) -> str:
    if symbol not in ALLOWED_SYMBOLS:
        raise ValueError(
            f"Simbolo '{symbol}' non permesso. Ammessi: {sorted(ALLOWED_SYMBOLS)}"
        )
    return symbol
