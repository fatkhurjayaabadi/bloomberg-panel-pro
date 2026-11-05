import streamlit as st
import pandas as pd
import io
import re
from functools import reduce
import numpy as np

# ==========================================
# 1. PENGATURAN HALAMAN & CSS ULTRA PREMIUM
# ==========================================
st.set_page_config(page_title="Bloomberg Panel Pro", page_icon="💠", layout="wide")

st.markdown("""
    <style>
        .premium-title {
            background: linear-gradient(135deg, #1A2980 0%, #26D0CE 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 52px;
            font-weight: 900;
            text-align: center;
            letter-spacing: -1.5px;
            margin-bottom: 5px;
        }
        .premium-subtitle {
            text-align: center;
            color: #64748B;
            font-size: 18px;
            font-weight: 500;
            margin-bottom: 35px;
            letter-spacing: 0.5px;
        }
        .stButton>button {
            background: linear-gradient(135deg, #0F2027 0%, #203A43 50%, #2C5364 100%);
            color: white;
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.1);
            padding: 12px 24px;
            font-size: 18px;
            font-weight: bold;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 25px rgba(0, 0, 0, 0.3);
            border-color: #26D0CE;
        }
        div[data-testid="metric-container"] {
            background: linear-gradient(145deg, #ffffff, #f0f4f8);
            border-left: 5px solid #26D0CE;
            padding: 15px 20px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.04);
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='premium-title'>Bloomberg Panel Engine</div>", unsafe_allow_html=True)
st.markdown("<div class='premium-subtitle'>Ekstraksi Otomatis, Pemaksaan Target Negara, & Penghapus Duplikat Cerdas</div>", unsafe_allow_html=True)

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
    st.write("### ⚙️ Engine Parameters")
    st.write("---")
    
    with st.expander("🗓️ Tentukan Rentang Tahun", expanded=True):
        col1, col2 = st.columns(2)
        start_year = col1.number_input("Dari", value=2015, step=1)
        end_year = col2.number_input("Sampai", value=2026, step=1)

    with st.expander("🎯 Target & Filter Negara", expanded=True):
        opsi_negara = st.radio(
            "Tindakan untuk file ini:",
            [
                "1. Otomatis (Sesuai Bawaan Bloomberg)",
                "2. PAKSA 1 NEGARA (Sangat Disarankan)",
                "3. FILTER (Pilih Beberapa Negara)"
            ],
            help="Opsi 2 akan mengabaikan semua kode bursa asing dan memaksa seluruh data di file tersebut diakui sebagai 1 negara pilihan Anda."
        )
        
        daftar_negara_unik = sorted(list(set(country_map.values())))
        if "PAKSA" in opsi_negara:
            negara_paksaan = st.selectbox("Paksa semua data menjadi negara:", daftar_negara_unik, index=daftar_negara_unik.index("OMAN") if "OMAN" in daftar_negara_unik else 0)
            negara_pilihan = []
        elif "FILTER" in opsi_negara:
            negara_pilihan = st.multiselect("Pertahankan hanya data dari:", daftar_negara_unik, default=["OMAN", "LEBANON"])
            negara_paksaan = None
        else:
            negara_paksaan = None
            negara_pilihan = []

    with st.expander("🌍 Koreksi Sandi Otomatis", expanded=True):
        st.caption("Klik tabel di bawah untuk menambah atau mengedit kode secara interaktif.")
        
        default_corrections = pd.DataFrame({
            "Kode Asing (Ketik)": ["EO", "EU", "EP", "EZ", "B3", "L1", "L3", "LI", "S2"],
            "Ubah Menjadi Negara": ["OMAN", "OMAN", "OMAN", "OMAN", "OMAN", "OMAN", "OMAN", "OMAN", "OMAN"]
        })
        
        edited_corrections = st.data_editor(default_corrections, num_rows="dynamic", use_container_width=True)
        
        custom_country_map = {}
        for _, row in edited_corrections.iterrows():
            if pd.notna(row["Kode Asing (Ketik)"]) and pd.notna(row["Ubah Menjadi Negara"]):
                k = str(row["Kode Asing (Ketik)"]).strip().upper()
                v = str(row["Ubah Menjadi Negara"]).strip().upper()
                if k and v:
                    custom_country_map[k] = v

    with st.expander("📚 Buku Saku Kode Bloomberg", expanded=False):
        st.caption("Cari kode sandi standar dari berbagai negara.")
        df_kamus = pd.DataFrame(list(country_map.items()), columns=["KODE", "NAMA NEGARA"])
        st.dataframe(df_kamus, hide_index=True, use_container_width=True, height=250)

    with st.expander("🛡️ Kecerdasan Pembersih Duplikat", expanded=True):
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
            "Format Panel Data:",
            [
                "Unbalanced (Aman: Struktur Tahun Utuh, Ada Nilai Kosong)", 
                "Balanced (Ketat: Hapus KESELURUHAN BANK jika ada 1 tahun yang kosong)"
            ],
            index=0
        )

# ==========================================
# 4. AREA KERJA UTAMA
# ==========================================
uploaded_files = st.file_uploader(
    "📥 Drag & Drop semua file Excel Bloomberg mentah (grid1_xxx.xlsx) ke area ini", 
    type=["xlsx"], 
    accept_multiple_files=True
)

st.markdown("<br>", unsafe_allow_html=True)
col_spacer1, col_btn, col_spacer2 = st.columns([1, 2, 1])
with col_btn:
    mulai_proses = st.button("🚀 EKSEKUSI PENGGABUNGAN DATA", use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ==========================================
# 5. MESIN ALGORITMA UTAMA
# ==========================================
if mulai_proses:
    if not uploaded_files:
        st.warning("⚠️ Anda belum mengunggah file Excel apa pun.")
    else:
        dict_variabel_dfs_wide = {}
        
        with st.status("🛠️ Membedah file dan menyelaraskan rentang tahun...", expanded=True) as status:
            progress_bar = st.progress(0)
            
            requested_years_list = list(range(start_year, end_year + 1))
            
            # TAHAP 1: Ekstraksi Data
            for i, file in enumerate(uploaded_files):
                df = pd.read_excel(file, engine='openpyxl')
                year_cols = [col for col in df.columns if ":" in str(col)]
                if not year_cols:
                    continue
                    
                raw_var_name = str(year_cols[0]).split(":")[0].strip()
                clean_var_name = re.sub(r'[^a-zA-Z0-9_]', '_', raw_var_name).lower()
                clean_var_name = re.sub(r'_+', '_', clean_var_name).strip('_')
                
                df = df.drop([0, 1]).reset_index(drop=True)
                df['country_code'] = df['Ticker'].apply(get_country_code)
                
                # Penerapan Kamus
                df['country'] = df['country_code'].map(custom_country_map).fillna(df['country_code'].map(country_map)).fillna(df['country_code'])
                df = df.rename(columns={'Name': 'bank'})
                
                # Fallback ke Ticker jika nama bank kosong/NaN
                df['bank'] = df['bank'].fillna(df['Ticker'])
                df['bank'] = df['bank'].astype(str).str.strip().str.upper()
                
                # Pastikan string kosong atau yang terbaca 'NAN' diganti paksa pakai Ticker
                mask_kosong = df['bank'].isin(['NAN', 'NONE', 'NULL', 'NA', ''])
                df.loc[mask_kosong, 'bank'] = df.loc[mask_kosong, 'Ticker'].astype(str).str.strip().str.upper()
                
                df['country'] = df['country'].astype(str).str.strip().str.upper()
                
                # Penerapan Opsi Paksa/Filter Negara
                if "PAKSA" in opsi_negara:
                    df['country'] = negara_paksaan
                elif "FILTER" in opsi_negara:
                    if negara_pilihan:
                        df = df[df['country'].isin(negara_pilihan)]
                        if df.empty:
                            continue
                
                valid_year_cols = [col for col in year_cols if start_year <= int(str(col).split(":")[1][:4]) <= end_year]
                rename_dict = {col: int(str(col).split(":")[1][:4]) for col in valid_year_cols}
                
                for col in valid_year_cols:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                df = df.rename(columns=rename_dict)
                
                # Mengisi tahun yang hilang dengan NaN agar struktur panel seimbang di awal
                for yr in requested_years_list:
                    if yr not in df.columns:
                        df[yr] = np.nan
                
                df_wide = df[['country', 'bank'] + requested_years_list]
                
                if clean_var_name not in dict_variabel_dfs_wide:
                    dict_variabel_dfs_wide[clean_var_name] = []
                dict_variabel_dfs_wide[clean_var_name].append(df_wide)
                
                progress_bar.progress((i + 1) / len(uploaded_files))
            
            st.caption("🔄 Menyeleksi nama bank dan menghapus duplikat...")
            
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
                df_var['bank_len'] = df_var['bank'].str.len()
                
                df_var = df_var.sort_values(
                    by=['is_standard', 'is_valid_bank_name', 'bank_len', 'bank'], 
                    ascending=[False, False, True, True]
                )
                
                if "NAMA BANK" in opsi_duplikat:
                    df_var = df_var.drop_duplicates(subset=['country', 'bank'], keep='first')
                
                elif "NILAI DATA" in opsi_duplikat:
                    has_data = df_var[requested_years_list].notna().any(axis=1)
                    df_with_data = df_var[has_data]
                    df_no_data = df_var[~has_data]
                    
                    df_with_data = df_with_data.drop_duplicates(subset=requested_years_list, keep='first')
                    df_var = pd.concat([df_with_data, df_no_data], ignore_index=True)
                
                df_var = df_var.drop(columns=['is_standard', 'is_valid_bank_name', 'bank_len'])
                
                # Ubah ke format Panjang (Stata Panel)
                df_long = pd.melt(df_var, id_vars=['country', 'bank'], value_vars=requested_years_list, var_name='year', value_name=var_name)
                df_long = df_long.drop_duplicates(subset=['country', 'bank', 'year'], keep='first')
                all_processed_dfs.append(df_long)
            
            st.caption("⚙️ Menyusun arsitektur kolom Stata final...")
            
            # TAHAP 3: Penggabungan Keseluruhan
            if all_processed_dfs:
                df_master = reduce(lambda left, right: pd.merge(left, right, on=['country', 'bank', 'year'], how='outer'), all_processed_dfs)
                
                # 🚀 MESIN BALANCED PANEL MUTLAK (STRICT)
                if "Balanced" in opsi_panel:
                    # 1. Cari riwayat bank yang punya setidaknya 1 nilai kosong di variabel/tahun mana pun
                    bank_cacat = df_master[df_master[variabel_list].isna().any(axis=1)][['country', 'bank']].drop_duplicates()
                    
                    # 2. Tendang KESELURUHAN baris dari bank yang cacat tersebut
                    if not bank_cacat.empty:
                        df_master = df_master.set_index(['country', 'bank'])
                        bank_cacat_idx = bank_cacat.set_index(['country', 'bank']).index
                        df_master = df_master[~df_master.index.isin(bank_cacat_idx)].reset_index()
                    
                df_master = df_master.sort_values(by=['country', 'bank', 'year']).reset_index(drop=True)
                df_master['country_id'] = df_master.groupby('country').ngroup() + 1
                df_master['bank_id'] = df_master.groupby('bank').ngroup() + 1
                
                kolom_awal = ['country_id', 'bank_id', 'country', 'bank', 'year']
                df_master = df_master[kolom_awal + variabel_list]
                
                status.update(label="✅ Selesai: Master Data Panel Berhasil Dirakit!", state="complete", expanded=False)
                st.balloons()
                
                # ==========================================
                # 6. DASHBOARD HASIL & TOMBOL UNDUH
                # ==========================================
                st.write("### 📊 Parameter Statistik Akhir")
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("📌 Total Variabel", len(variabel_list))
                m2.metric("🌍 Zona Negara", df_master['country'].nunique())
                m3.metric("🏦 Bank Terdaftar", f"{df_master['bank'].nunique():,}")
                m4.metric("📈 Total Baris", f"{len(df_master):,}")
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.dataframe(df_master, use_container_width=True, hide_index=True, height=400)
                
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_master.to_excel(writer, index=False, sheet_name='Master_Data_Stata')
                    
                st.markdown("<br>", unsafe_allow_html=True)
                c1, c2, c3 = st.columns([1,2,1])
                with c2:
                    st.download_button(
                        label="📥 EXPORT MASTER DATA (.xlsx)",
                        data=output.getvalue(),
                        file_name=f"Master_Stata_Final_{start_year}_{end_year}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
            else:
                status.update(label="❌ Terjadi Kesalahan", state="error", expanded=True)
                st.error("Gagal menyatukan data. File mungkin kosong atau terhapus semua oleh filter negara.")
