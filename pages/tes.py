import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

st.title("🛠️ Grafik Tanaman (Mode Perbaikan)")

uploaded_file = st.file_uploader("Upload File Excel", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
        # --- 1. BACA FILE (HARDCODE KHUSUS FILE BAPAK) ---
        # Kita lewati baris pertama (header=1 artinya baris ke-2 jadi judul)
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, header=1)
        else:
            df = pd.read_excel(uploaded_file, header=1)

        # --- 2. BERSIHKAN KOLOM KOSONG ---
        # Hapus kolom yang namanya "Unnamed" (kolom kosong di depan)
        cols_bersih = [c for c in df.columns if "Unnamed" not in str(c)]
        df = df[cols_bersih]
        
        # Hapus baris yang kosong semua
        df = df.dropna(how='all')

        # --- 3. AMBIL 2 KOLOM PERTAMA (PAKSA) ---
        # Kita tidak peduli namanya apa, pokoknya ambil kolom 1 dan 2
        if len(df.columns) >= 2:
            col_dosis = df.columns[0] # Kolom Dosis
            col_nilai = df.columns[1] # Kolom Angka
        else:
            st.error("Gagal: Kolom data kurang dari 2.")
            st.stop()

        # --- 4. PASTIKAN ANGKA ---
        df[col_nilai] = pd.to_numeric(df[col_nilai], errors='coerce')
        
        # --- 5. TAMPILKAN DATA (Untuk Pengecekan) ---
        st.write("✅ **Data Terbaca:**")
        st.write(f"Kolom Dosis: **{col_dosis}** | Kolom Nilai: **{col_nilai}**")
        st.dataframe(df.head())

        # --- 6. ATUR POSISI TITIK (BIAR GAK GOYANG) ---
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Atur Titik")
            # Slider Jitter
            geser = st.slider("Geser Titik (Jitter)", 0.0, 0.3, 0.15)
            # Kunci Posisi (Seed)
            kunci = st.number_input("Kode Kunci Posisi (Seed)", value=42, step=1)
            st.caption("Ubah angka '42' jika ingin posisi titik yang lain.")

        with col2:
            st.subheader("Grafik")
            fig, ax = plt.subplots(figsize=(6, 5))
            
            # URUTKAN DOSIS (0, 5, 10...)
            # Kita cari angka di dalam teks dosis untuk pengurutan
            def cari_angka(teks):
                import re
                ketemu = re.search(r'\d+', str(teks))
                return int(ketemu.group()) if ketemu else 999
            
            urutan = sorted(df[col_dosis].
