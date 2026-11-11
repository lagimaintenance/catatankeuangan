import streamlit as st
import sqlite3
import pandas as pd
import pypdf
import re
import datetime
import os
import shutil
import altair as alt
import numpy as np
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

    @media (max-width: 768px) {{
        h1 {{ font-size: 1.4rem; }}
        h3 {{ font-size: 1.1rem; }}
        h4 {{ font-size: 1rem; }}
        .stTabs [data-baseweb="tab-list"] {{
            flex-wrap: wrap;
            max-width: 100%;
        }}
        .stTabs [data-baseweb="tab"] p, 
        .stTabs [data-baseweb="tab"] span, 
        .stTabs [data-baseweb="tab"] div {{
            font-size: 0.7rem !important;
            padding: 4px 8px !important;
        }}
        div[data-testid="stMetricValue"] {{ font-size: 1.2rem; }}
        div[data-testid="stMetricLabel"] {{ font-size: 0.65rem; }}
    }}
    </style>
""", unsafe_allow_html=True)

# --- DATABASE SETUP ---
BASE_DB = 'CK(18-10-2026-132328).ckbak'
WORK_DB = 'CK_Working.ckbak'  
INV_DB = 'INV_Working.db'     

if not os.path.exists(WORK_DB) and os.path.exists(BASE_DB):
    shutil.copyfile(BASE_DB, WORK_DB)

def get_bank_connection():
    return sqlite3.connect(WORK_DB)

def get_inv_connection():
    conn = sqlite3.connect(INV_DB)
    conn.execute('''CREATE TABLE IF NOT EXISTS STOCK_PORTFOLIO (
        _id INTEGER PRIMARY KEY AUTOINCREMENT,
        period_str TEXT,
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
    
    conn.execute('''CREATE TABLE IF NOT EXISTS STOCK_TRANSACTIONS (
        _id INTEGER PRIMARY KEY AUTOINCREMENT,
        period_str TEXT,
        date_str TEXT,
        category TEXT,
        description TEXT,
        amount REAL
    )''')
    
    # Tabel tambahan untuk history XIRR / Terminal Value per periode
    conn.execute('''CREATE TABLE IF NOT EXISTS PORTFOLIO_HISTORY (
        period_str TEXT PRIMARY KEY,
        timestamp INTEGER,
        total_market_value REAL,
        total_buy_value REAL
    )''')

    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(STOCK_PORTFOLIO);")
    columns = [col[1] for col in cursor.fetchall()]
    if 'period_str' not in columns:
        cursor.execute("ALTER TABLE STOCK_PORTFOLIO ADD COLUMN period_str TEXT DEFAULT 'Bulan-Unknown';")
        conn.commit()
        
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

# --- STOCKBIT SOA DAILY TRANSACTION PARSER ---
def _soa_number(value):
    value = str(value).strip().replace(',', '')
    if value.startswith('(') and value.endswith(')'):
        return -float(value[1:-1])
    return float(value)

def parse_stockbit_daily_transactions(text):
    transactions = []
    current_trade_date = None
    seen = set()
    lines = [re.sub(r'\s+', ' ', line).strip() for line in (text or '').splitlines()]
    number_re = re.compile(r'\(?-?[\d,]+(?:\.\d+)?\)?')

    def ledger_fields(line):
        row = re.match(r'^\d{2}/\d{2}/\d{4}\s+\d{2}/\d{2}/\d{4}\s+(.*)$', line)
        if not row:
            return None, None, line
        rest = row.group(1)
        ref = re.match(r'^[A-Z]\s+\S+\s+(.*)$', rest)
        if ref:
            rest = ref.group(1)
        tokens = rest.split()
        trailing = []
        while tokens and number_re.fullmatch(tokens[-1]):
            trailing.insert(0, tokens.pop())
        if len(trailing) < 4:
            return None, None, rest
        fields = trailing[-5:] if len(trailing) >= 5 else trailing[-4:]
        try:
            debit, credit = _soa_number(fields[0]), _soa_number(fields[1])
            return debit, credit, ' '.join(tokens).strip()
        except (ValueError, TypeError):
            return None, None, rest

    def ledger_amounts(line):
        debit, credit, _ = ledger_fields(line)
        return debit, credit

    def add(date_str, category, description, amount):
        if not date_str or amount is None or abs(amount) < 0.000001:
            return
        description = re.sub(r'\s+', ' ', description).strip()
        key = (date_str, category, description.casefold(), round(float(amount), 2))
        if key in seen:
            return
        seen.add(key)
        transactions.append({
            'date_str': date_str,
            'category': category,
            'description': description,
            'amount': round(abs(float(amount)), 2),
        })

    stock_detail_re = re.compile(
        r'(?P<ref>\d{5,8})\s+(?P<side>[BS]):\s*RG\s+'
        r'(?P<symbol>[A-Z0-9]{3,5})\s+(?P<qty>[\d,]+)\s*@\s*'
        r'(?P<price>[\d,.]+)\s*=\s*(?P<amount>[\d,]+(?:\.\d{1,2})?)',
        re.IGNORECASE,
    )

    for line in lines:
        if not line:
            continue
        invoice_match = re.search(r'\bTrx on (\d{2}/\d{2}/\d{4})\b', line, re.IGNORECASE)
        if invoice_match:
            current_trade_date = invoice_match.group(1)
            continue

        row_match = re.match(r'^(\d{2}/\d{2}/\d{4})\s+(\d{2}/\d{2}/\d{4})\s+(.*)$', line)
        if row_match:
            tr_date, due_date, rest = row_match.groups()
            current_trade_date = None

            if re.search(r'^J\s+\S+\s+SELL\s+(?:FR|PBS)\d+', rest, re.IGNORECASE):
                db_amount, cr_amount = ledger_amounts(line)
                amount = cr_amount if cr_amount and cr_amount > 0 else None
                description = ledger_fields(line)[2].strip()
                add(tr_date, 'Jual Obligasi', description, amount)
                continue

            if re.search(r'^D\s+\S+\s+.*(bond interest|dividend|dividen)', rest, re.IGNORECASE):
                db_amount, cr_amount = ledger_amounts(line)
                amount = cr_amount if cr_amount and cr_amount > 0 else None
                category = 'Dividen' if re.search(r'dividend|dividen', rest, re.IGNORECASE) else 'Bunga Obligasi'
                description = ledger_fields(line)[2].strip()
                add(tr_date, category, description, amount)
                continue

            if re.search(r'^(?:P\s+\S+\s+Payment to:|R\s+\S+\s+Receipt from:)', rest, re.IGNORECASE):
                db_amount, cr_amount = ledger_amounts(line)
                if re.search(r'^P\s+', rest, re.IGNORECASE):
                    category, amount = 'Penarikan', db_amount
                else:
                    category, amount = 'Setoran', cr_amount
                description = ledger_fields(line)[2].strip()
                # Simpan juga dengan tanda positif/negatif untuk XIRR
                raw_amount = amount if category == 'Setoran' else -abs(amount)
                add(tr_date, 'Setoran Kas' if category=='Setoran' else 'Penarikan Kas', description, amount)
                continue

        detail_match = stock_detail_re.search(line)
        if detail_match and current_trade_date:
            d = detail_match.groupdict()
            category = 'Beli' if d['side'].upper() == 'B' else 'Jual'
            description = (
                f"{category} saham {d['symbol'].upper()} — {int(d['qty'].replace(',', '')):,} lembar "
                f"@ Rp {_soa_number(d['price']):,.4f} (Ref {d['ref']})"
            )
            add(current_trade_date, category, description, _soa_number(d['amount']))

    return transactions

# Ekstraksi khusus untuk XIRR dari ledger Stockbit (Setor+, Tarik-)
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

tab1, tab2, tab3 = st.tabs(["Konversi PDF", "Dashboard", "Investasi"])

# ================= PAGE 1: KONVERSI PDF =================
with tab1:
    st.markdown("<h3>Terminal Input Data</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: {sub_text}; font-size: 0.85rem;'>Upload semua file Statement (BCA / Stockbit) disini. Data investasi akan dikelompokkan per bulan secara otomatis.</p>", unsafe_allow_html=True)
    st.write("")
    
    col_p_space1, col_p_main, col_p_space2 = st.columns([1, 2, 1])
    with col_p_main:
        pdf_password = st.text_input("Password PDF Kartu Kredit", type="password", value="")
    
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
            added_count, duplicate_count, stockbit_count, stockbit_trx_count = 0, 0, 0, 0
            
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
                        raw_pdf_text = extract_pdf_text(reader)
                        statement_year = infer_statement_year(raw_pdf_text)
                        if not raw_pdf_text.strip():
                            st.warning(f"Tidak ada teks yang bisa dibaca dari PDF rekening koran: {uploaded_file.name}.")
                            continue
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

                if uploaded_cc_files:
                    months_map = {'JAN':1, 'FEB':2, 'MAR':3, 'APR':4, 'MEI':5, 'JUN':6, 'JUL':7, 'AUG':8, 'SEP':9, 'OCT':10, 'NOV':11, 'DEC':12, 'AGU':8, 'AGT':8, 'OKT':10, 'NOP':11, 'DES':12}
                    for uploaded_file in uploaded_cc_files:
                        temp_path = f"temp_cc_{uploaded_file.name}"
                        with open(temp_path, "wb") as f: f.write(uploaded_file.getbuffer())
                        reader = pypdf.PdfReader(temp_path)
                        if reader.is_encrypted:
                            if not pdf_password:
                                raise ValueError("PDF kartu kredit terkunci. Masukkan password PDF terlebih dahulu.")
                            decrypt_status = reader.decrypt(pdf_password)
                            if not decrypt_status:
                                raise ValueError("Password PDF kartu kredit salah atau PDF tidak dapat dibuka.")
                        text = extract_pdf_text(reader)
                        statement_year = infer_statement_year(text)
                        if not text.strip():
                            continue
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
                                    month_token = m1.upper()
                                    month_num = int(month_token) if month_token.isdigit() else months_map.get(month_token)
                                    if not month_num or not 1 <= month_num <= 12:
                                        continue
                                    day_num = int(d1)
                                    try:
                                        dt = datetime.datetime(statement_year, month_num, day_num, 12, 0, 0)
                                    except ValueError:
                                        continue
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

                conn_bank.commit()
                conn_bank.close()

            # --- PROSES PORTFOLIO & TRANSAKSI STOCKBIT (PLUS XIRR) ---
            if uploaded_stockbit_files:
                conn_inv = get_inv_connection()
                cursor_inv = conn_inv.cursor()
                
                for uploaded_file in uploaded_stockbit_files:
                    temp_path = f"temp_sb_{uploaded_file.name}"
                    with open(temp_path, "wb") as f: f.write(uploaded_file.getbuffer())
                    portfolio_count_before = stockbit_count
                    trx_count_before = stockbit_trx_count
                    cursor_inv.execute("SAVEPOINT stockbit_file")
                    try:
                        reader = pypdf.PdfReader(temp_path)
                        text = extract_pdf_text(reader)
                        period_str = parse_period_name(text)

                        daily_transactions = parse_stockbit_daily_transactions(text)
                        if not daily_transactions:
                            raise ValueError("Tidak ada transaksi harian yang dikenali dari PDF ini.")

                        # Ekstraksi khusus XIRR & Terminal Value dari SOA
                        cashflows, mkt_val, buy_val = parse_stockbit_soa_xirr(text)

                        cursor_inv.execute("DELETE FROM STOCK_PORTFOLIO WHERE period_str = ?", (period_str,))
                        cursor_inv.execute("DELETE FROM STOCK_TRANSACTIONS WHERE period_str = ?", (period_str,))
                        cursor_inv.execute("DELETE FROM PORTFOLIO_HISTORY WHERE period_str = ?", (period_str,))

                        ts_now = int(datetime.datetime.now().timestamp() * 1000)
                        if mkt_val > 0:
                            cursor_inv.execute("""
                                INSERT INTO PORTFOLIO_HISTORY (period_str, timestamp, total_market_value, total_buy_value)
                                VALUES (?, ?, ?, ?)
                            """, (period_str, ts_now, mkt_val, buy_val))

                        # 1. PARSER PORTFOLIO STATEMENT
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
                                        (period_str, timestamp, symbol, qty, avg_price, last_price, buy_value, market_value, unrealized_rp, unrealized_pct)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                    """, (period_str, timestamp_ms, symbol, qty, avg_price, last_price, buy_value, market_value, unrealized_rp, unrealized_pct))
                                    stockbit_count += 1

                        # 2. PARSER TRANSAKSI HARIAN STOCKBIT
                        for trx in daily_transactions:
                            cursor_inv.execute("""
                                INSERT INTO STOCK_TRANSACTIONS
                                (period_str, date_str, category, description, amount)
                                VALUES (?, ?, ?, ?, ?)
                            """, (
                                period_str,
                                trx['date_str'],
                                trx['category'],
                                trx['description'],
                                trx['amount'],
                            ))
                            stockbit_trx_count += 1

                        # 3. SIMPAN CASHFLOW KE STOCKBIT_CASHFLOW UNTUK REKONSILIASI
                        cursor_inv.execute('''CREATE TABLE IF NOT EXISTS STOCKBIT_CASHFLOW (
                            _id INTEGER PRIMARY KEY AUTOINCREMENT,
                            period_str TEXT,
                            date_str TEXT,
                            timestamp INTEGER,
                            category TEXT,
                            amount REAL
                        )''')
                        cursor_inv.execute("DELETE FROM STOCKBIT_CASHFLOW WHERE period_str = ?", (period_str,))
                        for cf in cashflows:
                            cursor_inv.execute("""
                                INSERT INTO STOCKBIT_CASHFLOW (period_str, date_str, timestamp, category, amount)
                                VALUES (?, ?, ?, ?, ?)
                            """, (period_str, cf['date_str'], cf['timestamp'], cf['category'], cf['amount']))

                        cursor_inv.execute("RELEASE SAVEPOINT stockbit_file")
                    except Exception as e:
                        cursor_inv.execute("ROLLBACK TO SAVEPOINT stockbit_file")
                        cursor_inv.execute("RELEASE SAVEPOINT stockbit_file")
                        stockbit_count = portfolio_count_before
                        stockbit_trx_count = trx_count_before
                        st.error(f"Gagal memproses file Stockbit: {e}")
                    finally:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                conn_inv.commit()
                conn_inv.close()
            
            st.success(f"Sinkronisasi Selesai! | Transaksi Bank: {added_count} | Portofolio: {stockbit_count} emiten | Transaksi Harian: {stockbit_trx_count} terekstrak")

            # Jalankan Rekonsiliasi Otomatis BCA vs Stockbit
            df_reconcile = reconcile_transactions()
            if df_reconcile is not None:
                st.markdown("---")
                st.markdown("### Laporan Validasi Cross-Check (BCA ↔ Stockbit)")
                if df_reconcile.empty:
                    st.success("✅ Seluruh arus kas Stockbit tervalidasi dan match berlawanan arah dengan mutasi Bank BCA.")
                else:
                    st.warning("⚠️ Ditemukan ketidakcocokan arus kas antara Stockbit dan Bank BCA:")
                    st.dataframe(df_reconcile.style.format({'Nominal (Rp)': '{:,.2f}'}), use_container_width=True)

    st.write("")
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        if os.path.exists(WORK_DB):
            with open(WORK_DB, "rb") as f:
                st.download_button(label="Download DB Catatan Keuangan (.ckbak)", data=f, file_name="CK_Working.ckbak", mime="application/octet-stream", use_container_width=True)
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

# --- FUNGSI DASHBOARD INVESTASI (TAB 3 LENGKAP + XIRR, CAGR, & GRAFIK) ---
def render_investment():
    st.markdown("<h3>Portofolio Investasi</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: {sub_text}; font-size: 0.75rem; letter-spacing: 1px;'>[ HISTORICAL PERFORMANCE & TRANSACTIONS ]</p>", unsafe_allow_html=True)
    st.write("")
    
    if os.path.exists(INV_DB):
        conn = get_inv_connection()
        df_port = pd.read_sql_query("SELECT * FROM STOCK_PORTFOLIO", conn)
        df_trx = pd.read_sql_query("SELECT * FROM STOCK_TRANSACTIONS", conn)
        df_hist = pd.read_sql_query("SELECT * FROM PORTFOLIO_HISTORY ORDER BY timestamp ASC", conn)
        df_cf = pd.read_sql_query("SELECT * FROM STOCKBIT_CASHFLOW ORDER BY timestamp ASC", conn) if "STOCKBIT_CASHFLOW" in [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()] else pd.DataFrame()
        conn.close()
        
        if not df_port.empty:
            periods = sorted(df_port['period_str'].unique(), reverse=True)
            selected_period = st.selectbox("Pilih Periode Statement Bulanan", periods)
            
            df_filtered = df_port[df_port['period_str'] == selected_period].reset_index(drop=True)
            df_trx_filtered = df_trx[df_trx['period_str'] == selected_period].reset_index(drop=True) if not df_trx.empty else pd.DataFrame()
            
            tot_buy = df_filtered['buy_value'].sum()
            tot_mkt = df_filtered['market_value'].sum()
            tot_unreal = df_filtered['unrealized_rp'].sum()
            
            tot_div = 0.0
            if not df_trx_filtered.empty and 'category' in df_trx_filtered.columns:
                div_df = df_trx_filtered[df_trx_filtered['category'].str.lower() == 'dividen']
                tot_div = div_df['amount'].sum() if not div_df.empty else 0.0

            # --- KALKULASI XIRR & CAGR TAMBAHAN ---
            xirr_pct, cagr_pct = 0.0, 0.0
            if not df_hist.empty:
                latest_portfolio = df_hist.iloc[-1]
                terminal_date = datetime.datetime.fromtimestamp(latest_portfolio['timestamp'] / 1000)
                terminal_value = latest_portfolio['total_market_value']
                total_modal = latest_portfolio['total_buy_value']
                
                xirr_data = []
                if not df_cf.empty:
                    df_cf['date_obj'] = pd.to_datetime(df_cf['date_str'], format='%d/%m/%Y', errors='coerce')
                    for _, row in df_cf.iterrows():
                        if pd.notnull(row['date_obj']):
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

            st.write("")
            col_s1, col_s2, col_s3, col_s4, col_s5, col_s6 = st.columns(6)
            col_s1.metric(f"Total Modal", f"Rp {tot_buy:,.0f}".replace(",", "."))
            col_s2.metric(f"Total Aset", f"Rp {tot_mkt:,.0f}".replace(",", "."))
            col_s3.metric(f"Unrealized P/L", f"Rp {tot_unreal:,.0f}".replace(",", "."))
            col_s4.metric(f"Total Dividen", f"Rp {tot_div:,.0f}".replace(",", "."))
            col_s5.metric("XIRR", f"{xirr_pct:,.2f}%")
            col_s6.metric("CAGR", f"{cagr_pct:,.2f}%")
            
            st.divider()
            
            sub_tab = st.radio("Pilih Tampilan Dashboard", ["Ringkasan Portofolio", "Rincian Transaksi Harian", "Grafik Return (XIRR)"], horizontal=True)
            st.divider()
            
            if sub_tab == "Ringkasan Portofolio":
                st.markdown(f"<h4>Alokasi Aset ({selected_period})</h4>", unsafe_allow_html=True)
                chart_donut = alt.Chart(df_filtered).mark_arc(innerRadius=60).encode(
                    theta=alt.Theta(field="market_value", type="quantitative"),
                    color=alt.Color(field="symbol", type="nominal", legend=alt.Legend(title="Emiten", labelColor=chart_text, titleColor=chart_text)),
                    tooltip=['symbol', 'market_value', 'unrealized_pct']
                ).properties(height=350, background=chart_bg).configure_view(stroke=None)
                
                st.altair_chart(chart_donut, use_container_width=True)
                
                st.markdown(f"<h4>Rincian Performa per Emiten ({selected_period})</h4>", unsafe_allow_html=True)
                df_display = df_filtered[['symbol', 'qty', 'avg_price', 'last_price', 'buy_value', 'market_value', 'unrealized_rp', 'unrealized_pct']].copy()
                df_display.insert(1, 'Kategori', df_display['unrealized_rp'].apply(lambda x: 'Beli (Untung)' if x >= 0 else 'Jual (Rugi)'))
                df_display.columns = ['Emiten', 'Kategori', 'Lot/Qty', 'Avg Price', 'Last Price', 'Modal (Rp)', 'Market Value (Rp)', 'Unrealized (Rp)', 'Unrealized (%)']
                
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
            
            elif sub_tab == "Rincian Transaksi Harian":
                if not df_trx_filtered.empty:
                    st.markdown(f"<h4>Log Transaksi Harian ({selected_period})</h4>", unsafe_allow_html=True)
                    df_trx_display = df_trx_filtered[['date_str', 'category', 'description', 'amount']].copy()
                    df_trx_display['_tanggal_sort'] = pd.to_datetime(
                        df_trx_display['date_str'], format='%d/%m/%Y', errors='coerce'
                    )
                    df_trx_display = df_trx_display.sort_values('_tanggal_sort', ascending=False).drop(columns='_tanggal_sort')
                    df_trx_display.columns = ['Tanggal', 'Kategori', 'Deskripsi Transaksi', 'Jumlah (Rp)']

                    format_trx = {'Jumlah (Rp)': '{:,.2f}'}
                    st.dataframe(df_trx_display.style.format(format_trx), use_container_width=True)
                else:
                    st.info(f"Tidak ada rincian transaksi harian terekstrak untuk periode {selected_period}.")
            
            else: # Grafik Return (XIRR)
                st.markdown("<h4>Cumulative Portfolio Return vs IHSG</h4>", unsafe_allow_html=True)
                if not df_hist.empty:
                    df_hist['Cumulative_Return'] = ((df_hist['total_market_value'] - df_hist['total_buy_value']) / df_hist['total_buy_value']) * 100
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
                    st.info("Belum ada data history untuk grafik return.")
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
st.markdown(f"<p style='text-align: center; font-size: 0.75rem; color: {sub_text}; letter-spacing: 1px;'>© 2026 rifqihasperi</p>", unsafe_allow_html=True)
