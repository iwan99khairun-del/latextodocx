import streamlit as st
import random
import time

def app():
    st.title("🎲 Tebak-tebakan Binatang (Magic)")
    st.write("Coba klik tombol di bawah.")

    # 1. DATABASE BINATANG
    if 'db_binatang' not in st.session_state:
        # Anda bisa menambah daftar ini sesuka hati
        st.session_state.db_binatang = [
            "harimau", "kucing", "anjing", "kambing", 
            "sapi", "kerbau", "elang", "ular", "tikus",
            "singa", "jerapah", "kuda", "zebra", "buaya",
            "kelinci", "monyet", "ayam", "bebek", "angsa",
            "panda", "koala", "kanguru", "paus", "lumba-lumba"
        ]

    # 2. SESSION STATE (INGATAN)
    if 'hewan_sekarang' not in st.session_state:
        st.session_state.hewan_sekarang = ""
    
    if 'waktu_klik_terakhir' not in st.session_state:
        st.session_state.waktu_klik_terakhir = 0.0

    # 3. FUNGSI LOGIKA (MAGIC)
    def acak_binatang():
        waktu_sekarang = time.time()
        selisih_waktu = waktu_sekarang - st.session_state.waktu_klik_terakhir
        
        # LOGIKA 1: DOUBLE CLICK (< 1 detik) -> GAJAH
        if selisih_waktu < 1.0: 
            hasil = "gajah"
            st.toast("🐘 Double Click! Muncul Gajah!")
        
        # LOGIKA 2: SEBELUMNYA KAMBING -> HARUS KIJANG
        elif st.session_state.hewan_sekarang == "kambing":
            hasil = "kijang"
            st.info("Setelah Kambing pasti Kijang!")
            
        # LOGIKA 3: ACAK BIASA
        else:
            pilihan = st.session_state.db_binatang.copy()
            if "gajah" in pilihan: pilihan.remove("gajah") 
            hasil = random.choice(pilihan)

        st.session_state.hewan_sekarang = hasil
        st.session_state.waktu_klik_terakhir = waktu_sekarang

    # 4. TOMBOL & HASIL
    st.button("KLIK SAYA 🎲", on_click=acak_binatang)

    if st.session_state.hewan_sekarang:
        st.divider()
        st.header(f"Hasil: {st.session_state.hewan_sekarang.upper()}")

    # 5. MENAMPILKAN DAFTAR BINATANG DI BAWAH
    st.divider()
    with st.expander("📜 Lihat Daftar Semua Binatang"):
        # Menggabungkan list menjadi teks rapi dengan koma
        daftar_teks = ", ".join(st.session_state.db_binatang).title()
        st.write(daftar_teks)
        st.caption(f"Total ada {len(st.session_state.db_binatang)} nama binatang.")

if __name__ == "__main__":
    app()
