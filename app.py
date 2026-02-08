import streamlit as st

st.set_page_config(page_title="Portal Akademik", page_icon="🏠", layout="wide")

# Sidebar otomatis untuk logo & link
with st.sidebar:
    st.image("https://raw.githubusercontent.com/iwan99khairun-del/latextodocx/main/logo1.png", use_container_width=True)
    st.write("🔗 **Link Penting:**")
    st.markdown("[Masjid Al Muttaqin](https://masjid-almuttaqin-gamplong1.blogspot.com/)")
    st.markdown("[Universiti Malaysia Pahang](https://www.umpsa.edu.my)")

# Isi Halaman Beranda
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

st.info("👈 Silakan pilih menu di sebelah kiri untuk menggunakan Konverter atau melihat daftar Jurnal.")
