import streamlit as st
import random

def app():
    st.title("🎲 Tebak-tebakan Nama Binatang")
    st.write("Klik tombol di bawah untuk memunculkan nama binatang secara acak.")

    # 1. Inisialisasi Database
    if 'database_binatang' not in st.session_state:
        st.session_state.database_binatang = [
            "harimau", "gajah", "kucing", "anjing", "kambing", 
            "sapi", "kerbau", "elang", "ular", "tikus",
            "singa", "jerapah", "kuda", "zebra", "buaya",
            "kelinci", "monyet", "ayam", "bebek", "angsa"
        ]

    # 2. Inisialisasi State (Ingatan Aplikasi)
    if 'binatang_saat_ini' not in st.session_state:
        st.session_state.binatang_saat_ini = ""
    
    # --- BARU: Inisialisasi Penghitung Klik ---
    if 'jumlah_klik' not in st.session_state:
        st.session_state.jumlah_klik = 0

    # Fungsi logika utama
    def acak_binatang():
        # Tambah hitungan klik setiap kali fungsi dipanggil
        st.session_state.jumlah_klik += 1
        klik_ke = st.session_state.jumlah_klik

        # LOGIKA 1: Jika ini adalah klik ke-2, WAJIB Gajah
        if klik_ke == 2:
            st.session_state.binatang_saat_ini = "gajah"
            st.warning(f"(Ssst... ini setingan klik ke-{klik_ke})")
        
        # LOGIKA 2: Jika sebelumnya Kambing, maka sekarang WAJIB Kijang
        # (Kita pakai 'elif' supaya tidak menimpa logika Gajah jika kebetulan klik ke-2)
        elif st.session_state.binatang_saat_ini == "kambing":
            st.session_state.binatang_saat_ini = "kijang"
            st.info("Karena sebelumnya Kambing, maka sekarang pasti Kijang!")
            
        # LOGIKA 3: Selain itu, acak normal
        else:
            pilihan_baru = random.choice(st.session_state.database_binatang)
            st.session_state.binatang_saat_ini = pilihan_baru

    # 3. Tombol Aksi
    if st.button("Acak Nama Binatang"):
        acak_binatang()

    # 4. Tampilkan Hasil
    if st.session_state.binatang_saat_ini:
        st.subheader(f"Binatang: {st.session_state.binatang_saat_ini.upper()}")
        st.caption(f"Total klik: {st.session_state.jumlah_klik}")

if __name__ == "__main__":
    app()
