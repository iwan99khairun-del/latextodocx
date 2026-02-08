import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io

# --- 1. Konfigurasi Halaman ---
st.set_page_config(page_title="Studio Grafik Pro", layout="wide")
st.title("📊 Studio Grafik Pro: All-in-One")
st.markdown("Upload Excel, pilih jenis visualisasi, dan download hasilnya dalam resolusi tinggi.")

# --- 2. Fungsi Load Data ---
@st.cache_data
def load_data(file):
    df_raw = pd.read_excel(file)
    
    # Pembersihan Data (Hapus baris satuan jika ada)
    first_val = df_raw.iloc[0, 0]
    if isinstance(first_val, str) and not first_val.replace('.', '', 1).isdigit():
        df = df_raw.drop(index=0).reset_index(drop=True)
        st.toast("Baris satuan terdeteksi dan dihapus.", icon="🧹")
    else:
        df = df_raw
    
    # Konversi ke angka
    df = df.apply(pd.to_numeric, errors='coerce')
    return df

# --- 3. Upload File ---
uploaded_file = st.file_uploader("Upload File Excel (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    try:
        df = load_data(uploaded_file)
        columns = df.columns.tolist()
        
        # Layout 2 Kolom
        col_settings, col_preview = st.columns([1, 2])
        
        with col_settings:
            st.header("⚙️ Pengaturan")
            
            # PILIH JENIS GRAFIK DULUAN
            chart_category = st.selectbox(
                "Pilih Jenis Grafik",
                [
                    "📈 Line & Area (Tren)", 
                    "📊 Bar & Column (Perbandingan)", 
                    "fan Scatter Plot (Hubungan)", 
                    "🥧 Pie & Donut (Komposisi)", 
                    "📦 Box & Histogram (Distribusi)",
                    "🔥 Heatmap (Korelasi)"
                ]
            )
            
            st.divider()
            
            # --- LOGIKA UI DINAMIS (Input berubah sesuai grafik) ---
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # 1. LINE & AREA
            if "Line & Area" in chart_category:
                chart_type = st.radio("Style", ["Line Chart", "Area Chart (Stacked)"])
                x_axis = st.selectbox("Sumbu X (Waktu/Kategori)", columns)
                y_axis = st.multiselect("Sumbu Y (Data)", [c for c in columns if c != x_axis])
                
                if x_axis and y_axis:
                    if chart_type == "Line Chart":
                        for col in y_axis:
                            ax.plot(df[x_axis], df[col], marker='o', label=col)
                    else:
                        df.plot(kind='area', x=x_axis, y=y_axis, ax=ax, alpha=0.5)

            # 2. BAR CHART
            elif "Bar & Column" in chart_category:
                orientasi = st.radio("Orientasi", ["Vertikal (Column)", "Horizontal (Bar)"])
                x_axis = st.selectbox("Sumbu Label (Kategori)", columns)
                y_axis = st.multiselect("Sumbu Data (Nilai)", [c for c in columns if c != x_axis])
                
                if x_axis and y_axis:
                    if orientasi == "Vertikal (Column)":
                        df.plot(kind='bar', x=x_axis, y=y_axis, ax=ax)
                    else:
                        df.plot(kind='barh', x=x_axis, y=y_axis, ax=ax)

            # 3. SCATTER PLOT
            elif "Scatter" in chart_category:
                x_axis = st.selectbox("Sumbu X", columns)
                y_axis = st.multiselect("Sumbu Y", [c for c in columns if c != x_axis])
                
                if x_axis and y_axis:
                    for col in y_axis:
                        ax.scatter(df[x_axis], df[col], label=col, alpha=0.7)

            # 4. PIE CHART
            elif "Pie" in chart_category:
                label_col = st.selectbox("Kolom Label (Nama)", columns)
                value_col = st.selectbox("Kolom Nilai (Angka)", [c for c in columns if c != label_col])
                donut = st.checkbox("Buat jadi Donut Chart?")
                
                if label_col and value_col:
                    # Siapkan data (Groupby agar label unik)
                    data_pie = df.groupby(label_col)[value_col].sum()
                    
                    if donut:
                        ax.pie(data_pie, labels=data_pie.index, autopct='%1.1f%%', startangle=90, wedgeprops={'width':0.4})
                    else:
                        ax.pie(data_pie, labels=data_pie.index, autopct='%1.1f%%', startangle=90)

            # 5. DISTRIBUSI (Histogram & Box)
            elif "Box" in chart_category:
                dist_type = st.radio("Tipe", ["Histogram", "Box Plot", "Violin Plot"])
                target_cols = st.multiselect("Pilih Data Analisis", columns)
                
                if target_cols:
                    if dist_type == "Histogram":
                        bins = st.slider("Jumlah Bin", 5, 50, 15)
                        for col in target_cols:
                            sns.histplot(df[col], kde=True, ax=ax, label=col, element="step")
                    elif dist_type == "Box Plot":
                        sns.boxplot(data=df[target_cols], ax=ax, orient='h')
                    elif dist_type == "Violin Plot":
                        sns.violinplot(data=df[target_cols], ax=ax, orient='h')

            # 6. HEATMAP (Korelasi)
            elif "Heatmap" in chart_category:
                st.info("Heatmap akan menghitung korelasi antar semua kolom angka.")
                corr_matrix = df.corr()
                sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
                ax.set_title("Matriks Korelasi Data")

            # --- FINISHING TOUCHES (Grid, Legend, Title) ---
            st.divider()
            judul_grafik = st.text_input("Judul Grafik", "Analisis Data Proyek")
            tampilkan_grid = st.checkbox("Tampilkan Grid", value=True)
            dpi = st.number_input("Resolusi Download (DPI)", 100, 600, 300)

            ax.set_title(judul_grafik, fontsize=14, pad=20)
            if tampilkan_grid and "Pie" not in chart_category and "Heatmap" not in chart_category:
                ax.grid(True, linestyle='--',
