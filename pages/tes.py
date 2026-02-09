import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import io

st.set_page_config(page_title="Replika R - Mode Kontrol Penuh", layout="centered")
st.title("📊 Replika R (Kontrol Penuh)")

# --- 1. UPLOAD FILE ---
uploaded_file = st.file_uploader("Upload File Excel", type=["xlsx", "csv"])

if uploaded_file:
    try:
        # --- LANGKAH 1: CEK DATA MENTAH DULU ---
        st.subheader("1. Cek Data Mentah Anda")
        st.info("Lihat tabel di bawah. Baris nomor berapa yang berisi Judul (Header)?")
        
        # Baca tanpa header dulu buat ngintip
        if uploaded_file.name.endswith('.csv'):
            df_preview = pd.read_csv(uploaded_file, header=None, nrows=10)
        else:
            try:
                df_preview = pd.read_excel(uploaded_file, header=None, nrows=10)
            except:
                df_preview = pd.read_excel(uploaded_file, sheet_name=0, header=None, nrows=10)
        
        # Tampilkan data mentah
        st.dataframe(df_preview)

        # Input Baris Header
        header_row = st.number_input(
            "Masukkan Nomor Baris Judul (Lihat index di kiri tabel, mulai dari 0)", 
            value=1, 
            min_value=0, 
            step=1,
            help="Contoh: Kalau judul 'Irradiation Doses' ada di baris ke-2, tulis 1 (karena hitungan mulai dari 0)."
        )

        if st.button("Proses Data"):
            st.session_state['header_fixed'] = True
            st.session_state['row_idx'] = header_row

        # --- LANGKAH 2: BACA DATA SESUAI HEADER PILIHAN ---
        # Kita pakai trik 'session_state' biar gak reload terus
        idx_to_use = st.session_state.get('row_idx', header_row)
        
        # Baca ulang file dengan header yang benar
        uploaded_file.seek(0) # Reset pembacaan file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, header=idx_to_use)
        else:
            try:
                df = pd.read_excel(uploaded_file, sheet_name="Sheet2", header=idx_to_use)
            except:
                df = pd.read_excel(uploaded_file, header=idx_to_use)

        # Bersihkan nama kolom
        df.columns = df.columns.astype(str).str.strip()
        # Hapus kolom aneh
        cols = [c for c in df.columns if "Unnamed" not in c and c != "nan"]
        df = df[cols]

        st.success("✅ Data Berhasil Dibaca!")
        
        # --- LANGKAH 3: PILIH KOLOM ---
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            pilihan_x = st.selectbox("Pilih Kolom Kategori (Dosis)", df.columns)
        with col2:
            pilihan_y = st.selectbox("Pilih Kolom Angka (Nilai)", df.columns, index=1 if len(df.columns) > 1 else 0)

        # PROSES FINAL
        if pilihan_x and pilihan_y:
            # Pastikan kolom Angka isinya benar-benar ANGKA
            df[pilihan_y] = pd.to_numeric(df[pilihan_y], errors='coerce')
            df_clean = df.dropna(subset=[pilihan_x, pilihan_y]).copy()

            if df_clean.empty:
                st.error("Data kosong setelah dibersihkan. Cek apakah kolom yang dipilih isinya angka.")
                st.stop()

            #
