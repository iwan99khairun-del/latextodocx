import streamlit as st
import pypandoc
import os

# --- 1. PENGATURAN AWAL & PASSWORD ---
PASSWORD_RAHASIA = "iwan123" 

st.set_page_config(page_title="Portal Pak Iwan", page_icon="📝", layout="wide")

# Inisialisasi status login
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# --- 2. SIDEBAR (MENU NAVIGASI) ---
with st.sidebar:
    # Logo Kampus/Pribadi
    st.image("https://raw.githubusercontent.com/iwan99khairun-del/latextodocx/main/logo1.png", use_container_width=True)
    
    st.title("Main Menu")
    # Membuat pilihan halaman seperti template
    pilihan_halaman = st.radio("Pilih Layanan:", ["🏠 Beranda / Profil", "📄 Konverter LaTeX", "📚 Materi & Riset"])
    
    st.markdown("---")
    st.write("📧 **Kontak:**")
    st.write("iwan99khairun@gmail.com")
    
    if st.session_state["authenticated"]:
        if st.sidebar.button("Keluar / Logout"):
            st.session_state["authenticated"] = False
            st.rerun()

# --- 3. LOGIKA HALAMAN ---

# --- HALAMAN 1: BERANDA / PROFIL (Tanpa Password) ---
if pilihan_halaman == "🏠 Beranda / Profil":
    st.title("👨‍🏫 Profil Dosen")
    st.write("### Iwan Gunawan, PhD")
    st.write("Affiliation:")
    st.write("- **Universitas Khairun**, Indonesia")
    st.write("- **Universiti Malaysia Pahang Al-Sultan Abdullah**")
    
    st.info("Selamat datang di portal akademik saya. Silakan pilih menu di samping untuk menggunakan alat konverter.")

# --- HALAMAN 2: KONVERTER (Pakai Password) ---
elif pilihan_halaman == "📄 Konverter LaTeX":
    if not st.session_state["authenticated"]:
        st.title("🔐 Akses Terbatas")
        input_password = st.text_input("Masukkan Password Konverter:", type="password")
        if st.button("Masuk"):
            if input_password == PASSWORD_RAHASIA:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Password Salah!")
    else:
        st.title("📄 Konverter LaTeX ke Word")
        # --- Masukkan Kode Konverter Bapak yang Sudah Jadi di Sini ---
        uploaded_file = st.file_uploader("Upload File .tex Disini", type="tex")
        if uploaded_file:
            st.success("File siap dikonversi!")
            # (Tambahkan logika pypandoc Bapak di sini)

# --- HALAMAN 3: MATERI & RISET (Tanpa Password) ---
elif pilihan_halaman == "📚 Materi & Riset":
    st.title("📚 Publikasi & Riset")
    st.write("Penelitian terbaru saya mengenai:")
    st.write("- *Effect Of Liquid Additives on Diesel Engine Performance*")
    st.markdown("[Lihat di Google Scholar](https://scholar.google.com)")
