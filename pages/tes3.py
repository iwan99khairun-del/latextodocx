import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import io

# --- SETUP HALAMAN ---
st.set_page_config(page_title="Replika R + Ukuran Titik", layout="centered")
st.title("📊 Replika R (Fitur Lengkap)")

# --- 1. UPLOAD FILE ---
uploaded_file = st.file_uploader("Upload File Excel/CSV", type=["xlsx", "csv"])

if uploaded_file:
    try:
        # --- LANGKAH 1: INTIP DATA (Cari Header) ---
        st.info("👇 **Langkah 1: Tentukan Baris Judul**")
        
        # Baca 10 baris pertama
        if uploaded_file.name.endswith('.csv'):
            df_preview = pd.read_csv(uploaded_file, header=None, nrows=10)
        else:
            df_preview = pd.read_excel(uploaded_file, header=None, nrows=10)
        
        st.dataframe(df_preview)
        
        # Input Baris Header
        header_idx = st.number_input(
            "Baris ke berapa Judul Kolomnya? (Lihat angka index paling kiri 0, 1, 2...)", 
            min_value=0, value=0, step=1
        )

        # --- LANGKAH 2: BACA DATA ---
        uploaded_file.seek(0) # Reset file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, header=header_idx)
        else:
            df = pd.read_excel(uploaded_file, header=header_idx)

        # Bersihkan Kolom
        df.columns = df.columns.astype(str).str.strip()
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        
        # --- LANGKAH 3: PILIH DATA ---
        st.divider()
        st.info("👇 **Langkah 2: Pilih Data Grafik**")
        
        c1, c2 = st.columns(2)
        with c1:
            x_col = st.selectbox("Sumbu X (Kategori/Dosis):", df.columns)
        with c2:
            y_col = st.selectbox("Sumbu Y (Angka):", df.columns, index=1 if len(df.columns) > 1 else 0)

        if x_col and y_col:
            # Pastikan Y angka
            df[y_col] = pd.to_numeric(df[y_col], errors='coerce')
            plot_data = df.dropna(subset=[x_col, y_col]).copy()
            
            if plot_data.empty:
                st.error("Data kosong. Pastikan kolom Y isinya angka.")
                st.stop()

            # Urutkan Kategori Custom (Jika ada pola gy)
            urutan_custom = ["0 gy", "5 gy", "10 gy", "15 gy", "20 gy"]
            cek_kat = plot_data[x_col].unique().astype(str)
            
            if any(k in cek_kat for k in urutan_custom):
                plot_data[x_col] = pd.Categorical(plot_data[x_col], categories=urutan_custom, ordered=True)
                order_final = urutan_custom
            else:
                # Sortir manual
                try:
                    order_final = sorted(plot_data[x_col].unique())
                except:
                    order_final = plot_data[x_col].unique()

            # --- LANGKAH 4: SETTING TAMPILAN ---
            st.divider()
            st.info("👇 **Langkah 3: Atur Tampilan**")
            
            # Pindahkan pengaturan ke dalam Expander biar rapi
            with st.expander("⚙️ Buka Pengaturan Gambar & Titik", expanded=True):
                # Saya buat 3 kolom biar muat
                col_s1, col_s2, col_s3 = st.columns(3)
                
                with col_s1:
                    st.markdown("##### 📏 Dimensi")
                    fig_w = st.slider("Lebar (Width)", 3.0, 10.0, 5.0)
                    fig_h = st.slider("Tinggi (Height)", 3.0, 10.0, 4.0)
                
                with col_s2:
                    st.markdown("##### 🎯 Posisi")
                    seed = st.number_input("Kode Posisi (Seed)", value=42, help="Ganti angka ini agar posisi titik teracak ulang.")
                    jitter = st.slider("Sebaran (Jitter)", 0.0, 0.3, 0.12)
                    
                with col_s3:
                    st.markdown("##### 🔵 Bulatan")
                    # FITUR BARU: UKURAN TITIK
                    point_size_val = st.slider("Ukuran Titik (Size)", 2.0, 15.0, 7.0, help="Geser untuk memperbesar/memperkecil bulatan.")

            # --- GAMBAR GRAFIK ---
            fig, ax = plt.subplots(figsize=(fig_w, fig_h))
            
            # Style R Classic
            ax.set_facecolor('white')
            for spine in ax.spines.values():
                spine.set_visible(True)
                spine.set_color('#595959')
                spine.set_linewidth(1)

            # Boxplot
            sns.boxplot(
                data=plot_data, x=x_col, y=y_col, order=order_final, ax=ax,
                width=0.65, showfliers=False,
                boxprops=dict(facecolor='#CCCCCC', edgecolor='#595959', linewidth=0.9),
                whiskerprops=dict(color='#595959', linewidth=0.9),
                capprops=dict(color='#595959', linewidth=0.9),
                medianprops=dict(color='#595959', linewidth=2)
            )

            # Jitter Points
            np.random.seed(int(seed))
            sns.stripplot(
                data=plot_data, x=x_col, y=y_col, order=order_final, ax=ax,
                jitter=jitter, 
                size=point_size_val, # <--- INI YANG BERUBAH (Pakai nilai slider)
                edgecolor='red', linewidth=0.7,
                color='orange', alpha=0.9,
                marker='o'
            )

            # Labels
            ax.set_xlabel(x_col, fontweight='bold', color='black')
            ax.set_ylabel(y_col, fontweight='bold', color='black')
            ax.tick_params(colors='black')

            st.pyplot(fig)

            # --- LANGKAH 5: DOWNLOAD DENGAN RESOLUSI ---
            st.write("---")
            st.subheader("💾 Simpan Gambar")
            
            col_d1, col_d2 = st.columns([2, 1])
            
            with col_d1:
                # PILIHAN RESOLUSI (DPI)
                pilihan_dpi = st.selectbox(
                    "Pilih Kualitas (Resolusi):",
                    options=[
                        "72 DPI (Ringan - Buat WA/HP)",
                        "150 DPI (Sedang - PPT/Word)",
                        "300 DPI (Tinggi - Jurnal/Skripsi)",
                        "600 DPI (Ultra - Poster Besar)"
                    ],
                    index=2 # Default ke 300 DPI
                )
                
                # Ambil angkanya saja dari teks pilihan
                dpi_final = int(pilihan_dpi.split(" ")[0])

            with col_d2:
                # Simpan ke memori sesuai DPI
                buf = io.BytesIO()
                fig.savefig(buf, format="png", dpi=dpi_final, bbox_inches='tight')
                buf.seek(0)
                
                st.write("") # Spasi biar tombol agak turun dikit
                st.write("")
                st.download_button(
                    label=f"⬇️ Download PNG ({dpi_final} DPI)",
                    data=buf,
                    file_name=f"grafik_replika_R_{dpi_final}dpi.png",
                    mime="image/png",
                    use_container_width=True
                )

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
