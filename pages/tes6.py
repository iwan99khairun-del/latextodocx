import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import io

# --- SETUP HALAMAN ---
st.set_page_config(page_title="Replika R - Edit Per Group", layout="wide")
st.title("📊 Replika R (Edit Detail Per Group)")

# CSS Supaya input angka lebih compact
st.markdown("""
<style>
    .stNumberInput input { background-color: #f0f2f6; }
    .block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# --- 1. UPLOAD FILE ---
uploaded_file = st.file_uploader("Upload File Excel/CSV", type=["xlsx", "csv"])

if uploaded_file:
    try:
        # --- BACA DATA ---
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, header=0) # Asumsi header baris pertama
        else:
            df = pd.read_excel(uploaded_file, header=0)

        # Bersihkan nama kolom
        df.columns = df.columns.astype(str).str.strip()
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        
        # --- PILIH KOLOM ---
        c1, c2 = st.columns(2)
        with c1:
            x_col = st.selectbox("Sumbu X (Kategori):", df.columns)
        with c2:
            y_col = st.selectbox("Sumbu Y (Angka):", df.columns, index=1 if len(df.columns) > 1 else 0)

        if x_col and y_col:
            # Pastikan format data benar
            df[y_col] = pd.to_numeric(df[y_col], errors='coerce')
            df = df.dropna(subset=[x_col, y_col])
            
            # --- 2. INISIALISASI DATA STATISTIK (Hanya sekali jalan) ---
            # Kita simpan konfigurasi di session_state supaya tidak hilang saat ganti grup
            if 'data_config' not in st.session_state:
                st.session_state['data_config'] = {}
            
            # Deteksi Kategori Unik (Semua Group)
            # Coba urutkan secara logis jika ada angka
            try:
                cats = sorted(df[x_col].unique())
            except:
                cats = df[x_col].unique()

            # Generate config awal untuk setiap kategori jika belum ada
            for cat in cats:
                cat_str = str(cat)
                if cat_str not in st.session_state['data_config']:
                    # Hitung statistik asli data
                    sub_data = df[df[x_col] == cat][y_col]
                    stats = sub_data.describe()
                    
                    st.session_state['data_config'][cat_str] = {
                        'med': float(stats['50%']),
                        'q1': float(stats['25%']),
                        'q3': float(stats['75%']),
                        'whislo': float(stats['min']),
                        'whishi': float(stats['max']),
                        'width': 0.65 # Default lebar
                    }

            # --- LAYOUT KIRI (MENU) & KANAN (GAMBAR) ---
            st.write("---")
            col_kiri, col_kanan = st.columns([1, 2])

            with col_kiri:
                # ==========================
                # A. PENGATURAN UMUM
                # ==========================
                with st.expander("1️⃣ Pengaturan Gambar (Global)", expanded=False):
                    fig_w = st.slider("Lebar Gambar", 3.0, 15.0, 6.0)
                    fig_h = st.slider("Tinggi Gambar", 3.0, 10.0, 5.0)
                    point_size = st.slider("Ukuran Titik", 2.0, 15.0, 7.0)
                    jitter_val = st.slider("Jitter (Sebaran)", 0.0, 0.4, 0.12)
                    seed_val = st.number_input("Seed (Acak)", value=42)

                # ==========================
                # B. PILIH GROUP (DROPDOWN)
                # ==========================
                st.write("")
                st.subheader("2️⃣ Edit Kotak")
                
                # Dropdown untuk memilih group mana yang mau diedit
                pilih_group = st.selectbox(
                    "Pilih Group yang mau diedit:",
                    options=[str(c) for c in cats]
                )

                # Tampilkan Slider KHUSUS untuk group yang dipilih
                if pilih_group:
                    st.info(f"🛠️ Sedang mengedit: **{pilih_group}**")
                    
                    # Ambil data dari memory (session_state)
                    current_conf = st.session_state['data_config'][pilih_group]
                    
                    # 1. Lebar
                    new_width = st.slider(f"Lebar Kotak ({pilih_group})", 0.1, 1.0, current_conf['width'])
                    
                    # 2. Tinggi (Statistik)
                    c_h1, c_h2 = st.columns(2)
                    with c_h1:
                        new_q3 = st.number_input("Atas (Q3)", value=current_conf['q3'])
                        new_q1 = st.number_input("Bawah (Q1)", value=current_conf['q1'])
                    with c_h2:
                        new_med = st.number_input("Tengah (Median)", value=current_conf['med'])
                    
                    # UPDATE MEMORY
                    # Setiap kali slider digeser, simpan balik ke session_state
                    st.session_state['data_config'][pilih_group]['width'] = new_width
                    st.session_state['data_config'][pilih_group]['q3'] = new_q3
                    st.session_state['data_config'][pilih_group]['q1'] = new_q1
                    st.session_state['data_config'][pilih_group]['med'] = new_med

            with col_kanan:
                # ==========================
                # C. GAMBAR GRAFIK
                # ==========================
                st.subheader("🖼️ Hasil Grafik")
                
                fig, ax = plt.subplots(figsize=(fig_w, fig_h))
                
                # Style R
                ax.set_facecolor('white')
                for spine in ax.spines.values():
                    spine.set_visible(True)
                    spine.set_color('#595959')
                    spine.set_linewidth(1)

                # --- 1. SIAPKAN DATA BOXPLOT DARI MEMORY ---
                bxp_stats = []
                list_widths = []
                
                # Kita loop semua kategori agar urutannya benar di gambar
                for cat in cats:
                    cat_str = str(cat)
                    conf = st.session_state['data_config'][cat_str]
                    
                    bxp_stats.append({
                        'label': cat_str,
                        'med': conf['med'],
                        'q1': conf['q1'],
                        'q3': conf['q3'],
                        'whislo': conf['whislo'], # Whisker pakai data asli
                        'whishi': conf['whishi'], # Whisker pakai data asli
                        'fliers': []
                    })
                    list_widths.append(conf['width'])

                # --- 2. GAMBAR BOXPLOT MANUAL ---
                ax.bxp(bxp_stats, showfliers=False, widths=list_widths,
                       patch_artist=True,
                       boxprops=dict(facecolor='#CCCCCC', edgecolor='#595959', linewidth=0.9),
                       medianprops=dict(color='#595959', linewidth=2),
                       whiskerprops=dict(color='#595959', linewidth=0.9),
                       capprops=dict(color='#595959', linewidth=0.9))

                # --- 3. GAMBAR TITIK ASLI (OVERLAY) ---
                # Mapping kategori ke angka 1, 2, 3 untuk scatter plot
                cat_map = {str(c): i+1 for i, c in enumerate(cats)}
                df['x_idx'] = df[x_col].apply(lambda x: cat_map[str(x)])
                
                np.random.seed(int(seed_val))
                noise = np.random.uniform(-jitter_val, jitter_val, size=len(df))
                
                ax.scatter(df['x_idx'] + noise, df[y_col],
                           s=point_size**1.5,
                           c='orange', edgecolor='red', linewidth=0.7, alpha=0.9,
                           zorder=3)

                # Label
                ax.set_xlabel(x_col, fontweight='bold')
                ax.set_ylabel(y_col, fontweight='bold')
                
                st.pyplot(fig)

                # --- DOWNLOAD ---
                st.write("---")
                col_d1, col_d2 = st.columns([2, 1])
                with col_d1:
                    dpi = st.selectbox("Resolusi Download", [300, 600], format_func=lambda x: f"{x} DPI (High Res)")
                with col_d2:
                    buf = io.BytesIO()
                    fig.savefig(buf, format="png", dpi=dpi, bbox_inches='tight')
                    buf.seek(0)
                    st.write("")
                    st.download_button("⬇️ Download PNG", buf, "grafik_custom.png", "image/png", use_container_width=True)

    except Exception as e:
        st.error(f"Terjadi kesalahan atau data belum dipilih: {e}")
