import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

st.set_page_config(page_title="Grafik Manual Total")
st.title("🛠️ Mode Manual: Tunjuk Sendiri")

uploaded_file = st.file_uploader("Upload File Excel/CSV", type=["xlsx", "csv"])

if uploaded_file is not None:
    # --- LANGKAH 1: BACA DATA MENTAH (TAMPILKAN APA ADANYA) ---
    st.subheader("1. Cek Data Mentah")
    try:
        if uploaded_file.name.endswith('.csv'):
            df_raw = pd.read_csv(uploaded_file, header=None)
        else:
            df_raw = pd.read_excel(uploaded_file, header=None)
            
        st.write("Lihat tabel di bawah. Di baris nomor berapa tulisan **'Irradiation Doses'** berada?")
        st.write("(Biasanya di baris 0, 1, atau 2)")
        st.dataframe(df_raw.head(5))
        
        # --- LANGKAH 2: PILIH BARIS JUDUL ---
        row_header = st.number_input("Masukkan Nomor Baris Judul:", min_value=0, value=1, step=1)
        
        if st.button("✅ Pakai Baris Ini Sebagai Judul"):
            # Baca ulang dengan header yang benar
            if uploaded_file.name.endswith('.csv'):
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, header=row_header)
            else:
                df = pd.read_excel(uploaded_file, header=row_header)

            # Bersihkan kolom hantu (Unnamed)
            df = df.loc[:, ~df.columns.str.contains('^Unnamed', na=False)]
            
            # Simpan di session state biar gak hilang
            st.session_state['df_fixed'] = df
            st.success("Header berhasil diatur!")

    except Exception as e:
        st.error(f"Gagal baca file: {e}")

    # --- LANGKAH 3: PILIH KOLOM & GAMBAR ---
    if 'df_fixed' in st.session_state:
        df = st.session_state['df_fixed']
        cols = df.columns.tolist()
        
        st.divider()
        st.subheader("2. Pilih Kolom & Atur Gambar")
        
        c1, c2 = st.columns(2)
        with c1:
            col_x = st.selectbox("Pilih Kolom Dosis (Sumbu X):", cols)
        with c2:
            col_y = st.selectbox("Pilih Kolom Angka (Sumbu Y):", cols)
            
        # --- ATUR POSISI TITIK (BIAR SAMA PERSIS) ---
        st.write("---")
        st.write("🔐 **Kunci Posisi Titik**")
        col_kunci, col_geser = st.columns(2)
        with col_kunci:
            seed_val = st.number_input("Kode Kunci (Ganti angka ini biar posisi berubah)", value=42)
        with col_geser:
            jitter_val = st.slider("Lebar Sebaran Titik", 0.0, 0.4, 0.15)
            
        # PROSES GAMBAR
        if col_x and col_y:
            try:
                fig, ax = plt.subplots(figsize=(8, 6))
                
                # Paksa jadi angka
                df[col_y] = pd.to_numeric(df[col_y], errors='coerce')
                
                # Urutkan Dosis
                import re
                def cari_angka(t):
                    res = re.search(r'\d+', str(t))
                    return int(res.group()) if res else 999
                
                urutan = sorted(df[col_x].unique(), key=cari_angka)
                
                # KUNCI POSISI (SUPAYA TIDAK GOYANG/BEDA)
                np.random.seed(seed_val)
                
                # 1. Gambar Boxplot
                sns.boxplot(data=df, x=col_x, y=col_y, order=urutan, ax=ax, palette="Pastel1", showfliers=False)
                
                # 2. Gambar Titik (Strip Plot Terkunci)
                sns.stripplot(data=df, x=col_x, y=col_y, order=urutan, ax=ax, 
                              color='black', alpha=0.6, jitter=jitter_val, size=6)
                
                ax.set_xlabel(col_x, fontweight='bold')
                ax.set_ylabel(col_y, fontweight='bold')
                ax.grid(True, linestyle='--', alpha=0.5)
                
                st.pyplot(fig)
                
            except Exception as e:
                st.error(f"Masih error saat menggambar: {e}")
                st.write("Pastikan kolom Angka isinya benar-benar angka.")
