# --- 1. PERSIAPAN SISTEM ---
import os
import urllib.request

# Hapus pengaturan tema lama agar tidak bentrok
if os.path.exists(".streamlit/config.toml"):
    os.remove(".streamlit/config.toml")

print("1. Menyiapkan sistem...")
os.system("pip install streamlit pypandoc > /dev/null")
os.system("sudo apt-get install pandoc > /dev/null")
os.system("npm install -g localtunnel > /dev/null") 

# --- 2. MEMBUAT APLIKASI DENGAN TOMBOL BIRU ---
isi_kode_app = r'''
import streamlit as st
import pypandoc
import os

st.set_page_config(page_title="Konverter Pak Iwan", page_icon="📝")

# --- CSS KHUSUS: MEMAKSA TOMBOL UPLOAD JADI BIRU ---
st.markdown("""
    <style>
    /* 1. Paksa area upload berwarna putih dengan garis hijau */
    [data-testid='stFileUploader'] {
        background-color: white;
        border: 2px dashed #4CAF50;
        padding: 20px;
        border-radius: 10px;
    }
    
    /* 2. Paksa TOMBOL 'Browse files' menjadi BIRU dan Teks PUTIH */
    [data-testid='stFileUploader'] button {
        background-color: #0066cc !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        padding: 10px 20px !important;
    }
    
    /* Style lainnya (Nama & Kedip) */
    @keyframes kedip { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    .identitas { font-size: 36px !important; font-weight: bold; color: #003366; text-align: center; margin-top: 20px; font-family: Arial, sans-serif; }
    .kampus { font-size: 24px; color: #555; text-align: center; margin-bottom: 30px; }
    .ayat-container { border: 2px solid #4CAF50; background-color: #f9fff9; padding: 20px; border-radius: 10px; text-align: center; margin-top: 30px; animation: kedip 2s infinite; }
    .arab { font-size: 32px; color: #006400; font-family: 'Traditional Arabic', serif; margin-bottom: 10px; }
    .terjemah { font-size: 16px; font-style: italic; color: #333; }
    </style>
""", unsafe_allow_html=True)

st.title("📄 Konverter LaTeX ke Word")
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
        
        st.markdown("""
            <hr>
            <div class="identitas">Created by: Iwan Gunawan, PhD</div>
            <div class="kampus">Universiti Malaysia Pahang Al-Sultan Abdullah</div>
            <div class="ayat-container">
                <div class="arab">وَأَقِيمُوا الصَّلَاةَ وَآَتُوا الزَّكَاةَ وَأَطِيعُوا الرَّسُولَ لَعَلَّكُمْ تُرْحَمُونَ</div>
                <div class="terjemah">“Dan dirikanlah shalat, tunaikanlah zakat, dan ta’atlah kepada rasul,<br>supaya kamu diberi rahmat.” (QS. An Nur [24] : 56)</div>
            </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Gagal: {e}")
'''

with open("app.py", "w") as f:
    f.write(isi_kode_app)

# --- 3. JALANKAN ---
print("="*50)
print("✅ SIAP. Klik link di bawah dan masukkan password.")
print("="*50)
ip_address = urllib.request.urlopen('https://ipv4.icanhazip.com').read().decode('utf8').strip("\n")
print(f"PASSWORD:  {ip_address}")
print("-" * 20)
print("Tunggu sebentar sampai muncul link 'your url is: ...'")
print("="*50)

# Kita gunakan tema 'light' bawaan streamlit lewat perintah ini
!streamlit run app.py --theme.base="light" & lt --port 8501