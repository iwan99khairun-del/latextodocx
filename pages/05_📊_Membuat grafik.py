import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io

# --- 1. Konfigurasi Halaman ---
st.set_page_config(page_title="Studio Grafik Pro", layout="wide")
st.title("📊 Studio Grafik Pro: All-in-One")
st.write("Upload Excel, pilih jenis visualisasi, dan download hasilnya.")

# --- 2. Fungsi Load Data ---
@st.cache_data
def load_data(file):
    try:
        df_raw = pd.read_excel(file)
        # Pembersihan Data (Hapus baris satuan jika ada)
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
        
        # Layout 2 Kolom
        col_settings, col_preview = st.columns([1, 2])
        
        with col_settings:
            st.header("⚙️ Pengaturan")
            
            # PILIH JENIS GRAFIK
            chart_category = st.selectbox(
                "Pilih Jenis Grafik",
                [
                    "📈 Line & Area (Tren)", 
                    "📊 Bar & Column (Perbandingan)", 
                    "🔵 Scatter Plot (Hubungan)", 
                    "🥧 Pie & Donut (Komposisi)", 
                    "📦 Box & Histogram (Distribusi)",
                    "🔥 Heatmap (Korelasi)"
                ]
            )
            
            st.divider()
            
            # --- LOGIKA UI DINAMIS ---
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # 1. LINE & AREA
            if "Line & Area" in chart_category:
                chart_type = st.radio("Style", ["Line Chart", "Area Chart"])
                x_axis = st.selectbox("Sumbu X", columns)
                y_axis = st.multiselect("Sumbu Y", [c for c in columns if c != x_axis])
                
                if x_axis and y_axis:
                    if chart_type == "Line Chart":
                        for col in y_axis:
                            ax.plot(df[x_axis], df[col], marker='o', label=col)
                    else:
                        df.plot(kind='area', x=x_axis, y=y_axis, ax=ax, alpha=0.5)

            # 2. BAR CHART
            elif "Bar & Column" in chart_category:
                orientasi = st.radio("Orientasi", ["Vertikal", "Horizontal"])
                x_axis = st.selectbox("Sumbu Label", columns)
                y_axis = st.multiselect("Sumbu Data", [c for c in columns if c != x_axis])
                
                if x_axis and y_axis:
                    kind = 'bar' if orientasi == "Vertikal" else 'barh'
                    df.plot(kind=kind, x=x_axis, y=y_axis, ax=ax)

            # 3. SCATTER PLOT
            elif "Scatter" in chart_category:
                x_axis = st.selectbox("Sumbu X", columns)
                y_axis = st.multiselect("Sumbu Y", [c for c in columns if c != x_axis])
                
                if x_axis and y_axis:
                    for col in y_axis:
                        ax.scatter(df[x_axis], df[col], label=col, alpha=0.7)

            # 4. PIE CHART
            elif "Pie" in chart_category:
                label_col = st.selectbox("Label", columns)
                value_col = st.selectbox("Nilai", [c for c in columns if c != label_col])
                donut = st.checkbox("Donut Chart?")
                
                if label_col and value_col:
                    data_pie = df.groupby(label_col)[value_col].sum()
                    if donut:
                        ax.pie(data_pie, labels=data_pie.index, autopct='%1.1f%%', wedgeprops={'width':0.4})
                    else:
                        ax.pie(data_pie, labels=data_pie.index, autopct='%1.1f%%')

            # 5. DISTRIBUSI
            elif "Box" in chart_category:
                dist_type = st.radio("Tipe", ["Histogram", "Box Plot", "Violin Plot"])
                target_cols = st.multiselect("Pilih Data", columns)
                
                if target_cols:
                    if dist_type == "Histogram":
                        for col in target_cols:
                            sns.histplot(df[col], kde=True, ax=ax, label=col)
                    elif dist_type == "Box Plot":
                        sns.boxplot(data=df[target_cols], ax=ax, orient='h')
                    elif dist_type == "Violin Plot":
                        sns.violinplot(data=df[target_cols], ax=ax, orient='h')

            # 6. HEATMAP
            elif "Heatmap" in chart_category:
                sns.heatmap(df.corr(), annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
                ax.set_title("Korelasi Data")

            # --- FINISHING ---
            st.divider()
            tampilkan_grid = st.checkbox("Tampilkan Grid", value=True)
            dpi = st.number_input("Resolusi Download (DPI)", 100, 901, 300)

            if tampilkan_grid and "Pie" not in chart_category and "Heatmap" not in chart_category:
                ax.grid(True, linestyle='--', alpha=0.5)
            
            if "Heatmap" not in chart_category and "Pie" not in chart_category:
                 ax.legend(bbox_to_anchor=(1, 1), loc='upper left')

        # --- 4. PREVIEW & DOWNLOAD ---
        with col_preview:
            st.subheader("🖼️ Hasil Grafik")
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
    st.info("👋 Silakan upload file Excel di atas.")
