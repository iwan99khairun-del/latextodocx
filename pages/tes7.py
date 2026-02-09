import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import numpy as np
# Import toolkit 3D
from mpl_toolkits.mplot3d import Axes3D 

# --- 1. Konfigurasi Halaman ---
st.set_page_config(page_title="Studio Grafik Pro+", layout="wide")
st.title("📊 Studio Grafik Pro: Stock & Surface 3D")
st.markdown("""
Fitur Baru: **Stock Chart (Candlestick)** & **3D Surface**. Upload data Excel Anda untuk visualisasi.
""")

# --- 2. Fungsi Load Data ---
@st.cache_data
def load_data(file):
    try:
        df_raw = pd.read_excel(file)
        # Cek header/baris pertama
        first_val = df_raw.iloc[0, 0]
        if isinstance(first_val, str) and not str(first_val).replace('.', '', 1).isdigit():
            df = df_raw.drop(index=0).reset_index(drop=True)
        else:
            df = df_raw
        
        # Konversi ke angka (kecuali kolom yang terdeteksi tanggal/string)
        # Kita biarkan kolom tanggal tetap object agar tidak error
        for col in df.columns:
            # Coba convert ke numeric, kalau gagal biarkan as-is
            pd.to_numeric(df[col], errors='ignore')
            
        return df
    except Exception:
        return None

# --- 3. Upload File ---
uploaded_file = st.file_uploader("Upload File Excel (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    if df is not None:
        columns = df.columns.tolist()
        
        # Layout
        col_settings, col_preview = st.columns([1, 2])
        
        with col_settings:
            st.header("⚙️ Pengaturan")
            
            # Pilihan Jenis Grafik
            chart_type = st.selectbox(
                "Pilih Jenis Grafik",
                [
                    "📈 Line Chart (Dual Axis)", 
                    "🕯️ Stock Chart (Candlestick)", # <--- BARU
                    "🧊 3D Line Chart", 
                    "🏔️ 3D Surface Chart",         # <--- BARU
                    "📊 Bar Chart", 
                    "🔵 Scatter Plot", 
                    "🥧 Pie Chart", 
                    "🔥 Heatmap"
                ]
            )
            
            st.divider()
            
            # Inisialisasi Figure Default
            fig = plt.figure(figsize=(10, 6))
            ax = fig.add_subplot(111) 
            
            # ==========================================
            # 1. LOGIKA STOCK CHART (CANDLESTICK)
            # ==========================================
            if chart_type == "🕯️ Stock Chart (Candlestick)":
                st.info("Pastikan urutan data benar (Open, High, Low, Close).")
                
                col_date = st.selectbox("Sumbu X (Waktu/Tanggal)", columns)
                
                c1, c2 = st.columns(2)
                with c1:
                    open_col = st.selectbox("Open (Buka)", columns, index=0)
                    high_col = st.selectbox("High (Tertinggi)", columns, index=1 if len(columns)>1 else 0)
                with c2:
                    low_col = st.selectbox("Low (Terendah)", columns, index=2 if len(columns)>2 else 0)
                    close_col = st.selectbox("Close (Tutup)", columns, index=3 if len(columns)>3 else 0)

                if col_date and open_col and high_col and low_col and close_col:
                    # Pastikan data numerik
                    for col in [open_col, high_col, low_col, close_col]:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    df = df.dropna(subset=[open_col, high_col, low_col, close_col])

                    # Warna Candle
                    up = df[df[close_col] >= df[open_col]]
                    down = df[df[close_col] < df[open_col]]
                    
                    # Lebar batang
                    width = 0.5
                    width2 = 0.05

                    # Gambar Candle Naik (Hijau)
                    ax.bar(up[col_date], up[close_col]-up[open_col], width, bottom=up[open_col], color='green', edgecolor='black', linewidth=0.5)
                    ax.bar(up[col_date], up[high_col]-up[close_col], width2, bottom=up[close_col], color='black') # Wick atas
                    ax.bar(up[col_date], up[low_col]-up[open_col], width2, bottom=up[open_col], color='black')   # Wick bawah

                    # Gambar Candle Turun (Merah)
                    ax.bar(down[col_date], down[open_col]-down[close_col], width, bottom=down[close_col], color='red', edgecolor='black', linewidth=0.5)
                    ax.bar(down[col_date], down[high_col]-down[open_col], width2, bottom=down[open_col], color='black') # Wick atas
                    ax.bar(down[col_date], down[low_col]-down[close_col], width2, bottom=down[close_col], color='black') # Wick bawah

                    ax.set_title(f"Stock Chart: {col_date}", pad=20)
                    ax.set_ylabel("Harga")
                    plt.xticks(rotation=45)

            # ==========================================
            # 2. LOGIKA 3D SURFACE CHART
            # ==========================================
            elif chart_type == "🏔️ 3D Surface Chart":
                st.info("Grafik Surface menggunakan Triangulasi (cocok untuk data Excel biasa).")
                
                # Ubah ke mode 3D
                fig.clear()
                ax = fig.add_subplot(111, projection='3d')

                c_x, c_y, c_z = st.columns(3)
                with c_x: x_axis = st.selectbox("Sumbu X", columns, key="surf_x")
                with c_y: y_axis = st.selectbox("Sumbu Y", columns, key="surf_y")
                with c_z: z_axis = st.selectbox("Sumbu Z (Tinggi)", columns, key="surf_z")
                
                cmap_choice = st.selectbox("Warna (Colormap)", ["viridis", "plasma", "inferno", "magma", "coolwarm"])

                if x_axis and y_axis and z_axis:
                    # Pastikan Numeric
                    df[x_axis] = pd.to_numeric(df[x_axis], errors='coerce')
                    df[y_axis] = pd.to_numeric(df[y_axis], errors='coerce')
                    df[z_axis] = pd.to_numeric(df[z_axis], errors='coerce')
                    df = df.dropna(subset=[x_axis, y_axis, z_axis])

                    # Plot Trisurf (Triangulated Surface) - Lebih aman untuk data non-grid
                    surf = ax.plot_trisurf(df[x_axis], df[y_axis], df[z_axis], cmap=cmap_choice, edgecolor='none', alpha=0.9, linewidth=0.2)
                    
                    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5, label=z_axis)
                    
                    ax.set_xlabel(x_axis)
                    ax.set_ylabel(y_axis)
                    ax.set_zlabel(z_axis)
                    ax.set_title(f"Surface Plot: {z_axis}")

            # ==========================================
            # 3. LOGIKA DUAL AXIS (Yg sudah ada)
            # ==========================================
            elif chart_type == "📈 Line Chart (Dual Axis)":
                st.info("Sumbu Kiri dan Kanan bisa berbeda skala.")
                x_axis = st.selectbox("Pilih Sumbu X", columns)
                col_y1, col_y2 = st.columns(2)
                with col_y1:
                    y_left = st.multiselect("Sumbu Y Kiri", [c for c in columns if c != x_axis])
                with col_y2:
                    y_right = st.multiselect("Sumbu Y Kanan", [c for c in columns if c != x_axis and c not in y_left])

                if x_axis and (y_left or y_right):
                    if y_left:
                        ax.set_xlabel(x_axis)
                        ax.set_ylabel("Sumbu Kiri", color="tab:blue")
                        for col in y_left:
                            ax.plot(df[x_axis], df[col], label=f"{col} (Kiri)", linestyle='-', marker='o')
                        ax.tick_params(axis='y', labelcolor="tab:blue")

                    if y_right:
                        ax2 = ax.twinx()
                        ax2.set_ylabel("Sumbu Kanan", color="tab:red")
                        for col in y_right:
                            ax2.plot(df[x_axis], df[col], label=f"{col} (Kanan)", color='tab:red', linestyle='--', marker='x')
                        ax2.tick_params(axis='y', labelcolor="tab:red")
                    
                    ax.set_title(f"Dual Axis: {x_axis}")

            # ==========================================
            # 4. LOGIKA 3D LINE (Yg sudah ada)
            # ==========================================
            elif chart_type == "🧊 3D Line Chart":
                fig.clear()
                ax = fig.add_subplot(111, projection='3d')
                col_x, col_y, col_z = st.columns(3)
                with col_x: x_axis = st.selectbox("Sumbu X", columns, key="3dx")
                with col_y: y_axis = st.selectbox("Sumbu Y", columns, key="3dy")
                with col_z: z_axis = st.selectbox("Sumbu Z", columns, key="3dz")

                if x_axis and y_axis and z_axis:
                    ax.plot(df[x_axis], df[y_axis], df[z_axis], marker='o', markersize=4)
                    ax.set_xlabel(x_axis)
                    ax.set_ylabel(y_axis)
                    ax.set_zlabel(z_axis)

            # ==========================================
            # 5. LOGIKA STANDARD LAINNYA
            # ==========================================
            elif chart_type == "📊 Bar Chart":
                x_axis = st.selectbox("Sumbu X", columns)
                y_axis = st.multiselect("Sumbu Y", [c for c in columns if c != x_axis])
                if x_axis and y_axis:
                    df.plot(kind='bar', x=x_axis, y=y_axis, ax=ax)

            elif chart_type == "🔵 Scatter Plot":
                x_axis = st.selectbox("Sumbu X", columns)
                y_axis = st.multiselect("Sumbu Y", [c for c in columns if c != x_axis])
                if x_axis and y_axis:
                    for col in y_axis:
                        ax.scatter(df[x_axis], df[col], label=col, alpha=0.7)

            elif chart_type == "🥧 Pie Chart":
                label_col = st.selectbox("Label", columns)
                value_col = st.selectbox("Nilai", [c for c in columns if c != label_col])
                if label_col and value_col:
                    data_pie = df.groupby(label_col)[value_col].sum()
                    ax.pie(data_pie, labels=data_pie.index, autopct='%1.1f%%')

            elif chart_type == "🔥 Heatmap":
                # Hanya ambil kolom numerik untuk korelasi
                df_numeric = df.select_dtypes(include=[np.number])
                if not df_numeric.empty:
                    sns.heatmap(df_numeric.corr(), annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
                    ax.set_title("Matriks Korelasi")
                else:
                    st.warning("Data tidak memiliki kolom angka untuk Heatmap.")

            # --- FINISHING & DOWNLOAD ---
            st.divider()
            tampilkan_grid = st.checkbox("Tampilkan Grid", value=True)
            dpi = st.number_input("Resolusi (DPI)", 100, 901, 300)

            # Grid Logic
            if tampilkan_grid and chart_type not in ["🥧 Pie Chart", "🔥 Heatmap", "🧊 3D Line Chart", "🏔️ 3D Surface Chart"]:
                ax.grid(True, linestyle='--', alpha=0.5)
            
            # Legend Logic (Standard)
            if chart_type not in ["🥧 Pie Chart", "🔥 Heatmap", "🏔️ 3D Surface Chart", "🕯️ Stock Chart (Candlestick)"]:
                if chart_type == "📈 Line Chart (Dual Axis)" and 'ax2' in locals():
                    lines1, labels1 = ax.get_legend_handles_labels()
                    lines2, labels2 = ax2.get_legend_handles_labels()
                    ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left', bbox_to_anchor=(1.05, 1))
                else:
                    ax.legend(bbox_to_anchor=(1.05, 1))

        # --- 4. PREVIEW ---
        with col_preview:
            st.subheader("🖼️ Preview Grafik")
            st.pyplot(fig)
            
            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches='tight', dpi=dpi)
            buf.seek(0)
            
            st.download_button(
                label=f"⬇️ Download Grafik ({dpi} DPI)",
                data=buf,
                file_name="grafik_pro.png",
                mime="image/png",
                use_container_width=True
            )
    else:
        st.error("Format data Excel tidak valid atau kosong.")
else:
    st.info("👋 Silakan upload file Excel.")
