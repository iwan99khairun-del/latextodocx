import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io

# --- 1. Konfigurasi Halaman ---
st.set_page_config(page_title="Studio Grafik: Box Plot Tanaman", layout="wide")
st.title("🌱 Analisis Data Tanaman (Box Plot + Jitter)")
st.write("Upload file Excel/CSV data tanaman Anda, dan grafik akan otomatis dibuat.")

# --- 2. Fungsi Load Data Cerdas ---
@st.cache_data
def load_data(file):
    try:
        # Cek tipe file
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

        # PEMBERSIHAN KHUSUS DATA BAPAK:
        # 1. Hapus kolom yang namanya kosong atau "Unnamed" (biasanya kolom index sisa)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        
        # 2. Hapus baris kosong jika ada
        df = df.dropna(how='all')
        
        return df
    except Exception as e:
        return None

# --- 3. Upload File ---
uploaded_file = st.file_uploader("Upload File Data Tanaman (.csv / .xlsx)", type=["xlsx", "csv"])

if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    if df is not None:
        columns = df.columns.tolist()
        
        # Layout: Kiri (Menu), Kanan (Gambar)
        col_settings, col_preview = st.columns([1, 2])
        
        with col_settings:
            st.header("⚙️ Pengaturan Grafik")
            
            # Deteksi Otomatis untuk Data Bapak
            st.info("💡 Sistem mendeteksi format data: 'Long Format' (Memanjang ke bawah).")
            
            # Pilih Kolom
            st.subheader("1. Tentukan Data")
            try:
                # Cari otomatis kolom yang mirip "Dose" atau "Dosis"
                default_cat = next((c for c in columns if 'dose' in c.lower() or 'gy' in c.lower()), columns[0])
                cat_col = st.selectbox("Pilih Kolom Kategori (Sumbu X)", columns, index=columns.index(default_cat))
                
                # Cari otomatis kolom angka (selain kategori)
                remaining = [c for c in columns if c != cat_col]
                val_col = st.selectbox("Pilih Kolom Nilai/Angka (Sumbu Y)", remaining, index=0 if remaining else 0)
            except:
                cat_col = st.selectbox("Pilih Kolom Kategori (Sumbu X)", columns)
                val_col = st.selectbox("Pilih Kolom Nilai/Angka (Sumbu Y)", columns)

            st.subheader("2. Tampilan")
            col_opt1, col_opt2 = st.columns(2)
            with col_opt1:
                orientasi = st.radio("Arah Grafik", ["Vertikal (Berdiri)", "Horizontal (Tidur)"])
            with col_opt2:
                show_dots = st.checkbox("Tampilkan Titik (Dots)", value=True)
                
            dpi = st.number_input("Kualitas Gambar (DPI)", 100, 600, 300)
            tampilkan_grid = st.checkbox("Tampilkan Garis Grid", value=True)

            # --- RENDER GRAFIK ---
            fig, ax = plt.subplots(figsize=(10, 6))
            
            try:
                # Pastikan data nilai adalah angka
                df[val_col] = pd.to_numeric(df[val_col], errors='coerce')
                
                # Warna-warni
                colors = "Set2"
                
                if orientasi == "Vertikal (Berdiri)":
                    # Gambar Box Plot
                    sns.boxplot(data=df, x=cat_col, y=val_col, ax=ax, palette=colors, showfliers=False)
                    # Gambar Titik-titik (Jitter)
                    if show_dots:
                        sns.stripplot(data=df, x=cat_col, y=val_col, ax=ax, color='black', alpha=0.5, jitter=True, size=5)
                    
                    ax.set_xlabel(cat_col, fontsize=12, fontweight='bold')
                    ax.set_ylabel(val_col, fontsize=12, fontweight='bold')
                    
                else: # Horizontal
                    # Gambar Box Plot
                    sns.boxplot(data=df, x=val_col, y=cat_col, ax=ax, palette=colors, showfliers=False)
                    # Gambar Titik-titik (Jitter)
                    if show_dots:
                        sns.stripplot(data=df, x=val_col, y=cat_col, ax=ax, color='black', alpha=0.5, jitter=True, size=5)
                        
                    ax.set_xlabel(val_col, fontsize=12, fontweight='bold')
                    ax.set_ylabel(cat_col, fontsize=12, fontweight='bold')

                ax.set_title(f"Distribusi {val_col} berdasarkan {cat_col}", fontsize=14, pad=15)
                
                if tampilkan_grid:
                    ax.grid(True, linestyle='--', alpha=0.5)
                    
            except Exception as e:
                st.error(f"Error saat membuat grafik: {e}")
                st.write("Pastikan kolom Nilai berisi angka.")

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
                file_name=f"grafik_tanaman_{dpi}dpi.png",
                mime="image/png",
                use_container_width=True
            )
    else:
        st.error("Format file tidak dikenali. Coba save as Excel (.xlsx) atau CSV.")
else:
    st.info("Upload file data tanaman Anda di sini.")
