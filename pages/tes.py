import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.title("🛠️ Perbaikan Khusus (Hardcode)")

uploaded_file = st.file_uploader("Upload File CSV Bapak", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        # 1. BACA FILE (Khusus struktur file Bapak: Baris 1 kosong, Baris 2 Judul)
        if uploaded_file.name.endswith('.csv'):
            # header=1 artinya baris ke-2 dijadikan judul (karena baris 1 kosong)
            df = pd.read_csv(uploaded_file, header=1)
        else:
            df = pd.read_excel(uploaded_file, header=1)

        # 2. BERSIHKAN DATA (Hapus kolom 'Unnamed' yang muncul karena koma di depan)
        # Kita ambil kolom yang namanya jelas saja
        cols_to_use = [c for c in df.columns if "Unnamed" not in str(c)]
        df = df[cols_to_use]

        # 3. CEK DATA DI LAYAR (Supaya Bapak tahu apa yang dibaca komputer)
        st.write("### 1. Data yang terbaca:")
        st.dataframe(df.head())

        # 4. AMBIL 2 KOLOM PERTAMA SECARA PAKSA
        # (Tidak peduli namanya apa, pokoknya kolom 1 = Kategori, Kolom 2 = Angka)
        col_kategori = df.columns[0]
        col_nilai = df.columns[1]

        st.write(f"Sumbu X: **{col_kategori}** | Sumbu Y: **{col_nilai}**")

        # 5. CONVERT KE ANGKA (PENTING!)
        df[col_nilai] = pd.to_numeric(df[col_nilai], errors='coerce')
        df = df.dropna() # Hapus data yang gagal jadi angka

        # 6. GAMBAR GRAFIK SEDERHANA
        st.write("### 2. Hasil Grafik:")
        fig, ax = plt.subplots(figsize=(8, 5))
        
        # Urutan manual supaya rapi (0, 5, 10, 15, 20)
        # Kita cek dulu apakah ada angka-angka ini di data
        urutan_manual = ['0 gy', '5 gy', '10 gy', '15 gy', '20 gy']
        # Hanya pakai urutan yang benar-benar ada di data Bapak
        urutan_final = [u for u in urutan_manual if u in df[col_kategori].unique()]
        
        if not urutan_final: 
            urutan_final = None # Kalau nama beda (misal "0 Gy"), biarkan otomatis

        # Plot
        sns.boxplot(data=df, x=col_kategori, y=col_nilai, order=urutan_final, ax=ax, palette="Set2")
        sns.stripplot(data=df, x=col_kategori, y=col_nilai, order=urutan_final, ax=ax, color='black', alpha=0.5)
        
        st.pyplot(fig)

    except Exception as e:
        st.error("MASIH EROR PAK.")
        st.error(f"Pesan Error Komputer: {e}")
        st.write("Tolong fotokan pesan merah di atas ini kirim ke saya.")
