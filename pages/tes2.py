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
        x_min_crop, x_max_crop = st.slider("Potong Kiri-Kanan (X)", 0, width_
