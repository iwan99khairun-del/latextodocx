import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io

# --- 1. CONFIG ---
st.set_page_config(page_title="Grafik Simpel", layout="wide")
st.title("📦 Box Plot Manual (Anti-Eror)")

# --- 2. FUNGSI BACA DATA (Sangat Sederhana) ---
def load_data_simple(file):
    try:
        # Baca file tanpa header dulu
        if file.name.endswith('.csv'):
            df = pd.read_csv(file, header=None)
        else:
            df = pd.read_excel(file, header=None)
        return df
    except Exception as e:
        st.error(f"Gagal baca file: {e}")
        return None

# --- 3. PROGRAM UTAMA ---
uploaded_file = st.file_uploader("Upload File Excel/CSV", type=["xlsx", "csv"])

if uploaded_file is not None:
    # 1. Tampilkan Data Mentah Dulu (Supaya Bapak bisa lihat isinya)
    df_raw = load_data_simple(uploaded_file)
    
    if df_raw is not None:
        st.subheader("1. Cek Data Mentah Anda")
        st.write("Lihat tabel di bawah. Baris nomor berapa yang berisi Judul (Header)?")
        st.dataframe(df_raw.head(5))
        
        # 2. Minta Bapak Tentukan Baris Judul
        header_row = st.number_input("Masukkan Nomor Baris Judul (Lihat index di kiri tabel, mulai dari 0)", 
                                     min_value=0, value=1, step=1)
        
        if st.button("Proses Data"):
            try:
                # Reload data dengan header yang benar pilihan Bapak
                if uploaded_file.name.endswith('.csv'):
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, header=header_row)
                else:
                    df = pd.read_excel(uploaded_file, header=header_row)
                
                # Buang kolom kosong/Unnamed
                df = df.loc[:, ~df.columns.str.contains('^Unnamed', na=False)]
                
                # --- MENU PILIH KOLOM ---
                cols = df.columns.tolist()
                c1, c2 = st.columns([1, 2])
                
                with c1:
                    st.success("✅ Data Berhasil Dibaca!")
                    x_axis = st.selectbox("Pilih Kolom Kategori (Dosis)", cols)
                    y_axis = st.selectbox("Pilih Kolom Angka (Nilai)", cols)
                    
                    st.write("---")
                    st.write("Pastikan kolom Nilai berisi ANGKA.")
                    
                with c2:
                    # --- GAMBAR GRAFIK ---
                    fig, ax = plt.subplots(figsize=(8, 6))
                    
                    # Paksa jadi angka (biar gak error)
                    df[y_axis] = pd.to_numeric(df[y_axis], errors='coerce')
                    
                    # Plot Sederhana
                    sns.boxplot(data=df, x=x_axis, y=y_axis, ax=ax, palette="Set2")
                    sns.stripplot(data=df, x=x_axis, y=y_axis, ax=ax, color='black', alpha=0.5)
                    
                    ax.set_title(f"{x_axis} vs {y_axis}")
                    st.pyplot(fig)
                    
            except Exception as e:
                st.error(f"TERJADI ERROR: {e}")
                st.write("Coba ganti nomor baris judul di atas.")
else:
    st.info("Upload file dulu ya Pak.")
