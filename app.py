import streamlit as st

st.set_page_config(
    page_title="Portal Pak Iwan",
    page_icon="👋",
    layout="wide",
    initial_sidebar_state="expanded"  # <--- INI TAMBAHAN PENTINGNYA
)


st.title("👨‍🏫 Portal Iwan Gunawan, PhD")
st.markdown("---")

col1, col2 = st.columns([1, 2])

with col1:
    # Ganti dengan link foto Bapak jika ada
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=200)

with col2:
    st.write("""
    ### Tentang Saya
    Saya adalah dosen dan peneliti dengan afiliasi di:
    * **Universitas Khairun**, Indonesia
    * **Universiti Malaysia Pahang Al-Sultan Abdullah**

    ### Minat Penelitian
    1.  Electronics (Audio Amplifiers)
    2.  Fluid Mechanics & Thermodynamics
    3.  Programming & Web Development
    """)

st.info("""
**👈 SILAKAN LIHAT MENU DI KIRI LAYAR**
# --- MENAMBAH LOGO DI ATAS SIDEBAR ---
    # Ganti link di bawah dengan link gambar logo Bapak atau kampus
    st.sidebar.image("https://raw.githubusercontent.com/iwan99khairun-del/latextodocx/main/logo1.png", use_container_width=True)
Gunakan menu di samping (klik tanda panah '>' di pojok kiri atas jika di HP) untuk membuka:
1.  **📄 Konverter**: Untuk mengubah file LaTeX ke Word.
2.  **📚 Materi**: Untuk melihat daftar referensi jurnal.
""")

st.write("📧 Kontak: iwan99khairun@gmail.com")



