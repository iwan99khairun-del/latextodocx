import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import re
import numpy as np

# --- 1. CONFIG HALAMAN ---
st.set_page_config(page_title="Pencari Posisi Titik Pas", layout="wide")
st.title("🎯 Atur Letak Titik Sampai Pas")

# --- 2. BACA DATA ---
@st.cache_data
def load_data(file):
    try:
        # Baca file
        if file.name.endswith('.csv'):
            df_temp = pd.read_csv(file, header=None)
        else:
            df_temp = pd.read_excel(file, header=None)
        
        # Cari header
        header_idx = 0
        for i, row in df_temp.iterrows():
            txt = row.astype(str).str.lower().to_string()
            if 'dose' in txt or 'gy' in txt:
                header_idx = i
                break
        
        # Reload
        if file.name.endswith('.csv'):
            file.seek(0)
            df = pd.read_csv(file, header=header_idx)
        else:
            df = pd.read_excel(file, header=header_idx)

        # Bersih-bersih
        df = df.dropna(axis=1, how='all')
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', na=False)]
        return df
    except:
        return None

def urutan_dosis(val):
    cari = re.search(r'\d+', str(val))
    return int(cari.group()) if cari else 999

# --- 3. PROGRAM UTAMA ---
uploaded_file = st.file_uploader("Upload File Excel", type=["xlsx", "csv"])

if uploaded_file:
    df = load_data(uploaded_file)
    
    if df is not None:
        cols = df.columns.tolist()
        
        # Auto Select
        try:
            col_x = next(c for c in cols if 'dose' in c.lower() or 'gy' in c.lower())
            col_y = next(c for c in cols if 'diversity' in c.lower() or 'genetic' in c.lower())
        except:
            col_x, col_y = cols[0], cols[1] if len(cols)>1 else cols[0]

        # Layout
        c1, c2 = st.columns([1, 2])
        
        with c1:
            st.subheader("🎛️ Pengendali Posisi")
            
            x_axis = st.selectbox("Sumbu X", cols, index=cols.index(col_x))
            y_axis = st.selectbox("Sumbu Y", cols, index=cols.index(col_y))
            
            st.divider()
            
            st.write("### 🎮 CARI POSISI DI SINI:")
            
            # 1. ATUR LEBARNYA
            jitter_val = st.slider("1. Lebar Sebaran (Jitter)", 0.0, 0.4, 0.15, step=0.01)
            
            # 2. ATUR POLANYA (SEED) - INI KUNCINYA
            seed_val = st.number_input("2. Kode Pola (Ganti angka ini!)", 
                                       min_value=1, max_value=1000, value=42, step=1,
                                       help="Ganti angka ini (misal: 1, 2, 100) sampai ketemu posisi titik yang Bapak suka.")
            
            st.info("👆 **Tips:** Klik tombol (+) atau (-) pada 'Kode Pola' di atas. Perhatikan grafiknya akan berubah posisinya. Cari sampai ketemu yang pas.")
            
            st.divider()
            orientasi = st.radio("Bentuk", ["Vertikal", "Horizontal"])

        with c2:
            st.subheader("🖼️ Hasil Grafik")
            
            fig, ax = plt.subplots(figsize=(8, 6))
            
            # Data process
            df[y_axis] = pd.to_numeric(df[y_axis], errors='coerce')
            urutan = sorted(df[x_axis].unique(), key=urutan_dosis)
            
            # --- PENGUNCI POSISI ---
            # Kita kunci posisi berdasarkan angka yang Bapak masukkan
            np.random.seed(seed_val) 
            # -----------------------

            if orientasi == "Vertikal":
                sns.boxplot(data=df, x=x_axis, y=y_axis, order=urutan, ax=ax, 
                            palette="Pastel1", showfliers=False)
                sns.stripplot(data=df, x=x_axis, y=y_axis, order=urutan, ax=ax, 
                              color='black', alpha=0.6, jitter=jitter_val, size=6)
                
                ax.set_xlabel(x_axis, fontweight='bold')
                ax.set_ylabel(y_axis, fontweight='bold')
            else:
                sns.boxplot(data=df, x=y_axis, y=x_axis, order=urutan, ax=ax, 
                            palette="Pastel1", showfliers=False)
                sns.stripplot(data=df, x=y_axis, y=x_axis, order=urutan, ax=ax, 
                              color='black', alpha=0.6, jitter=jitter_val, size=6)
                
                ax.set_xlabel(y_axis, fontweight='bold')
                ax.set_ylabel(x_axis, fontweight='bold')

            ax.grid(True, linestyle='--',
