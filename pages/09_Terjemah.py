import streamlit as st
from deep_translator import GoogleTranslator
from docx import Document

# Judul Halaman
st.title("🇮🇩 Penerjemah Dokumen (Indo -> Inggris) 🇬🇧")
st.write("Upload file .txt atau .docx. (Mendukung file panjang)")

# Fungsi Membaca Docx
def read_docx(file):
    doc = Document(file)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

# Fungsi Memecah Teks (Chunking) & Menerjemahkan
def translate_long_text(text):
    translator = GoogleTranslator(source='id', target='en')
    
    # 1. Pecah teks menjadi potongan max 4500 karakter (aman di bawah batas 5000)
    chunk_size = 4500
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    
    translated_chunks = []
    
    # Baris progress (agar user tahu proses berjalan)
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # 2. Terjemahkan per potongan
    for i, chunk in enumerate(chunks):
        status_text.text(f"Menerjemahkan bagian {i+1} dari {len(chunks)}...")
        try:
            # Terjemahkan potongan ini
            res = translator.translate(chunk)
            translated_chunks.append(res)
        except Exception as e:
            # Jika error, biarkan teks asli dan catat error
            translated_chunks.append(chunk)
            st.warning(f"Bagian {i+1} gagal diterjemahkan: {e}")
        
        # Update progress bar
        progress_bar.progress((i + 1) / len(chunks))
            
    status_text.text("Selesai!")
    progress_bar.empty() # Hilangkan bar setelah selesai
    
    # 3. Gabungkan kembali
    return ' '.join(translated_chunks)

# --- Tampilan Utama ---
uploaded_file = st.file_uploader("Pilih file", type=['txt', 'docx'])

if uploaded_file is not None:
    # Proses baca file
    if uploaded_file.name.endswith('.txt'):
        text_input = uploaded_file.getvalue().decode("utf-8")
    elif uploaded_file.name.endswith('.docx'):
        text_input = read_docx(uploaded_file)
    
    st.subheader("Teks Asli (Preview):")
    st.text_area("Indo", text_input, height=150)

    if st.button("Terjemahkan Sekarang"):
        # Cek apakah teks kosong
        if not text_input.strip():
            st.warning("File kosong, tidak ada teks yang bisa diterjemahkan.")
        else:
            with st.spinner('Sedang memproses dokumen panjang...'):
                hasil_terjemahan = translate_long_text(text_input)
                
                st.success("Selesai!")
                st.subheader("Hasil Terjemahan (Inggris):")
                st.text_area("Output", hasil_terjemahan, height=300)
                
                st.download_button(
                    label="Download Hasil (.txt)",
                    data=hasil_terjemahan,
                    file_name="hasil_terjemahan_inggris.txt",
                    mime="text/plain"
                )
