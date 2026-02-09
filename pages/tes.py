import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io

# --- 1. Konfigurasi Halaman ---
st.set_page_config(page_title="Studio Grafik Lengkap", layout="wide")
st.title("📊 Studio Grafik: Dual Axis & Box Plot")
st.write("Fitur: Dual Axis (Kiri/Kanan), Box Plot, Bar, Scatter, dll.")

# --- 2. Fungsi Load Data ---
@st.cache_data
def load_data(file):
    try:
        df_raw = pd.read_excel(file)
        
        # Bersihkan kolom "Unnamed" jika ada (biasanya sisa index)
        df_raw = df_raw.loc[:, ~df_raw.columns.str.contains('^Unnamed')]

        # Cek baris satuan (jika baris pertama teks, hapus)
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
        
        # Bagi layar jadi 2 kolom
        col_settings, col_preview = st.columns([1, 2])
        
        with col_settings:
            st.header("⚙️ Pengaturan")
            
            # --- PILIH JENIS GRAFIK ---
            chart_type = st.selectbox(
                "Pilih Jenis Grafik",
                [
                    "📈 Line Chart (Dual Axis)", 
                    "📦 Box & Whisker Plot",
                    "📊 Bar Chart", 
                    "🔵 Scatter Plot", 
                    "🥧 Pie Chart", 
                    "🔥 Heatmap (Korelasi)"
                ]
            )
            
            st.divider()
            
            # Variabel DPI didefinisikan LEBIH AWAL agar aman
            dpi = st.number_input("Resolusi Gambar (DPI)", min_value=100, max_value=600, value=300)
            tampilkan_grid = st.checkbox("Tampilkan Grid", value=True)
            
            st.divider()

            fig, ax = plt.subplots(figsize=(10, 6))
            
            # ---------------------------------------------------------
            # 1. LINE CHART (DUAL AXIS)
            # ---------------------------------------------------------
            if chart_type == "📈 Line Chart (Dual Axis)":
                st.info("Mode Dual Axis: Sumbu Kiri & Kanan terpisah.")
                x_axis = st.selectbox("Sumbu X", columns)
                
                col_y1, col_y2 = st.columns(2)
                with col_y1:
                    y_left = st.multiselect("Sumbu Kiri (Biru)", [c for c in columns if c != x_axis])
                with col_y2:
                    y_right = st.multiselect("Sumbu Kanan (Merah)", [c for c in columns if c != x_axis and c not in y_left])

                if x_axis and (y_left or y_right):
                    # Plot Kiri
                    if y_left:
                        ax.set_xlabel(x_axis)
                        ax.set_ylabel("Sumbu Kiri", color="tab:blue")
                        for col in y_left:
                            ax.plot(df[x_axis], df[col], label=f"{col} (Kiri)", linestyle='-', marker='o')
                        ax.tick_params(axis='y', labelcolor="tab:blue")

                    # Plot Kanan
                    if y_right:
                        ax2 = ax.twinx()
                        ax2.set_ylabel("Sumbu Kanan", color="tab:red")
                        for col in y_right:
                            ax2.plot(df[x_axis], df[col], label=f"{col} (Kanan)", color='tab:red', linestyle='--', marker='x')
                        ax2.tick_params(axis='y', labelcolor="tab:red")
                    
                    ax.set_title(f"Dual Axis: {x_axis}")

            # ---------------------------------------------------------
            # 2. BOX PLOT
            # ---------------------------------------------------------
            elif chart_type == "📦 Box & Whisker Plot":
                target_cols = st.multiselect("Pilih Data", columns)
                orientasi = st.radio("Arah", ["Vertikal", "Horizontal"])
                
                if target_cols:
                    if orientasi == "Vertikal":
                        sns.boxplot(data=df[target_cols], orient='v', ax=ax, palette="Set2")
                    else:
                        sns.boxplot(data=df[target_cols], orient='h', ax=ax, palette="Set2")
                    ax.set_title("Analisis Sebaran Data (Box Plot)")

            # ---------------------------------------------------------
            # 3. GRAFIK LAINNYA
            # ---------------------------------------------------------
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

            elif chart_type == "🔥 Heatmap (Korelasi)":
                sns.heatmap(df.corr(), annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
                ax.set_title("Korelasi Data")

            # --- FINISHING ---
            # Grid Logic
            if tampilkan_grid and chart_type not in ["🥧 Pie Chart", "🔥 Heatmap (Korelasi)"]:
                ax.grid(True, linestyle='--', alpha=0.5)
            
            # Legend Logic
            if chart_type == "📈 Line Chart (Dual Axis)" and (y_left or y_right):
                lines1, labels1 = ax.get_legend_handles_labels()
                if 'ax2' in locals():
                    lines2, labels2 = ax2.get_legend_handles_labels()
                    ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left', bbox_to_anchor=(1.05, 1))
                else:
                    ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1))
            elif chart_type not in ["📦 Box & Whisker Plot", "🥧 Pie Chart", "🔥 Heatmap (Korelasi)"]:
                ax.legend(bbox_to_anchor=(1, 1))

        # --- 4. PREVIEW & DOWNLOAD ---
        with col_preview:
            st.subheader("🖼️ Hasil Grafik")
            st.pyplot(fig)
            
            buf = io.BytesIO()
            # Di sini error terjadi sebelumnya, sekarang aman karena dpi sudah ada di atas
            fig.savefig(buf, format="png", bbox_inches='tight', dpi=dpi)
            buf.seek(0)
            
            st.download_button(
                label=f"⬇️ Download Grafik ({dpi} DPI)",
                data=buf,
                file_name="hasil_grafik.png",
                mime="image/png",
                use_container_width=True
            )
    else:
        st.error("Data kosong atau format salah.")
else:
    st.info("Silakan upload file Excel.")
