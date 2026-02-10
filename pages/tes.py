import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io
from datetime import datetime
import re

st.set_page_config(page_title="Boxplot Editor - Bisa Upload Kembali", layout="wide")
st.title("📊 Boxplot Editor (Edit → Download → Upload lagi → Grafik sama)")

# ── Fungsi pengurutan natural ──
def natural_sort_key(s):
    s = str(s)
    num = re.search(r'(\d+)', s)
    return int(num.group(1)) if num else s

# ── Upload ──
uploaded = st.file_uploader("Upload CSV data raw atau CSV statistik custom", type=["csv"])

if uploaded is not None:
    try:
        df = pd.read_csv(uploaded)

        # Deteksi apakah ini file statistik custom (bukan data raw)
        custom_columns = {'Group', 'Median', 'Q1', 'Q3', 'Lebar_kotak'}
        if custom_columns.issubset(df.columns):
            # ── Mode: upload hasil edit sebelumnya ──
            st.success("File custom terdeteksi → grafik menggunakan nilai edit kamu")

            data_config = {}
            for _, row in df.iterrows():
                g = str(row['Group'])
                data_config[g] = {
                    'med': float(row['Median']),
                    'q1': float(row['Q1']),
                    'q3': float(row['Q3']),
                    'whislo': float(row.get('Min_whisker', row['Q1'])),
                    'whishi': float(row.get('Max_whisker', row['Q3'])),
                    'width': float(row['Lebar_kotak'])
                }

            groups = sorted(data_config.keys(), key=natural_sort_key)

        else:
            # ── Mode: data raw ──
            st.info("File data raw terdeteksi → pilih kolom dulu")

            col1, col2 = st.columns(2)
            x_col = col1.selectbox("Kolom kategori (X)", df.columns)
            y_col = col2.selectbox("Kolom nilai (Y)", df.columns, index=1)

            if x_col and y_col:
                df[y_col] = pd.to_numeric(df[y_col], errors='coerce')
                df = df.dropna(subset=[x_col, y_col])

                groups_raw = sorted(df[x_col].unique(), key=natural_sort_key)
                groups = [str(g) for g in groups_raw]

                data_config = {}
                for g_str in groups:
                    sub = df[df[x_col] == g_str][y_col]
                    desc = sub.describe()
                    data_config[g_str] = {
                        'med': float(desc['50%']),
                        'q1': float(desc['25%']),
                        'q3': float(desc['75%']),
                        'whislo': float(desc['min']),
                        'whishi': float(desc['max']),
                        'width': 0.65
                    }

        # ── Jika sudah punya data_config ──
        if 'data_config' in locals() and data_config:
            st.divider()

            left, right = st.columns([1, 2.5])

            with left:
                # Pengaturan global
                with st.expander("Pengaturan grafik", expanded=False):
                    fig_w = st.slider("Lebar gambar", 5.0, 15.0, 9.0, 0.5)
                    fig_h = st.slider("Tinggi gambar", 4.0, 10.0, 6.0, 0.5)
                    pt_size = st.slider("Ukuran titik", 10, 80, 30, 5)
                    jitter = st.slider("Jitter titik", 0.0, 0.4, 0.08, 0.02)

                # Edit per group (hanya jika mode data raw)
                if 'x_col' in locals():
                    st.subheader("Edit kotak")
                    sel = st.selectbox("Pilih group", groups)

                    if sel:
                        conf = data_config[sel]

                        new_w = st.slider(f"Lebar kotak {sel}", 0.3, 1.0, conf['width'], 0.05)

                        c1, c2 = st.columns(2)
                        with c1:
                            q3 = st.number_input(f"Q3 {sel}", value=conf['q3'], format="%.4f")
                            q1 = st.number_input(f"Q1 {sel}", value=conf['q1'], format="%.4f")
                        with c2:
                            med = st.number_input(f"Median {sel}", value=conf['med'], format="%.4f")

                        # Simpan perubahan
                        data_config[sel]['width'] = new_w
                        data_config[sel]['q1'] = q1
                        data_config[sel]['q3'] = q3
                        data_config[sel]['med'] = med

            with right:
                st.subheader("Grafik")

                fig, ax = plt.subplots(figsize=(fig_w, fig_h))

                stats = []
                ws = []
                for g in groups:
                    c = data_config[g]
                    stats.append({
                        'label': g,
                        'med': c['med'],
                        'q1': c['q1'],
                        'q3': c['q3'],
                        'whislo': c['whislo'],
                        'whishi': c['whishi'],
                        'fliers': []
                    })
                    ws.append(c['width'])

                ax.bxp(stats, widths=ws, showfliers=False, patch_artist=True,
                       boxprops=dict(facecolor='#bbdefb', edgecolor='#0d47a1'),
                       medianprops=dict(color='#c62828', linewidth=2.5))

                ax.set_xticklabels(groups, rotation=45, ha='right')
                ax.grid(True, axis='y', alpha=0.3)
                st.pyplot(fig)

                # ── Download ──
                st.divider()
                st.subheader("Download")

                col_dpi, col_btn = st.columns([1, 2])

                with col_dpi:
                    dpi = st.selectbox("Resolusi PNG", [200, 300, 400, 600])

                with col_btn:
                    buf_png = io.BytesIO()
                    fig.savefig(buf_png, dpi=dpi, bbox_inches='tight', format='png')
                    buf_png.seek(0)
                    st.download_button("⬇️ Download Grafik PNG", buf_png,
                                       f"boxplot_{datetime.now():%Y%m%d_%H%M}.png",
                                       "image/png")

                    # ── Download statistik custom (untuk upload ulang) ──
                    rows = []
                    for g in groups:
                        c = data_config[g]
                        rows.append({
                            'Group': g,
                            'Median': round(c['med'], 4),
                            'Q1': round(c['q1'], 4),
                            'Q3': round(c['q3'], 4),
                            'Min_whisker': round(c['whislo'], 4),
                            'Max_whisker': round(c['whishi'], 4),
                            'Lebar_kotak': round(c['width'], 3)
                        })

                    df_out = pd.DataFrame(rows)

                    buf_csv = io.BytesIO()
                    df_out.to_csv(buf_csv, index=False, encoding='utf-8-sig')
                    buf_csv.seek(0)

                    st.download_button(
                        "⬇️ Download Statistik Custom (bisa upload lagi)",
                        buf_csv,
                        f"boxplot_custom_{datetime.now():%Y%m%d_%H%M}.csv",
                        "text/csv",
                        help="Upload file ini lagi nanti → grafik akan sama persis seperti sekarang"
                    )

    except Exception as e:
        st.error(f"Ada masalah: {e}\nCoba upload ulang file atau reset halaman.")

st.caption("Catatan: Saat upload file custom, edit fitur dinonaktifkan sementara (hanya tampil grafik).")
