import rispy

def buat_pendahuluan(judul, materi_pdf, file_ris, jumlah_sitasi):
    # 1. Load data dari RIS
    with open(file_ris, 'r') as f:
        entries = rispy.load(f)
    
    # 2. Ambil referensi sesuai jumlah yang diminta user
    sitasi_terpilih = entries[:jumlah_sitasi]
    
    # 3. Format referensi untuk AI (misal: Author, Year)
    formatted_refs = [f"{e['first_authors'][0]} ({e['year']})" for e in sitasi_terpilih]
    
    # 4. Kirim Prompt ke AI (Gemini/GPT)
    prompt = f"""
    Tuliskan pendahuluan untuk karya ilmiah berjudul '{judul}'.
    Gunakan konteks materi berikut: {materi_pdf}
    Anda WAJIB menyertakan {jumlah_sitasi} sitasi berikut dalam teks: {', '.join(formatted_refs)}.
    """
    
    # Di sini Anda memanggil API AI untuk mendapatkan teks final
    return "Hasil teks pendahuluan dari AI..."
