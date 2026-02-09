import streamlit as st
from deep_translator import GoogleTranslator
from docx import Document
import time

# --- Konfigurasi Halaman ---
st.set_page_config(page_title="Penerjemah Unlimited", layout="wide")

st.title("🇮🇩 Penerjemah Dokumen 'Unlimited' (Indo -> Inggris) 🇬🇧")
st.markdown("""
**Tips:** Aplikasi ini menggunakan mode **'Aman & Stabil'**. 
Prosesnya mungkin sedikit lebih pelan (ada jeda otomatis), tapi ini dilakukan agar Google tidak memblokir terjemahan dokumen panjang Anda.
""")

# --- Fungsi-Fungsi ---

def read_docx(file):
    doc = Document(file)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def translate_with_retry(text, chunk_index, total_chunks):
    """
    Fungsi ini mencoba menerjemahkan. Jika gagal, dia akan menunggu 5 detik
    lalu mencoba lagi otomatis.
    """
    translator = GoogleTranslator(source='id', target='en')
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            return translator.translate(text)
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(5) # Tunggu 5 detik kalau error, lalu coba lagi
                continue
            else:
                return f"[Gagal menerjemahkan bagian ini: {text[:50]}...]"

def process_translation(text):
    # Pecah teks menjadi potongan kecil (kurangi jadi 3000 biar lebih aman)
    chunk_size = 3000 
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    
    translated_chunks = []
    
    # Progress Bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total = len(chunks)
    
    for i, chunk in enumerate(chunks):
        # Update status
        percent = int(((i + 1) / total) * 100)
        status_text.text(f"Sedang memproses bagian {i+1} dari {total} ({percent}%)...")
        
        # PROSES TERJEMAHAN
        res = translate_with_retry(chunk, i, total)
        translated_chunks.append(res)
        
        # Update bar
        progress_bar.progress((i + 1) / total)
        
        # --- KUNCI ANTI-BLOKIR ---
        # Istirahat 2 detik setiap selesai 1 potongan
        time.sleep(2) 
            
    status_text.success("Selesai! Silakan download hasilnya.")
    return ' '.join(translated_chunks)

# --- Tampilan Utama ---

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Upload File")
    uploaded_file = st.file_uploader("Upload .txt atau .docx", type=['txt', 'docx'])

if uploaded_file is not None:
    # Baca File
    if uploaded_file.name.endswith('.txt'):
        text_input = uploaded_file.getvalue().decode("utf-8")
    elif uploaded_file.name.endswith('.docx'):
        text_input = read_docx(uploaded_file)
    
    with col1:
        st.info(f"Jumlah karakter: {len(text_input)}")
        st.text_area("Preview Asli", text_input, height=300)

    # Tombol Aksi
    with col2:
        st.subheader("2. Hasil Terjemahan")
        if st.button("Mulai Menerjemahkan (Mode Stabil)", type="primary"):
            if not text_input.strip():
                st.warning("File kosong.")
            else:
                result = process_translation(text_input)
                
                st.text_area("Preview Inggris", result, height=300)
                
                st.download_button(
                    label="📥 Download Hasil (.txt)",
                    data=result,
                    file_name="hasil_terjemahan_full.txt",
                    mime="text/plain"
                )
