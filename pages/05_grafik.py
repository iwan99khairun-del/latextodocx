import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# 1. Judul Aplikasi
st.title("📊 Aplikasi Pembuat Grafik dari Excel")
st.write("Upload file Excel Anda, pilih kolom, dan download grafiknya.")

# 2. Widget Upload File
uploaded_file = st.file_uploader("Pilih file Excel (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    # Membaca file excel menggunakan Pandas
    try:
        df = pd.read_excel(uploaded_file)
        
        # Tampilkan preview data (5 baris pertama)
        st.subheader("Preview Data:")
        st.dataframe(df.head())

        # 3. Form Konfigurasi Grafik
        st.subheader("Pengaturan Grafik")
        
        # Mengambil nama-nama kolom dari Excel
        columns = df.columns.tolist()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            x_axis = st.selectbox("Pilih Sumbu X (Horizontal)", columns)
        with col2:
            y_axis = st.selectbox("Pilih Sumbu Y (Vertikal)", columns)
        with col3:
            chart_type = st.selectbox("Jenis Grafik", ["Line Chart", "Bar Chart", "Scatter Plot"])
        #-----------------------------------------    
                  # ... (kode sebelumnya: color picker)
        color = st.color_picker("Pilih Warna Grafik", "#1f77b4")
        
        # [BARU] Widget untuk memilih Resolusi (DPI)
        dpi_pilihan = st.selectbox(
            "Pilih Resolusi Gambar (DPI)",
            options=[100, 300, 600],
            index=1, # Default pilih 300
            help="300 DPI standar untuk cetak/jurnal. 100 DPI untuk layar komputer."
        )
        #--------------------------------------------
        color = st.color_picker("Pilih Warna Grafik", "#1f77b4")

        # 4. Logic Membuat Grafik dengan Matplotlib
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if chart_type == "Line Chart":
            ax.plot(df[x_axis], df[y_axis], color=color, marker='o')
        elif chart_type == "Bar Chart":
            ax.bar(df[x_axis], df[y_axis], color=color)
        elif chart_type == "Scatter Plot":
            ax.scatter(df[x_axis], df[y_axis], color=color)

        ax.set_xlabel(x_axis)
        ax.set_ylabel(y_axis)
        ax.set_title(f"Grafik {y_axis} vs {x_axis}")
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.xticks(rotation=45) # Miringkan teks sumbu X agar terbaca

        # Tampilkan Grafik di Web
        st.pyplot(fig)

        # 5. Fitur Download
        # Simpan gambar ke dalam memory (buffer) bukan ke harddisk
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches='tight')
        buf.seek(0)

        st.download_button(
            label="⬇️ Download Grafik (PNG)",
            data=buf,
            file_name="hasil_grafik.png",
            mime="image/png"
        )

    except Exception as e:
        st.error(f"Terjadi kesalahan saat membaca file: {e}")

else:
    st.info("Silakan upload file Excel untuk memulai.")
