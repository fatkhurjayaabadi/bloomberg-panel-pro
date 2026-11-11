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
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='premium-title'>Assistance Bloomberg</div>", unsafe_allow_html=True)
st.markdown("<div class='premium-subtitle'>Sistem Ekstraksi Mikro-Panel & Integrasi Makroekonomi</div>", unsafe_allow_html=True)

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
# 3. SIDEBAR PENGATURAN LANJUTAN
# ==========================================
with st.sidebar:
    st.write("### ⚙️ Konfigurasi")
    st.write("---")
    
    with st.expander("🗓️ Rentang Waktu Observasi", expanded=True):
        st.caption("Bisa diisi Tahun bulat (2015), Kuartal (2016Q4), atau Bulan (2016-12).")
        col1, col2 = st.columns(2)
        # 🚀 PERUBAHAN: Input kini berbentuk TEKS bebas, bukan Angka
        start_period = col1.text_input("Dari", value="", placeholder="Cth: 2016Q4")
        end_period = col2.text_input("Sampai", value="", placeholder="Cth: 2025Q3")

    with st.expander("🎯 Target Negara", expanded=True):
        opsi_negara = st.radio(
            "Tindakan Target:",
            ["1. Otomatis", "2. Paksa 1 Negara", "3. Filter Multi-Negara"]
        )
        
        daftar_negara_unik = sorted(list(set(country_map.values())))
        if "Paksa" in opsi_negara:
            negara_paksaan = st.selectbox("Tujuan Pemaksaan:", daftar_negara_unik, index=None, placeholder="Pilih negara...")
            negara_pilihan = []
        elif "Filter" in opsi_negara:
            negara_pilihan = st.multiselect("Pertahankan hanya:", daftar_negara_unik, default=None, placeholder="Pilih negara...")
            negara_paksaan = None
        else:
            negara_paksaan = None
            negara_pilihan = []

    with st.expander("🌍 Koreksi Sandi Otomatis", expanded=True):
        st.caption("Koreksi paksa kode bursa asing jika diperlukan.")
        default_corrections = pd.DataFrame(columns=["Kode Asing (Ketik)", "Ubah Menjadi Negara"])
        edited_corrections = st.data_editor(default_corrections, num_rows="dynamic", use_container_width=True)
        
        custom_country_map = {}
        for _, row in edited_corrections.iterrows():
            if pd.notna(row.get("Kode Asing (Ketik)")) and pd.notna(row.get("Ubah Menjadi Negara")):
                k = str(row["Kode Asing (Ketik)"]).strip().upper()
                v = str(row["Ubah Menjadi Negara"]).strip().upper()
                if k and v: custom_country_map[k] = v

    with st.expander("🛡️ Proteksi Duplikat", expanded=True):
        opsi_duplikat = st.radio(
            "Pilih Mode Deteksi:",
            [
                "Biarkan semua data (Jangan hapus)", 
                "Hapus jika NAMA BANK persis sama",
                "Hapus jika NILAI DATA sama (Silang Negara)"
            ],
            index=2
        )

    with st.expander("⚖️ Desain Tabel Stata", expanded=True):
        opsi_panel = st.radio(
            "Format Panel Akhir:",
            [
                "Unbalanced (Aman: Pertahankan sel kosong)", 
                "Balanced (Ketat: Tendang bank yang tidak utuh)"
            ],
            index=0
        )

# ==========================================
# 4. AREA KERJA UTAMA (2 LUBANG UNGGAHAN)
# ==========================================
col_up1, col_up2 = st.columns(2)
with col_up1:
    uploaded_files = st.file_uploader(
        "🏢 1. Unggah Mikro Bloomberg (.xlsx)", 
        type=["xlsx"], 
        accept_multiple_files=True
    )
with col_up2:
    uploaded_wb_files = st.file_uploader(
        "🌍 2. Unggah Makro World Bank (.xlsx)", 
        type=["xlsx", "xls"], 
        accept_multiple_files=True,
        help="Otomatis diselaraskan ke negara dan tahun terkait. Hanya diletakkan di Q4 atau Bulan 12."
    )

st.markdown("<br>", unsafe_allow_html=True)
col_spacer1, col_btn, col_spacer2 = st.columns([1, 2, 1])
with col_btn:
    mulai_proses = st.button("MULAI PROSES KOMPILASI", use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ==========================================
# 5. MESIN ALGORITMA UTAMA
# ==========================================
if mulai_proses:
    if not uploaded_files:
        st.warning("⚠️ Mohon unggah file Excel Bloomberg terlebih dahulu.")
    elif not start_period or not end_period:
        st.error("🚨 WAKTU OBSERVASI KOSONG: Anda wajib mengisi 'Dari' dan 'Sampai'.")
    else:
        # Bersihkan spasi dan jadikan huruf besar (cth: " 2016q4 " -> "2016Q4")
        start_period = start_period.strip().upper()
        end_period = end_period.strip().upper()
        
        if start_period > end_period:
            st.error("🚨 KESALAHAN LOGIKA: Periode 'Dari' tidak boleh lebih besar dari periode 'Sampai'.")
        else:
            # 🚀 ALGORITMA CERDAS: Jika user hanya mengetik "2023", tambahkan karakter "Z" 
            # agar ia mengangkut seluruh kuartal 2023 (Q1-Q4) tanpa memotongnya.
            end_period_check = end_period + "Z" if len(end_period) == 4 and end_period.isdigit() else end_period

            dict_variabel_dfs_wide = {}
            
            with st.status("🛠️ Mengekstraksi dan Membersihkan Data...", expanded=True) as status:
                progress_bar = st.progress(0)
                
                # TAHAP 0: KAMUS NAMA BANK LINTAS FILE
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
                                if t not in global_ticker_map:
                                    global_ticker_map[t] = n
                                else:
                                    if len(n) < len(global_ticker_map[t]):
                                        global_ticker_map[t] = n
                                        
                # 🚀 TAHAP 0.5: DETEKSI WAKTU ALFANUMERIK (Mendukung Q1-Q4 dan Bulan)
                st.caption("📅 Menganalisis frekuensi waktu Bloomberg...")
                valid_periods_set = set()
                for fname, df in raw_data_cache:
                    for col in df.columns:
                        if ":" in str(col):
                            raw_period = str(col).split(":", 1)[1].strip().upper()
                            # Bandingkan string: Hanya ambil periode di antara batas yang diminta
                            if start_period <= raw_period <= end_period_check:
                                valid_periods_set.add(raw_period)
                
                requested_periods_list = sorted(list(valid_periods_set))
                
                if not requested_periods_list:
                    status.update(label="❌ Kesalahan Data", state="error", expanded=True)
                    st.error(f"🚨 TIDAK ADA DATA WAKTU: Tidak ditemukan rentang periode {start_period} s.d {end_period} di dalam file Excel Anda.")
                    st.stop()
                
                # TAHAP 1: EKSTRAKSI BLOOMBERG
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
                    df['bank'] = df['bank'].fillna(df['Ticker_Clean']).astype(str).str.strip().str.upper()
                    
                    mask_kosong_akhir = df['bank'].isin(['NAN', 'NONE', 'NULL', 'NA', ''])
                    df.loc[mask_kosong_akhir, 'bank'] = df.loc[mask_kosong_akhir, 'Ticker_Clean']
                    df['country'] = df['country'].astype(str).str.strip().str.upper()
                    
                    if "Paksa" in opsi_negara and negara_paksaan:
                        df['country'] = negara_paksaan
                    elif "Filter" in opsi_negara and negara_pilihan:
                        df = df[df['country'].isin(negara_pilihan)]
                        if df.empty: continue
                    
                    rename_dict = {}
                    for col in year_cols:
                        raw_period = str(col).split(":", 1)[1].strip().upper()
                        if raw_period in requested_periods_list:
                            rename_dict[col] = raw_period
                    
                    for col in rename_dict.keys():
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                        
                    df = df.rename(columns=rename_dict)
                    for per in requested_periods_list:
                        if per not in df.columns: df[per] = np.nan
                    
                    df_wide = df[['country', 'bank'] + requested_periods_list]
                    if clean_var_name not in dict_variabel_dfs_wide:
                        dict_variabel_dfs_wide[clean_var_name] = []
                    dict_variabel_dfs_wide[clean_var_name].append(df_wide)
                    progress_bar.progress((i + 1) / len(uploaded_files))
                
                st.caption("🔄 Mengeliminasi duplikat Bloomberg...")
                
                # TAHAP 2: PEMBERSIHAN DUPLIKAT
                all_processed_dfs = []
                mikro_vars = list(dict_variabel_dfs_wide.keys())
                makro_vars = []
                
                for var_name, list_dfs in dict_variabel_dfs_wide.items():
                    if not list_dfs: continue
                    df_var = pd.concat(list_dfs, ignore_index=True)
                    
                    df_var['is_standard'] = df_var['country'].str.len() > 2
                    df_var['is_valid_bank_name'] = df_var['bank'].apply(lambda x: len(str(x).strip()) >= 2 and str(x).strip().upper() not in ['NAN', 'NONE', 'NULL', 'NA'])
                    df_var['is_ticker_name'] = df_var['bank'].astype(str).str.contains(' EQUITY', case=False, na=False)
                    df_var['bank_len'] = df_var['bank'].str.len()
                    
                    df_var = df_var.sort_values(
                        by=['is_standard', 'is_valid_bank_name', 'is_ticker_name', 'bank_len', 'bank'], 
                        ascending=[False, False, True, True, True]
                    )
                    
                    if "NAMA BANK" in opsi_duplikat:
                        df_var = df_var.drop_duplicates(subset=['country', 'bank'], keep='first')
                    elif "NILAI DATA" in opsi_duplikat:
                        has_data = df_var[requested_periods_list].notna().any(axis=1)
                        df_with_data = df_var[has_data].drop_duplicates(subset=requested_periods_list, keep='first')
                        df_no_data = df_var[~has_data]
                        df_var = pd.concat([df_with_data, df_no_data], ignore_index=True)
                    
                    df_var = df_var.drop(columns=['is_standard', 'is_valid_bank_name', 'is_ticker_name', 'bank_len'])
                    df_long = pd.melt(df_var, id_vars=['country', 'bank'], value_vars=requested_periods_list, var_name='period', value_name=var_name)
                    df_long = df_long.drop_duplicates(subset=['country', 'bank', 'period'], keep='first')
                    all_processed_dfs.append(df_long)
                
                st.caption("⚙️ Menyusun arsitektur master panel...")
                
                # TAHAP 3: MERGE BLOOMBERG
                if all_processed_dfs:
                    df_master = reduce(lambda left, right: pd.merge(left, right, on=['country', 'bank', 'period'], how='outer'), all_processed_dfs)
                    
                    # TAHAP 4: INTEGRASI WORLD BANK MAKRO
                    if uploaded_wb_files:
                        st.caption("🌍 Menyuntikkan Data Makro World Bank ke Q4/Akhir Tahun...")
                        
                        df_master['Merge_Year'] = df_master['period'].astype(str).str[:4].astype(int)
                        
                        def is_end_of_year(p):
                            p = str(p).upper().strip()
                            if len(p) == 4: return True
                            if p.endswith('Q4') or p.endswith('12'): return True
                            return False
                        df_master['is_target_macro'] = df_master['period'].apply(is_end_of_year)
                        
                        wb_rename_map = {
                            'KOREA, REP.': 'SOUTH KOREA', 'EGYPT, ARAB REP.': 'EGYPT', 
                            'VENEZUELA, RB': 'VENEZUELA', 'YEMEN, REP.': 'YEMEN', 
                            'IRAN, ISLAMIC REP.': 'IRAN', 'SYRIAN ARAB REPUBLIC': 'SYRIA', 
                            'RUSSIAN FEDERATION': 'RUSSIA', 'SLOVAK REPUBLIC': 'SLOVAKIA',
                            'TURKIYE': 'TURKEY', 'BAHAMAS, THE': 'BAHAMAS',
                            'CONGO, DEM. REP.': 'DEMOCRATIC REPUBLIC OF THE CONGO'
                        }
                        
                        for wb_file in uploaded_wb_files:
                            try:
                                df_wb = pd.read_excel(wb_file, skiprows=3)
                            except Exception:
                                df_wb = pd.read_excel(wb_file)
                            
                            if 'Indicator Name' in df_wb.columns:
                                raw_macro_name = df_wb['Indicator Name'].iloc[0]
                                macro_var_name = re.sub(r'[^a-zA-Z0-9]', '_', str(raw_macro_name)).lower()
                                macro_var_name = re.sub(r'_+', '_', macro_var_name).strip('_')[:32] 
                            else:
                                macro_var_name = "macro_data"
                                
                            wb_year_cols = [c for c in df_wb.columns if str(c).isdigit()]
                            df_wb_long = df_wb.melt(id_vars=['Country Name'], value_vars=wb_year_cols, var_name='Year', value_name=macro_var_name)
                            
                            df_wb_long['country'] = df_wb_long['Country Name'].astype(str).str.upper().str.strip()
                            df_wb_long['country'] = df_wb_long['country'].replace(wb_rename_map)
                            df_wb_long['Year'] = df_wb_long['Year'].astype(int)
                            
                            df_wb_clean = df_wb_long[['country', 'Year', macro_var_name]].dropna(subset=[macro_var_name])
                            
                            df_master = pd.merge(df_master, df_wb_clean, left_on=['country', 'Merge_Year'], right_on=['country', 'Year'], how='left')
                            
                            df_master.loc[~df_master['is_target_macro'], macro_var_name] = np.nan
                            
                            df_master = df_master.drop(columns=['Year'])
                            if macro_var_name not in makro_vars:
                                makro_vars.append(macro_var_name)
                                
                        df_master = df_master.drop(columns=['Merge_Year', 'is_target_macro'])
                    
                    if "Balanced" in opsi_panel:
                        bank_cacat = df_master[df_master[mikro_vars].isna().any(axis=1)][['country', 'bank']].drop_duplicates()
                        if not bank_cacat.empty:
                            df_master = df_master.set_index(['country', 'bank'])
                            bank_cacat_idx = bank_cacat.set_index(['country', 'bank']).index
                            df_master = df_master[~df_master.index.isin(bank_cacat_idx)].reset_index()
                    
                    if df_master.empty:
                        status.update(label="❌ Kesalahan Logika", state="error", expanded=True)
                        st.error("🚨 KOSONG TOTAL: Tidak ada bank yang memiliki data absolut penuh di periode yang diminta.")
                    else:
                        df_master = df_master.sort_values(by=['country', 'bank', 'period']).reset_index(drop=True)
                        df_master['country_id'] = df_master.groupby('country').ngroup() + 1
                        df_master['bank_id'] = df_master.groupby('bank').ngroup() + 1
                        
                        kolom_awal = ['country_id', 'bank_id', 'country', 'bank', 'period']
                        df_master = df_master[kolom_awal + mikro_vars + makro_vars]
                        
                        status.update(label="✅ Selesai: Panel Ekonometrika Siap!", state="complete", expanded=False)
                        st.balloons()
                        
                        st.write("### 📊 Statistik Parameter Akhir")
                        m1, m2, m3, m4 = st.columns(4)
                        m1.metric("Variabel (Mikro + Makro)", len(mikro_vars) + len(makro_vars))
                        m2.metric("Negara Terdaftar", df_master['country'].nunique())
                        m3.metric("Entitas Bank", f"{df_master['bank'].nunique():,}")
                        m4.metric("Baris Observasi (N)", f"{len(df_master):,}")
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.dataframe(df_master, use_container_width=True, hide_index=True, height=400)
                        
                        # Mencegah error karakter aneh pada nama file
                        safe_start = re.sub(r'[^a-zA-Z0-9_]', '', start_period)
                        safe_end = re.sub(r'[^a-zA-Z0-9_]', '', end_period)
                        
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            df_master.to_excel(writer, index=False, sheet_name='Master_Data')
                            
                        st.markdown("<br>", unsafe_allow_html=True)
                        c1, c2, c3 = st.columns([1,2,1])
                        with c2:
                            st.download_button(
                                label="📥 UNDUH FORMAT STATA (.xlsx)",
                                data=output.getvalue(),
                                file_name=f"Data_Panel_{safe_start}_{safe_end}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )
                else:
                    status.update(label="❌ Terjadi Kesalahan", state="error", expanded=True)
                    st.error("Gagal memproses data. File mungkin kosong atau terhapus semua oleh aturan filter.")
