import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import re
import numpy as np # Kita butuh ini untuk mengunci posisi

# --- 1. SETTING HALAMAN ---
st.set_page_config(page_title="Grafik Posisi Tetap", layout="wide")
st.title("🌱 Grafik Box Plot (Posisi Titik Terkunci/Tetap)")

# --- 2. FUNGSI BACA DATA (ROBUST) ---
@st.cache_data
def load_data(file):
    try:
        # Baca tanpa header
        if file.name.endswith('.csv'):
            df_temp = pd.read_csv(file, header=None)
        else:
            df_temp = pd.read_excel(file, header=None)
            
        # Cari baris judul (dose/gy)
        header_idx = 0
        for i, row in df_temp.iterrows():
            txt = row.astype(str).str.lower().to_string()
            if 'dose' in txt or 'gy' in txt:
                header_idx = i
                break
        
        # Baca ulang
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
uploaded_file = st.file_uploader("Upload File Excel Bapak", type=["xlsx", "csv"])

if uploaded_file:
    df = load_data(uploaded_file)
    
    if df is not None:
        cols = df.columns.tolist()
        
        # Auto Pilih Kolom
        try:
            col_x = next(c for c in cols if 'dose' in c.lower() or 'gy' in c.lower())
            col_y = next(c for c in cols if 'diversity' in c.lower() or 'genetic' in c.lower())
        except:
            col_x, col_y = cols[0], cols[1] if len(cols)>1 else cols[0]

        # Layout
        c1, c2 = st.columns([1, 2])
        
        with c1:
            st.subheader("⚙️ Kunci Posisi")
            
            x_axis = st.selectbox("Sumbu X", cols, index=cols.index(col_x))
            y_axis = st.selectbox("Sumbu Y", cols, index=cols.index(col_y))
            
            st.divider()
            
            # FITUR UTAMA: SEBARAN
            st.write("📍 **Atur Kerapian Titik**")
            jitter_val = st.slider("Lebar Sebaran", 0.0, 0.3, 0.15, 0.01)
            
            st.info("ℹ️ **INFO:** Kode ini menggunakan 'Pengunci' (Seed 42). Posisi titik TIDAK akan berubah-ubah lagi walau direfresh.")
            
            st.divider()
            orientasi = st.radio("Bentuk", ["Vertikal", "Horizontal"])

        with c2:
            st.subheader("🖼️ Hasil Final")
            
            fig, ax = plt.subplots(figsize=(8, 6))
            
            # Data Processing
            df[y_axis] = pd.to_numeric(df[y_axis], errors='coerce')
            urutan = sorted(df[x_axis].unique(), key=urutan_dosis)
            
            # --- BAGIAN PENTING: PENGUNCI (LOCK) ---
            # Kita set seed numpy supaya acakannya SELALU SAMA
            np.random.seed(42) 
            # ---------------------------------------

            if orientasi == "Vertikal":
                # Boxplot
                sns.boxplot(data=df, x=x_axis, y=y_axis, order=urutan, ax=ax, 
                            palette="Pastel1", showfliers=False)
                # Stripplot (Titik)
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

            ax.grid(True, linestyle='--', alpha=0.5)
            st.pyplot(fig)
            
            # Download
            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches='tight', dpi=300)
            buf.seek(0)
            st.download_button("⬇️ Download Gambar Stabil", buf, "grafik_stabil.png", "image/png")
else:
    st.info("Silakan upload file.")
