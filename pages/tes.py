import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="R to Python Converter", layout="wide")
st.title("📊 Replika Grafik R (ggplot2)")
st.markdown("Kode ini didesain untuk meniru gaya `ggplot2` + `geom_jitter` yang Bapak kirim.")

# --- 1. UPLOAD FILE ---
uploaded_file = st.file_uploader("Upload File Excel (Sesuai script R: Sheet2)", type=["xlsx", "csv"])

if uploaded_file:
    # --- 2. PROSES DATA (MIRIP BAGIAN DPLYR DI R) ---
    try:
        # R Code: df <- import("...", sheet = "Sheet2")
        # Python: Kita coba baca, handle baris kosong (header=1) sesuai file Bapak
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, header=1)
        else:
            # Coba baca Sheet2 kalau ada, kalau tidak baca sheet pertama
            try:
                df = pd.read_excel(uploaded_file, sheet_name="Sheet2", header=1)
            except:
                df = pd.read_excel(uploaded_file, header=1)

        # Bersihkan kolom hantu
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', na=False)]
        df = df.dropna(how='all')

        # Pastikan Kolom Ada
        cols = df.columns.tolist()
        if len(cols) < 2:
            st.error("Data kurang kolom.")
            st.stop()
            
        col_x = cols[0] # Irradiation Doses
        col_y = cols[1] # Diversity_Genetic

        # R Code: mutate(Irradiation Doses = factor(..., levels = c("0 gy", ...)))
        # Python: Kita buat Categorical agar urutannya persis
        urutan_custom = ["0 gy", "5 gy", "10 gy", "15 gy", "20 gy"]
        
        # Cek apakah data di Excel sesuai dengan tulisan di atas
        # Kalau tidak sama persis (misal '0 Gy' vs '0 gy'), kita biarkan urutan alami
        cek_data = df[col_x].unique().astype(str)
        if any(x in cek_data for x in urutan_custom):
            df[col_x] = pd.Categorical(df[col_x], categories=urutan_custom, ordered=True)
            urutan_final = urutan_custom
        else:
            # Fallback jika nama beda (misal pakai huruf besar)
            import re
            def sorter(x):
                m = re.search(r'\d+', str(x))
                return int(m.group()) if m else 999
            urutan_final = sorted(df[col_x].unique(), key=sorter)

        # R Code: as.numeric(Diversity_Genetic) & filter(!is.na)
        df[col_y] = pd.to_numeric(df[col_y], errors='coerce')
        df = df.dropna(subset=[col_x, col_y])

        # --- 3. PENGATURAN TAMPILAN (MIRIP GGPLOT) ---
        with st.sidebar:
            st.header("🎛️ Kontrol Tampilan")
            st.write("Atur ini agar posisi titik sama persis dengan R:")
            
            # Kunci utama agar posisi sama
            seed_val = st.number_input("Seed (Acak Posisi)", value=42, step=1, help="Ganti angka ini sampai posisi titik mirip.")
            
            st.divider()
            jitter_width = st.slider("Lebar Jitter (R: 0.12)", 0.05, 0.3, 0.12)
            point_size = st.slider("Ukuran Titik (R: 2.2)", 30, 100, 60) # Skala matplotlib beda dgn R
            point_alpha = st.slider("Transparansi (R: 0.9)", 0.1, 1.0, 0.9)

        # --- 4. MEMBUAT GRAFIK (MATPLOTLIB RASA GGPLOT) ---
        fig, ax = plt.subplots(figsize=(7, 5))
        
        # A. SET TEMA (theme_classic + panel.border)
        ax.set_facecolor('white') # Latar putih
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_color('#595959') # grey35
            spine.set_linewidth(1)

        # B. GAMBAR BOXPLOT
        # R: fill="grey80", color="grey35", width=0.65, fatten=2
        sns.boxplot(
            data=df, x=col_x, y=col_y, order=urutan_final, ax=ax,
            width=0.65,
            showfliers=False, # outlier.shape = NA
            # Warna
            boxprops=dict(facecolor='#CCCCCC', edgecolor='#595959', linewidth=0.9), # grey80 & grey35
            whiskerprops=dict(color='#595959', linewidth=0.9),
            capprops=dict(color='#595959', linewidth=0.9),
            medianprops=dict(color='#595959', linewidth=2) # fatten=2
        )

        # C. GAMBAR JITTER (TITIK)
        # R: geom_jitter(width=0.12, shape=21, fill="orange", color="red")
        
        # Trik: Kunci Random State agar posisi titik DIAM dan BISA DIATUR
        np.random.seed(seed_val) 
        
        sns.stripplot(
            data=df, x=col_x, y=col_y, order=urutan_final, ax=ax,
            jitter=jitter_width,
            size=np.sqrt(point_size), # Konversi size
            edgecolor='red', # color = "red"
            linewidth=0.7,   # stroke = 0.7
            color='orange',  # fill = "orange"
            alpha=point_alpha,
            marker='o'       # Bulat
        )

        # D. LABEL & GRID
        ax.set_xlabel("Irradiation Doses", color='black')
        ax.set_ylabel("Diversity Genetic", color='black')
        ax.tick_params(colors='black', labelsize=10)
        
        # Tampilkan
        st.pyplot(fig)
        
        st.success(f"✅ Grafik berhasil dibuat dengan gaya R!")
        st.caption("Catatan: Jika posisi titik belum sama persis, ubah angka **'Seed'** di menu sebelah kiri.")

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
        st.write("Pastikan file Excel memiliki struktur yang benar (Header di baris 2).")

else:
    st.info("Silakan upload file Excel Bapak.")
