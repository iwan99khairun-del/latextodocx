import streamlit as st
import pypandoc
import os
import pandas as pd  # Kita butuh ini untuk membuat Tabel

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
    
    # PILIHAN HALAMAN
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
    
    # TOMBOL LOGOUT
    if st.session_state["authenticated"]:
        st.markdown("---")
        if st.button("Keluar / Logout"):
            st.session_state["authenticated"] = False
            st.rerun()

# --- 3. LOGIKA PINDAH HALAMAN ---

# === HALAMAN 1: PROFIL DOSEN ===
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

# === HALAMAN 2: KONVERTER LATEX (PAKAI PASSWORD) ===
elif halaman == "📄 Konverter LaTeX":
    
    if not st.session_state["authenticated"]:
        st.title("🔐 Akses Terbatas")
        st.markdown("### Area Khusus Mahasiswa")
        st.write("Silakan masukkan password untuk menggunakan alat konversi.")
        
        input_pass = st.text_input("Password:", type="password")
        if st.button("Buka Kunci"):
            if input_pass == PASSWORD_RAHASIA:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Password Salah!")
    
    else:
        # KODE KONVERTER BAPAK
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


# === HALAMAN 3: MATERI & RISET (Isi Data Jurnal) ===
elif halaman == "📚 Materi & Riset":
    st.title("📚 Daftar Referensi Jurnal")
    st.write("Berikut adalah daftar jurnal terindeks SINTA & Scopus yang direkomendasikan:")

    # 1. INPUT DATA (Bisa Bapak tambah terus ke bawah)
    # 1. INPUT DATA JURNAL (UPDATE TERBARU: 20 JURNAL)
    data_jurnal = [
        # --- LEVEL INTERNASIONAL / SCOPUS (SINTA 1) ---
        {"No": 1, "Jurnal": "International Journal of Technology (IJTech)", "Index": "SINTA 1 (SCOPUS Q2)", "Penerbit": "Universitas Indonesia", "Link": "https://ijtech.eng.ui.ac.id/"},
        {"No": 2, "Jurnal": "Indonesian Journal of Science and Technology (IJoST)", "Index": "SINTA 1 (SCOPUS Q1)", "Penerbit": "UPI Bandung", "Link": "https://ejournal.upi.edu/index.php/ijost/"},
        {"No": 3, "Jurnal": "Telkomnika (Telecommunication Computing Electronics and Control)", "Index": "SINTA 1 (SCOPUS Q2)", "Penerbit": "Univ. Ahmad Dahlan", "Link": "http://journal.uad.ac.id/index.php/TELKOMNIKA"},
        {"No": 4, "Jurnal": "Automotive Experiences", "Index": "SINTA 1 (SCOPUS Q2)", "Penerbit": "Univ. Muhammadiyah Magelang", "Link": "https://journal.unimma.ac.id/index.php/automotive"},
        {"No": 5, "Jurnal": "Journal of Engineering and Technological Sciences", "Index": "SINTA 1 (SCOPUS Q3)", "Penerbit": "ITB", "Link": "https://journals.itb.ac.id/index.php/jets"},
        {"No": 6, "Jurnal": "International Journal of Electrical and Computer Engineering (IJECE)", "Index": "SINTA 1 (SCOPUS Q2)", "Penerbit": "IAES Institute", "Link": "http://ijece.iaescore.com/"},
        {"No": 7, "Jurnal": "Bulletin of Electrical Engineering and Informatics (BEEI)", "Index": "SINTA 1 (SCOPUS Q3)", "Penerbit": "Univ. Ahmad Dahlan", "Link": "http://beei.org/"},
        {"No": 8, "Jurnal": "Makara Journal of Technology", "Index": "SINTA 1 (SCOPUS Q4)", "Penerbit": "Universitas Indonesia", "Link": "https://scholarhub.ui.ac.id/mjt/"},
        {"No": 9, "Jurnal": "EMITTER International Journal of Engineering Technology", "Index": "SINTA 1 (SCOPUS)", "Penerbit": "PENS Surabaya", "Link": "https://emitter.pens.ac.id/index.php/emitter"},
        {"No": 10, "Jurnal": "Journal of Mechatronics, Electrical Power, and Vehicular Technology (MEV)", "Index": "SINTA 1 (SCOPUS)", "Penerbit": "BRIN (LIPI)", "Link": "https://mevjournal.com/index.php/mev"},

        # --- LEVEL NASIONAL TERAKREDITASI (SINTA 2) ---
        {"No": 11, "Jurnal": "Jurnal Nasional Teknik Elektro dan Teknologi Informasi (JNTETI)", "Index": "SINTA 2", "Penerbit": "UGM", "Link": "https://jurnal.ugm.ac.id/v3/JNTETI"},
        {"No": 12, "Jurnal": "Jurnal Elektronika dan Telekomunikasi", "Index": "SINTA 2", "Penerbit": "BRIN (LIPI)", "Link": "https://www.jurnalet.com/jet"},
        {"No": 13, "Jurnal": "Jurnal Rekayasa Mesin", "Index": "SINTA 2", "Penerbit": "Universitas Brawijaya", "Link": "https://jrm.ub.ac.id/"},
        {"No": 14, "Jurnal": "Jurnal Ilmiah Teknik Elektro Komputer dan Informatika (JITEKI)", "Index": "SINTA 2", "Penerbit": "Univ. Ahmad Dahlan", "Link": "http://journal.uad.ac.id/index.php/JITEKI"},
        {"No": 15, "Jurnal": "ELKOMIKA: Jurnal Teknik Energi Elektrik, Telekomunikasi, & Elektronika", "Index": "SINTA 2", "Penerbit": "Itenas", "Link": "https://ejurnal.itenas.ac.id/index.php/elkomika"},
        {"No": 16, "Jurnal": "Jurnal Teknologi dan Sistem Komputer", "Index": "SINTA 2", "Penerbit": "Universitas Diponegoro", "Link": "https://jtsiskom.undip.ac.id/"},
        {"No": 17, "Jurnal": "Jurnal RESTI (Rekayasa Sistem dan Teknologi Informasi)", "Index": "SINTA 2", "Penerbit": "Politeknik Negeri Padang", "Link": "http://jurnal.iaii.or.id/index.php/RESTI"},
        {"No": 18, "Jurnal": "IPTEK The Journal for Technology and Science", "Index": "SINTA 1", "Penerbit": "ITS Surabaya", "Link": "https://iptek.its.ac.id/index.php/jts"},
        {"No": 19, "Jurnal": "Register: Jurnal Ilmiah Teknologi Sistem Informasi", "Index": "SINTA 2", "Penerbit": "Unipdu Jombang", "Link": "https://journal.unipdu.ac.id/index.php/register"},
        {"No": 20, "Jurnal": "Jurnal Pendidikan Teknologi dan Kejuruan", "Index": "SINTA 2", "Penerbit": "UNY", "Link": "https://journal.uny.ac.id/index.php/jptk"},
    ]
    ]

    # 2. MEMBUAT DATAFRAME (TABEL)
    df = pd.DataFrame(data_jurnal)

    # 3. TAMPILKAN TABEL DI WEBSITE
    st.dataframe(
        df,
        column_config={
            "Link": st.column_config.LinkColumn("Website Jurnal"), # Agar link bisa diklik
        },
        hide_index=True,
        use_container_width=True
    )

    # 4. TOMBOL DOWNLOAD EXCEL/CSV
    st.markdown("---")
    st.write("📥 **Unduh Data:**")
    
    # Kita ubah jadi CSV agar ringan & cepat di download
    csv = df.to_csv(index=False).encode('utf-8')
    
    st.download_button(
        label="Download Daftar Jurnal (CSV)",
        data=csv,
        file_name='Daftar_Jurnal_Pak_Iwan.csv',
        mime='text/csv',
    )

