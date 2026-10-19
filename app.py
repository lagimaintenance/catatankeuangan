import streamlit as st
import sqlite3
import pandas as pd
import pypdf
import re
import datetime
import os
import shutil
import altair as alt

# --- PAGE CONFIG ---
st.set_page_config(page_title="Dashboard Keuangan", layout="wide")

# --- STATE MANAGEMENT UNTUK THEME ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'Light'

# --- DYNAMIC CSS & NOTHING AESTHETIC REFINEMENT (MOBILE RESPONSIVE) ---
if st.session_state.theme == 'Light':
    bg_color = "#F7F7F8"
    card_bg = "#FFFFFF"
    text_color = "#111111"
    sub_text = "#555555"
    border_color = "#222222"
    input_bg = "#FFFFFF"
    tab_bg = "#EAEAEA"
    tab_active_bg = "#111111"
    tab_active_text = "#FFFFFF"
    tab_inactive_text = "#333333"
    chart_bg = "#FFFFFF"
    chart_text = "#333333"
    chart_grid = "#E5E5E5"
    shadow_box = "0 4px 12px rgba(0, 0, 0, 0.04)"
else:
    bg_color = "#1E1E22"
    card_bg = "#2A2D32"
    text_color = "#F5F5F5"
    sub_text = "#AAAAAA"
    border_color = "#555555"
    input_bg = "#22252A"
    tab_bg = "#22252A"
    tab_active_bg = "#F5F5F5"
    tab_active_text = "#1E1E22"
    tab_inactive_text = "#CCCCCC"
    chart_bg = "#2A2D32"
    chart_text = "#CCCCCC"
    chart_grid = "#3A3D42"
    shadow_box = "0 4px 12px rgba(0, 0, 0, 0.2)"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap');

    .stApp {{
        background-color: {bg_color};
        color: {text_color};
        font-family: 'Montserrat', sans-serif !important;
        font-size: 0.9rem;
    }}
    
    h1 {{
        text-align: center;
        color: {text_color};
        font-weight: 700;
        font-size: 1.8rem;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }}
    
    h3 {{
        text-align: center;
        color: {text_color};
        font-weight: 600;
        font-size: 1.3rem;
    }}

    h4 {{
        text-align: center;
        color: {text_color};
        font-weight: 600;
        font-size: 1.1rem;
    }}
    
    p, span, label, .stMarkdown {{
        color: {text_color} !important;
        font-size: 0.85rem;
    }}
    
    div[data-testid="stMetric"] {{
        background-color: {card_bg};
        border: 1px solid {border_color};
        padding: 12px;
        border-radius: 4px;
        box-shadow: {shadow_box};
    }}
    div[data-testid="stMetricValue"] {{
        font-size: 1.5rem;
        color: {text_color};
        font-weight: 700;
    }}
    div[data-testid="stMetricLabel"] {{
        color: {sub_text};
        text-transform: uppercase;
        font-size: 0.75rem;
    }}
    
    .stTabs [data-baseweb="tab-list"] {{
        justify-content: center;
        gap: 4px;
        background-color: {tab_bg};
        padding: 4px;
        border: 1px solid {border_color};
        border-radius: 4px;
        max-width: 600px;
        margin: 0 auto;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: transparent !important;
        border-radius: 2px;
    }}
    .stTabs [data-baseweb="tab"] p, 
    .stTabs [data-baseweb="tab"] span, 
    .stTabs [data-baseweb="tab"] div {{
        color: {tab_inactive_text} !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {tab_active_bg} !important;
        border-radius: 2px !important;
    }}
    .stTabs [aria-selected="true"] p, 
    .stTabs [aria-selected="true"] span, 
    .stTabs [aria-selected="true"] div {{
        color: {tab_active_text} !important;
        font-weight: 700 !important;
    }}
    
    .stButton button {{
        background-color: {card_bg};
        color: {text_color};
        border: 1px solid {border_color};
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.85rem;
        text-transform: uppercase;
        box-shadow: {shadow_box};
    }}
    .stButton button:hover {{
        background-color: {text_color};
        color: {bg_color};
        border-color: {text_color};
    }}
    
    .stTextInput input, .stSelectbox select {{
        background-color: {input_bg};
        color: {text_color};
        border: 1px solid {border_color};
        border-radius: 4px;
        font-size: 0.85rem;
    }}

    div[data-testid="stFileUploader"] {{
        border: 1px solid {border_color};
        border-radius: 4px;
        padding: 10px;
        background-color: {card_bg} !important;
        box-shadow: {shadow_box};
    }}
    div[data-testid="stFileUploader"] section {{
        background-color: {input_bg} !important;
        border: 1px dashed {border_color} !important;
    }}

    hr {{
        border-color: {border_color};
    }}

    /* OPTIMASI TAMPILAN MOBILE & CLOUD */
    @media (max-width: 768px) {{
        h1 {{ font-size: 1.4rem; }}
        h3 {{ font-size: 1.1rem; }}
        .stTabs [data-baseweb="tab-list"] {{
            flex-wrap: wrap; /* Mencegah tab meluber ke samping di HP */
            max-width: 100%;
        }}
        .stTabs [data-baseweb="tab"] p, 
        .stTabs [data-baseweb="tab"] span, 
        .stTabs [data-baseweb="tab"] div {{
            font-size: 0.7rem !important;
        }}
        div[data-testid="stMetricValue"] {{ font-size: 1.2rem; }}
        div[data-testid="stMetricLabel"] {{ font-size: 0.65rem; }}
    }}
    </style>
""", unsafe_allow_html=True)

# --- DATABASE SETUP (2 DATABASE TERPISAH) ---
BASE_DB = 'CK(18-10-2026-132328).ckbak'
WORK_DB = 'CK_Working.ckbak'  # Khusus Catatan Keuangan 3rd Party
INV_DB = 'INV_Working.db'     # Khusus Data Investasi

# Copy template awal jika belum ada
if not os.path.exists(WORK_DB) and os.path.exists(BASE_DB):
    shutil.copyfile(BASE_DB, WORK_DB)

def get_bank_connection():
    return sqlite3.connect(WORK_DB)

def get_inv_connection():
    conn = sqlite3.connect(INV_DB)
    conn.execute('''CREATE TABLE IF NOT EXISTS STOCK_PORTFOLIO (
        _id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp INTEGER,
        symbol TEXT,
        qty REAL,
        avg_price REAL,
        last_price REAL,
        buy_value REAL,
        market_value REAL,
        unrealized_rp REAL,
        unrealized_pct REAL
    )''')
    conn.commit()
    return conn

# --- HELPER FUNCTIONS ---
def get_category_id_v2(desc, tx_type):
    d = desc.lower()
    if tx_type == 1: # Income
        if 'artax' in d or 'gaji' in d or 'pybca' in d: return 3
        elif 'bunga' in d or 'dividen' in d: return 2
        elif 'wd bca' in d or 'setoran' in d or 'cdm' in d or 'switching' in d or 'bi-fast cr' in d: return 41
        elif 'ftscy' in d or 'stockbit' in d or 'rdn' in d: return 42
        elif any(name in d for name in ['laura', 'rizqi', 'jhasperi', 'joni', 'mawaddah', 'dewi', 'hidayatun']): return 7
        else: return 12
    else: # Expense
        if 'ftscy' in d or 'stockbit' in d or 'rdn' in d or 'bibit' in d or 'investasi' in d: return 42
        elif 'shopeefood' in d: return 25
        elif 'tkpd' in d or 'tokopedia' in d: return 15
        elif 'oxy' in d or 'clean bright' in d or 'laundry' in d or 'cuci' in d: return 30
        elif 'nasi' in d: return 25
        elif 'hhb' in d or 'hokben' in d: return 25
        elif 'papa dom' in d or 'barber' in d: return 45
        elif 'basecamp' in d: return 25
        elif 'omni flora' in d: return 19
        elif 'selvie indah' in d: return 25
        elif any(k in d for k in ['spbu', 'pertamina', 'bensin', 'grab', 'gojek', 'gocar', 'bus', 'kereta', 'access by', 'driv', 'park', 'flazz', 'switc', 'toll']): return 38
        elif any(k in d for k in ['telkomse', 'xl', 'paket data', 'pulsa', 'mytelkomse']): return 37
        elif any(k in d for k in ['pln', 'listrik', 'pdam', 'indihome', 'tagihan', 'spaylater', 'halodoc']): return 35
        elif any(k in d for k in ['idm', 'indoma', 'alfamart', 'hypermart', 'shopee', 'ikea', 'aeon', 'klikindomare', 'blibli', 'sektoral', 'bravo', 'supermarket', 'go-pay', 'gopay', 'shopeepay', 'dana', 'kaspro', 'ovo']): return 15
        elif any(k in d for k in ['pempek', 'roti', 'resto', 'mcdonald', 'kfc', 'solaria', 'warung', 'bakso', 'ayam', 'es teh', 'siomay', 'seblak', 'makan', 'depot', 'teh poci', 'kantin', 'nasgor', 'kedai', 'suteki', 'doner', 'pawon', 'looyal', 'coffee', 'ultra coffee', 'mooi', 'luuca', 'd\'vella', 'ampera', 'ndok', 'tahu', 'sederha', 'roti bakar', 'bopet', 'sebo', 'g kitchen', 'sego', 'timtong', 'pos ketan', 'woofelgo', 'honey pok', 'mr suprek', 'fauzan', 'pangsit', 'cafe', 'tjap njonj', 'verte', 'moogs', 'puti reno', 'pins fries', 'cucicuy', 'l080', 'lapak kue', 'tahu tek', 'golbal', 'ate doz', 'sgmb np', 'brawijaya', 'kovitiam']): return 25
        elif any(k in d for k in ['spotify', 'goers', 'reddoorz', 'hawai', 'game box', 'padel', 'malang nig', 'toilet vip', 'drink cour', 'tenan hawa', 'bioskop', 'xxi']): return 21
        elif any(k in d for k in ['kost', 'sewa kost', 'cuan bersama']): return 33
        elif any(k in d for k in ['apotek', 'kesehatan', 'obat']): return 24
        elif any(k in d for k in ['bca card', 'kartu kredit']): return 46
        elif any(k in d for k in ['dr martens', 'the body shop', 'penampilan']): return 45
        elif any(k in d for k in ['bea meterai', 'biaya adm', 'koreksi bunga', 'biaya kartu', 'tarikan atm', 'tarik tunai']): return 39
        else: return 39

def clean_desc_v3(text):
    s = text
    for cutoff in ["rekening ini", "apabila nasabah", "laporan mutasi", "bca berhak", "bersambung ke", "halaman", "periode", "mata uang"]:
        idx = s.lower().find(cutoff)
        if idx != -1: s = s[:idx]
    s = re.sub(r'^\d{2}/\d{2}\s*', '', s)
    s = re.sub(r'TRANSAKSI DEBIT|TRSF E-BANKING DB|TRSF E-BANKING CR|DB INTERCHANGE|KR INTERCHANGE|DB DEBIT DOMESTIK|BI-FAST DB|BI-FAST CR|KARTU KREDIT/PL|KARTU DEBIT|SETORAN VIA CDM|SWITCHING CR|SWITCHING', '', s, flags=re.IGNORECASE)
    s = re.sub(r'TGL:\s*\d{2}/\d{2}', '', s, flags=re.IGNORECASE)
    s = re.sub(r'TANGGAL:\s*\d{2}/\d{2}', '', s, flags=re.IGNORECASE)
    s = re.sub(r'00000\.00', '', s)
    s = re.sub(r'QRC?014|QR\s*\d{3}', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\b\d{1,3}(?:[,\.]\d{3})*\.\d{2}\b', '', s)
    s = re.sub(r'\bDB\b', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\bCR\b', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\bWSID:[A-Z0-9]+\b', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\s+', ' ', s).strip().lower()
    return s if s else "transaksi bank"

# --- AUTHENTICATION SETUP ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# --- HEADER & TOGGLE TEMA ---
col_head1, col_head2 = st.columns([10, 1])
with col_head2:
    toggle_label = "D" if st.session_state.theme == 'Light' else "L"
    if st.button(toggle_label, help="Ganti Tema (Light/Dark)"):
        st.session_state.theme = 'Dark' if st.session_state.theme == 'Light' else 'Light'
        st.rerun()

st.markdown("<h1>Financial Dashboard</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: {sub_text}; letter-spacing: 2px; font-size: 0.75rem;'>[ SYSTEM ACTIVE // SECURE ENVIRONMENT ]</p>", unsafe_allow_html=True)
st.write("")

tab1, tab2, tab3 = st.tabs(["Konversi PDF", "Dashboard", "Investasi"])

# ================= PAGE 1: KONVERSI PDF =================
with tab1:
    st.markdown("<h3>Terminal Input Data</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: {sub_text}; font-size: 0.85rem;'>Upload semua file Statement (BCA / Stockbit) disini. Sistem akan memisahkan database secara otomatis.</p>", unsafe_allow_html=True)
    st.write("")
    
    col_p_space1, col_p_main, col_p_space2 = st.columns([1, 2, 1])
    with col_p_main:
        pdf_password = st.text_input("Password PDF Kartu Kredit", type="password", value="21062002")
    
    st.write("")
    col1, col2, col3 = st.columns(3)
    with col1:
        uploaded_bank_files = st.file_uploader("Rekening Koran BCA", type=["pdf"], accept_multiple_files=True)
    with col2:
        uploaded_cc_files = st.file_uploader("CC BCA (Passworded)", type=["pdf"], accept_multiple_files=True)
    with col3:
        uploaded_stockbit_files = st.file_uploader("Stockbit SoA (PDF)", type=["pdf"], accept_multiple_files=True)
        
    st.write("")
    col_b_space1, col_b_main, col_b_space2 = st.columns([1, 2, 1])
    with col_b_main:
        process_btn = st.button("Proses & Sinkronisasi Database", type="primary", use_container_width=True)

    if process_btn:
        with st.spinner("Memproses sinkronisasi data..."):
            added_count, duplicate_count, stockbit_count = 0, 0, 0
            
            # --- PROSES REKENING KORAN & CC (DB 1: CK_Working.ckbak) ---
            if (uploaded_bank_files or uploaded_cc_files) and not os.path.exists(WORK_DB):
                st.error("File database template CK belum tersedia.")
            elif uploaded_bank_files or uploaded_cc_files:
                conn_bank = get_bank_connection()
                cursor = conn_bank.cursor()
                cursor.execute("SELECT MAX(_id) FROM TRANSACT;")
                res_id = cursor.fetchone()[0]
                next_id = (res_id or 0) + 1
                
                if uploaded_bank_files:
                    for uploaded_file in uploaded_bank_files:
                        temp_path = f"temp_{uploaded_file.name}"
                        with open(temp_path, "wb") as f: f.write(uploaded_file.getbuffer())
                        reader = pypdf.PdfReader(temp_path)
                        text_lines = []
                        for page in reader.pages:
                            for line in page.extract_text().split('\n'):
                                l = line.strip()
                                if not l: continue
                                if any(b in l for b in ["REKENING TAHAPAN XPRESI", "KCP SUNGKONO", "NO. REKENING", "HALAMAN", "PERIODE", "MATA UANG", "CATATAN:", "SALDO AWAL", "MUTASI CR", "MUTASI DB", "SALDO AKHIR", "KETERANGAN"]): continue
                                text_lines.append(l)
                                
                        blocks, curr = [], []
                        for l in text_lines:
                            if re.match(r'^\d{2}/\d{2}\b', l):
                                if curr: blocks.append(curr)
                                curr = [l]
                            else:
                                if curr: curr.append(l)
                        if curr: blocks.append(curr)
                        
                        for b in blocks:
                            b_str = " ".join(b)
                            if "SALDO AWAL" in b_str: continue
                            m_date = re.match(r'^(\d{2})/(\d{2})', b[0])
                            if not m_date: continue
                            day, mon_in_text = int(m_date.group(1)), int(m_date.group(2))
                            is_db = " DB" in b_str
                            if 'kartu kredit' in b_str.lower() or 'bca card' in b_str.lower(): continue
                            tx_type = 0 if is_db else 1
                            matches = []
                            for m in re.finditer(r'(\d{1,3}(?:[,\.]\d{3})*\.\d{2}|\d+\.\d{2})\s*(DB)?', b_str):
                                val_str, flag = m.group(1), m.group(2)
                                if val_str == '00000.00': continue
                                matches.append((val_str, flag))
                            if not matches: continue
                            if is_db:
                                db_matches = [m for m in matches if m[1] == 'DB']
                                amount = float(db_matches[0][0].replace(',', '')) if db_matches else float(matches[0][0].replace(',', ''))
                            else: amount = [float(m[0].replace(',', '')) for m in matches][0]
                                
                            dt = datetime.datetime(2026, mon_in_text, day, 12, 0, 0)
                            timestamp_ms = int(dt.timestamp() * 1000)
                            desc = clean_desc_v3(b_str)
                            cat_id = get_category_id_v2(desc, tx_type)
                            str_amount = str(int(round(amount)))
                            
                            cursor.execute("SELECT COUNT(*) FROM TRANSACT WHERE date = ? AND desc = ? AND amount = ? AND type = ?", (timestamp_ms, desc, str_amount, tx_type))
                            if cursor.fetchone()[0] > 0:
                                duplicate_count += 1
                                continue
                            cursor.execute("INSERT INTO TRANSACT (_id, id_category, desc, type, date, amount) VALUES (?, ?, ?, ?, ?, ?)", (next_id, cat_id, desc, tx_type, timestamp_ms, str_amount))
                            next_id += 1
                            added_count += 1
                        os.remove(temp_path)

                if uploaded_cc_files:
                    months_map = {'JAN':1, 'FEB':2, 'MAR':3, 'APR':4, 'MEI':5, 'JUN':6, 'JUL':7, 'AUG':8, 'SEP':9, 'OCT':10, 'NOV':11, 'DEC':12, 'AGU':8, 'AGT':8, 'OKT':10, 'NOP':11, 'DES':12}
                    for uploaded_file in uploaded_cc_files:
                        temp_path = f"temp_cc_{uploaded_file.name}"
                        with open(temp_path, "wb") as f: f.write(uploaded_file.getbuffer())
                        reader = pypdf.PdfReader(temp_path)
                        if reader.is_encrypted: reader.decrypt(pdf_password)
                        text = ""
                        for page in reader.pages: text += page.extract_text() + "\n"
                        lines = [l.strip() for l in text.split('\n') if l.strip()]
                        
                        for line in lines:
                            m = re.match(r'^(\d{2})[-/]([A-Z]{3}|\d{2})\s+(\d{2})[-/]([A-Z]{3}|\d{2})\s+(.+)$', line, re.IGNORECASE)
                            if m:
                                d1, m1, d2, m2, rest = m.groups()
                                amt_match = re.search(r'([\d\.]+)(\s+CR)?$', rest)
                                if amt_match:
                                    amt_str = amt_match.group(1)
                                    is_cr = bool(amt_match.group(2))
                                    desc = rest[:amt_match.start()].strip()
                                    amount = float(amt_str.replace('.', ''))
                                    d_lower = desc.lower()
                                    if 'cicilan bca ke' in d_lower or 'reversal cicilan' in d_lower or 'pembayaran' in d_lower or 'biaya bunga' in d_lower or 'bunga' in d_lower: continue
                                    if is_cr: continue
                                    month_num = months_map.get(m1.upper(), 5)
                                    day_num = int(d1)
                                    dt = datetime.datetime(2026, month_num, day_num, 12, 0, 0)
                                    timestamp_ms = int(dt.timestamp() * 1000)
                                    cleaned_cc_desc = clean_desc_v3(desc)
                                    cat_id = get_category_id_v2(cleaned_cc_desc, 0)
                                    str_amount = str(int(round(amount)))
                                    
                                    cursor.execute("SELECT COUNT(*) FROM TRANSACT WHERE date = ? AND desc = ? AND amount = ? AND type = ?", (timestamp_ms, cleaned_cc_desc, str_amount, 0))
                                    if cursor.fetchone()[0] > 0:
                                        duplicate_count += 1
                                        continue
                                    cursor.execute("INSERT INTO TRANSACT (_id, id_category, desc, type, date, amount) VALUES (?, ?, ?, ?, ?, ?)", (next_id, cat_id, cleaned_cc_desc, 0, timestamp_ms, str_amount))
                                    next_id += 1
                                    added_count += 1
                        os.remove(temp_path)

                cursor.execute("UPDATE sqlite_sequence SET seq = ? WHERE name = 'TRANSACT';", (next_id - 1,))
                conn_bank.commit()
                cursor.execute("VACUUM;")
                conn_bank.commit()
                conn_bank.close()

            # --- PROSES PORTFOLIO STOCKBIT (DB 2: INV_Working.db) ---
            if uploaded_stockbit_files:
                conn_inv = get_inv_connection()
                cursor_inv = conn_inv.cursor()
                cursor_inv.execute("DELETE FROM STOCK_PORTFOLIO") # Reset data lama
                
                for uploaded_file in uploaded_stockbit_files:
                    temp_path = f"temp_sb_{uploaded_file.name}"
                    with open(temp_path, "wb") as f: f.write(uploaded_file.getbuffer())
                    try:
                        reader = pypdf.PdfReader(temp_path)
                        text = ""
                        for page in reader.pages: text += page.extract_text() + "\n"
                        
                        if "PORTFOLIO STATEMENT" in text:
                            port_text = text.split("PORTFOLIO STATEMENT")[1]
                            if "This statement is taken to be correct" in port_text:
                                port_text = port_text.split("This statement is taken to be correct")[0]
                            
                            port_text = port_text.replace('|', ' ') 
                            pattern = r'\b([A-Z]{4})\b(.*?)(?=\b[A-Z]{4}\b|$)'
                            matches = re.finditer(pattern, port_text, re.DOTALL)
                            
                            for m in matches:
                                symbol = m.group(1)
                                chunk = m.group(2)
                                if symbol in ['DATE', 'PAGE', 'IDR', 'TGL:']: continue
                                
                                nums = re.findall(r'(?:^|\s)(-?\d+(?:,\d{3})*(?:\.\d+)?)(?=\s|$)', chunk)
                                if len(nums) >= 7:
                                    nums = nums[:7] 
                                    qty = float(nums[0].replace(',', ''))
                                    avg_price = float(nums[1].replace(',', ''))
                                    last_price = float(nums[2].replace(',', ''))
                                    buy_value = float(nums[3].replace(',', ''))
                                    market_value = float(nums[4].replace(',', ''))
                                    unrealized_rp = float(nums[5].replace(',', ''))
                                    unrealized_pct = float(nums[6].replace(',', ''))
                                    
                                    timestamp_ms = int(datetime.datetime.now().timestamp() * 1000)
                                    cursor_inv.execute("""
                                        INSERT INTO STOCK_PORTFOLIO 
                                        (timestamp, symbol, qty, avg_price, last_price, buy_value, market_value, unrealized_rp, unrealized_pct)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                    """, (timestamp_ms, symbol, qty, avg_price, last_price, buy_value, market_value, unrealized_rp, unrealized_pct))
                                    stockbit_count += 1
                    except Exception as e:
                        st.error(f"Gagal memproses file Stockbit: {e}")
                    finally:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                conn_inv.commit()
                conn_inv.close()
            
            st.success(f"Sinkronisasi Selesai! | Transaksi Bank: {added_count} (Duplikat {duplicate_count}) | Portofolio Diekstrak: {stockbit_count}")

    # Area Download Database Terpisah
    st.write("")
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        if os.path.exists(WORK_DB):
            with open(WORK_DB, "rb") as f:
                st.download_button(label="Download DB Catatan Keuangan (.ckbak)", data=f, file_name="CK(18-10-2026-132328).ckbak", mime="application/octet-stream", use_container_width=True)
    with col_dl2:
        if os.path.exists(INV_DB):
            with open(INV_DB, "rb") as f:
                st.download_button(label="Download DB Investasi (.db)", data=f, file_name="INV_Data.db", mime="application/octet-stream", use_container_width=True)

# --- FUNGSI DASHBOARD KEUANGAN UTAMA (TAB 2) ---
def render_dashboard():
    st.markdown("<h3>Analisis Cashflow</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: {sub_text}; font-size: 0.75rem; letter-spacing: 1px;'>[ FINANCIAL METRICS INTERFACE ]</p>", unsafe_allow_html=True)
    st.write("")
    
    if os.path.exists(WORK_DB):
        conn = get_bank_connection()
        df = pd.read_sql_query("""
            SELECT t._id, c.NAME as Kategori, t.desc as Deskripsi, t.amount as Jumlah, t.date, t.type
            FROM TRANSACT t
            JOIN CATEGORY c ON t.id_category = c._id
        """, conn)
        conn.close()
        
        if not df.empty:
            df['datetime'] = pd.to_datetime(df['date'], unit='ms')
            df['Tahun'] = df['datetime'].dt.year
            df['Bulan'] = df['datetime'].dt.month
            df['Jumlah'] = pd.to_numeric(df['Jumlah'])
            
            years = sorted(df['Tahun'].unique(), reverse=True)
            selected_year = st.selectbox("Pilih Tahun", years)
            
            df_year = df[df['Tahun'] == selected_year]
            
            total_income_yr = df_year[df_year['type'] == 1]['Jumlah'].sum()
            total_expense_yr = df_year[df_year['type'] == 0]['Jumlah'].sum()
            
            col_a, col_b, col_c = st.columns(3)
            col_a.metric(f"Total Pemasukan ({selected_year})", f"Rp {total_income_yr:,.0f}".replace(",", "."))
            col_b.metric(f"Total Pengeluaran ({selected_year})", f"Rp {total_expense_yr:,.0f}".replace(",", "."))
            col_c.metric("Net Cashflow", f"Rp {total_income_yr - total_expense_yr:,.0f}".replace(",", "."))
            
            st.divider()
            
            months_dict = {1:'Januari', 2:'Februari', 3:'Maret', 4:'April', 5:'Mei', 6:'Juni', 7:'Juli', 8:'Agustus', 9:'September', 10:'Oktober', 11:'November', 12:'Desember'}
            available_months = sorted(df_year['Bulan'].unique())
            selected_month = st.selectbox("Pilih Bulan", available_months, format_func=lambda x: months_dict.get(x, str(x)))
            
            df_month = df_year[df_year['Bulan'] == selected_month]
            
            total_income_mo = df_month[df_month['type'] == 1]['Jumlah'].sum()
            total_expense_mo = df_month[df_month['type'] == 0]['Jumlah'].sum()
            
            st.markdown(f"<h4 style='text-align: center; color: {text_color};'>Periode: {months_dict.get(selected_month)} {selected_year}</h4>", unsafe_allow_html=True)
            m1, m2 = st.columns(2)
            m1.metric("Pemasukan Bulan Ini", f"Rp {total_income_mo:,.0f}".replace(",", "."))
            m2.metric("Pengeluaran Bulan Ini", f"Rp {total_expense_mo:,.0f}".replace(",", "."))
            
            df_expense_mo = df_month[df_month['type'] == 0]
            if not df_expense_mo.empty:
                st.markdown("<h4>Pengeluaran per Kategori</h4>", unsafe_allow_html=True)
                cat_summary = df_expense_mo.groupby('Kategori')['Jumlah'].sum().reset_index().sort_values(by='Jumlah', ascending=False)
                max_val = cat_summary['Jumlah'].max()
                cat_summary['color_type'] = cat_summary['Jumlah'].apply(lambda x: '#FF3333' if x == max_val else (text_color))
                
                chart = alt.Chart(cat_summary).mark_bar(cornerRadiusTopLeft=2, cornerRadiusTopRight=2).encode(
                    x=alt.X('Kategori:N', sort='-y', title=None, axis=alt.Axis(labelAngle=-45, labelColor=chart_text)),
                    y=alt.Y('Jumlah:Q', title=None, axis=alt.Axis(labelColor=chart_text)),
                    color=alt.Color('color_type:N', scale=None)
                ).properties(height=300, background=chart_bg).configure_view(stroke=None).configure_axis(gridColor=chart_grid)
                
                st.altair_chart(chart, use_container_width=True)
                st.markdown("<h4>Rincian Transaksi</h4>", unsafe_allow_html=True)
                st.dataframe(df_expense_mo[['datetime', 'Kategori', 'Deskripsi', 'Jumlah']].sort_values(by='datetime', ascending=False), use_container_width=True)
            else:
                st.info("Tidak ada data pengeluaran untuk periode ini.")
        else:
            st.warning("Database transaksi kosong.")
    else:
        st.info("Silakan lakukan sinkronisasi data di Tab Konversi PDF.")

# --- FUNGSI DASHBOARD INVESTASI (TAB 3) ---
def render_investment():
    st.markdown("<h3>Portofolio Investasi</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: {sub_text}; font-size: 0.75rem; letter-spacing: 1px;'>[ ASSET ALLOCATION & PERFORMANCE ]</p>", unsafe_allow_html=True)
    st.write("")
    
    if os.path.exists(INV_DB):
        conn = get_inv_connection()
        df = pd.read_sql_query("SELECT * FROM STOCK_PORTFOLIO", conn)
        conn.close()
        
        if not df.empty:
            df_latest = df.sort_values('timestamp').groupby('symbol').tail(1).reset_index(drop=True)
            
            tot_buy = df_latest['buy_value'].sum()
            tot_mkt = df_latest['market_value'].sum()
            tot_unreal = df_latest['unrealized_rp'].sum()
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Modal (Buy Value)", f"Rp {tot_buy:,.0f}".replace(",", "."))
            col2.metric("Total Aset (Market Value)", f"Rp {tot_mkt:,.0f}".replace(",", "."))
            col3.metric("Total Unrealized P/L", f"Rp {tot_unreal:,.0f}".replace(",", "."))
            
            st.divider()
            
            st.markdown("<h4>Alokasi Aset (Market Value)</h4>", unsafe_allow_html=True)
            chart_donut = alt.Chart(df_latest).mark_arc(innerRadius=60).encode(
                theta=alt.Theta(field="market_value", type="quantitative"),
                color=alt.Color(field="symbol", type="nominal", legend=alt.Legend(title="Emiten", labelColor=chart_text, titleColor=chart_text)),
                tooltip=['symbol', 'market_value', 'unrealized_pct']
            ).properties(height=350, background=chart_bg).configure_view(stroke=None)
            
            st.altair_chart(chart_donut, use_container_width=True)
            
            st.markdown("<h4>Rincian Performa per Emiten</h4>", unsafe_allow_html=True)
            
            df_display = df_latest[['symbol', 'qty', 'avg_price', 'last_price', 'buy_value', 'market_value', 'unrealized_rp', 'unrealized_pct']].copy()
            df_display.columns = ['Emiten', 'Lot/Qty', 'Avg Price', 'Last Price', 'Modal (Rp)', 'Market Value (Rp)', 'Unrealized (Rp)', 'Unrealized (%)']
            
            format_dict = {
                'Lot/Qty': '{:,.0f}', 'Avg Price': '{:,.2f}', 'Last Price': '{:,.0f}',
                'Modal (Rp)': '{:,.0f}', 'Market Value (Rp)': '{:,.0f}',
                'Unrealized (Rp)': '{:,.0f}', 'Unrealized (%)': '{:,.2f}%'
            }
            
            def color_negative_red(val):
                if isinstance(val, (int, float)) and val < 0:
                    return 'color: #FF3333; font-weight: 600;'
                return f'color: {text_color}'
                
            st.dataframe(df_display.style.map(color_negative_red, subset=['Unrealized (Rp)', 'Unrealized (%)']).format(format_dict), use_container_width=True)
        else:
            st.info("Belum ada data Portofolio. Silakan upload file Statement Stockbit di Tab Konversi PDF.")
    else:
        st.warning("Database Investasi belum tersedia.")

# ================= PAGE 2: DASHBOARD (Protected) =================
with tab2:
    if not st.session_state.authenticated:
        st.markdown("<h3>Automasi Akses Terbatas</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: {sub_text}; font-size: 0.85rem;'>Masukkan password untuk membuka data keuangan.</p>", unsafe_allow_html=True)
        st.write("")
        col_p1, col_p2, col_p3 = st.columns([1, 2, 1])
        with col_p2:
            pwd_input = st.text_input("Password", type="password", key="dash_pwd")
            if st.button("Buka Akses", use_container_width=True):
                if pwd_input == "355443":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Password tidak valid.")
    else:
        col_k1, col_k2, col_k3 = st.columns([3, 1, 3])
        with col_k2:
            if st.button("Kunci Kembali", use_container_width=True, key="lock_dash"):
                st.session_state.authenticated = False
                st.rerun()
        st.write("")
        render_dashboard()

# ================= PAGE 3: INVESTASI (Protected) =================
with tab3:
    if not st.session_state.authenticated:
        st.markdown("<h3>Automasi Akses Terbatas</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: {sub_text}; font-size: 0.85rem;'>Masukkan password untuk membuka data portofolio.</p>", unsafe_allow_html=True)
        st.write("")
        col_i1, col_i2, col_i3 = st.columns([1, 2, 1])
        with col_i2:
            pwd_input_inv = st.text_input("Password", type="password", key="inv_pwd")
            if st.button("Buka Akses Portofolio", use_container_width=True):
                if pwd_input_inv == "355443":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Password tidak valid.")
    else:
        col_k1, col_k2, col_k3 = st.columns([3, 1, 3])
        with col_k2:
            if st.button("Kunci Kembali", use_container_width=True, key="lock_inv"):
                st.session_state.authenticated = False
                st.rerun()
        st.write("")
        render_investment()

# --- COPYRIGHT FOOTER ---
st.write("")
st.write("")
st.markdown(f"<p style='text-align: center; font-size: 0.75rem; color: {sub_text}; letter-spacing: 1px;'>&copy; 2026 rifqihasperi", unsafe_allow_html=True)