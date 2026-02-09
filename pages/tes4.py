import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import io

# --- SETUP HALAMAN ---
st.set_page_config(page_title="Replika R - Edit Per Kotak", layout="wide") # Layout wide biar muat menu banyak
st.title("📊 Replika R (Edit Tiap Kotak Manual)")
st.markdown("""
<style>
    .stNumberInput input { background-color: #f0f2f6; }
</style>
""", unsafe_allow_html=True)

# --- 1. UPLOAD FILE ---
col_up, col_info = st.columns([1, 2])
with col_up:
    uploaded_file = st.file_uploader("Upload File Excel/CSV", type=["xlsx", "csv"])

if uploaded_file:
    try:
        # --- BACA DATA OTOMATIS (Simple Mode) ---
        if uploaded_file.name.endswith('.csv'):
            df_raw = pd.read_csv(uploaded_file, header=None, nrows=10)
        else:
            df_raw = pd.read_excel(uploaded_file, header=None, nrows=10)
            
        # Langsung baca (asumsi header di baris yang mengandung text)
        uploaded_file.seek(0)
        # Kita pakai slider simple untuk header agar tidak ribet
        header_idx = st.number_input("Baris Header (Mulai 0)", 0, 10, 0)
        
        uploaded_file.seek(0)
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, header=header_idx)
        else:
            df = pd.read_excel(uploaded_file, header=header_idx)

        # Bersihkan
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        
        # --- PILIH KOLOM ---
        st.write("---")
        c1, c2 = st.columns(2)
        with c1:
            x_col = st.selectbox("Sumbu X (Kategori):", df.columns)
        with c2:
            y_col = st.selectbox("Sumbu Y (Angka):", df.columns, index=1 if len(df.columns)>1 else 0)

        if x_col and y_col:
            df[y_col] = pd.to_numeric(df[y_col], errors='coerce')
            df = df.dropna(subset=[x_col, y_col])
            
            # Urutan Kategori
            urutan_custom = ["0 gy", "5 gy", "10 gy", "15 gy", "20 gy"]
            unique_vals = df[x_col].unique().astype(str)
            
            if any(x in unique_vals for x in urutan_custom):
                cats = [x for x in urutan_custom if x in unique_vals]
                # Tambah sisa kategori yang tidak ada di urutan_custom
                cats += [x for x in unique_vals if x not in urutan_custom]
            else:
                try:
                    cats = sorted(df[x_col].unique())
                except:
                    cats = df[x_col].unique()

            # --- LOGIKA EDIT PER KOTAK ---
            st.write("---")
            st.subheader("🛠️ Edit Kotak Satu per Satu")
            st.info("⚠️ Mengubah Q1/Q3 berarti mengubah tinggi kotak secara visual (Memanipulasi tampilan statistik).")

            # Siapkan container untuk data plot
            plot_stats = []
            
            # Kita bagi layar jadi 2: Kiri untuk Menu Edit, Kanan untuk Grafik
            col_menu, col_grafik = st.columns([1, 2])

            with col_menu:
                with st.container(height=600): # Scrollable container
                    st.write("**Pengaturan Per Grup:**")
                    
                    for i, cat in enumerate(cats):
                        # Ambil data asli grup ini
                        sub_data = df[df[x_col] == cat][y_col]
                        stats = sub_data.describe()
                        
                        # Buat Expander untuk setiap kategori
                        with st.expander(f"📦 Grup: {cat}", expanded=(i==0)):
                            c_w, c_q = st.columns(2)
                            
                            # 1. LEBAR
                            width = st.slider(f"Lebar ({cat})", 0.1, 1.0, 0.65, key=f"w_{i}")
                            
                            # 2. TINGGI (Q1 dan Q3)
                            # Q3 = Garis Atas Kotak
                            # Q1 = Garis Bawah Kotak
                            q3_asli = stats['75%']
                            q1_asli = stats['25%']
                            med_asli = stats['50%']
                            
                            st.caption("Atur Tinggi Kotak:")
                            q3_new = st.number_input(f"Batas Atas (Q3)", value=float(q3_asli), step=0.5, key=f"q3_{i}")
                            med_new = st.number_input(f"Garis Tengah (Median)", value=float(med_asli), step=0.5, key=f"med_{i}")
                            q1_new = st.number_input(f"Batas Bawah (Q1)", value=float(q1_asli), step=0.5, key=f"q1_{i}")
                            
                            # Simpan data untuk plotting nanti
                            plot_stats.append({
                                'label': str(cat),
                                'med': med_new,
                                'q1': q1_new,
                                'q3': q3_new,
                                'whislo': stats['min'], # Whisker tetap data asli
                                'whishi': stats['max'], # Whisker tetap data asli
                                'fliers': [], # Hilangkan outlier biar bersih
                                'width': width
                            })

            with col_grafik:
                # --- PENGATURAN UMUM ---
                with st.expander("⚙️ Pengaturan Umum (Ukuran Gambar & Titik)", expanded=False):
                    cg1, cg2, cg3 = st.columns(3)
                    with cg1:
                        fig_w = st.slider("Lebar Kanvas", 4.0, 15.0, 6.0)
                        fig_h = st.slider("Tinggi Kanvas", 3.0, 10.0, 5.0)
                    with cg2:
                        point_size = st.slider("Ukuran Titik", 2.0, 15.0, 7.0)
                        jitter_val = st.slider("Jitter", 0.0, 0.3, 0.1)
                    with cg3:
                        y_lim_max = st.number_input("Max Y Axis (Zoom)", value=0.0)

                # --- GAMBAR GRAFIK CUSTOM ---
                fig, ax = plt.subplots(figsize=(fig_w, fig_h))
                
                # Style R
                ax.set_facecolor('white')
                for spine in ax.spines.values():
                    spine.set_visible(True)
                    spine.set_color('#595959')
                    spine.set_linewidth(1)

                # 1. GAMBAR KOTAK MANUAL (Pakai data dari inputan Bapak)
                # Kita pisahkan width karena bxp butuh list of width
                widths = [p['width'] for p in plot_stats]
                
                # Matplotlib bxp menggambar berdasarkan statistik yang kita suap
                ax.bxp(plot_stats, showfliers=False, widths=widths, 
                       patch_artist=True, # Biar bisa diwarnai
                       boxprops=dict(facecolor='#CCCCCC', edgecolor='#595959', linewidth=0.9),
                       medianprops=dict(color='#595959', linewidth=2),
                       whiskerprops=dict(color='#595959', linewidth=0.9),
                       capprops=dict(color='#595959', linewidth=0.9))

                # 2. GAMBAR TITIK ASLI (Overlay)
                # Kita harus mapping kategori ke angka 1, 2, 3... karena bxp pakai koordinat 1-based
                df['x_idx'] = df[x_col].apply(lambda x: cats.index(str(x)) + 1)
                
                np.random.seed(42)
                # Buat jitter manual karena kita pakai plot manual
                x_jittered = df['x_idx'] + np.random.uniform(-jitter_val, jitter_val, size=len(df))
                
                ax.scatter(x_jittered, df[y_col], 
                           s=point_size**1.5, # Scale size
                           c='orange', edgecolors='red', linewidth=0.7, alpha=0.9, zorder=3)

                # Label
                ax.set_xlabel(x_col, fontweight='bold')
                ax.set_ylabel(y_col, fontweight='bold')
                
                if y_lim_max > 0:
                    ax.set_ylim(top=y_lim_max)

                st.pyplot(fig)

                # --- DOWNLOAD ---
                buf = io.BytesIO()
                fig.savefig(buf, format="png", dpi=300, bbox_inches='tight')
                buf.seek(0)
                st.download_button("⬇️ Download PNG HD", buf, "grafik_custom.png", "image/png", use_container_width=True)

    except Exception as e:
        st.error(f"Eror: {e}")
