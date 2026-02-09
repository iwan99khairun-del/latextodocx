import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import re

st.set_page_config(page_title="Grafik Final Anti-Eror")
st.title("🛠️ Grafik: Mode Pembersih Paksa")

uploaded_file = st.file_uploader("Upload File Excel/CSV", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
        # 1. BACA FILE (Header di baris ke-2, karena baris 1 kosong)
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, header=1)
        else:
            df = pd.read_excel(uploaded_file, header=1)

        # 2. BERSIH-BERSIH EKSTREM (Sapu Jagat)
        # Hapus kolom yang isinya kosong semua (Kolom A)
        df = df.dropna(axis=1, how='all')
        
        # Hapus kolom yang namanya aneh (Unnamed) jika masih nyangkut
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', na=False)]
        
        # Hapus baris yang kosong melompong
        df = df.dropna(how='all')

        # 3. AMBIL 2 KOLOM YANG TERSISA
        # Kita anggap kolom pertama adalah Dosis, kolom kedua adalah Angka
        # Apapun namanya!
        cols = df.columns.tolist()
        
        if len(cols) < 2:
            st.error("❌ Data tidak terbaca dengan benar. Pastikan Excel minimal ada 2 kolom isi.")
        else:
            col_x = cols[0] # Kolom Dosis
            col_y = cols[1] # Kolom Angka (Diversity/Tinggi)
            
            # Konversi kolom ke-2 jadi angka (Paksa)
            df[col_y] = pd.to_numeric(df[col_y], errors='coerce')
            
            # Buang data yang gagal jadi angka (misal judul nyangkut)
            df = df.dropna(subset=[col_y])

            # --- TAMPILAN ---
            c1, c2 = st.columns([1, 2])
            
            with c1:
                st.success(f"✅ Data Bersih! \n\nX: {col_x}\n\nY: {col_y}")
                
                st.write("---")
                st.write("🎛️ **Atur Posisi Titik**")
                
                # SLIDER JITTER
                jitter = st.slider("Sebaran (Jitter)", 0.0, 0.4, 0.15, step=0.01)
                
                # SEED (PENGUNCI)
                seed_val = st.number_input("Kode Kunci (Ganti angka ini biar posisi berubah)", value=42)
                
                st.info("Selama 'Kode Kunci' sama, posisi titik tidak akan berubah.")

            with c2:
                fig, ax = plt.subplots(figsize=(7, 5))
                
                # URUTKAN DOSIS (Biar 0 gy di kiri, 5 gy di kanan)
                def urutkan(teks):
                    cari = re.search(r'\d+', str(teks))
                    return int(cari.group()) if cari else 999
                
                urutan_fix = sorted(df[col_x].unique(), key=urutkan)
                
                # KUNCI POSISI AGAR DIAM
                np.random.seed(seed_val)
                
                # GAMBAR BOXPLOT
                sns.boxplot(data=df, x=col_x, y=col_y, order=urutan_fix, ax=ax, 
                            palette="Pastel1", showfliers=False)
                
                # GAMBAR TITIK
                sns.stripplot(data=df, x=col_x, y=col_y, order=urutan_fix, ax=ax, 
                              color='black', alpha=0.6, jitter=jitter, size=6)
                
                ax.grid(True, linestyle='--', alpha=0.5)
                ax.set_ylabel(col_y, fontweight='bold')
                ax.set_xlabel(col_x, fontweight='bold')
                
                st.pyplot(fig)

    except Exception as e:
        st.error(f"Masih Eror: {e}")
        st.write("Kemungkinan format file Excel Bapak sangat berbeda dari contoh.")
