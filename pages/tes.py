import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io

# --- 1. Konfigurasi Halaman ---
st.set_page_config(page_title="Studio Grafik Lengkap", layout="wide")
st.title("📊 Studio Grafik: Dual Axis & Box Plot")
st.write("Fitur Lengkap: Dual Axis (Kiri/Kanan), Box & Whisker, dan lainnya.")

# --- 2. Fungsi Load Data ---
@st.cache_data
def load_data(file):
    try:
        df_raw = pd.read_excel(file)
        # Hapus baris satuan (misal baris pertama isi 'Mpa', 'm/s')
        first_val = df_raw.iloc[0, 0]
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
        
        # Bagi layar jadi 2 kolom (Kiri: Setting, Kanan: Gambar)
        col_settings, col_preview = st.columns([1, 2])
        
        with col_settings:
            st.header("⚙️ Pengaturan")
            
            # --- PILIHAN JENIS GRAFIK ---
            chart_type = st.selectbox(
                "Pilih Jenis Grafik",
                [
                    "📈 Line Chart (Dual Axis)", 
                    "📦 Box & Whisker Plot",   # <--- FITUR BARU
                    "📊 Bar Chart", 
                    "🔵 Scatter Plot", 
                    "🥧 Pie Chart", 
                    "🔥 Heatmap (Korelasi)"
                ]
            )
            
            st.divider()
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # ---------------------------------------------------------
            # 1. LINE CHART (DUAL AXIS)
            # ---------------------------------------------------------
            if chart_type == "📈 Line Chart (Dual Axis)":
                st.info("Info: Grafik ini punya 2 sumbu Y (Kiri & Kanan).")
                x_axis = st.selectbox("Sumbu X (Horizontal)", columns)
                
                col_y1, col_y2 = st.columns(2)
                with col_y1:
                    y_left = st.multiselect("Sumbu KIRI (Utama)", [c for c in columns if c != x_axis])
                with col_y2:
                    y_right = st.multiselect("Sumbu KANAN (Sekunder)", [c for c in columns if c != x_axis and c not in y_left])

                if x_axis and (y_left or y_right):
                    # Plot Kiri
                    if y_left:
                        ax.set_xlabel(x_axis)
                        ax.set_ylabel("Sumbu Kiri", color="tab:blue")
                        for col in y_left:
                            ax.plot(df[x_axis], df[col], label=f"{col} (Kiri)", linestyle='-', marker='o')
                        ax.tick_params(axis='y', labelcolor="tab:blue")

                    # Plot Kanan (Twin Axis)
                    if y_right:
                        ax2 = ax.twinx()
                        ax2.set_ylabel("Sumbu Kanan", color="tab:red")
                        for col in y_right:
                            ax2.plot(df[x_axis], df[col], label=f"{col} (Kanan)", color='tab:red', linestyle='--', marker='x')
                        ax2.tick_params(axis='y', labelcolor="tab:red")
                    
                    ax.set_title(f"Grafik Dual Axis: {x_axis}")

            # ---------------------------------------------------------
            # 2. BOX & WHISKER PLOT (FITUR BARU)
            # ---------------------------------------------------------
            elif chart_type == "📦 Box & Whisker Plot":
                st.info("Box Plot menunjukkan Minimum, Kuartil, Median, dan Maximum.")
                
                target_cols = st.multiselect("Pilih Data untuk Dianalisis", columns)
                orientasi = st.radio("Orientasi Grafik", ["Vertikal (Berdiri)", "Horizontal (Tidur)"])
                
                if target_cols:
                    if orientasi == "Vertikal (Berdiri)":
                        sns.boxplot(data=df[target_cols], orient='v', ax=ax, palette="Set2")
                    else:
                        sns.boxplot(data=df[target_cols], orient='h', ax=ax, palette="Set2")
                    
                    ax.set_title("Box & Whisker Plot (Analisis Sebaran Data)")

            # ---------------------------------------------------------
            # 3. BAR CHART
            # ---------------------------------------------------------
            elif chart_type == "📊 Bar Chart":
                x_axis = st.selectbox("Sumbu Label", columns)
                y_axis = st.multiselect("Sumbu Data", [c for c in columns if c != x_axis])
                if x_axis and y_axis:
                    df.plot(kind='bar', x=x_axis, y=y_axis, ax=ax)

            # ---------------------------------------------------------
            # 4. SCATTER PLOT
            # ---------------------------------------------------------
            elif chart_type == "🔵 Scatter Plot":
                x_axis = st.selectbox("Sumbu X", columns)
                y_axis = st.multiselect("Sumbu Y", [c for c in columns if c != x_axis])
                if x_axis and y_axis:
                    for col in y_axis:
                        ax.scatter(df[x_axis], df[col], label=col, alpha=0.7)

            # ---------------------------------------------------------
            # 5. PIE CHART
            # ---------------------------------------------------------
            elif chart_type == "🥧 Pie Chart":
                label_col = st.selectbox("Label Kategori", columns)
                value_col = st.selectbox("Nilai Angka", [c for c in columns if c != label_col])
                if label_col and value_col:
                    data_pie = df.groupby(label_col)[value_col].sum()
                    ax.pie(data_pie, labels=data_pie.index, autopct='%1.1f%%', startangle=90)

            # ---------------------------------------------------------
            # 6. HEATMAP
            # ---------------------------------------------------------
            elif chart_type == "🔥 Heatmap (Korelasi)":
                sns.heatmap(df.corr(), annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
                ax.set_title("Matriks Korelasi Antar Data")

            # --- FINISHING & LEGENDA ---
            st.divider()
            tampilkan_grid = st.checkbox("Tampilkan Grid", value=True)
            dpi
