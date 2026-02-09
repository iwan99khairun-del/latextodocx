import streamlit as st
import rispy
import fitz  # PyMuPDF
import io
import google.generativeai as genai

# --- KONFIGURASI API KEY ---
# Masukkan API Key Google Gemini Anda di sini
# Dapatkan gratis di: https://aistudio.google.com/app/apikey
API_KEY = ".PO6M Gemini API Key" 
genai.configure(api_key=API_KEY)

# --- FUNGSI BANTUAN ---

def extract_text_from_pdf(uploaded_file):
    """Mengekstrak teks dari file PDF yang diupload."""
    text = ""
    try:
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        st.error(f"Gagal membaca PDF: {e}")
    return text

def format_references_for_prompt(ris_file):
    """Membaca file RIS dan mengubahnya menjadi format list string untuk AI."""
    formatted_refs = []
    try:
        # Streamlit mengembalikan bytes, rispy butuh text. Kita decode dulu.
        ris_text = io.TextIOWrapper(ris_file, encoding='utf-8')
        entries = rispy.load(ris_text)
        
        for entry in entries:
            # Ambil data penting untuk sitasi APA
            authors = entry.get('authors', ['No Author'])
            year = entry.get('year', 'n.d.')
            title = entry.get('title', 'No Title')
            
            # Format penulis: "Smith, J." atau "Smith et al."
            if len(authors) > 2:
                author_str = f"{authors[0]} et al."
            elif len(authors) == 2:
                author_str = f"{authors[0]} & {authors[1]}"
            else:
                author_str = authors[0]
            
            # Format baris untuk dibaca AI
            # Contoh: [1] Smith et al. (2023). Judul Jurnal.
            ref_str = f"- {author_str} ({year}). {title}"
            formatted_refs.append(ref_str)
            
    except Exception as e:
        st.error(f"Gagal membaca file RIS: {e}")
    
    return "\n".join(formatted_refs)

def generate_introduction(judul, materi, referensi_str, jumlah_sitasi):
    """Mengirim prompt ke AI (Gemini) untuk membuat pendahuluan."""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash') # Atau gemini-pro
        
        prompt = f"""
        Bertindaklah sebagai peneliti akademis. Tuliskan BAGIAN PENDAHULUAN (Introduction) untuk jurnal ilmiah.
        
        Topik/Judul Penelitian: {judul}
        
        Gunakan materi latar belakang berikut sebagai konteks:
        {materi[:4000]} (dipotong agar muat)
        
        Gunakan daftar referensi berikut untuk membuat sitasi (Gaya APA 7):
        {referensi_str}
        
        Instruksi Khusus:
        1. Tulis dalam Bahasa Indonesia yang akademis dan formal.
        2. Masukkan setidaknya {jumlah_sitasi} sitasi di dalam teks (in-text citation) menggunakan format APA 7, contoh: (Author, Year) atau Author (Year).
        3. Jangan mengarang referensi di luar daftar yang diberikan.
        4. Alur tulisan: Latar belakang umum -> Masalah penelitian -> Solusi yang ditawarkan.
        """
        
        with st.spinner("AI sedang menulis pendahuluan Anda..."):
            response = model.generate_content(prompt)
            return response.text
            
    except Exception as e:
        return f"Terjadi kesalahan pada AI: {e}. (Pastikan API Key sudah benar)"

# --- APLIKASI UTAMA ---

st.title("Penulis Pendahuluan Otomatis 📝")

# 1. Input Judul
judul = st.text_input("Masukkan Judul Penelitian")

# 2. Upload File PDF
materi_pdf = st.file_uploader("Upload Materi (PDF)", type=["pdf"])

# 3. Upload File RIS
file_ris = st.file_uploader("Upload Referensi (RIS)", type=["ris"])

# 4. Pilih Jumlah Sitasi
jumlah_sitasi = st.number_input("Jumlah sitasi yang diinginkan", min_value=1, max_value=20, value=5)

# Tombol untuk proses
if st.button("Buat Pendahuluan"):
    if judul and materi_pdf and file_ris:
        
        # A. Proses File
        teks_materi = extract_text_from_pdf(materi_pdf)
        string_referensi = format_references_for_prompt(file_ris)
        
        if not teks_materi:
            st.warning("Materi PDF kosong atau tidak terbaca.")
        elif not string_referensi:
            st.warning("File RIS kosong atau tidak terbaca.")
        else:
            # B. Panggil AI
            hasil_tulisan = generate_introduction(judul, teks_materi, string_referensi, jumlah_sitasi)
            
            # C. Tampilkan Hasil
            st.success("Selesai!")
            st.subheader("Draft Pendahuluan:")
            st.text_area("Hasil Output", value=hasil_tulisan, height=400)
            
            # D. Tombol Download
            st.download_button(
                label="📥 Download Hasil (.txt)",
                data=hasil_tulisan,
                file_name=f"Pendahuluan_{judul[:10]}.txt",
                mime="text/plain"
            )
            
    else:
        st.warning("Mohon lengkapi semua input (Judul, PDF, dan RIS)!")
