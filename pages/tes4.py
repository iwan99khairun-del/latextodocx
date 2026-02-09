import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import io

# --- SETUP HALAMAN ---
st.set_page_config(page_title="Replika R + Atur Kotak", layout="centered")
st.title("📊 Replika R (Kontrol Geometri)")

# --- 1. UPLOAD FILE ---
uploaded_file = st.file_uploader("Upload File Excel/CSV", type=["xlsx", "csv"])

if uploaded_file:
    try:
        # --- LANGKAH 1: INTIP DATA (Cari Header) ---
        st.info("👇 **Langkah 1: Tentukan Baris Judul**")
        
        if uploaded_file.name.endswith('.csv'):
            df_preview = pd.read_csv(uploaded_file, header=None, nrows=10)
        else:
            df_preview = pd.read_excel(uploaded_file, header=None, nrows=10)
        
        st.dataframe(df_preview)
        
        header_idx = st.number_input(
            "Baris ke berapa Judul Kolomnya? (Index 0, 1, 2...)", 
            min_value=0, value=0, step=1
        )

        # --- LANGKAH 2: BACA DATA ---
        uploaded_file.seek(0) 
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
            df[y_col] = pd.to_numeric(df[y_col], errors='coerce')
            plot_data = df.dropna(subset=[x_col, y_col]).copy()
            
            if plot_data.empty:
                st.error("Data kosong. Pastikan kolom Y isinya angka.")
                st.stop()

            # Urutkan Kategori
            urutan_custom = ["0 gy", "5 gy", "10 gy", "15 gy", "20 gy"]
            cek_kat = plot_data[x_col].unique().astype(str)
            
            if any(k in cek_kat for k in urutan_custom):
                plot_data[x_col] = pd.Categorical(plot_data[x_col], categories=urutan_custom, ordered=True)
                order_final = urutan_custom
            else:
                try:
                    order_final = sorted(plot_data[x_col].unique())
                except:
                    order_final = plot_data[x_col].unique()

            # --- LANGKAH 4: SETTING TAMPILAN ---
            st.divider()
            st.info("👇 **Langkah 3: Atur Tampilan**")
            
            with st.expander("⚙️ Buka Pengaturan Gambar, Titik & Kotak", expanded=True):
                # TAB 1: DIMENSI GAMBAR
                st.markdown("##### 🖼️ Ukuran Kanvas")
                col_dim1, col_dim2 = st.columns(2)
                with col_dim1:
                    fig_w = st.slider("Lebar Gambar", 3.0, 12.0, 5.0)
                with col_dim2:
                    fig_h = st.slider("Tinggi Gambar", 3.0, 12.0, 4.0)

                st.divider()

                # TAB 2: GEOMETRI KOTAK & SUMBU
                st.markdown("##### 📦 Bentuk Kotak & Sumbu Y")
                col_box1, col_box2, col_box3 = st.columns(3)
                
                with col_box1:
                    # FITUR BARU: LEBAR KOTAK
                    box_width_val = st.slider("Lebar Kotak (Width)", 0.1, 1.0, 0.65, help="Atur seberapa gemuk kotaknya. Default R = 0.65")
                
                with col_box2:
                    # FITUR BARU: BATAS BAWAH Y
                    y_min_manual = st.number_input("Batas Bawah Y (Min)", value=0.0, step=1.0, help="Atur angka paling bawah di sumbu Y")
                
                with col_box3:
                    # FITUR BARU: BATAS ATAS Y (Otomatis deteksi max data + sedikir margin)
                    default_max = float(plot_data[y_col].max()) * 1.1
                    y_max_manual = st.number_input("Batas Atas Y (Max)", value=default_max, step=1.0, help="Atur angka paling atas di sumbu Y")

                st.divider()

                # TAB 3: TITIK (JITTER)
                st.markdown("##### 🔵 Titik Data")
                col_pt1, col_pt2, col_pt3 = st.columns(3)
                with col_pt1:
                    seed = st.number_input("Kode Posisi (Seed)", value=42)
                with col_pt2:
                    jitter = st.slider("Sebaran (Jitter)", 0.0, 0.3, 0.12)
                with col_pt3:
                    point_size_val = st.slider("Ukuran Titik", 2.0, 15.0, 7.0)

            # --- GAMBAR GRAFIK ---
            fig, ax = plt.subplots(figsize=(fig_w, fig_h))
            
            # Style R Classic
            ax.set_facecolor('white')
            for spine in ax.spines.values():
                spine.set_visible(True)
                spine.set_color('#595959')
                spine.set_linewidth(1)

            # FITUR BARU: SET LIMIT SUMBU Y
            # Ini yang mengatur "Tinggi Visual" dari grafik
            if y_max_manual > y_min_manual:
                ax.set_ylim(bottom=y_min_manual, top=y_max_manual)

            # Boxplot
            sns.boxplot(
                data=plot_data, x=x_col, y=y_col, order=order_final, ax=ax,
                width=box_width_val, # <--- INI VARIABEL LEBAR KOTAK
                showfliers=False,
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
                size=point_size_val, 
                edgecolor='red', linewidth=0.7,
                color='orange', alpha=0.9,
                marker='o'
            )

            # Labels
            ax.set_xlabel(x_col, fontweight='bold', color='black')
            ax.set_ylabel(y_col, fontweight='bold', color='black')
            ax.tick_params(colors='black')

            st.pyplot(fig)

            # --- LANGKAH 5: DOWNLOAD ---
            st.write("---")
            st.subheader("💾 Simpan Gambar")
            
            col_d1, col_d2 = st.columns([2, 1])
            with col_d1:
                pilihan_dpi = st.selectbox(
                    "Pilih Kualitas (Resolusi):",
                    options=["72 DPI (Ringan)", "150 DPI (Sedang)", "300 DPI (Tinggi)", "600 DPI (Ultra)"],
                    index=2
                )
                dpi_final = int(pilihan_dpi.split(" ")[0])

            with col_d2:
                buf = io.BytesIO()
                fig.savefig(buf, format="png", dpi=dpi_final, bbox_inches='tight')
                buf.seek(0)
                st.write(""); st.write("")
                st.download_button(f"⬇️ Download PNG", buf, f"grafik_{dpi_final}dpi.png", "image/png", use_container_width=True)

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
