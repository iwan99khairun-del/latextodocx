import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import io  # Untuk fitur download

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Replika R + Download", layout="centered") # Layout centered biar gambar gak kegedean
st.title("📊 Replika R (Kecil & Download)")

# --- 1. UPLOAD FILE ---
uploaded_file = st.file_uploader("Upload File Excel", type=["xlsx", "csv"])

if uploaded_file:
    # --- 2. PROSES DATA ---
    try:
        # Baca file (Handle baris 1 kosong)
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, header=1)
        else:
            try:
                df = pd.read_excel(uploaded_file, sheet_name="Sheet2", header=1)
            except:
                df = pd.read_excel(uploaded_file, header=1)

        # Bersihkan
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', na=False)]
        df = df.dropna(how='all')

        # Cek Kolom
        cols = df.columns.tolist()
        if len(cols) < 2:
            st.error("Data kurang kolom.")
            st.stop()
            
        col_x = cols[0] # Dosis
        col_y = cols[1] # Angka

        # Urutan Dosis (Agar 0 gy, 5 gy, dst)
        urutan_custom = ["0 gy", "5 gy", "10 gy", "15 gy", "20 gy"]
        cek_data = df[col_x].unique().astype(str)
        
        if any(x in cek_data for x in urutan_custom):
            # Jika tulisan di excel sama persis dengan urutan custom
            df[col_x] = pd.Categorical(df[col_x], categories=urutan_custom, ordered=True)
            urutan_final = urutan_custom
        else:
            # Fallback (Urutkan angka saja)
            import re
            def sorter(x):
                m = re.search(r'\d+', str(x))
                return int(m.group()) if m else 999
            urutan_final = sorted(df[col_x].unique(), key=sorter)

        # Paksa jadi angka
        df[col_y] = pd.to_numeric(df[col_y], errors='coerce')
        df = df.dropna(subset=[col_x, col_y])

        # --- 3. PENGATURAN TAMPILAN (MENU KIRI) ---
        with st.sidebar:
            st.header("🎛️ Pengaturan Gambar")
            
            # UKURAN GAMBAR (Biar bisa dikecilin)
            st.subheader("📏 Ukuran Preview")
            fig_w = st.slider("Lebar Gambar", 3.0, 10.0, 5.0) # Default 5 (Kecil)
            fig_h = st.slider("Tinggi Gambar", 3.0, 10.0, 4.0) # Default 4 (Kecil)
            
            st.divider()
            
            # KONTROL POSISI TITIK
            st.subheader("🎯 Posisi Titik")
            seed_val = st.number_input("Kode Posisi (Seed)", value=42, step=1, help="Ganti angka ini biar posisi titik berubah.")
            jitter_width = st.slider("Sebaran (Jitter)", 0.05, 0.3, 0.12)
            point_size = st.slider("Ukuran Titik", 30, 100, 60)

        # --- 4. MEMBUAT GRAFIK ---
        # Pakai ukuran dari slider
        fig, ax = plt.subplots(figsize=(fig_w, fig_h))
        
        # Style Box (Mirip R)
        ax.set_facecolor('white')
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_color('#595959') # grey35
            spine.set_linewidth(1)

        # Gambar Boxplot
        sns.boxplot(
            data=df, x=col_x, y=col_y, order=urutan_final, ax=ax,
            width=0.65, showfliers=False,
            boxprops=dict(facecolor='#CCCCCC', edgecolor='#595959', linewidth=0.9), # grey80
            whiskerprops=dict(color='#595959', linewidth=0.9),
            capprops=dict(color='#595959', linewidth=0.9),
            medianprops=dict(color='#595959', linewidth=2)
        )

        # Gambar Titik (Jitter)
        np.random.seed(seed_val) # Kunci posisi
        sns.stripplot(
            data=df, x=col_x, y=col_y, order=urutan_final, ax=ax,
            jitter=jitter_width,
            size=np.sqrt(point_size),
            edgecolor='red', linewidth=0.7, # Pinggir Merah
            color='orange', alpha=0.9,      # Isi Oranye
            marker='o'
        )

        # Label
        ax.set_xlabel(col_x, color='black', fontweight='bold')
        ax.set_ylabel(col_y, color='black', fontweight='bold')
        ax.tick_params(colors='black')
        
        # --- TAMPILKAN GRAFIK ---
        st.pyplot(fig)

        # --- 5. MENU DOWNLOAD ---
        st.write("---")
        col_dl1, col_dl2 = st.columns([2, 1])
        
        with col_dl1:
            st.write("👇 **Simpan Gambar:**")
            
            # Simpan gambar ke memori
            buffer = io.BytesIO()
            fig.savefig(buffer, format="png", dpi=300, bbox_inches='tight') # Resolusi tinggi (300 DPI)
            buffer.seek(0)
            
            # Tombol Download
            st.download_button(
                label="⬇️ Download Gambar (PNG)",
                data=buffer,
                file_name="grafik_replika_R.png",
                mime="image/png",
                use_container_width=True
            )

    except Exception as e:
        st.error(f"Eror: {e}")
