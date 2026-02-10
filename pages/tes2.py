import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import io
import re

# --- SETUP HALAMAN ---
st.set_page_config(page_title="Replika R - Hasil Asli Data (900 DPI)", layout="wide")

# --- CSS UNTUK MENYESUAIKAN TAMPILAN ---
st.markdown("""
    <style>
    /* Mengatur container agar ada garis tepi seperti di gambar */
    [data-testid="stVerticalBlock"] > div:has(div.stExpander) {
        border: 1px solid #ddd;
        padding: 10px;
        border-radius: 5px;
    }
    /* Tombol Simpan Gambar Warna Hijau */
    div.stButton > button:first-child {
        background-color: #5cb85c;
        color: white;
        height: 3em;
        width: 100%;
        border-radius: 5px;
        border: none;
        font-weight: bold;
    }
    /* Tombol Reset Warna Merah Muda */
    div.stButton > button[key="reset_btn"] {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
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

# --- STRUKTUR KOLOM (Kiri: Input, Kanan: Preview) ---
col_sidebar, col_main = st.columns([1, 2.5])

with col_sidebar:
    # --- 1. DATA INPUT ---
    with st.container(border=True):
        st.markdown("### 1. Data Input")
        uploaded_file = st.file_uploader("Upload Excel/CSV", type=["xlsx", "csv"], label_visibility="collapsed")
        
        # Inisialisasi variabel
        df = None
        x_col = None
        y_col = None

        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                df.columns = df.columns.astype(str).str.strip()
                df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
                
                x_col = st.selectbox("Sumbu X (Kategori):", df.columns)
                y_col = st.selectbox("Sumbu Y (Angka):", df.columns, index=1 if len(df.columns) > 1 else 0)
            except Exception as e:
                st.error(f"Gagal membaca file: {e}")

    # --- 2. STATISTIK MANUAL EDIT ---
    with st.container(border=True):
        st.markdown("### 2. Statistik _Manual Edit")
        
        if df is not None and x_col and y_col:
            df[y_col] = pd.to_numeric(df[y_col], errors='coerce')
            df = df.dropna(subset=[x_col, y_col])
            
            # Urutkan grup secara alami
            cats = sorted(df[x_col].unique(), key=natural_sort_key)

            if 'data_config' not in st.session_state:
                st.session_state['data_config'] = {}

            # Simpan data asli jika belum ada di session state
            for cat in cats:
                cat_str = str(cat)
                if cat_str not in st.session_state['data_config']:
                    sub_data = df[df[x_col] == cat][y_col]
                    stats = sub_data.describe()
                    st.session_state['data_config'][cat_str] = {
                        'med': float(stats['50%']),
                        'q1': float(stats['25%']),
                        'q3': float(stats['75%']),
                        'whislo': float(stats['min']),
                        'whishi': float(stats['max'])
                    }

            pilih_group = st.selectbox("Pilih Group:", options=[str(c) for c in cats])
            
            # Input Manual (Stacked Vertikal)
            conf = st.session_state['data_config'][pilih_group]
            
            new_med = st.number_input("Median:", value=conf['med'], format="%.4f")
            new_q1 = st.number_input("Q1 (Bawah):", value=conf['q1'], format="%.4f")
            new_q3 = st.number_input("Q3 (Atas):", value=conf['q3'], format="%.4f")
            
            # Update data di memory
            st.session_state['data_config'][pilih_group].update({
                'med': new_med, 'q1': new_q1, 'q3': new_q3
            })

            if st.button("🔄 Reset ke Hasil Asli Data", key="reset_btn", use_container_width=True):
                st.session_state.pop('data_config', None)
                st.rerun()
        else:
            st.info("Upload file untuk mengedit statistik.")

    # --- 3. VISUAL SETTING ---
    with st.container(border=True):
        st.markdown("### 3. Visual Setting")
        point_size = st.number_input("Ukuran Titik:", value=7.00, step=0.10, format="%.2f")
        jitter_val = st.number_input("Jitter (Sebar):", value=0.12, step=0.01, format="%.2f")

    # --- 4. SIMPAN GRAFIK ---
    with st.container(border=True):
        st.markdown("### 4. Simpan Grafik")
        dpi_val = st.selectbox("Pilih Resolusi (DPI):", [300, 600, 900, 1200])
        btn_simpan = st.button("💾 SIMPAN GAMBAR")

# --- AREA KANAN (PREVIEW) ---
with col_main:
    st.markdown("<h1 style='text-align: center;'>Preview Tabel</h1>", unsafe_allow_html=True)
    
    if df is not None and x_col and y_col:
        # Layouting Gambar
        fig, ax = plt.subplots(figsize=(10, 6))
        
        bxp_stats = []
        for cat in cats:
            cat_str = str(cat)
            c = st.session_state['data_config'][cat_str]
            bxp_stats.append({
                'label': cat_str, 
                'med': c['med'], 
                'q1': c['q1'], 
                'q3': c['q3'],
                'whislo': c['whislo'], 
                'whishi': c['whishi'], 
                'fliers': []
            })
        
        # Gambar Boxplot
        ax.bxp(bxp_stats, showfliers=False, patch_artist=True,
               boxprops=dict(facecolor='#CCCCCC', color='#595959', linewidth=1),
               medianprops=dict(color='#595959', linewidth=2),
               whiskerprops=dict(color='#595959'),
               capprops=dict(color='#595959'))
        
        # Tambahkan Scatter/Jitter
        cat_map = {str(c): i+1 for i, c in enumerate(cats)}
        df_plot = df.copy()
        df_plot['x_idx'] = df_plot[x_col].astype(str).map(cat_map)
        
        np.random.seed(42)
        noise = np.random.uniform(-jitter_val, jitter_val, size=len(df_plot))
        
        ax.scatter(df_plot['x_idx'] + noise, df_plot[y_col], 
                   s=point_size * 10,  # Skala ukuran titik
                   c='orange', edgecolor='red', linewidth=0.5, alpha=0.8, zorder=3)
        
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.grid(axis='y', linestyle='--', alpha=0.3)
        
        st.pyplot(fig)
        
        # Logika Download saat tombol Simpan ditekan
        if btn_simpan:
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=dpi_val, bbox_inches='tight')
            st.download_button(
                label="✅ Klik di sini untuk mengunduh file PNG",
                data=buf,
                file_name="grafik_box_plot.png",
                mime="image/png"
            )
    else:
        st.info("Preview akan muncul di sini setelah file di-upload dan kolom dipilih.")
