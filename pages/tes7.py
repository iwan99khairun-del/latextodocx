import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import numpy as np
from mpl_toolkits.mplot3d import Axes3D 

# --- 1. Konfigurasi Halaman ---
st.set_page_config(page_title="Studio Grafik Pro+", layout="wide")
st.title("📊 Studio Grafik Pro: Grfik untuk Jurnal resolusi tinggi")
st.markdown("""
Fitur Baru: **Stock Chart** (OHLC/HLC) & **Surface** (Filled/Wireframe/Contour) + Anti Crash.
""")

# --- 2. Fungsi Load Data ---
@st.cache_data
def load_data(file):
    try:
        df_raw = pd.read_excel(file)
        # Cek header/baris pertama jika ada teks aneh
        first_val = df_raw.iloc[0, 0]
        if isinstance(first_val, str) and not str(first_val).replace('.', '', 1).isdigit():
            df = df_raw.drop(index=0).reset_index(drop=True)
        else:
            df = df_raw
        
        # Konversi ke angka otomatis
        for col in df.columns:
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
        
        # Layout: Kiri (Pengaturan), Kanan (Preview)
        col_settings, col_preview = st.columns([1, 2])
        
        with col_settings:
            st.header("⚙️ Pengaturan")
            
            # Pilihan Jenis Grafik
            chart_type = st.selectbox(
                "Pilih Jenis Grafik",
                [
                    "📈 Line Chart (Dual Axis)", 
                    "🕯️ Stock Chart (Saham)",       
                    "🏔️ Surface Chart (3D/Contour)", 
                    "🧊 3D Line Chart", 
                    "📊 Bar Chart", 
                    "🔵 Scatter Plot", 
                    "🥧 Pie Chart", 
                    "🔥 Heatmap"
                ]
            )
            
            st.divider()
            
            # Inisialisasi Figure Default
            fig = plt.figure(figsize=(10, 6))
            
            # ==========================================
            # A. LOGIKA STOCK CHART
            # ==========================================
            if chart_type == "🕯️ Stock Chart (Saham)":
                st.info("Mendukung format OHLC dan HLC.")
                
                stock_mode = st.radio("Mode Data:", ["OHLC (Lengkap)", "HLC (Sederhana)"], horizontal=True)
                col_date = st.selectbox("Sumbu X (Waktu/Tanggal)", columns)
                
                # Input Kolom Dinamis
                if stock_mode == "OHLC (Lengkap)":
                    c1, c2 = st.columns(2)
                    with c1:
                        open_col = st.selectbox("Open (Buka)", columns, index=0)
                        high_col = st.selectbox("High (Tertinggi)", columns, index=1 if len(columns)>1 else 0)
                    with c2:
                        low_col = st.selectbox("Low (Terendah)", columns, index=2 if len(columns)>2 else 0)
                        close_col = st.selectbox("Close (Tutup)", columns, index=3 if len(columns)>3 else 0)
                else: # HLC
                    c1, c2 = st.columns(2)
                    with c1:
                        high_col = st.selectbox("High (Tertinggi)", columns, index=0)
                        low_col = st.selectbox("Low (Terendah)", columns, index=1 if len(columns)>1 else 0)
                    with c2:
                        close_col = st.selectbox("Close (Tutup)", columns, index=2 if len(columns)>2 else 0)
                    open_col = None

                # Validasi Input
                cols_to_check = [high_col, low_col, close_col]
                if open_col: cols_to_check.append(open_col)

                if col_date and all(cols_to_check):
                    ax = fig.add_subplot(111)
                    # Pastikan Numeric
                    for c in cols_to_check:
                        df[c] = pd.to_numeric(df[c], errors='coerce')
                    df_stock = df.dropna(subset=cols_to_check)

                    width = 0.5
                    width2 = 0.05
                    
                    if stock_mode == "OHLC (Lengkap)":
                        up = df_stock[df_stock[close_col] >= df_stock[open_col]]
                        down = df_stock[df_stock[close_col] < df_stock[open_col]]
                        
                        # Hijau (Naik)
                        ax.bar(up[col_date], up[close_col]-up[open_col], width, bottom=up[open_col], color='green', edgecolor='black', linewidth=0.5)
                        ax.bar(up[col_date], up[high_col]-up[close_col], width2, bottom=up[close_col], color='black')
                        ax.bar(up[col_date], up[low_col]-up[open_col], width2, bottom=up[open_col], color='black')
                        
                        # Merah (Turun)
                        ax.bar(down[col_date], down[open_col]-down[close_col], width, bottom=down[close_col], color='red', edgecolor='black', linewidth=0.5)
                        ax.bar(down[col_date], down[high_col]-down[open_col], width2, bottom=down[open_col], color='black')
                        ax.bar(down[col_date], down[low_col]-down[close_col], width2, bottom=down[close_col], color='black')
                    
                    else:
                        # Logic HLC
                        ax.bar(df_stock[col_date], df_stock[high_col]-df_stock[low_col], width2, bottom=df_stock[low_col], color='black')
                        ax.plot(df_stock[col_date], df_stock[close_col], 'r_', markersize=10, markeredgewidth=2)

                    ax.set_title(f"Stock Chart ({stock_mode})", pad=20)
                    ax.set_ylabel("Harga")
                    plt.xticks(rotation=45)

            # ==========================================
            # B. LOGIKA SURFACE CHART (ANTI CRASH)
            # ==========================================
            elif chart_type == "🏔️ Surface Chart (3D/Contour)":
                surf_style = st.selectbox(
                    "Gaya Tampilan", 
                    ["🌈 Filled Surface (Isi)", "🕸️ Wireframe (Jaring)", "🗺️ Contour (Peta 2D)"]
                )
                
                c_x, c_y, c_z = st.columns(3)
                with c_x: x_axis = st.selectbox("Sumbu X", columns, key="sx")
                with c_y: y_axis = st.selectbox("Sumbu Y", columns, key="sy")
                with c_z: z_axis = st.selectbox("Sumbu Z", columns, key="sz")
                
                cmap_choice = st.selectbox("Warna", ["viridis", "plasma", "coolwarm", "terrain", "ocean"])

                if x_axis and y_axis and z_axis:
                    if x_axis == y_axis:
                        st.warning("⚠️ Sumbu X dan Y harus berbeda kolom.")
                    else:
                        # Konversi Data
                        df[x_axis] = pd.to_numeric(df[x_axis], errors='coerce')
                        df[y_axis] = pd.to_numeric(df[y_axis], errors='coerce')
                        df[z_axis] = pd.to_numeric(df[z_axis], errors='coerce')
                        df_surf = df.dropna(subset=[x_axis, y_axis, z_axis])

                        try:
                            if surf_style == "🗺️ Contour (Peta 2D)":
                                ax = fig.add_subplot(111)
                                cntr = ax.tricontourf(df_surf[x_axis], df_surf[y_axis], df_surf[z_axis], levels=14, cmap=cmap_choice)
                                fig.colorbar(cntr, ax=ax, label=z_axis)
                                ax.set_title(f"Contour: {z_axis}")
                            
                            elif surf_style == "🕸️ Wireframe (Jaring)":
                                ax = fig.add_subplot(111, projection='3d')
                                ax.plot_trisurf(
                                    df_surf[x_axis], df_surf[y_axis], df_surf[z_axis], 
                                    color=(1,1,1,0), edgecolor='black', linewidth=0.5
                                )
                                ax.set_title(f"Wireframe: {z_axis}")
                                
                            else: 
                                ax = fig.add_subplot(111, projection='3d')
                                surf = ax.plot_trisurf(
                                    df_surf[x_axis], df_surf[y_axis], df_surf[z_axis], 
                                    cmap=cmap_choice, edgecolor='none', alpha=0.9
                                )
                                fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5, label=z_axis)
                                ax.set_title(f"Surface: {z_axis}")

                            if surf_style != "🗺️ Contour (Peta 2D)":
                                ax.set_zlabel(z_axis)
                            
                            ax.set_xlabel(x_axis)
                            ax.set_ylabel(y_axis)

                        except Exception as e:
                            st.error("⛔ Gagal membuat Surface.")
                            st.info("Penyebab: Data X dan Y mungkin membentuk garis lurus (segaris). Harap pilih kolom X dan Y yang datanya menyebar (tidak identik/berhubungan linear sempurna).")

            # ==========================================
            # C. CHART LAINNYA
            # ==========================================
            else:
                ax = fig.add_subplot(111)
                
                if chart_type == "📈 Line Chart (Dual Axis)":
                    x_axis = st.selectbox("Sumbu X", columns)
                    c_l, c_r = st.columns(2)
                    with c_l: y_left = st.multiselect("Sumbu Kiri", [c for c in columns if c!=x_axis])
                    with c_r: y_right = st.multiselect("Sumbu Kanan", [c for c in columns if c!=x_axis and c not in y_left])
                    
                    if x_axis and (y_left or y_right):
                        if y_left:
                            ax.set_xlabel(x_axis)
                            ax.set_ylabel("Kiri", color="tab:blue")
                            for col in y_left: ax.plot(df[x_axis], df[col], 'o-', label=f"{col} (L)")
                            ax.tick_params(axis='y', labelcolor="tab:blue")
                        if y_right:
                            ax2 = ax.twinx()
                            ax2.set_ylabel("Kanan", color="tab:red")
                            for col in y_right: ax2.plot(df[x_axis], df[col], 'x--', color='tab:red', label=f"{col} (R)")
                            ax2.tick_params(axis='y', labelcolor="tab:red")

                elif chart_type == "🧊 3D Line Chart":
                    fig.clear()
                    ax = fig.add_subplot(111, projection='3d')
                    c_x, c_y, c_z = st.columns(3)
                    with c_x: x = st.selectbox("X", columns, key="3dx")
                    with c_y: y = st.selectbox("Y", columns, key="3dy")
                    with c_z: z = st.selectbox("Z", columns, key="3dz")
                    if x and y and z:
                        ax.plot(df[x], df[y], df[z], marker='o')
                        ax.set_xlabel(x); ax.set_ylabel(y); ax.set_zlabel(z)

                elif chart_type == "📊 Bar Chart":
                    x = st.selectbox("X", columns); y = st.multiselect("Y", [c for c in columns if c!=x])
                    if x and y: df.plot(kind='bar', x=x, y=y, ax=ax)

                elif chart_type == "🔵 Scatter Plot":
                    x = st.selectbox("X", columns); y = st.multiselect("Y", [c for c in columns if c!=x])
                    if x and y: 
                        for c in y: ax.scatter(df[x], df[c], label=c)

                elif chart_type == "🥧 Pie Chart":
                    lbl = st.selectbox("Label", columns); val = st.selectbox("Nilai", [c for c in columns if c!=lbl])
                    if lbl and val: 
                        d = df.groupby(lbl)[val].sum()
                        ax.pie(d, labels=d.index, autopct='%1.1f%%')

                elif chart_type == "🔥 Heatmap":
                    df_num = df.select_dtypes(include=[np.number])
                    if not df_num.empty: sns.heatmap(df_num.corr(), annot=True, ax=ax, cmap="coolwarm")

            # --- FINISHING ---
            st.divider()
            tampilkan_grid = st.checkbox("Grid", value=True)
            dpi = st.number_input("Resolusi (DPI)", 100, 900, 300)
            
            if tampilkan_grid and chart_type not in ["🥧 Pie Chart", "🔥 Heatmap"]:
                try: ax.grid(True, linestyle='--', alpha=0.5)
                except: pass
            
            # Legend
            if chart_type not in ["🥧 Pie Chart", "🔥 Heatmap", "🏔️ Surface Chart (3D/Contour)"]:
                try: ax.legend(loc='best')
                except: pass

        # --- 4. PREVIEW ---
        with col_preview:
            st.subheader("🖼️ Hasil Grafik")
            st.pyplot(fig)
            
            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches='tight', dpi=dpi)
            buf.seek(0)
            st.download_button("⬇️ Download PNG", buf, "grafik_pro.png", "image/png", use_container_width=True)
    else:
        st.error("Data tidak valid.")
else:
    st.info("👋 Upload file Excel untuk memulai.")
