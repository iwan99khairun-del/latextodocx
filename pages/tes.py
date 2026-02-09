import streamlit as st
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import io

def hex_to_hsv(hex_color):
    """Mengubah kode warna HEX (dari color picker) ke format HSV OpenCV"""
    hex_color = hex_color.lstrip('#')
    h_len = len(hex_color)
    rgb = tuple(int(hex_color[i:i + h_len // 3], 16) for i in range(0, h_len, h_len // 3))
    # Convert RGB to HSV using OpenCV standard (H: 0-179, S: 0-255, V: 0-255)
    # Note: Streamlit color picker returns RGB, OpenCV needs BGR ordering for conversion usually,
    # but here we construct a 1x1 pixel image.
    pixel = np.uint8([[list(rgb)]])
    hsv = cv2.cvtColor(pixel, cv2.COLOR_RGB2HSV)
    return hsv[0][0]

st.set_page_config(page_title="Ekstraktor Grafik ke Excel", layout="wide")

st.title("📈 Ekstrak Data dari Gambar Grafik")
st.markdown("Upload gambar grafik, pilih warna garisnya, tentukan skala, dan download Excel-nya!")

# 1. UPLOAD IMAGE
uploaded_file = st.sidebar.file_uploader("Upload Gambar Grafik (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Baca file gambar
    image_pil = Image.open(uploaded_file).convert('RGB')
    img_array = np.array(image_pil)
    
    # Simpan dimensi asli
    height_ori, width_ori, _ = img_array.shape

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("1. Tampilan Asli & Cropping")
        st.info("Gunakan slider di bawah untuk memotong gambar HANYA pada area kotak grafik (tanpa label sumbu/judul).")
        
        # Slider untuk Cropping (Memotong area grafik saja)
        y_min_crop, y_max_crop = st.slider("Potong Tinggi (Y)", 0, height_ori, (0, height_ori))
        x_min_crop, x_max_crop = st.slider("Potong Lebar (X)", 0, width_ori, (0, width_ori))
        
        # Proses Crop
        cropped_img = img_array[y_min_crop:y_max_crop, x_min_crop:x_max_crop]
        st.image(cropped_img, caption="Area Grafik yang Akan Diproses")
        
        h_crop, w_crop, _ = cropped_img.shape

    with st.sidebar:
        st.header("2. Kalibrasi Sumbu")
        st.write("Masukkan nilai MIN dan MAX sesuai angka di sumbu grafik aslimu.")
        x_axis_min = st.number_input("Nilai X Minimum", value=0.0)
        x_axis_max = st.number_input("Nilai X Maksimum", value=100.0)
        y_axis_min = st.number_input("Nilai Y Minimum", value=0.0)
        y_axis_max = st.number_input("Nilai Y Maksimum", value=100.0)

        st.header("3. Deteksi Warna Garis")
        target_color_hex = st.color_picker("Pilih Warna Garis Grafik", "#0000FF") # Default Blue
        tolerance = st.slider("Toleransi Warna (Sensitivity)", 10, 100, 40)

    # PROSES EKSTRAKSI
    with col2:
        st.subheader("4. Hasil Deteksi")
        
        # Convert ke HSV untuk deteksi warna yang lebih akurat
        hsv_img = cv2.cvtColor(cropped_img, cv2.COLOR_RGB2HSV)
        target_hsv = hex_to_hsv(target_color_hex)

        # Buat range warna berdasarkan toleransi
        lower_bound = np.array([max(0, target_hsv[0]-tolerance), 50, 50])
        upper_bound = np.array([min(179, target_hsv[0]+tolerance), 255, 255])
        
        # Masking (Hanya ambil warna yang dipilih)
        mask = cv2.inRange(hsv_img, lower_bound, upper_bound)
        
        # Tampilkan Masking untuk debugging user
        st.image(mask, caption="Garis yang Terdeteksi (Putih = Data)", clamp=True)

        # LOGIKA MATEMATIKA: Ekstraksi Koordinat
        # Kita scan setiap kolom pixel (X) untuk mencari rata-rata posisi pixel putih (Y)
        extracted_data = []
        
        # Mencari pixel putih
        # Koordinat pixel (y, x) dimana mask > 0
        ys, xs = np.where(mask > 0)
        
        if len(xs) > 0:
            # Buat DataFrame sementara untuk menghitung rata-rata Y per X
            df_pixel = pd.DataFrame({'px_x': xs, 'px_y': ys})
            
            # Group by X pixel, ambil rata-rata Y (untuk menangani tebal garis)
            df_grouped = df_pixel.groupby('px_x')['px_y'].mean().reset_index()
            
            # --- KONVERSI PIXEL KE DATA ASLI ---
            # Rumus Interpolasi Linear:
            # Data_X = X_min + (px_x / lebar_gambar) * (X_max - X_min)
            # Data_Y = Y_min + ((tinggi_gambar - px_y) / tinggi_gambar) * (Y_max - Y_min)
            # Catatan: Pixel Y dihitung dari atas (0), sedangkan grafik Y dihitung dari bawah. Jadi harus dibalik.
            
            df_grouped['Data_X'] = x_axis_min + (df_grouped['px_x'] / w_crop) * (x_axis_max - x_axis_min)
            
            # Inversi Y pixel
            df_grouped['Data_Y'] = y_axis_min + ((h_crop - df_grouped['px_y']) / h_crop) * (y_axis_max - y_axis_min)
            
            final_df = df_grouped[['Data_X', 'Data_Y']].sort_values(by='Data_X')
            
            st.success(f"Berhasil mengekstrak {len(final_df)} titik data!")
            st.dataframe(final_df.head())
            
            # 5. DOWNLOAD MENU
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                final_df.to_excel(writer, index=False, sheet_name='Sheet1')
            
            st.download_button(
                label="📥 Download File Excel",
                data=output.getvalue(),
                file_name="hasil_ekstraksi_grafik.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        else:
            st.warning("Tidak ada garis yang terdeteksi. Coba atur 'Toleransi Warna' atau pilih warna yang lebih pas.")

else:
    st.info("Silakan upload gambar grafik di panel sebelah kiri.")
