import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import re
import numpy as np

# --- 1. SETTING HALAMAN ---
st.set_page_config(page_title="Studio Grafik Stabil", layout="wide")
st.title("🌱 Grafik Box Plot (Versi Stabil & Rapi)")

# --- 2. FUNGSI BACA DATA ---
@st.cache_data
def load_data(file):
    try:
        if file.name.endswith('.csv'):
            df_temp = pd.read_csv(file, header=None)
        else:
            df_temp = pd.read_excel(file, header=None)
            
        # Cari baris judul (cari kata "dose" atau "gy")
        header_idx = 0
        for i, row in df_temp.iterrows():
            row_str = row.astype(str).str.lower().to_string()
            if 'dose' in row_str or 'gy' in row_str or 'dosis' in row_str:
                header_idx = i
                break
        
        if file.name.endswith('.csv'):
            file.seek(0)
            df = pd.read_csv(file, header=header_idx)
        else:
            df = pd.read_excel(file, header=header_idx)

        df = df.dropna(axis=1, how='all')
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', na=False)]
        return df
    except Exception:
        return None

def urutan_dosis(val):
    cari = re.search(r'\d+', str(val))
    return int(cari.group()) if cari else 999

# --- 3. MAIN PROGRAM ---
uploaded_file = st.file_uploader("Upload Data Excel", type=["xlsx", "csv"])

if uploaded_file:
    df = load_data(uploaded_file)
    
    if df is not None:
        cols = df.columns.tolist()
        
        # Auto Detect
        try:
            col_x = next(c for c in cols if 'dose' in c.lower() or 'gy' in c.lower())
            col_y = next(c for c in cols if 'diversity' in c.lower() or 'genetic' in c.lower() or 'tinggi' in c.lower())
        except:
            col_x = cols[0]
            col_y = cols[1] if len(cols) > 1 else cols[0]

        # Layout
        c1, c2 = st.columns([1, 2])
        
        with c1:
            st.subheader("⚙️ Atur Tampilan")
            x_axis = st.selectbox("Kategori (Sumbu X)", cols, index=cols.index(col_x))
            y_axis = st.selectbox("Nilai (Sumbu Y)", cols, index=cols.index(col_y))
            
            st.divider()
            
            # --- PENGATUR TITIK ---
            st.write("📍 **Posisi Titik Data**")
            tampil_titik = st.checkbox("Tampilkan Titik", value=True)
            
            # DEFAULT JITTER 0 (SUPAYA LURUS RAPI)
            jitter_amount = st.slider("Sebaran Titik (Jitter)", 0.0, 0.4, 0.0, 0.05, 
                                      help="0.0 = Lurus Rapi, 0.3 = Menyebar Acak")
            
            st.info("💡 **Tips:** Geser slider ke **Kiri (0.0)** kalau mau titiknya lurus rapi.")
            
            st.divider()
            orientasi = st.radio("Orientasi", ["Vertikal", "Horizontal"])

        with c2:
            st.subheader("🖼️ Grafik")
            
            fig, ax = plt.subplots(figsize=(8, 5))
            
            # Pastikan Y angka
            df[y_axis] = pd.to_numeric(df[y_axis], errors='coerce')
            
            # Urutkan X
            urutan = sorted(df[x_axis].unique(), key=urutan_dosis)
            
            # 1. Gambar Box
            if orientasi == "Vertikal":
                sns.boxplot(data=df, x=x_axis, y=y_axis, order=urutan, ax=ax, palette="Pastel1", showfliers=False)
                
                # 2. Gambar Titik (Strip Plot)
                if tampil_titik:
                    # Menggunakan jitter=True/False tergantung slider
                    is_jitter = True if jitter_amount > 0 else False
                    
                    # Trik agar titik STABIL (tidak goyang saat diklik)
                    # Kita pakai seed random yang sama terus
                    np.random.seed(42)
