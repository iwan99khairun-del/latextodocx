import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import io

st.set_page_config(page_title="Replika R - Mode Kontrol Penuh", layout="centered")
st.title("📊 Replika R (Kontrol Penuh)")

# --- 1. UPLOAD FILE ---
uploaded_file = st.file_uploader("Upload File Excel", type=["xlsx", "csv"])

if uploaded_file:
    try:
        # --- LANGKAH 1: CEK DATA MENTAH DULU ---
        st.subheader("1. Cek Data Mentah Anda")
        st.info("Lihat tabel di bawah. Baris nomor berapa yang berisi Judul (Header)?")
        
        # Baca tanpa header dulu buat ngintip
        if uploaded_file.name.endswith('.csv'):
            df_preview = pd.read_csv(uploaded_file, header=None, nrows=10)
        else:
            try:
                df_preview = pd.read_excel(uploaded_file, header=None, nrows=10)
            except:
                df_preview = pd.read_excel(uploaded_file, sheet_name=0, header=None, nrows=10)
        
        # Tampilkan data mentah
        st.dataframe(df_preview)

        # Input Baris Header
        header_row = st.number_input(
            "Masukkan Nomor Baris Judul (Lihat index di kiri tabel, mulai dari 0)", 
            value=1, 
            min_value=0, 
            step=1,
            help="Contoh: Kalau judul 'Irradiation Doses' ada di baris ke-2, tulis 1 (karena hitungan mulai dari 0)."
        )

        if st.button("Proses Data"):
            st.session_state['header_fixed'] = True
            st.session_state['row_idx'] = header_row

        # --- LANGKAH 2: BACA DATA SESUAI HEADER PILIHAN ---
        # Kita pakai trik 'session_state' biar gak reload terus
        idx_to_use = st.session_state.get('row_idx', header_row)
        
        # Baca ulang file dengan header yang benar
        uploaded_file.seek(0) # Reset pembacaan file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, header=idx_to_use)
        else:
            try:
                df = pd.read_excel(uploaded_file, sheet_name="Sheet2", header=idx_to_use)
            except:
                df = pd.read_excel(uploaded_file, header=idx_to_use)

        # Bersihkan nama kolom
        df.columns = df.columns.astype(str).str.strip()
        # Hapus kolom aneh
        cols = [c for c in df.columns if "Unnamed" not in c and c != "nan"]
        df = df[cols]

        st.success("✅ Data Berhasil Dibaca!")
        
        # --- LANGKAH 3: PILIH KOLOM ---
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            pilihan_x = st.selectbox("Pilih Kolom Kategori (Dosis)", df.columns)
        with col2:
            pilihan_y = st.selectbox("Pilih Kolom Angka (Nilai)", df.columns, index=1 if len(df.columns) > 1 else 0)

        # PROSES FINAL
        if pilihan_x and pilihan_y:
            # Pastikan kolom Angka isinya benar-benar ANGKA
            df[pilihan_y] = pd.to_numeric(df[pilihan_y], errors='coerce')
            df_clean = df.dropna(subset=[pilihan_x, pilihan_y]).copy()

            if df_clean.empty:
                st.error("Data kosong setelah dibersihkan. Cek apakah kolom yang dipilih isinya angka.")
                st.stop()

            # Atur Urutan Kategori (Biar 0 gy, 5 gy...)
            urutan_custom = ["0 gy", "5 gy", "10 gy", "15 gy", "20 gy"]
            cek_isi = df_clean[pilihan_x].unique().astype(str)
            
            if any(x in cek_isi for x in urutan_custom):
                df_clean[pilihan_x] = pd.Categorical(df_clean[pilihan_x], categories=urutan_custom, ordered=True)
                urutan_final = urutan_custom
            else:
                # Sortir manual angka
                import re
                def sorter(val):
                    m = re.search(r'\d+', str(val))
                    return int(m.group()) if m else 999
                urutan_final = sorted(df_clean[pilihan_x].unique(), key=sorter)

            # --- LANGKAH 4: ATUR TAMPILAN & GAMBAR ---
            st.divider()
            st.subheader("2. Atur Grafik")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                w_fig = st.slider("Lebar", 3.0, 8.0, 5.0)
            with c2:
                h_fig = st.slider("Tinggi", 3.0, 8.0, 4.0)
            with c3:
                seed_val = st.number_input("Acak Posisi (Seed)", value=42)
                jitter_val = st.slider("Jitter", 0.0, 0.3, 0.12)

            # --- GAMBAR (Matplotlib gaya R) ---
            fig, ax = plt.subplots(figsize=(w_fig, h_fig))
            
            # Tema Putih + Border Abu
            ax.set_facecolor('white')
            for spine in ax.spines.values():
                spine.set_visible(True)
                spine.set_color('#595959')
                spine.set_linewidth(1)

            # Boxplot
            sns.boxplot(
                data=df_clean, x=pilihan_x, y=pilihan_y, order=urutan_final, ax=ax,
                width=0.65, showfliers=False,
                boxprops=dict(facecolor='#CCCCCC', edgecolor='#595959', linewidth=0.9),
                whiskerprops=dict(color='#595959', linewidth=0.9),
                capprops=dict(color='#595959', linewidth=0.9),
                medianprops=dict(color='#595959', linewidth=2)
            )

            # Jitter Points
            np.random.seed(seed_val)
            sns.stripplot(
                data=df_clean, x=pilihan_x, y=pilihan_y, order=urutan_final, ax=ax,
                jitter=jitter_val, size=7,
                edgecolor='red', linewidth=0.7,
                color='orange', alpha=0.9,
                marker='o'
            )

            # Labels
            ax.set_xlabel(pilihan_x, fontweight='bold', color='black')
            ax.set_ylabel(pilihan_y, fontweight='bold', color='black')
            ax.tick_params(colors='black')

            st.pyplot(fig)

            # Download
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=300, bbox_inches='tight')
            buf.seek(0)
            st.download_button("⬇️ Download Gambar PNG", buf, "grafik_fix.png", "image/png")

    except Exception as e:
        st.error(f"Terjadi error: {e}")
        st.warning("Coba ganti nomor baris judul di atas.")

else:
    st.info("Upload file Excel Bapak dulu.")
