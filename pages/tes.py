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
            df
