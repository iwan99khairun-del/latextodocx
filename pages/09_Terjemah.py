# app.py
import streamlit as st
from deep_translator import GoogleTranslator
from docx import Document
import io

st.set_page_config(page_title="Penerjemah Dokumen", page_icon="🇮🇩")

st.title("🇮🇩 Penerjemah Dokumen (Indo -> Inggris) 🇬🇧")
st.write("Upload file .txt atau .docx Anda di bawah ini.")

def read_docx(file):
    doc = Document(file)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def translate_text(text):
    try:
        # Memotong teks jika terlalu panjang untuk menghindari error
        # Deep translator menghandle chunks otomatis, tapi untuk safety kita wrap try-except
        translator = GoogleTranslator(source='id', target='en')
        translated = translator.translate(text) 
        return translated
    except Exception as e:
        return f"Error: {e}"

uploaded_file = st.file_uploader("Pilih file", type=['txt', 'docx'])

if uploaded_file is not None:
    if uploaded_file.name.endswith('.txt'):
        text_input = uploaded_file.getvalue().decode("utf-8")
    elif uploaded_file.name.endswith('.docx'):
        text_input = read_docx(uploaded_file)
    
    st.subheader("Teks Asli:")
    st.text_area("Preview", text_input, height=150)

    if st.button("Terjemahkan Sekarang"):
        with st.spinner('Sedang menerjemahkan... (Mohon tunggu)'):
            hasil_terjemahan = translate_text(text_input)
            
            st.success("Selesai!")
            st.subheader("Hasil Terjemahan (Inggris):")
            st.text_area("Output", hasil_terjemahan, height=150)
            
            st.download_button(
                label="Download Hasil (.txt)",
                data=hasil_terjemahan,
                file_name="hasil_terjemahan.txt",
                mime="text/plain"
            )
