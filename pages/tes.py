import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import re

st.set_page_config(page_title="Pencari Posisi Titik", layout="wide")
st.title("🎯 Alat Pencari Posisi Titik (Agar Sama Persis)")

# --- 1. BACA DATA (KHUSUS FILE BAPAK) ---
@st.cache_data
def load_data(file):
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file, header=1) # Lewati baris 1 kosong
        else:
            df = pd.read_excel(file, header=1) # Lewati baris 1 kosong
            
        # Hapus kolom kosong (Unnamed)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', na=False)]
        df = df.dropna(how='all') # Hapus baris kosong
        return df
    except:
        return None

# --- 2. PROGRAM UTAMA ---
uploaded_file = st.file_uploader("Upload File Excel", type=["xlsx", "csv"])

if uploaded_file:
    df = load_data(uploaded_file)
    
    if df is not None and len(df.columns) >= 2:
        # Ambil 2 kolom pertama
        col_x = df.columns[0] # Dosis
        col_y = df.columns[1] # Nilai
        
        # Pastikan kolom nilai jadi angka
        df[col_y] = pd.to_numeric(df[col_y], errors='coerce')

        # --- PANEL PENGATUR (SIDEBAR) ---
        with st.sidebar:
            st.header("🎛️ KENDALI TITIK")
            st.write("Ubah angka di bawah ini sampai posisi titik **SAMA** dengan contoh Bapak.")
            
            # 1. NOMOR GAYA (SEED) - INI KUNCINYA
            seed_key = st.number_input("1. NOMOR GAYA (Ganti-ganti angka ini!)", 
                                       value=42, step=1, 
                                       help="Setiap angka menghasilkan posisi titik yang berbeda.")
            
            # 2. LEBAR SEBARAN
            width_val = st.slider("2. Lebar Sebaran", 0.05, 0.40, 0.15, step=0.01)
            
            # 3. UKURAN TITIK
            size_val = st.slider("3. Besar Titik", 3, 10, 6)
            
            st.warning("Tips: Klik tanda (+) atau (-) pada 'Nomor Gaya' perlahan-lahan sambil melihat gambar.")

        # --- AREA GAMBAR ---
        col_main, _ = st.columns([3, 1])
        with col_main:
            fig, ax = plt.subplots(figsize=(8, 6))
            
            # Urutan Dosis
            def urutkan(t):
                cari = re.search(r'\d+', str(t))
                return int(cari.group()) if cari else 999
            urutan = sorted(df[col_x].unique(), key=urutkan)
            
            # --- BAGIAN AJAIB (PENGUNCI) ---
            # Apapun angkanya, kuncinya dipasang di sini
            np.random.seed(seed_key) 
            # -------------------------------

            # Gambar Boxplot
            sns.boxplot(data=df, x=col_x, y=
