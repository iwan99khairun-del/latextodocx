import streamlit as st
import random
import time

def app():
    st.title("🎲 Tebak-tebakan Binatang (Magic)")
    st.write("Coba klik tombol di bawah.")

    # 1. DATABASE BINATANG
    if 'db_binatang' not in st.session_state:
        st.session_state.db_binatang = [
            "harimau", "kucing", "anjing", "kambing", 
            "sapi", "kerbau", "elang", "ular", "tikus",
            "singa", "jerapah", "kuda", "zebra", "buaya",
            "kelinci", "monyet", "ayam", "bebek", "angsa"
        ]

    # 2. SESSION STATE (INGATAN)
    if 'hewan_sekarang' not in st.session_state:
        st.session_state.hewan_sekarang = ""
    
    # Simpan waktu klik terakhir
    if 'waktu_klik_terakhir' not in st.session_state:
        st.session_state.waktu_klik_terakhir = 0.0

    # 3. FUNGSI LOGIKA
    def acak_binatang():
        waktu_sekarang = time.time()
        
        # Hitung selisih waktu antara klik sekarang dan klik sebelumnya
        selisih_waktu = waktu_sekarang - st.session_state.waktu_klik_terakhir
        
        # --- ATURAN 1: DOUBLE CLICK (Cepat < 1 detik) ---
        # Jika selisih waktunya sangat sedikit, berarti user melakukan double click
        if selisih_waktu < 1.0: 
            hasil = "gajah"
            st.toast("🐘 Double Click Terdeteksi! Muncul Gajah!")
        
        # --- ATURAN 2: SETELAH KAMBING HARUS KIJANG ---
        elif st.session_state.hewan_sekarang == "kambing":
            hasil = "kijang"
            st.info("Setelah Kambing pasti Kijang!")
            
        # --- ATURAN 3: ACAK BIASA ---
        else:
            pilihan = st.session_state.db_binatang.copy()
            # Opsional: Hapus gajah dari acak biasa biar makin misterius
            if "gajah" in pilihan: pilihan.remove("gajah") 
            hasil = random.choice(pilihan)

        # Update Session State
        st.session_state.hewan_sekarang = hasil
        st.session_state.waktu_klik_terakhir = waktu_sekarang

    # 4. TOMBOL & TAMPILAN
    st.button("KLIK SAYA 🎲", on_click=acak_binatang)

    if st.session_state.hewan_sekarang:
        st.divider()
        st.header(f"Hasil: {st.session_state.hewan_sekarang.upper()}")

if __name__ == "__main__":
    app()
