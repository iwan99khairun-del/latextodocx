import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import re
from datetime import datetime
import numpy as np

st.set_page_config(page_title="Boxplot Editor - Edit & Upload Kembali", layout="wide")
st.title("📊 Boxplot Editor – Edit Kotak → Download → Upload Lagi → Grafik Sama Persis")

# Fungsi pengurutan natural
def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', str(s))]

# Upload file (sekarang support CSV dan XLSX)
uploaded_file = st.file_uploader(
    "Upload file data mentah (.csv / .xlsx) atau konfigurasi kotak custom (.csv)",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:
    try:
        file_name = uploaded_file.name.lower()

        # Baca file sesuai ekstensi
        if file_name.endswith('.csv'):
            df_upload = pd.read_csv(uploaded_file)
        else:  # .xlsx
            df_upload = pd.read_excel(uploaded_file)

        df_upload.columns = df_upload.columns.str.strip()

        # Deteksi apakah ini file konfigurasi custom (hanya untuk .csv)
        custom_cols = ['Group', 'Median', 'Q1', 'Q3', 'Lebar_kotak']
        is_custom = file_name.endswith('.csv') and all(col in df_upload.columns for col in custom_cols)

        if is_custom:
            # Mode custom: langsung pakai nilai edit sebelumnya
            st.success("✅ File konfigurasi custom (.csv) terdeteksi! Grafik akan pakai kotak yang sudah diedit.")

            config = {}
            groups = []
            for _, row in df_upload.iterrows():
                g = str(row['Group'])
                groups.append(g)
                config[g] = {
                    'med': float(row['Median']),
                    'q1': float(row['Q1']),
                    'q3': float(row['Q3']),
                    'whislo': float(row.get('Min_whisker', row['Q1'] - 1.5*(row['Q3'] - row['Q1']))),
                    'whishi': float(row.get('Max_whisker', row['Q3'] + 1.5*(row['Q3'] - row['Q1']))),
                    'width': float(row['Lebar_kotak'])
                }

            groups = sorted(groups, key=natural_sort_key)
            has_raw_data = False  # Tidak ada scatter di mode custom

        else:
            # Mode data mentah (.csv atau .xlsx)
            st.info("📄 File data mentah terdeteksi. Pilih kolom untuk membuat grafik.")

            col1, col2 = st.columns(2)
            with col1:
                x_col = st.selectbox("Kolom kategori / Group (X)", df_upload.columns)
            with col2:
                y_col = st.selectbox("Kolom nilai numerik (Y)", df_upload.columns, index=1 if len(df_upload.columns) > 1 else 0)

            if x_col and y_col:
                # Bersihkan data
                df_upload[y_col] = pd.to_numeric(df_upload[y_col], errors='coerce')
                df_upload = df_upload.dropna(subset=[x_col, y_col]).copy()

                # Simpan data mentah untuk scatter
                df_raw = df_upload[[x_col, y_col]].copy()

                groups_raw = sorted(df_upload[x_col].unique(), key=natural_sort_key)
                groups = [str(g) for g in groups_raw]

                # Config disimpan di session_state
                if 'config' not in st.session_state:
                    st.session_state.config = {}

                # Reset config jika file baru
                current_key = uploaded_file.name
                if 'last_file' not in st.session_state or st.session_state.last_file != current_key:
                    st.session_state.config = {}
                    st.session_state.last_file = current_key

                for g in groups:
                    if g not in st.session_state.config:
                        sub = df_upload[df_upload[x_col] == g][y_col]
                        desc = sub.describe()
                        st.session_state.config[g] = {
                            'med': float(desc['50%']),
                            'q1': float(desc['25%']),
                            'q3': float(desc['75%']),
                            'whislo': float(desc['min']),
                            'whishi': float(desc['max']),
                            'width': 0.65
                        }

                config = st.session_state.config
                has_raw_data = True

        # Tampilkan grafik jika sudah siap
        if 'groups' in locals() and groups and 'config' in locals():
            st.divider()

            left_col, right_col = st.columns([1, 2.5])

            with left_col:
                with st.expander("Pengaturan Grafik Global", expanded=False):
                    fig_width = st.slider("Lebar gambar", 6.0, 16.0, 10.0, 0.5)
                    fig_height = st.slider("Tinggi gambar", 4.0, 12.0, 6.5, 0.5)
                    if has_raw_data:
                        point_size = st.slider("Ukuran titik scatter", 10, 100, 40, 5)
                        jitter_val = st.slider("Jitter titik", 0.0, 0.4, 0.1, 0.02)
                        seed = st.number_input("Seed random", value=42, step=1)

                # Edit hanya untuk mode data mentah
                if not is_custom:
                    st.subheader("✏️ Edit Kotak per Group")
                    selected_group = st.selectbox("Pilih group", groups)

                    if selected_group:
                        current = config[selected_group]

                        new_width = st.slider("Lebar kotak", 0.2, 1.0, current['width'], 0.05)
                        col_a, col_b = st.columns(2)
                        with col_a:
                            new_q1 = st.number_input("Q1 (bawah)", value=current['q1'], format="%.4f")
                            new_q3 = st.number_input("Q3 (atas)", value=current['q3'], format="%.4f")
                        with col_b:
                            new_med = st.number_input("Median", value=current['med'], format="%.4f")

                        config[selected_group].update({
                            'width': new_width,
                            'q1': new_q1,
                            'q3': new_q3,
                            'med': new_med
                        })

            with right_col:
                st.subheader("🖼️ Preview Grafik")

                fig, ax = plt.subplots(figsize=(fig_width, fig_height))
                ax.set_facecolor('#fafafa')

                # Boxplot dari config (selalu nilai edit)
                bxp_stats = []
                widths = []
                for g in groups:
                    c = config[g]
                    bxp_stats.append({
                        'label': g,
                        'med': c['med'],
                        'q1': c['q1'],
                        'q3': c['q3'],
                        'whislo': c['whislo'],
                        'whishi': c['whishi'],
                        'fliers': []
                    })
                    widths.append(c['width'])

                ax.bxp(bxp_stats, widths=widths, showfliers=False, patch_artist=True,
                       boxprops=dict(facecolor='#bbdefb', edgecolor='#1976d2', linewidth=1.2),
                       medianprops=dict(color='#d32f2f', linewidth=2.5),
                       whiskerprops=dict(color='#1976d2', linewidth=1.2),
                       capprops=dict(color='#1976d2', linewidth=1.2))

                # Scatter jika ada data mentah
                if has_raw_data:
                    np.random.seed(seed)
                    pos_map = {g: i+1 for i, g in enumerate(groups)}
                    df_raw['pos'] = df_raw[x_col].astype(str).map(pos_map)
                    noise = np.random.uniform(-jitter_val, jitter_val, len(df_raw))
                    ax.scatter(df_raw['pos'] + noise, df_raw[y_col],
                               s=point_size, color='orange', edgecolor='darkred', alpha=0.8, zorder=3)

                ax.set_xticks(range(1, len(groups)+1))
                ax.set_xticklabels(groups, rotation=45, ha='right')
                ax.set_xlabel("Group")
                ax.set_ylabel("Nilai")
                ax.grid(True, axis='y', alpha=0.3, linestyle='--')

                st.pyplot(fig)

                # Download
                st.divider()
                st.subheader("⬇️ Download")

                d1, d2 = st.columns(2)

                with d1:
                    dpi = st.selectbox("Resolusi PNG", [200, 300, 600], index=1)
                    buf_img = io.BytesIO()
                    fig.savefig(buf_img, format='png', dpi=dpi, bbox_inches='tight')
                    buf_img.seek(0)
                    st.download_button("📷 Download Grafik PNG",
                                       buf_img,
                                       f"boxplot_{datetime.now().strftime('%Y%m%d_%H%M')}.png",
                                       "image/png")

                with d2:
                    export_data = []
                    for g in groups:
                        c = config[g]
                        export_data.append({
                            'Group': g,
                            'Median': round(c['med'], 4),
                            'Q1': round(c['q1'], 4),
                            'Q3': round(c['q3'], 4),
                            'Min_whisker': round(c['whislo'], 4),
                            'Max_whisker': round(c['whishi'], 4),
                            'Lebar_kotak': round(c['width'], 3)
                        })

                    df_export = pd.DataFrame(export_data)
                    buf_csv = io.BytesIO()
                    df_export.to_csv(buf_csv, index=False, encoding='utf-8-sig')
                    buf_csv.seek(0)

                    st.download_button("📄 Download Konfigurasi Kotak (CSV)",
                                       buf_csv,
                                       f"boxplot_custom_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                                       "text/csv",
                                       help="Upload CSV ini lagi → grafik langsung sama persis!")

    except Exception as e:
        st.error(f"Error: {e}")
        st.info("Pastikan file .xlsx/.csv punya header yang benar dan kolom numerik valid.")

else:
    st.info("Upload file .csv atau .xlsx dulu untuk mulai.")
