import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import numpy as np
import re

st.set_page_config(page_title="Grafik Copy-Paste", layout="wide")
st.title("✂️ Grafik Cara Copy-Paste (Pasti Berhasil)")

# --- AREA TEMPEL DATA ---
st.write("### Langkah 1: Copy Data dari Excel, Paste di Sini")
st.caption("Caranya: Blok data di Excel (termasuk Judul) -> Copy -> Paste di kotak bawah.")

paste_data = st.text_area("Paste Data di sini:", height=200, 
                          placeholder="Contoh:\nIrradiation Doses\tDiversity_Genetic\n0 gy\t43\n5 gy\t45\n...")

if paste_data:
    try:
        # 1. BACA DATA DARI TEKS
        # Kita pakai separator tab (\t) karena copy dari excel biasanya tab
        df = pd.read_csv(io.StringIO(paste_data), sep='\t')
        
        # Coba deteksi jika separatornya koma (kalau dari CSV)
        if len(df.columns) < 2:
             df = pd.read_csv(io.StringIO(paste_data), sep=',')

        # 2. BERSIHKAN DATA
        df = df.dropna() # Hapus baris kosong
        
        if len(df.columns) < 2:
            st.error("❌ Data tidak terbaca. Pastikan Anda meng-copy minimal 2 kolom (Dosis & Angka).")
        else:
            # Ambil 2 kolom pertama
            col_x = df.columns[0]
            col_y = df.columns[1]
            
            # Ubah kolom ke-2 jadi angka (Penting!)
            df[col_y] = pd.to_numeric(df[col_y], errors='coerce')
            df = df.dropna() # Buang yang bukan angka

            # --- PENGATURAN GRAFIK ---
            st.write("---")
            c1, c2 = st.columns([1, 2])
            
            with c1:
                st.success(f"✅ Data Masuk! ({len(df)} baris)")
                st.write(f"Sumbu X: **{col_x}**")
                st.write(f"Sumbu Y: **{col_y}**")
                
                st.divider()
                st.write("🎯 **Cari Posisi Titik**")
                # SLIDER & SEED
                jitter = st.slider("Sebaran", 0.0, 0.4, 0.15)
                seed_val = st.number_input("Nomor Pola (Ganti angka ini!)", value=42, step=1, 
                                          help="Ganti angka ini sampai titiknya pas.")
                
                size_dot = st.slider("Ukuran Titik", 3, 10, 6)

            with c2:
                fig, ax = plt.subplots(figsize=(7, 5))
                
                # Urutkan
                def urut(x):
                    res = re.search(r'\d+', str(x))
                    return int(res.group()) if res else 999
                urutan = sorted(df[col_x].unique(), key=urut)
                
                # KUNCI BIAR GAK GOYANG
                np.random.seed(seed_val)
                
                # GAMBAR
                sns.boxplot(data=df, x=col_x, y=col_y, order=urutan, ax=ax, 
                            palette="Pastel1", showfliers=False)
                
                sns.stripplot(data=df, x=col_x, y=col_y, order=urutan, ax=ax, 
                              color='black', alpha=0.6, jitter=jitter, size=size_dot)
                
                ax.grid(True, linestyle='--', alpha=0.5)
                st.pyplot(fig)

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
        st.write("Pastikan data yang di-paste rapi.")
else:
    st.info("👆 Menunggu data di-paste...")
