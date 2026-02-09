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
st.markdown("Upload gambar grafik, pilih tipe grafik (Garis/Batang), atur warna, dan download datanya.")

# Upload File
uploaded_file = st.file_uploader("Upload Gambar Grafik (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image_pil = Image.open(uploaded_file).convert('RGB')
    img_array = np.array(image_pil)
    height_ori, width_ori, _ = img_array.shape

    # --- SIDEBAR: PENGATURAN ---
    with st.sidebar:
        st.header("🔧 Konfigurasi")
        
        # 1. PILIH TIPE (Baru!)
        st.subheader("1. Tipe Grafik")
        chart_type = st.radio(
            "Apa yang mau diambil?",
            ["Garis (Line Chart)", "Batang (Bar Chart)"],
            help="Pilih 'Batang' untuk mengambil nilai puncak dari grafik balok."
        )
        
        # 2. KALIBRASI
        st.subheader("2. Kalibrasi Sumbu")
        st.caption("Masukkan angka MIN dan MAX sesuai label di sumbu grafik.")
        col_x1, col_x2 = st.columns(2)
        with col_x1: x_axis_min = st.number_input("X Min", value=0.0)
        with col_x2: x_axis_max = st.number_input("X Max", value=100.0)
        
        col_y1, col_y2 = st.columns(2)
        with col_y1: y_axis_min = st.number_input("Y Min", value=0.0)
        with col_y2: y_axis_max = st.number_input("Y Max", value=100.0)

        # 3. WARNA
        st.subheader("3. Deteksi Warna")
        st.caption("Pilih warna yang ingin diambil datanya.")
        target_color_hex = st.color_picker("Warna Target", "#FF0000") 
        tolerance = st.slider("Toleransi Warna", 10, 150, 60) # Range diperbesar sampai 150

    # --- AREA UTAMA ---
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("✂️ Step 1: Potong Gambar")
        st.info("PENTING: Geser slider sampai label angka & judul HILANG. Sisakan kotaknya saja.")
        
        y_crop = st.slider("Potong Atas-Bawah (Y)", 0, height_ori, (0, height_ori))
        x_crop = st.slider("Potong Kiri-Kanan (X)", 0, width_ori, (0, width_ori))
        
        # Applying Crop
        cropped_img = img_array[y_crop[0]:y_crop[1], x_crop[0]:x_crop[1]]
        st.image(cropped_img, caption="Area Grafik Bersih")
        h_crop, w_crop, _ = cropped_img.shape

    with col2:
        st.subheader("👀 Step 2: Preview & Download")
        
        # Proses Warna
        hsv_img = cv2.cvtColor(cropped_img, cv2.COLOR_RGB2HSV)
        target_hsv = hex_to_hsv(target_color_hex)

        # Range warna diperlebar (Saturation & Value min 20, bukan 50) agar lebih sensitif
        lower_bound = np.array([max(0, target_hsv[0]-tolerance), 20, 20])
        upper_bound = np.array([min(179, target_hsv[0]+tolerance), 255, 255])
        
        mask = cv2.inRange(hsv_img, lower_bound, upper_bound)
        st.image(mask, caption="Preview Deteksi (Putih = Data Terbaca)", clamp=True)

        # Hitung Koordinat
        ys, xs = np.where(mask > 0)
        
        if len(xs) > 0:
            df_pixel = pd.DataFrame({'px_x': xs, 'px_y': ys})
            
            # --- LOGIKA MATEMATIKA ---
            if chart_type == "Batang (Bar Chart)":
                # Cari nilai Y minimum (karena pixel 0 ada di atas, min pixel = posisi paling tinggi/puncak)
                df_grouped = df_pixel.groupby('px_x')['px_y'].min().reset_index()
            else:
                # Cari nilai rata-rata (tengah garis)
                df_grouped = df_pixel.groupby('px_x')['px_y'].mean().reset_index()

            # Konversi ke Skala Asli
            df_grouped['Data_X'] = x_axis_min + (df_grouped['px_x'] / w_crop) * (x_axis_max - x_axis_min)
            # Rumus Y dibalik karena koordinat pixel terbalik
            df_grouped['Data_Y'] = y_axis_min + ((h_crop - df_grouped['px_y']) / h_crop) * (y_axis_max - y_axis_min)
            
            final_df = df_grouped[['Data_X', 'Data_Y']].sort_values(by='Data_X')
            
            st.success(f"Berhasil! Ditemukan {len(final_df)} titik data.")
            st.dataframe(final_df.head(5))
            
            # Tombol Download
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                final_df.to_excel(writer, index=False, sheet_name='Data_Grafik')
            
            st.download_button(
                label="📥 DOWNLOAD EXCEL",
                data=output.getvalue(),
                file_name="hasil_data_grafik.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )
        else:
            st.error("⚠️ Tidak ada data terdeteksi! Coba naikkan 'Toleransi Warna' atau pilih ulang warnanya.")
