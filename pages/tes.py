import streamlit as st
import rispy
import fitz  # PyMuPDF
import io
import google.generativeai as genai

# --- 1. KONFIGURASI API KEY ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("API Key belum disetting di Streamlit Secrets!")

# --- 2. FUNGSI BANTUAN ---

def extract_text_from_pdf(uploaded_file):
    text = ""
    try:
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        st.error(f"Gagal membaca PDF: {e}")
    return text

def format_references_for_prompt(ris_file):
    formatted_refs = []
    try:
        ris_text = io.TextIOWrapper(ris_file, encoding='utf-8')
        entries = rispy.load(ris_text)
        for entry in entries:
            authors = entry.get('authors', ['No Author'])
            year = entry.get('year', 'n.d.')
            title = entry.get('title', 'No Title')
            
            if len(authors) > 2:
                author_str = f"{authors[0]} et al."
            elif len(authors) == 2:
                author_str = f"{authors[0]} & {authors[1]}"
            else:
                author_str = authors[0]
            
            formatted_refs.append(f"- {author_str} ({year}). {title}")
    except Exception as e:
        st.error(f"Gagal membaca file RIS: {e}")
    return "\n".join(formatted_refs)

def get_gemini_response(prompt):
    """Mencoba model terbaru, jika gagal pakai model lama."""
    try:
        # Coba model Flash (Cepat & Bagus)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception:
        try:
            # Jika Flash gagal (karena versi lama), coba Pro
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"

# --- 3. APLIKASI UTAMA ---

st.title("Penulis Pendahuluan Otomatis 📝")

judul = st.text_input("Masukkan Judul Penelitian")
materi_pdf = st.file_uploader("Upload Materi (PDF)", type=["pdf"])
file_ris = st.file_uploader("Upload Referensi (RIS)", type=["ris"])
jumlah_sitasi = st.number_input("Jumlah sitasi", min_value=1, value=5)

if st.button("Buat Pendahuluan"):
    if judul and materi_pdf and file_ris:
        teks_materi = extract_text_from_pdf(materi_pdf)
        string_referensi = format_references_for_prompt(file_ris)
        
        if teks_materi and string_referensi:
            prompt = f"""
            Buatlah PENDAHULUAN jurnal ilmiah untuk judul: {judul}.
            
            Materi:
            {teks_materi[:4000]}
            
            Referensi (Wajib gunakan sitasi APA 7 untuk {jumlah_sitasi} sitasi):
            {string_referensi}
            """
            
            with st.spinner("AI sedang berpikir..."):
                hasil = get_gemini_response(prompt)
                
            if "Error:" in hasil:
                st.error(hasil)
                st.info("Tips: Pastikan file 'requirements.txt' sudah dibuat di GitHub.")
            else:
                st.success("Selesai!")
                st.text_area("Hasil", value=hasil, height=400)
                st.download_button("Download", data=hasil, file_name="Pendahuluan.txt")
    else:
        st.warning("Mohon lengkapi semua input.")
