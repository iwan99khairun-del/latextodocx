import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import re

st.set_page_config(page_title="Pencocok Grafik", layout="wide")
st.title("🎯 Peniru Grafik (Agar Mirip Contoh)")

# --- 1. FUNGSI BACA DATA ---
@st.cache_data
def load_data(file):
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file, header=1)
        else:
            df = pd.read_excel(file, header=1)
        
        # Bersihkan
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', na=False)]
        df = df.dropna(how='all')
        return df
    except:
        return None

# --- 2. PROGRAM UTAMA ---
uploaded_file = st.file_uploader("Upload File Excel", type=["xlsx", "csv"])

if uploaded_file:
    df = load_data(uploaded_file)
    
    if df is not None and len(df.columns) >= 2:
        col_x = df.columns[0]
        col_y = df.columns[1]
        df[col_y] = pd.to_numeric(df[col_y], errors='coerce')
        df = df.dropna(subset=[col_y])

        # Urutkan
        def urutkan(t):
            cari = re.search(r'\d+', str(t))
            return int(cari.group()) if cari else 999
        urutan = sorted(df[col_x].unique(), key=urutkan)

        # --- MENU SAMPING ---
        with st.sidebar:
            st.header("⚙️ Pengaturan")
            st.info("Klik tombol di bawah berulang kali sampai posisi titik mirip dengan contoh.")
            
            # Tombol pengacak
            if 'seed_state' not in st.session_state:
                st.session_state.seed_state = 42
            
            if st.button("🎲 ACAK ULANG POSISI TITIK"):
                st.session_state.seed_state += 1
            
            st.write(f"Kode Posisi Saat Ini: **{st.session_state.seed_state}**")
            
            st.divider()
            lebar_sebar = st.slider("Lebar Sebaran Kiri-Kanan", 0.1, 0.4, 0.20)
            ukuran_titik = st.slider("Ukuran Titik", 4, 10, 6)

        # --- AREA GAMBAR ---
        c1, c2 = st.columns([3, 1])
        
        with c1:
            fig, ax = plt.subplots(figsize=(8, 5))
            
            # KUNCI POSISI (Ini intinya)
            np.random.seed(st.session_state.seed_state)

            # 1. Boxplot (ABU-ABU seperti contoh)
            sns.boxplot(data=df, x=col_x, y=col_y, order=urutan, ax=ax, 
                        color="#D3D3D3",  # Abu-abu muda
                        linecolor="#404040", # Garis abu tua
                        showfliers=False, width=0.5)
            
            # 2. Stripplot (ORANYE seperti contoh)
            sns.stripplot(data=df, x=col_x, y=col_y, order=urutan, ax=ax, 
                          color="#FF4500", # Oranye kemerahan
                          alpha=0.8,       # Agak transparan
                          jitter=lebar_sebar, 
                          size=ukuran_titik,
                          edgecolor="black", linewidth=0.5) # Garis pinggir titik
            
            ax.set_xlabel(col_x, fontweight='bold')
            ax.set_ylabel(col_y, fontweight='bold')
            ax.grid(True, axis='y', linestyle='--', alpha=0.3)
            
            st.pyplot(fig)
            
        with c2:
            st.warning("👇 **Tips:**")
            st.write("Karena grafik contoh menggunakan metode 'Acak', tidak ada rumus pasti.")
            st.write("Silakan klik **Acak Ulang** di menu kiri beberapa kali sampai Bapak melihat pola yang 'Pas'.")

    else:
        st.error("Format data salah.")
else:
    st.info("Silakan upload file.")
