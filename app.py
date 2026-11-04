import streamlit as st
import pandas as pd
import io
import re
from functools import reduce

# ==========================================
# 1. PENGATURAN HALAMAN & CSS KUSTOM
# ==========================================
st.set_page_config(page_title="Bloomberg Panel Pro", page_icon="📈", layout="wide")

# CSS untuk mempercantik UI (Warna Gradient, Tombol Melengkung, dll)
st.markdown("""
    <style>
        /* Mengubah font judul menjadi gradient */
        .title-gradient {
            background: -webkit-linear-gradient(45deg, #1E88E5, #42A5F5, #004D40);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 42px;
            font-weight: 800;
            text-align: center;
            margin-bottom: 5px;
        }
        .subtitle {
            text-align: center;
            color: #6c757d;
            font-size: 18px;
            margin-bottom: 30px;
        }
        /* Mempercantik tombol */
        .stButton>button {
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            transition: 0.3s;
        }
        .stButton>button:hover {
            transform: scale(1.02);
        }
    </style>
""", unsafe_allow_html=True)

# Header Aplikasi
st.markdown("<div class='title-gradient'>Bloomberg Panel Builder Pro</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Ekstraksi Otomatis & Penggabungan Ratusan File Excel ke Master Data Stata</div>", unsafe_allow_html=True)

# ==========================================
# 2. KAMUS NEGARA & FUNGSI PELACAK
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
        if parts[-1].upper() == 'EQUITY':
            return parts[-2].upper()
        else:
            return parts[-1].upper()
    return "UNKNOWN"

# ==========================================
# 3. SIDEBAR (MENU PENGATURAN)
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/settings.png", width=50)
    st.write("## ⚙️ Pengaturan Panel")
    
    st.write("---")
    st.write("🗓️ **Rentang Tahun**")
    col_yr1, col_yr2 = st.columns(2)
    with col_yr1:
        start_year = st.number_input("Dari", value=2015, step=1)
    with col_yr2:
        end_year = st.number_input("Sampai", value=2025, step=1)
    
    st.write("---")
    st.write("⚖️ **Kaidah Data (Stata)**")
    opsi_panel = st.radio(
        "Pilih Format Panel:",
        ["Unbalanced (Biarkan baris kosong/NaN)", 
         "Balanced (Hapus bank jika ada 1 nilai kosong)"],
        label_visibility="collapsed"
    )
    
    st.write("---")
    st.info("💡 **Tips:** Seret semua file Excel sekaligus ke area unggah di layar utama.")

# ==========================================
# 4. AREA KERJA UTAMA (DRAG & DROP)
# ==========================================
# Kotak unggah file yang lebar
uploaded_files = st.file_uploader(
    "📤 Unggah seluruh file Excel mentah (grid1_xxx.xlsx) Anda di sini...", 
    type=["xlsx"], 
    accept_multiple_files=True
)

st.markdown("<br>", unsafe_allow_html=True)
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    mulai_proses = st.button("🚀 MULAI PROSES PENGGABUNGAN DATA", use_container_width=True, type="primary")

st.markdown("<hr>", unsafe_allow_html=True)

# ==========================================
# 5. LOGIKA PEMROSESAN & TAMPILAN HASIL
# ==========================================
if mulai_proses:
    if not uploaded_files:
        st.warning("⚠️ Mohon unggah setidaknya satu file Excel terlebih dahulu.")
    else:
        all_processed_dfs = []
        variabel_list = []
        
        # Animasi status yang modern
        with st.status("🛠️ Membedah dan Menyatukan File Excel...", expanded=True) as status:
            
            progress_bar = st.progress(0)
            
            for i, file in enumerate(uploaded_files):
                st.write(f"Menganalisis file: `{file.name}`")
                df = pd.read_excel(file, engine='openpyxl')
                year_cols = [col for col in df.columns if ":" in str(col)]
                
                if not year_cols:
                    continue
                    
                raw_var_name = str(year_cols[0]).split(":")[0].strip()
                clean_var_name = re.sub(r'[^a-zA-Z0-9_]', '_', raw_var_name).lower()
                clean_var_name = re.sub(r'_+', '_', clean_var_name).strip('_')
                
                original_var_name = clean_var_name
                counter = 1
                while clean_var_name in variabel_list:
                    clean_var_name = f"{original_var_name}_{counter}"
                    counter += 1
                variabel_list.append(clean_var_name)
                
                df = df.drop([0, 1]).reset_index(drop=True)
                
                df['country_code'] = df['Ticker'].apply(get_country_code)
                df['country'] = df['country_code'].map(country_map).fillna(df['country_code'])
                df = df.rename(columns={'Name': 'bank'})
                
                df['bank'] = df['bank'].astype(str).str.strip().str.upper()
                df['country'] = df['country'].astype(str).str.strip().str.upper()
                
                valid_year_cols = [col for col in year_cols if start_year <= int(str(col).split(":")[1][:4]) <= end_year]
                
                for col in valid_year_cols:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                df_long = pd.melt(df, id_vars=['country', 'bank'], value_vars=valid_year_cols, var_name='year_raw', value_name=clean_var_name)
                df_long['year'] = df_long['year_raw'].apply(lambda x: int(str(x).split(":")[1][:4]))
                df_long = df_long[['country', 'bank', 'year', clean_var_name]]
                
                df_long = df_long.drop_duplicates(subset=['country', 'bank', 'year'])
                all_processed_dfs.append(df_long)
                
                # Update progress bar
                progress_bar.progress((i + 1) / len(uploaded_files))
            
            st.write("🔄 Menggabungkan semua variabel menjadi Master Data...")
            
            if all_processed_dfs:
                df_master = reduce(lambda left, right: pd.merge(left, right, on=['country', 'bank', 'year'], how='outer'), all_processed_dfs)
                
                if "Balanced" in opsi_panel:
                    df_master = df_master.dropna(subset=variabel_list)
                    
                df_master = df_master.sort_values(by=['country', 'bank', 'year']).reset_index(drop=True)
                
                df_master['country_id'] = df_master.groupby('country').ngroup() + 1
                df_master['bank_id'] = df_master.groupby('bank').ngroup() + 1
                
                kolom_awal = ['country_id', 'bank_id', 'country', 'bank', 'year']
                df_master = df_master[kolom_awal + variabel_list]
                
                status.update(label="✅ Data Berhasil Disatukan!", state="complete", expanded=False)
                
                # Munculkan pop-up sukses sebentar di pojok kanan bawah
                st.toast('Proses Selesai!', icon='🎉')
                
                # ==========================================
                # 6. DASHBOARD HASIL (METRIK & TABEL)
                # ==========================================
                st.write("### 📊 Ringkasan Dataset")
                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    st.metric("Total Variabel", len(variabel_list))
                with m2:
                    st.metric("Total Negara", df_master['country'].nunique())
                with m3:
                    st.metric("Total Bank Unik", df_master['bank'].nunique())
                with m4:
                    st.metric("Baris Observasi", f"{len(df_master):,}")
                
                # Menampilkan tabel dengan gaya yang rapi
                st.dataframe(df_master, use_container_width=True, height=350)
                
                # Tombol Download (Lebar & Menonjol)
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_master.to_excel(writer, index=False, sheet_name='Data_Panel_Stata')
                    
                st.markdown("<br>", unsafe_allow_html=True)
                st.download_button(
                    label="📥 UNDUH MASTER DATA STATA (.xlsx)",
                    data=output.getvalue(),
                    file_name=f"Master_Panel_Data_{start_year}_{end_year}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    type="primary"
                )
            else:
                status.update(label="❌ Gagal mengekstrak data", state="error", expanded=True)
                st.error("Pastikan file yang diunggah memiliki format yang benar.")