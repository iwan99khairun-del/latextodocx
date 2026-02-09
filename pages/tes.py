import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import re
import numpy as np

# --- 1. SETTING HALAMAN ---
st.set_page_config(page_title="Aplikasi Grafik Aman", layout="wide")
st.title("🌱 Grafik Box Plot + Titik Data (Versi Stabil)")

# --- 2. FUNGSI BACA DATA (SUPER AMAN) ---
@st.cache_data
def load_data(file):
    try:
        # 1. Baca mentah (tanpa header dulu)
        if file.name.endswith('.csv'):
            df_temp = pd.read_csv(file, header=None)
        else:
            df_temp = pd.read_excel(file, header=None)
            
        # 2. Cari baris yang mengandung kata "dose", "gy", atau "dosis"
        header_idx = -1
        for i, row in df_temp.iterrows():
            row_text = row.astype(str).str.lower().to_string()
            if 'dose' in row_text or 'gy' in row_text or 'dosis' in row_text:
                header_idx = i
                break
        
        # 3. Kalau tidak ketemu, pakai baris ke-1 (indeks 1) karena baris 0 biasanya kosong
        if header_idx == -1:
            header_idx = 1
        
        # 4. Baca ulang dengan header yang benar
        if file.name.endswith('.csv'):
            file.seek(0)
            df = pd.read_csv(file, header=header_idx)
        else:
            df = pd.read_excel(file, header=header_idx)

        # 5. Bersihkan kolom aneh (Unnamed)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', na=False)]
        
        # 6. Hapus baris yang isinya kosong melompong
        df = df.dropna(how='all')
        
        return df
    except Exception as e:
        return None

# Fungsi pengurut (0, 5, 10...)
def urutan_dosis(val):
    cari = re.search(r'\d+', str(val))
    return int(cari.group()) if cari else 999

# --- 3. TAMPILAN UTAMA ---
uploaded_file = st.file_uploader("Upload Data Excel", type=["xlsx", "csv"])

if uploaded_file:
    df = load_data(uploaded_file)
    
    if df is not None:
        cols = df.columns.tolist()
        
        # Coba tebak kolom otomatis
        try:
            col_x = next(c for c in cols if 'dose' in c.lower() or 'gy' in c.lower())
            col_y = next(c for c in cols if 'diversity' in c.lower() or 'genetic' in c.lower())
        except:
            if len(cols) >= 2:
                col_x, col_y = cols[0], cols[1]
            else:
                col_x, col_y = cols[0], cols[0]

        # --- LAYOUT KIRI KANAN ---
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("⚙️ Pengaturan")
            x_axis = st.selectbox("Sumbu X (Kategori)", cols, index=cols.index(col_x) if col_x in cols else 0)
            y_axis = st.selectbox("Sumbu Y (Nilai)", cols, index=cols.index(col_y) if col_y in cols else 0)
            
            st.divider()
            
            st.write(" **Atur Titik-Titik (Dots):**")
            pake_titik = st.checkbox("Tampilkan Titik", value=True)
            
            # SLIDER JITTER (SOLUSI SUPAYA RAPI)
            sebaran = st.slider("Kerapian
