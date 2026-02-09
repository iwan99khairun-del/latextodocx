import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io

# --- 1. Konfigurasi Halaman ---
st.set_page_config(page_title="Studio Grafik Pro Max", layout="wide")
st.title("📊 Studio Grafik: Smart Data Support")
st.markdown("""
**Fitur Baru:** Sekarang mendukung 2 jenis format Excel:
1. **Wide Format:** Setiap kategori punya kolom sendiri (Contoh: Kolom A=0gy, Kolom B=5gy).
2. **Long Format:** Satu kolom nama kategori, satu kolom nilai angka (Contoh data Bapak yang tadi).
""")

# --- 2. Fungsi Load Data ---
@st.cache_data
def load_data(file):
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df_raw = pd.read_excel(file)
            # Bersihkan kolom "Unnamed"
            df_raw = df_raw.loc[:, ~df_raw.columns.str.contains('^Unnamed')]
            
            # Cek baris satuan (jika baris pertama teks, hapus)
            first_val = df_raw.iloc[0, 0]
            if isinstance(first_val, str) and not str(first_val).replace('.', '', 1).isdigit():
                df = df_raw.drop(index=0).reset_index(drop=True)
            else:
                df = df_raw
        
        # Coba konversi ke angka (untuk kolom yang memang angka)
        # Kita tidak memaksa semua jadi angka, karena Long Format butuh kolom Teks (Kategori)
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='ignore')
            
        return df
    except Exception as e:
        return None

# --- 3. Upload File ---
uploaded_file = st.file_uploader("Upload File Excel (.xlsx) atau CSV", type=["xlsx", "csv"])

if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    if df is not None:
        columns = df.columns.tolist()
        
        col_settings, col_preview = st.columns([1, 2])
        
        with col_settings:
            st.header("⚙️ Pengaturan")
            
            # --- PILIHAN JENIS GRAFIK ---
            chart_type = st.selectbox(
                "Pilih Jenis Grafik",
                [
                    "📦 Box & Whisker Plot (Smart)", 
                    "📈 Line Chart (Dual Axis)", 
                    "📊 Bar Chart", 
                    "🔵 Scatter Plot", 
                    "🥧 Pie Chart", 
                    "🔥 Heatmap"
                ]
            )
            
            st.divider()
            dpi = st.number_input("Resolusi (DPI)", 100, 901, 300)
            tampilkan_grid = st.checkbox("Tampilkan Grid", value=True)
            st.divider()

            fig, ax = plt.subplots(figsize=(10, 6))
            
            # ---------------------------------------------------------
            # 1. BOX PLOT (SMART MODE)
            # ---------------------------------------------------------
            if chart_type == "📦 Box & Whisker Plot (Smart)":
                st.subheader("Format Data Excel Bapak?")
                data_mode = st.radio("Pilih Model Data:", 
                                     ["Model 1: Kolom Terpisah (Wide)", 
                                      "Model 2: Satu Kolom Kategori (Long)"])
                
                # --- OPSI 1: WIDE FORMAT (Seperti yang dulu) ---
                if data_mode == "Model 1: Kolom Terpisah (Wide)":
                    st.caption("Contoh: Kolom A='Baja', Kolom B='Aluminium'")
                    target_cols = st.multiselect("Pilih Kolom Data", columns)
                    orientasi = st.radio("Arah", ["Vertikal", "Horizontal"])
                    show_dots = st.checkbox("Tampilkan Dots", value=True)
                    
                    if target_cols:
                        if orientasi == "Vertikal":
                            sns.boxplot(data=df[target_cols], orient='v', ax=ax, palette="Pastel1", showfliers=False)
                            if show_dots:
                                sns.stripplot(data=df[target_cols], orient='v', ax=ax, color='black', alpha=0.6, jitter=True, size=5)
                        else:
                            sns.boxplot(data=df[target_cols], orient='h', ax=ax, palette="Pastel1", showfliers=False)
                            if show_dots:
                                sns.stripplot(data=df[target_cols], orient='h', ax=ax, color='black', alpha=0.6, jitter=True, size=5)

                # --- OPSI 2: LONG FORMAT (KHUSUS DATA BAPAK YANG SEKARANG) ---
                else: 
                    st.caption("Contoh: Kolom A='Dosis' (0gy, 5gy...), Kolom B='Nilai'")
                    cat_col = st.selectbox("Pilih Kolom Kategori (Grup)", columns, index=0)
                    val_col = st.selectbox("Pilih Kolom Nilai (Angka)", columns, index=1 if len(columns)>1 else 0)
                    
                    orientasi = st.radio("Arah Grafik", ["Vertikal", "Horizontal"])
                    show_dots = st.checkbox("Tampilkan Dots Asli", value=True)

                    if cat_col and val_col:
                        try:
                            # Pastikan kolom nilai benar-benar angka
                            df[val_col] = pd.to_numeric(df[val_col], errors='coerce')
                            
                            if orientasi == "Vertikal":
                                sns.boxplot(data=df, x=cat_col, y=val_col, ax=ax, palette="Pastel1", showfliers=False)
                                if show_dots:
                                    sns.stripplot(data=df, x=cat_col, y=val_col, ax=ax, color='black', alpha=0.6, jitter=True, size=5)
                                ax.set_xlabel("Kategori / Dosis")
                                ax.set_ylabel("Nilai")
                            else:
                                sns.boxplot(data=df, x=val_col, y=cat_col, ax=ax, palette="Pastel1", showfliers=False)
                                if show_dots:
                                    sns.stripplot(data=df, x=val_col, y=cat_col, ax=ax, color='black', alpha=0.6, jitter=True, size=5)
                                ax.set_xlabel("Nilai")
                                ax.set_ylabel("Kategori / Dosis")
                        except Exception as e:
                            st.error(f"Gagal memproses grafik: {e}")

                ax.set_title("Analisis Box & Whisker Plot")

            # ---------------------------------------------------------
            # 2. LINE CHART (DUAL AXIS)
            # ---------------------------------------------------------
            elif chart_type == "📈 Line Chart (Dual Axis)":
                x_axis = st.selectbox("Sumbu X", columns)
                col_y1, col_y2 = st.columns(2)
                with col_y1:
                    y_left = st.multiselect("Sumbu Kiri (Biru)", [c for c in columns if c != x_axis])
                with col_y2:
                    y_right = st.multiselect("Sumbu Kanan (Merah)", [c for c in columns if c != x_axis and c not in y_left])

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

            # ---------------------------------------------------------
            # 3. OTHER CHARTS
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
            
            elif chart_type == "🔥 Heatmap":
                # Hanya ambil kolom angka
                df_numeric = df.select_dtypes(include=['float64', 'int64'])
                if not df_numeric.empty:
                    sns.heatmap(df_numeric.corr(), annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
                else:
                    st.warning("Heatmap butuh kolom angka. Data Bapak isinya teks semua?")

            # --- FINISHING ---
            if tampilkan_grid and "Pie" not in chart_type and "Heatmap" not in chart_type:
                ax.grid(True, linestyle='--', alpha=0.5)
            
            if chart_type == "📈 Line Chart (Dual Axis)" and (y_left or y_right):
                lines1, labels1 = ax.get_legend_handles_labels()
                if 'ax2' in locals():
                    lines2, labels2 = ax2.get_legend_handles_labels()
                    ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left', bbox_to_anchor=(1.05, 1))
                else:
                    ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1))
            elif "Pie" not in chart_type and "Heatmap" not in chart_type:
                # Cek apakah legend kosong sebelum dipanggil
                if ax.get_legend_handles_labels()[0]:
                    ax.legend(bbox_to_anchor=(1, 1))

        # --- 4. DOWNLOAD ---
        with col_preview:
            st.subheader("🖼️ Preview Grafik")
            st.pyplot(fig)
            
            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches='tight', dpi=dpi)
            buf.seek(0)
            
            st.download_button(
                label=f"⬇️ Download Grafik ({dpi} DPI)",
                data=buf,
                file_name="hasil_grafik_pro.png",
                mime="image/png",
                use_container_width=True
            )
    else:
        st.error("Gagal membaca file. Pastikan format Excel/CSV benar.")
else:
    st.info("👋 Upload file Excel di panel atas.")
