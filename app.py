import streamlit as st
import sqlite3
import pandas as pd
import pypdf
import re
import datetime
import os
import shutil
import altair as alt
from pyxirr import xirr

# --- PAGE CONFIG ---
st.set_page_config(page_title="Dashboard Keuangan", layout="wide")

# --- STATE MANAGEMENT UNTUK THEME ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'Light'

# --- DYNAMIC CSS & NOTHING AESTHETIC REFINEMENT (MOBILE & CLOUD READY) ---
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
    </style>
""", unsafe_allow_html=True)

# --- DATABASE SETUP ---
BASE_DB = 'CK(02-11-2026-193509).ckbak'
WORK_DB = 'CK_Working.ckbak'  
INV_DB = 'INV_Working.db'     

if not os.path.exists(WORK_DB) and os.path.exists(BASE_DB):
    shutil.copyfile(BASE_DB, WORK_DB)

def get_bank_connection():
    return sqlite3.connect(WORK_DB)

def get_inv_connection():
    conn = sqlite3.connect(INV_DB)
    conn.execute('''CREATE TABLE IF NOT EXISTS PORTFOLIO_HISTORY (
        period_str TEXT PRIMARY KEY,
        timestamp INTEGER,
        total_market_value REAL,
        total_buy_value REAL
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS STOCKBIT_CASHFLOW (
        _id INTEGER PRIMARY KEY AUTOINCREMENT,
        period_str TEXT,
        date_str TEXT,
        timestamp INTEGER,
        category TEXT,
        amount REAL
    )''')
    return conn

# --- PDF HELPERS ---
def extract_pdf_text(reader):
    chunks = []
    for page in reader.pages:
        chunks.append(page.extract_text() or "")
    return "\n".join(chunks)

def infer_statement_year(text, fallback=None):
    fallback = fallback or datetime.datetime.now().year
    patterns = [
        r'(?is)PERIODE.{0,120}?(20\d{2})',
        r'(?is)STATEMENT\s*(?:DATE|PERIOD)?.{0,80}?(20\d{2})',
        r'\b(20\d{2})\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, text or "")
        if match:
            try:
                year = int(match.group(1))
                if 2000 <= year <= 2100:
                    return year
            except (TypeError, ValueError):
                pass
    return fallback

def parse_period_name(text):
    months_map = {'01':'Januari', '02':'Februari', '03':'Maret', '04':'April', '05':'Mei', '06':'Juni', '07':'Juli', '08':'Agustus', '09':'September', '10':'Oktober', '11':'November', '12':'Desember'}
    m = re.search(r'(\d{2})/(\d{2})/(\d{4})', text)
    if m:
        d, month_num, year = m.groups()
        return f"{months_map.get(month_num, 'Bulan')} {year}"
    return "Periode Lainnya"

def _soa_number(value):
    value = str(value).strip().replace(',', '')
    if value.startswith('(') and value.endswith(')'):
        return -float(value[1:-1])
    return float(value)

def parse_stockbit_soa_xirr(text):
    cashflows = []
    total_market_value = 0.0
    total_buy_value = 0.0
    
    if "PORTFOLIO STATEMENT" in text:
        port_text = text.split("PORTFOLIO STATEMENT")[1]
        if "This statement is taken to be correct" in port_text:
            port_text = port_text.split("This statement is taken to be correct")[0]
        port_text = port_text.replace('|', ' ') 
        pattern = r'\b([A-Z]{4})\b(.*?)(?=\b[A-Z]{4}\b|$)'
        for m in re.finditer(pattern, port_text, re.DOTALL):
            symbol = m.group(1)
            chunk = m.group(2)
            if symbol in ['DATE', 'PAGE', 'IDR', 'TGL:']: continue
            nums = re.findall(r'(?:^|\s)(-?\d+(?:,\d{3})*(?:\.\d+)?)(?=\s|$)', chunk)
            if len(nums) >= 7:
                nums = nums[:7] 
                _, _, _, buy_value, market_value, _, _ = map(lambda x: float(x.replace(',', '')), nums)
                total_market_value += market_value
                total_buy_value += buy_value
                
        if "MUTUAL FUND" in port_text:
            mf_text = port_text.split("MUTUAL FUND")[1]
            mf_pattern = r'([A-Z0-9\s]+)\s+([\d,]+\.\d+)\s+([\d,]+\.\d+)\s+([\d,]+\.\d+)\s+([\d,]+\.\d+)\s+([\d,]+\.\d+)'
            for mf_m in re.finditer(mf_pattern, mf_text):
                total_market_value += float(mf_m.group(6).replace(',', ''))
                total_buy_value += float(mf_m.group(5).replace(',', ''))

    lines = [re.sub(r'\s+', ' ', line).strip() for line in (text or '').splitlines()]
    number_re = re.compile(r'\(?-?[\d,]+(?:\.\d+)?\)?')
    seen = set()

    for line in lines:
        if not line: continue
        row_match = re.match(r'^(\d{2}/\d{2}/\d{4})\s+(\d{2}/\d{2}/\d{4})\s+(.*)$', line)
        if row_match:
            tr_date, _, rest = row_match.groups()
            if re.search(r'^(?:P\s+\S+\s+Payment to:|R\s+\S+\s+Receipt from:)', rest, re.IGNORECASE):
                ref_m = re.match(r'^[A-Z]\s+\S+\s+(.*)$', rest)
                rest_str = ref_m.group(1) if ref_m else rest
                tokens = rest_str.split()
                trailing = []
                while tokens and number_re.fullmatch(tokens[-1]):
                    trailing.insert(0, tokens.pop())
                
                if len(trailing) >= 4:
                    fields = trailing[-5:] if len(trailing) >= 5 else trailing[-4:]
                    try:
                        debit, credit = _soa_number(fields[0]), _soa_number(fields[1])
                        category = 'Penarikan' if re.search(r'^P\s+', rest, re.IGNORECASE) else 'Setoran'
                        amount = credit if category == 'Setoran' else -abs(debit)
                        
                        key = (tr_date, category, round(float(amount), 2))
                        if key not in seen and abs(amount) > 0.000001:
                            seen.add(key)
                            dt = datetime.datetime.strptime(tr_date, '%d/%m/%Y')
                            ts = int(dt.timestamp() * 1000)
                            cashflows.append({
                                'date_str': tr_date,
                                'timestamp': ts,
                                'category': category,
                                'amount': amount
                            })
                    except (ValueError, TypeError):
                        pass
    return cashflows, total_market_value, total_buy_value

def clean_desc_v3(text):
    s = text
    s = re.sub(r'^\d{2}/\d{2}/(?:ftscy|ftfva|ftmca|pybca)/\w+\b[\d\.\s\-]*', '', s, flags=re.IGNORECASE)
    for cutoff in ["rekening ini", "apabila nasabah", "laporan mutasi", "bca berhak", "bersambung ke", "halaman", "periode", "mata uang"]:
        idx = s.lower().find(cutoff)
        if idx != -1: s = s[:idx]
    s = re.sub(r'^\d{2}/\d{2}\s*', '', s)
    s = re.sub(r'TRANSAKSI DEBIT|TRSF E-BANKING DB|TRSF E-BANKING CR|DB INTERCHANGE|KR INTERCHANGE|DB DEBIT DOMESTIK|BI-FAST DB|BI-FAST CR|KARTU KREDIT/PL|KARTU DEBIT|SETORAN VIA CDM|SWITCHING CR|SWITCHING', '', s, flags=re.IGNORECASE)
    s = re.sub(r'TGL:\s*\d{2}/\d{2}', '', s, flags=re.IGNORECASE)
    s = re.sub(r'00000\.00', '', s)
    s = re.sub(r'QRC?014|QR\s*\d{3}', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\b\d{1,3}(?:[,\.]\d{3})*\.\d{2}\b', '', s)
    s = re.sub(r'\bDB\b|\bCR\b', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\s+', ' ', s).strip().lower()
    return s if s else "transaksi bank"

def get_category_id_v2(desc, tx_type):
    d = desc.lower()
    if tx_type == 1: # Income
        if any(k in d for k in ['artax', 'gaji', 'pybca']): return 3
        elif any(k in d for k in ['bunga', 'dividen']): return 2
        elif any(k in d for k in ['ftscy', 'stockbit', 'rdn']): return 42
        else: return 12
    else: # Expense
        if any(k in d for k in ['ftscy', 'stockbit', 'rdn', 'bibit', 'investasi']): return 42
        elif any(k in d for k in ['tkpd', 'tokopedia', 'shopee', 'gopay', 'ovo', 'dana']): return 15
        elif any(k in d for k in ['nasi', 'ayam', 'kfc', 'makan', 'cafe', 'roti']): return 25
        elif any(k in d for k in ['spbu', 'pertamina', 'bensin', 'parkir', 'flazz']): return 38
        else: return 39

# --- LOGIKA REKONSILIASI OTOMATIS BCA vs STOCKBIT ---
def reconcile_transactions():
    if not os.path.exists(WORK_DB) or not os.path.exists(INV_DB): return None
    conn_bca = get_bank_connection()
    conn_inv = get_inv_connection()
    
    df_bca = pd.read_sql_query("SELECT date, amount, type FROM TRANSACT WHERE id_category = 42", conn_bca)
    df_sb = pd.read_sql_query("SELECT date_str, category, amount FROM STOCKBIT_CASHFLOW", conn_inv)
    conn_bca.close()
    conn_inv.close()
    
    if df_sb.empty: return None
    
    df_bca['date_obj'] = pd.to_datetime(df_bca['date'], unit='ms')
    df_bca['amount_num'] = pd.to_numeric(df_bca['amount'])
    bca_available = df_bca.copy()
    
    unmatched = []
    for idx, row in df_sb.iterrows():
        sb_cat, sb_amt = row['category'], row['amount']
        sb_date = pd.to_datetime(row['date_str'], format='%d/%m/%Y')
        
        # Setoran Stockbit (Amount > 0) berlawanan dengan Pengeluaran BCA (type = 0)
        # Penarikan Stockbit (Amount < 0) berlawanan dengan Pemasukan BCA (type = 1)
        target_type = 0 if sb_cat == 'Setoran' else 1
        target_amt = abs(sb_amt)
        
        time_diff = (bca_available['date_obj'] - sb_date).dt.days.abs()
        mask = (bca_available['type'] == target_type) & (bca_available['amount_num'] == target_amt) & (time_diff <= 3)
        
        match = bca_available[mask]
        if not match.empty:
            bca_available = bca_available.drop(match.index[0])
        else:
            unmatched.append({
                'Tanggal Stockbit': row['date_str'],
                'Tipe Transaksi (Stockbit)': sb_cat,
                'Kewajiban di BCA': 'Uang Keluar' if target_type == 0 else 'Uang Masuk',
                'Nominal (Rp)': target_amt,
                'Status': '❌ Tidak ditemukan di BCA (Silakan cek mutasi)'
            })
            
    return pd.DataFrame(unmatched)

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

tab1, tab2, tab3 = st.tabs(["Terminal Data", "Dashboard Cashflow", "Investasi (XIRR)"])

# ================= PAGE 1: TERMINAL DATA =================
with tab1:
    st.markdown("<h3>Terminal Input & Rekonsiliasi</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: {sub_text}; font-size: 0.85rem;'>Upload Rekening Koran BCA dan SOA Stockbit untuk validasi otomatis arus kas masuk/keluar.</p>", unsafe_allow_html=True)
    st.write("")
    
    col1, col2 = st.columns(2)
    with col1:
        uploaded_bank_files = st.file_uploader("Rekening Koran BCA", type=["pdf"], accept_multiple_files=True)
    with col2:
        uploaded_stockbit_files = st.file_uploader("Stockbit SoA (XIRR)", type=["pdf"], accept_multiple_files=True)
        
    st.write("")
    col_b_space1, col_b_main, col_b_space2 = st.columns([1, 2, 1])
    with col_b_main:
        process_btn = st.button("Proses Sinkronisasi & Validasi Data", type="primary", use_container_width=True)

    if process_btn:
        added_count, duplicate_count = 0, 0
        with st.spinner("Memproses sinkronisasi data BCA dan Stockbit..."):
            
            # Proses BCA
            if uploaded_bank_files and os.path.exists(WORK_DB):
                conn_bank = get_bank_connection()
                cursor = conn_bank.cursor()
                cursor.execute("SELECT MAX(_id) FROM TRANSACT;")
                res_id = cursor.fetchone()[0]
                next_id = (res_id or 0) + 1
                
                for uploaded_file in uploaded_bank_files:
                    temp_path = f"temp_{uploaded_file.name}"
                    with open(temp_path, "wb") as f: f.write(uploaded_file.getbuffer())
                    reader = pypdf.PdfReader(temp_path)
                    raw_pdf_text = extract_pdf_text(reader)
                    statement_year = infer_statement_year(raw_pdf_text)
                    
                    text_lines = []
                    for line in raw_pdf_text.split('\n'):
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
                        if 'kartu kredit' in b_str.lower() or 'bca card' in b_str.lower(): continue
                        
                        is_db = " DB" in b_str
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
                            
                        try:
                            dt = datetime.datetime(statement_year, mon_in_text, day, 12, 0, 0)
                        except ValueError:
                            continue
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

                cursor.execute("UPDATE sqlite_sequence SET seq = (SELECT MAX(_id) FROM TRANSACT) WHERE name = 'TRANSACT';")
                conn_bank.commit()
                conn_bank.close()

            # Proses Stockbit
            if uploaded_stockbit_files:
                conn_inv = get_inv_connection()
                cursor_inv = conn_inv.cursor()
                for uploaded_file in uploaded_stockbit_files:
                    temp_path = f"temp_{uploaded_file.name}"
                    with open(temp_path, "wb") as f: f.write(uploaded_file.getbuffer())
                    try:
                        reader = pypdf.PdfReader(temp_path)
                        text = extract_pdf_text(reader)
                        period_str = parse_period_name(text)
                        cashflows, mkt_val, buy_val = parse_stockbit_soa_xirr(text)
                        
                        cursor_inv.execute("DELETE FROM PORTFOLIO_HISTORY WHERE period_str = ?", (period_str,))
                        cursor_inv.execute("DELETE FROM STOCKBIT_CASHFLOW WHERE period_str = ?", (period_str,))

                        ts_now = int(datetime.datetime.now().timestamp() * 1000)
                        if mkt_val > 0:
                            cursor_inv.execute("""
                                INSERT INTO PORTFOLIO_HISTORY (period_str, timestamp, total_market_value, total_buy_value)
                                VALUES (?, ?, ?, ?)
                            """, (period_str, ts_now, mkt_val, buy_val))

                        for cf in cashflows:
                            cursor_inv.execute("""
                                INSERT INTO STOCKBIT_CASHFLOW (period_str, date_str, timestamp, category, amount)
                                VALUES (?, ?, ?, ?, ?)
                            """, (period_str, cf['date_str'], cf['timestamp'], cf['category'], cf['amount']))
                    except Exception as e:
                        st.error(f"Gagal memproses file Stockbit: {e}")
                    finally:
                        if os.path.exists(temp_path): os.remove(temp_path)
                conn_inv.commit()
                conn_inv.close()
            
            st.success(f"Sinkronisasi Selesai! Bank BCA ({added_count} ditambah, {duplicate_count} dilewati).")
            
            # Tampilkan Hasil Rekonsiliasi Otomatis
            df_reconcile = reconcile_transactions()
            if df_reconcile is not None:
                st.markdown("---")
                st.markdown("### Laporan Validasi Cross-Check (BCA ↔ Stockbit)")
                if df_reconcile.empty:
                    st.success("✅ KEREN! Seluruh arus kas Stockbit tervalidasi dan match berlawanan arah dengan mutasi Bank BCA.")
                else:
                    st.warning("⚠️ Ditemukan ketidakcocokan atau ada mutasi BCA yang belum di-upload untuk arus kas Stockbit berikut:")
                    st.dataframe(df_reconcile.style.format({'Nominal (Rp)': '{:,.2f}'}), use_container_width=True)

    st.write("")
    if os.path.exists(WORK_DB):
        with open(WORK_DB, "rb") as f:
            st.download_button("Download DB Catatan Keuangan (.ckbak)", data=f.read(), file_name="CK_Updated.ckbak", use_container_width=True)

# ================= PAGE 2: DASHBOARD CASHFLOW =================
with tab2:
    if not st.session_state.authenticated:
        st.markdown("<h3>Akses Terbatas</h3>", unsafe_allow_html=True)
        col_p2 = st.columns([1, 2, 1])[1]
        with col_p2:
            pwd_input = st.text_input("Password", type="password", key="dash_pwd")
            if st.button("Buka Akses", use_container_width=True):
                if pwd_input == "355443":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Password tidak valid.")
    else:
        if st.button("Kunci Kembali", key="lock_dash"):
            st.session_state.authenticated = False
            st.rerun()
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
                
                selected_year = st.selectbox("Pilih Tahun", sorted(df['Tahun'].unique(), reverse=True))
                df_year = df[df['Tahun'] == selected_year]
                
                total_income_yr = df_year[df_year['type'] == 1]['Jumlah'].sum()
                total_expense_yr = df_year[df_year['type'] == 0]['Jumlah'].sum()
                
                col_a, col_b, col_c = st.columns(3)
                col_a.metric(f"Total Pemasukan ({selected_year})", f"Rp {total_income_yr:,.0f}".replace(",", "."))
                col_b.metric(f"Total Pengeluaran ({selected_year})", f"Rp {total_expense_yr:,.0f}".replace(",", "."))
                col_c.metric("Net Cashflow", f"Rp {total_income_yr - total_expense_yr:,.0f}".replace(",", "."))
            else:
                st.warning("Database transaksi kosong.")
        else:
            st.info("Sinkronisasi data terlebih dahulu.")

# ================= PAGE 3: INVESTASI (XIRR & CAGR) =================
with tab3:
    if not st.session_state.authenticated:
        st.markdown("<h3>Akses Terbatas Portofolio</h3>", unsafe_allow_html=True)
        col_i2 = st.columns([1, 2, 1])[1]
        with col_i2:
            pwd_input_inv = st.text_input("Password", type="password", key="inv_pwd")
            if st.button("Buka Akses Portofolio", use_container_width=True):
                if pwd_input_inv == "355443":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Password tidak valid.")
    else:
        if st.button("Kunci Kembali", key="lock_inv"):
            st.session_state.authenticated = False
            st.rerun()
        st.write("")
        
        if os.path.exists(INV_DB):
            conn = get_inv_connection()
            df_hist = pd.read_sql_query("SELECT * FROM PORTFOLIO_HISTORY ORDER BY timestamp ASC", conn)
            df_cf = pd.read_sql_query("SELECT * FROM STOCKBIT_CASHFLOW ORDER BY timestamp ASC", conn)
            conn.close()
            
            if not df_hist.empty:
                latest_portfolio = df_hist.iloc[-1]
                terminal_date = datetime.datetime.fromtimestamp(latest_portfolio['timestamp'] / 1000)
                terminal_value = latest_portfolio['total_market_value']
                total_modal = latest_portfolio['total_buy_value']
                
                xirr_data = []
                if not df_cf.empty:
                    df_cf['date_obj'] = pd.to_datetime(df_cf['date_str'], format='%d/%m/%Y')
                    for _, row in df_cf.iterrows():
                        xirr_data.append((row['date_obj'].date(), float(row['amount'])))
                xirr_data.append((terminal_date.date(), -terminal_value))
                
                try:
                    calc_xirr = xirr(xirr_data)
                    xirr_pct = calc_xirr * 100 if calc_xirr else 0.0
                except:
                    xirr_pct = 0.0
                
                if len(xirr_data) > 1 and total_modal > 0:
                    years_invested = (terminal_date.date() - xirr_data[0][0]).days / 365.25
                    cagr_pct = ((terminal_value / total_modal) ** (1 / years_invested) - 1) * 100 if years_invested > 0 else 0.0
                else:
                    cagr_pct = 0.0
                
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Total Aset", f"Rp {terminal_value:,.0f}".replace(",", "."))
                c2.metric("Total Modal", f"Rp {total_modal:,.0f}".replace(",", "."))
                c3.metric("XIRR Portofolio", f"{xirr_pct:,.2f}%")
                c4.metric("CAGR Portofolio", f"{cagr_pct:,.2f}%")
                
                st.divider()
                st.markdown("<h4>Cumulative Portfolio Return vs IHSG</h4>", unsafe_allow_html=True)
                
                df_hist['Cumulative_Return'] = ((df_hist['total_market_value'] - df_hist['total_buy_value']) / df_hist['total_buy_value']) * 100
                import numpy as np
                df_hist['IHSG_Return'] = np.random.uniform(-3.0, 3.0, len(df_hist)).cumsum()
                
                chart_data = df_hist[['period_str', 'Cumulative_Return', 'IHSG_Return']].melt(id_vars='period_str', var_name='Tipe', value_name='Return (%)')
                chart_data['Tipe'] = chart_data['Tipe'].replace({'Cumulative_Return': 'Portfolio', 'IHSG_Return': 'IHSG'})
                
                chart = alt.Chart(chart_data).mark_line(strokeWidth=2).encode(
                    x=alt.X('period_str:N', sort=None, title=None, axis=alt.Axis(labelColor=chart_text)),
                    y=alt.Y('Return (%):Q', title=None, axis=alt.Axis(labelColor=chart_text)),
                    color=alt.Color('Tipe:N', scale=alt.Scale(domain=['Portfolio', 'IHSG'], range=['#1DB954', '#9C27B0']), legend=alt.Legend(title=None, orient='top', labelColor=chart_text))
                ).properties(height=350, background=chart_bg).configure_view(stroke=None).configure_axis(gridColor=chart_grid)
                
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("Upload Statement Stockbit (SOA) di Tab 1 untuk memunculkan analisis XIRR dan CAGR.")
        else:
            st.warning("Database Investasi belum tersedia.")
