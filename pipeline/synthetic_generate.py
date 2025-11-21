import argparse
import json
import os
import random
import re
from datetime import datetime, timedelta
from pathlib import Path

from dateutil.relativedelta import relativedelta
from num2words import num2words
from playwright.sync_api import sync_playwright


# ----------------------------
# Paths / Config
# ----------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = Path("/mnt/data/invoice_template_photo_style.html")  # <-- uploaded template path
OUT_ROOT = PROJECT_ROOT / "data" / "raw" / "synthetic"
JSON_DIR = OUT_ROOT / "json"
HTML_DIR = OUT_ROOT / "html"
PDF_DIR = OUT_ROOT / "pdf"
PNG_DIR = OUT_ROOT / "png"

GST_SLABS = [0, 5, 12, 18, 28]
STATE = {
    "name": "Maharashtra",
    "code": "27",
}

SELLER_POOL = [
    ("TALOJA MANUFACTURERS' ASSOCIATION", "TALOJA MFG ASSN"),
    ("NEXOL INDUSTRIES PVT LTD", "NEXOL INDUSTRIES"),
    ("KANTEEN FOODS LLP", "KANTEEN FOODS"),
    ("VISTA REALTY SERVICES", "VISTA REALTY"),
    ("LABS TECH SOLUTIONS", "LABS TECH"),
]

BUYER_POOL = [
    "SHREE SIDDHI VINAYAK ENTERPRISES",
    "OMKAR TRADERS",
    "BLUEWAVE RETAILS",
    "GREENFIELD LOGISTICS",
    "SUNRISE ELECTRONICS",
    "UNITY CONSTRUCTIONS",
    "STARLIGHT CATERERS",
]

ITEM_POOL = [
    ("Consulting Services", "998312"),
    ("Software Subscription", "997331"),
    ("Office Rent", "999599"),
    ("Catering Services", "996331"),
    ("Electrical Supplies", "853690"),
    ("Furniture Purchase", "940330"),
    ("Advertising Services", "998361"),
]

BANK_POOL = [
    ("STATE BANK OF INDIA", "SBIN0012984", "SBININBBXXX"),
    ("HDFC BANK", "HDFC0000123", "HDFCINBBXXX"),
    ("ICICI BANK", "ICIC0000456", "ICICINBBXXX"),
]


# ----------------------------
# Helpers
# ----------------------------
def ensure_dirs():
    for d in (JSON_DIR, HTML_DIR, PDF_DIR, PNG_DIR):
        d.mkdir(parents=True, exist_ok=True)


def rand_gstin():
    # Basic fake GSTIN: 2 digits state + 10-char PAN-ish + 1Z + checksum-ish
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    pan = (
        random.choice(letters)
        + random.choice(letters)
        + random.choice(letters)
        + random.choice(letters)
        + random.choice(letters)
        + str(random.randint(1000, 9999))
        + random.choice(letters)
    )
    return f"{STATE['code']}{pan}1Z{random.randint(1,9)}"


def rand_pan():
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return (
        random.choice(letters)
        + random.choice(letters)
        + random.choice(letters)
        + random.choice(letters)
        + random.choice(letters)
        + str(random.randint(1000, 9999))
        + random.choice(letters)
    )


def rand_date():
    # Random date within last 18 months
    end = datetime.now()
    start = end - relativedelta(months=18)
    delta_days = (end - start).days
    d = start + timedelta(days=random.randint(0, delta_days))
    return d


def format_date(d: datetime):
    # Your template uses like "12-Aug-25"
    return d.strftime("%d-%b-%y")


def money_words_inr(n: float):
    n_int = int(round(n))
    words = num2words(n_int, lang="en_IN").title()
    return f"INR {words} Only"


def build_items():
    k = random.randint(2, 8)
    items = []
    for _ in range(k):
        name, hsn = random.choice(ITEM_POOL)
        qty = random.choice([1, 2, 3, 5, 10])
        rate = random.randint(200, 5000)
        amount = qty * rate
        items.append(
            {
                "particulars": name,
                "hsn": hsn,
                "qty": str(qty),
                "rate": rate,
                "amount": amount,
            }
        )
    return items


def compute_tax(items):
    taxable_total = sum(it["amount"] for it in items)
    slab = random.choice(GST_SLABS)
    cgst_rate = slab / 2
    sgst_rate = slab / 2

    cgst_amt = taxable_total * (cgst_rate / 100)
    sgst_amt = taxable_total * (sgst_rate / 100)
    tax_total = cgst_amt + sgst_amt

    tax_rows = [
        {
            "hsn": items[0]["hsn"] if items else "000000",
            "taxable": taxable_total,
            "cgst_rate": cgst_rate,
            "cgst_amt": round(cgst_amt, 2),
            "sgst_rate": sgst_rate,
            "sgst_amt": round(sgst_amt, 2),
        }
    ]

    totals = {
        "subtotal": taxable_total,
        "taxable_total": taxable_total,
        "cgst_total": round(cgst_amt, 2),
        "sgst_total": round(sgst_amt, 2),
        "tax_total": round(tax_total, 2),
    }

    return totals, tax_rows, slab


def random_invoice_json(i: int):
    seller_name, seller_short = random.choice(SELLER_POOL)
    buyer_name = random.choice(BUYER_POOL)

    d = rand_date()
    items = build_items()
    totals, tax_rows, slab = compute_tax(items)

    bank_name, ifsc, swift = random.choice(BANK_POOL)

    inv_no = random.choice(["INV", "T", "PB", "GST"]) + f"-{random.randint(1,999):03d}"

    data = {
        "seller": {
            "name": seller_name,
            "name_short": seller_short,
            "addr1": f"Plot {random.randint(1,999)}, MIDC Area",
            "addr2": f"Taloja, Navi Mumbai - {random.randint(400000, 499999)}",
            "gstin": rand_gstin(),
            "state_name": STATE["name"],
            "state_code": STATE["code"],
            "email": f"accounts{random.randint(1,99)}@{seller_short.lower().replace(' ','')}.com",
            "pan": rand_pan(),
        },
        "buyer": {
            "name": buyer_name,
            "address": f"Flat {random.randint(1,999)}, Sector {random.randint(1,50)}, Mumbai - {random.randint(400000, 499999)}",
            "gstin": rand_gstin(),
            "state_name": STATE["name"],
            "state_code": STATE["code"],
        },
        "invoice": {
            "no": inv_no,
            "date": format_date(d),
            "delivery_note": "",
            "payment_terms": random.choice(["Immediate", "15 Days", "30 Days", "Credit"]),
            "supplier_ref": "",
            "other_ref": "",
            "order_no": f"PO-{random.randint(1000,9999)}",
            "order_date": format_date(d - timedelta(days=random.randint(0,10))),
            "dispatch_doc": "",
            "delivery_note_date": "",
            "dispatch_through": random.choice(["Courier", "Hand Delivery", "Email"]),
            "destination": random.choice(["Mumbai", "Pune", "Navi Mumbai", "Thane"]),
            "delivery_terms": random.choice(["FOB", "CIF", "Ex-Works", ""]),
        },
        "items": items,
        "totals": totals,
        "tax_rows": tax_rows,
        "amount_in_words": money_words_inr(totals["subtotal"] + totals["tax_total"]),
        "tax_amount_in_words": money_words_inr(totals["tax_total"]),
        "remarks": random.choice(
            [
                "Goods supplied as per order.",
                "Monthly service billing.",
                "Lease compensation for premises.",
                "Subscription renewal invoice.",
            ]
        ),
        "bank": {
            "name": bank_name,
            "acno": str(random.randint(10**10, 10**11 - 1)),
            "branch_ifsc": f"{random.choice(['TALOJA','MUMBAI','PUNE'])} – {ifsc}",
            "swift": swift,
        },
        "_meta": {
            "gst_slab": slab,
            "generated_id": i,
        },
    }
    return data


def inject_demo_into_template(template_html: str, data: dict):
    """
    Replace the existing `const demo = {...};` with our generated JSON.
    Your HTML calls updateInvoice(demo) after demo definition.
    """
    demo_json = json.dumps(data, ensure_ascii=False, indent=2)
    pattern = r"const\s+demo\s*=\s*\{.*?\};"
    replacement = f"const demo = {demo_json};"
    new_html, n = re.subn(pattern, replacement, template_html, flags=re.DOTALL)
    if n == 0:
        raise RuntimeError("Could not find `const demo = {...};` block in template.")
    return new_html


def render_html_to_pdf_png(html_path: Path, pdf_path: Path, png_path: Path):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 794, "height": 1123})  # ~A4 px
        page.goto(html_path.as_uri(), wait_until="load")
        page.wait_for_timeout(500)  # let JS fill fields/tables

        page.pdf(path=str(pdf_path), print_background=True, format="A4")
        page.screenshot(path=str(png_path), full_page=True)

        browser.close()


def main(n: int):
    ensure_dirs()
    
    # Try multiple template paths (Linux path, Windows path, project root)
    template_paths = [
        TEMPLATE_PATH,  # Original Linux path
        PROJECT_ROOT / "invoice_template_photo_style.html",  # Project root
        Path("invoice_template_photo_style.html"),  # Current directory
    ]
    
    template_html = None
    for tp in template_paths:
        if tp.exists():
            template_html = tp.read_text(encoding="utf-8")
            print(f"Using template: {tp}")
            break
    
    if template_html is None:
        raise FileNotFoundError(
            f"Template not found. Tried: {[str(tp) for tp in template_paths]}\n"
            "Please place invoice_template_photo_style.html in the project root or update TEMPLATE_PATH."
        )

    for i in range(1, n + 1):
        data = random_invoice_json(i)

        base = f"inv_{i:05d}"
        json_path = JSON_DIR / f"{base}.json"
        html_path = HTML_DIR / f"{base}.html"
        pdf_path = PDF_DIR / f"{base}.pdf"
        png_path = PNG_DIR / f"{base}.png"

        filled_html = inject_demo_into_template(template_html, data)

        json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        html_path.write_text(filled_html, encoding="utf-8")

        render_html_to_pdf_png(html_path, pdf_path, png_path)

        print(f"[{i}/{n}] saved -> {json_path.name}, {pdf_path.name}, {png_path.name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=50, help="number of synthetic invoices to generate")
    args = parser.parse_args()
    main(args.n)

