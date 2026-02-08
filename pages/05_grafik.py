import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# --- 1. Konfigurasi Halaman ---
st.set_page_config(page_title="Grafik Multi-Axis", layout="wide")
st.title("📊 Aplikasi Grafik Multi-Axis")
st.markdown("Upload Excel, pilih satu sumbu X, dan **pilih banyak sumbu Y** sesuka hati.")

# --- 2. Upload File ---
uploaded_file = st.file_uploader("Upload File Excel (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Baca Data
        df_raw = pd.read_excel(uploaded_file)

        # --- PEMBERSIHAN DATA (Agar tidak error satuan) ---
        first_val = df_raw.iloc[0, 0]
        # Jika baris pertama bukan angka, kita anggap itu satuan (Mpa, m/s) dan dihapus
        if isinstance(first_val, str) and not first_val.replace('.', '', 1).isdigit():
            df = df_raw.drop(index=0).reset_index(drop=True)
            st.toast("Baris satuan telah dihapus otomatis.", icon="🧹")
        else:
            df = df_raw
            
        # Konversi semua ke angka
        df = df.apply(pd.to_numeric, errors='coerce')
        columns = df.columns.tolist()

        # --- 3. Pengaturan Sumbu ---
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Pengaturan Sumbu")
            # Pilih X (Hanya satu)
            x_axis = st.selectbox("Pilih Sumbu X (Horizontal)", columns)
            
            # Filter kolom sisa untuk Y (agar X tidak muncul di pilihan Y)
            remaining_cols = [c for c in columns if c != x_axis]
            
            # Opsi Cepat: Pilih Semua
            pilih_semua = st.checkbox("✅ Pilih Semua Kolom Sisa?")
            
            if pilih_semua:
                y_axis_list = remaining_cols
                st.info(f"Terpilih {len(y_axis_list)} data untuk sumbu Y.")
            else:
                # Pilih Y (Bisa Banyak / Multiselect)
                y_axis_list = st.multiselect("Pilih Sumbu Y (Bisa lebih dari satu)", remaining_cols)

            st.write("---")
            chart_type = st.selectbox("Jenis Grafik", ["Line Chart", "Bar Chart", "Scatter Plot"])
            dpi = st.number_input("Resolusi Download (DPI)", value=300, step=50)

        # --- 4. Tampilan Grafik ---
        with col2:
            st.subheader("Preview Grafik")
            
            if x_axis and y_axis_list:
                fig, ax = plt.subplots(figsize=(10, 6))

                # --- LOOPING PLOTTING (Kunci agar bisa banyak grafik) ---
                for col_name in y_axis_list:
                    if chart_type == "Line Chart":
                        # Tidak pakai color=... agar warna otomatis beda-beda
                        ax.plot(df[x_axis], df[col_name], marker='o', label=col_name)
                    
                    elif chart_type == "Scatter Plot":
                        ax.scatter(df[x_axis], df[col_name], label=col_name)
                    
                    elif chart_type == "Bar Chart":
                        # Bar chart agak tricky kalau ditumpuk, tapi kita coba standar
                        ax.bar(df[x_axis], df[col_name], label=col_name, alpha=0.6)

                # Pemanis Grafik
                ax.set_xlabel(x_axis)
                ax.set_ylabel("Nilai / Value")
                ax.set_title(f"Grafik: {', '.join(y_axis_list)} vs {x_axis}")
                ax.grid(True, linestyle='--', alpha=0.5)
                
                # MUNCULKAN LEGENDA (Penting agar tahu warna apa milik siapa)
                ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left') 

                st.pyplot(fig)

                # --- 5. Download Button ---
                buf = io.BytesIO()
                fig.savefig(buf, format="png", bbox_inches='tight', dpi=dpi)
                buf.seek(0)
                
                st.download_button(
                    label="⬇️ Download Grafik",
                    data=buf,
                    file_name="grafik_multi_axis.png",
                    mime="image/png"
                )
            else:
                st.warning("Silakan pilih setidaknya satu kolom untuk Sumbu Y.")

    except Exception as e:
        st.error(f"Error: {e}")
