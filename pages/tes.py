import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import re

# --- 1. SETTING HALAMAN ---
st.set_page_config(page_title="Analisis Tanaman Final", layout="wide")
st.title("🌱 Grafik Box Plot + Sebaran Data (Dots)")

# --- 2. FUNGSI BACA DATA KHUSUS (SUPERSMART) ---
@st.cache_data
def load_data(file):
    try:
        # Baca file mentah
        if file.name.endswith('.csv'):
            df_temp = pd.read_csv(file, header=None)
        else:
            df_temp = pd.read_excel(file, header=None)
            
        # Cari baris judul yang benar (cari kata "Dose" atau "gy")
        header_idx = 0
        for i, row in df_temp.iterrows():
            row_str = row.astype(str).str.lower().to_string()
            if 'dose' in row_str or 'gy' in row_str or 'dosis' in row_str:
                header_idx = i
                break
        
        # Reload dengan header yang tepat
        if file.name.endswith('.csv'):
            file.seek(0)
            df = pd.read_csv(file, header=header_idx)
        else:
            df = pd.read_excel(file, header=header_idx)

        # Bersihkan data
        df = df.dropna(axis=1, how='all') # Buang kolom kosong
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', na=False)] # Buang kolom Unnamed
        
        return df
    except Exception as e:
        return None

# Fungsi pengurut dosis (supaya 5 gy tidak lompat ke belakang)
def urutan_dosis(val):
    cari_angka = re.search(r'\d+', str(val))
    return int(cari_angka.group()) if cari_angka else 999

# --- 3. MAIN PROGRAM ---
uploaded_file = st.file_uploader("Upload Data Excel", type=["xlsx", "csv"])

if uploaded_file:
    df = load_data(uploaded_file)
    
    if df is not None:
        cols = df.columns.tolist()
        
        # --- PRESET OTOMATIS UNTUK DATA BAPAK ---
        # Mencari kolom dosis dan nilai secara otomatis
        try:
            col_kategori = next(c for c in cols if 'dose' in c.lower() or 'gy' in c.lower())
            col_nilai = next(c for c in cols if 'diversity' in c.lower() or 'genetic' in c.lower() or 'tinggi' in c.lower())
        except:
            col_kategori = cols[0]
            col_nilai = cols[1] if len(cols) > 1 else cols[0]

        # --- LAYOUT ---
        col_kiri, col_kanan = st.columns([1, 2])
        
        with col_kiri:
            st.subheader("⚙️ Pengaturan")
            x_axis = st.selectbox("Sumbu X (Grup)", cols, index=cols.index(col_kategori))
            y_axis = st.selectbox("Sumbu Y (Nilai)", cols, index=cols.index(col_nilai))
            
            st.divider()
            st.write(" **Tampilan Titik (Dots):**")
            pake_dots = st.checkbox("Tampilkan Dots", value=True)
            jitter_val = st.slider("Sebaran Titik (Jitter)", 0.0, 0.4, 0.1, 0.05)
            
            st.divider()
            orientasi = st.radio("Orientasi", ["Vertikal", "Horizontal"])
            
            # URUTKAN DATA (SORTING)
            # Ambil data unik dan urutkan berdasarkan angkanya
            kategori_unik = df[x_axis].unique()
            urutan_fix = sorted(kategori_unik, key=urutan_dosis)

        with col_kanan:
            st.subheader("🖼️ Hasil Grafik")
            
            # Setup Canvas
            fig, ax = plt.subplots(figsize=(8, 5))
            
            # Pastikan data nilai jadi angka
            df[y_axis] = pd.to_numeric(df[y_axis], errors='coerce')
            
            # PLOTTING
            if orientasi == "Vertikal":
                # 1. Gambar Kotak (Boxplot)
                sns.boxplot(data=df, x=x_axis, y=y_axis, order=urutan_fix, ax=ax, 
                            palette="Pastel1", showfliers=False, width=0.5)
                # 2. Gambar Titik (Stripplot)
                if pake_dots:
                    sns.stripplot(data=df, x=x_axis, y=y_axis, order=urutan_fix, ax=ax, 
                                  color='black', alpha=0.6, jitter=jitter_val, size=5)
                
                ax.set_xlabel(x_axis, fontweight='bold')
                ax.set_ylabel(y_axis, fontweight='bold')
            
            else: #
