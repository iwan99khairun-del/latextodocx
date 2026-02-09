import random

def main():
    # Contoh data binatang (Anda bisa mengisi ini hingga 1000 nama)
    database_binatang = [
        "harimau", "gajah", "kucing", "anjing", "kambing", 
        "sapi", "kerbau", "elang", "ular", "tikus",
        "singa", "jerapah", "kuda", "zebra", "buaya",
        "kelinci", "monyet", "ayam", "bebek", "angsa"
        # ... tambahkan sisa data binatang di sini
    ]
    
    # Pastikan 'kijang' ada di dalam daftar untuk mencegah error
    if "kijang" not in database_binatang:
        database_binatang.append("kijang")

    print("=== Permainan Tebak Nama Binatang ===")
    print("Ketik 'mulai' untuk melihat nama binatang atau 'keluar' untuk berhenti.")

    nama_sebelumnya = ""

    while True:
        perintah = input("\nTekan Enter untuk nama selanjutnya (atau ketik 'keluar'): ").lower()
        
        if perintah == 'keluar':
            print("Terima kasih telah bermain!")
            break
        
        # Logika Khusus: Jika yang sebelumnya adalah 'kambing', maka sekarang HARUS 'kijang'
        if nama_sebelumnya == "kambing":
            binatang_terpilih = "kijang"
            print(f"Binatang selanjutnya adalah: {binatang_terpilih.upper()} (Khusus setelah Kambing!)")
        else:
            # Pilih acak dari database
            binatang_terpilih = random.choice(database_binatang)
            print(f"Tebak binatang ini: {binatang_terpilih.upper()}")
        
        # Simpan nama binatang ini sebagai 'nama_sebelumnya' untuk putaran berikutnya
        nama_sebelumnya = binatang_terpilih

if __name__ == "__main__":
    main()
