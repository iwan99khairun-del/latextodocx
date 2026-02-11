import streamlit as st
import midtransclient
import time
import uuid

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Download Materi Premium", page_icon="🔒")

# --- FUNGSI UTAMA ---

def init_midtrans():
    """Menginisialisasi koneksi ke Midtrans menggunakan API Key dari secrets"""
    try:
        # Mengambil kunci dari secrets.toml atau Streamlit Cloud Secrets
        server_key = st.secrets["midtrans"]["server_key"]
        client_key = st.secrets["midtrans"]["client_key"]
        is_prod = st.secrets["midtrans"]["is_production"]
        
        # Inisialisasi Snap API (untuk membuat link bayar)
        snap = midtransclient.Snap(
            is_production=is_prod,
            server_key=server_key,
            client_key=client_key
        )
        # Inisialisasi Core API (untuk cek status pembayaran)
        core = midtransclient.CoreApi(
            is_production=is_prod,
            server_key=server_key,
            client_key=client_key
        )
        return snap, core
    except Exception as e:
        st.error("Kunci API Midtrans belum disetting di secrets.toml!")
        return None, None

def get_binary_file_downloader_html(bin_file, file_label='File'):
    """Fungsi pembantu untuk membuat tombol download"""
    # Di aplikasi nyata, baca file ZIP Anda di sini
    # with open("materi.zip", "rb") as f:
    #     data = f.read()
    # return data
    pass

# --- LOGIKA APLIKASI ---

def main():
    st.title("🎓 Materi Python Premium")
    st.markdown("""
    Dapatkan akses ke **Source Code Lengkap + Ebook PDF**.
    Silakan isi data di bawah untuk melakukan pembelian.
    """)
    
    # Inisialisasi Session State (Agar data tidak hilang saat klik tombol)
    if 'order_id' not in st.session_state:
        st.session_state.order_id = None
    if 'payment_url' not in st.session_state:
        st.session_state.payment_url = None
    if 'status_pembayaran' not in st.session_state:
        st.session_state.status_pembayaran = "Belum Bayar"

    # Load Midtrans
    snap_api, core_api = init_midtrans()

    # --- STEP 1: FORM PEMBELI ---
    with st.form("form_beli"):
        nama = st.text_input("Nama Lengkap")
        email = st.text_input("Email Aktif")
        submit = st.form_submit_button("Beli Sekarang (Rp 100.000)")

    if submit and nama and email:
        # Buat Order ID Unik
        order_id = f"ORDER-{uuid.uuid4().hex[:8]}"
        st.session_state.order_id = order_id
        
        # Data Transaksi untuk Midtrans
        param = {
            "transaction_details": {
                "order_id": order_id,
                "gross_amount": 100000
            },
            "customer_details": {
                "first_name": nama,
                "email": email
            }
        }

        try:
            # Minta Link Pembayaran ke Midtrans
            transaction = snap_api.create_transaction(param)
            st.session_state.payment_url = transaction['redirect_url']
            st.success("Order berhasil dibuat!")
        except Exception as e:
            st.error(f"Gagal koneksi ke Midtrans: {e}")

    # --- STEP 2: PROSES PEMBAYARAN & CEK STATUS ---
    if st.session_state.payment_url:
        st.divider()
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("Langkah 1: Lakukan Pembayaran")
            st.link_button("👉 Bayar Sekarang via Midtrans", st.session_state.payment_url)
        
        with col2:
            st.info("Langkah 2: Konfirmasi")
            cek_status = st.button("🔄 Cek Status Pembayaran")
            
            if cek_status:
                try:
                    # Cek status langsung ke Server Midtrans
                    status_response = core_api.transactions.status(st.session_state.order_id)
                    transaksi_status = status_response['transaction_status']
                    fraud_status = status_response['fraud_status']
                    
                    # Logika Status Midtrans
                    if transaksi_status == 'capture':
                        if fraud_status == 'challenge':
                            st.warning("Pembayaran sedang diverifikasi.")
                        else:
                            st.session_state.status_pembayaran = "LUNAS"
                    elif transaksi_status == 'settlement':
                        st.session_state.status_pembayaran = "LUNAS"
                    elif transaksi_status == 'pending':
                        st.warning("Menunggu pembayaran Anda...")
                    else:
                        st.error("Pembayaran batal atau kadaluarsa.")
                        
                except Exception as e:
                    st.warning("Belum ada pembayaran terdeteksi atau Order ID tidak ditemukan.")

    # --- STEP 3: AREA DOWNLOAD (Hanya Muncul Jika LUNAS) ---
    if st.session_state.status_pembayaran == "LUNAS":
        st.balloons()
        st.success("✅ Pembayaran Berhasil Diterima!")
        
        st.write("### 📂 Download Area")
        st.write("Terima kasih sudah membeli. Silakan download materi Anda di bawah ini:")
        
        # Siapkan File Dummy untuk Demo (Ganti ini dengan file asli Anda nanti)
        # Cara Pakai: Taruh file 'materi.zip' di folder yang sama dengan main.py
        # Lalu uncomment kode di bawah ini:
        
        # with open("materi.zip", "rb") as file:
        #     btn = st.download_button(
        #         label="📥 Download Materi (.zip)",
        #         data=file,
        #         file_name="Materi_Premium_Python.zip",
        #         mime="application/zip"
        #     )
            
        # Untuk DEMO saja (agar tidak error saat Anda copy paste):
        st.download_button(
            label="📥 Download Materi (Demo)",
            data="Isi file dummy karena Anda belum upload file zip asli.",
            file_name="Materi_Demo.txt"
        )

if __name__ == "__main__":
    main()
