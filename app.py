import streamlit as st
import sqlite3
import pandas as pd
import pypdf
import re
import datetime
import calendar
import os
import shutil
import altair as alt
import numpy as np
from pyxirr import xirr
from streamlit_gsheets import GSheetsConnection

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
    primary_btn_bg = "#111111"
    primary_btn_text = "#FFFFFF"
    chart_bg = "#FFFFFF"
    chart_text = "#333333"
    chart_grid = "#E5E5E5"
    shadow_box = "0 4px 12px rgba(0, 0, 0, 0.04)"
    mono_palette = ["#111111", "#2B2B2B", "#454545", "#5E5E5E", "#787878", "#919191", "#ABABAB", "#C4C4C4", "#DCDCDC"]
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
    primary_btn_bg = "#F5F5F5"
    primary_btn_text = "#111111"
    chart_bg = "#2A2D32"
    chart_text = "#CCCCCC"
    chart_grid = "#3A3D42"
    shadow_box = "0 4px 12px rgba(0, 0, 0, 0.2)"
    mono_palette = ["#F5F5F5", "#DCDCDC", "#C2C2C2", "#A8A8A8", "#8E8E8E", "#757575", "#5C5C5C", "#454545", "#333333"]

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
        font-size: 1.45rem;
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
    
    /* --- UNIFIED BUTTON STYLING (st.button, st.download_button, File Uploader Browse) --- */
    .stButton button,
    .stDownloadButton button,
    div[data-testid="stFileUploader"] button,
    div[data-testid="stFileUploaderDropzone"] button {{
        background-color: {card_bg} !important;
        color: {text_color} !important;
        border: 1px solid {border_color} !important;
        border-radius: 4px !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
        box-shadow: {shadow_box};
        transition: all 0.15s ease;
    }}
    .stButton button p,
    .stButton button span,
    .stDownloadButton button p,
    .stDownloadButton button span,
    div[data-testid="stFileUploader"] button p,
    div[data-testid="stFileUploader"] button span,
    div[data-testid="stFileUploaderDropzone"] button p,
    div[data-testid="stFileUploaderDropzone"] button span {{
        color: {text_color} !important;
    }}
    .stButton button:hover,
    .stDownloadButton button:hover,
    div[data-testid="stFileUploader"] button:hover,
    div[data-testid="stFileUploaderDropzone"] button:hover {{
        background-color: {primary_btn_bg} !important;
        color: {primary_btn_text} !important;
        border-color: {primary_btn_bg} !important;
    }}
    .stButton button:hover p,
    .stButton button:hover span,
    .stDownloadButton button:hover p,
    .stDownloadButton button:hover span,
    div[data-testid="stFileUploader"] button:hover p,
    div[data-testid="stFileUploader"] button:hover span {{
        color: {primary_btn_text} !important;
    }}

    /* Primary Action Button */
    .stButton button[kind="primary"] {{
        background-color: {primary_btn_bg} !important;
        color: {primary_btn_text} !important;
        border: 1px solid {primary_btn_bg} !important;
        text-transform: uppercase;
    }}
    .stButton button[kind="primary"] p,
    .stButton button[kind="primary"] span {{
        color: {primary_btn_text} !important;
    }}
    .stButton button[kind="primary"]:hover {{
        opacity: 0.88;
    }}

    /* Input & Password Eye Toggle Button */
    .stTextInput input, .stSelectbox select {{
        background-color: {input_bg} !important;
        color: {text_color} !important;
        border: 1px solid {border_color} !important;
        border-radius: 4px !important;
        font-size: 0.85rem;
    }}
    div[data-testid="stTextInput"] button {{
        background-color: {input_bg} !important;
        color: {text_color} !important;
        border: none !important;
    }}
    div[data-testid="stTextInput"] button svg {{
        fill: {text_color} !important;
        color: {text_color} !important;
    }}

    /* File Uploader Dropzone & Uploaded File Item */
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
    div[data-testid="stFileUploader"] section svg {{
        fill: {text_color} !important;
        color: {text_color} !important;
    }}
    div[data-testid="stFileUploaderFile"] {{
        background-color: {tab_bg} !important;
        border: 1px solid {border_color} !important;
        border-radius: 4px !important;
        padding: 4px 8px !important;
    }}
    div[data-testid="stFileUploaderFile"] span,
    div[data-testid="stFileUploaderFile"] small,
    div[data-testid="stFileUploaderFile"] div {{
        color: {text_color} !important;
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

# --- INDONESIAN NUMBER FORMATTING HELPERS ---
def fmt_int(val):
    if val is None or pd.isna(val):
        return "0"
    n = int(round(float(val)))
    sign = "-" if n < 0 else ""
    return f"{sign}{abs(n):,}".replace(",", ".")

def fmt_signed_int(val):
    if val is None or pd.isna(val):
        return "0"
    n = int(round(float(val)))
    if n > 0:
        return f"+{n:,}".replace(",", ".")
    elif n < 0:
        return f"-{abs(n):,}".replace(",", ".")
    return "0"

def fmt_rp(val):
    if val is None or pd.isna(val):
        return "Rp 0"
    n = int(round(float(val)))
    if n < 0:
        return f"-Rp {abs(n):,}".replace(",", ".")
    return f"Rp {n:,}".replace(",", ".")

def fmt_dec(val, decimals=2):
    if val is None or pd.isna(val):
        return "0,00"
    f = float(val)
    sign = "-" if f < 0 else ""
    formatted = f"{abs(f):,.{decimals}f}"
    # Swap US (1,234.56) -> ID (1.234,56)
    return sign + formatted.replace(",", "X").replace(".", ",").replace("X", ".")

def fmt_pct(val, signed=False):
    if val is None or pd.isna(val):
        return "0,00%"
    f = float(val)
    prefix = "+" if (signed and f > 0) else ("-" if f < 0 else "")
    formatted = f"{abs(f):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{prefix}{formatted}%"

def fmt_trx_amount(val):
    if val is None or pd.isna(val):
        return "0"
    f = float(val)
    if abs(f - round(f)) < 0.005:
        return fmt_int(round(f))
    return fmt_dec(f, 2)

# --- DATABASE & GOOGLE SHEETS SETUP ---
BASE_DB = 'CK(18-10-2026-132328).ckbak'
WORK_DB = 'CK_Working.ckbak'
INV_DB = 'INV_Working.db'

TRANSACT_COLS = ['_id', 'id_category', 'desc', 'type', 'date', 'amount']
PORT_COLS = [
    'period_str', 'timestamp', 'symbol', 'qty', 'avg_price', 'last_price',
    'buy_value', 'market_value', 'unrealized_rp', 'unrealized_pct',
    'total_modal', 'total_aset', 'total_unrealized_rp', 'equity_nab'
]
TRX_COLS = ['period_str', 'date_str', 'category', 'description', 'amount']

if not os.path.exists(WORK_DB) and os.path.exists(BASE_DB):
    shutil.copyfile(BASE_DB, WORK_DB)

conn_gsheets = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=60, show_spinner=False)
def read_worksheet_cached(sheet_name):
    df = conn_gsheets.read(worksheet=sheet_name, ttl=0)
    return df.dropna(how='all')

def get_sheet_df(sheet_name, expected_cols):
    try:
        df = read_worksheet_cached(sheet_name).copy()
        if df.empty:
            return pd.DataFrame(columns=expected_cols)
        numeric_defaults = {'total_modal', 'total_aset', 'total_unrealized_rp', 'equity_nab'}
        for col in expected_cols:
            if col not in df.columns:
                df[col] = 0.0 if col in numeric_defaults else ""
        return df[expected_cols]
    except Exception as e:
        st.warning(f"Catatan koneksi sheet '{sheet_name}': pastikan tab '{sheet_name}' sudah dibuat di Google Sheets. ({e})")
        return pd.DataFrame(columns=expected_cols)

def save_sheet_df(df, sheet_name, expected_cols):
    out_df = df.reindex(columns=expected_cols).copy() if not df.empty else pd.DataFrame(columns=expected_cols)
    out_df = out_df.fillna("")
    try:
        conn_gsheets.update(worksheet=sheet_name, data=out_df)
    except Exception:
        conn_gsheets.create(worksheet=sheet_name, data=out_df)
    read_worksheet_cached.clear()

def get_bank_connection():
    return sqlite3.connect(WORK_DB)

def get_category_map():
    if os.path.exists(WORK_DB):
        conn = get_bank_connection()
        df_cat = pd.read_sql_query("SELECT _id, NAME FROM CATEGORY", conn)
        conn.close()
        return dict(zip(df_cat['_id'].astype(int), df_cat['NAME']))
    return {}

def load_or_seed_transact():
    df_gs = get_sheet_df("TRANSACT", TRANSACT_COLS)
    if df_gs.empty and os.path.exists(WORK_DB):
        conn = get_bank_connection()
        df_local = pd.read_sql_query("SELECT _id, id_category, desc, type, date, amount FROM TRANSACT", conn)
        conn.close()
        if not df_local.empty:
            save_sheet_df(df_local, "TRANSACT", TRANSACT_COLS)
            return df_local
    return df_gs

def sync_work_db_from_df(df_transact):
    if not os.path.exists(WORK_DB) or df_transact.empty:
        return
    conn = get_bank_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM TRANSACT;")
    rows = [
        (
            int(float(r['_id'])),
            int(float(r['id_category'])),
            str(r['desc']),
            int(float(r['type'])),
            int(float(r['date'])),
            str(int(round(float(r['amount']))))
        )
        for _, r in df_transact.iterrows()
    ]
    cursor.executemany(
        "INSERT INTO TRANSACT (_id, id_category, desc, type, date, amount) VALUES (?, ?, ?, ?, ?, ?)",
        rows
    )
    conn.commit()
    conn.close()

def sync_inv_db_from_dfs(df_port, df_trx):
    conn = sqlite3.connect(INV_DB)
    df_port.to_sql("STOCK_PORTFOLIO", conn, if_exists="replace", index=False)
    df_trx.to_sql("STOCK_TRANSACTIONS", conn, if_exists="replace", index=False)
    conn.commit()
    conn.close()

# --- PDF HELPERS ---
def extract_pdf_text(reader):
    chunks = []
    for page in reader.pages:
        chunks.append(page.extract_text() or "")
    return "\n".join(chunks)

def _mult_matrix(m1, m2):
    return [
        m1[0] * m2[0] + m1[1] * m2[2],
        m1[0] * m2[1] + m1[1] * m2[3],
        m1[2] * m2[0] + m1[3] * m2[2],
        m1[2] * m2[1] + m1[3] * m2[3],
        m1[4] * m2[0] + m1[5] * m2[2] + m2[4],
        m1[4] * m2[1] + m1[5] * m2[3] + m2[5],
    ]

def extract_pdf_visual_lines(reader):
    """Mengekstrak teks PDF per baris visual berdasarkan koordinat (Y, X) agar kolom tabel selalu sejajar."""
    all_lines = []
    for page in reader.pages:
        fragments = []

        def visitor(text, cm, tm, font_dict, font_size):
            if not text or not text.strip():
                return
            mat = _mult_matrix(tm, cm)
            fragments.append((float(mat[5]), float(mat[4]), text))

        try:
            page.extract_text(visitor_text=visitor)
        except TypeError:
            raw = page.extract_text() or ""
            all_lines.extend([l.strip() for l in raw.splitlines() if l.strip()])
            continue

        if not fragments:
            raw = page.extract_text() or ""
            all_lines.extend([l.strip() for l in raw.splitlines() if l.strip()])
            continue

        fragments.sort(key=lambda item: (-item[0], item[1]))

        rows = []
        y_tolerance = 3.2
        for y, x, txt in fragments:
            placed = False
            for r in rows:
                if abs(r['y'] - y) <= y_tolerance:
                    r['items'].append((x, txt))
                    placed = True
                    break
            if not placed:
                rows.append({'y': y, 'items': [(x, txt)]})

        for r in rows:
            r['items'].sort(key=lambda item: item[0])
            parts = []
            for _, txt in r['items']:
                clean_t = re.sub(r'\s+', ' ', txt).strip()
                if clean_t:
                    parts.append(clean_t)
            line_str = " ".join(parts).strip()
            if line_str:
                all_lines.append(line_str)

    return "\n".join(all_lines)

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

MONTHS_ID = {
    '01': 'Januari', '02': 'Februari', '03': 'Maret', '04': 'April',
    '05': 'Mei', '06': 'Juni', '07': 'Juli', '08': 'Agustus',
    '09': 'September', '10': 'Oktober', '11': 'November', '12': 'Desember'
}

def date_str_to_period_name(date_str):
    m = re.match(r'^(\d{2})/(\d{2})/(\d{4})$', str(date_str).strip())
    if m:
        _, month_num, year = m.groups()
        return f"{MONTHS_ID.get(month_num, 'Bulan')} {year}"
    return "Periode Lainnya"

def parse_period_name(text):
    range_m = re.search(r'(\d{2})/(\d{2})/(\d{4})\s*-\s*(\d{2})/(\d{2})/(\d{4})', text or "")
    if range_m:
        _, _, _, _, month_num, year = range_m.groups()
        return f"{MONTHS_ID.get(month_num, 'Bulan')} {year}"
    m = re.search(r'(\d{2})/(\d{2})/(\d{4})', text or "")
    if m:
        _, month_num, year = m.groups()
        return f"{MONTHS_ID.get(month_num, 'Bulan')} {year}"
    return "Periode Lainnya"

def period_str_to_end_date(period_str):
    months_rev = {
        'januari': 1, 'februari': 2, 'maret': 3, 'april': 4, 'mei': 5, 'juni': 6,
        'juli': 7, 'agustus': 8, 'september': 9, 'oktober': 10, 'november': 11, 'desember': 12
    }
    parts = str(period_str).strip().split()
    if len(parts) == 2 and parts[0].lower() in months_rev and parts[1].isdigit():
        m = months_rev[parts[0].lower()]
        y = int(parts[1])
        last_day = calendar.monthrange(y, m)[1]
        end_dt = datetime.date(y, m, last_day)
        return min(end_dt, datetime.date.today())
    return datetime.date.today()

# --- STOCKBIT SOA & ANNUAL REPORT PARSERS ---
def _soa_number(value):
    value = str(value).strip().replace(',', '')
    if value.startswith('(') and value.endswith(')'):
        return -float(value[1:-1])
    return float(value)

def parse_stockbit_portfolio(visual_text, raw_text, period_str):
    rows = []
    if not visual_text or "PORTFOLIO STATEMENT" not in visual_text.upper():
        return rows

    lines = [l.strip() for l in visual_text.splitlines() if l.strip()]

    equity_nab = 0.0
    for line in lines:
        m_nab = re.search(r'\bEquity\s+NAB\s+(-?[\d,]+(?:\.\d+)?)', line, re.IGNORECASE)
        if m_nab:
            try:
                equity_nab = _soa_number(m_nab.group(1))
                break
            except (ValueError, TypeError):
                pass
    if equity_nab == 0.0 and raw_text:
        m_nab_raw = re.search(r'Equity\s+NAB\s*\|?\s*(-?[\d,]+(?:\.\d+)?)', raw_text, re.IGNORECASE)
        if m_nab_raw:
            try:
                equity_nab = _soa_number(m_nab_raw.group(1))
            except (ValueError, TypeError):
                pass

    in_portfolio_section = False
    in_stocks_table = False
    total_modal = 0.0
    total_aset = 0.0
    total_unrealized_rp = 0.0

    excluded_tickers = {'DATE', 'PAGE', 'TGL:', 'TBK.', 'BANK', 'CASH', 'DAYS', 'SELL', 'OPEN', 'HIGH', 'GAIN', 'LOSS', 'NOTE', 'SPEC', 'TOTAL'}

    for line in lines:
        upper_line = line.upper()
        if "PORTFOLIO STATEMENT" in upper_line:
            in_portfolio_section = True
            continue
        if not in_portfolio_section:
            continue
        if "THIS STATEMENT IS TAKEN TO BE CORRECT" in upper_line:
            break

        if re.search(r'\bStocks\b', line) and re.search(r'\bBuying\b', line, re.IGNORECASE):
            in_stocks_table = True
            continue
        if not in_stocks_table:
            continue

        norm_line = re.sub(r'\bT\s*O\s*T\s*A\s*L\b', 'TOTAL', line, flags=re.IGNORECASE)
        if re.search(r'\bTOTAL\b', norm_line, re.IGNORECASE):
            tot_nums = [
                _soa_number(x)
                for x in re.findall(r'\(?-?\d+(?:,\d{3})*(?:\.\d+)?\)?', norm_line)
            ]
            if len(tot_nums) >= 3:
                total_modal = tot_nums[0]
                total_aset = tot_nums[1]
                total_unrealized_rp = tot_nums[2]
            break

        m_sym = re.match(r'^([A-Z]{4}|IDR)\b\s*(.*)$', line)
        if not m_sym:
            continue
        symbol = m_sym.group(1)
        if symbol in excluded_tickers:
            continue

        rest = m_sym.group(2)
        nums = re.findall(r'-?\d+(?:,\d{3})*(?:\.\d+)?', rest)
        if len(nums) >= 7:
            tail = nums[-7:]
            qty = _soa_number(tail[0])
            avg_price = _soa_number(tail[1])
            last_price = _soa_number(tail[2])
            buy_value = _soa_number(tail[3])
            market_value = _soa_number(tail[4])
            unrealized_rp = _soa_number(tail[5])
            unrealized_pct = _soa_number(tail[6])

            rows.append({
                'period_str': period_str,
                'timestamp': int(datetime.datetime.now().timestamp() * 1000),
                'symbol': symbol,
                'qty': float(qty),
                'avg_price': avg_price,
                'last_price': last_price,
                'buy_value': buy_value,
                'market_value': market_value,
                'unrealized_rp': unrealized_rp,
                'unrealized_pct': unrealized_pct,
                'total_modal': total_modal,
                'total_aset': total_aset,
                'total_unrealized_rp': total_unrealized_rp,
                'equity_nab': equity_nab
            })

    if rows:
        if total_modal == 0.0 and total_aset == 0.0:
            total_modal = sum(r['buy_value'] for r in rows)
            total_aset = sum(r['market_value'] for r in rows)
            total_unrealized_rp = sum(r['unrealized_rp'] for r in rows)
        for r in rows:
            r['total_modal'] = total_modal
            r['total_aset'] = total_aset
            r['total_unrealized_rp'] = total_unrealized_rp

    return rows

def parse_stockbit_daily_transactions(visual_text):
    transactions = []
    seen = set()
    lines = [re.sub(r'\s+', ' ', line).strip() for line in (visual_text or '').splitlines()]
    number_re = re.compile(r'\(?-?[\d,]+(?:\.\d+)?\)?')

    def ledger_fields(line):
        row = re.match(r'^\d{2}/\d{2}/\d{4}\s+\d{2}/\d{2}/\d{4}\s+(.*)$', line)
        if not row:
            return None, None, line
        rest = row.group(1)
        ref = re.match(r'^(?:[A-Z]\s+\S+|\d{5,8}\s+[A-Z])\s+(.*)$', rest)
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
        r'(?P<price>[\d,.]+)\s*[=-]\s*(?P<amount>[\d,]+(?:\.\d{1,2})?)',
        re.IGNORECASE,
    )

    current_trade_date = None
    for line in lines:
        if not line:
            continue
        invoice_match = re.search(r'\bTrx on (\d{2}/\d{2}/\d{4})\b', line, re.IGNORECASE)
        if invoice_match:
            current_trade_date = invoice_match.group(1)
            continue

        row_match = re.match(r'^(\d{2}/\d{2}/\d{4})\s+(\d{2}/\d{2}/\d{4})\s+(.*)$', line)
        if row_match:
            current_trade_date = None
            tr_date, _, rest = row_match.groups()

            if re.search(r'^J\s+\S+\s+SELL\s+(?:FR|PBS)\d+', rest, re.IGNORECASE):
                _, cr_amount, desc_txt = ledger_fields(line)
                amount = cr_amount if cr_amount and cr_amount > 0 else None
                add(tr_date, 'Jual Obligasi', desc_txt.strip(), amount)
                continue

            if re.search(r'^D\s+\S+\s+.*(bond interest|dividend|dividen)', rest, re.IGNORECASE):
                _, cr_amount, desc_txt = ledger_fields(line)
                amount = cr_amount if cr_amount and cr_amount > 0 else None
                category = 'Dividen' if re.search(r'dividend|dividen', rest, re.IGNORECASE) else 'Bunga Obligasi'
                add(tr_date, category, desc_txt.strip(), amount)
                continue

        if current_trade_date:
            for m in stock_detail_re.finditer(line):
                d = m.groupdict()
                category = 'Beli' if d['side'].upper() == 'B' else 'Jual'
                description = (
                    f"{category} saham {d['symbol'].upper()} — {fmt_int(d['qty'].replace(',', ''))} lembar "
                    f"@ Rp {fmt_dec(_soa_number(d['price']), 2)} (Ref {d['ref']})"
                )
                add(current_trade_date, category, description, _soa_number(d['amount']))

    return transactions

def parse_stockbit_annual_report(visual_text, raw_text):
    """Mengekstrak riwayat dividen & snapshot portofolio 31 Desember dari Stock_Report tahunan Stockbit."""
    combined = (visual_text or "") + "\n" + (raw_text or "")
    if "TAX REPORT" not in combined.upper() or "DIVIDEND HISTORY" not in combined.upper():
        return None

    lines = [re.sub(r'\s+', ' ', l).strip() for l in (visual_text or "").splitlines() if l.strip()]

    report_year = None
    m_yr = re.search(r'31\s+Desember\s+(20\d{2})', combined, re.IGNORECASE)
    if m_yr:
        report_year = m_yr.group(1)
    else:
        m_per = re.search(r'01/01/(20\d{2})\s*-\s*31/12/\2', combined)
        if m_per:
            report_year = m_per.group(1)

    rdn_cash = 0.0
    for pat in [
        r'Saldo\s+RDN\)\s*\|?\s*Rp\s*([\d,]+(?:\.\d+)?)',
        r'012\s+Kas\s*\|?\s*Rp\s*([\d,]+(?:\.\d+)?)',
    ]:
        m_rdn = re.search(pat, combined, re.IGNORECASE)
        if m_rdn:
            rdn_cash = _soa_number(m_rdn.group(1))
            break

    dividends = []
    in_div_section = False
    seen_div = set()
    for line in lines:
        upper_l = line.upper()
        if "DIVIDEND HISTORY" in upper_l:
            in_div_section = True
            continue
        if not in_div_section:
            continue
        if "STOCK DIVIDEND" in upper_l:
            break
        if re.match(r'^TOTAL\b', upper_l):
            continue

        m_div = re.match(r'^(\d{2}/\d{2}/\d{4})\s+([A-Z]{4})\s+(.*)$', line)
        if m_div:
            pay_date, sym, rest = m_div.groups()
            nums = re.findall(r'-?\d+(?:,\d{3})*(?:\.\d+)?', rest)
            if len(nums) >= 3:
                qty_sh = int(round(_soa_number(nums[0])))
                div_per_sh = _soa_number(nums[1])
                gross_amt = round(_soa_number(nums[2]), 2)
                desc = f"Dividen Tunai {sym} — {fmt_int(qty_sh)} lembar @ Rp {fmt_dec(div_per_sh, 2)}"
                key = (pay_date, sym, gross_amt)
                if gross_amt > 0 and key not in seen_div:
                    seen_div.add(key)
                    dividends.append({
                        'period_str': date_str_to_period_name(pay_date),
                        'date_str': pay_date,
                        'category': 'Dividen',
                        'description': desc,
                        'amount': gross_amt
                    })

    port_rows = []
    in_port = False
    total_modal = 0.0
    total_aset = 0.0
    excluded_words = {'DATE', 'PAGE', 'KODE', 'TOTAL', 'STOCK', 'CLIENT'}

    for line in lines:
        upper_l = line.upper()
        if f"PORTOFOLIO PER 31 DESEMBER {report_year}" in upper_l if report_year else "PORTOFOLIO PER 31 DESEMBER" in upper_l:
            in_port = True
            continue
        if not in_port:
            continue
        if "DISCLAIMER" in upper_l or "TRANSACTION HISTORY" in upper_l:
            break

        if re.match(r'^TOTAL\b', upper_l):
            tot_nums = [_soa_number(x) for x in re.findall(r'-?\d+(?:,\d{3})*(?:\.\d+)?', line)]
            if len(tot_nums) >= 2:
                total_modal = tot_nums[0]
                total_aset = tot_nums[1]
            break

        m_sym = re.match(r'^([A-Z]{4})\s+(.*)$', line)
        if m_sym and m_sym.group(1) not in excluded_words:
            sym = m_sym.group(1)
            nums = re.findall(r'-?\d+(?:,\d{3})*(?:\.\d+)?', m_sym.group(2))
            if len(nums) >= 7:
                port_rows.append({
                    'period_str': f"Desember {report_year}" if report_year else "Desember",
                    'timestamp': int(datetime.datetime.now().timestamp() * 1000),
                    'symbol': sym,
                    'qty': float(_soa_number(nums[0])),
                    'avg_price': _soa_number(nums[1]),
                    'last_price': _soa_number(nums[2]),
                    'buy_value': _soa_number(nums[3]),
                    'market_value': _soa_number(nums[4]),
                    'unrealized_rp': _soa_number(nums[5]),
                    'unrealized_pct': _soa_number(nums[6]),
                    'total_modal': 0.0,
                    'total_aset': 0.0,
                    'total_unrealized_rp': 0.0,
                    'equity_nab': 0.0
                })

    equity_nab = (total_aset + rdn_cash) if total_aset > 0 else 0.0
    if port_rows:
        if total_modal == 0.0:
            total_modal = sum(r['buy_value'] for r in port_rows)
            total_aset = sum(r['market_value'] for r in port_rows)
            equity_nab = total_aset + rdn_cash
        tot_unr = sum(r['unrealized_rp'] for r in port_rows)
        for r in port_rows:
            r['total_modal'] = total_modal
            r['total_aset'] = total_aset
            r['total_unrealized_rp'] = tot_unr
            r['equity_nab'] = equity_nab

    return {
        'report_year': report_year,
        'period_dec': f"Desember {report_year}" if report_year else None,
        'equity_nab': equity_nab,
        'dividends': dividends,
        'portfolio_rows': port_rows
    }

def get_bca_stockbit_cashflows(df_transact):
    """Mengambil mutasi aktual setor/tarik RDN Stockbit dari Rekening Koran BCA (TRANSACT)."""
    if df_transact.empty:
        return []
    df = df_transact.copy()
    df['id_category'] = pd.to_numeric(df['id_category'], errors='coerce').fillna(0).astype(int)
    df['type'] = pd.to_numeric(df['type'], errors='coerce').fillna(0).astype(int)
    df['date'] = pd.to_numeric(df['date'], errors='coerce').fillna(0)
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0.0)
    df['desc_str'] = df['desc'].astype(str)

    mask = (df['id_category'] == 42) & df['desc_str'].str.contains(r'stockbit|4994633351', case=False, na=False)
    sb_bca = df[mask].sort_values(by='date', ascending=True)

    cashflows = []
    for _, row in sb_bca.iterrows():
        dt_obj = pd.to_datetime(row['date'], unit='ms', errors='coerce')
        if pd.isnull(dt_obj):
            continue
        amt = abs(float(row['amount']))
        if amt <= 0:
            continue
        signed_amt = -amt if int(row['type']) == 0 else amt
        cashflows.append((dt_obj.date(), signed_amt))
    return cashflows

def get_category_id_v2(desc, tx_type):
    d = desc.lower()
    if tx_type == 1: # Income
        if 'artax' in d or 'gaji' in d or 'pybca' in d: return 3
        elif 'bunga' in d or 'dividen' in d: return 2
        elif 'wd bca' in d or 'setoran' in d or 'cdm' in d or 'switching' in d or 'bi-fast cr' in d: return 41
        elif 'ftscy' in d or 'stockbit' in d or 'rdn' in d or '4994633351' in d: return 42
        elif any(name in d for name in ['laura', 'rizqi', 'jhasperi', 'joni', 'mawaddah', 'dewi', 'hidayatun']): return 7
        else: return 12
    else: # Expense
        if 'ftscy' in d or 'stockbit' in d or 'rdn' in d or '4994633351' in d or 'bibit' in d or 'investasi' in d: return 42
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
st.markdown(f"<p style='text-align: center; color: {sub_text}; letter-spacing: 2px; font-size: 0.75rem;'>[ SYSTEM ACTIVE // CLOUD PERSISTENCE ]</p>", unsafe_allow_html=True)
st.write("")

tab1, tab2, tab3 = st.tabs(["Konversi PDF", "Dashboard", "Investasi"])

# ================= PAGE 1: KONVERSI PDF =================
with tab1:
    st.markdown("<h3>Terminal Input Data</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: {sub_text}; font-size: 0.85rem;'>Upload semua file Statement (BCA / Stockbit) disini. Data tersimpan otomatis ke Google Sheets.</p>", unsafe_allow_html=True)
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
        with st.spinner("Memproses sinkronisasi data ke Google Sheets..."):
            added_count, duplicate_count, stockbit_count, stockbit_trx_count = 0, 0, 0, 0
            
            # --- PROSES MUTASI BCA & KARTU KREDIT ---
            if uploaded_bank_files or uploaded_cc_files:
                df_transact = load_or_seed_transact()
                if not df_transact.empty:
                    df_transact['_id'] = pd.to_numeric(df_transact['_id'], errors='coerce').fillna(0).astype(int)
                    df_transact['date'] = pd.to_numeric(df_transact['date'], errors='coerce').fillna(0).astype('int64')
                    df_transact['type'] = pd.to_numeric(df_transact['type'], errors='coerce').fillna(0).astype(int)
                    df_transact['amount'] = df_transact['amount'].apply(lambda x: str(int(round(float(x)))) if str(x).strip() != "" else "0")
                    df_transact['desc'] = df_transact['desc'].astype(str)
                    next_id = int(df_transact['_id'].max()) + 1
                    existing_keys = set(zip(df_transact['date'], df_transact['desc'], df_transact['amount'], df_transact['type']))
                else:
                    next_id = 1
                    existing_keys = set()
                
                new_bank_rows = []
                
                if uploaded_bank_files:
                    for uploaded_file in uploaded_bank_files:
                        temp_path = f"temp_{uploaded_file.name}"
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        reader = pypdf.PdfReader(temp_path)
                        raw_pdf_text = extract_pdf_text(reader)
                        statement_year = infer_statement_year(raw_pdf_text)
                        if not raw_pdf_text.strip():
                            st.warning(f"Tidak ada teks yang bisa dibaca dari PDF rekening koran: {uploaded_file.name}.")
                            os.remove(temp_path)
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
                            else:
                                amount = [float(m[0].replace(',', '')) for m in matches][0]
                                
                            try:
                                dt = datetime.datetime(statement_year, mon_in_text, day, 12, 0, 0)
                            except ValueError:
                                continue
                            timestamp_ms = int(dt.timestamp() * 1000)
                            desc = clean_desc_v3(b_str)
                            cat_id = get_category_id_v2(desc, tx_type)
                            str_amount = str(int(round(amount)))
                            
                            key = (timestamp_ms, desc, str_amount, tx_type)
                            if key in existing_keys:
                                duplicate_count += 1
                                continue
                            existing_keys.add(key)
                            new_bank_rows.append({
                                '_id': next_id,
                                'id_category': cat_id,
                                'desc': desc,
                                'type': tx_type,
                                'date': timestamp_ms,
                                'amount': str_amount
                            })
                            next_id += 1
                            added_count += 1
                        os.remove(temp_path)

                if uploaded_cc_files:
                    months_map = {'JAN':1, 'FEB':2, 'MAR':3, 'APR':4, 'MEI':5, 'JUN':6, 'JUL':7, 'AUG':8, 'SEP':9, 'OCT':10, 'NOV':11, 'DEC':12, 'AGU':8, 'AGT':8, 'OKT':10, 'NOP':11, 'DES':12}
                    for uploaded_file in uploaded_cc_files:
                        temp_path = f"temp_cc_{uploaded_file.name}"
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        try:
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
                                        
                                        key = (timestamp_ms, cleaned_cc_desc, str_amount, 0)
                                        if key in existing_keys:
                                            duplicate_count += 1
                                            continue
                                        existing_keys.add(key)
                                        new_bank_rows.append({
                                            '_id': next_id,
                                            'id_category': cat_id,
                                            'desc': cleaned_cc_desc,
                                            'type': 0,
                                            'date': timestamp_ms,
                                            'amount': str_amount
                                        })
                                        next_id += 1
                                        added_count += 1
                        finally:
                            if os.path.exists(temp_path):
                                os.remove(temp_path)

                if new_bank_rows:
                    df_transact = pd.concat([df_transact, pd.DataFrame(new_bank_rows)], ignore_index=True)
                    save_sheet_df(df_transact, "TRANSACT", TRANSACT_COLS)
                    sync_work_db_from_df(df_transact)

            # --- PROSES PORTFOLIO, TRANSAKSI & STOCK REPORT STOCKBIT ---
            if uploaded_stockbit_files:
                df_port = get_sheet_df("STOCK_PORTFOLIO", PORT_COLS)
                df_trx = get_sheet_df("STOCK_TRANSACTIONS", TRX_COLS)
                
                for uploaded_file in uploaded_stockbit_files:
                    temp_path = f"temp_sb_{uploaded_file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    try:
                        reader = pypdf.PdfReader(temp_path)
                        visual_text = extract_pdf_visual_lines(reader)
                        raw_text = extract_pdf_text(reader)

                        annual_data = parse_stockbit_annual_report(visual_text, raw_text)
                        if annual_data is not None:
                            yr = annual_data['report_year']
                            div_rows = annual_data['dividends']
                            dec_period = annual_data['period_dec']
                            dec_port_rows = annual_data['portfolio_rows']

                            if not div_rows and not dec_port_rows:
                                raise ValueError("Tidak ada data dividen maupun portofolio akhir tahun yang dikenali dari Stock Report ini.")

                            if not df_trx.empty and yr:
                                is_same_year_div = (
                                    (df_trx['category'].astype(str).str.lower() == 'dividen') &
                                    (df_trx['date_str'].astype(str).str.endswith(f"/{yr}"))
                                )
                                df_trx = df_trx[~is_same_year_div]

                            if div_rows:
                                df_trx = pd.concat([df_trx, pd.DataFrame(div_rows)], ignore_index=True)
                                stockbit_trx_count += len(div_rows)

                            if dec_period and dec_port_rows:
                                if df_port.empty or (df_port['period_str'] != dec_period).all():
                                    df_port = pd.concat([df_port, pd.DataFrame(dec_port_rows)], ignore_index=True)
                                    stockbit_count += len(dec_port_rows)
                                elif annual_data['equity_nab'] > 0:
                                    mask_dec = (df_port['period_str'] == dec_period) & (pd.to_numeric(df_port['equity_nab'], errors='coerce').fillna(0) <= 0)
                                    df_port.loc[mask_dec, 'equity_nab'] = annual_data['equity_nab']
                        else:
                            period_str = parse_period_name(visual_text)
                            new_port_rows = parse_stockbit_portfolio(visual_text, raw_text, period_str)
                            daily_transactions = parse_stockbit_daily_transactions(visual_text)

                            if not new_port_rows and not daily_transactions:
                                raise ValueError("Tidak ada data portofolio maupun transaksi harian yang dikenali dari PDF ini.")

                            if not df_port.empty:
                                df_port = df_port[df_port['period_str'] != period_str]
                            if not df_trx.empty:
                                is_target_period = (df_trx['period_str'] == period_str)
                                is_div = (df_trx['category'].astype(str).str.lower() == 'dividen')
                                df_trx = df_trx[~(is_target_period & ~is_div)]

                            stockbit_count += len(new_port_rows)

                            new_trx_rows = [
                                {
                                    'period_str': period_str,
                                    'date_str': trx['date_str'],
                                    'category': trx['category'],
                                    'description': trx['description'],
                                    'amount': trx['amount']
                                }
                                for trx in daily_transactions
                            ]
                            stockbit_trx_count += len(new_trx_rows)

                            if new_port_rows:
                                df_port = pd.concat([df_port, pd.DataFrame(new_port_rows)], ignore_index=True)
                            if new_trx_rows:
                                df_trx = pd.concat([df_trx, pd.DataFrame(new_trx_rows)], ignore_index=True)

                    except Exception as e:
                        st.error(f"Gagal memproses file Stockbit ({uploaded_file.name}): {e}")
                    finally:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)

                save_sheet_df(df_port, "STOCK_PORTFOLIO", PORT_COLS)
                save_sheet_df(df_trx, "STOCK_TRANSACTIONS", TRX_COLS)
                sync_inv_db_from_dfs(df_port, df_trx)
            
            st.success(f"Sinkronisasi Google Sheets Selesai! | Transaksi Bank: {fmt_int(added_count)} (Duplikat: {fmt_int(duplicate_count)}) | Portofolio: {fmt_int(stockbit_count)} baris | Transaksi Harian: {fmt_int(stockbit_trx_count)} terekstrak")

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
    
    df = load_or_seed_transact()
    cat_map = get_category_map()
    
    if not df.empty:
        df['id_category'] = pd.to_numeric(df['id_category'], errors='coerce').fillna(0).astype(int)
        df['Kategori'] = df['id_category'].map(cat_map).fillna('Lainnya')
        df['Deskripsi'] = df['desc'].astype(str)
        df['type'] = pd.to_numeric(df['type'], errors='coerce').fillna(0).astype(int)
        df['datetime'] = pd.to_datetime(pd.to_numeric(df['date'], errors='coerce'), unit='ms')
        df['Tahun'] = df['datetime'].dt.year
        df['Bulan'] = df['datetime'].dt.month
        df['Jumlah'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
        
        years = sorted(df['Tahun'].dropna().unique().astype(int), reverse=True)
        selected_year = st.selectbox("Pilih Tahun", years)
        
        df_year = df[df['Tahun'] == selected_year]
        
        total_income_yr = df_year[df_year['type'] == 1]['Jumlah'].sum()
        total_expense_yr = df_year[df_year['type'] == 0]['Jumlah'].sum()
        
        col_a, col_b, col_c = st.columns(3)
        col_a.metric(f"Total Pemasukan ({selected_year})", fmt_rp(total_income_yr))
        col_b.metric(f"Total Pengeluaran ({selected_year})", fmt_rp(total_expense_yr))
        col_c.metric("Net Cashflow", fmt_rp(total_income_yr - total_expense_yr))
        
        st.divider()
        
        months_dict = {1:'Januari', 2:'Februari', 3:'Maret', 4:'April', 5:'Mei', 6:'Juni', 7:'Juli', 8:'Agustus', 9:'September', 10:'Oktober', 11:'November', 12:'Desember'}
        available_months = sorted(df_year['Bulan'].dropna().unique().astype(int))
        selected_month = st.selectbox("Pilih Bulan", available_months, format_func=lambda x: months_dict.get(x, str(x)))
        
        df_month = df_year[df_year['Bulan'] == selected_month]
        
        total_income_mo = df_month[df_month['type'] == 1]['Jumlah'].sum()
        total_expense_mo = df_month[df_month['type'] == 0]['Jumlah'].sum()
        
        st.markdown(f"<h4 style='text-align: center; color: {text_color};'>Periode: {months_dict.get(selected_month)} {selected_year}</h4>", unsafe_allow_html=True)
        m1, m2 = st.columns(2)
        m1.metric("Pemasukan Bulan Ini", fmt_rp(total_income_mo))
        m2.metric("Pengeluaran Bulan Ini", fmt_rp(total_expense_mo))
        
        df_expense_mo = df_month[df_month['type'] == 0]
        if not df_expense_mo.empty:
            st.markdown("<h4>Pengeluaran per Kategori</h4>", unsafe_allow_html=True)
            cat_summary = df_expense_mo.groupby('Kategori')['Jumlah'].sum().reset_index().sort_values(by='Jumlah', ascending=False)
            max_val = cat_summary['Jumlah'].max()
            cat_summary['color_type'] = cat_summary['Jumlah'].apply(lambda x: '#FF3333' if x == max_val else text_color)
            cat_summary['Jumlah_Fmt'] = cat_summary['Jumlah'].apply(fmt_rp)
            
            chart = alt.Chart(cat_summary).mark_bar(cornerRadiusTopLeft=2, cornerRadiusTopRight=2).encode(
                x=alt.X('Kategori:N', sort='-y', title=None, axis=alt.Axis(labelAngle=-45, labelColor=chart_text)),
                y=alt.Y('Jumlah:Q', title=None, axis=alt.Axis(labelColor=chart_text)),
                color=alt.Color('color_type:N', scale=None),
                tooltip=[alt.Tooltip('Kategori:N', title='Kategori'), alt.Tooltip('Jumlah_Fmt:N', title='Total')]
            ).properties(height=300, background=chart_bg).configure_view(stroke=None).configure_axis(gridColor=chart_grid)
            
            st.altair_chart(chart, use_container_width=True)
            st.markdown("<h4>Rincian Transaksi</h4>", unsafe_allow_html=True)
            df_exp_disp = df_expense_mo.sort_values(by='datetime', ascending=False).copy()
            df_exp_disp['Tanggal'] = df_exp_disp['datetime'].dt.strftime('%d/%m/%Y')
            df_exp_disp['Jumlah (Rp)'] = df_exp_disp['Jumlah'].apply(fmt_int)
            st.dataframe(df_exp_disp[['Tanggal', 'Kategori', 'Deskripsi', 'Jumlah (Rp)']], use_container_width=True, hide_index=True)
        else:
            st.info("Tidak ada data pengeluaran untuk periode ini.")
    else:
        st.info("Silakan lakukan sinkronisasi data di Tab Konversi PDF.")

# --- FUNGSI DASHBOARD INVESTASI (TAB 3 LENGKAP + XIRR, CAGR, & GRAFIK) ---
def _compute_period_xirr(bca_cashflows, end_date, terminal_value):
    flows = [(dt, amt) for dt, amt in bca_cashflows if dt <= end_date]
    if terminal_value > 0:
        flows.append((end_date, terminal_value))
    if len(flows) > 1:
        try:
            res = xirr(flows)
            return (res * 100) if res is not None else 0.0
        except Exception:
            return 0.0
    return 0.0

def render_investment():
    st.markdown("<h3>Portofolio Investasi</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: {sub_text}; font-size: 0.75rem; letter-spacing: 1px;'>[ HISTORICAL PERFORMANCE & TRANSACTIONS ]</p>", unsafe_allow_html=True)
    st.write("")
    
    df_port = get_sheet_df("STOCK_PORTFOLIO", PORT_COLS)
    df_trx = get_sheet_df("STOCK_TRANSACTIONS", TRX_COLS)
    df_transact = load_or_seed_transact()
    
    if not df_port.empty:
        num_cols = [
            'qty', 'avg_price', 'last_price', 'buy_value', 'market_value',
            'unrealized_rp', 'unrealized_pct', 'total_modal', 'total_aset',
            'total_unrealized_rp', 'equity_nab'
        ]
        for col in num_cols:
            df_port[col] = pd.to_numeric(df_port[col], errors='coerce').fillna(0.0)
        if not df_trx.empty:
            df_trx['amount'] = pd.to_numeric(df_trx['amount'], errors='coerce').fillna(0.0)

        bca_cashflows = get_bca_stockbit_cashflows(df_transact)

        periods = sorted(df_port['period_str'].astype(str).unique(), key=period_str_to_end_date, reverse=True)
        selected_period = st.selectbox("Pilih Periode Statement Bulanan", periods)
        val_date = period_str_to_end_date(selected_period)
        
        df_filtered = df_port[df_port['period_str'] == selected_period].reset_index(drop=True)
        df_trx_filtered = df_trx[df_trx['period_str'] == selected_period].reset_index(drop=True) if not df_trx.empty else pd.DataFrame()
        
        tot_buy_row = float(df_filtered['total_modal'].iloc[0]) if not df_filtered.empty else 0.0
        tot_mkt_row = float(df_filtered['total_aset'].iloc[0]) if not df_filtered.empty else 0.0
        tot_unreal_row = float(df_filtered['total_unrealized_rp'].iloc[0]) if not df_filtered.empty else 0.0

        tot_buy = tot_buy_row if tot_buy_row > 0 else df_filtered['buy_value'].sum()
        tot_mkt = tot_mkt_row if tot_mkt_row > 0 else df_filtered['market_value'].sum()
        tot_unreal = tot_unreal_row if (tot_buy_row > 0 or tot_mkt_row > 0) else df_filtered['unrealized_rp'].sum()
        equity_nab_val = float(df_filtered['equity_nab'].max()) if not df_filtered.empty else 0.0
        
        tot_div = 0.0
        if not df_trx.empty and 'category' in df_trx.columns:
            div_all = df_trx[df_trx['category'].astype(str).str.lower() == 'dividen'].copy()
            if not div_all.empty:
                div_all['_dt'] = pd.to_datetime(div_all['date_str'], format='%d/%m/%Y', errors='coerce')
                div_valid = div_all[div_all['_dt'].notnull() & (div_all['_dt'].dt.date <= val_date)]
                tot_div = div_valid['amount'].sum() if not div_valid.empty else 0.0

        terminal_equity = equity_nab_val if equity_nab_val > 0 else tot_mkt
        xirr_pct = _compute_period_xirr(bca_cashflows, val_date, terminal_equity)

        cagr_pct = 0.0
        if tot_buy > 0 and tot_mkt > 0:
            valid_cf_dates = [dt for dt, _ in bca_cashflows if dt <= val_date]
            if valid_cf_dates:
                first_date = valid_cf_dates[0]
            else:
                earliest_period = min(periods, key=period_str_to_end_date)
                first_date = period_str_to_end_date(earliest_period).replace(day=1)
            days_invested = max((val_date - first_date).days, 1)
            years_invested = max(days_invested / 365.25, 1.0)
            cagr_pct = ((tot_mkt / tot_buy) ** (1 / years_invested) - 1) * 100

        simple_ret_pct = (tot_unreal / tot_buy * 100) if tot_buy > 0 else 0.0

        st.write("")
        col_s1, col_s2, col_s3, col_s4, col_s5, col_s6 = st.columns(6)
        col_s1.metric("Total Modal", fmt_rp(tot_buy))
        col_s2.metric("Total Aset", fmt_rp(tot_mkt))
        col_s3.metric("Unrealized P/L", fmt_rp(tot_unreal), delta=fmt_pct(simple_ret_pct, signed=True))
        col_s4.metric("Total Dividen", fmt_rp(tot_div))
        col_s5.metric("XIRR", fmt_pct(xirr_pct))
        col_s6.metric("CAGR", fmt_pct(cagr_pct))
        
        st.divider()
        
        sub_tab = st.radio("Pilih Tampilan Dashboard", ["Ringkasan Portofolio", "Rincian Transaksi Harian", "Grafik Return (XIRR)"], horizontal=True)
        st.divider()
        
        if sub_tab == "Ringkasan Portofolio":
            df_stocks_only = df_filtered[df_filtered['symbol'] != 'IDR'].sort_values(by='market_value', ascending=False).copy()
            total_mv_chart = df_stocks_only['market_value'].sum()
            df_stocks_only['Market_Fmt'] = df_stocks_only['market_value'].apply(fmt_rp)
            df_stocks_only['Bobot_Fmt'] = df_stocks_only['market_value'].apply(
                lambda v: fmt_pct((v / total_mv_chart * 100) if total_mv_chart > 0 else 0.0)
            )
            df_stocks_only['Unreal_Pct_Fmt'] = df_stocks_only['unrealized_pct'].apply(lambda v: fmt_pct(v, signed=True))

            sorted_symbols = df_stocks_only['symbol'].tolist()
            slice_colors = [mono_palette[i % len(mono_palette)] for i in range(len(sorted_symbols))]

            st.markdown(f"<h4>Alokasi Aset ({selected_period})</h4>", unsafe_allow_html=True)
            chart_donut = alt.Chart(df_stocks_only).mark_arc(innerRadius=60, stroke=chart_bg, strokeWidth=2).encode(
                theta=alt.Theta(field="market_value", type="quantitative", sort=None),
                order=alt.Order(field="market_value", sort="descending"),
                color=alt.Color(
                    field="symbol",
                    type="nominal",
                    sort=sorted_symbols,
                    scale=alt.Scale(domain=sorted_symbols, range=slice_colors),
                    legend=alt.Legend(title="Emiten", labelColor=chart_text, titleColor=chart_text)
                ),
                tooltip=[
                    alt.Tooltip('symbol:N', title='Emiten'),
                    alt.Tooltip('Market_Fmt:N', title='Market Value'),
                    alt.Tooltip('Bobot_Fmt:N', title='Alokasi'),
                    alt.Tooltip('Unreal_Pct_Fmt:N', title='Unrealized P/L')
                ]
            ).properties(height=350, background=chart_bg).configure_view(stroke=None)
            
            st.altair_chart(chart_donut, use_container_width=True)
            
            st.markdown(f"<h4>Rincian Performa per Emiten ({selected_period})</h4>", unsafe_allow_html=True)
            df_display = pd.DataFrame({
                'Emiten': df_stocks_only['symbol'],
                'Status': df_stocks_only['unrealized_rp'].apply(lambda x: 'Untung' if x > 0 else ('Impas' if x == 0 else 'Rugi')),
                'Lembar/Qty': df_stocks_only['qty'].apply(fmt_int),
                'Avg Price': df_stocks_only['avg_price'].apply(lambda x: fmt_dec(x, 2)),
                'Last Price': df_stocks_only['last_price'].apply(fmt_int),
                'Modal (Rp)': df_stocks_only['buy_value'].apply(fmt_int),
                'Market Value (Rp)': df_stocks_only['market_value'].apply(fmt_int),
                'Unrealized (Rp)': df_stocks_only['unrealized_rp'].apply(fmt_signed_int),
                'Unrealized (%)': df_stocks_only['unrealized_pct'].apply(lambda x: fmt_pct(x, signed=True)),
            })

            def style_pl_row(row):
                styles = ['' for _ in row.index]
                pl_idx_rp = list(row.index).index('Unrealized (Rp)')
                pl_idx_pct = list(row.index).index('Unrealized (%)')
                if row['Status'] == 'Untung':
                    styles[pl_idx_rp] = 'color: #22C55E; font-weight: 600;'
                    styles[pl_idx_pct] = 'color: #22C55E; font-weight: 600;'
                elif row['Status'] == 'Rugi':
                    styles[pl_idx_rp] = 'color: #FF4B4B; font-weight: 600;'
                    styles[pl_idx_pct] = 'color: #FF4B4B; font-weight: 600;'
                else:
                    styles[pl_idx_rp] = 'color: #9CA3AF; font-weight: 500;'
                    styles[pl_idx_pct] = 'color: #9CA3AF; font-weight: 500;'
                return styles

            st.dataframe(df_display.style.apply(style_pl_row, axis=1), use_container_width=True, hide_index=True)
        
        elif sub_tab == "Rincian Transaksi Harian":
            if not df_trx_filtered.empty:
                st.markdown(f"<h4>Log Transaksi Harian ({selected_period})</h4>", unsafe_allow_html=True)
                df_trx_display = df_trx_filtered[['date_str', 'category', 'description', 'amount']].copy()
                df_trx_display['_tanggal_sort'] = pd.to_datetime(
                    df_trx_display['date_str'], format='%d/%m/%Y', errors='coerce'
                )
                df_trx_display = df_trx_display.sort_values('_tanggal_sort', ascending=False).drop(columns='_tanggal_sort')
                df_trx_display['Jumlah (Rp)'] = df_trx_display['amount'].apply(fmt_trx_amount)
                df_trx_display = df_trx_display[['date_str', 'category', 'description', 'Jumlah (Rp)']]
                df_trx_display.columns = ['Tanggal', 'Kategori', 'Deskripsi Transaksi', 'Jumlah (Rp)']

                st.dataframe(df_trx_display, use_container_width=True, hide_index=True)
            else:
                st.info(f"Tidak ada rincian transaksi harian terekstrak untuk periode {selected_period}.")
        
        else: # Grafik Return (XIRR)
            st.markdown("<h4>Historis Return Portofolio & XIRR (%)</h4>", unsafe_allow_html=True)
            chart_periods = sorted(df_port['period_str'].astype(str).unique(), key=period_str_to_end_date)
            hist_records = []
            for p in chart_periods:
                sub_df = df_port[df_port['period_str'] == p]
                p_date = period_str_to_end_date(p)
                b_row = float(sub_df['total_modal'].iloc[0]) if not sub_df.empty else 0.0
                m_row = float(sub_df['total_aset'].iloc[0]) if not sub_df.empty else 0.0
                u_row = float(sub_df['total_unrealized_rp'].iloc[0]) if not sub_df.empty else 0.0
                nab_row = float(sub_df['equity_nab'].max()) if not sub_df.empty else 0.0

                b_val = b_row if b_row > 0 else sub_df['buy_value'].sum()
                m_val = m_row if m_row > 0 else sub_df['market_value'].sum()
                u_val = u_row if (b_row > 0 or m_row > 0) else sub_df['unrealized_rp'].sum()
                ret = (u_val / b_val * 100) if b_val > 0 else 0.0
                p_xirr = _compute_period_xirr(bca_cashflows, p_date, nab_row if nab_row > 0 else m_val)
                hist_records.append({
                    'period_str': p,
                    'Portfolio Return (%)': round(ret, 2),
                    'XIRR (%)': round(p_xirr, 2)
                })
            
            df_chart_source = pd.DataFrame(hist_records)
            if not df_chart_source.empty:
                chart_data = df_chart_source.melt(id_vars='period_str', var_name='Metrik', value_name='Return (%)')
                chart_data['Return_Fmt'] = chart_data['Return (%)'].apply(lambda v: fmt_pct(v, signed=True))
                
                chart = alt.Chart(chart_data).mark_line(strokeWidth=2, point=True).encode(
                    x=alt.X('period_str:N', sort=None, title=None, axis=alt.Axis(labelColor=chart_text)),
                    y=alt.Y('Return (%):Q', title=None, axis=alt.Axis(labelColor=chart_text)),
                    color=alt.Color('Metrik:N', scale=alt.Scale(domain=['Portfolio Return (%)', 'XIRR (%)'], range=[text_color, '#787878']), legend=alt.Legend(title=None, orient='top', labelColor=chart_text)),
                    tooltip=[
                        alt.Tooltip('period_str:N', title='Periode'),
                        alt.Tooltip('Metrik:N', title='Metrik'),
                        alt.Tooltip('Return_Fmt:N', title='Nilai')
                    ]
                ).properties(height=350, background=chart_bg).configure_view(stroke=None).configure_axis(gridColor=chart_grid)
                
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("Belum cukup data untuk merender grafik return historis.")
    else:
        st.info("Belum ada data Portofolio di Google Sheets. Silakan upload ulang file Statement Stockbit di Tab Konversi PDF.")

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
