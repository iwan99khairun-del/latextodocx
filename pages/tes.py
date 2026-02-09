import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

st.set_page_config(page_title="Grafik Manual Pasti Bisa")
st.title("🛠️ Grafik Manual (Pilih Kolom Sendiri)")

uploaded_file = st.file_uploader("Upload File Excel/CSV", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
        # --- 1. BACA FILE (Coba baca header di baris ke-2) ---
        # Karena file Bapak baris 1-nya kosong
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, header=1)
        else:
            df = pd.read_excel(uploaded_file, header=1)

        # --- 2. BERSIHKAN KOLOM 'UNNAMED' (Kolom Kosong) ---
        # Hapus kolom yang namanya aneh/kosong
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', na=False)]
        
        # Hapus baris kosong
        df = df.dropna(how='all')
        
        # Tampilkan data supaya Bapak yakin
        st.write("✅ **Data Berhasil Dibaca:**")
        st.dataframe(df.head(3))

        # --- 3. BAPAK PILIH SENDIRI KOLOMNYA ---
        st.subheader("👇 Pilih Kolom di Sini:")
        cols = df.columns.tolist()
        
        c1, c2 = st.columns(2)
        with c1:
            col_x = st.selectbox("Pilih Kolom Dosis (Kategori):", cols)
        with c2:
            col_y = st.selectbox("Pilih Kolom Angka (Tinggi/Genetik):", cols)

        # --- 4. GAMBAR GRAFIK ---
        if col_x and col_y:
            # Pastikan Y adalah Angka
            df[col_y] = pd.to_numeric(df[col_y], errors='coerce')
            
            # Pengaturan Tampilan
            st.write("---")
            col_opt1, col_opt2 = st.columns(2)
            with col_opt1:
                tampil_titik = st.checkbox("Tampilkan Titik-Titik", value=True)
            with col_opt2:
                # KUNCI POSISI (Supaya tidak goyang)
                kunci_posisi = st.number_input("Kunci Posisi (Seed) - Ganti angka ini biar pola berubah", value=42)

            fig, ax = plt.subplots(figsize=(8, 6))
            
            # Urutkan Dosis secara alami (0, 5, 10...)
            # Supaya urutannya tidak berantakan
            try:
                urutan = sorted(df[col_x].unique(), key=lambda x: int(''.join(filter(str.isdigit, str(x)))) if any(c.isdigit() for c in str(x)) else x)
            except:
                urutan = None # Kalau gagal urutkan, pakai default

            # KUNCI RANDOM AGAR POSISI TETAP
            np.random.seed(kunci_posisi)

            # GAMBAR
            sns.boxplot(data=df, x=col_x, y=col_y, order=urutan, ax=ax, palette="Pastel1", showfliers=False)
            
            if tampil_titik:
                sns.stripplot(data=df, x=col_x, y=col_y, order=urutan, ax=ax, 
                              color='black', alpha=0.6, jitter=0.15, size=6)

            ax.set_xlabel(col_x, fontweight='bold')
            ax.set_ylabel(col_y, fontweight='bold')
            ax.grid(True, linestyle='--', alpha=0.5)
            
            st.pyplot(fig)

    except Exception as e:
        st.error("MASIH EROR.")
        st.error(f"Pesan: {e}")
        st.info("Tips: Coba buka Excel Bapak, Hapus Baris 1 (yang kosong), Save, lalu Upload lagi.")
