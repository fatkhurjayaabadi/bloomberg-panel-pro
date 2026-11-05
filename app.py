import streamlit as st
import pandas as pd
import io
import re
from functools import reduce
import numpy as np

# ==========================================
# 1. PENGATURAN HALAMAN & CSS LUXURY MINIMALIST
# ==========================================
st.set_page_config(page_title="Bloomberg Panel Pro", page_icon="🏛️", layout="wide")

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

st.markdown("<div class='premium-title'>Bloomberg Panel Engine</div>", unsafe_allow_html=True)
st.markdown("<div class='premium-subtitle'>Sistem Ekstraksi, Filtrasi, dan Penyusunan Data Ekonometrika</div>", unsafe_allow_html=True)

# ==========================================
# 2. KAMUS NEGARA GLOBAL BLOOMBERG
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
    
    with st.expander("🗓️ Waktu Observasi", expanded=True):
        st.caption("Wajib diisi untuk menentukan rentang kolom tahun.")
        col1, col2 = st.columns(2)
        start_year = col1.number_input("Dari", value=None, placeholder="Cth: 2015", step=1, min_value=1900, max_value=2100)
        end_year = col2.number_input("Sampai", value=None, placeholder="Cth: 2023", step=1, min_value=1900, max_value=2100)

    with st.expander("🎯 Target Negara", expanded=True):
        opsi_negara = st.radio(
            "Tindakan Target:",
            [
                "1. Otomatis",
                "2. Paksa 1 Negara",
                "3. Filter Multi-Negara"
            ]
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
        st.caption("Tambahkan baris jika ada kode bursa yang ingin dikoreksi paksa (Opsional).")
        default_corrections = pd.DataFrame(columns=["Kode Asing (Ketik)", "Ubah Menjadi Negara"])
        edited_corrections = st.data_editor(default_corrections, num_rows="dynamic", use_container_width=True)
        
        custom_country_map = {}
        for _, row in edited_corrections.iterrows():
            if pd.notna(row.get("Kode Asing (Ketik)")) and pd.notna(row.get("Ubah Menjadi Negara")):
                k = str(row["Kode Asing (Ketik)"]).strip().upper()
                v = str(row["Ubah Menjadi Negara"]).strip().upper()
                if k and v:
                    custom_country_map[k] = v

    with st.expander("📚 Buku Saku Kode Bloomberg", expanded=False):
        st.caption("Pencarian kode sandi bawaan.")
        df_kamus = pd.DataFrame(list(country_map.items()), columns=["KODE", "NAMA NEGARA"])
        st.dataframe(df_kamus, hide_index=True, use_container_width=True, height=250)

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
            "Format Panel:",
            [
                "Unbalanced (Aman: Pertahankan sel kosong)", 
                "Balanced (Ketat: Tendang bank yang tidak utuh)"
            ],
            index=0
        )

# ==========================================
# 4. AREA KERJA UTAMA
# ==========================================
uploaded_files = st.file_uploader(
    "📥 Unggah File Mentah Bloomberg (.xlsx)", 
    type=["xlsx"], 
    accept_multiple_files=True
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
        st.warning("⚠️ Mohon unggah file Excel terlebih dahulu.")
    elif start_year is None or end_year is None:
        st.error("🚨 WAKTU OBSERVASI KOSONG: Anda wajib mengisi 'Dari Tahun' dan 'Sampai Tahun' di menu samping kiri sebelum memulai.")
    else:
        start_year = int(start_year)
        end_year = int(end_year)
        
        if start_year > end_year:
            st.error("🚨 KESALAHAN LOGIKA: 'Dari Tahun' tidak boleh lebih besar dari 'Sampai Tahun'.")
        else:
            dict_variabel_dfs_wide = {}
            
            with st.status("🛠️ Mengekstraksi dan Membersihkan Data...", expanded=True) as status:
                progress_bar = st.progress(0)
                requested_years_list = list(range(start_year, end_year + 1))
                
                # TAHAP 0: MEMBANGUN KAMUS NAMA BANK GLOBAL LINTAS-FILE
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
                
                # TAHAP 1: Ekstraksi Data Utama
                for i, (fname, df) in enumerate(raw_data_cache):
                    year_cols = [col for col in df.columns if ":" in str(col)]
                    if not year_cols:
                        continue
                        
                    raw_var_name = str(year_cols[0]).split(":")[0].strip()
                    clean_var_name = re.sub(r'[^a-zA-Z0-9_]', '_', raw_var_name).lower()
                    clean_var_name = re.sub(r'_+', '_', clean_var_name).strip('_')
                    
                    df = df.drop([0, 1]).reset_index(drop=True)
                    df['country_code'] = df['Ticker'].apply(get_country_code)
                    
                    df['country'] = df['country_code'].map(custom_country_map).fillna(df['country_code'].map(country_map)).fillna(df['country_code'])
                    df = df.rename(columns={'Name': 'bank'})
                    
                    df['Ticker_Clean'] = df['Ticker'].astype(str).str.strip()
                    df['bank'] = df['bank'].astype(str).str.strip().str.upper()
                    
                    mask_kosong = df['bank'].isin(['NAN', 'NONE', 'NULL', 'NA', ''])
                    df.loc[mask_kosong, 'bank'] = df.loc[mask_kosong, 'Ticker_Clean'].map(global_ticker_map)
                    
                    df['bank'] = df['bank'].fillna(df['Ticker_Clean'])
                    df['bank'] = df['bank'].astype(str).str.strip().str.upper()
                    mask_kosong_akhir = df['bank'].isin(['NAN', 'NONE', 'NULL', 'NA', ''])
                    df.loc[mask_kosong_akhir, 'bank'] = df.loc[mask_kosong_akhir, 'Ticker_Clean']
                    
                    df['country'] = df['country'].astype(str).str.strip().str.upper()
                    
                    if "Paksa" in opsi_negara and negara_paksaan:
                        df['country'] = negara_paksaan
                    elif "Filter" in opsi_negara and negara_pilihan:
                        df = df[df['country'].isin(negara_pilihan)]
                        if df.empty:
                            continue
                    
                    valid_year_cols = [col for col in year_cols if start_year <= int(str(col).split(":")[1][:4]) <= end_year]
                    rename_dict = {col: int(str(col).split(":")[1][:4]) for col in valid_year_cols}
                    
                    for col in valid_year_cols:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                        
                    df = df.rename(columns=rename_dict)
                    
                    for yr in requested_years_list:
                        if yr not in df.columns:
                            df[yr] = np.nan
                    
                    df_wide = df[['country', 'bank'] + requested_years_list]
                    
                    if clean_var_name not in dict_variabel_dfs_wide:
                        dict_variabel_dfs_wide[clean_var_name] = []
                    dict_variabel_dfs_wide[clean_var_name].append(df_wide)
                    
                    progress_bar.progress((i + 1) / len(uploaded_files))
                
                st.caption("🔄 Mengeliminasi duplikat dan standarisasi panel...")
                
                # TAHAP 2: Pembersihan & Perubahan Format
                all_processed_dfs = []
                variabel_list = list(dict_variabel_dfs_wide.keys())
                
                for var_name, list_dfs in dict_variabel_dfs_wide.items():
                    if not list_dfs:
                        continue
                    df_var = pd.concat(list_dfs, ignore_index=True)
                    
                    df_var['is_standard'] = df_var['country'].str.len() > 2
                    df_var['is_valid_bank_name'] = df_var['bank'].apply(
                        lambda x: len(str(x).strip()) >= 2 and str(x).strip().upper() not in ['NAN', 'NONE', 'NULL', 'NA']
                    )
                    
                    # 🚀 FITUR BARU: MENDETEKSI KASTA NAMA (TICKER VS NAMA ASLI)
                    # Jika nama mengandung kata " EQUITY", ia akan ditandai True. Mesin akan mengutamakan yang nilainya False.
                    df_var['is_ticker_name'] = df_var['bank'].astype(str).str.contains(' EQUITY', case=False, na=False)
                    
                    df_var['bank_len'] = df_var['bank'].str.len()
                    
                    # Pengurutan:
                    # 1. is_standard == True (Di Atas)
                    # 2. is_valid_bank_name == True (Di Atas)
                    # 3. is_ticker_name == False (Nama Asli Harus Di Atas Ticker)
                    # 4. bank_len == Kecil (Nama Terpendek Di Atas)
                    df_var = df_var.sort_values(
                        by=['is_standard', 'is_valid_bank_name', 'is_ticker_name', 'bank_len', 'bank'], 
                        ascending=[False, False, True, True, True]
                    )
                    
                    if "NAMA BANK" in opsi_duplikat:
                        df_var = df_var.drop_duplicates(subset=['country', 'bank'], keep='first')
                    elif "NILAI DATA" in opsi_duplikat:
                        has_data = df_var[requested_years_list].notna().any(axis=1)
                        df_with_data = df_var[has_data]
                        df_no_data = df_var[~has_data]
                        
                        df_with_data = df_with_data.drop_duplicates(subset=requested_years_list, keep='first')
                        df_var = pd.concat([df_with_data, df_no_data], ignore_index=True)
                    
                    df_var = df_var.drop(columns=['is_standard', 'is_valid_bank_name', 'is_ticker_name', 'bank_len'])
                    
                    df_long = pd.melt(df_var, id_vars=['country', 'bank'], value_vars=requested_years_list, var_name='year', value_name=var_name)
                    df_long = df_long.drop_duplicates(subset=['country', 'bank', 'year'], keep='first')
                    all_processed_dfs.append(df_long)
                
                st.caption("⚙️ Menyusun arsitektur Stata akhir...")
                
                # TAHAP 3: Penggabungan Keseluruhan
                if all_processed_dfs:
                    df_master = reduce(lambda left, right: pd.merge(left, right, on=['country', 'bank', 'year'], how='outer'), all_processed_dfs)
                    
                    if "Balanced" in opsi_panel:
                        bank_cacat = df_master[df_master[variabel_list].isna().any(axis=1)][['country', 'bank']].drop_duplicates()
                        if not bank_cacat.empty:
                            df_master = df_master.set_index(['country', 'bank'])
                            bank_cacat_idx = bank_cacat.set_index(['country', 'bank']).index
                            df_master = df_master[~df_master.index.isin(bank_cacat_idx)].reset_index()
                    
                    if df_master.empty:
                        status.update(label="❌ Kesalahan Logika", state="error", expanded=True)
                        st.error("🚨 KOSONG TOTAL: Tidak ada entitas bank yang memenuhi kriteria. Jika Anda memakai mode 'Balanced', ini berarti tidak ada satu bank pun yang memiliki data absolut 100% penuh dari tahun awal sampai akhir yang Anda tentukan.")
                    else:
                        df_master = df_master.sort_values(by=['country', 'bank', 'year']).reset_index(drop=True)
                        df_master['country_id'] = df_master.groupby('country').ngroup() + 1
                        df_master['bank_id'] = df_master.groupby('bank').ngroup() + 1
                        
                        kolom_awal = ['country_id', 'bank_id', 'country', 'bank', 'year']
                        df_master = df_master[kolom_awal + variabel_list]
                        
                        status.update(label="✅ Selesai: Master Panel Siap Diunduh!", state="complete", expanded=False)
                        st.balloons()
                        
                        # DASHBOARD HASIL & TOMBOL UNDUH
                        st.write("### 📊 Statistik Parameter Akhir")
                        m1, m2, m3, m4 = st.columns(4)
                        m1.metric("Variabel Terekstrak", len(variabel_list))
                        m2.metric("Negara Terdaftar", df_master['country'].nunique())
                        m3.metric("Entitas Bank", f"{df_master['bank'].nunique():,}")
                        m4.metric("Baris Observasi (N)", f"{len(df_master):,}")
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.dataframe(df_master, use_container_width=True, hide_index=True, height=400)
                        
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            df_master.to_excel(writer, index=False, sheet_name='Master_Data')
                            
                        st.markdown("<br>", unsafe_allow_html=True)
                        c1, c2, c3 = st.columns([1,2,1])
                        with c2:
                            st.download_button(
                                label="📥 UNDUH FORMAT STATA (.xlsx)",
                                data=output.getvalue(),
                                file_name=f"Data_Panel_Final_{start_year}_{end_year}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )
                else:
                    status.update(label="❌ Terjadi Kesalahan", state="error", expanded=True)
                    st.error("Gagal memproses data. File mungkin kosong atau terhapus semua oleh aturan filter.")
