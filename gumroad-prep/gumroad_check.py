"""Controllo e correzione testi dei 4 prodotti Gumroad, in un solo passaggio.

Uso (da PowerShell):
    pip install pypdf
    python gumroad_check.py            # solo verifica, non scrive nulla
    python gumroad_check.py --apply    # corregge schede\\, prodotti.csv, script copertine (con backup)

Cosa NON fa: non carica nulla, non usa credenziali, non tocca upload\\ né i file in
Downloads/Desktop/OneDrive, non modifica i PDF né i PNG.
"""
import argparse
import csv
import datetime as dt
import io
import json
import re
import shutil
import sys
from pathlib import Path

from pypdf import PdfReader

ROOT = Path.home() / "gumroad-prep"
ORIGINAL_DIRS = [Path.home() / d for d in ("Downloads", "Desktop", "OneDrive")]
TEXT_EXT = {".md", ".txt", ".csv", ".html", ".htm", ".json", ".py", ".js", ".ps1", ".svg", ".yaml", ".yml"}
NEW_PHRASE_IT = "stampabile e annotabile con qualsiasi app di annotazione"
NEW_PHRASE_EN = "printable and annotatable with any annotation app"

PRODUCTS = {
    "Debt Payoff Roadmap": {"keys": ["debt"], "expected_pages": 23},
    "Subscription Audit Protocol": {"keys": ["audit"], "expected_pages": 10},
    "Utility Bill Defense Kit": {"keys": ["utility"], "expected_pages": None},
    "Subscription Reset": {"keys": ["reset"], "expected_pages": 17, "pdf_name": "The_Subscription_Reset_v2.pdf"},
}

# Parole vietate (case-insensitive). "fill" è parola intera per non colpire "fulfill"/"refill".
FORBIDDEN = re.compile(r"print or fill|fill digitally|fillable|compilabil\w*|\bfill\b", re.I)

# Sostituzioni automatiche, dalla più specifica alla più generica.
# Il "fill" isolato NON viene sostituito automaticamente: viene solo segnalato.
REPLACEMENTS = [
    (re.compile(r"print or fill digitally", re.I), lambda m: _case(m, "Printable and annotatable with any annotation app")),
    (re.compile(r"print or fill", re.I), lambda m: _case(m, "Printable and annotatable")),
    (re.compile(r"fill digitally", re.I), lambda m: _case(m, "annotate with any annotation app")),
    (re.compile(r"fillable", re.I), lambda m: _case(m, "printable and annotatable")),
    (re.compile(r"compilabil[ei]", re.I), lambda m: _case(m, NEW_PHRASE_IT)),
]


def _case(m, text):
    return text[0].upper() + text[1:] if m.group(0)[0].isupper() else text


def is_original_copy(p: Path) -> bool:
    s = str(p).lower()
    return any(k in s for k in ("original", "orig_", "_orig", "backup", ".bak", "_backup_"))


def product_of(p):
    name = (p.name if isinstance(p, Path) else p).lower()
    for prod, cfg in PRODUCTS.items():
        if any(k in name for k in cfg["keys"]):
            return prod
    return None


def snapshot(paths):
    out = {}
    for base in paths:
        if not base.exists():
            continue
        for f in base.rglob("*"):
            if f.is_file() and f.suffix.lower() in {".pdf", ".png", ".jpg", ".csv", ".md", ".txt"}:
                try:
                    st = f.stat()
                    out[str(f)] = [st.st_size, st.st_mtime]
                except OSError:
                    pass
    return out


def pdf_info(p: Path):
    r = PdfReader(str(p))
    fields = r.get_fields() or {}
    first = (r.pages[0].extract_text() or "") if r.pages else ""
    return {"pages": len(r.pages), "fields": len(fields), "first_page_print_or_fill": bool(re.search(r"print or fill", first, re.I))}


def fix_page_count(text: str, old: int, new: int) -> str:
    # "22 pages", "22-page", "22 pagine", "22 printable and annotatable pages"
    return re.sub(rf"\b{old}(?=(\s|-)(\w+\s){{0,3}}(pages?|pagine|pagina)\b)", str(new), text, flags=re.I)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="scrive le correzioni (con backup)")
    ap.add_argument("--root", default=str(ROOT))
    args = ap.parse_args()
    root = Path(args.root)
    if not root.exists():
        sys.exit(f"Cartella non trovata: {root}")

    upload = root / "upload"
    protected = [upload] + ORIGINAL_DIRS
    before = snapshot(protected)
    baseline_file = root / "_originals_baseline.json"
    report = {p: {"pdf": None, "pages": None, "fields": None, "covers": [], "desc_ok": True, "left": []} for p in PRODUCTS}

    # 1. PDF: pagine e campi AcroForm
    print("== 1. PDF in upload\\ ==")
    no_fields_everywhere = True
    for pdf in sorted(upload.glob("*.pdf")):
        info = pdf_info(pdf)
        prod = product_of(pdf)
        print(f"  {pdf.name}: {info['pages']} pagine, {info['fields']} campi AcroForm, prodotto={prod}")
        if info["fields"]:
            no_fields_everywhere = False
        if prod:
            want = PRODUCTS[prod].get("pdf_name")
            if want and pdf.name != want:
                continue
            report[prod].update(pdf=pdf.name, pages=info["pages"], fields=info["fields"])
            if prod == "Utility Bill Defense Kit" and info["first_page_print_or_fill"]:
                print("  !! Utility Bill Defense Kit: la prima pagina del PDF dice 'Print or fill digitally'. PDF NON modificato.")
                report[prod]["left"].append("PDF p.1: 'Print or fill digitally'")
    if not no_fields_everywhere:
        print("  !! Almeno un PDF ha campi compilabili: controlla prima di togliere 'fillable' da quel prodotto.")

    # File di testo da controllare/correggere
    targets = []
    for sub in ("schede", "covers", "reset_rebuild"):
        d = root / sub
        if d.exists():
            targets += [f for f in d.rglob("*") if f.is_file() and f.suffix.lower() in TEXT_EXT]
    if (root / "prodotti.csv").exists():
        targets.append(root / "prodotti.csv")
    targets = [t for t in targets if not is_original_copy(t)]

    backup_dir = root / f"_backup_{dt.datetime.now():%Y%m%d_%H%M%S}"
    changed = []

    print("\n== 2-3. Testi (schede, csv, script copertine, reset_rebuild) ==")
    for f in targets:
        text = f.read_text(encoding="utf-8", errors="replace")
        new = text
        if no_fields_everywhere:
            for rx, rep in REPLACEMENTS:
                new = rx.sub(rep, new)

        # Numero pagine
        if f.name.lower() == "prodotti.csv":
            rows = list(csv.reader(io.StringIO(new)))
            orig_rows = [r[:] for r in rows]
            header = [h.lower() for h in rows[0]] if rows else []
            page_cols = [i for i, h in enumerate(header) if "pag" in h]
            for row in rows[1:]:
                prod = product_of(",".join(row))
                fixes = {"Debt Payoff Roadmap": (22, 23)}
                real = report["Utility Bill Defense Kit"]["pages"]
                if real in (22, 23):
                    fixes["Utility Bill Defense Kit"] = (22 if real == 23 else 23, real)
                if prod in fixes:
                    old, val = fixes[prod]
                    for i, cell in enumerate(row):
                        if i in page_cols and cell.strip() == str(old):
                            row[i] = str(val)
                        else:
                            row[i] = fix_page_count(cell, old, val)
            if rows != orig_rows:
                buf = io.StringIO()
                csv.writer(buf, lineterminator="\r\n" if "\r\n" in text else "\n").writerows(rows)
                new = buf.getvalue()
        else:
            prod = product_of(f)
            if prod == "Debt Payoff Roadmap":
                new = fix_page_count(new, 22, 23)
            elif prod == "Utility Bill Defense Kit" and report[prod]["pages"] in (22, 23):
                real = report[prod]["pages"]
                new = fix_page_count(new, 22 if real == 23 else 23, real)

        if new != text:
            changed.append(f)
            if args.apply:
                dest = backup_dir / f.relative_to(root)
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, dest)
                f.write_text(new, encoding="utf-8")
            print(f"  {'CORRETTO' if args.apply else 'DA CORREGGERE'}: {f.relative_to(root)}")

        # In dry-run mostra cosa resterebbe dopo la correzione
        for m in FORBIDDEN.finditer(new):
            line_no = new[: m.start()].count("\n") + 1
            hit = f"{f.relative_to(root)}:{line_no} '{m.group(0)}'"
            prod = product_of(f) or "?"
            if prod in report:
                report[prod]["left"].append(hit)
                report[prod]["desc_ok"] = False
            print(f"  RIMASTO: {hit}")
        if f.parent.name.lower() == "covers" and f in changed:
            print(f"  -> script copertina modificato: rilancialo per rigenerare il PNG ({f.name})")

    # Copertine e miniature
    covers = root / "covers"
    if covers.exists():
        for img in covers.rglob("*"):
            if img.suffix.lower() in {".png", ".jpg", ".jpeg"} and not is_original_copy(img):
                prod = product_of(img)
                if prod:
                    report[prod]["covers"].append(img.name)
    debt_scripts = [f for f in targets if f.parent.name.lower() == "covers" and f.suffix.lower() in {".py", ".js", ".html", ".ps1", ".svg"}]
    if not debt_scripts:
        print("\n  !! Nessuno script in covers\\: 01_Debt_Payoff_Roadmap_1280x720.png NON è generata da script. Non la modifico.")

    # 4. Originali invariati
    after = snapshot(protected)
    diff = [k for k in before if after.get(k) != before[k]]
    if baseline_file.exists():
        base = json.loads(baseline_file.read_text(encoding="utf-8"))
        diff += [k for k in base if k in after and after[k] != base[k]]
    else:
        baseline_file.write_text(json.dumps(before, indent=1), encoding="utf-8")
        print(f"\n  Baseline originali salvata in {baseline_file.name} (rilancia per confrontare).")

    print("\n== 4. Riepilogo ==")
    print(f"{'Prodotto':30} {'PDF':34} {'Pag':>4} {'Campi':>5}  {'Desc ok':7}  Copertine")
    for prod, r in report.items():
        exp = PRODUCTS[prod]["expected_pages"]
        pag = f"{r['pages']}" + ("" if exp is None or r["pages"] in (None, exp) else f"!={exp}")
        print(f"{prod:30} {str(r['pdf']):34} {pag:>4} {str(r['fields']):>5}  {'sì' if r['desc_ok'] else 'no':7}  {', '.join(r['covers']) or '-'}")
        for h in r["left"]:
            print(f"    parola rimasta: {h}")
    print(f"\nFile {'corretti' if args.apply else 'da correggere'}: {len(changed)}" + (f" (backup in {backup_dir.name})" if args.apply and changed else ""))
    print("Originali invariati: " + ("SÌ" if not diff else "NO -> " + ", ".join(sorted(set(diff)))))
    print("Copertine PNG: verifica a occhio che non contengano 'fillable' / 'Print or fill' (lo script non legge il testo nelle immagini).")


if __name__ == "__main__":
    main()
