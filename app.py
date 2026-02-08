import streamlit as st

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Portal Pak Iwan",
    page_icon="👋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. JUDUL ---
st.title("👨‍🏫 Portal Iwan Gunawan, PhD")
st.markdown("---")

# --- 3. MEMBAGI KOLOM (FOTO & TEXT) ---
col1, col2 = st.columns([1, 2])

# --- BAGIAN FOTO (COL 1) ---
# Perhatikan: Baris st.image HARUS menjorok ke dalam
with col1:
    st.image("https://raw.githubusercontent.com/iwan99khairun-del/latextodocx/refs/heads/main/kampus.png", width=200)

# --- BAGIAN TEKS (COL 2) ---
# Perhatikan: Baris st.write HARUS menjorok ke dalam
with col2:
    st.write("""
    ### Sepercik Harapan
    **Afiliasi:**
    * **Universitas Khairun**, Indonesia
    * **Universiti Malaysia Pahang Al-Sultan Abdullah**

    ### Minat Penelitian
    1.  Combustion
    2.  Fluid Mechanics & Pumps
    3.  Drawing 3D
    """)

# --- 4. INFO NAVIGASI DI BAWAH ---
st.info("""
**👈 MENU NAVIGASI ADA DI KIRI**

Silakan pilih menu di sidebar samping untuk:
1.  **📄 Konverter**: Mengubah LaTeX ke Word.
2.  **📚 List Jurnal**: Melihat daftar referensi.
3.  **🏷️ Barcode**: Membuat barcode alat.
""")

st.write("📧 Kontak: iwan99khairun@gmail.com")

