import os
import shutil
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_ROOT = os.path.join(BASE_DIR, "SCHEDE_FITOSANITARI")
INDEX_FILE = os.path.join(BASE_DIR, "index.html")
PDFLIST_FILE = os.path.join(BASE_DIR, "pdfList.js")
BACKUP_DIR = os.path.join(BASE_DIR, "backup")

# ------------------------
# BACKUP
# ------------------------
def backup_file(path):
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    name = os.path.basename(path)
    backup_path = os.path.join(BACKUP_DIR, f"{name}.backup_{timestamp}")
    shutil.copy2(path, backup_path)
    print(f"Backup creato: {backup_path}")

# ------------------------
# SCANSIONE PDF
# ------------------------
def scan_pdfs():
    pdf_list = []

    for root, dirs, files in os.walk(PDF_ROOT):
        for file in files:
            if file.lower().endswith(".pdf"):
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, BASE_DIR)
                relative_path = relative_path.replace("\\", "/")
                pdf_list.append(relative_path)

    pdf_list.sort(key=lambda x: x.lower())
    return pdf_list

# ------------------------
# AGGIORNA pdfList.js
# ------------------------
def update_pdf_list(pdf_list):
    backup_file(PDFLIST_FILE)

    with open(PDFLIST_FILE, "w", encoding="utf-8") as f:
        f.write("const pdfList = [\n")
        for pdf in pdf_list:
            f.write(f'    "{pdf}",\n')
        f.write("];\n")

    print(f"pdfList.js aggiornato ({len(pdf_list)} PDF trovati)")

# ------------------------
# AGGIORNA FORNITORI IN index.html
# ------------------------
def update_index(pdf_list):
    backup_file(INDEX_FILE)

    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    # Estrai fornitori dalla struttura cartelle
    fornitori = sorted({
        pdf.split("/")[1]
        for pdf in pdf_list
        if pdf.startswith("SCHEDE_FITOSANITARI/")
    }, key=lambda x: x.lower())

    new_block = '<div class="fornitori">\n'
    for f in fornitori:
        display_name = f.replace("_", " ")
        new_block += f'    <a class="fornitore" href="SCHEDE_FITOSANITARI/{f}/index.html">{display_name}</a>\n'
    new_block += "</div>"

    # Sostituisce SOLO il blocco fornitori
    start = html.find('<div class="fornitori">')
    end = html.find("</div>", start) + len("</div>")

    if start == -1 or end == -1:
        print("Blocco fornitori non trovato.")
        return

    html = html[:start] + new_block + html[end:]

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print("Blocco fornitori aggiornato in index.html")

# ------------------------
# MAIN
# ------------------------
if __name__ == "__main__":
    print("Scansione PDF in corso...")
    pdfs = scan_pdfs()

    update_pdf_list(pdfs)
    update_index(pdfs)

    print("\nSITO AGGIORNATO CORRETTAMENTE ✅")