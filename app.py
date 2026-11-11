import streamlit as st
import pandas as pd
import io
import re
from functools import reduce
import numpy as np

# ==========================================
# 1. PENGATURAN HALAMAN & CSS LUXURY MINIMALIST
# ==========================================
st.set_page_config(page_title="Assistance Bloomberg", page_icon="🏛️", layout="wide")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;500;700&display=swap');
        html, body, [class*="css"]  {
            font-family: 'Inter', sans-serif;
        }
        .premium-title {
            color: #111111;
            font-size: 2.8rem;
            font-weight: 800;
            text-align: center;
            letter-spacing: -1.5px;
            margin-bottom: 0px;
            padding-top: 1rem;
        }
        .premium-subtitle {
            text-align: center;
            color: #666666;
            font-size: 1.1rem;
            font-weight: 300;
            margin-bottom: 3rem;
            letter-spacing: 0.2px;
        }
        .stButton>button {
            background-color: #111111;
            color: #ffffff;
            border-radius: 8px;
            border: 1px solid #111111;
            padding: 14px 24px;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        }
        .stButton>button:hover {
            background-color: #ffffff;
            color: #111111;
            border: 1px solid #111111;
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(0, 0, 0, 0.15);
        }
        div[data-testid="metric-container"] {
            background: #ffffff;
            border-top: 3px solid #111111;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.03);
            border-left: 1px solid #eeeeee;
            border-right: 1px solid #eeeeee;
            border-bottom: 1px solid #eeeeee;
        }
        div[data-testid="metric-container"] label {
            color: #888888 !important;
            font-weight: 500;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .streamlit-expanderHeader {
            font-weight: 600 !important;
            color: #111111 !important;
        }
        pre {
            background-color: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #e9ecef;
            padding: 15px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='premium-title'>Assistance Bloomberg</div>", unsafe_allow_html=True)
st.markdown("<div class='premium-subtitle'>Sistem Ekstraksi Mikro-Panel & Generator Skrip Stata</div>", unsafe_allow_html=True)

# Inisialisasi Memori Aplikasi
if 'master_panel' not in st.session_state:
    st.session_state['master_panel'] = None
if 'freq' not in st.session_state:
    st.session_state['freq'] = None

# ==========================================
# 2. KAMUS NEGARA GLOBAL 
# ==========================================
country_map = {
    'IJ': 'INDONESIA', 'MK': 'MALAYSIA', 'SP': 'SINGAPORE', 'TB': 'THAILAND',
    'PM': 'PHILIPPINES', 'VN': 'VIETNAM', 'CH': 'CHINA', 'CS': 'CHINA', 'CY': 'CHINA',
    'HK': 'HONG KONG', 'TT': 'TAIWAN', 'KS': 'SOUTH KOREA', 'KP': 'SOUTH KOREA', 
    'JP': 'JAPAN', 'JT': 'JAPAN', 'AU': 'AUSTRALIA', 'NZ': 'NEW ZEALAND', 
    'IN': 'INDIA', 'IB': 'INDIA', 'PA': 'PAKISTAN', 'SL': 'SRI LANKA',
    'BD': 'BANGLADESH', 'KZ': 'KAZAKHSTAN', 'MN': 'MONGOLIA', 'NP': 'NEPAL',
    'AB': 'SAUDI ARABIA', 'AE': 'UAE', 'UH': 'UAE', 'AD': 'UAE', 'OM': 'OMAN', 
    'BI': 'BAHRAIN', 'QA': 'QATAR', 'KW': 'KUWAIT', 'KK': 'KUWAIT', 'JR': 'JORDAN', 
    'IL': 'ISRAEL', 'IT': 'ISRAEL', 'LB': 'LEBANON', 'IQ': 'IRAQ', 'IR': 'IRAN', 
    'SY': 'SYRIA', 'YE': 'YEMEN', 'SJ': 'SOUTH AFRICA', 'EY': 'EGYPT', 'EG': 'EGYPT', 
    'NL': 'NIGERIA', 'MA': 'MOROCCO', 'MC': 'MOROCCO', 'KE': 'KENYA', 'KN': 'KENYA',
    'GH': 'GHANA', 'MU': 'MAURITIUS', 'TZ': 'TANZANIA', 'UG': 'UGANDA', 'ZM': 'ZAMBIA', 
    'ZW': 'ZIMBABWE', 'BW': 'BOTSWANA', 'NA': 'NAMIBIA', 'TN': 'TUNISIA', 'DZ': 'ALGERIA',
    'LN': 'UNITED KINGDOM', 'FP': 'FRANCE', 'GY': 'GERMANY', 'GR': 'GERMANY', 
    'IM': 'ITALY', 'SM': 'SPAIN', 'SQ': 'SPAIN', 'SW': 'SWITZERLAND', 'SE': 'SWITZERLAND',
    'NA': 'NETHERLANDS', 'BB': 'BELGIUM', 'SS': 'SWEDEN', 'NO': 'NORWAY', 
    'DC': 'DENMARK', 'FH': 'FINLAND', 'ID': 'IRELAND', 'PT': 'PORTUGAL', 'PL': 'PORTUGAL',
    'AT': 'AUSTRIA', 'AV': 'AUSTRIA', 'GA': 'GREECE', 'LU': 'LUXEMBOURG', 'IS': 'ICELAND', 
    'RM': 'RUSSIA', 'RU': 'RUSSIA', 'PW': 'POLAND', 'PO': 'POLAND', 'CZ': 'CZECH REPUBLIC', 
    'CP': 'CZECH REPUBLIC', 'HB': 'HUNGARY', 'RO': 'ROMANIA', 'BG': 'BULGARIA', 
    'HR': 'CROATIA', 'RS': 'SERBIA', 'SI': 'SLOVENIA', 'SK': 'SLOVAKIA', 
    'EE': 'ESTONIA', 'LV': 'LATVIA', 'LT': 'LITHUANIA', 'UA': 'UKRAINE', 
    'CY': 'CYPRUS', 'MT': 'MALTA', 'TI': 'TURKEY', 'TR': 'TURKEY', 'TU': 'TURKEY',
    'US': 'UNITED STATES', 'UQ': 'UNITED STATES', 'UW': 'UNITED STATES', 'UN': 'UNITED STATES',
    'CN': 'CANADA', 'MM': 'MEXICO', 'BZ': 'BRAZIL', 'AR': 'ARGENTINA', 'CI': 'CHILE', 
    'CB': 'COLOMBIA', 'PE': 'PERU', 'VE': 'VENEZUELA', 'EC': 'ECUADOR', 'UY': 'URUGUAY', 
    'PY': 'PARAGUAY', 'BO': 'BOLIVIA', 'CR': 'COSTA RICA', 'PA': 'PANAMA', 'JM': 'JAMAICA'
}

def get_country_code(ticker):
    parts = str(ticker).split()
    if len(parts) >= 2:
        return parts[-2].upper() if parts[-1].upper() == 'EQUITY' else parts[-1].upper()
    return "UNKNOWN"

# ==========================================
# 3. NAVIGASI SUPER APP (2 TAB)
# ==========================================
tab_etl, tab_stata = st.tabs(["🧹 1. DATA ENGINEERING (ETL)", "💻 2. STATA DO-FILE GENERATOR"])

# ==============================================================================
# ======================== TAB 1: DATA ENGINEERING ==============================
# ==============================================================================
with tab_etl:
    with st.sidebar:
        st.write("### ⚙️ Konfigurasi")
        st.write("---")
        
        with st.expander("🗓️ Frekuensi & Observasi Waktu", expanded=True):
            # 🚀 PEMBARUAN: Menu Dropdown Waktu Tanpa Mengetik
            frekuensi = st.radio("Pilih Frekuensi Data:", ["Kuartalan (Q)", "Tahunan (Y)", "Bulanan (M)"])
            
            c1, c2 = st.columns(2)
            # DARI
            start_year = c1.selectbox("Dari Tahun:", range(1990, 2041), index=28) # Default 2018
            if frekuensi == "Kuartalan (Q)":
                start_sub = c1.selectbox("Dari Kuartal:", ["Q1", "Q2", "Q3", "Q4"], index=3)
                start_period = f"{start_year}{start_sub}"
            elif frekuensi == "Bulanan (M)":
                start_sub = c1.selectbox("Dari Bulan:", [f"{i:02d}" for i in range(1, 13)], index=0)
                start_period = f"{start_year}-{start_sub}"
            else:
                start_period = str(start_year)
                
            # SAMPAI
            end_year = c2.selectbox("Sampai Tahun:", range(1990, 2041), index=33) # Default 2023
            if frekuensi == "Kuartalan (Q)":
                end_sub = c2.selectbox("Sampai Kuartal:", ["Q1", "Q2", "Q3", "Q4"], index=0)
                end_period = f"{end_year}{end_sub}"
            elif frekuensi == "Bulanan (M)":
                end_sub = c2.selectbox("Sampai Bulan:", [f"{i:02d}" for i in range(1, 13)], index=11)
                end_period = f"{end_year}-{end_sub}"
            else:
                end_period = str(end_year)

        with st.expander("🎯 Target Negara", expanded=False):
            opsi_negara = st.radio("Tindakan Target:", ["1. Otomatis", "2. Paksa 1 Negara", "3. Filter Multi-Negara"])
            daftar_negara_unik = sorted(list(set(country_map.values())))
            if "Paksa" in opsi_negara:
                negara_paksaan = st.selectbox("Tujuan Pemaksaan:", daftar_negara_unik, index=None)
                negara_pilihan = []
            elif "Filter" in opsi_negara:
                negara_pilihan = st.multiselect("Pertahankan hanya:", daftar_negara_unik, default=None)
                negara_paksaan = None
            else:
                negara_paksaan = None; negara_pilihan = []

        with st.expander("🌍 Koreksi Sandi Otomatis", expanded=False):
            st.caption("Koreksi paksa kode bursa asing jika diperlukan.")
            default_corrections = pd.DataFrame(columns=["Kode Asing (Ketik)", "Ubah Menjadi Negara"])
            edited_corrections = st.data_editor(default_corrections, num_rows="dynamic", use_container_width=True)
            custom_country_map = {str(row["Kode Asing (Ketik)"]).strip().upper(): str(row["Ubah Menjadi Negara"]).strip().upper() 
                                  for _, row in edited_corrections.iterrows() if pd.notna(row.get("Kode Asing (Ketik)")) and pd.notna(row.get("Ubah Menjadi Negara"))}
                    
        with st.expander("📚 Buku Saku Kode Bloomberg", expanded=False):
            df_kamus = pd.DataFrame(list(country_map.items()), columns=["KODE", "NAMA NEGARA"])
            st.dataframe(df_kamus, hide_index=True, use_container_width=True, height=250)

        with st.expander("🛡️ Proteksi Duplikat", expanded=False):
            opsi_duplikat = st.radio("Pilih Mode Deteksi:", ["Biarkan semua data (Jangan hapus)", "Hapus jika NAMA BANK persis sama", "Hapus jika NILAI DATA sama (Silang Negara/Bank Hantu)"], index=2)

        with st.expander("⚖️ Desain Tabel Stata", expanded=False):
            opsi_panel = st.radio("Format Panel Akhir:", ["Unbalanced (Aman: Pertahankan sel kosong)", "Balanced (Ketat: Tendang bank yang tidak utuh)"], index=0)

    col_up1, col_up2 = st.columns(2)
    with col_up1:
        uploaded_files = st.file_uploader("🏢 1. Unggah Mikro Bloomberg (.xlsx)", type=["xlsx"], accept_multiple_files=True)
    with col_up2:
        uploaded_wb_files = st.file_uploader("🌍 2. Unggah Makro World Bank (.xlsx)", type=["xlsx", "xls"], accept_multiple_files=True, help="Hanya diletakkan di Q4 atau Bulan 12.")

    st.markdown("<br>", unsafe_allow_html=True)
    col_spacer1, col_btn, col_spacer2 = st.columns([1, 2, 1])
    with col_btn:
        mulai_proses = st.button("MULAI PROSES KOMPILASI", use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    if mulai_proses:
        if not uploaded_files:
            st.warning("⚠️ Mohon unggah file Excel Bloomberg terlebih dahulu.")
        else:
            # Simpan frekuensi ke memori untuk Tab Stata
            st.session_state['freq'] = frekuensi
            
            start_period_safe = start_period.replace(":", "").replace("-", "").strip().upper()
            end_period_safe = end_period.replace(":", "").replace("-", "").strip().upper()
            
            if start_period_safe > end_period_safe:
                st.error("🚨 KESALAHAN LOGIKA: Periode 'Dari' tidak boleh lebih besar dari periode 'Sampai'.")
            else:
                end_period_check = end_period_safe + "Z" if len(end_period_safe) == 4 and end_period_safe.isdigit() else end_period_safe
                dict_variabel_dfs_wide = {}
                
                with st.status("🛠️ Mengekstraksi dan Membersihkan Data...", expanded=True) as status:
                    progress_bar = st.progress(0)
                    
                    st.caption("🔍 Membangun Kamus Ingatan Nama Bank...")
                    raw_data_cache = []
                    global_ticker_map = {}
                    
                    for file in uploaded_files:
                        df_raw = pd.read_excel(file, engine='openpyxl')
                        raw_data_cache.append((file.name, df_raw))
                        if 'Ticker' in df_raw.columns and 'Name' in df_raw.columns:
                            df_temp = df_raw.iloc[2:].copy()
                            for _, row in df_temp.iterrows():
                                t = str(row['Ticker']).strip()
                                n = str(row['Name']).strip().upper()
                                if n not in ['NAN', 'NONE', 'NULL', 'NA', ''] and len(n) > 2:
                                    if t not in global_ticker_map: global_ticker_map[t] = n
                                    else:
                                        if len(n) < len(global_ticker_map[t]): global_ticker_map[t] = n
                                            
                    st.caption("📅 Menganalisis frekuensi waktu Bloomberg...")
                    valid_periods_set = set()
                    for fname, df in raw_data_cache:
                        for col in df.columns:
                            if ":" in str(col):
                                raw_period = str(col).split(":", 1)[1].strip().upper()
                                raw_period_safe = raw_period.replace(":", "").replace("-", "")
                                if start_period_safe <= raw_period_safe <= end_period_check:
                                    valid_periods_set.add(raw_period)
                    
                    requested_periods_list = sorted(list(valid_periods_set))
                    if not requested_periods_list:
                        status.update(label="❌ Kesalahan Data", state="error", expanded=True)
                        st.error(f"🚨 TIDAK ADA DATA WAKTU: Tidak ditemukan rentang periode {start_period} s.d {end_period} di file Anda.")
                        st.stop()
                    
                    for i, (fname, df) in enumerate(raw_data_cache):
                        year_cols = [col for col in df.columns if ":" in str(col)]
                        if not year_cols: continue
                            
                        raw_var_name = str(year_cols[0]).split(":")[0].strip()
                        clean_var_name = re.sub(r'[^a-zA-Z0-9_]', '_', raw_var_name).lower().strip('_')
                        
                        df = df.drop([0, 1]).reset_index(drop=True)
                        df['country_code'] = df['Ticker'].apply(get_country_code)
                        df['country'] = df['country_code'].map(custom_country_map).fillna(df['country_code'].map(country_map)).fillna(df['country_code'])
                        df = df.rename(columns={'Name': 'bank'})
                        
                        df['Ticker_Clean'] = df['Ticker'].astype(str).str.strip()
                        df['bank'] = df['bank'].astype(str).str.strip().str.upper()
                        
                        mask_kosong = df['bank'].isin(['NAN', 'NONE', 'NULL', 'NA', ''])
                        df.loc[mask_kosong, 'bank'] = df.loc[mask_kosong, 'Ticker_Clean'].map(global_ticker_map)
                        
                        mask_invalid_name = (df['bank'].isna() | df['bank'].isin(['NAN', 'NONE', 'NULL', 'NA', '']) | df['bank'].astype(str).str.contains(' EQUITY', case=False, na=False))
                        df = df[~mask_invalid_name].copy()
                        df['country'] = df['country'].astype(str).str.strip().str.upper()
                        
                        if "Paksa" in opsi_negara and negara_paksaan: df['country'] = negara_paksaan
                        elif "Filter" in opsi_negara and negara_pilihan:
                            df = df[df['country'].isin(negara_pilihan)]
                            if df.empty: continue
                        
                        rename_dict = {col: str(col).split(":", 1)[1].strip().upper() for col in year_cols if str(col).split(":", 1)[1].strip().upper() in requested_periods_list}
                        for col in rename_dict.keys(): df[col] = pd.to_numeric(df[col], errors='coerce')
                            
                        df = df.rename(columns=rename_dict)
                        for per in requested_periods_list:
                            if per not in df.columns: df[per] = np.nan
                        
                        df_wide = df[['country', 'bank'] + requested_periods_list]
                        if clean_var_name not in dict_variabel_dfs_wide: dict_variabel_dfs_wide[clean_var_name] = []
                        dict_variabel_dfs_wide[clean_var_name].append(df_wide)
                        progress_bar.progress((i + 1) / len(uploaded_files))
                    
                    st.caption("🔄 Mengonsolidasi & Membasmi Bank Duplikat...")
                    all_processed_dfs, mikro_vars, makro_vars = [], list(dict_variabel_dfs_wide.keys()), []
                    
                    for var_name, list_dfs in dict_variabel_dfs_wide.items():
                        if not list_dfs: continue
                        df_var = pd.concat(list_dfs, ignore_index=True)
                        for col in requested_periods_list: df_var[col] = pd.to_numeric(df_var[col], errors='coerce')
                            
                        df_var = df_var.groupby(['country', 'bank'], as_index=False)[requested_periods_list].max()
                        
                        df_var['is_standard'] = df_var['country'].str.len() > 2
                        df_var['is_valid_bank_name'] = df_var['bank'].apply(lambda x: len(str(x).strip()) >= 2)
                        df_var['is_ticker_name'] = df_var['bank'].astype(str).str.contains(' EQUITY', case=False, na=False)
                        df_var['is_derivative'] = df_var['bank'].astype(str).str.contains(r'-RIGHT|-RTS|-SDR|ADR|FOREIGN|RIGHTS', regex=True, case=False)
                        df_var['bank_len'] = df_var['bank'].str.len()
                        
                        df_var = df_var.sort_values(by=['is_standard', 'is_valid_bank_name', 'is_ticker_name', 'is_derivative', 'bank_len', 'bank'], ascending=[False, False, True, True, True, True])
                        
                        if "NAMA BANK" in opsi_duplikat: df_var = df_var.drop_duplicates(subset=['country', 'bank'], keep='first')
                        elif "NILAI DATA" in opsi_duplikat:
                            has_data = df_var[requested_periods_list].notna().any(axis=1)
                            df_with_data = df_var[has_data].drop_duplicates(subset=requested_periods_list, keep='first')
                            df_no_data = df_var[~has_data].drop_duplicates(subset=['country', 'bank'], keep='first')
                            df_var = pd.concat([df_with_data, df_no_data], ignore_index=True)
                        
                        df_var = df_var.drop(columns=['is_standard', 'is_valid_bank_name', 'is_ticker_name', 'is_derivative', 'bank_len'], errors='ignore')
                        df_long = pd.melt(df_var, id_vars=['country', 'bank'], value_vars=requested_periods_list, var_name='period', value_name=var_name)
                        df_long = df_long.drop_duplicates(subset=['country', 'bank', 'period'], keep='first')
                        all_processed_dfs.append(df_long)
                    
                    st.caption("⚙️ Menyusun arsitektur master panel...")
                    if all_processed_dfs:
                        df_master = reduce(lambda left, right: pd.merge(left, right, on=['country', 'bank', 'period'], how='outer'), all_processed_dfs)
                        
                        if uploaded_wb_files:
                            st.caption("🌍 Menyuntikkan Data Makro World Bank ke Q4/Akhir Tahun...")
                            df_master['Merge_Year'] = df_master['period'].astype(str).str[:4].astype(int)
                            
                            def is_end_of_year(p):
                                p = str(p).upper().strip()
                                if len(p) == 4 or p.endswith('Q4') or p.endswith('12'): return True
                                return False
                            df_master['is_target_macro'] = df_master['period'].apply(is_end_of_year)
                            
                            wb_rename_map = {'KOREA, REP.': 'SOUTH KOREA', 'EGYPT, ARAB REP.': 'EGYPT', 'VENEZUELA, RB': 'VENEZUELA', 'YEMEN, REP.': 'YEMEN', 'IRAN, ISLAMIC REP.': 'IRAN', 'SYRIAN ARAB REPUBLIC': 'SYRIA', 'RUSSIAN FEDERATION': 'RUSSIA', 'SLOVAK REPUBLIC': 'SLOVAKIA', 'TURKIYE': 'TURKEY', 'BAHAMAS, THE': 'BAHAMAS', 'CONGO, DEM. REP.': 'DEMOCRATIC REPUBLIC OF THE CONGO'}
                            
                            for wb_file in uploaded_wb_files:
                                try: df_wb = pd.read_excel(wb_file, skiprows=3)
                                except Exception: df_wb = pd.read_excel(wb_file)
                                
                                if 'Indicator Name' in df_wb.columns: mac_name = re.sub(r'[^a-zA-Z0-9]', '_', str(df_wb['Indicator Name'].iloc[0])).lower().strip('_')[:32] 
                                else: mac_name = "macro_data"
                                    
                                wb_year_cols = [c for c in df_wb.columns if str(c).isdigit()]
                                df_wb_long = df_wb.melt(id_vars=['Country Name'], value_vars=wb_year_cols, var_name='Year', value_name=mac_name)
                                df_wb_long['country'] = df_wb_long['Country Name'].astype(str).str.upper().str.strip().replace(wb_rename_map)
                                df_wb_long['Year'] = df_wb_long['Year'].astype(int)
                                df_wb_clean = df_wb_long[['country', 'Year', mac_name]].dropna(subset=[mac_name])
                                
                                df_master = pd.merge(df_master, df_wb_clean, left_on=['country', 'Merge_Year'], right_on=['country', 'Year'], how='left')
                                df_master.loc[~df_master['is_target_macro'], mac_name] = np.nan
                                df_master = df_master.drop(columns=['Year'])
                                if mac_name not in makro_vars: makro_vars.append(mac_name)
                                    
                            df_master = df_master.drop(columns=['Merge_Year', 'is_target_macro'])
                        
                        if "Balanced" in opsi_panel:
                            bank_cacat = df_master[df_master[mikro_vars].isna().any(axis=1)][['country', 'bank']].drop_duplicates()
                            if not bank_cacat.empty:
                                df_master = df_master.set_index(['country', 'bank'])
                                bank_cacat_idx = bank_cacat.set_index(['country', 'bank']).index
                                df_master = df_master[~df_master.index.isin(bank_cacat_idx)].reset_index()
                        
                        if df_master.empty:
                            status.update(label="❌ Kesalahan Logika", state="error", expanded=True)
                            st.error("🚨 KOSONG TOTAL: Tidak ada bank yang memenuhi kriteria 'Balanced'. Silakan potong rentang observasi atau ubah format panel ke 'Unbalanced'.")
                        else:
                            df_master = df_master.sort_values(by=['country', 'bank', 'period']).reset_index(drop=True)
                            df_master['country_id'] = df_master.groupby('country').ngroup() + 1
                            df_master['bank_id'] = df_master.groupby('bank').ngroup() + 1
                            
                            kolom_awal = ['country_id', 'bank_id', 'country', 'bank', 'period']
                            df_master = df_master[kolom_awal + mikro_vars + makro_vars]
                            
                            st.session_state['master_panel'] = df_master
                            
                            status.update(label="✅ Selesai: Data Panel Siap!", state="complete", expanded=False)
                            st.balloons()
                            
                            st.write("### 📊 Statistik Panel Akhir")
                            m1, m2, m3, m4 = st.columns(4)
                            m1.metric("Variabel Total", len(mikro_vars) + len(makro_vars))
                            m2.metric("Negara", df_master['country'].nunique())
                            m3.metric("Entitas Bank", f"{df_master['bank'].nunique():,}")
                            m4.metric("Total Observasi", f"{len(df_master):,}")
                            
                            st.dataframe(df_master, use_container_width=True, hide_index=True, height=250)
                            
                            safe_start = re.sub(r'[^a-zA-Z0-9_]', '', start_period)
                            safe_end = re.sub(r'[^a-zA-Z0-9_]', '', end_period)
                            output = io.BytesIO()
                            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                                df_master.to_excel(writer, index=False, sheet_name='Master_Data')
                            
                            st.markdown("<br>", unsafe_allow_html=True)
                            c1, c2, c3 = st.columns([1,2,1])
                            with c2:
                                st.download_button(
                                    label="📥 UNDUH EXCEL (.xlsx)",
                                    data=output.getvalue(),
                                    file_name=f"Data_Panel_{safe_start}_{safe_end}.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True
                                )
                    else:
                        status.update(label="❌ Terjadi Kesalahan", state="error", expanded=True)
                        st.error("Gagal memproses data. File mungkin kosong.")


# ==============================================================================
# ======================== TAB 2: STATA DO-FILE GENERATOR ========================
# ==============================================================================
with tab_stata:
    st.write("### 💻 Generator Skrip Stata Ekonometrika")
    st.caption("Mesin ini mendeteksi otomatis jenis data Anda (Panel / Time Series / Cross-Section) dan merakit skrip Stata yang paling presisi.")
    
    if st.session_state['master_panel'] is None:
        st.info("👈 Silakan unggah dan kompilasi data Excel Anda di **Tab 1** terlebih dahulu agar mesin bisa membaca struktur data Anda.")
    else:
        df_stata = st.session_state['master_panel']
        freq_state = st.session_state.get('freq', 'Tahunan (Y)')
        
        # Detektor Tipe Data
        jml_bank = df_stata['bank'].nunique()
        jml_waktu = df_stata['period'].nunique()
        
        if jml_bank > 1 and jml_waktu > 1:
            tipe_data = "PANEL DATA"
            warna_badge = "blue"
        elif jml_bank == 1 and jml_waktu > 1:
            tipe_data = "TIME SERIES"
            warna_badge = "green"
        else:
            tipe_data = "CROSS-SECTION"
            warna_badge = "orange"
            
        st.markdown(f"**📌 Terdeteksi Struktur Data:** :{warna_badge}[**{tipe_data}**] (N={jml_bank}, T={jml_waktu})")
        
        daftar_vars = [col for col in df_stata.columns if col not in ['country_id', 'bank_id', 'country', 'bank', 'period']]
        
        col_y, col_x = st.columns([1, 2])
        with col_y:
            y_var = st.selectbox("Pilih Variabel Terikat (Y):", daftar_vars)
        with col_x:
            x_vars = st.multiselect("Pilih Variabel Bebas (X):", [v for v in daftar_vars if v != y_var])
            
        st.write("---")
        if st.button("🚀 GENERATE DO-FILE STATA", use_container_width=True):
            if not x_vars:
                st.error("Pilih minimal 1 Variabel Bebas (X) terlebih dahulu.")
            else:
                x_str = " ".join(x_vars)
                
                # 1. LOGIKA WAKTU (Membaca tipe frekuensi dari Tab 1)
                stata_time_logic = ""
                if freq_state == "Kuartalan (Q)":
                    stata_time_logic = """* Membersihkan teks waktu
gen time_val = quarterly(period, "YQ")
format time_val %tq
drop period
rename time_val period"""
                elif freq_state == "Bulanan (M)":
                    stata_time_logic = """* Membersihkan teks waktu (Misal format 2018-12)
* Ubah tanda strip agar rapi dibaca Stata
replace period = subinstr(period, "-", "", .)
gen time_val = monthly(period, "YM")
format time_val %tm
drop period
rename time_val period"""
                else:
                    stata_time_logic = """* Format waktu Tahunan
gen time_val = real(period)
format time_val %ty
drop period
rename time_val period"""

                # 2. LOGIKA SETTING STRUKTUR
                if tipe_data == "PANEL DATA":
                    stata_set_logic = "xtset bank_id period"
                    
                    stata_core_logic = f"""
* ==============================================================================
* 3. UJI STASIONERITAS (UNIT ROOT TESTS)
* ==============================================================================
* Uji stasioneritas penting untuk makroekonomi/keuangan panel (hindari spurious regression)
foreach var of varlist {y_var} {x_str} {{
    quietly xtunitroot llc `var'
    di "Levin-Lin-Chu Unit Root Test for `var': p-value = " r(p)
    quietly xtunitroot ips `var'
    di "Im-Pesaran-Shin Unit Root Test for `var': p-value = " r(p)
}}

* ==============================================================================
* 4. EKSPLORASI LAG & UJI ASUMSI KLASIK PANEL
* ==============================================================================
* Menambahkan Efek Masa Lalu (Lag 1 dan Lag 2) pada model OLS Dasar
regress {y_var} L.{y_var} L2.{y_var} {x_str} L.({x_str})

* A. Uji Multikolinearitas (VIF)
regress {y_var} {x_str}
vif

* B. Uji Heteroskedastisitas (Modified Wald test)
quietly xtreg {y_var} {x_str}, fe
xttest3

* C. Uji Autokorelasi (Wooldridge test) - (ssc install xtserial)
xtserial {y_var} {x_str}

* D. Uji Cross-Sectional Dependence (Pesaran CD) - (ssc install xtcd)
quietly xtreg {y_var} {x_str}, fe
xtcd

* ==============================================================================
* 5. PEMILIHAN MODEL PANEL UTAMA
* ==============================================================================
* A. Pooled OLS vs Fixed Effect (Chow Test)
quietly xtreg {y_var} {x_str}, fe
estimates store fe_model

* B. Random Effect
quietly xtreg {y_var} {x_str}, re
estimates store re_model

* C. Hausman Test (FE vs RE)
hausman fe_model re_model

* D. Breusch-Pagan LM Test (OLS vs RE)
quietly xtreg {y_var} {x_str}, re
xttest0

* ==============================================================================
* 6. ESTIMASI MODEL TERBAIK & ADVANCED ROBUSTNESS CHECK
* ==============================================================================
* Model 1: Pooled OLS (Robust Standard Errors)
regress {y_var} {x_str}, vce(cluster bank_id)
estimates store OLS_Rob

* Model 2: Fixed Effect (Robust)
xtreg {y_var} {x_str}, fe vce(robust)
estimates store FE_Rob

* Model 3: Random Effect (Robust)
xtreg {y_var} {x_str}, re vce(robust)
estimates store RE_Rob

* Model 4: Feasible Generalized Least Squares (FGLS) 
* (Mengobati Heteroskedastisitas & Autokorelasi AR1)
xtgls {y_var} {x_str}, panels(hetero) corr(ar1)
estimates store FGLS_Mod

* Model 5: Panel Corrected Standard Errors (PCSE)
xtpcse {y_var} {x_str}, correlation(ar1)
estimates store PCSE_Mod

* ==============================================================================
* 7. DYNAMIC PANEL ESTIMATION (GMM)
* ==============================================================================
* Mengatasi masalah Endogenitas dan Lag menggunakan Arellano-Bond (ssc install xtabond2)

* Difference GMM (Satu Lag Y)
xtabond2 {y_var} l.{y_var} {x_str}, gmm(l.{y_var}, lag(2 .)) iv({x_str}) noleveleq robust small
estimates store GMM_Diff

* System GMM (Blundell-Bond)
xtabond2 {y_var} l.{y_var} {x_str}, gmm(l.{y_var}, lag(2 .)) iv({x_str}) robust small
estimates store GMM_Sys

* ==============================================================================
* 8. EXPORT TABEL HASIL REGRESI (ssc install estout)
* ==============================================================================
esttab OLS_Rob FE_Rob RE_Rob FGLS_Mod PCSE_Mod using "Hasil_Regresi_Panel.rtf", replace ///
    b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) ///
    title("Tabel 1: Hasil Uji Regresi Panel & Robustness") ///
    mtitle("Pooled OLS" "FE" "RE" "FGLS" "PCSE") ///
    stats(r2 r2_w r2_o N, labels("R-Squared" "R2 Within" "R2 Overall" "Observations"))

esttab GMM_Diff GMM_Sys using "Hasil_Regresi_GMM.rtf", replace ///
    b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) ///
    title("Tabel 2: Hasil Uji Dynamic Panel (GMM)") ///
    mtitle("Diff GMM" "Sys GMM") ///
    stats(N, labels("Observations"))
"""

                elif tipe_data == "TIME SERIES":
                    stata_set_logic = "tsset period"
                    stata_core_logic = f"""
* ==============================================================================
* 3. UJI STASIONERITAS (ADF & Phillips-Perron)
* ==============================================================================
foreach var of varlist {y_var} {x_str} {{
    dfuller `var', lag(2)
    pperron `var'
}}

* ==============================================================================
* 4. EKSPLORASI LAG OPTIMAL & KOINTEGRASI
* ==============================================================================
* Mencari panjang lag optimal (AIC, SBIC)
varsoc {y_var} {x_str}

* Uji Kointegrasi Johansen (Ubah lag sesuai hasil varsoc)
vecrank {y_var} {x_str}, lags(2)

* ==============================================================================
* 5. ESTIMASI MODEL (OLS, VAR, VECM, ARIMA)
* ==============================================================================
* Model 1: OLS dengan Lag
regress {y_var} L.{y_var} {x_str} L.({x_str}), vce(robust)
estimates store OLS_Lag

* Model 2: ARIMA (Auto-Regressive Integrated Moving Average)
* Contoh ARIMA(1,0,1) dengan variabel eksogen (ARIMAX)
arima {y_var} {x_str}, ar(1) ma(1)
estimates store ARIMAX

* Model 3: Vector Autoregression (VAR)
var {y_var} {x_str}, lags(1/2)
estimates store VAR_Mod

* ==============================================================================
* 6. UJI ASUMSI TIME SERIES
* ==============================================================================
* A. Normalitas Residual
predict res, resid
sktest res

* B. Uji Autokorelasi Breusch-Godfrey LM test
estat bgodfrey, lags(1 2)

* C. Uji Efek ARCH (Heteroskedastisitas Time Series)
estat archlm, lags(1)

* (Opsional) Jika terdapat efek ARCH, jalankan GARCH(1,1)
arch {y_var} {x_str}, arch(1) garch(1)
estimates store GARCH_Mod

* ==============================================================================
* 7. EXPORT TABEL HASIL (ssc install estout)
* ==============================================================================
esttab OLS_Lag ARIMAX VAR_Mod GARCH_Mod using "Hasil_Time_Series.rtf", replace ///
    b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) ///
    title("Tabel Hasil Estimasi Time Series") ///
    mtitle("OLS Lags" "ARIMAX" "VAR" "GARCH")
"""
                
                else: # CROSS-SECTION
                    stata_set_logic = "* Data Cross-Section tidak memerlukan setting panel (tsset/xtset)"
                    stata_core_logic = f"""
* ==============================================================================
* 3. UJI ASUMSI KLASIK CROSS-SECTION
* ==============================================================================
* A. Uji Multikolinearitas
regress {y_var} {x_str}
vif

* B. Uji Heteroskedastisitas (Breusch-Pagan / Cook-Weisberg)
hettest

* C. Uji Normalitas Residual
predict res, resid
sktest res

* ==============================================================================
* 4. ESTIMASI MODEL & ROBUSTNESS
* ==============================================================================
* Model 1: Standard OLS
regress {y_var} {x_str}
estimates store OLS_Std

* Model 2: OLS dengan Robust Standard Errors (Mengobati Heteroskedastisitas)
regress {y_var} {x_str}, vce(robust)
estimates store OLS_Rob

* ==============================================================================
* 5. EXPORT TABEL HASIL (ssc install estout)
* ==============================================================================
esttab OLS_Std OLS_Rob using "Hasil_CrossSection.rtf", replace ///
    b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) ///
    title("Tabel Hasil Regresi Cross-Section") ///
    mtitle("Standard OLS" "Robust OLS") ///
    stats(r2 N, labels("R-Squared" "Observations"))
"""

                # MENJAHIT KODE FINAL
                do_code = f"""* ==============================================================================
* STATA DO-FILE: {tipe_data} ANALYSIS & ROBUSTNESS CHECKS
* GENERATED BY: ASSISTANCE BLOOMBERG ENGINE
* ==============================================================================

* 1. PERSIAPAN DATA
clear all
capture log close

* [CATATAN]: Pastikan Anda sudah mengimpor file Excel hasil dari Tab 1.
* import excel "Data_Panel.xlsx", sheet("Master_Data") firstrow clear

{stata_time_logic}

* 2. DEKLARASI STRUKTUR DATA
{stata_set_logic}

* Menampilkan ringkasan statistik & Korelasi
sum {y_var} {x_str}
pwcorr {y_var} {x_str}, star(0.05) sig
{stata_core_logic}
* ==============================================================================
* END OF DO-FILE
* ==============================================================================
"""
                st.success(f"✅ Kode Stata untuk **{tipe_data}** berhasil di-generate!")
                st.code(do_code, language="stata")
                st.info("💡 **Tips:** Salin kode di atas (gunakan tombol *Copy* di pojok kanan boks), buka **Do-file Editor (Ctrl+9)** di Stata Anda, lalu tempelkan. Jalankan perlahan demi perlahan (Ctrl+D) per blok (Bab) untuk menganalisis hasilnya.")
