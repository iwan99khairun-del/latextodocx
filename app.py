import streamlit as st

# --- 1. KONFIGURASI HALAMAN (Wajib di baris pertama setelah import) ---
st.set_page_config(
    page_title="Portal Pak Iwan",
    page_icon="👨‍🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. JUDUL ---
st.title("👨‍🏫 Portal Iwan Gunawan, PhD")
st.markdown("---")

# --- 3. PROFIL & AFILIASI ---
col1, col2 = st.columns([1, 2])

with col1:
    # Menggunakan try-except agar aplikasi tidak mati jika gambar gagal dimuat
    try:
        # Prioritaskan file lokal karena repo Bapak Private
        # Pastikan file 'sepeda.png' atau 'logo1.png' ada di folder utama GitHub
        st.image("sepeda.png", caption="Iwan Gunawan", width=250)
    except:
        # Jika file lokal tidak ada, gunakan URL cadangan
        st.image("https://brand.umpsa.edu.my/images/2024/02/28/logo-umpsa-full-color__4041x3027.png", width=200)

with col2:
    st.markdown("### Sepercik Harapan")
    st.write("**Afiliasi:**")
    st.markdown("* **Universitas Khairun**, Indonesia")
    st.markdown("* **Universiti Malaysia Pahang Al-Sultan Abdullah**")
    
     
    st.write("**Minat Penelitian:**")
    st.write("1. Combustion")
    st.write("2. Fluid Mechanics & Pumps")
    st.write("3. Drawing 3D")

# --- 4. INFO NAVIGASI ---
st.markdown("---")
st.subheader("📌 Navigasi Portal")
nav_col1, nav_col2, nav_col3 = st.columns(3)

with nav_col1:
    st.success("**📄 Konverter**\n\nLatex to Word & PDF")
with nav_col2:
    st.warning("**📚 Publikasi**\n\nList Jurnal & Conference")






