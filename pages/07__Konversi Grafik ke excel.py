import streamlit as st
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import io

def hex_to_hsv(hex_color):
    hex_color = hex_color.lstrip('#')
    h_len = len(hex_color)
    rgb = tuple(int(hex_color[i:i + h_len // 3], 16) for i in range(0, h_len, h_len // 3))
    pixel = np.uint8([[list(rgb)]])
    hsv = cv2.cvtColor(pixel, cv2.COLOR_RGB2HSV)
    return hsv[0][0]

st.set_page_config(page_title="Ekstraktor Grafik ke Excel", layout="wide")

st.title("📈 Ekstrak Data dari Gambar Grafik")
st.markdown("Upload gambar grafik, lalu atur parameter di sebelah kiri untuk mendapatkan datanya.")

# --- PERUBAHAN DI SINI ---
# Menghapus 'st.sidebar' agar letaknya di tengah halaman utama
uploaded_file = st.file_uploader("Upload Gambar Grafik (JPG/PNG)", type=["jpg", "jpeg", "png"])
# -------------------------

if uploaded_file is not None:
    # Baca file gambar
    image_pil = Image.open(uploaded_file).convert('RGB')
    img_array = np.array(image_pil)
    height_ori, width_ori, _ = img_array.shape

    # --- MENU PENGATURAN (Tetap di Sidebar agar rapi) ---
    with st.sidebar:
        st.header("🔧 Pengaturan & Kalibrasi")
        
        st.subheader("1. Kalibrasi Sumbu")
        st.info("Masukkan angka sesuai sumbu di grafi aslimu.")
        x_axis_min = st.number_input("Nilai X Minimum", value=0.0)
        x_axis_max = st.number_input("Nilai X Maksimum", value=100.0)
        y_axis_min = st.number_input("Nilai Y Minimum", value=0.0)
        y_axis_max = st.number_input("Nilai Y Maksimum", value=100.0)

        st.subheader("2. Deteksi Warna")
        target_color_hex = st.color_picker("Pilih Warna Garis", "#0000FF") 
        tolerance = st.slider("Toleransi Warna", 10, 100, 40)
        
        st.markdown("---")
        st.caption("Tips: Jika hasil kosong, naikkan toleransi warna.")

    # --- TAMPILAN UTAMA (Split 2 Kolom) ---
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("✂️ Potong Gambar (Crop)")
        st.info("Geser slider ini sampai HANYA kotak grafik yang terlihat (buang label/judul).")
        
        # Slider Cropping
        y_min_crop, y_max_crop = st.slider("Potong Atas-Bawah (Y)", 0, height_ori, (0, height_ori))
        x_min_crop, x_max_crop = st.slider("Potong Kiri-Kanan (X)", 0, width_ori, (0, width_ori))
        
        # Proses Crop
        cropped_img = img_array[y_min_crop:y_max_crop, x_min_crop:x_max_crop]
        st.image(cropped_img, caption="Area Grafik yang Akan Diproses")
        
        h_crop, w_crop, _ = cropped_img.shape

    # PROSES EKSTRAKSI
    with col2:
        st.subheader("📊 Hasil Data")
        
        # Logika Deteksi (Sama seperti sebelumnya)
        hsv_img = cv2.cvtColor(cropped_img, cv2.COLOR_RGB2HSV)
        target_hsv = hex_to_hsv(target_color_hex)

        lower_bound = np.array([max(0, target_hsv[0]-tolerance), 50, 50])
        upper_bound = np.array([min(179, target_hsv[0]+tolerance), 255, 255])
        
        mask = cv2.inRange(hsv_img, lower_bound, upper_bound)
        
        # Tampilkan Masking (Preview apa yang dilihat komputer)
        st.image(mask, caption="Garis Terdeteksi (Putih = Data)", clamp=True)

        # Hitung Koordinat
        ys, xs = np.where(mask > 0)
        
        if len(xs) > 0:
            df_pixel = pd.DataFrame({'px_x': xs, 'px_y': ys})
            df_grouped = df_pixel.groupby('px_x')['px_y'].mean().reset_index()
            
            # Rumus Konversi Pixel ke Nilai Asli
            df_grouped['Data_X'] = x_axis_min + (df_grouped['px_x'] / w_crop) * (x_axis_max - x_axis_min)
            df_grouped['Data_Y'] = y_axis_min + ((h_crop - df_grouped['px_y']) / h_crop) * (y_axis_max - y_axis_min)
            
            final_df = df_grouped[['Data_X', 'Data_Y']].sort_values(by='Data_X')
            
            st.success(f"Ditemukan {len(final_df)} titik data.")
            st.dataframe(final_df.head(), height=150)
            
            # Tombol Download
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                final_df.to_excel(writer, index=False, sheet_name='Sheet1')
            
            st.download_button(
                label="📥 Download Excel",
                data=output.getvalue(),
                file_name="hasil_ekstraksi_grafik.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary" # Membuat tombol lebih menonjol
            )
            
        else:
            st.warning("⚠️ Garis tidak terdeteksi. Coba ganti warna atau naikkan toleransi di menu kiri.")

else:
    # Pesan jika belum ada file yang diupload
    st.info("👆 Silakan upload file grafik di atas untuk memulai.")
