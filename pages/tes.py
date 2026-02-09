import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io

# --- 1. Konfigurasi Halaman ---
st.set_page_config(page_title="Studio Grafik Pro", layout="wide")
st.title("📊 Studio Grafik: Dual Axis & Jitter Plot")
st.write("Fitur Baru: Box Plot kini bisa menampilkan titik-titik data asli (Dots).")

# --- 2. Fungsi Load Data ---
@st.cache_data
def load_data(file):
    try:
        df_raw = pd.read_excel(file)
        
        # Bersihkan kolom "Unnamed" atau sisa index
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
        
        # Layout 2 Kolom
        col_settings, col_preview = st.columns([1, 2])
        
        with col_settings:
            st.header("⚙️ Pengaturan")
            
            # --- PILIHAN JENIS GRAFIK ---
            chart_type = st.selectbox(
                "Pilih Jenis Grafik",
                [
                    "📦 Box & Whisker Plot (Dengan Dots)", # <--- NAMA BARU
                    "📈 Line Chart (Dual Axis)", 
                    "📊 Bar Chart", 
                    "🔵 Scatter Plot", 
                    "🥧 Pie Chart", 
                    "🔥 Heatmap"
                ]
            )
            
            st.divider()
            
            # Variabel DPI & Grid
            dpi = st.number_input("Resolusi Gambar (DPI)", 100, 600, 300)
            tampilkan_grid = st.checkbox("Tampilkan Grid", value=True)
            
            st.divider()

            fig, ax = plt.subplots(figsize=(10, 6))
            
            # ---------------------------------------------------------
            # 1. BOX & WHISKER PLOT (DENGAN DOTS/TITIK)
            # ---------------------------------------------------------
            if chart_type == "📦 Box & Whisker Plot (Dengan Dots)":
                st.info("Tips: Centang 'Tampilkan Dots' untuk melihat sebaran titik data asli.")
                
                target_cols = st.multiselect("Pilih Data (Kolom)", columns)
                
                # Opsi Tambahan Khusus Box Plot
                col_opt1, col_opt2 = st.columns(2)
                with col_opt1:
                    orientasi = st.radio("Arah", ["Vertikal", "Horizontal"])
                with col_opt2:
                    show_dots = st.checkbox("Tampilkan Dots (Titik Data)", value=True)
                
                if target_cols:
                    # 1. Gambar Kotaknya (Box Plot)
                    # Kami gunakan warna agak transparan (boxprops) supaya titiknya kelihatan
                    if orientasi == "Vertikal":
                        sns.boxplot(data=df[target_cols], orient='v', ax=ax, palette="Pastel1", showfliers=False)
                        
                        # 2. Gambar Titiknya (Strip Plot / Jitter)
                        if show_dots:
                            sns.stripplot(data=df[target_cols], orient='v', ax=ax, color='black', alpha=0.6, jitter=True, size=5)
                            
                    else: # Horizontal
                        sns.boxplot(data=df[target_cols], orient='h', ax=ax, palette="Pastel1", showfliers=False)
                        
                        # 2. Gambar Titiknya (Strip Plot / Jitter)
                        if show_dots:
                            sns.stripplot(data=df[target_cols], orient='h', ax=ax, color='black', alpha=0.6, jitter=True, size=5)
                    
                    ax.set_title("Distribusi Data dengan Titik Sampel")

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

            elif chart_type == "🔥 Heatmap":
                sns.heatmap(df.corr(), annot=True, cmap="coolwarm", fmt=".2f", ax=ax)

            # --- FINISHING ---
            if tampilkan_grid and chart_type != "🥧 Pie Chart" and chart_type != "🔥 Heatmap":
                ax.grid(True, linestyle='--', alpha=0.5)
            
            # Legend Logic
            if chart_type == "📈 Line Chart (Dual Axis)" and (y_left or y_right):
                lines1, labels1 = ax.get_legend_handles_labels()
                if 'ax2' in locals():
                    lines2, labels2 = ax2.get_legend_handles_labels()
                    ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left', bbox_to_anchor=(1.05, 1))
                else:
                    ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1))
            elif chart_type not in ["📦 Box & Whisker Plot (Dengan Dots)", "🥧 Pie Chart", "🔥 Heatmap"]:
                ax.legend(bbox_to_anchor=(1, 1))

        # --- 4. DOWNLOAD ---
        with col_preview:
            st.subheader("🖼️ Hasil Grafik")
            st.pyplot(fig)
            
            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches='tight', dpi=dpi)
            buf.seek(0)
            
            st.download_button(
                label=f"⬇️ Download Grafik ({dpi} DPI)",
                data=buf,
                file_name="grafik_box_jitter.png",
                mime="image/png",
                use_container_width=True
            )
    else:
        st.error("Data Excel kosong atau rusak.")
else:
    st.info("Upload file Excel dulu ya Pak.")
