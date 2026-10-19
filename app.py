{\rtf1\ansi\ansicpg1252\cocoartf2870
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import streamlit as st\
import sqlite3\
import pandas as pd\
import pypdf\
import re\
import datetime\
import os\
import shutil\
import zipfile\
\
st.set_page_config(page_title="Dashboard Catatan Keuangan", page_icon="\uc0\u55357 \u56496 ", layout="wide")\
\
st.title("\uc0\u55357 \u56496  Dashboard & Pemroses Catatan Keuangan Otomatis")\
st.markdown("Upload e-statement Bank BCA dan Kartu Kredit, sistem akan otomatis membersihkan, mengkategorikan, dan menghasilkan file `.ckbak` siap restore.")\
\
# Sidebar untuk Input\
st.sidebar.header("\uc0\u55357 \u56593  Pengaturan")\
pdf_password = st.sidebar.text_input("Password PDF (Tanggal Lahir DDMMYYYY)", type="password", value="21062002")\
\
uploaded_bank_files = st.sidebar.file_uploader("Upload PDF Rekening Koran BCA (Bisa banyak sekaligus)", type=["pdf"], accept_multiple_files=True)\
uploaded_cc_files = st.sidebar.file_uploader("Upload PDF Kartu Kredit BCA (Bisa banyak sekaligus)", type=["pdf"], accept_multiple_files=True)\
\
# Fungsi Kategori Mapping Sesuai Aturan Terbaru\
def get_category_id_v2(desc, tx_type):\
    d = desc.lower()\
    if tx_type == 1: # Income\
        if 'artax' in d or 'gaji' in d or 'pybca' in d: return 3\
        elif 'bunga' in d or 'dividen' in d: return 2\
        elif 'wd bca' in d or 'setoran' in d or 'cdm' in d or 'switching' in d or 'bi-fast cr' in d: return 41\
        elif 'ftscy' in d or 'stockbit' in d or 'rdn' in d: return 42\
        elif any(name in d for name in ['laura', 'rizqi', 'jhasperi', 'joni', 'mawaddah', 'dewi', 'hidayatun']): return 7\
        else: return 12\
    else: # Expense\
        if 'ftscy' in d or 'stockbit' in d or 'rdn' in d or 'bibit' in d or 'investasi' in d: return 42\
        elif 'shopeefood' in d: return 25\
        elif 'tkpd' in d or 'tokopedia' in d: return 15\
        elif 'oxy' in d or 'clean bright' in d or 'laundry' in d or 'cuci' in d: return 30\
        elif 'nasi' in d: return 25\
        elif 'hhb' in d or 'hokben' in d: return 25\
        elif 'papa dom' in d or 'barber' in d: return 45\
        elif 'basecamp' in d: return 25\
        elif 'omni flora' in d: return 19\
        elif 'selvie indah' in d: return 25\
        elif any(k in d for k in ['spbu', 'pertamina', 'bensin', 'grab', 'gojek', 'gocar', 'bus', 'kereta', 'access by', 'driv', 'park', 'flazz', 'switc', 'toll']): return 38\
        elif any(k in d for k in ['telkomse', 'xl', 'paket data', 'pulsa', 'mytelkomse']): return 37\
        elif any(k in d for k in ['pln', 'listrik', 'pdam', 'indihome', 'tagihan', 'spaylater', 'halodoc']): return 35\
        elif any(k in d for k in ['idm', 'indoma', 'alfamart', 'hypermart', 'shopee', 'ikea', 'aeon', 'klikindomare', 'blibli', 'sektoral', 'bravo', 'supermarket', 'go-pay', 'gopay', 'shopeepay', 'dana', 'kaspro', 'ovo']): return 15\
        elif any(k in d for k in ['pempek', 'roti', 'resto', 'mcdonald', 'kfc', 'solaria', 'warung', 'bakso', 'ayam', 'es teh', 'siomay', 'seblak', 'makan', 'depot', 'teh poci', 'kantin', 'nasgor', 'kedai', 'suteki', 'doner', 'pawon', 'looyal', 'coffee', 'ultra coffee', 'mooi', 'luuca', 'd\\'vella', 'ampera', 'ndok', 'tahu', 'sederha', 'roti bakar', 'bopet', 'sebo', 'g kitchen', 'sego', 'timtong', 'pos ketan', 'woofelgo', 'honey pok', 'mr suprek', 'fauzan', 'pangsit', 'cafe', 'tjap njonj', 'verte', 'moogs', 'puti reno', 'pins fries', 'cucicuy', 'l080', 'lapak kue', 'tahu tek', 'golbal', 'ate doz', 'sgmb np', 'brawijaya', 'kovitiam']): return 25\
        elif any(k in d for k in ['spotify', 'goers', 'reddoorz', 'hawai', 'game box', 'padel', 'malang nig', 'toilet vip', 'drink cour', 'tenan hawa', 'bioskop', 'xxi']): return 21\
        elif any(k in d for k in ['kost', 'sewa kost', 'cuan bersama']): return 33\
        elif any(k in d for k in ['apotek', 'kesehatan', 'obat']): return 24\
        elif any(k in d for k in ['bca card', 'kartu kredit']): return 46\
        elif any(k in d for k in ['dr martens', 'the body shop', 'penampilan']): return 45\
        elif any(k in d for k in ['bea meterai', 'biaya adm', 'koreksi bunga', 'biaya kartu', 'tarikan atm', 'tarik tunai']): return 39\
        else: return 39\
\
def clean_desc_v3(text):\
    s = text\
    for cutoff in ["rekening ini", "apabila nasabah", "laporan mutasi", "bca berhak", "bersambung ke", "halaman", "periode", "mata uang"]:\
        idx = s.lower().find(cutoff)\
        if idx != -1: s = s[:idx]\
    s = re.sub(r'^\\d\{2\}/\\d\{2\}\\s*', '', s)\
    s = re.sub(r'TRANSAKSI DEBIT|TRSF E-BANKING DB|TRSF E-BANKING CR|DB INTERCHANGE|KR INTERCHANGE|DB DEBIT DOMESTIK|BI-FAST DB|BI-FAST CR|KARTU KREDIT/PL|KARTU DEBIT|SETORAN VIA CDM|SWITCHING CR|SWITCHING', '', s, flags=re.IGNORECASE)\
    s = re.sub(r'TGL:\\s*\\d\{2\}/\\d\{2\}', '', s, flags=re.IGNORECASE)\
    s = re.sub(r'TANGGAL:\\s*\\d\{2\}/\\d\{2\}', '', s, flags=re.IGNORECASE)\
    s = re.sub(r'00000\\.00', '', s)\
    s = re.sub(r'QRC?014|QR\\s*\\d\{3\}', '', s, flags=re.IGNORECASE)\
    s = re.sub(r'\\b\\d\{1,3\}(?:[,\\.]\\d\{3\})*\\.\\d\{2\}\\b', '', s)\
    s = re.sub(r'\\bDB\\b', '', s, flags=re.IGNORECASE)\
    s = re.sub(r'\\bCR\\b', '', s, flags=re.IGNORECASE)\
    s = re.sub(r'\\bWSID:[A-Z0-9]+\\b', '', s, flags=re.IGNORECASE)\
    s = re.sub(r'\\s+', ' ', s).strip().lower()\
    return s if s else "transaksi bank"\
\
if st.button("\uc0\u55357 \u56960  Proses & Generate File .ckbak"):\
    if not os.path.exists('CK(18-10-2026-132328).ckbak'):\
        st.error("File database template `CK(18-10-2026-132328).ckbak` belum dimasukkan ke folder project!")\
    else:\
        with st.spinner("Sedang memproses transaksi dan menerapkan aturan kustom..."):\
            work_db = 'CK_Working.ckbak'\
            shutil.copyfile('CK(18-10-2026-132328).ckbak', work_db)\
            \
            conn = sqlite3.connect(work_db)\
            cursor = conn.cursor()\
            \
            cursor.execute("SELECT MAX(_id) FROM TRANSACT;")\
            next_id = cursor.fetchone()[0] + 1\
            \
            # 1. Proses Rekening Koran Bank\
            if uploaded_bank_files:\
                for uploaded_file in uploaded_bank_files:\
                    temp_pdf_path = f"temp_\{uploaded_file.name\}"\
                    with open(temp_pdf_path, "wb") as f:\
                        f.write(uploaded_file.getbuffer())\
                        \
                    reader = pypdf.PdfReader(temp_pdf_path)\
                    text_lines = []\
                    for page in reader.pages:\
                        for line in page.extract_text().split('\\n'):\
                            l = line.strip()\
                            if not l: continue\
                            if any(b in l for b in ["REKENING TAHAPAN XPRESI", "KCP SUNGKONO", "NO. REKENING", "HALAMAN", "PERIODE", "MATA UANG", "CATATAN:", "SALDO AWAL", "MUTASI CR", "MUTASI DB", "SALDO AKHIR", "KETERANGAN"]): continue\
                            text_lines.append(l)\
                            \
                    blocks, curr = [], []\
                    for l in text_lines:\
                        if re.match(r'^\\d\{2\}/\\d\{2\}\\b', l):\
                            if curr: blocks.append(curr)\
                            curr = [l]\
                        else:\
                            if curr: curr.append(l)\
                    if curr: blocks.append(curr)\
                    \
                    for b in blocks:\
                        b_str = " ".join(b)\
                        if "SALDO AWAL" in b_str: continue\
                        m_date = re.match(r'^(\\d\{2\})/(\\d\{2\})', b[0])\
                        if not m_date: continue\
                        day, mon_in_text = int(m_date.group(1)), int(m_date.group(2))\
                        is_db = " DB" in b_str\
                        \
                        # Eliminasi pembayaran CC di bank\
                        if 'kartu kredit' in b_str.lower() or 'bca card' in b_str.lower():\
                            continue\
                            \
                        tx_type = 0 if is_db else 1\
                        matches = []\
                        for m in re.finditer(r'(\\d\{1,3\}(?:[,\\.]\\d\{3\})*\\.\\d\{2\}|\\d+\\.\\d\{2\})\\s*(DB)?', b_str):\
                            val_str, flag = m.group(1), m.group(2)\
                            if val_str == '00000.00': continue\
                            matches.append((val_str, flag))\
                        if not matches: continue\
                        if is_db:\
                            db_matches = [m for m in matches if m[1] == 'DB']\
                            amount = float(db_matches[0][0].replace(',', '')) if db_matches else float(matches[0][0].replace(',', ''))\
                        else:\
                            amount = [float(m[0].replace(',', '')) for m in matches][0]\
                            \
                        dt = datetime.datetime(2026, mon_in_text, day, 12, 0, 0)\
                        timestamp_ms = int(dt.timestamp() * 1000)\
                        desc = clean_desc_v3(b_str)\
                        cat_id = get_category_id_v2(desc, tx_type)\
                        \
                        cursor.execute("""\
                            INSERT INTO TRANSACT (_id, id_category, desc, type, date, amount)\
                            VALUES (?, ?, ?, ?, ?, ?)\
                        """, (next_id, cat_id, desc, tx_type, timestamp_ms, str(int(round(amount)))))\
                        next_id += 1\
                    os.remove(temp_pdf_path)\
\
            # 2. Proses Kartu Kredit\
            if uploaded_cc_files:\
                months_map = \{'JAN':1, 'FEB':2, 'MAR':3, 'APR':4, 'MEI':5, 'JUN':6, 'JUL':7, 'AUG':8, 'SEP':9, 'OCT':10, 'NOV':11, 'DEC':12, 'AGU':8, 'AGT':8, 'OKT':10, 'NOP':11, 'DES':12\}\
                for uploaded_file in uploaded_cc_files:\
                    temp_pdf_path = f"temp_cc_\{uploaded_file.name\}"\
                    with open(temp_pdf_path, "wb") as f:\
                        f.write(uploaded_file.getbuffer())\
                        \
                    reader = pypdf.PdfReader(temp_pdf_path)\
                    if reader.is_encrypted:\
                        reader.decrypt(pdf_password)\
                        \
                    text = ""\
                    for page in reader.pages: text += page.extract_text() + "\\n"\
                    lines = [l.strip() for l in text.split('\\n') if l.strip()]\
                    \
                    # Deteksi bulan statement dari nama file atau isi\
                    stmt_month = 5 # default fallback\
                    for line in lines:\
                        if "TANGGAL REKENING" in line:\
                            # parse month if available\
                            pass\
\
                    for line in lines:\
                        m = re.match(r'^(\\d\{2\})[-/]([A-Z]\{3\}|\\d\{2\})\\s+(\\d\{2\})[-/]([A-Z]\{3\}|\\d\{2\})\\s+(.+)$', line, re.IGNORECASE)\
                        if m:\
                            d1, m1, d2, m2, rest = m.groups()\
                            amt_match = re.search(r'([\\d\\.]+)(\\s+CR)?$', rest)\
                            if amt_match:\
                                amt_str = amt_match.group(1)\
                                is_cr = bool(amt_match.group(2))\
                                desc = rest[:amt_match.start()].strip()\
                                amount = float(amt_str.replace('.', ''))\
                                \
                                d_lower = desc.lower()\
                                if 'cicilan bca ke' in d_lower or 'reversal cicilan' in d_lower or 'pembayaran' in d_lower or 'biaya bunga' in d_lower or 'bunga' in d_lower:\
                                    continue\
                                if is_cr: continue\
                                \
                                month_num = months_map.get(m1.upper(), 5)\
                                day_num = int(d1)\
                                trans_year = 2026\
                                \
                                dt = datetime.datetime(trans_year, month_num, day_num, 12, 0, 0)\
                                timestamp_ms = int(dt.timestamp() * 1000)\
                                cleaned_cc_desc = clean_desc_v3(desc)\
                                cat_id = get_category_id_v2(cleaned_cc_desc, 0)\
                                \
                                cursor.execute("""\
                                    INSERT INTO TRANSACT (_id, id_category, desc, type, date, amount)\
                                    VALUES (?, ?, ?, ?, ?, ?)\
                                """, (next_id, cat_id, cleaned_cc_desc, 0, timestamp_ms, str(int(round(amount)))))\
                                next_id += 1\
                    os.remove(temp_pdf_path)\
\
            # Optimasi DB\
            cursor.execute("UPDATE sqlite_sequence SET seq = ? WHERE name = 'TRANSACT';", (next_id - 1,))\
            conn.commit()\
            cursor.execute("VACUUM;")\
            conn.commit()\
            conn.close()\
            \
            st.success("\uc0\u10024  Berhasil diproses! Silakan download database terbaru di bawah.")\
            \
            # Tampilkan Grafik Ringkasan Pengeluaran per Kategori\
            conn = sqlite3.connect(work_db)\
            df_res = pd.read_sql_query("""\
                SELECT c.NAME as Kategori, SUM(CAST(t.amount AS REAL)) as Total\
                FROM TRANSACT t\
                JOIN CATEGORY c ON t.id_category = c._id\
                WHERE t.type = 0\
                GROUP BY c.NAME\
                ORDER BY Total DESC\
            """, conn)\
            conn.close()\
            \
            st.subheader("\uc0\u55357 \u56522  Grafik Pengeluaran Berdasarkan Kategori")\
            st.bar_chart(df_res.set_index('Kategori'))\
            \
            # Tombol Download\
            with open(work_db, "rb") as f:\
                st.download_button(\
                    label="\uc0\u55357 \u56549  Download File .ckbak Terbaru",\
                    data=f,\
                    file_name="CK(18-10-2026-132328).ckbak",\
                    mime="application/octet-stream"\
                )}