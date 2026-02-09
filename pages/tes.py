import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io

# --- 1. Konfigurasi Halaman ---
st.set_page_config(page_title="Studio Grafik Tanaman", layout="wide")
st.title("🌱 Analisis Data Tanaman (Auto Fix)")
st.write("Aplikasi ini otomatis memperbaiki posisi judul yang bergeser.")

# --- 2. Fungsi Load Data (DIPERBAIKI) ---
@st.cache_data
def load_data(file):
    try:
        # 1. Baca dulu mentah-mentah tanpa header
        if file.name.endswith('.csv'):
            df_temp = pd.read_csv(file, header=None)
        else:
            df_temp = pd.read_excel(file, header=None)
            
        # 2. Cari baris mana yang isinya judul (bukan kosong)
        header_row_index = 0
        for i, row in df_temp.iterrows():
            # Jika baris ini punya lebih dari 1 teks/isi, kemungkinan ini judulnya
            if row.count() > 1:
                header_row_index = i
                break
        
        # 3. Baca ulang file mulai dari baris judul yang ditemukan
        if file.name.endswith('.csv'):
            file.seek(0)
            df = pd.read_csv(file, header=header_row_index)
        else:
            df = pd.read_excel(file, header=header_row_index)

        # 4. Bersihkan kolom sampah (Unnamed)
        # Hapus kolom yang namanya mengandung "Unnamed" ATAU yang isinya kosong semua
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False, na=False)]
        df = df.dropna(axis=1, how='all') 
        
        return df
    except Exception as e:
        return None

# --- 3. Upload File ---
uploaded_file = st.file_uploader("Upload File Data Tanaman (.csv / .xlsx)", type=["xlsx", "csv"])

if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    if df is not None and not df.empty:
        columns = df.columns.tolist()
        
        col_settings, col_preview = st.columns([1, 2])
        
        with col_settings:
            st.header("⚙️ Pengaturan")
            
            # --- DETEKSI KOLOM OTOMATIS ---
            # Cari kolom yang namanya mirip "Dose" atau "Gy"
            col_kategori = next((c for c in columns if 'dose' in c.lower() or 'gy' in c.lower() or 'perlakuan' in c.lower()), columns[0])
            
            # Cari kolom yang namanya mirip "Genetic" atau "Diversity" atau angka lainnya
            col_nilai_candidates = [c for c in columns if c != col_kategori]
            col_nilai = next((c for c in col_nilai_candidates if 'diversity' in c.lower() or 'genetic' in c.lower()), col_nilai_candidates[0] if col_nilai_candidates else col_kategori)

            # Input User (Bisa diganti kalau deteksi salah)
            cat_col = st.selectbox("Pilih Kolom Kategori (Sumbu X)", columns, index=columns.index(col_kategori))
            val_col = st.selectbox("Pilih Kolom Nilai (Sumbu Y)", columns, index=columns.index(col_nilai) if col_nilai in columns else 0)
            
            st.divider()
            
            # Pengaturan Tampilan
            orientasi = st.radio("Arah Grafik", ["Vertikal (Berdiri)", "Horizontal (Tidur)"])
            show_dots = st.checkbox("Tampilkan Titik Data (Dots)", value=True)
            tampilkan_grid = st.checkbox("Tampilkan Grid", value=True)
            dpi = st.number_input("Resolusi (DPI)", 100, 600, 300)

            # --- RENDER GRAFIK ---
            fig, ax = plt.subplots(figsize=(8, 6))
            
            try:
                # Pastikan data nilai benar-benar angka
                df[val_col] = pd.to_numeric(df[val_col], errors='coerce')
                
                # Plotting
                if orientasi == "Vertikal (Berdiri)":
                    sns.boxplot(data=df, x=cat_col, y=val_col, ax=ax, palette="Set2", showfliers=False)
                    if show_dots:
                        sns.stripplot(data=df, x=cat_col, y=val_col, ax=ax, color='black', alpha=0.5, jitter=True, size=5)
                    ax.set_xlabel(cat_col, fontweight='bold')
                    ax.set_ylabel(val_col, fontweight='bold')
                else:
                    sns.boxplot(data=df, x=val_col, y=cat_col, ax=ax, palette="Set2", showfliers=False)
                    if show_dots:
                        sns.stripplot(data=df, x=val_col, y=cat_col, ax=ax, color='black', alpha=0.5, jitter=True, size=5)
                    ax.set_xlabel(val_col, fontweight='bold')
                    ax.set_ylabel(cat_col, fontweight='bold')

                ax.set_title(f"Box Plot: {val_col} vs {cat_col}")
                
                if tampilkan_grid:
                    ax.grid(True, linestyle='--', alpha=0.5)

            except Exception as e:
                st.error(f"Gagal membuat grafik: {e}")

        # --- DOWNLOAD ---
        with col_preview:
            st.subheader("🖼️ Hasil Grafik")
            st.pyplot(fig)
            
            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches='tight', dpi=dpi)
            buf.seek(0)
            
            st.download_button(
                label=f"⬇️ Download Grafik ({dpi} DPI)",
                data=buf,
                file_name="grafik_tanaman.png",
                mime="image/png",
                use_container_width=True
            )
    else:
        st.error("File terbaca kosong. Coba cek isi file Excelnya.")
else:
    st.info("Silakan upload file CSV/Excel Bapak.")
