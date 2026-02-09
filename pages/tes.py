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
            df[col_x] = pd.Categorical(df[col_x], categories
