import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import io

st.set_page_config(page_title="Replika R Manual", layout="centered")
st.title("📊 Replika R (Pilih Kolom Sendiri)")

# --- 1. UPLOAD FILE ---
uploaded_file = st.file_uploader("Upload File Excel", type=["xlsx", "csv"])

if uploaded_file:
    try:
        # BACA FILE (Header di baris 2/Index 1, karena baris 1 kosong)
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, header=1)
        else:
            # Coba Sheet2 dulu, kalau gagal baru sheet 1
            try:
                df = pd.read_excel(uploaded_file, sheet_name="Sheet2", header=1)
            except:
                df = pd.read_excel(uploaded_file, header=1)

        # Bersihkan nama kolom dari spasi aneh
        df.columns = df.columns.str.strip()
        
        # Hapus kolom yang namanya kosong/Unnamed
        cols = [c for c in df.columns if "Unnamed" not in str(c)]
        df = df[cols]

        # --- 2. MENU PILIH KOLOM (INI YANG KEMARIN HILANG) ---
        st.subheader("👇 1. Pilih Kolom Dulu:")
        col1, col2 = st.columns(2)
        
        with col1:
            # Dropdown untuk memilih Sumbu X
            pilihan_x = st.selectbox("Pilih Data Sumbu X (Dosis):", df.columns)
            
        with col2:
            # Dropdown untuk memilih Sumbu Y
            pilihan_y = st.selectbox("Pilih Data Sumbu Y (Angka/Genetik):", df.columns)

        # --- 3. PROSES DATA ---
        if pilihan_x and pilihan_y:
            # Pastikan Y jadi angka
            df[pilihan_y] = pd.to_numeric(df[pilihan_y], errors='coerce')
            df = df.dropna(subset=[pilihan_x, pilihan_y])

            # Atur Urutan Dosis (0 gy, 5 gy...)
            urutan_custom = ["0 gy", "5 gy", "10 gy", "15 gy", "20 gy"]
            cek_isi = df[pilihan_x].unique().astype(str)
            
            # Cek apakah tulisan di excel sama dengan urutan_custom
            if any(x in cek_isi for x in urutan_custom):
                urutan_final = urutan_custom
            else:
                # Kalau beda (misal 0 Gy huruf besar), urutkan angka saja
                import re
                def sorter(val):
                    m = re.search(r'\d+', str(val))
                    return int(m.group()) if m else 999
                urutan_final = sorted(df[pilihan_x].unique(), key=sorter)

            # --- 4. PENGATURAN TAMPILAN ---
            st.divider()
            st.subheader("👇 2. Atur Tampilan:")
            
            with st.expander("Klik untuk Buka Pengaturan Gambar", expanded=True):
                c_set1, c_set2 = st.columns(2)
                with c_set1:
                    w_fig = st.slider("Lebar Gambar", 3.0, 8.0, 5.0)
                    h_fig = st.slider("Tinggi Gambar", 3.0, 8.0, 4.0)
                with c_set2:
                    seed_val = st.number_input("Kode Posisi (Ganti biar titik geser)", value=42)
                    jitter_val = st.slider("Sebaran (Jitter)", 0.0, 0.3, 0.12)

            # --- 5. GAMBAR GRAFIK (GAYA R) ---
            fig, ax = plt.subplots(figsize=(w_fig, h_fig))

            # Gaya Kotak R (theme_classic + border)
            ax.set_facecolor('white')
            for spine in ax.spines.values():
                spine.set_visible(True)
                spine.set_color('#595959')
                spine.set_linewidth(1)

            # Gambar Boxplot (Abu-abu R)
            sns.boxplot(
                data=df, x=pilihan_x, y=pilihan_y, order=urutan_final, ax=ax,
                width=0.65, showfliers=False,
                boxprops=dict(facecolor='#CCCCCC', edgecolor='#595959', linewidth=0.9),
                whiskerprops=dict(color='#595959', linewidth=0.9),
                capprops=dict(color='#595959', linewidth=0.9),
                medianprops=dict(color='#595959', linewidth=2)
            )

            # Gambar Titik (Oranye R)
            np.random.seed(seed_val) # Kunci posisi
            sns.stripplot(
                data=df, x=pilihan_x, y=pilihan_y, order=urutan_final, ax=ax,
                jitter=jitter_val, size=7,
                edgecolor='red', linewidth=0.7, # Pinggir Merah
                color='orange', alpha=0.9,      # Isi Oranye
                marker='o'
            )

            # Label Sumbu (Ambil dari pilihan Bapak)
            ax.set_xlabel(pilihan_x, fontweight='bold', color='black')
            ax.set_ylabel(pilihan_y, fontweight='bold', color='black')
            ax.tick_params(colors='black')

            st.pyplot(fig)

            # --- 6. DOWNLOAD ---
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=300, bbox_inches='tight')
            buf.seek(0)
            st.download_button("⬇️ Download Gambar PNG", buf, "grafik_replika_R.png", "image/png")

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
        st.write("Coba cek file Excelnya lagi Pak.")
