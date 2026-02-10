import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import io
import re

# --- SETUP HALAMAN ---
st.set_page_config(page_title="Replika R - Hasil Asli Data", layout="wide")

# --- CSS CUSTOM UNTUK TAMPILAN ---
st.markdown("""
    <style>
    /* Mengatur background kontainer input */
    [data-testid="stVerticalBlock"] > div:has(div.stButton) {
        #background-color: #f8f9fa;
    }
    .main-sidebar {
        background-color: #eeeeee;
        padding: 15px;
        border-radius: 5px;
    }
    /* Warna tombol Simpan Gambar */
    div.stButton > button:first-child {
        background-color: #5cb85c;
        color: white;
        border-radius: 5px;
        width: 100%;
        font-weight: bold;
    }
    /* Warna tombol Reset */
    div.stButton > button[key="reset_btn"] {
        background-color: #fff1f1;
        color: #d9534f;
        border: 1px solid #d9534f;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNGSI PENGURUTAN ALAMI ---
def natural_sort_key(s):
    s = str(s)
    angka = re.search(r'(\d+)', s)
    if angka:
        return int(angka.group(1))
    return s

# --- LOGIKA DASHBOARD ---
col_sidebar, col_main = st.columns([1, 3])

with col_sidebar:
    # --- 1. DATA INPUT ---
    with st.container(border=True):
        st.markdown("### 1. Data Input")
        uploaded_file = st.file_uploader("Upload Excel/CSV", type=["xlsx", "csv"], label_visibility="collapsed")
        
        # Placeholder untuk selectbox agar tidak eror sebelum file diupload
        x_col = None
        y_col = None
        
        if uploaded_file:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            df.columns = df.columns.astype(str).str.strip()
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            
            x_col = st.selectbox("Sumbu X (Kategori):", df.columns)
            y_col = st.selectbox("Sumbu Y (Angka):", df.columns, index=1 if len(df.columns) > 1 else 0)

    # --- 2. STATISTIK MANUAL EDIT ---
    with st.container(border=True):
        st.markdown("### 2. Statistik _Manual Edit")
        
        if uploaded_file and x_col and y_col:
            df[y_col] = pd.to_numeric(df[y_col], errors='coerce')
            df = df.dropna(subset=[x_col, y_col])
            cats = sorted(df[x_col].unique(), key=natural_sort_key)

            if 'data_config' not in st.session_state:
                st.session_state['data_config'] = {}

            for cat in cats:
                cat_str = str(cat)
                if cat_str not in st.session_state['data_config']:
                    sub_data = df[df[x_col] == cat][y_col]
                    stats = sub_data.describe()
                    st.session_state['data_config'][cat_str] = {
                        'med': float(stats['50%']), 'q1': float(stats['25%']), 
                        'q3': float(stats['75%']), 'whislo': float(stats['min']),
                        'whishi': float(stats['max'])
                    }

            pilih_group = st.selectbox("Pilih Group:", options=[str(c) for c in cats])
            
            col_stat1, col_stat2 = st.columns(1) # Stacked as per image
            conf = st.session_state['data_config'][pilih_group]
            
            new_med = st.number_input("Median:", value=conf['med'], format="%.4f")
            new_q1 = st.number_input("Q1 (Bawah):", value=conf['q1'], format="%.4f")
            new_q3 = st.number_input("Q3 (Atas):", value=conf['q3'], format="%.4f")
            
            # Update Session State
            st.session_state['data_config'][pilih_group].update({'med': new_med, 'q1': new_q1, 'q3': new_q3})

            if st.button("🔄 Reset ke Hasil Asli Data", key="reset_btn", use_container_width=True):
                del st.session_state['data_config']
                st.rerun()

    # --- 3. VISUAL SETTING ---
    with st.container(border=True):
        st.markdown("### 3. Visual Setting")
        point_size = st.number_input("Ukuran Titik:", value=7.00, step=0.5)
        jitter_val = st.number_input("Jitter (Sebar):", value=0.12, step=0.01)

    # --- 4. SIMPAN GRAFIK ---
    with st.container(border=True):
        st.markdown("### 4. Simpan Grafik")
        dpi_val = st.selectbox("Pilih Resolusi (DPI):", [300, 600, 900], index=0)
        btn_simpan = st.button("💾 SIMPAN GAMBAR")

# --- AREA KANAN (PREVIEW) ---
with col_main:
    st.markdown("<h1 style='text-align: center;'>Preview Tabel</h1>", unsafe_allow_html=True)
    
    if uploaded_file and x_col and y_col:
        # Layouting Preview (Tabel & Grafik)
        tab1, tab2 = st.tabs(["📈 Grafik Preview", "📄 Data Tabel"])
        
        with tab1:
            # Logic Gambar Matplotlib (Sesuai kode lama Anda)
            fig, ax = plt.subplots(figsize=(8, 5))
            bxp_stats = []
            for cat in cats:
                cat_str = str(cat)
                c = st.session_state['data_config'][cat_str]
                bxp_stats.append({
                    'label': cat_str, 'med': c['med'], 'q1': c['q1'], 'q3': c['q3'],
                    'whislo': c['whislo'], 'whishi': c['whishi'], 'fliers': []
                })
            
            ax.bxp(bxp_stats, showfliers=False, patch_artist=True,
                   boxprops=dict(facecolor='#CCCCCC', color='#595959'),
                   medianprops=dict(color='#595959', linewidth=2))
            
            # Scatter Plot Jitter
            cat_map = {str(c): i+1 for i, c in enumerate(cats)}
            df['x_idx'] = df[x_col].apply(lambda x: cat_map[str(x)])
            np.random.seed(42)
            noise = np.random.uniform(-jitter_val, jitter_val, size=len(df))
            ax.scatter(df['x_idx'] + noise, df[y_col], s=point_size**2, 
                       c='orange', edgecolor='red', alpha=0.7, zorder=3)
            
            st.pyplot(fig)
            
            if btn_simpan:
                buf = io.BytesIO()
                fig.savefig(buf, format="png", dpi=dpi_val, bbox_inches='tight')
                st.download_button(label="Klik untuk Mendownload", data=buf, 
                                   file_name="grafik.png", mime="image/png")

        with tab2:
            st.dataframe(df, use_container_width=True)
    else:
        st.info("Silakan upload file di kolom kiri untuk melihat preview.")
