import streamlit as st
import pandas as pd
import io
import re
from functools import reduce

# ==========================================
# 1. PENGATURAN HALAMAN & CSS ULTRA PREMIUM
# ==========================================
st.set_page_config(page_title="Bloomberg Panel Pro", page_icon="💠", layout="wide")

st.markdown("""
    <style>
        /* Tipografi & Latar Belakang */
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
        
        /* Tombol Utama Bergaya Modern SaaS */
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

        /* Kartu Metrik (Glassmorphism) */
        div[data-testid="metric-container"] {
            background: linear-gradient(145deg, #ffffff, #f0f4f8);
            border-left: 5px solid #26D0CE;
            padding: 15px 20px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.04);
        }
        div[data-testid="metric-container"] label {
            color: #475569 !important;
            font-weight: 700;
            font-size: 14px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='premium-title'>Bloomberg Panel Engine</div>", unsafe_allow_html=True)
st.markdown("<div class='premium-subtitle'>Mendeteksi Otomatis, Menghapus Duplikat Cerdas, & Membangun Stata Panel</div>", unsafe_allow_html=True)

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
    st.write("### ⚙️ Engine Parameters")
    st.write("---")
    
    with st.expander("🗓️ Tentukan Rentang Tahun", expanded=True):
        col1, col2 = st.columns(2)
        start_year = col1.number_input("Dari", value=2015, step=1)
        end_year = col2.number_input("Sampai", value=2025, step=1)

    with st.expander("🛡️ Kecerdasan Pembersih Duplikat", expanded=True):
        opsi_duplikat = st.radio(
            "Pilih Mode Deteksi:",
            [
                "Biarkan semua data (Jangan hapus)", 
                "Hapus jika NAMA BANK persis sama",
                "Hapus jika NILAI DATA sama (Simpan nama bank yang terpendek/paling bersih)"
            ],
            help="Opsi ke-3 sangat cerdas: Jika ada Bank A dan Bank A Tbk memiliki deretan angka 2015-2025 yang identik, sistem akan menghapus Bank A Tbk dan menyisakan nama yang lebih rapi."
        )

    with st.expander("⚖️ Desain Tabel Stata", expanded=True):
        opsi_panel = st.radio(
            "Format Panel Data:",
            ["Unbalanced (Aman & Fleksibel)", "Balanced (Ketat & Utuh)"]
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
        # Kamus untuk menampung data mentah (format menyamping) berdasarkan nama variabelnya
        dict_variabel_dfs_wide = {}
        
        with st.status("🛠️ Mesin AI sedang membedah dan membersihkan ratusan file...", expanded=True) as status:
            progress_bar = st.progress(0)
            
            # TAHAP 1: Ekstraksi seluruh file ke memori
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
                df['country'] = df['country_code'].map(country_map).fillna(df['country_code'])
                df = df.rename(columns={'Name': 'bank'})
                
                df['bank'] = df['bank'].astype(str).str.strip().str.upper()
                df['country'] = df['country'].astype(str).str.strip().str.upper()
                
                # Saring tahun yang valid dan ubah nama kolom menjadi angka (int)
                valid_year_cols = [col for col in year_cols if start_year <= int(str(col).split(":")[1][:4]) <= end_year]
                rename_dict = {col: int(str(col).split(":")[1][:4]) for col in valid_year_cols}
                
                for col in valid_year_cols:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                df = df.rename(columns=rename_dict)
                valid_year_ints = list(rename_dict.values())
                
                # Simpan dalam format WIDE (menyamping)
                df_wide = df[['country', 'bank'] + valid_year_ints]
                
                if clean_var_name not in dict_variabel_dfs_wide:
                    dict_variabel_dfs_wide[clean_var_name] = []
                dict_variabel_dfs_wide[clean_var_name].append(df_wide)
                
                progress_bar.progress((i + 1) / len(uploaded_files))
            
            st.caption("🔄 Mengidentifikasi duplikat dan memilih penulisan nama bank terbaik...")
            
            # TAHAP 2: Pembersihan Lintas-File & Perubahan Format
            all_processed_dfs = []
            variabel_list = list(dict_variabel_dfs_wide.keys())
            
            for var_name, list_dfs in dict_variabel_dfs_wide.items():
                df_var = pd.concat(list_dfs, ignore_index=True)
                year_cols_in_df = [c for c in df_var.columns if isinstance(c, int)]
                
                # LOGIKA CERDAS: Hitung panjang karakter nama bank untuk menentukan mana yang "terbersih"
                df_var['bank_len'] = df_var['bank'].str.len()
                df_var = df_var.sort_values(by=['country', 'bank_len', 'bank'])
                
                # Eksekusi Penghapusan Duplikat
                if "NAMA BANK" in opsi_duplikat:
                    df_var = df_var.drop_duplicates(subset=['country', 'bank'], keep='first')
                elif "NILAI DATA" in opsi_duplikat:
                    # Menghapus duplikat nilai data (karena nama terpendek ditaruh di atas, ia yang akan selamat)
                    df_var = df_var.drop_duplicates(subset=['country'] + year_cols_in_df, keep='first')
                
                df_var = df_var.drop(columns=['bank_len'])
                
                # Ubah ke format Memanjang (Long Format)
                df_long = pd.melt(df_var, id_vars=['country', 'bank'], value_vars=year_cols_in_df, var_name='year', value_name=var_name)
                df_long = df_long.dropna(subset=[var_name])
                df_long = df_long.drop_duplicates(subset=['country', 'bank', 'year'], keep='first')
                
                all_processed_dfs.append(df_long)
            
            st.caption("⚙️ Menyusun arsitektur kolom Stata...")
            
            # TAHAP 3: Penggabungan Final
            if all_processed_dfs:
                df_master = reduce(lambda left, right: pd.merge(left, right, on=['country', 'bank', 'year'], how='outer'), all_processed_dfs)
                
                if "Balanced" in opsi_panel:
                    df_master = df_master.dropna(subset=variabel_list)
                    
                df_master = df_master.sort_values(by=['country', 'bank', 'year']).reset_index(drop=True)
                df_master['country_id'] = df_master.groupby('country').ngroup() + 1
                df_master['bank_id'] = df_master.groupby('bank').ngroup() + 1
                
                kolom_awal = ['country_id', 'bank_id', 'country', 'bank', 'year']
                df_master = df_master[kolom_awal + variabel_list]
                
                status.update(label="✅ Berhasil: Master Data Stata Berhasil Dirakit!", state="complete", expanded=False)
                st.balloons()
                
                # ==========================================
                # 6. DASHBOARD HASIL & TOMBOL UNDUH
                # ==========================================
                st.write("### 📊 Parameter Statistik Akhir")
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("📌 Total Variabel", len(variabel_list))
                m2.metric("🌍 Zona Negara", df_master['country'].nunique())
                m3.metric("🏦 Bank Terdaftar", f"{df_master['bank'].nunique():,}")
                m4.metric("📈 Total Baris (N)", f"{len(df_master):,}")
                
                st.markdown("<br>", unsafe_allow_html=True)
                # Menyembunyikan Index agar tabel makin mirip software profesional
                st.dataframe(df_master, use_container_width=True, hide_index=True, height=400)
                
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_master.to_excel(writer, index=False, sheet_name='Master_Data_Stata')
                    
                st.markdown("<br>", unsafe_allow_html=True)
                c1, c2, c3 = st.columns([1,2,1])
                with c2:
                    st.download_button(
                        label="📥 EXPORT DATA (.xlsx)",
                        data=output.getvalue(),
                        file_name=f"Master_Stata_Final_{start_year}_{end_year}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
            else:
                status.update(label="❌ Terjadi Kesalahan Ekstraksi", state="error", expanded=True)
                st.error("Gagal menyatukan data. Silakan periksa kembali file Anda.")
