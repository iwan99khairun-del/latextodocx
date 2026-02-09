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

# Layout atas
col_intro, col_upload = st.columns([1, 2])
with col_intro:
    st.markdown("""
    **Cara Pakai:**
    1. Upload Gambar.
    2. **CROP (Potong)** gambar sampai angka/tulisan hilang.
    3. Pilih Warna & Download.
    """)
with col_upload:
    uploaded_file = st.file_uploader("Upload Gambar Grafik (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image_pil = Image.open(uploaded_file).convert('RGB')
    img_array = np.array(image_pil)
    height_ori, width_ori, _ = img_array.shape

    # --- SIDEBAR ---
    with st.sidebar:
        st.header("🔧 Pengaturan")
        
        st.subheader("1. Tipe Grafik")
        chart_type = st.radio("Pilih:", ["Garis (Line)", "Batang (Bar)"])
        
        st.subheader("2. Kalibrasi Sumbu")
        col1, col2 = st.columns(2)
        x_min = col1.number_input("X Min", value=0.0)
        x_max = col2.number_input("X Max", value=100.0)
        y_min = col1.number_input("Y Min", value=0.0)
        y_max = col2.number_input("Y Max", value=100.0)

        st.subheader("3. Deteksi Warna")
        target_color = st.color_picker("Pilih Warna", "#FF9900") 
        # Range toleransi saya perbesar default-nya
        tolerance = st.slider("Sensitivitas Warna", 10, 180, 60)

    # --- MAIN AREA ---
    col_crop, col_result = st.columns([1, 1])

    with col_crop:
        st.subheader("✂️ 1. POTONG (CROP)")
        st.warning("Geser slider sampai angka sumbu & judul HILANG!")
        
        y_crop = st.slider("Potong Atas-Bawah", 0, height_ori, (0, height_ori))
        x_crop = st.slider("Potong Kiri-Kanan", 0, width_ori, (0, width_ori))
        
        cropped_img = img_array[y_crop[0]:y_crop[1], x_crop[0]:x_crop[1]]
        st.image(cropped_img, caption=f"Area Bersih ({cropped_img.shape[1]}x{cropped_img.shape[0]} px)")
        h_crop, w_crop, _ = cropped_img.shape

    with col_result:
        st.subheader("👀 2. HASIL DETEKSI")
        
        # Proses Warna yang Diperbaiki
        hsv_img = cv2.cvtColor(cropped_img, cv2.COLOR_RGB2HSV)
        target_hsv = hex_to_hsv(target_color)

        # Logika range warna lebih agresif menangkap variasi kecerahan
        lower = np.array([max(0, target_hsv[0] - tolerance), 30, 30])
        upper = np.array([min(179, target_hsv[0] + tolerance), 255, 255])
        
        mask = cv2.inRange(hsv_img, lower, upper)
        
        # VISUALISASI YANG LEBIH BAGUS (Overlay Hijau di atas gambar asli)
        # Bikin gambar background jadi agak gelap biar kontras
        dimmed_img = (cropped_img * 0.5).astype(np.uint8)
        # Bikin layer hijau
        green_layer = np.zeros_like(cropped_img)
        green_layer[:] = [0, 255, 0] # Warna Hijau Neon
        # Gabungkan: Gambar gelap + (Layer Hijau yg dimasking)
        result_viz = np.where(mask[:, :, None] > 0, green_layer, dimmed_img)
        # Campur sedikit dengan gambar asli biar transparan
        final_viz = cv2.addWeighted(cropped_img, 0.3, result_viz, 0.7, 0)

        st.image(final_viz, caption="Area Hijau = Data Terambil", clamp=True)

        # Hitung Data
        ys, xs = np.where(mask > 0)
        
        if len(xs) > 0:
            df_pixel = pd.DataFrame({'px_x': xs, 'px_y': ys})
            
            if chart_type == "Batang (Bar)":
                # Ambil titik teratas (Y minimum pixel)
                df_grouped = df_pixel.groupby('px_x')['px_y'].min().reset_index()
            else:
                # Ambil titik tengah
                df_grouped = df_pixel.groupby('px_x')['px_y'].mean().reset_index()

            # Konversi
            df_grouped['Data_X'] = x_min + (df_grouped['px_x'] / w_crop) * (x_max - x_min)
            df_grouped['Data_Y'] = y_min + ((h_crop - df_grouped['px_y']) / h_crop) * (y_max - y_min)
            
            final_df = df_grouped[['Data_X', 'Data_Y']].sort_values(by='Data_X')
            
            st.success(f"✅ Oke! {len(final_df)} titik ditemukan.")
            
            # Download
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                final_df.to_excel(writer, index=False)
            
            st.download_button(
                "📥 DOWNLOAD EXCEL",
                data=output.getvalue(),
                file_name="data_grafik.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )
        else:
            st.error("⚠️ Masih kosong? Coba naikkan 'Sensitivitas Warna' atau pilih ulang warnanya.")
