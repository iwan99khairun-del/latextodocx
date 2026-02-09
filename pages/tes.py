import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import re

# --- SETTING HALAMAN ---
st.set_page_config(page_title="Grafik Rapi Final", layout="wide")
st.title("🌱 Grafik Boxplot + Swarm (Rapi & Tetap)")

# --- FUNGSI BACA DATA SPESIFIK FILE BAPAK ---
def load_data_special(file):
    try:
        # 1. Baca dengan header di baris ke-2 (Index 1) karena baris 1 kosong
        if file.name.endswith('.csv'):
            df = pd.read_csv(file, header=1)
        else:
            df = pd.read_excel(file, header=1)
            
        # 2. HAPUS KOLOM KOSONG (KOLOM A)
        # Cari kolom yang namanya ada isinya (bukan Unnamed)
        cols_valid = [c for c in df.columns if "Unnamed" not in str(c)]
        df = df[cols_valid]
        
        # 3. Hapus baris kosong
        df = df.dropna()
        
        return df
    except Exception as e:
        return None

# Fungsi urutkan dosis (0, 5, 10...)
def sort_doses(val):
    search = re.search(r'\d+', str(val))
    return int(search.group()) if search else 999

# --- PROGRAM UTAMA ---
uploaded_file = st.file_uploader("Upload File Excel Bapak", type=["xlsx", "csv"])

if uploaded_file:
    df = load_data_special(uploaded_file)
    
    if df is not None and len(df.columns) >= 2:
        # Ambil 2 kolom pertama yang tersisa (Pasti Dosis & Angka)
        col_x = df.columns[0] # Irradiation Doses
        col_y = df.columns[1] # Diversity_Genetic
        
        # Pastikan kolom ke-2 adalah angka
        df[col_y] = pd.to_numeric(df[col_y], errors='coerce')
        
        # Urutkan Dosis (Biar 0 di kiri, 20 di kanan)
        urutan = sorted(df[col_x].unique(), key=sort_doses)
        
        # --- PENGATURAN TAMPILAN ---
        c1, c2 = st.columns([1, 3])
        
        with c1:
            st.success("✅ Data Bersih!")
            st.write(f"**X:** {col_x}")
            st.write(f"**Y:** {col_y}")
            
            st.divider()
            point_size = st.slider("Ukuran Titik", 3, 10, 6)
            st.info("Mode: **Swarm Plot**\n(Titik otomatis diatur rapi dan tidak akan berubah posisi/acak).")

        with c2:
            # --- GAMBAR GRAFIK ---
            fig, ax = plt.subplots(figsize=(8, 6))
            
            # 1. Boxplot (Kotak) - Warna Putih/Transparan biar bersih
            sns.boxplot(data=df, x=col_x, y=col_y, order=urutan, ax=ax, 
                        color="white",  # Kotak putih
                        linecolor="black", # Garis hitam
                        showfliers=False, # Hapus outlier (karena sudah ada titik)
                        width=0.5)
            
            # 2. Swarmplot (Titik Rapi)
            # Ini kuncinya: Swarmplot menyusun titik agar tidak tumpang tindih
            # Tanpa perlu random/acak, jadi posisinya PASTI TETAP.
            sns.swarmplot(data=df, x=col_x, y=col_y, order=urutan, ax=ax, 
                          size=point_size, palette="Set1", edgecolor="gray", linewidth=0.5)
            
            # Perbagus Tampilan
            ax.set_xlabel(col_x, fontweight='bold', fontsize=11)
            ax.set_ylabel(col_y, fontweight='bold', fontsize=11)
            ax.grid(True, axis='y', linestyle='--', alpha=0.3)
            ax.set_title(f"Distribusi {col_y} per {col_x}", fontsize=14)
            
            st.pyplot(fig)
            
            # Download
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=300, bbox_inches='tight')
            buf.seek(0)
            st.download_button("⬇️ Download Gambar Rapi (High Res)", buf, "grafik_rapi.png", "image/png")
            
    else:
        st.error("Format file tidak sesuai. Pastikan ada Header di baris ke-2.")
else:
    st.info("Silakan upload file.")
