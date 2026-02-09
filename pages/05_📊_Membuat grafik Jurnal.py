import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
# Import toolkit 3D secara eksplisit (kadang diperlukan untuk versi matplotlib tertentu)
from mpl_toolkits.mplot3d import Axes3D 

# --- 1. Konfigurasi Halaman ---
st.set_page_config(page_title="Studio Grafik Dual-Axis", layout="wide")
st.title("📊 Studio Grafik Pro: Dual Axis & 3D Support")
st.markdown("""
Fitur: **Dual Y-Axis** & **3D Line Plot**. Upload data Excel Anda untuk mulai memvisualisasikan data.
""")

# --- 2. Fungsi Load Data ---
@st.cache_data
def load_data(file):
    try:
        df_raw = pd.read_excel(file)
        # Pembersihan Data (Hapus baris satuan jika ada)
        first_val = df_raw.iloc[0, 0]
        # Cek jika baris pertama adalah string/huruf (bukan angka)
        if isinstance(first_val, str) and not str(first_val).replace('.', '', 1).isdigit():
            df = df_raw.drop(index=0).reset_index(drop=True)
        else:
            df = df_raw
        
        # Konversi ke angka
        df = df.apply(pd.to_numeric, errors='coerce')
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
            
            # Pilihan Jenis Grafik (Menambahkan 3D Line Chart)
            chart_type = st.selectbox(
                "Pilih Jenis Grafik",
                [
                    "📈 Line Chart (Dual Axis)", 
                    "🧊 3D Line Chart",  # <--- ITEM BARU
                    "📊 Bar Chart", 
                    "🔵 Scatter Plot", 
                    "🥧 Pie Chart", 
                    "🔥 Heatmap"
                ]
            )
            
            st.divider()
            
            # Inisialisasi Figure
            fig = plt.figure(figsize=(10, 6))
            
            # Kita buat ax default (2D), nanti jika 3D dipilih, kita timpa.
            ax = fig.add_subplot(111) 
            
            # --- LOGIKA KHUSUS DUAL AXIS (LINE CHART) ---
            if chart_type == "📈 Line Chart (Dual Axis)":
                st.info("Mode ini memungkinkan Sumbu Kiri dan Kanan berbeda skala.")
                
                x_axis = st.selectbox("Pilih Sumbu X (Horizontal)", columns)
                
                # Input untuk Sumbu Kiri & Kanan
                col_y1, col_y2 = st.columns(2)
                with col_y1:
                    y_left = st.multiselect("Sumbu Y Kiri (Utama)", [c for c in columns if c != x_axis])
                with col_y2:
                    y_right = st.multiselect("Sumbu Y Kanan (Sekunder)", [c for c in columns if c != x_axis and c not in y_left])

                # Logic Plotting Dual Axis
                if x_axis and (y_left or y_right):
                    # 1. Plot Sumbu Kiri (Ax1)
                    if y_left:
                        ax.set_xlabel(x_axis)
                        ax.set_ylabel("Sumbu Kiri", color="tab:blue")
                        for col in y_left:
                            # Garis Solid untuk Kiri
                            ax.plot(df[x_axis], df[col], label=f"{col} (Kiri)", linestyle='-', marker='o')
                        ax.tick_params(axis='y', labelcolor="tab:blue")

                    # 2. Plot Sumbu Kanan (Ax2)
                    if y_right:
                        ax2 = ax.twinx()  # Membuat kembaran sumbu X tapi Y-nya beda
                        ax2.set_ylabel("Sumbu Kanan", color="tab:red")
                        for col in y_right:
                            # Garis Putus-putus untuk Kanan (biar beda)
                            ax2.plot(df[x_axis], df[col], label=f"{col} (Kanan)", color='tab:red', linestyle='--', marker='x')
                        ax2.tick_params(axis='y', labelcolor="tab:red")
                    
                    # Judul
                    ax.set_title(f"Grafik Dual Axis: {x_axis}", pad=20)

            # --- LOGIKA KHUSUS 3D LINE CHART (BARU) ---
            elif chart_type == "🧊 3D Line Chart":
                st.info("Pilih 3 variabel untuk sumbu X, Y, dan Z.")
                
                # Kita perlu menghapus axis 2D default dan menggantinya dengan 3D projection
                fig.clear()
                ax = fig.add_subplot(111, projection='3d')

                col_x, col_y, col_z = st.columns(3)
                with col_x: x_axis = st.selectbox("Sumbu X", columns, key="3dx")
                with col_y: y_axis = st.selectbox("Sumbu Y", columns, key="3dy")
                with col_z: z_axis = st.selectbox("Sumbu Z (Tinggi)", columns, key="3dz")

                if x_axis and y_axis and z_axis:
                    # Plotting 3D Line
                    ax.plot(df[x_axis], df[y_axis], df[z_axis], marker='o', markersize=4, linestyle='-', linewidth=2)
                    
                    # Labeling
                    ax.set_xlabel(x_axis)
                    ax.set_ylabel(y_axis)
                    ax.set_zlabel(z_axis)
                    ax.set_title(f"3D Plot: {x_axis} vs {y_axis} vs {z_axis}")

            # --- LOGIKA GRAFIK LAINNYA (Standar) ---
            elif chart_type == "📊 Bar Chart":
                x_axis = st.selectbox("Sumbu X", columns)
                y_axis = st.multiselect("Sumbu Y", [c for c in columns if c != x_axis])
                if x_axis and y_axis:
                    df.plot(kind='bar', x=x_axis, y=y_axis, ax=ax)
                    ax.set_ylabel("Nilai")

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
                sns.heatmap(df.corr(), annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
                ax.set_title("Matriks Korelasi")

            # --- FINISHING & LEGENDA ---
            st.divider()
            tampilkan_grid = st.checkbox("Tampilkan Grid", value=True)
            dpi = st.number_input("Resolusi (DPI)", 100, 901, 300)

            # Grid logic (Skip grid setting for Pie/Heatmap/3D handled automatically)
            if tampilkan_grid and chart_type not in ["🥧 Pie Chart", "🔥 Heatmap", "🧊 3D Line Chart"]:
                ax.grid(True, linestyle='--', alpha=0.5)
            
            # Legenda Logic
            if chart_type == "📈 Line Chart (Dual Axis)" and (y_left or y_right):
                # Trik menggabungkan legend dari 2 sumbu berbeda
                lines1, labels1 = ax.get_legend_handles_labels()
                if 'ax2' in locals(): # Kalau sumbu kanan aktif
                    lines2, labels2 = ax2.get_legend_handles_labels()
                    ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left', bbox_to_anchor=(1.05, 1))
                else:
                    ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1))
            elif chart_type not in ["🥧 Pie Chart", "🔥 Heatmap", "🧊 3D Line Chart"]:
                # Default legend placement for standard charts
                ax.legend(bbox_to_anchor=(1, 1))

        # --- 4. PREVIEW & DOWNLOAD ---
        with col_preview:
            st.subheader("🖼️ Preview Grafik")
            st.pyplot(fig)
            
            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches='tight', dpi=dpi)
            buf.seek(0)
            
            st.download_button(
                label=f"⬇️ Download Grafik ({dpi} DPI)",
                data=buf,
                file_name="grafik_studio.png",
                mime="image/png",
                use_container_width=True
            )
    else:
        st.error("Format data Excel tidak valid.")
else:
    st.info("👋 Upload file Excel untuk mencoba fitur Dual Axis dan 3D.")
