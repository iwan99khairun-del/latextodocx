import streamlit as st
import pypandoc
import os
import pandas as pd

# --- 1. PENGATURAN AWAL ---
PASSWORD_RAHASIA = "123123"  # Password

st.set_page_config(page_title="Portal Pak Iwan", page_icon="📝", layout="wide")

# Inisialisasi Login
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# --- 2. SIDEBAR NAVIGASI ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/iwan99khairun-del/latextodocx/main/logo1.png", use_container_width=True)
    st.title("Menu Utama")
    
    # Navigasi Halaman
    halaman = st.radio("Pilih Layanan:", 
        ["🏠 Profil Dosen", "📄 Konverter LaTeX", "📚 Materi & Riset"]
    )
    
    st.markdown("---")
    st.write("🔗 **Link Penting:**")
    st.markdown("[Masjid Al Muttaqin](https://masjid-almuttaqin-gamplong1.blogspot.com/)")
    st.markdown("[Universiti Malaysia Pahang](https://www.umpsa.edu.my)")
    
    st.markdown("---")
    st.write("📧 **Kontak:**")
    st.write("iwan99khairun@gmail.com")
    
    if st.session_state["authenticated"]:
        st.markdown("---")
        if st.button("Keluar / Logout"):
            st.session_state["authenticated"] = False
            st.rerun()

# --- 3. ISI HALAMAN ---

# === HALAMAN 1: PROFIL ===
if halaman == "🏠 Profil Dosen":
    st.title("👨‍🏫 Profil Dosen")
    st.markdown("### Iwan Gunawan, PhD")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=200)
    with col2:
        st.write("""
        **Afiliasi:**
        * Universitas Khairun, Indonesia
        * Universiti Malaysia Pahang Al-Sultan Abdullah
        
        **Bidang Minat:**
        * Electronics (Audio Amplifiers)
        * Fluid Mechanics & Thermodynamics
        * Programming & Web Development
        """)
    st.info("👋 Selamat datang! Silakan pilih menu di samping.")

# === HALAMAN 2: KONVERTER LATEX ===
elif halaman == "📄 Konverter LaTeX":
    if not st.session_state["authenticated"]:
        st.title("🔐 Akses Terbatas")
        st.write("Silakan masukkan password:")
        input_pass = st.text_input("Password:", type="password")
        if st.button("Buka Kunci"):
            if input_pass == PASSWORD_RAHASIA:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Password Salah!")
    else:
        st.title("📄 Konverter LaTeX ke Word")
        st.markdown("<h3 style='text-align: center; color: #555;'>By Iwan Gunawan, PhD</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666;'>Universiti Malaysia Pahang Al-Sultan Abdullah</p>", unsafe_allow_html=True)

        st.markdown("""
            <style>
            @keyframes kedip { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
            [data-testid='stFileUploader'] { background-color: white; border: 2px dashed #4CAF50; padding: 20px; border-radius: 10px; }
            [data-testid='stFileUploader'] button { background-color: #0066cc !important; color: white !important; }
            .identitas-bawah { font-size: 36px !important; font-weight: bold; color: #003366; text-align: center; margin-top: 20px; }
            .kampus-bawah { font-size: 24px; color: #555; text-align: center; margin-bottom: 30px; }
            .ayat-container { border: 2px solid #4CAF50; background-color: #f9fff9; padding: 20px; border-radius: 10px; text-align: center; margin-top: 30px; animation: kedip 2s infinite; }
            .arab { font-size: 32px; color: #006400; font-family: 'Traditional Arabic', serif; margin-bottom: 10px; }
            .terjemah { font-size: 16px; font-style: italic; color: #333; }
            </style>
        """, unsafe_allow_html=True)

        st.info("Silakan upload file .tex di bawah ini:")
        uploaded_file = st.file_uploader("", type="tex")

        if uploaded_file is not None:
            with open("input.tex", "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.write("⏳ Sedang memproses...")
