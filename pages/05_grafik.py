import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# --- 1. Judul & Konfigurasi Halaman ---
st.title("📊 Aplikasi Pembuat Grafik dari Excel")
st.write("Upload file Excel, atur parameter, dan download grafik resolusi tinggi.")

# --- 2. Widget Upload File ---
uploaded_file = st.file_uploader("Pilih file Excel (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Membaca file excel
        df_raw = pd.read_excel(uploaded_file)
        
        # --- PEMBERSIHAN DATA OTOMATIS ---
        # Cek apakah baris pertama isinya teks satuan (seperti 'Mpa', 'm/s')
        # Jika kolom pertama baris ke-0 bukan angka, kita asumsikan itu baris satuan dan kita hapus
        first_val = df_raw.iloc[0, 0]
        if isinstance(first_val, str) and not first_val.replace('.', '', 1).isdigit():
            st.info("⚠️ Mendeteksi baris satuan (misal: Mpa, m/s). Baris tersebut otomatis dihapus agar grafik valid.")
            df = df_raw.drop(index=0).reset_index(drop=True)
        else:
            df = df_raw

        # Paksa semua data menjadi angka (jika ada teks nyelip, diubah jadi NaN)
        df = df.apply(pd.to_numeric, errors='coerce')
        
        # Tampilkan preview data bersih
        with st.expander("Klik untuk melihat Preview Data Bersih"):
            st.dataframe(df.head())

        # --- 3. Pengaturan Grafik ---
        st.subheader("Pengaturan Grafik")
        
        columns = df.columns.tolist()
        
        col1, col2 = st.columns(2)
        with col1:
            x_axis = st.selectbox("Pilih Sumbu X (Horizontal)", columns)
        with col2:
            y_axis = st.selectbox("Pilih Sumbu Y (Vertikal)", columns)
            
        col3, col4, col5 = st.columns(3)
        with col3:
            chart_type = st.selectbox("Jenis Grafik", ["Line Chart", "Bar Chart", "Scatter Plot"])
        with col4:
            # HANYA ADA SATU color_picker DI SINI
            color = st.color_picker("Pilih Warna", "#1f77b4")
        with col5:
            # Pilihan DPI
            dpi_pilihan = st.selectbox("Resolusi (DPI)", [100, 300, 600], index=1)

        # --- 4. Logic Membuat Grafik ---
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plotting
        if chart_type == "Line Chart":
            ax.plot(df[x_axis], df[y_axis], color=color, marker='o', linestyle='-')
        elif chart_type == "Bar Chart":
            ax.bar(df[x_axis], df[y_axis], color=color)
        elif chart_type == "Scatter Plot":
            ax.scatter(df[x_axis], df[y_axis], color=color)

        # Labeling
        ax.set_xlabel(x_axis)
        ax.set_ylabel(y_axis)
        ax.set_title(f"{y_axis} vs {x_axis}")
        ax.grid(True, linestyle='--', alpha=0.6)
        
        # Tampilkan Grafik
        st.pyplot(fig)

        # --- 5. Tombol Download ---
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches='tight', dpi=dpi_pilihan)
        buf.seek(0)

        st.download_button(
            label=f"⬇️ Download Grafik ({dpi_pilihan} DPI)",
            data=buf,
            file_name=f"grafik_{y_axis}_vs_{x_axis}.png",
            mime="image/png"
        )

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
        st.warning("Pastikan data Excel Anda bersih (baris pertama Header, baris selanjutnya Angka).")

else:
    st.info("Silakan upload file Excel untuk memulai.")
