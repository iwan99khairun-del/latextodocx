import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import io

# --- SETUP HALAMAN ---
st.set_page_config(page_title="Replika R - Full Custom", layout="wide")
st.title("📊 Replika R (Kontrol Total)")

# CSS Biar tampilan input angka lebih rapi
st.markdown("""
<style>
    .stNumberInput input { background-color: #f0f2f6; }
    div[data-testid="stExpander"] div[role="button"] p { font-size: 1.1rem; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 1. UPLOAD FILE ---
col_up, _ = st.columns([1, 2])
with col_up:
    uploaded_file = st.file_uploader("Upload File Excel/CSV", type=["xlsx", "csv"])

if uploaded_file:
    try:
        # --- BACA DATA ---
        if uploaded_file.name.endswith('.csv'):
            df_preview = pd.read_csv(uploaded_file, header=None, nrows=10)
        else:
            df_preview = pd.read_excel(uploaded_file, header=None, nrows=10)
        
        # Auto-detect header simpel (anggap baris 0)
        uploaded_file.seek(0)
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, header=0)
        else:
            df = pd.read_excel(uploaded_file, header=0)

        # Bersihkan nama kolom
        df.columns = df.columns.astype(str).str.strip()
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        
        # --- PILIH KOLOM ---
        st.write("---")
        c1, c2 = st.columns(2)
        with c1:
            x_col = st.selectbox("Sumbu X (Kategori):", df.columns)
        with c2:
            y_col = st.selectbox("Sumbu Y (Angka):", df.columns, index=1 if len(df.columns) > 1 else 0)

        if x_col and y_col:
            # Pastikan Y angka
            df[y_col] = pd.to_numeric(df[y_col], errors='coerce')
            df = df.dropna(subset=[x_col, y_col])
            
            # Tentukan Urutan Kategori
            urutan_custom = ["0 gy", "5 gy", "10 gy", "15 gy", "20 gy"]
            unique_vals = df[x_col].unique().astype(str)
            
            # Cek apakah data cocok dengan urutan custom
            cats = []
            if any(x in unique_vals for x in urutan_custom):
                cats = [x for x in urutan_custom if x in unique_vals]
                # Tambah sisa kategori yang tidak ada di list custom
                cats += [x for x in unique_vals if x not in cats]
            else:
                try:
                    cats = sorted(df[x_col].unique())
                except:
                    cats = df[x_col].unique()

            # --- LAYOUT UTAMA (Kiri: Menu, Kanan: Gambar) ---
            st.write("---")
            col_menu, col_grafik = st.columns([1.3, 2]) # Kiri agak kecil, Kanan besar

            # ==========================
            # MENU KIRI (CONTROLS)
            # ==========================
            with col_menu:
                # ----------------------------------------
                # 1. PENGATURAN GLOBAL (SESUAI REQUEST BAPAK)
                # ----------------------------------------
                with st.expander("⚙️ Buka Pengaturan Gambar & Titik (Global)", expanded=True):
                    # Kolom 1: Dimensi
                    st.markdown("##### 📏 Dimensi")
                    fig_w = st.slider("Lebar (Width)", 3.0, 15.0, 6.0)
                    fig_h = st.slider("Tinggi (Height)", 3.0, 10.0, 5.0)
                    
                    st.divider()
                    
                    # Kolom 2: Posisi & Bulatan
                    c_p1, c_p2 = st.columns(2)
                    with c_p1:
                        st.markdown("##### 🎯 Posisi")
                        seed = st.number_input("Seed", value=42, label_visibility="collapsed")
                        st.caption("Kode Posisi (Seed)")
                        jitter = st.slider("Sebaran", 0.0, 0.4, 0.12, label_visibility="collapsed")
                        st.caption("Sebaran (Jitter)")
                    
                    with c_p2:
                        st.markdown("##### 🔵 Bulatan")
                        point_size_val = st.slider("Size", 2.0, 15.0, 7.0, label_visibility="collapsed")
                        st.caption("Ukuran Titik")

                # ----------------------------------------
                # 2. PENGATURAN PER KOTAK (INDIVIDUAL)
                # ----------------------------------------
                st.info("👇 **Edit Kotak Satu per Satu di bawah ini:**")
                
                # Container Scrollable biar tidak terlalu panjang ke bawah
                with st.container(height=500):
                    plot_stats = [] # List untuk menyimpan data manual
                    
                    for i, cat in enumerate(cats):
                        # Ambil statistik asli dari data
                        sub_data = df[df[x_col].astype(str) == str(cat)][y_col]
                        stats = sub_data.describe()
                        
                        st.markdown(f"**📦 Grup: {cat}**")
                        
                        # Buat kolom kecil-kecil
                        cm1, cm2 = st.columns(2)
                        with cm1:
                            # Slider Lebar
                            width_box = st.slider(f"Lebar", 0.1, 1.0, 0.65, key=f"w_{i}", help=f"Lebar kotak untuk {cat}")
                        with cm2:
                            # Median (Garis Tengah)
                            med_val = st.number_input("Tengah (Median)", value=float(stats['50%']), step=0.5, key=f"m_{i}")

                        cq1, cq2 = st.columns(2)
                        with cq1:
                            # Q3 (Atas)
                            q3_val = st.number_input("Atas (Q3)", value=float(stats['75%']), step=0.5, key=f"q3_{i}")
                        with cq2:
                            # Q1 (Bawah)
                            q1_val = st.number_input("Bawah (Q1)", value=float(stats['25%']), step=0.5, key=f"q1_{i}")

                        st.divider()

                        # Simpan settingan user ke list
                        plot_stats.append({
                            'label': str(cat),
                            'med': med_val,
                            'q1': q1_val,
                            'q3': q3_val,
                            'whislo': stats['min'], # Whisker tetap ikut data asli
                            'whishi': stats['max'], # Whisker tetap ikut data asli
                            'fliers': [], 
                            'width': width_box
                        })

            # ==========================
            # BAGIAN KANAN (GRAFIK)
            # ==========================
            with col_grafik:
                st.subheader("🖼️ Pratinjau Grafik")
                
                # Setup Canvas
                fig, ax = plt.subplots(figsize=(fig_w, fig_h))
                
                # Style Dasar
                ax.set_facecolor('white')
                for spine in ax.spines.values():
                    spine.set_visible(True)
                    spine.set_color('#595959')
                    spine.set_linewidth(1)

                # 1. GAMBAR KOTAK (Berdasarkan Input Manual di Kiri)
                # Ambil list lebar yang sudah diatur user
                widths_list = [p['width'] for p in plot_stats]
                
                ax.bxp(plot_stats, showfliers=False, widths=widths_list,
                       patch_artist=True,
                       boxprops=dict(facecolor='#CCCCCC', edgecolor='#595959', linewidth=0.9),
                       medianprops=dict(color='#595959', linewidth=2),
                       whiskerprops=dict(color='#595959', linewidth=0.9),
                       capprops=dict(color='#595959', linewidth=0.9))

                # 2. GAMBAR TITIK (Overlay Data Asli)
                # Mapping kategori ke index 1, 2, 3...
                # Kita perlu index ini karena matplotlib bxp pakai koordinat 1,2,3
                cat_map = {str(c): i+1 for i, c in enumerate(cats)}
                df['x_idx'] = df[x_col].astype(str).map(cat_map)
                
                # Jitter Manual
                np.random.seed(int(seed))
                # Buat noise acak antara -jitter s/d +jitter
                noise = np.random.uniform(-jitter, jitter, size=len(df))
                x_jittered = df['x_idx'] + noise
                
                # Plot Titik
                ax.scatter(x_jittered, df[y_col], 
                           s=point_size_val**1.5, # Skala ukuran biar pas
                           c='orange', edgecolor='red', linewidth=0.7, alpha=0.9,
                           zorder=3) # zorder 3 biar di atas kotak

                # Label & Ticks
                ax.set_xlabel(x_col, fontweight='bold', color='black')
                ax.set_ylabel(y_col, fontweight='bold', color='black')
                ax.tick_params(colors='black')

                # Tampilkan
                st.pyplot(fig)

                # DOWNLOAD
                st.write("---")
                col_d1, col_d2 = st.columns([2,1])
                with col_d1:
                     dpi_select = st.selectbox("Resolusi", ["300 DPI", "600 DPI"], index=0)
                     dpi = int(dpi_select.split()[0])
                with col_d2:
                    buf = io.BytesIO()
                    fig.savefig(buf, format="png", dpi=dpi, bbox_inches='tight')
                    buf.seek(0)
                    st.write("")
                    st.download_button("⬇️ Download PNG", buf, "grafik_custom.png", "image/png", use_container_width=True)

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
