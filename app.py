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
    st.image("https://github.com/iwan99khairun-del/latextodocx/blob/main/sepeda.png", width=200)

with col2:
    st.write("""
    ### Sepercik Harapan
   Affiliasi:
    * **Universitas Khairun**, Indonesia
    * **Universiti Malaysia Pahang Al-Sultan Abdullah**

    ### Minat Penelitian
    1.  Combustion
    2.  Fluid Mechanics & Pumps
    3.  Drawing 3D
    """)

st.info("""
**👈 SILAKAN LIHAT MENU DI KIRI LAYAR**

Gunakan menu di samping (klik tanda panah '>' di pojok kiri atas jika di HP) untuk membuka:
1.  **📄 Konverter**: Untuk mengubah file LaTeX ke Word.
2.  **📚 List Jurnal**: Untuk melihat daftar referensi jurnal.
""")

st.write("📧 Kontak: infak")










