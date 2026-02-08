import streamlit as st
import pypandoc
import os

# --- 1. PENGATURAN AWAL ---
PASSWORD_RAHASIA = "123123"  # Password Bapak

st.set_page_config(page_title="Portal Pak Iwan", page_icon="📝", layout="wide")

# Inisialisasi status login
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# --- 2. SIDEBAR (MENU NAVIGASI KIRI) ---
with st.sidebar:
    # LOGO
    st.image("https://raw.githubusercontent.com/iwan99khairun-del/latextodocx/main/logo1.png", use_container_width=True)
    
    st.title("Menu Utama")
    
    # PILIHAN HALAMAN (Ini kuncinya agar jadi seperti template)
    halaman = st.radio("Pilih Layanan:", 
        ["🏠 Profil Dosen", "📄 Konverter LaTeX", "📚 Materi & Riset"]
    )
    
    st.markdown("---")
    
    # LINK PENTING
    st.write("🔗 **Link Penting:**")
    st.markdown("[Masjid Al Muttaqin](https://masjid-almuttaqin-gamplong1.blogspot.com/)")
    st.markdown("[Universiti Malaysia Pahang](https://www.umpsa.edu.my)")
    
    st.markdown("---")
    st.write("📧 **Kontak:**")
    st.write("iwan99khairun@gmail.com")
    
    # TOMBOL LOGOUT (Hanya muncul jika sedang login)
    if st.session_state["authenticated"]:
        st.markdown("---")
        if st.button("Keluar / Logout"):
            st.session_state["authenticated"] = False
            st.rerun()

# --- 3. LOGIKA PINDAH HALAMAN ---

# === HALAMAN 1: PROFIL DOSEN (Tanpa Password) ===
if halaman == "🏠 Profil Dosen":
    st.title("👨‍🏫 Profil Dosen")
    st.markdown("### Iwan Gunawan, PhD")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        # Bapak bisa ganti link gambar ini dengan foto profil Bapak
        st.image("https://cdn-icons-png.fl
