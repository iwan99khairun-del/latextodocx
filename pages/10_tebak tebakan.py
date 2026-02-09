import streamlit as st
import random

def app():
    st.title("🎲 Tebak-tebakan Nama Binatang")
    st.write("Klik tombol di bawah untuk memunculkan nama binatang secara acak.")

    # 1. Inisialisasi Database Binatang (Sampel data)
    # Anda bisa memperbanyak list ini hingga 1000
    if 'database_binatang' not in st.session_state:
        st.session_state.database_binatang = [
            "harimau", "gajah", "kucing", "anjing", "kambing", 
            "sapi", "kerbau", "elang", "ular", "tikus",
            "singa", "jerapah", "kuda", "zebra", "buaya",
            "kelinci", "monyet", "ayam", "bebek", "angsa"
        ]

    # 2. Inisialisasi State (Ingatan Aplikasi)
    # Kita butuh ini agar Streamlit "ingat" binatang apa yang muncul sebelumnya
    if 'binatang_saat_ini' not in st.session_state:
        st.session_state.binatang_saat_ini = ""
    
    # Fungsi untuk mengacak
    def acak_binatang():
        # Cek apakah binatang yang TAMPIL SEKARANG adalah kambing?
        # Jika iya, maka selanjutnya WAJIB kijang.
        if st.session_state.binatang_saat_ini == "kambing":
            st.session_state.binatang_saat_ini = "kijang"
            st.info("Karena sebelumnya Kambing, maka sekarang pasti Kijang!")
        else:
            # Jika bukan kambing, acak normal
            pilihan_baru = random.choice(st.session_state.database_binatang)
            st.session_state.binatang_saat_ini = pilihan_baru

    # 3. Tombol Aksi
    if st.button("Acak Nama Binatang"):
        acak_binatang()

    # 4. Tampilkan Hasil
    if st.session_state.binatang_saat_ini:
        st.subheader(f"Binatang: {st.session_state.binatang_saat_ini.upper()}")

# Panggil fungsi app jika file dijalankan langsung
if __name__ == "__main__":
    app()
