import streamlit as st
import streamlit.components.v1 as components
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
    st.session_state.theme = 'Dark'

# --- DYNAMIC CSS & NOTHING AESTHETIC REFINEMENT (MOBILE & CLOUD READY) ---
if st.session_state.theme == 'Light':
    bg_color = "#F5F7FA"
    card_bg = "#FFFFFF"
    text_color = "#1B2430"
    sub_text = "#687385"
    border_color = "#E1E6ED"
    input_bg = "#FFFFFF"
    tab_bg = "#EEF1F5"
    tab_active_bg = "#263548"
    tab_active_text = "#FFFFFF"
    tab_inactive_text = "#536071"
    primary_btn_bg = "#202C3B"
    primary_btn_text = "#FFFFFF"
    chart_bg = "#FFFFFF"
    chart_text = "#536071"
    chart_grid = "#E8ECF1"
    shadow_box = "0 8px 24px rgba(25, 38, 55, 0.05)"
    accent_color = "#B69A68"
    mono_palette = ["#202C3B", "#344255", "#48596D", "#607186", "#78889A", "#929EAC", "#ADB6C1", "#C8CED6", "#E1E5EA"]
else:
    bg_color = "#12161C"
    card_bg = "#1B212A"
    text_color = "#EDF1F6"
    sub_text = "#9AA6B5"
    border_color = "#303946"
    input_bg = "#171D25"
    tab_bg = "#1B222C"
    tab_active_bg = "#DDE5EF"
    tab_active_text = "#17202B"
    tab_inactive_text = "#B8C2CF"
    primary_btn_bg = "#E9EEF5"
    primary_btn_text = "#17202B"
    chart_bg = "#1B212A"
    chart_text = "#B8C2CF"
    chart_grid = "#303946"
    shadow_box = "0 8px 24px rgba(0, 0, 0, 0.22)"
    accent_color = "#B69A68"
    mono_palette = ["#EDF1F6", "#D8DEE7", "#C2CBD7", "#ABB7C5", "#94A2B2", "#7D8C9E", "#66778A", "#4F6175", "#39495B"]

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Montserrat:wght@500;600;700&display=swap');

    .stApp,
    div[data-testid="stAppViewContainer"] {{
        background: {bg_color};
        color: {text_color};
        font-family: 'DM Sans', 'Inter', sans-serif !important;
        font-size: 15.5px;
        line-height: 1.5;
        letter-spacing: -0.012em;
    }}
    .stApp button, .stApp input, .stApp textarea, .stApp select,
    .stApp [data-baseweb] {{
        font-family: 'DM Sans', 'Inter', sans-serif !important;
    }}
    header[data-testid="stHeader"] {{
        background: transparent !important;
    }}
    div[data-testid="stToolbar"] {{
        background: transparent !important;
    }}

    /* Overall page rhythm */
    div[data-testid="stMainBlockContainer"],
    div[data-testid="stAppViewContainer"] .main .block-container,
    section.main > div.block-container {{
        max-width: 1440px !important;
        padding-top: 0.85rem !important;
        padding-bottom: 2.5rem !important;
    }}

    h1 {{
        font-family: 'Montserrat', sans-serif !important;
        text-align: center;
        color: {text_color};
        font-weight: 600;
        font-size: 1.78rem;
        letter-spacing: -0.025em;
        line-height: 1.18;
        text-transform: uppercase;
        margin-top: 0.05rem;
        margin-bottom: 0.25rem;
    }}

    h3 {{
        font-family: 'DM Sans', 'Inter', sans-serif !important;
        text-align: center;
        color: {text_color};
        font-weight: 600;
        font-size: 1.28rem;
    }}

    h4 {{
        font-family: 'DM Sans', 'Inter', sans-serif !important;
        text-align: center;
        color: {text_color};
        font-weight: 600;
        font-size: 1.08rem;
    }}

    p, span, label, .stMarkdown {{
        color: {text_color} !important;
        font-size: 0.94rem;
        line-height: 1.5;
    }}

    .app-subtitle {{
        text-align: center;
        color: {sub_text} !important;
        letter-spacing: 0.105em;
        font-size: 0.74rem !important;
        line-height: 1.45;
        font-weight: 600;
        margin-top: -0.1rem;
        margin-bottom: 0.65rem;
    }}

    .metric-section-label {{
        color: {sub_text} !important;
        font-family: 'DM Sans', 'Inter', sans-serif !important;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.11em;
        text-transform: uppercase;
        margin: 0.65rem 0 0.35rem 0.1rem;
    }}
    .metric-section-label.secondary {{
        margin-top: 1.1rem;
    }}

    .filter-summary-bar {{
        background: {tab_bg};
        border: 1px solid {border_color};
        border-radius: 10px;
        padding: 8px 14px;
        margin: 0.35rem 0 0.65rem 0;
        font-size: 0.84rem;
        color: {sub_text} !important;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
    }}
    .filter-summary-bar strong {{
        color: {text_color} !important;
    }}

    .health-diagnosis-card {{
        background: {card_bg};
        border: 1px solid {border_color};
        border-left: 4px solid {accent_color};
        border-radius: 14px;
        padding: 15px 18px;
        margin-top: 0.75rem;
        margin-bottom: 0.45rem;
        box-shadow: {shadow_box};
    }}
    .health-diagnosis-title {{
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        color: {text_color} !important;
        margin-bottom: 0.35rem;
    }}
    .health-diagnosis-list {{
        margin: 0;
        padding-left: 1.15rem;
    }}
    .health-diagnosis-list li {{
        color: {sub_text} !important;
        font-size: 0.84rem;
        line-height: 1.48;
        margin-bottom: 0.25rem;
    }}
    .health-diagnosis-list li strong {{
        color: {text_color} !important;
    }}

    /* Metric cards */
    div[data-testid="stMetric"] {{
        background: {card_bg};
        border: 1px solid {border_color};
        min-height: 112px;
        padding: 19px 21px;
        border-radius: 16px;
        box-shadow: {shadow_box};
        transition: border-color 0.18s ease, transform 0.18s ease;
    }}
    div[data-testid="stMetric"]:hover {{
        border-color: {accent_color};
        transform: translateY(-1px);
    }}
    div[data-testid="stMetricValue"] {{
        font-size: 1.55rem;
        line-height: 1.25;
        color: {text_color};
        font-weight: 600;
        letter-spacing: -0.035em;
        font-variant-numeric: tabular-nums;
    }}
    div[data-testid="stMetricLabel"] {{
        color: {sub_text};
        text-transform: none;
        font-size: 0.82rem;
        font-weight: 500;
        letter-spacing: -0.005em;
    }}

    /* CENTERED NAVIGATION — COMPACT FLOATING FRAME */
    div[data-testid="stTabs"] > div:first-child {{
        width: 100% !important;
        display: flex !important;
        justify-content: center !important;
    }}
    .stApp div[data-testid="stTabs"] [data-baseweb="tab-list"],
    .stApp div[data-testid="stTabs"] [role="tablist"] {{
        display: inline-flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: fit-content !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
        margin: 0 auto 0.95rem !important;
        gap: 5px !important;
        background: {tab_bg} !important;
        padding: 5px !important;
        border: 1px solid {border_color} !important;
        border-radius: 14px !important;
        box-shadow: 0 3px 12px rgba(20, 30, 45, 0.035) !important;
        border-bottom: 1px solid {border_color} !important;
    }}
    .stApp .stTabs [data-baseweb="tab-highlight"],
    .stApp .stTabs [data-baseweb="tab-border"],
    .stApp .stTabs [data-baseweb="tab"]::after,
    .stApp .stTabs [role="tab"]::after {{
        display: none !important;
        height: 0 !important;
        border: 0 !important;
        background: transparent !important;
    }}
    .stApp .stTabs [data-baseweb="tab"],
    .stApp .stTabs [role="tab"] {{
        flex: 0 0 auto !important;
        background: transparent !important;
        border: 0 !important;
        border-bottom: 0 !important;
        box-shadow: none !important;
        border-radius: 10px !important;
        padding: 9px 17px !important;
        margin: 0 !important;
        min-height: 39px !important;
        transition: background 0.18s ease, color 0.18s ease;
    }}
    .stApp .stTabs [data-baseweb="tab"] p,
    .stApp .stTabs [data-baseweb="tab"] span,
    .stApp .stTabs [data-baseweb="tab"] div,
    .stApp .stTabs [role="tab"] p,
    .stApp .stTabs [role="tab"] span,
    .stApp .stTabs [role="tab"] div {{
        color: {tab_inactive_text} !important;
        font-family: 'DM Sans', 'Inter', sans-serif !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        letter-spacing: -0.005em;
        text-transform: none;
    }}
    .stApp .stTabs [data-baseweb="tab"][aria-selected="true"],
    .stApp .stTabs [role="tab"][aria-selected="true"] {{
        background: {tab_active_bg} !important;
        border: 0 !important;
        border-bottom: 0 !important;
        border-radius: 10px !important;
        box-shadow: 0 1px 3px rgba(20, 30, 45, 0.10) !important;
    }}
    .stApp .stTabs [aria-selected="true"] p,
    .stApp .stTabs [aria-selected="true"] span,
    .stApp .stTabs [aria-selected="true"] div {{
        color: {tab_active_text} !important;
        font-weight: 600 !important;
    }}
    .stApp .stTabs [data-baseweb="tab-panel"] {{
        padding-top: 0.8rem;
    }}

    /* Buttons */
    .stButton button,
    .stDownloadButton button,
    div[data-testid="stFileUploader"] button,
    div[data-testid="stFileUploaderDropzone"] button {{
        background: {card_bg} !important;
        color: {text_color} !important;
        border: 1px solid {border_color} !important;
        border-radius: 11px !important;
        min-height: 40px;
        font-family: 'DM Sans', 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        box-shadow: {shadow_box};
        transition: all 0.18s ease;
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
        border-color: {accent_color} !important;
        transform: translateY(-1px);
    }}
    .stButton button[kind="primary"] {{
        background: {primary_btn_bg} !important;
        color: {primary_btn_text} !important;
        border: 1px solid {primary_btn_bg} !important;
        text-transform: uppercase;
        letter-spacing: 0.045em;
    }}
    .stButton button[kind="primary"] p,
    .stButton button[kind="primary"] span {{
        color: {primary_btn_text} !important;
    }}
    .stButton button[kind="primary"]:hover {{
        border-color: {accent_color} !important;
        opacity: 0.94;
    }}

    /* Inputs + password visibility icon */
    .stTextInput input, .stSelectbox select, .stNumberInput input, .stDateInput input {{
        background: {input_bg} !important;
        color: {text_color} !important;
        border: 1px solid {border_color} !important;
        border-radius: 11px !important;
        font-family: 'DM Sans', 'Inter', sans-serif !important;
        font-size: 0.94rem;
        box-shadow: none !important;
    }}
    div[data-testid="stTextInput"] button,
    div[data-testid="stTextInput"] button[aria-label],
    div[data-testid="stTextInput"] [data-testid*="visibilityToggle"],
    [data-testid*="TextInput"] button[aria-label],
    button[aria-label*="password" i] {{
        background: {input_bg} !important;
        color: {sub_text} !important;
        border: 0 !important;
        border-left: 1px solid {border_color} !important;
        border-radius: 0 10px 10px 0 !important;
        box-shadow: none !important;
        min-height: 0 !important;
        padding: 0 0.7rem !important;
        transform: none !important;
    }}
    div[data-testid="stTextInput"] button:hover,
    div[data-testid="stTextInput"] [data-testid*="visibilityToggle"]:hover,
    [data-testid*="TextInput"] button[aria-label]:hover,
    button[aria-label*="password" i]:hover {{
        background: {tab_bg} !important;
        border-color: {border_color} !important;
    }}
    div[data-testid="stTextInput"] button svg,
    div[data-testid="stTextInput"] [data-testid*="visibilityToggle"] svg,
    [data-testid*="TextInput"] button[aria-label] svg,
    button[aria-label*="password" i] svg {{
        fill: none !important;
        stroke: {sub_text} !important;
        color: {sub_text} !important;
        opacity: 0.9;
    }}
    div[data-testid="stTextInput"] button svg path,
    div[data-testid="stTextInput"] [data-testid*="visibilityToggle"] svg path,
    [data-testid*="TextInput"] button[aria-label] svg path,
    button[aria-label*="password" i] svg path {{
        fill: none !important;
        stroke: currentColor !important;
    }}

    /* PDF uploader */
    div[data-testid="stFileUploader"] {{
        border: 1px solid {border_color};
        border-radius: 14px;
        padding: 12px;
        background: {card_bg} !important;
        box-shadow: {shadow_box};
    }}
    div[data-testid="stFileUploader"] section {{
        background: {input_bg} !important;
        border: 1px dashed {border_color} !important;
        border-radius: 11px !important;
    }}
    div[data-testid="stFileUploader"] section svg {{
        fill: {sub_text} !important;
        color: {sub_text} !important;
    }}
    div[data-testid="stFileUploaderFile"] {{
        background: {tab_bg} !important;
        border: 1px solid {border_color} !important;
        border-radius: 9px !important;
        padding: 5px 9px !important;
    }}
    div[data-testid="stFileUploaderFile"] span,
    div[data-testid="stFileUploaderFile"] small,
    div[data-testid="stFileUploaderFile"] div {{
        color: {text_color} !important;
    }}

    div[data-testid="stAlert"] {{
        border-radius: 11px;
    }}

    hr {{
        border-color: {border_color};
    }}

    @media (max-width: 768px) {{
        div[data-testid="stMainBlockContainer"],
        div[data-testid="stAppViewContainer"] .main .block-container,
        section.main > div.block-container {{
            padding-top: 0.7rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }}
        h1 {{ font-size: 1.45rem; }}
        h3 {{ font-size: 1.12rem; }}
        h4 {{ font-size: 0.98rem; }}
        .stApp div[data-testid="stTabs"] [data-baseweb="tab-list"],
        .stApp div[data-testid="stTabs"] [role="tablist"] {{
            flex-wrap: wrap !important;
            gap: 5px !important;
        }}
        .stApp .stTabs [data-baseweb="tab"] {{
            padding: 7px 12px !important;
        }}
        .stApp .stTabs [data-baseweb="tab"] p,
        .stApp .stTabs [data-baseweb="tab"] span,
        .stApp .stTabs [data-baseweb="tab"] div {{
            font-size: 0.8rem !important;
        }}
        div[data-testid="stHorizontalBlock"] {{
            gap: 0.7rem !important;
            row-gap: 0.7rem !important;
            margin-bottom: 0 !important;
        }}
        div[data-testid="stHorizontalBlock"] > div {{
            margin-bottom: 0 !important;
            min-width: 0 !important;
        }}
        div[data-testid="stMetric"] {{
            min-height: 0 !important;
            padding: 13px 16px !important;
            margin-bottom: 0 !important;
            border-radius: 14px !important;
        }}
        div[data-testid="stMetricValue"] {{
            font-size: 1.22rem !important;
            line-height: 1.22 !important;
        }}
        div[data-testid="stMetricLabel"] {{
            font-size: 0.78rem !important;
            line-height: 1.3 !important;
        }}
        .metric-section-label {{
            margin-top: 0.45rem !important;
            margin-bottom: 0.25rem !important;
        }}
        .metric-section-label.secondary {{
            margin-top: 0.8rem !important;
        }}
        .app-subtitle {{
            margin-bottom: 0.55rem !important;
            font-size: 0.68rem !important;
        }}
        .stApp [data-testid="stTabs"] [data-baseweb="tab-list"] {{
            margin-bottom: 0.8rem !important;
        }}
    }}
    </style>
""", unsafe_allow_html=True)

# --- INDONESIAN NUMBER & TIME FORMATTING HELPERS ---
WIB_TZ = datetime.timezone(datetime.timedelta(hours=7))

def get_wib_timestamp_label():
    return datetime.datetime.now(WIB_TZ).strftime("%d-%m-%Y-%H%M%S")

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
DEFAULT_CC_LIMIT = 15_000_000.0

TRANSACT_COLS = ['_id', 'id_category', 'desc', 'type', 'date', 'amount']
CASH_POS_COLS = ['updated_at', 'saldo_bca', 'tagihan_cc', 'limit_cc_plafon', 'aktual_cash', 'keterangan']
RULES_COLS = ['keyword', 'tx_type', 'id_category', 'category_name', 'updated_at']
PORT_COLS = [
    'period_str', 'timestamp', 'symbol', 'qty', 'avg_price', 'last_price',
    'buy_value', 'market_value', 'unrealized_rp', 'unrealized_pct',
    'total_modal', 'total_aset', 'total_unrealized_rp', 'equity_nab'
]
TRX_COLS = ['period_str', 'date_str', 'category', 'description', 'amount']

DEFAULT_CATEGORIES = [
    (1, 'Gaji', 1), (2, 'Dividen / Bunga', 1), (3, 'Gaji', 1),
    (7, 'Pengembalian Dana', 1), (12, 'Lain-lain', 1),
    (15, 'Belanja', 0), (19, 'Hadiah', 0), (21, 'Hiburan', 0),
    (24, 'Kesehatan', 0), (25, 'Makanan & Minuman', 0), (30, 'Pakaian', 0),
    (33, 'Rumah', 0), (35, 'Tagihan', 0), (37, 'Pulsa & Data', 0),
    (38, 'Transportasi', 0), (39, 'Lain-lain', 0),
    (41, 'Penyesuaian Pemasukan', 1), (42, 'Investasi', 0),
    (45, 'Penampilan', 0), (46, 'Kartu Kredit', 0)
]

def init_working_db_file():
    if os.path.exists(BASE_DB):
        shutil.copyfile(BASE_DB, WORK_DB)
        return
    conn = sqlite3.connect(WORK_DB)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS android_metadata (locale TEXT);")
    cur.execute("DELETE FROM android_metadata;")
    cur.execute("INSERT INTO android_metadata (locale) VALUES ('in_ID');")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS CATEGORY (
            _id INTEGER PRIMARY KEY AUTOINCREMENT,
            NAME TEXT,
            TYPE INTEGER
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS TRANSACT (
            _id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_category INTEGER,
            desc TEXT,
            type INTEGER,
            date INTEGER,
            amount TEXT
        );
    """)
    cur.executemany("INSERT OR IGNORE INTO CATEGORY (_id, NAME, TYPE) VALUES (?, ?, ?)", DEFAULT_CATEGORIES)
    conn.commit()
    conn.close()

if not os.path.exists(WORK_DB):
    init_working_db_file()

conn_gsheets = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=60, show_spinner=False)
def read_worksheet_cached(sheet_name):
    df = conn_gsheets.read(worksheet=sheet_name, ttl=0)
    return df.dropna(how='all')

def get_sheet_df(sheet_name, expected_cols, silent_missing=False):
    try:
        df = read_worksheet_cached(sheet_name).copy()
        if df.empty:
            return pd.DataFrame(columns=expected_cols)
        numeric_defaults = {
            'total_modal', 'total_aset', 'total_unrealized_rp', 'equity_nab',
            'saldo_bca', 'tagihan_cc', 'limit_cc_plafon', 'aktual_cash'
        }
        for col in expected_cols:
            if col not in df.columns:
                df[col] = DEFAULT_CC_LIMIT if col == 'limit_cc_plafon' else (0.0 if col in numeric_defaults else "")
        return df[expected_cols]
    except Exception as e:
        if not silent_missing:
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

# --- CATEGORY CATALOG & SELF-LEARNING RULE ENGINE ---
def get_category_catalog():
    rows = DEFAULT_CATEGORIES
    if os.path.exists(WORK_DB):
        try:
            conn = get_bank_connection()
            df_cat = pd.read_sql_query("SELECT _id, NAME, TYPE FROM CATEGORY", conn)
            conn.close()
            if not df_cat.empty:
                rows = [
                    (int(r['_id']), str(r['NAME']).strip(), int(pd.to_numeric(r['TYPE'], errors='coerce') or 0))
                    for _, r in df_cat.iterrows()
                    if pd.notna(r['_id']) and str(r['NAME']).strip()
                ]
        except Exception:
            pass

    id_to_name = {}
    expense_name_to_id = {}
    income_name_to_id = {}

    for cid, cname, ctype in rows:
        id_to_name[cid] = cname
        if ctype == 1:
            if cname not in income_name_to_id or cid == 3:
                income_name_to_id[cname] = cid
        else:
            if cname not in expense_name_to_id:
                expense_name_to_id[cname] = cid

    if 'Investasi' not in income_name_to_id and 'Investasi' in expense_name_to_id:
        income_name_to_id['Investasi'] = expense_name_to_id['Investasi']

    def _sort_names(names):
        return sorted(names, key=lambda n: (n.lower() == 'lain-lain', n.lower()))

    expense_options = _sort_names(list(expense_name_to_id.keys()))
    income_options = _sort_names(list(income_name_to_id.keys()))
    all_options = _sort_names(list(set(expense_options) | set(income_options)))

    return {
        'id_to_name': id_to_name,
        'expense_name_to_id': expense_name_to_id,
        'income_name_to_id': income_name_to_id,
        'expense_options': expense_options,
        'income_options': income_options,
        'all_options': all_options,
    }

def resolve_category_id(category_name, tx_type, catalog=None):
    catalog = catalog or get_category_catalog()
    cname = str(category_name or '').strip()
    if int(tx_type) == 1:
        if cname in catalog['income_name_to_id']:
            return int(catalog['income_name_to_id'][cname])
        if cname in catalog['expense_name_to_id']:
            return int(catalog['expense_name_to_id'][cname])
        return 12
    else:
        if cname in catalog['expense_name_to_id']:
            return int(catalog['expense_name_to_id'][cname])
        if cname in catalog['income_name_to_id']:
            return int(catalog['income_name_to_id'][cname])
        return 39

def suggest_rule_keyword(desc):
    """Mengekstrak kata kunci bersih dari deskripsi mutasi agar bisa dipakai ulang lintas periode."""
    raw = re.sub(r'\s+', ' ', str(desc or '')).strip().lower()
    if not raw:
        return ""
    s = re.sub(r'\b\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?\b', ' ', raw)
    s = re.sub(r'\b\d{4,}\b', ' ', s)
    tokens = []
    stop_tokens = {'qris', 'qr', 'trf', 'transfer', 'pembayaran', 'topup', 'id', 'no', 'ref', 'inv', 'pt', 'cv', 'tbk'}
    for tok in s.split():
        clean_tok = tok.strip(".,-_:;()[]{}/\\")
        if not clean_tok:
            continue
        if len(clean_tok) >= 6 and any(c.isdigit() for c in clean_tok) and any(c.isalpha() for c in clean_tok):
            continue
        if clean_tok in stop_tokens:
            continue
        tokens.append(clean_tok)
    candidate = " ".join(tokens).strip()
    return candidate if len(candidate) >= 2 else raw

def keyword_matches_desc(keyword, desc):
    kw = str(keyword or '').strip().lower()
    target = str(desc or '').strip().lower()
    if not kw or not target:
        return False
    if len(kw) <= 3:
        return bool(re.search(rf'\b{re.escape(kw)}\b', target))
    return kw in target

def load_category_rules():
    df = get_sheet_df("CATEGORY_RULES", RULES_COLS, silent_missing=True)
    if df.empty:
        return pd.DataFrame(columns=RULES_COLS)
    df = df.copy()
    df['keyword'] = df['keyword'].astype(str).str.strip().str.lower()
    df['tx_type'] = pd.to_numeric(df['tx_type'], errors='coerce').fillna(0).astype(int)
    df['id_category'] = pd.to_numeric(df['id_category'], errors='coerce').fillna(0).astype(int)
    df['category_name'] = df['category_name'].astype(str).str.strip()
    df['updated_at'] = df['updated_at'].astype(str).str.strip()
    df = df[(df['keyword'] != '') & (df['id_category'] > 0)]
    df = df.drop_duplicates(subset=['keyword', 'tx_type'], keep='last').reset_index(drop=True)
    return df[RULES_COLS]

def save_category_rules(df_rules):
    if df_rules.empty:
        save_sheet_df(pd.DataFrame(columns=RULES_COLS), "CATEGORY_RULES", RULES_COLS)
        return
    clean_df = df_rules.copy()
    clean_df['keyword'] = clean_df['keyword'].astype(str).str.strip().str.lower()
    clean_df['tx_type'] = pd.to_numeric(clean_df['tx_type'], errors='coerce').fillna(0).astype(int)
    clean_df['id_category'] = pd.to_numeric(clean_df['id_category'], errors='coerce').fillna(0).astype(int)
    clean_df['category_name'] = clean_df['category_name'].astype(str).str.strip()
    clean_df['updated_at'] = clean_df['updated_at'].astype(str).str.strip()
    clean_df = clean_df[(clean_df['keyword'] != '') & (clean_df['id_category'] > 0)]
    clean_df = clean_df.drop_duplicates(subset=['keyword', 'tx_type'], keep='last').reset_index(drop=True)
    save_sheet_df(clean_df, "CATEGORY_RULES", RULES_COLS)

def upsert_rules_and_apply_retroactive(df_transact, rule_items, direct_id_updates=None):
    """
    Menyimpan aturan baru/update ke CATEGORY_RULES dan langsung menerapkan ke seluruh
    transaksi lama yang cocok di TRANSACT + sinkronisasi CK_Working.ckbak.
    """
    now_wib = datetime.datetime.now(WIB_TZ).strftime("%d/%m/%Y %H:%M WIB")
    catalog = get_category_catalog()
    df_rules = load_category_rules()

    new_rule_rows = []
    for item in rule_items:
        kw = str(item.get('keyword', '')).strip().lower()
        tx_t = 1 if int(item.get('tx_type', 0)) == 1 else 0
        cat_id = int(item.get('id_category', 0))
        cat_name = item.get('category_name') or catalog['id_to_name'].get(cat_id, 'Lain-lain')
        if kw and cat_id > 0:
            new_rule_rows.append({
                'keyword': kw,
                'tx_type': tx_t,
                'id_category': cat_id,
                'category_name': cat_name,
                'updated_at': now_wib,
            })

    if new_rule_rows:
        df_rules = pd.concat([df_rules, pd.DataFrame(new_rule_rows)], ignore_index=True)
        save_category_rules(df_rules)

    if df_transact.empty:
        return df_transact, 0

    df_updated = df_transact.copy()
    df_updated['_id'] = pd.to_numeric(df_updated['_id'], errors='coerce').fillna(0).astype(int)
    df_updated['type'] = pd.to_numeric(df_updated['type'], errors='coerce').fillna(0).astype(int)
    df_updated['id_category'] = pd.to_numeric(df_updated['id_category'], errors='coerce').fillna(0).astype(int)
    orig_cats = df_updated['id_category'].copy()

    if direct_id_updates:
        for tx_id, target_cat_id in direct_id_updates.items():
            df_updated.loc[df_updated['_id'] == int(tx_id), 'id_category'] = int(target_cat_id)

    for r in new_rule_rows:
        kw = r['keyword']
        tx_t = r['tx_type']
        target_cat_id = r['id_category']
        mask_type = (df_updated['type'] == tx_t)
        mask_kw = df_updated['desc'].astype(str).apply(lambda d: keyword_matches_desc(kw, d))
        df_updated.loc[mask_type & mask_kw, 'id_category'] = target_cat_id

    affected_count = int((df_updated['id_category'] != orig_cats).sum())
    save_sheet_df(df_updated, "TRANSACT", TRANSACT_COLS)
    sync_work_db_from_df(df_updated)
    return df_updated, affected_count

# --- CASH POSITION & FINANCIAL HEALTH ANALYTICS ---
def load_cash_position():
    if 'cash_pos_state' in st.session_state:
        return st.session_state['cash_pos_state']
    try:
        df = read_worksheet_cached("CASH_POSITION").copy()
        if not df.empty:
            last = df.iloc[-1]
            raw_limit = pd.to_numeric(last.get('limit_cc_plafon', DEFAULT_CC_LIMIT), errors='coerce')
            limit_plafon = float(raw_limit) if (pd.notna(raw_limit) and float(raw_limit) > 0) else DEFAULT_CC_LIMIT
            state = {
                'saldo_bca': float(pd.to_numeric(last.get('saldo_bca', 0), errors='coerce') or 0.0),
                'tagihan_cc': float(pd.to_numeric(last.get('tagihan_cc', 0), errors='coerce') or 0.0),
                'limit_cc_plafon': limit_plafon,
                'updated_at': str(last.get('updated_at', '-')),
                'keterangan': str(last.get('keterangan', '-')),
            }
            st.session_state['cash_pos_state'] = state
            return state
    except Exception:
        pass
    return {
        'saldo_bca': 0.0,
        'tagihan_cc': 0.0,
        'limit_cc_plafon': DEFAULT_CC_LIMIT,
        'updated_at': 'Belum ada data',
        'keterangan': '-',
    }

def save_cash_position(saldo_bca, tagihan_cc, limit_cc_plafon=DEFAULT_CC_LIMIT, keterangan="Update Manual"):
    now_wib = datetime.datetime.now(WIB_TZ).strftime("%d/%m/%Y %H:%M WIB")
    s_bca = float(saldo_bca or 0.0)
    t_cc = float(tagihan_cc or 0.0)
    l_plafon = float(limit_cc_plafon) if (limit_cc_plafon and float(limit_cc_plafon) > 0) else DEFAULT_CC_LIMIT
    a_cash = s_bca - t_cc

    state = {
        'saldo_bca': s_bca,
        'tagihan_cc': t_cc,
        'limit_cc_plafon': l_plafon,
        'updated_at': now_wib,
        'keterangan': keterangan,
    }
    st.session_state['cash_pos_state'] = state

    df_pos = pd.DataFrame([{
        'updated_at': now_wib,
        'saldo_bca': round(s_bca, 2),
        'tagihan_cc': round(t_cc, 2),
        'limit_cc_plafon': round(l_plafon, 2),
        'aktual_cash': round(a_cash, 2),
        'keterangan': keterangan,
    }])
    save_sheet_df(df_pos, "CASH_POSITION", CASH_POS_COLS)

def analyze_loan_health(saldo_bca, limit_used, limit_plafon, df_transact, df_port):
    """Menganalisis kesehatan pinjaman berdasarkan 4 kerangka teori keuangan."""
    limit_plafon = limit_plafon if limit_plafon > 0 else DEFAULT_CC_LIMIT
    aktual_cash = saldo_bca - limit_used
    sisa_limit = max(0.0, limit_plafon - limit_used)

    if limit_used <= 0:
        coverage_pct = 100.0
        coverage_status = "Likuid Penuh"
        coverage_color = "normal"
    else:
        coverage_pct = (saldo_bca / limit_used) * 100.0
        if coverage_pct >= 100.0:
            coverage_status = "Likuid (100%+ Tertutup)"
            coverage_color = "normal"
        elif coverage_pct >= 30.0:
            coverage_status = "Likuiditas Moderat"
            coverage_color = "off"
        else:
            coverage_status = "Defisit Likuiditas Tunai"
            coverage_color = "inverse"

    cur_pct = (limit_used / limit_plafon) * 100.0
    if cur_pct <= 30.0:
        cur_status = "Sehat (≤ 30%)"
        cur_color = "normal"
    elif cur_pct <= 50.0:
        cur_status = "Waspada (30–50%)"
        cur_color = "off"
    elif cur_pct <= 80.0:
        cur_status = "Risiko Tinggi (50–80%)"
        cur_color = "inverse"
    else:
        cur_status = "Kritis (> 80% Limit)"
        cur_color = "inverse"

    avg_monthly_income = 0.0
    if not df_transact.empty:
        df_inc = df_transact.copy()
        df_inc['type'] = pd.to_numeric(df_inc['type'], errors='coerce').fillna(0).astype(int)
        df_inc['id_category'] = pd.to_numeric(df_inc['id_category'], errors='coerce').fillna(0).astype(int)
        df_inc['amount'] = pd.to_numeric(df_inc['amount'], errors='coerce').fillna(0.0)
        df_inc['dt'] = pd.to_datetime(pd.to_numeric(df_inc['date'], errors='coerce'), unit='ms', errors='coerce')
        df_inc = df_inc[(df_inc['type'] == 1) & (~df_inc['id_category'].isin([41, 42])) & df_inc['dt'].notnull()]
        if not df_inc.empty:
            latest_yr = int(df_inc['dt'].dt.year.max())
            df_yr_inc = df_inc[df_inc['dt'].dt.year == latest_yr]
            active_months = max(int(df_yr_inc['dt'].dt.month.nunique()), 1)
            avg_monthly_income = float(df_yr_inc['amount'].sum()) / active_months

    if avg_monthly_income > 0:
        dti_pct = (limit_used / avg_monthly_income) * 100.0
        if dti_pct <= 30.0:
            dti_status = "Aman (≤ 30% Income)"
            dti_color = "normal"
        elif dti_pct <= 100.0:
            dti_status = "Terkelola (Wajib Cicilan 0%)"
            dti_color = "off"
        else:
            dti_status = "Tekanan Arus Kas (> 1x Gaji)"
            dti_color = "inverse"
    else:
        dti_pct = None
        dti_status = "Data Income Kosong"
        dti_color = "off"

    latest_equity = 0.0
    latest_period_label = "-"
    if not df_port.empty:
        df_p = df_port.copy()
        for col in ('equity_nab', 'total_aset', 'market_value'):
            df_p[col] = pd.to_numeric(df_p[col], errors='coerce').fillna(0.0)
        periods_sorted = sorted(df_p['period_str'].astype(str).unique(), key=period_str_to_end_date, reverse=True)
        if periods_sorted:
            latest_period_label = periods_sorted[0]
            sub_latest = df_p[df_p['period_str'] == latest_period_label]
            nab_val = float(sub_latest['equity_nab'].max())
            aset_val = float(sub_latest['total_aset'].iloc[0]) if float(sub_latest['total_aset'].iloc[0]) > 0 else float(sub_latest['market_value'].sum())
            latest_equity = nab_val if nab_val > 0 else aset_val

    net_liquid_worth = aktual_cash + latest_equity
    if latest_equity > 0:
        if net_liquid_worth >= 0:
            solvency_status = f"Solven (+Portofolio {latest_period_label})"
            solvency_color = "normal"
        else:
            solvency_status = "Defisit Ekuitas Likuid"
            solvency_color = "inverse"
    else:
        solvency_status = "Tanpa Data Portofolio" if aktual_cash < 0 else "Solven Tunai"
        solvency_color = "inverse" if aktual_cash < 0 else "normal"

    insights = []
    if aktual_cash < 0:
        insights.append(
            f"<strong>Likuiditas Tunai (Cash Coverage {fmt_pct(coverage_pct)}):</strong> "
            f"Saldo BCA ({fmt_rp(saldo_bca)}) belum menutup total limit terpakai ({fmt_rp(limit_used)}), "
            f"menyisakan gap kas sebesar <strong>{fmt_rp(abs(aktual_cash))}</strong>."
        )
    else:
        insights.append(
            f"<strong>Likuiditas Tunai (Cash Coverage {fmt_pct(coverage_pct)}):</strong> "
            f"Saldo BCA ({fmt_rp(saldo_bca)}) mencukupi untuk menutup seluruh limit CC terpakai ({fmt_rp(limit_used)})."
        )

    insights.append(
        f"<strong>Utilisasi Kredit / CUR ({fmt_pct(cur_pct)} dari Plafon {fmt_rp(limit_plafon)}):</strong> "
        f"Sisa limit tersisa <strong>{fmt_rp(sisa_limit)}</strong>. "
        + (
            "Utilisasi sudah melewati ambang 80% (zona kritis); tahan transaksi kredit baru agar ruang darurat tidak habis."
            if cur_pct > 80.0 else
            "Utilisasi di atas batas ideal 30%; prioritaskan pelunasan pokok berjalan."
            if cur_pct > 30.0 else
            "Utilisasi berada di zona sehat perbankan (≤ 30%)."
        )
    )

    if dti_pct is not None:
        insights.append(
            f"<strong>Kapasitas Arus Kas (Rasio Eksposur {fmt_pct(dti_pct)} terhadap rata-rata pemasukan {fmt_rp(avg_monthly_income)}/bln):</strong> "
            + (
                "Pastikan cicilan bulanan + tagihan non-cicilan jatuh tempo bulan ini tidak melampaui 30% pemasukan bulanan dan selalu dibayar <em>full payment</em> agar bebas bunga ritel 1,75%/bulan."
                if dti_pct > 30.0 else
                "Total eksposur CC masih dalam kapasitas aman arus kas bulanan (≤ 30%)."
            )
        )

    if latest_equity > 0:
        if net_liquid_worth >= 0:
            insights.append(
                f"<strong>Solvabilitas Neraca (Net Liquid Worth {fmt_rp(net_liquid_worth)}):</strong> "
                f"Secara kekayaan likuid bersih (BCA + Ekuitas Stockbit {fmt_rp(latest_equity)}), posisi Anda <strong>masih solven</strong>; defisit kas terjadi karena dana lebih banyak teralokasi di aset investasi."
            )
        else:
            insights.append(
                f"<strong>Solvabilitas Neraca (Net Liquid Worth {fmt_rp(net_liquid_worth)}):</strong> "
                f"Gabungan kas BCA dan ekuitas portofolio ({fmt_rp(latest_equity)}) masih di bawah total eksposur CC ({fmt_rp(limit_used)}); fokuskan arus kas masuk berikutnya untuk menurunkan saldo utang CC."
            )

    return {
        'aktual_cash': aktual_cash,
        'sisa_limit': sisa_limit,
        'coverage_pct': coverage_pct,
        'coverage_status': coverage_status,
        'coverage_color': coverage_color,
        'cur_pct': cur_pct,
        'cur_status': cur_status,
        'cur_color': cur_color,
        'dti_pct': dti_pct,
        'dti_status': dti_status,
        'dti_color': dti_color,
        'net_liquid_worth': net_liquid_worth,
        'solvency_status': solvency_status,
        'solvency_color': solvency_color,
        'insights': insights,
    }

def get_bank_connection():
    return sqlite3.connect(WORK_DB)

def get_category_map():
    return get_category_catalog()['id_to_name']

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

def optimize_sqlite_for_android(db_path):
    if not os.path.exists(db_path):
        return
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    has_seq = cur.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='sqlite_sequence';"
    ).fetchone()
    if has_seq:
        for tbl in ('TRANSACT', 'CATEGORY'):
            tbl_exists = cur.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?;", (tbl,)
            ).fetchone()
            if tbl_exists:
                max_id = cur.execute(f"SELECT COALESCE(MAX(_id), 0) FROM {tbl};").fetchone()[0]
                updated = cur.execute(
                    "UPDATE sqlite_sequence SET seq = ? WHERE name = ?;", (int(max_id), tbl)
                ).rowcount
                if updated == 0 and int(max_id) > 0:
                    cur.execute(
                        "INSERT INTO sqlite_sequence (name, seq) VALUES (?, ?);", (tbl, int(max_id))
                    )
    cur.execute("REINDEX;")
    cur.execute("ANALYZE;")
    conn.commit()
    conn.close()

    conn_vac = sqlite3.connect(db_path, isolation_level=None)
    cur_vac = conn_vac.cursor()
    cur_vac.execute("PRAGMA wal_checkpoint(TRUNCATE);")
    cur_vac.execute("PRAGMA journal_mode = DELETE;")
    cur_vac.execute("VACUUM;")
    conn_vac.close()

def sync_work_db_from_df(df_transact):
    if not os.path.exists(WORK_DB):
        init_working_db_file()
    if df_transact.empty:
        optimize_sqlite_for_android(WORK_DB)
        return

    conn = get_bank_connection()
    cursor = conn.cursor()
    valid_cats = {
        int(row[0])
        for row in cursor.execute("SELECT _id FROM CATEGORY;").fetchall()
        if row[0] is not None
    }

    df_clean = df_transact.copy()
    df_clean['_id_num'] = pd.to_numeric(df_clean['_id'], errors='coerce').fillna(0).astype(int)
    df_clean['date_num'] = pd.to_numeric(df_clean['date'], errors='coerce').fillna(0).astype('int64')
    df_clean = df_clean[df_clean['date_num'] > 0].sort_values(by=['date_num', '_id_num'], ascending=[True, True])

    used_ids = set()
    next_fallback_id = int(df_clean['_id_num'].max()) + 1 if not df_clean.empty else 1
    rows = []

    for _, r in df_clean.iterrows():
        raw_id = int(r['_id_num'])
        if raw_id <= 0 or raw_id in used_ids:
            raw_id = next_fallback_id
            next_fallback_id += 1
        used_ids.add(raw_id)

        tx_type = int(pd.to_numeric(r['type'], errors='coerce') or 0)
        tx_type = 1 if tx_type == 1 else 0

        cat_id = int(pd.to_numeric(r['id_category'], errors='coerce') or 0)
        if valid_cats and cat_id not in valid_cats:
            fallback_cat = 12 if tx_type == 1 else 39
            cat_id = fallback_cat if fallback_cat in valid_cats else next(iter(valid_cats))

        desc_raw = "" if pd.isna(r['desc']) else str(r['desc'])
        desc_clean = re.sub(r'[\x00-\x1f\x7f]+', ' ', desc_raw).strip() or "transaksi"

        amt_val = pd.to_numeric(r['amount'], errors='coerce')
        amt_str = str(int(round(abs(float(amt_val))))) if pd.notna(amt_val) else "0"

        rows.append((raw_id, cat_id, desc_clean, tx_type, int(r['date_num']), amt_str))

    cursor.execute("DELETE FROM TRANSACT;")
    cursor.executemany(
        "INSERT INTO TRANSACT (_id, id_category, desc, type, date, amount) VALUES (?, ?, ?, ?, ?, ?)",
        rows
    )
    conn.commit()
    conn.close()

    optimize_sqlite_for_android(WORK_DB)

def build_ckbak_download_bytes():
    df_t = load_or_seed_transact()
    if not df_t.empty:
        sync_work_db_from_df(df_t)
    elif os.path.exists(WORK_DB):
        optimize_sqlite_for_android(WORK_DB)
    else:
        return None
    with open(WORK_DB, "rb") as f:
        return f.read()

def sync_inv_db_from_dfs(df_port, df_trx):
    conn = sqlite3.connect(INV_DB)
    df_port.to_sql("STOCK_PORTFOLIO", conn, if_exists="replace", index=False)
    df_trx.to_sql("STOCK_TRANSACTIONS", conn, if_exists="replace", index=False)
    conn.commit()
    conn.close()

def ensure_local_dbs_ready():
    if 'dbs_hydrated' not in st.session_state:
        df_t = load_or_seed_transact()
        if not df_t.empty:
            sync_work_db_from_df(df_t)
        if not os.path.exists(INV_DB):
            df_p = get_sheet_df("STOCK_PORTFOLIO", PORT_COLS)
            df_x = get_sheet_df("STOCK_TRANSACTIONS", TRX_COLS)
            if not df_p.empty or not df_x.empty:
                sync_inv_db_from_dfs(df_p, df_x)
        st.session_state.dbs_hydrated = True

# --- PDF HELPERS ---
def extract_pdf_text(reader):
    chunks = []
    for page in reader.pages:
        chunks.append(page.extract_text() or "")
    return "\n".join(chunks)

def _parse_flexible_id_amount(val_str):
    if not val_str:
        return None
    s = re.sub(r'[^0-9.,]', '', str(val_str).strip())
    if not s:
        return None
    if ',' in s and '.' in s:
        if s.rfind(',') > s.rfind('.'):
            s = s.replace('.', '').replace(',', '.')
        else:
            s = s.replace(',', '')
    elif ',' in s:
        parts = s.split(',')
        s = s.replace(',', '.') if len(parts[-1]) == 2 else s.replace(',', '')
    elif '.' in s:
        parts = s.split('.')
        if len(parts[-1]) != 2:
            s = s.replace('.', '')
    try:
        return float(s)
    except ValueError:
        return None

def extract_bca_ending_balance(raw_text, visual_text=""):
    """Mengambil nominal SALDO AKHIR dari Rekening Koran BCA."""
    for source_txt in (visual_text, raw_text):
        if not source_txt:
            continue
        matches = re.findall(
            r'SALDO\s+AKHIR\s*[:=\-]?\s*(?:Rp\.?\s*)?(\d{1,3}(?:[,\.]\d{3})*(?:[,\.]\d{2})?|\d+(?:[,\.]\d{2})?)',
            source_txt,
            flags=re.IGNORECASE,
        )
        if matches:
            val = _parse_flexible_id_amount(matches[-1])
            if val is not None:
                return val
    return None

def extract_cc_statement_total(raw_text, visual_text=""):
    """Mengambil nominal TOTAL TAGIHAN / TAGIHAN BARU dari Billing CC BCA."""
    for source_txt in (visual_text, raw_text):
        if not source_txt:
            continue
        matches = re.findall(
            r'(?:TOTAL\s+TAGIHAN(?:\s+BARU)?|TAGIHAN\s+BARU|NEW\s+BALANCE)\s*[:=\-]?\s*(?:Rp\.?\s*)?(\d{1,3}(?:[,\.]\d{3})*(?:[,\.]\d{2})?|\d+(?:[,\.]\d{2})?)(\s*CR)?',
            source_txt,
            flags=re.IGNORECASE,
        )
        if matches:
            amt_raw, cr_flag = matches[-1]
            if cr_flag and cr_flag.strip().upper() == "CR":
                return 0.0
            val = _parse_flexible_id_amount(amt_raw)
            if val is not None:
                return val
    return None

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
    if tx_type == 1:
        if 'artax' in d or 'gaji' in d or 'pybca' in d: return 3
        elif 'bunga' in d or 'dividen' in d: return 2
        elif 'wd bca' in d or 'setoran' in d or 'cdm' in d or 'switching' in d or 'bi-fast cr' in d: return 41
        elif 'ftscy' in d or 'stockbit' in d or 'rdn' in d or '4994633351' in d: return 42
        elif any(name in d for name in ['laura', 'rizqi', 'jhasperi', 'joni', 'mawaddah', 'dewi', 'hidayatun']): return 7
        else: return 12
    else:
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

def classify_transaction_category(desc, tx_type, custom_rules=None):
    """Prioritaskan aturan kustom dari CATEGORY_RULES sebelum turun ke aturan bawaan."""
    if custom_rules is not None and not custom_rules.empty:
        sub_rules = custom_rules[custom_rules['tx_type'] == int(tx_type)].copy()
        if not sub_rules.empty:
            sub_rules['_kw_len'] = sub_rules['keyword'].astype(str).str.len()
            sub_rules = sub_rules.sort_values(by='_kw_len', ascending=False)
            for _, rule in sub_rules.iterrows():
                if keyword_matches_desc(rule['keyword'], desc):
                    return int(rule['id_category'])
    return get_category_id_v2(desc, tx_type)

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

# --- HEADER BAR: ORNAMEN JAM DI PALING ATAS + TOGGLE TEMA ---
clock_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
  :root {{
    --text: {text_color};
    --muted: {sub_text};
    --border: {border_color};
    --accent: {accent_color};
    --surface: {tab_bg};
  }}
- {{ box-sizing: border-box; }}
  html, body {{
    margin: 0; padding: 0; width: 100%; overflow: hidden;
    background: transparent; color: var(--text);
    font-family: 'DM Sans', sans-serif;
  }}
  .ornament-wrap {{
    width: 100%; display: flex; justify-content: center;
    padding: 2px 0 4px;
  }}
  @media (min-width: 769px) {{
    .ornament-wrap {{
      padding-left: 9%;
    }}
  }}
  .ornament-pill {{
    width: min(100%, 540px); min-height: 44px;
    display: flex; align-items: center; gap: 11px;
    padding: 6px 14px;
    border: 1px solid var(--border);
    border-radius: 18px;
    background: color-mix(in srgb, var(--surface) 58%, transparent);
    cursor: pointer;
    transition: background 0.28s ease, border-color 0.28s ease, transform 0.16s ease;
    user-select: none;
  }}
  .ornament-pill:hover {{
    border-color: var(--accent);
    transform: translateY(-1px);
  }}
  .ornament-pill:active {{
    transform: scale(0.992);
  }}
  .clock-badge {{
    flex: 0 0 auto; display: flex; align-items: baseline; gap: 4px;
    padding-right: 11px; border-right: 1px solid var(--border);
    font-size: 16px; line-height: 1; font-weight: 700;
    letter-spacing: -0.04em; font-variant-numeric: tabular-nums;
    transition: color 0.28s ease, border-color 0.28s ease;
  }}
  .tz-tag {{
    color: var(--muted); font-size: 8px; font-weight: 700; letter-spacing: 0.08em;
  }}
  .content-box {{
    min-width: 0; flex: 1;
  }}
  .headline {{
    font-size: 11px; line-height: 1.3; font-weight: 700;
    letter-spacing: -0.01em; white-space: nowrap;
    overflow: hidden; text-overflow: ellipsis;
    transition: color 0.28s ease;
  }}
  .subline {{
    color: var(--muted); font-size: 9.5px; line-height: 1.3;
    margin-top: 1px; white-space: nowrap;
    overflow: hidden; text-overflow: ellipsis;
    transition: color 0.28s ease;
  }}
  .status-cluster {{
    flex: 0 0 auto; display: flex; align-items: center; gap: 6px;
  }}
  .status-tag {{
    font-size: 8px; font-weight: 700; letter-spacing: 0.07em;
    text-transform: uppercase; color: var(--muted);
    transition: color 0.28s ease;
  }}
  .crash-dot {{
    width: 7px; height: 7px; border-radius: 50%;
    background: #22C55E;
    box-shadow: 0 0 6px rgba(34, 197, 94, 0.35);
    transition: background 0.28s ease, box-shadow 0.28s ease;
  }}
  @keyframes pulseCrash {{
    0%, 100% {{ opacity: 1; transform: scale(1); }}
    50% {{ opacity: 0.45; transform: scale(1.25); }}
  }}
  .is-crashing .crash-dot {{
    animation: pulseCrash 1.2s infinite ease-in-out;
  }}
  @media(max-width:520px) {{
    .ornament-pill {{ min-height: 42px; padding: 5px 11px; border-radius: 15px; gap: 9px; }}
    .clock-badge {{ font-size: 14.5px; padding-right: 8px; }}
    .headline {{ font-size: 10.5px; }}
    .subline {{ font-size: 8.5px; }}
    .status-tag {{ display: none; }}
  }}
</style>
</head>
<body>
<div class="ornament-wrap">
  <div class="ornament-pill" id="pill" onclick="cycleMarketMood()" title="Click to toggle market mood">
    <div class="clock-badge" id="clockBox"><span id="clock">--:--</span><span class="tz-tag">WIB</span></div>
    <div class="content-box">
      <div class="headline" id="headline">Getting the day together...</div>
      <div class="subline" id="subline">A small check-in, nothing more.</div>
    </div>
    <div class="status-cluster">
      <span class="status-tag" id="statusTag">LIVE</span>
      <span class="crash-dot" id="dot"></span>
    </div>
  </div>
</div>
<script>
  const fmt = (opts) => new Intl.DateTimeFormat('id-ID', {{ timeZone:'Asia/Jakarta', ...opts }});
  let crashLevel = 0;

  function getScheduleMoment() {{
    const parts = Object.fromEntries(fmt({{hour:'2-digit', minute:'2-digit', hourCycle:'h23'}})
      .formatToParts(new Date()).map(p => [p.type, p.value]));
    const h = Number(parts.hour), m = Number(parts.minute);
    const weekday = fmt({{weekday:'short'}}).format(new Date()).toLowerCase();
    const weekend = weekday.startsWith('sab') || weekday.startsWith('min');

    if (weekend) return {{
      title: 'Market is off. Lu juga boleh.',
      sub: 'A small check-in, nothing more.'
    }};
    if (h < 9) return {{
      title: '09.00 is coming. So is the coffee, hopefully.',
      sub: 'Pre-market calm.'
    }};
    if (h < 12) return {{
      title: 'Market is open. Behave yourself.',
      sub: 'Session I active.'
    }};
    if (h < 13 || (h === 13 && m < 30)) return {{
      title: 'Go eat. The market can wait.',
      sub: 'No financial decision needs to be made while hungry.'
    }};
    if (h < 16) return {{
      title: 'Afternoon session. Keep it together.',
      sub: 'Session II active.'
    }};
    if (h < 19) return {{
      title: 'Market closed. Lu boleh ikut tutup laptop.',
      sub: 'Today’s closing price: enough work done.'
    }};
    return {{
      title: 'Portfolio can wait. Life is happening.',
      sub: 'After hours.'
    }};
  }}

  const crashStates = [
    null,
    {{
      title: '-2.4%  —  Mild pullback. Nothing dramatic.',
      sub: 'A red candle is not a personal attack. Stay disciplined.',
      tag: '-2.4%',
      textColor: '#D97706',
      borderColor: 'rgba(217, 119, 6, 0.42)',
      bgColor: 'rgba(217, 119, 6, 0.06)',
      dotColor: '#D97706',
      glow: 'rgba(217, 119, 6, 0.45)',
      crashing: false
    }},
    {{
      title: '-6.8%  —  Heavy sell-off. Screen turning crimson.',
      sub: 'Long-term investor, short-term screen time. Interesting.',
      tag: '-6.8%',
      textColor: '#E11D48',
      borderColor: 'rgba(225, 29, 72, 0.55)',
      bgColor: 'rgba(225, 29, 72, 0.10)',
      dotColor: '#E11D48',
      glow: 'rgba(225, 29, 72, 0.55)',
      crashing: false
    }},
    {{
      title: '-14.2%  —  Market crash. Trading halt territory.',
      sub: 'Close the laptop. Your portfolio has not developed new feelings.',
      tag: 'CRASH',
      textColor: '#DC2626',
      borderColor: 'rgba(220, 38, 38, 0.78)',
      bgColor: 'rgba(220, 38, 38, 0.16)',
      dotColor: '#DC2626',
      glow: 'rgba(220, 38, 38, 0.75)',
      crashing: true
    }}
  ];

  function renderState() {{
    const pill = document.getElementById('pill');
    const clockBox = document.getElementById('clockBox');
    const headline = document.getElementById('headline');
    const subline = document.getElementById('subline');
    const statusTag = document.getElementById('statusTag');
    const dot = document.getElementById('dot');

    if (crashLevel === 0) {{
      const moment = getScheduleMoment();
      pill.classList.remove('is-crashing');
      pill.style.borderColor = '';
      pill.style.background = '';
      clockBox.style.color = '';
      headline.style.color = '';
      headline.textContent = moment.title;
      subline.textContent = moment.sub;
      statusTag.style.color = '';
      statusTag.textContent = 'LIVE';
      dot.style.background = '#22C55E';
      dot.style.boxShadow = '0 0 6px rgba(34, 197, 94, 0.35)';
    }} else {{
      const s = crashStates[crashLevel];
      pill.classList.toggle('is-crashing', s.crashing);
      pill.style.borderColor = s.borderColor;
      pill.style.background = s.bgColor;
      clockBox.style.color = s.textColor;
      headline.style.color = s.textColor;
      headline.textContent = s.title;
      subline.textContent = s.sub;
      statusTag.style.color = s.textColor;
      statusTag.textContent = s.tag;
      dot.style.background = s.dotColor;
      dot.style.boxShadow = `0 0 8px ${{s.glow}}`;
    }}
  }}

  function updateClock() {{
    const parts = Object.fromEntries(fmt({{hour:'2-digit', minute:'2-digit', hourCycle:'h23'}})
      .formatToParts(new Date()).map(p => [p.type, p.value]));
    document.getElementById('clock').textContent = `${{parts.hour}}:${{parts.minute}}`;
    if (crashLevel === 0) {{
      renderState();
    }}
  }}

  function cycleMarketMood() {{
    crashLevel = (crashLevel + 1) % crashStates.length;
    renderState();
  }}

  updateClock();
  setInterval(updateClock, 1000);
</script>
</body>
</html>
"""

col_head1, col_head2 = st.columns([10, 1])
with col_head1:
    components.html(clock_html, height=52, scrolling=False)
with col_head2:
    toggle_label = "☾" if st.session_state.theme == 'Light' else "☀"
    if st.button(toggle_label, help="Ganti tema terang / gelap"):
        st.session_state.theme = 'Dark' if st.session_state.theme == 'Light' else 'Light'
        st.rerun()

st.markdown("<h1>Financial Dashboard</h1>", unsafe_allow_html=True)
st.markdown(
    "<p class='app-subtitle'>PERSONAL FINANCE  •  CASH FLOW  •  INVESTMENTS</p>",
    unsafe_allow_html=True
)

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
            detected_bca_ending = None
            detected_cc_total = None
            
            # --- PROSES MUTASI BCA & KARTU KREDIT ---
            if uploaded_bank_files or uploaded_cc_files:
                df_transact = load_or_seed_transact()
                custom_rules_df = load_category_rules()
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
                    bank_balance_candidates = []
                    for uploaded_file in uploaded_bank_files:
                        temp_path = f"temp_{uploaded_file.name}"
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        reader = pypdf.PdfReader(temp_path)
                        raw_pdf_text = extract_pdf_text(reader)
                        visual_pdf_text = extract_pdf_visual_lines(reader)
                        statement_year = infer_statement_year(raw_pdf_text)
                        if not raw_pdf_text.strip():
                            st.warning(f"Tidak ada teks yang bisa dibaca dari PDF rekening koran: {uploaded_file.name}.")
                            os.remove(temp_path)
                            continue

                        ending_bal = extract_bca_ending_balance(raw_pdf_text, visual_pdf_text)
                        max_stmt_ts = 0

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
                            if timestamp_ms > max_stmt_ts:
                                max_stmt_ts = timestamp_ms
                            desc = clean_desc_v3(b_str)
                            cat_id = classify_transaction_category(desc, tx_type, custom_rules_df)
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

                        if ending_bal is not None:
                            bank_balance_candidates.append((max_stmt_ts, ending_bal))
                        os.remove(temp_path)

                    if bank_balance_candidates:
                        bank_balance_candidates.sort(key=lambda x: x[0])
                        detected_bca_ending = bank_balance_candidates[-1][1]

                if uploaded_cc_files:
                    months_map = {'JAN':1, 'FEB':2, 'MAR':3, 'APR':4, 'MEI':5, 'JUN':6, 'JUL':7, 'AUG':8, 'SEP':9, 'OCT':10, 'NOV':11, 'DEC':12, 'AGU':8, 'AGT':8, 'OKT':10, 'NOP':11, 'DES':12}
                    cc_total_candidates = []
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
                            visual_cc_text = extract_pdf_visual_lines(reader)
                            statement_year = infer_statement_year(text)
                            if not text.strip():
                                continue

                            cc_stmt_total = extract_cc_statement_total(text, visual_cc_text)
                            max_cc_ts = 0

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
                                        if timestamp_ms > max_cc_ts:
                                            max_cc_ts = timestamp_ms
                                        cleaned_cc_desc = clean_desc_v3(desc)
                                        cat_id = classify_transaction_category(cleaned_cc_desc, 0, custom_rules_df)
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

                            if cc_stmt_total is not None:
                                cc_total_candidates.append((max_cc_ts, cc_stmt_total))
                        finally:
                            if os.path.exists(temp_path):
                                os.remove(temp_path)

                    if cc_total_candidates:
                        cc_total_candidates.sort(key=lambda x: x[0])
                        detected_cc_total = cc_total_candidates[-1][1]

                if new_bank_rows:
                    df_transact = pd.concat([df_transact, pd.DataFrame(new_bank_rows)], ignore_index=True)
                    save_sheet_df(df_transact, "TRANSACT", TRANSACT_COLS)
                    sync_work_db_from_df(df_transact)

                if detected_bca_ending is not None or detected_cc_total is not None:
                    curr_pos = load_cash_position()
                    new_saldo_bca = detected_bca_ending if detected_bca_ending is not None else curr_pos['saldo_bca']
                    new_tagihan_cc = detected_cc_total if detected_cc_total is not None else curr_pos['tagihan_cc']
                    save_cash_position(
                        new_saldo_bca,
                        new_tagihan_cc,
                        limit_cc_plafon=curr_pos.get('limit_cc_plafon', DEFAULT_CC_LIMIT),
                        keterangan="Sinkronisasi PDF"
                    )

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

            extra_cash_notes = []
            if detected_bca_ending is not None:
                extra_cash_notes.append(f"Saldo Akhir BCA: {fmt_rp(detected_bca_ending)}")
            if detected_cc_total is not None:
                extra_cash_notes.append(f"Tagihan CC: {fmt_rp(detected_cc_total)}")
            extra_str = f" | {' | '.join(extra_cash_notes)}" if extra_cash_notes else ""

            st.success(f"Sinkronisasi Google Sheets Selesai! | Transaksi Bank: {fmt_int(added_count)} (Duplikat: {fmt_int(duplicate_count)}) | Portofolio: {fmt_int(stockbit_count)} baris | Transaksi Harian: {fmt_int(stockbit_trx_count)} terekstrak{extra_str}")

    ensure_local_dbs_ready()
    ts_download = get_wib_timestamp_label()
    ckbak_bytes = build_ckbak_download_bytes()

    st.write("")
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        if ckbak_bytes is not None:
            st.download_button(
                label="Download DB Catatan Keuangan (.ckbak)",
                data=ckbak_bytes,
                file_name=f"CK({ts_download}).ckbak",
                mime="application/octet-stream",
                use_container_width=True
            )
    with col_dl2:
        if os.path.exists(INV_DB):
            with open(INV_DB, "rb") as f:
                inv_bytes = f.read()
            st.download_button(
                label="Download DB Investasi (.db)",
                data=inv_bytes,
                file_name=f"INV({ts_download}).db",
                mime="application/octet-stream",
                use_container_width=True
            )

# --- FUNGSI DASHBOARD KEUANGAN UTAMA (TAB 2) ---
def render_dashboard():
    st.markdown("<h3>Analisis Cashflow</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: {sub_text}; font-size: 0.75rem; letter-spacing: 1px;'>[ FINANCIAL METRICS INTERFACE ]</p>", unsafe_allow_html=True)
    st.write("")

    if 'cat_editor_rev' not in st.session_state:
        st.session_state.cat_editor_rev = 0

    df = load_or_seed_transact()
    df_port_for_health = get_sheet_df("STOCK_PORTFOLIO", PORT_COLS)

    # --- POSISI AKTUAL CASH (SALDO AKHIR BCA - LIMIT CC TERPAKAI) ---
    cash_pos = load_cash_position()
    saldo_bca_val = cash_pos['saldo_bca']
    limit_used_val = cash_pos['tagihan_cc']
    limit_plafon_val = cash_pos.get('limit_cc_plafon', DEFAULT_CC_LIMIT)

    health = analyze_loan_health(
        saldo_bca=saldo_bca_val,
        limit_used=limit_used_val,
        limit_plafon=limit_plafon_val,
        df_transact=df,
        df_port=df_port_for_health
    )
    aktual_cash_val = health['aktual_cash']

    st.markdown("<div class='metric-section-label'>Posisi Aktual Cash (BCA − Limit CC Terpakai)</div>", unsafe_allow_html=True)
    col_cash1, col_cash2, col_cash3 = st.columns(3)
    col_cash1.metric("Saldo Akhir BCA", fmt_rp(saldo_bca_val))
    col_cash2.metric(
        "Limit CC Terpakai",
        fmt_rp(limit_used_val),
        delta=f"Sisa Limit: {fmt_rp(health['sisa_limit'])}",
        delta_color="off"
    )
    col_cash3.metric(
        "Aktual Cash",
        fmt_rp(aktual_cash_val),
        delta="Surplus Kas" if aktual_cash_val >= 0 else "Defisit Likuiditas",
        delta_color="normal" if aktual_cash_val >= 0 else "inverse"
    )

    # --- ANALISIS KESEHATAN PINJAMAN & LIKUIDITAS REAL-TIME ---
    st.markdown("<div class='metric-section-label secondary'>Analisis Kesehatan Pinjaman & Likuiditas</div>", unsafe_allow_html=True)
    h1, h2, h3, h4 = st.columns(4)
    h1.metric(
        "Cash Coverage Ratio",
        fmt_pct(health['coverage_pct']),
        delta=health['coverage_status'],
        delta_color=health['coverage_color']
    )
    h2.metric(
        "Credit Utilization (CUR)",
        fmt_pct(health['cur_pct']),
        delta=health['cur_status'],
        delta_color=health['cur_color']
    )
    h3.metric(
        "Eksposur CC / Income",
        fmt_pct(health['dti_pct']) if health['dti_pct'] is not None else "N/A",
        delta=health['dti_status'],
        delta_color=health['dti_color']
    )
    h4.metric(
        "Net Liquid Worth",
        fmt_rp(health['net_liquid_worth']),
        delta=health['solvency_status'],
        delta_color=health['solvency_color']
    )

    insights_html = "".join(f"<li>{item}</li>" for item in health['insights'])
    st.markdown(
        f"""
        <div class="health-diagnosis-card">
            <div class="health-diagnosis-title">Diagnosis Kesehatan Pinjaman & Likuiditas (Plafon CC {fmt_rp(limit_plafon_val)})</div>
            <ul class="health-diagnosis-list">
                {insights_html}
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.expander(f"Update Manual Saldo BCA / Limit CC Terpakai  •  Terakhir: {cash_pos['updated_at']}"):
        with st.form("form_update_aktual_cash"):
            u_col1, u_col2, u_col3 = st.columns(3)
            with u_col1:
                input_saldo_bca = st.number_input(
                    "Saldo Akhir BCA (Rp)",
                    min_value=0.0,
                    value=float(saldo_bca_val),
                    step=50000.0
                )
            with u_col2:
                input_limit_used = st.number_input(
                    "Limit CC Terpakai (Rp)",
                    min_value=0.0,
                    value=float(limit_used_val),
                    step=50000.0,
                    help="Total limit kartu kredit yang sudah terpakai (termasuk pokok cicilan berjalan)."
                )
            with u_col3:
                input_limit_plafon = st.number_input(
                    "Plafon Limit CC (Rp)",
                    min_value=1000000.0,
                    value=float(limit_plafon_val),
                    step=1000000.0,
                    help="Total batas limit kartu kredit BCA (default Rp 15.000.000)."
                )
            if st.form_submit_button("Simpan & Hitung Ulang Kesehatan Finansial", type="primary", use_container_width=True):
                save_cash_position(
                    input_saldo_bca,
                    input_limit_used,
                    limit_cc_plafon=input_limit_plafon,
                    keterangan="Update Manual"
                )
                st.rerun()

    st.divider()
    
    catalog = get_category_catalog()
    cat_map = catalog['id_to_name']
    
    if not df.empty:
        df['_id'] = pd.to_numeric(df['_id'], errors='coerce').fillna(0).astype(int)
        df['id_category'] = pd.to_numeric(df['id_category'], errors='coerce').fillna(0).astype(int)
        df['Kategori'] = df['id_category'].map(cat_map).fillna('Lain-lain')
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
        else:
            st.info("Tidak ada data pengeluaran untuk periode ini.")

        # --- TABEL INTERAKTIF KLASIFIKASI TRANSAKSI (FILTER & SORT ALA EXCEL) ---
        st.markdown("<h4>Rincian Transaksi & Ubah Kategori</h4>", unsafe_allow_html=True)
        st.markdown(
            f"<p style='text-align: center; color: {sub_text}; font-size: 0.82rem; margin-top: -0.25rem;'>"
            "Filter berdasarkan jenis, kategori, atau kata kunci keterangan, lalu klik kolom <b>Kategori</b> untuk mengubah klasifikasi & menyimpannya sebagai aturan otomatis."
            "</p>",
            unsafe_allow_html=True
        )

        f_r1_c1, f_r1_c2, f_r1_c3 = st.columns([1.25, 1.15, 1.4])
        with f_r1_c1:
            scope_label_mo = f"Bulan Terpilih ({months_dict.get(selected_month)} {selected_year})"
            scope_label_yr = f"Semua Bulan ({selected_year})"
            scope_label_all = "Semua Waktu"
            scope_mode = st.selectbox(
                "Cakupan Waktu",
                [scope_label_mo, scope_label_yr, scope_label_all],
                key="dash_tx_scope_filter"
            )
        with f_r1_c2:
            tx_filter_mode = st.selectbox(
                "Filter Jenis",
                ["Semua", "Pengeluaran", "Pemasukan"],
                key="dash_tx_type_filter"
            )
        with f_r1_c3:
            sort_mode = st.selectbox(
                "Urutkan Data",
                [
                    "Tanggal (Terbaru → Terlama)",
                    "Tanggal (Terlama → Terbaru)",
                    "Jumlah (Terbesar → Terkecil)",
                    "Jumlah (Terkecil → Terbesar)",
                    "Keterangan (A → Z)",
                    "Kategori (A → Z)",
                ],
                key="dash_tx_sort_mode"
            )

        f_r2_c1, f_r2_c2 = st.columns([1.35, 1.65])
        with f_r2_c1:
            selected_cats = st.multiselect(
                "Filter Kategori (Ketik / pilih lebih dari satu)",
                options=catalog['all_options'],
                default=[],
                placeholder="Semua Kategori...",
                key="dash_tx_cat_multiselect"
            )
        with f_r2_c2:
            desc_query = st.text_input(
                "Cari Keterangan / Deskripsi",
                value="",
                placeholder="Ketik kata kunci keterangan (misal: qris, grab, artax, kopi)...",
                key="dash_tx_desc_search"
            )

        # 1. Cakupan waktu
        if scope_mode == scope_label_all:
            df_edit_src = df.copy()
        elif scope_mode == scope_label_yr:
            df_edit_src = df_year.copy()
        else:
            df_edit_src = df_month.copy()

        total_scope_rows = len(df_edit_src)

        # 2. Filter Jenis Transaksi
        if tx_filter_mode == "Pengeluaran":
            df_edit_src = df_edit_src[df_edit_src['type'] == 0]
            dropdown_opts = catalog['expense_options']
        elif tx_filter_mode == "Pemasukan":
            df_edit_src = df_edit_src[df_edit_src['type'] == 1]
            dropdown_opts = catalog['income_options']
        else:
            dropdown_opts = catalog['all_options']

        # 3. Filter Kategori (Multi-select seperti Excel)
        if selected_cats:
            df_edit_src = df_edit_src[df_edit_src['Kategori'].isin(selected_cats)]

        # 4. Filter Pencarian Keterangan / Deskripsi
        clean_desc_q = desc_query.strip().lower()
        if clean_desc_q:
            df_edit_src = df_edit_src[
                df_edit_src['Deskripsi'].str.lower().str.contains(clean_desc_q, regex=False, na=False)
            ]

        # 5. Pengurutan (Sorting)
        if not df_edit_src.empty:
            if sort_mode == "Tanggal (Terlama → Terbaru)":
                df_edit_src = df_edit_src.sort_values(by=['datetime', '_id'], ascending=[True, True])
            elif sort_mode == "Jumlah (Terbesar → Terkecil)":
                df_edit_src = df_edit_src.sort_values(by=['Jumlah', 'datetime'], ascending=[False, False])
            elif sort_mode == "Jumlah (Terkecil → Terbesar)":
                df_edit_src = df_edit_src.sort_values(by=['Jumlah', 'datetime'], ascending=[True, False])
            elif sort_mode == "Keterangan (A → Z)":
                df_edit_src = df_edit_src.sort_values(
                    by=['Deskripsi', 'datetime'],
                    ascending=[True, False],
                    key=lambda col: col.str.lower() if col.name == 'Deskripsi' else col
                )
            elif sort_mode == "Kategori (A → Z)":
                df_edit_src = df_edit_src.sort_values(
                    by=['Kategori', 'datetime'],
                    ascending=[True, False],
                    key=lambda col: col.str.lower() if col.name == 'Kategori' else col
                )
            else:
                df_edit_src = df_edit_src.sort_values(by=['datetime', '_id'], ascending=[False, False])

        filtered_sum = float(df_edit_src['Jumlah'].sum()) if not df_edit_src.empty else 0.0
        st.markdown(
            f"""
            <div class="filter-summary-bar">
                <span>Menampilkan <strong>{fmt_int(len(df_edit_src))}</strong> dari <strong>{fmt_int(total_scope_rows)}</strong> transaksi</span>
                <span>Total Nominal Hasil Filter: <strong>{fmt_rp(filtered_sum)}</strong></span>
            </div>
            """,
            unsafe_allow_html=True
        )

        if not df_edit_src.empty:
            df_edit_src = df_edit_src.reset_index(drop=True)
            df_editor_input = pd.DataFrame({
                '_id': df_edit_src['_id'].astype(int),
                'Tanggal': df_edit_src['datetime'].dt.strftime('%d/%m/%Y'),
                'Jenis': df_edit_src['type'].map({0: 'Pengeluaran', 1: 'Pemasukan'}).fillna('Pengeluaran'),
                'Kategori': df_edit_src['Kategori'],
                'Deskripsi': df_edit_src['Deskripsi'],
                'Jumlah (Rp)': df_edit_src['Jumlah'].apply(fmt_int),
            })

            cat_sig = "_".join(sorted(selected_cats)) if selected_cats else "ALL"
            editor_key = (
                f"tx_cat_editor_{selected_year}_{selected_month}_{scope_mode}_"
                f"{tx_filter_mode}_{cat_sig}_{clean_desc_q}_{sort_mode}_{st.session_state.cat_editor_rev}"
            )
            edited_df = st.data_editor(
                df_editor_input,
                key=editor_key,
                use_container_width=True,
                hide_index=True,
                disabled=['_id', 'Tanggal', 'Jenis', 'Deskripsi', 'Jumlah (Rp)'],
                column_config={
                    '_id': st.column_config.NumberColumn('ID', width='small'),
                    'Tanggal': st.column_config.TextColumn('Tanggal', width='small'),
                    'Jenis': st.column_config.TextColumn('Jenis', width='small'),
                    'Kategori': st.column_config.SelectboxColumn(
                        'Kategori',
                        options=dropdown_opts,
                        required=True,
                        width='medium'
                    ),
                    'Deskripsi': st.column_config.TextColumn('Deskripsi', width='large'),
                    'Jumlah (Rp)': st.column_config.TextColumn('Jumlah (Rp)', width='small'),
                }
            )

            if st.button("Simpan Perubahan Kategori & Jadikan Aturan Otomatis", type="primary", use_container_width=True):
                changed_rules = []
                direct_updates = {}
                for idx in range(len(df_editor_input)):
                    old_cat = str(df_editor_input.loc[idx, 'Kategori']).strip()
                    new_cat = str(edited_df.loc[idx, 'Kategori']).strip()
                    if old_cat != new_cat and new_cat:
                        tx_id = int(df_editor_input.loc[idx, '_id'])
                        tx_t = 1 if df_editor_input.loc[idx, 'Jenis'] == 'Pemasukan' else 0
                        desc_val = str(df_editor_input.loc[idx, 'Deskripsi'])
                        target_cat_id = resolve_category_id(new_cat, tx_t, catalog)
                        kw = suggest_rule_keyword(desc_val)

                        direct_updates[tx_id] = target_cat_id
                        changed_rules.append({
                            'keyword': kw,
                            'tx_type': tx_t,
                            'id_category': target_cat_id,
                            'category_name': new_cat,
                        })

                if changed_rules:
                    with st.spinner("Menyimpan aturan & memperbarui seluruh transaksi historis..."):
                        _, affected_rows = upsert_rules_and_apply_retroactive(
                            df[['_id', 'id_category', 'desc', 'type', 'date', 'amount']],
                            changed_rules,
                            direct_id_updates=direct_updates
                        )
                        st.session_state.cat_editor_rev += 1
                        st.success(f"{len(changed_rules)} aturan disimpan & {fmt_int(affected_rows)} transaksi diperbarui!")
                        st.rerun()
                else:
                    st.info("Belum ada perubahan kategori pada tabel di atas.")
        else:
            st.info("Tidak ada transaksi yang cocok dengan filter saat ini.")

        # --- PANEL KELOLA ATURAN KUSTOM (SELF-LEARNING RULES) ---
        df_rules_curr = load_category_rules()
        with st.expander(f"Kelola Aturan Kategori Otomatis ({len(df_rules_curr)} aturan aktif)"):
            st.markdown(
                f"<p style='color: {sub_text}; font-size: 0.83rem;'>"
                "Tambah kata kunci kustom atau sesuaikan kata kunci yang sudah tersimpan (misalnya mempersingkat nama merchant agar mencakup semua cabang)."
                "</p>",
                unsafe_allow_html=True
            )
            with st.form("form_add_custom_rule"):
                r_col1, r_col2, r_col3 = st.columns([1.2, 2, 1.5])
                with r_col1:
                    rule_type_label = st.selectbox("Jenis Transaksi", ["Pengeluaran", "Pemasukan"])
                with r_col2:
                    rule_kw_input = st.text_input("Kata Kunci Deskripsi", placeholder="contoh: kopi kenangan / artax / grab")
                with r_col3:
                    rule_cat_choice = st.selectbox("Kategori Tujuan", catalog['all_options'])

                if st.form_submit_button("Simpan Aturan & Terapkan ke Semua Histori", type="primary", use_container_width=True):
                    clean_kw = str(rule_kw_input or '').strip().lower()
                    if len(clean_kw) < 2:
                        st.error("Kata kunci minimal 2 karakter.")
                    else:
                        tx_t_val = 1 if rule_type_label == "Pemasukan" else 0
                        target_cid = resolve_category_id(rule_cat_choice, tx_t_val, catalog)
                        _, affected_rows = upsert_rules_and_apply_retroactive(
                            df[['_id', 'id_category', 'desc', 'type', 'date', 'amount']],
                            [{
                                'keyword': clean_kw,
                                'tx_type': tx_t_val,
                                'id_category': target_cid,
                                'category_name': rule_cat_choice,
                            }]
                        )
                        st.session_state.cat_editor_rev += 1
                        st.success(f"Aturan '{clean_kw}' -> '{rule_cat_choice}' disimpan ({fmt_int(affected_rows)} transaksi diperbarui)!")
                        st.rerun()

            if not df_rules_curr.empty:
                st.markdown("**Daftar Aturan Tersimpan (Edit atau Hapus Baris):**")
                rules_disp = pd.DataFrame({
                    'Kata Kunci': df_rules_curr['keyword'],
                    'Jenis': df_rules_curr['tx_type'].map({0: 'Pengeluaran', 1: 'Pemasukan'}).fillna('Pengeluaran'),
                    'Kategori': df_rules_curr['category_name'],
                    'Diperbarui': df_rules_curr['updated_at'],
                })
                edited_rules_df = st.data_editor(
                    rules_disp,
                    key=f"rules_manager_editor_{st.session_state.cat_editor_rev}",
                    use_container_width=True,
                    hide_index=True,
                    num_rows="dynamic",
                    disabled=['Diperbarui'],
                    column_config={
                        'Kata Kunci': st.column_config.TextColumn('Kata Kunci', required=True),
                        'Jenis': st.column_config.SelectboxColumn('Jenis', options=['Pengeluaran', 'Pemasukan'], required=True),
                        'Kategori': st.column_config.SelectboxColumn('Kategori', options=catalog['all_options'], required=True),
                        'Diperbarui': st.column_config.TextColumn('Diperbarui'),
                    }
                )
                if st.button("Simpan Perubahan Daftar Aturan", use_container_width=True):
                    now_wib = datetime.datetime.now(WIB_TZ).strftime("%d/%m/%Y %H:%M WIB")
                    rebuilt_rows = []
                    for _, r in edited_rules_df.iterrows():
                        kw_clean = str(r.get('Kata Kunci', '')).strip().lower()
                        if not kw_clean or kw_clean == 'none':
                            continue
                        tx_t_val = 1 if str(r.get('Jenis', '')) == 'Pemasukan' else 0
                        cat_nm = str(r.get('Kategori', '')).strip()
                        cid = resolve_category_id(cat_nm, tx_t_val, catalog)
                        rebuilt_rows.append({
                            'keyword': kw_clean,
                            'tx_type': tx_t_val,
                            'id_category': cid,
                            'category_name': cat_nm,
                            'updated_at': str(r.get('Diperbarui') or now_wib),
                        })
                    new_rules_df = pd.DataFrame(rebuilt_rows, columns=RULES_COLS)
                    save_category_rules(new_rules_df)
                    if rebuilt_rows:
                        _, affected_rows = upsert_rules_and_apply_retroactive(
                            df[['_id', 'id_category', 'desc', 'type', 'date', 'amount']],
                            rebuilt_rows
                        )
                        st.success(f"Daftar aturan diperbarui & {fmt_int(affected_rows)} transaksi historis disinkronkan!")
                    else:
                        st.success("Semua aturan kustom berhasil dihapus.")
                    st.session_state.cat_editor_rev += 1
                    st.rerun()
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

        st.markdown("<div class='metric-section-label'>Nilai Portofolio</div>", unsafe_allow_html=True)
        value_cols = st.columns(3, gap="large")
        value_cols[0].metric("Total Modal", fmt_rp(tot_buy))
        value_cols[1].metric("Total Aset", fmt_rp(tot_mkt))
        value_cols[2].metric(
            "Unrealized P/L",
            fmt_rp(tot_unreal),
            delta=fmt_pct(simple_ret_pct, signed=True)
        )

        st.markdown("<div class='metric-section-label secondary'>Kinerja & Pendapatan</div>", unsafe_allow_html=True)
        performance_cols = st.columns(3, gap="large")
        performance_cols[0].metric("Total Dividen", fmt_rp(tot_div))
        performance_cols[1].metric("XIRR", fmt_pct(xirr_pct))
        performance_cols[2].metric("CAGR", fmt_pct(cagr_pct))

        st.divider()
        
        sub_tab = st.radio(
            "Pilih Tampilan Dashboard",
            ["Ringkasan Portofolio", "Rincian Transaksi Harian", "Perkembangan Nilai Saham", "Grafik Return (XIRR)"],
            horizontal=True
        )
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
        
        elif sub_tab == "Perkembangan Nilai Saham":
            st.markdown("<h4>Market Value vs Buying Value (Rp)</h4>", unsafe_allow_html=True)
            chart_periods = sorted(df_port['period_str'].astype(str).unique(), key=period_str_to_end_date)
            val_records = []
            for p in chart_periods:
                sub_df = df_port[(df_port['period_str'] == p) & (df_port['symbol'] != 'IDR')]
                if sub_df.empty:
                    sub_df = df_port[df_port['period_str'] == p]
                b_row = float(sub_df['total_modal'].iloc[0]) if not sub_df.empty else 0.0
                m_row = float(sub_df['total_aset'].iloc[0]) if not sub_df.empty else 0.0

                b_val = b_row if b_row > 0 else sub_df['buy_value'].sum()
                m_val = m_row if m_row > 0 else sub_df['market_value'].sum()
                val_records.append({
                    'period_str': p,
                    'Market Value': round(m_val),
                    'Buying Value': round(b_val)
                })

            df_val_source = pd.DataFrame(val_records)
            if not df_val_source.empty:
                val_chart_data = df_val_source.melt(id_vars='period_str', var_name='Metrik', value_name='Nilai (Rp)')
                val_chart_data['Nilai_Fmt'] = val_chart_data['Nilai (Rp)'].apply(fmt_rp)

                chart_val = alt.Chart(val_chart_data).mark_line(strokeWidth=2.5, point=True).encode(
                    x=alt.X('period_str:N', sort=None, title=None, axis=alt.Axis(labelColor=chart_text)),
                    y=alt.Y('Nilai (Rp):Q', title=None, axis=alt.Axis(labelColor=chart_text, format=',.0f')),
                    color=alt.Color(
                        'Metrik:N',
                        scale=alt.Scale(domain=['Market Value', 'Buying Value'], range=[text_color, '#8C8C8C']),
                        legend=alt.Legend(title=None, orient='top', labelColor=chart_text)
                    ),
                    strokeDash=alt.StrokeDash(
                        'Metrik:N',
                        scale=alt.Scale(domain=['Market Value', 'Buying Value'], range=[[1, 0], [5, 4]]),
                        legend=None
                    ),
                    tooltip=[
                        alt.Tooltip('period_str:N', title='Periode'),
                        alt.Tooltip('Metrik:N', title='Kategori'),
                        alt.Tooltip('Nilai_Fmt:N', title='Nilai')
                    ]
                ).properties(height=350, background=chart_bg).configure_view(stroke=None).configure_axis(gridColor=chart_grid)

                st.altair_chart(chart_val, use_container_width=True)
            else:
                st.info("Belum cukup data untuk merender grafik perkembangan nilai saham.")

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
        col_lock_space, col_lock = st.columns([6, 1])
        with col_lock:
            if st.button("Kunci Kembali", use_container_width=True, key="lock_dash"):
                st.session_state.authenticated = False
                st.rerun()
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
        col_lock_space, col_lock = st.columns([6, 1])
        with col_lock:
            if st.button("Kunci Kembali", use_container_width=True, key="lock_inv"):
                st.session_state.authenticated = False
                st.rerun()
        render_investment()

# --- COPYRIGHT FOOTER ---
st.write("")
st.write("")
st.markdown(f"<p style='text-align: center; font-size: 0.75rem; color: {sub_text}; letter-spacing: 1px;'>© 2026 rifqihasperi</p>", unsafe_allow_html=True)
