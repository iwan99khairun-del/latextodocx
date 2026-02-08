import streamlit as st
import pypandoc
import os

st.set_page_config(page_title="Konverter LaTeX", page_icon="📄")

PASSWORD_RAHASIA = "123123"

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔐 Akses Terbatas")
    st.write("Silakan masukkan password untuk konversi:")
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
                st.download_button(label="📥 DOWNLOAD FILE WORD (.DOCX)", data=file, file_name=uploaded_file.name.replace('.tex', '.docx'), mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            st.markdown("<hr><h3 style='text-align: center;'>Universiti Malaysia Pahang Al-Sultan Abdullah</h3>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Gagal Konversi: {e}")
            
    if st.button("Logout"):
        st.session_state["authenticated"] = False
        st.rerun()
