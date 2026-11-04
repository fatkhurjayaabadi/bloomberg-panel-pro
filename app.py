import streamlit as st
import pandas as pd
import io
import re
from functools import reduce

# ==========================================
# 1. PENGATURAN HALAMAN & CSS PREMIUM
# ==========================================
st.set_page_config(page_title="Bloomberg Panel Pro", page_icon="💠", layout="wide")

st.markdown("""
    <style>
        .premium-title {
            background: linear-gradient(90deg, #0f2027, #203a43, #2c5364);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 48px;
            font-weight: 900;
            text-align: center;
            letter-spacing: -1px;
            margin-bottom: 0px;
        }
        .premium-subtitle {
            text-align: center;
            color: #546e7a;
            font-size: 18px;
            font-weight: 500;
            margin-bottom: 40px;
            letter-spacing: 0.5px;
        }
        .stButton>button {
            background: linear-gradient(135deg, #1e88e5 0%, #1565c0 100%);
            color: white;
            border-radius: 12px;
            border: none;
            padding: 10px 24px;
            font-size: 18px;
            font-weight: bold;
            box-shadow: 0 4px 15px rgba(30, 136, 229, 0.3);
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(30, 136, 229, 0.5);
            color: white;
        }
        div[data-testid="metric-container"] {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='premium-title'>Bloomberg Panel Data Engine</div>", unsafe_allow_html=True)
st.markdown("<div class='premium-subtitle'>Ekstraksi Otomatis, Penyelarasan, & Penggabungan Ratusan File Excel</div>", unsafe_allow_html=True)

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
# 3. SIDEBAR PENGATURAN
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/dashboard-layout.png", width=60)
    st.write("### ⚙️ Parameter Analisis")
    
    with st.expander("🗓️ Rentang Waktu", expanded=True):
        col1, col2 = st.columns(2)
        start_year = col1.number_input("Dari Tahun", value=2015, step=1)
        end_year = col2.number_input("S/d Tahun", value=2025, step=1)

    with st.expander("🛡️ Penanganan Duplikat", expanded=True):
        opsi_duplikat = st.radio(
            "Pilih metode penyaringan:",
            [
                "Jangan hapus (Biarkan semua)", 
                "Hapus jika NAMA BANK persis sama",
                "Hapus jika NILAI DATA sama persis (Beda nama bank tidak apa-apa)"
            ],
            help="Opsi ke-3 akan mencari bank di negara yang sama yang memiliki deretan angka keuangan identik dari tahun awal s/d akhir."
        )

    with st.expander("⚖️ Struktur Data Stata", expanded=True):
        opsi_panel = st.radio(
            "Kaidah Panel:",
            ["Unbalanced (Aman & Fleksibel)", "Balanced (Sangat Ketat)"],
            help="Balanced akan membuang bank sepenuhnya jika ada 1 variabel yang kosong di tahun tertentu."
        )

# ==========================================
# 4. AREA KERJA UTAMA
# ==========================================
uploaded_files = st.file_uploader(
    "📥 Seret dan Lepas (Drag & Drop) seluruh file Excel Bloomberg (grid1_xxx.xlsx) Anda di sini", 
    type=["xlsx"], 
    accept_multiple_files=True
)

st.markdown("<br>", unsafe_allow_html=True)
col_spacer1, col_btn, col_spacer2 = st.columns([1, 2, 1])
with col_btn:
    mulai_proses = st.button("🚀 COMPILE & MERGE MASTER DATA", use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ==========================================
# 5. MESIN PEMROSESAN
# ==========================================
if mulai_proses:
    if not uploaded_files:
        st.warning("⚠️ Silakan unggah minimal 1 file Excel terlebih dahulu pada kotak di atas.")
    else:
        # Menggunakan Dictionary untuk menampung file dengan variabel yang sama
        dict_variabel_dfs = {}
        
        with st.status("🛠️ Membedah, Membersihkan, dan Menyatukan File...", expanded=True) as status:
            progress_bar = st.progress(0)
            
            for i, file in enumerate(uploaded_files):
                st.caption(f"Menganalisis: `{file.name}`")
                df = pd.read_excel(file, engine='openpyxl')
                year_cols = [col for col in df.columns if ":" in str(col)]
                
                if not year_cols:
                    continue
                    
                # Ekstraksi Nama Variabel
                raw_var_name = str(year_cols[0]).split(":")[0].strip()
                clean_var_name = re.sub(r'[^a-zA-Z0-9_]', '_', raw_var_name).lower()
                clean_var_name = re.sub(r'_+', '_', clean_var_name).strip('_')
                
                # Pembersihan Baris & Ekstraksi Negara
                df = df.drop([0, 1]).reset_index(drop=True)
                df['country_code'] = df['Ticker'].apply(get_country_code)
                df['country'] = df['country_code'].map(country_map).fillna(df['country_code'])
                df = df.rename(columns={'Name': 'bank'})
                
                df['bank'] = df['bank'].astype(str).str.strip().str.upper()
                df['country'] = df['country'].astype(str).str.strip().str.upper()
                
                valid_year_cols = [col for col in year_cols if start_year <= int(str(col).split(":")[1][:4]) <= end_year]
                for col in valid_year_cols:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                if "NAMA BANK" in opsi_duplikat:
                    df = df.drop_duplicates(subset=['country', 'bank'], keep='first')
                elif "NILAI DATA" in opsi_duplikat:
                    df = df.drop_duplicates(subset=['country'] + valid_year_cols, keep='first')
                
                # Wide to Long (Melting)
                df_long = pd.melt(df, id_vars=['country', 'bank'], value_vars=valid_year_cols, var_name='year_raw', value_name=clean_var_name)
                df_long['year'] = df_long['year_raw'].apply(lambda x: int(str(x).split(":")[1][:4]))
                df_long = df_long[['country', 'bank', 'year', clean_var_name]]
                df_long = df_long.drop_duplicates(subset=['country', 'bank', 'year'])
                
                # Masukkan ke dalam dictionary berdasarkan nama variabelnya
                if clean_var_name not in dict_variabel_dfs:
                    dict_variabel_dfs[clean_var_name] = []
                dict_variabel_dfs[clean_var_name].append(df_long)
                
                progress_bar.progress((i + 1) / len(uploaded_files))
            
            st.caption("🔄 Menggabungkan data yang bervariabel sama dan menyusun Master Database...")
            
            if dict_variabel_dfs:
                # 1. Tumpuk baris (Concat) untuk file yang memiliki nama variabel sama
                all_processed_dfs = []
                variabel_list = list(dict_variabel_dfs.keys())
                
                for var_name, list_dfs in dict_variabel_dfs.items():
                    # Menyatukan data ke bawah jika variabel sama
                    df_var_gabungan = pd.concat(list_dfs, ignore_index=True)
                    # Menghapus tumpang tindih data jika ada bank yang sama terekam 2x di file berbeda
                    df_var_gabungan = df_var_gabungan.drop_duplicates(subset=['country', 'bank', 'year'], keep='first')
                    all_processed_dfs.append(df_var_gabungan)
                
                # 2. Gabung menyamping (Merge) antar variabel yang berbeda
                df_master = reduce(lambda left, right: pd.merge(left, right, on=['country', 'bank', 'year'], how='outer'), all_processed_dfs)
                
                # 3. Penerapan Aturan Balanced Panel
                if "Balanced" in opsi_panel:
                    df_master = df_master.dropna(subset=variabel_list)
                    
                # 4. Pengurutan Rapi & Pembuatan ID Stata
                df_master = df_master.sort_values(by=['country', 'bank', 'year']).reset_index(drop=True)
                df_master['country_id'] = df_master.groupby('country').ngroup() + 1
                df_master['bank_id'] = df_master.groupby('bank').ngroup() + 1
                
                kolom_awal = ['country_id', 'bank_id', 'country', 'bank', 'year']
                df_master = df_master[kolom_awal + variabel_list]
                
                status.update(label="✅ Berhasil: Master Data Stata Siap!", state="complete", expanded=False)
                st.toast('Selesai Diproses!', icon='🔥')
                
                # ==========================================
                # 6. DASHBOARD HASIL
                # ==========================================
                st.write("### 📊 Ringkasan Dataset Akhir")
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("📌 Total Kolom Variabel", len(variabel_list))
                m2.metric("🌍 Total Negara", df_master['country'].nunique())
                m3.metric("🏦 Bank Terdaftar", f"{df_master['bank'].nunique():,}")
                m4.metric("📈 Baris Observasi", f"{len(df_master):,}")
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.dataframe(df_master, use_container_width=True, height=400)
                
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_master.to_excel(writer, index=False, sheet_name='Master_Data_Stata')
                    
                st.markdown("<br>", unsafe_allow_html=True)
                c1, c2, c3 = st.columns([1,2,1])
                with c2:
                    st.download_button(
                        label="📥 UNDUH MASTER DATA (.xlsx)",
                        data=output.getvalue(),
                        file_name=f"Master_Panel_Data_{start_year}_{end_year}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
            else:
                status.update(label="❌ Terjadi Kesalahan Ekstraksi", state="error", expanded=True)
                st.error("Tidak ada data yang berhasil diekstrak. Periksa format file Anda.")
