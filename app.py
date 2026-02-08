import streamlit as st
import pypandoc
import os

# --- 1. PENGATURAN PASSWORD ---
PASSWORD_RAHASIA = "iwan123"  # Silakan ganti password ini sesuai keinginan Bapak

st.set_page_config(page_title="Konverter Pak Iwan", page_icon="📝")

# Inisialisasi status login
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
# --- MENAMBAH SIDEBAR DI SISI KIRI ---
with st.sidebar:
    # --- MENAMBAH LOGO DI ATAS SIDEBAR ---
    # Ganti link di bawah dengan link gambar logo Bapak atau kampus
    st.sidebar.image("https://raw.githubusercontent.com/iwan99khairun-del/latextodocx/main/logo1.png", use_container_width=True)

with st.sidebar:
    st.title("Menu Navigasi")
    # ... kode sidebar lainnya ...
   
    st.markdown("---")
    
    # Menambahkan Link Teks
    st.write("🔗 **Link Penting:**")
    st.markdown("[Masjid Al Muttaqin](https://masjid-almuttaqin-gamplong1.blogspot.com/)") # Ganti dengan link Bapak
    st.markdown("[Universiti Malaysia Pahang](https://www.umpsa.edu.my)")
    
    st.markdown("---")
    st.write("📧 **Kontak:**")
    st.write("iwan99khairun@gmail.com") # Sesuaikan email Bapak
    
    st.markdown("---")
    st.info("Alat ini digunakan untuk membantu mahasiswa mengonversi tugas LaTeX ke format Word (.docx).")

# --- 2. TAMPILAN HALAMAN LOGIN ---
if not st.session_state["authenticated"]:
    st.title("🔐 Akses Terbatas")
    st.markdown("### Alat Konversi LaTeX - Docx")
    st.markdown("### by Iwan Gunawan, PhD")
    st.markdown("### Universiti Malaysia Al sultan Abdullah")
    input_password = st.text_input("Masukkan Password:", type="password")
    
    if st.button("Masuk"):
        if input_password == PASSWORD_RAHASIA:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Password Salah! Silakan hubungi Iwan Gunawan, PhD.")
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Created by: Iwan Gunawan, PhD</h3>", unsafe_allow_html=True)
    st.stop()  # Berhenti di sini jika belum login

# --- 3. TAMPILAN UTAMA (HANYA MUNCUL JIKA PASSWORD BENAR) ---

# Tampilan Judul dan Nama Bapak di Atas
st.title("📄 Konverter LaTeX ke Word")
st.markdown("<h3 style='text-align: center; color: #555;'>By Iwan Gunawan, PhD</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>Universiti Malaysia Pahang Al-Sultan Abdullah</p>", unsafe_allow_html=True)

# CSS untuk mempercantik area upload dan ayat
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

st.info("Tombol upload ada di dalam kotak garis putus-putus di bawah ini:")

# Tombol Upload
uploaded_file = st.file_uploader("Upload File .tex Disini", type="tex")

if uploaded_file is not None:
    with open("input.tex", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.write("⏳ Sedang memproses...")
    
    try:
        output_filename = "hasil_konversi.docx"
        pypandoc.convert_file("input.tex", 'docx', outputfile=output_filename, extra_args=['--mathml'])
        
        st.success("✅ BERHASIL! Silakan download:")
        
        with open(output_filename, "rb") as file:
            st.download_button(
                label="📥 DOWNLOAD FILE WORD (.DOCX)",
                data=file,
                file_name=uploaded_file.name.replace('.tex', '.docx'),
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        
        # Bagian Bawah: Identitas Besar dan Ayat Al-Quran Berkedip
        st.markdown("""
            <hr>
            <div class="identitas-bawah">Created by: Iwan Gunawan, PhD</div>
            <div class="kampus-bawah">Universiti Malaysia Pahang Al-Sultan Abdullah</div>
            <div class="ayat-container">
                <div class="arab">وَأَقِيمُوا الصَّلَاةَ وَآَتُوا الزَّكَاةَ وَأَطِيعُوا الرَّسُولَ لَعَلَّكُمْ تُرْحَمُونَ</div>
                <div class="terjemah">“Dan dirikanlah shalat, tunaikanlah zakat, dan ta’atlah kepada rasul,<br>
                supaya kamu diberi rahmat.” (QS. An Nur [24] : 56)</div>
            </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Gagal Konversi: {e}")

# Tombol Logout (Opsional)
if st.sidebar.button("Keluar / Logout"):
    st.session_state["authenticated"] = False
    st.rerun()















