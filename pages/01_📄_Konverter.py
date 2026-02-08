import streamlit as st
import pypandoc
import os

# --- KONFIGURASI ---
st.set_page_config(page_title="Konverter LaTeX", page_icon="📄")

# --- PASSWORD ---
PASSWORD_RAHASIA = "123123"

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# --- LOGIKA LOGIN ---
if not st.session_state["authenticated"]:
    st.title("🔐 Akses Terbatas")
    st.info("Masukkan password untuk menggunakan konverter.")
    input_pass = st.text_input("Password:", type="password")
    
    if st.button("Masuk"):
        if input_pass == PASSWORD_RAHASIA:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Password Salah!")
else:
    # --- ISI KONVERTER ---
    st.title("📄 Konverter LaTeX ke Word")
    st.markdown("### Upload file .tex Bapak di sini")
    
    # CSS agar tombol upload lebih bagus
    st.markdown("""
        <style>
        [data-testid='stFileUploader'] { background-color: #f0f2f6; padding: 20px; border-radius: 10px; }
        </style>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("", type="tex")

    if uploaded_file is not None:
        with open("input.tex", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.write("⏳ File terbaca...")
        
        if st.button("Mulai Konversi"):
            try:
                output_filename = "hasil.docx"
                pypandoc.convert_file("input.tex", 'docx', outputfile=output_filename, extra_args=['--mathml'])
                
                with open(output_filename, "rb") as file:
                    st.download_button(
                        label="📥 DOWNLOAD HASIL WORD",
                        data=file,
                        file_name=uploaded_file.name.replace('.tex', '.docx'),
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                st.success("Selesai! Silakan download.")
            except Exception as e:
                st.error(f"Error: {e}")
