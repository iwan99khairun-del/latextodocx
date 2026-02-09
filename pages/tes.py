import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import re

st.set_page_config(page_title="Grafik Otomatis (Swarm)", layout="wide")
st.title("🌱 Grafik Sebaran Otomatis (Swarm Plot)")

# --- 1. FUNGSI BACA DATA (KHUSUS FILE BAPAK) ---
@st.cache_data
def load_data(file):
    try:
        # File Bapak header ada di baris ke-2 (index 1)
        if file.name.endswith('.csv'):
            df = pd.read_csv(file, header=1)
        else:
            df = pd.read_excel(file, header=1)
            
        # Bersihkan kolom kosong (Unnamed)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', na=False)]
        # Hapus baris kosong
        df = df.dropna(how='all')
        return df
    except:
        return None

# --- 2. PROGRAM UTAMA ---
uploaded_file = st.file_uploader("Upload File Excel/CSV", type=["xlsx", "csv"])

if uploaded_file:
    df = load_data(uploaded_file)
    
    if df is not None and len(df.columns) >= 2:
        # Ambil 2 kolom pertama
        col_x = df.columns[0] # Kategori (Dosis)
        col_y = df.columns[1] # Angka (Tinggi/Genetik)
        
        # Pastikan kolom Y jadi angka
        df[col_y] = pd.to_numeric(df[col_y], errors='coerce')
        df = df.dropna(subset=[col_y])

        # Urutkan Dosis (0, 5, 10...)
        def urutkan(t):
            cari = re.search(r'\d+', str(t))
            return int(cari.group()) if cari else 999
        
        urutan = sorted(df[col_x].unique(), key=urutkan)
        
        # --- PENGATURAN ---
        c1, c2 = st.columns([1, 3])
        
        with c1:
            st.info("ℹ️ **Mode Otomatis (Swarm)**")
            st.write("Titik-titik akan menyusun diri secara otomatis berdasarkan kepadatan data.")
            st.write("Bapak **TIDAK PERLU** mengatur sebaran manual lagi.")
            
            st.divider()
            # Hanya ukuran titik yang perlu diatur jika data terlalu banyak
            ukuran_titik = st.slider("Ukuran Titik", 3, 10, 5, help="Jika titik saling bertabrakan/hilang, kecilkan ukuran ini.")

        with c2:
            fig, ax = plt.subplots(figsize=(8, 6))
            
            # 1. BOXPLOT (Background Transparan)
            sns.boxplot(data=df, x=col_x, y=col_y, order=urutan, ax=ax, 
                        color="white", linecolor="black", showfliers=False, width=0.5)
            
            # 2. SWARMPLOT (TITIK OTOMATIS)
            # Ini kuncinya: swarmplot menyusun titik agar tidak tumpang tindih secara otomatis
            try:
                sns.swarmplot(data=df, x=col_x, y=col_y, order=urutan, ax=ax, 
                              size=ukuran_titik, palette="Set1", edgecolor="gray", linewidth=0.5)
            except Exception as e:
                st.warning("Data terlalu padat untuk ukuran titik ini. Coba kecilkan 'Ukuran Titik' di sebelah kiri.")
                # Fallback jika swarm gagal (jarang terjadi)
                sns.stripplot(data=df, x=col_x, y=col_y, order=urutan, ax=ax, color='black')

            ax.set_xlabel(col_x, fontweight='bold')
            ax.set_ylabel(col_y, fontweight='bold')
            ax.grid(True, axis='y', linestyle='--', alpha=0.3)
            
            st.pyplot(fig)
            
            st.write(f"**Total Data:** {len(df)} baris")

    else:
        st.error("Format file tidak terbaca. Pastikan ada Header di baris ke-2.")
else:
    st.info("Silakan upload file.")
