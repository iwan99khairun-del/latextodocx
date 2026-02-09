import streamlit as st
import rispy
import pymupdf  # atau fitz

st.title("Penulis Pendahuluan Otomatis 📝")

# 1. Input Judul
judul = st.text_input("Masukkan Judul Penelitian")

# 2. Upload File PDF
materi_pdf = st.file_uploader("Upload Materi (PDF)", type=["pdf"])

# 3. Upload File RIS
file_ris = st.file_uploader("Upload Referensi (RIS)", type=["ris"])

# 4. Pilih Jumlah Sitasi
jumlah_sitasi = st.number_input("Jumlah sitasi yang diinginkan", min_value=1, max_value=20, value=5)

# Tombol untuk proses
if st.button("Buat Pendahuluan"):
    if judul and materi_pdf and file_ris:
        st.info("Sedang memproses... (Logika AI akan ditaruh di sini)")
        # Di sini nanti kita masukkan kode untuk baca RIS dan kirim ke AI
    else:
        st.warning("Mohon lengkapi semua input ya!")
