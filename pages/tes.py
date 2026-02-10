import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io
import re
from datetime import datetime

st.set_page_config(page_title="Boxplot Editor - Custom & Re-upload", layout="wide")
st.title("📊 Box-and-Whisker Plot Editor (bisa upload hasil edit kembali)")

# ── CSS sederhana ──
st.markdown("""
<style>
    .stNumberInput input { background-color: #f8f9fa; }
    .stButton button { width: 100%; }
</style>
""", unsafe_allow_html=True)

def natural_sort_key(s):
    s = str(s)
    m = re.search(r'(\d+)', s)
    return int(m.group(1)) if m else s

# ── Upload file ──
uploaded_file = st.file_uploader("Upload data raw (.csv/.xlsx) atau file statistik custom (.csv)", 
                                 type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        filename = uploaded_file.name.lower()

        # ── Deteksi apakah ini file statistik custom atau data raw ──
        is_custom_stats = False
        required_cols = {'Group', 'Median', 'Q1', 'Q3', 'Lebar_kotak'}

        if filename.endswith('.csv'):
            df_temp = pd.read_csv(uploaded_file)
            if required_cols.issubset(df_temp.columns):
                is_custom_stats = True
                df_stats = df_temp
            else:
                df = df_temp
        else:
            df = pd.read_excel(uploaded_file)

        current_key = f"{uploaded_file.name}__{is_custom_stats}"

        if 'prev_key' not in st.session_state or st.session_state.prev_key != current_key:
            st.session_state.data_config = {}
            st.session_state.original_stats = {}
            st.session_state.prev_key = current_key
            st.session_state.is_custom_mode = is_custom_stats

        if is_custom_stats:
            # ── Mode: upload file hasil edit sebelumnya ──
            st.success("File statistik custom terdeteksi → grafik akan menggunakan nilai yang sudah diedit")
            
            for _, row in df_stats.iterrows():
                group = str(row['Group'])
                st.session_state.data_config[group] = {
                    'n': int(row.get('n', 0)),
                    'med': float(row['Median']),
                    'q1': float(row['Q1']),
                    'q3': float(row['Q3']),
                    'whislo': float(row.get('Min_whisker', row['Q1'] - 1.5*(row['Q3']-row['Q1']))),
                    'whishi': float(row.get('Max_whisker', row['Q3'] + 1.5*(row['Q3']-row['Q1']))),
                    'width': float(row['Lebar_kotak'])
                }
                # original_stats tidak diisi karena ini mode custom
            categories = list(st.session_state.data_config.keys())
            cat_strings = sorted(categories, key=natural_sort_key)

        else:
            # ── Mode normal: data raw ──
            df.columns = df.columns.astype(str).str.strip()
            df = df.loc[:, ~df.columns.str.contains(r'^Unnamed')]

            col1, col2 = st.columns(2)
            with col1:
                x_col = st.selectbox("Kolom kategori (X)", df.columns.tolist())
            with col2:
                y_col = st.selectbox("Kolom nilai (Y)", df.columns.tolist(), index=1)

            if x_col and y_col:
                df[y_col] = pd.to_numeric(df[y_col], errors='coerce')
                df = df.dropna(subset=[x_col, y_col])

                categories = sorted(df[x_col].unique(), key=natural_sort_key)
                cat_strings = [str(c) for c in categories]

                for cat in categories:
                    cat_str = str(cat)
                    if cat_str not in st.session_state.data_config:
                        sub = df[df[x_col] == cat][y_col]
                        desc = sub.describe()
                        stats = {
                            'n': len(sub),
                            'med': float(desc['50%']),
                            'q1': float(desc['25%']),
                            'q3': float(desc['75%']),
                            'whislo': float(desc['min']),
                            'whishi': float(desc['max']),
                            'width': 0.65
                        }
                        st.session_state.data_config[cat_str] = stats.copy()
                        st.session_state.original_stats[cat_str] = stats.copy()

        # ── Jika sudah punya categories ──
        if 'cat_strings' in locals():
            st.divider()
            left, right = st.columns([1, 2.3])

            with left:
                with st.expander("Pengaturan grafik", expanded=False):
                    fig_w = st.slider("Lebar", 5.0, 16.0, 10.0, 0.5)
                    fig_h = st.slider("Tinggi", 4.0, 12.0, 6.5, 0.5)
                    pt_size = st.slider("Ukuran titik", 10, 100, 35, 5)
                    jitter = st.slider("Jitter", 0.0, 0.5, 0.10, 0.02)
                    seed = st.number_input("Seed", value=42)

                    if st.button("Reset semua ke asli"):
                        st.session_state.data_config = {}
                        st.rerun()

                if not is_custom_stats:
                    st.subheader("Edit kotak")
                    sel_group = st.selectbox("Pilih group", cat_strings)

                    if sel_group:
                        conf = st.session_state.data_config[sel_group]
                        orig = st.session_state.original_stats.get(sel_group, conf)

                        st.info(f"Group: {sel_group} (n = {conf['n']})")

                        if st.button(f"Reset {sel_group}"):
                            st.session_state.data_config[sel_group] = orig.copy()
                            st.rerun()

                        new_w = st.slider("Lebar kotak", 0.2, 1.0, float(conf['width']), 0.05)

                        ca, cb = st.columns(2)
                        with ca:
                            q3_new = st.number_input("Q3", value=float(conf['q3']), format="%.4f")
                            q1_new = st.number_input("Q1", value=float(conf['q1']), format="%.4f")
                        with cb:
                            med_new = st.number_input("Median", value=float(conf['med']), format="%.4f")

                        st.session_state.data_config[sel_group].update({
                            'width': new_w, 'q1': q1_new, 'q3': q3_new, 'med': med_new
                        })

            with right:
                st.subheader("Grafik")

                fig, ax = plt.subplots(figsize=(fig_w, fig_h))

                bxp_data = []
                widths = []
                for g in cat_strings:
                    c = st.session_state.data_config[g]
                    bxp_data.append({
                        'label': g,
                        'med': c['med'],
                        'q1': c['q1'],
                        'q3': c['q3'],
                        'whislo': c['whislo'],
                        'whishi': c['whishi'],
                        'fliers': []
                    })
                    widths.append(c['width'])

                ax.bxp(bxp_data, widths=widths, showfliers=False, patch_artist=True,
                       boxprops=dict(facecolor='#e3f2fd', edgecolor='#1976d2'),
                       medianprops=dict(color='#d81b60', linewidth=2.5))

                ax.set_xticklabels(cat_strings, rotation=40, ha='right')
                ax.set_xlabel("Group")
                ax.set_ylabel("Nilai")
                ax.grid(True, axis='y', alpha=0.3)

                st.pyplot(fig)

                st.divider()
                st.subheader("Download")

                c1, c2, c3 = st.columns([2, 1.4, 1.4])

                with c1:
                    dpi = st.selectbox("DPI", [200, 300, 600, 900], index=1)

                with c2:
                    buf = io.BytesIO()
                    fig.savefig(buf, dpi=dpi, bbox_inches='tight', format='png')
                    buf.seek(0)
                    st.download_button("⬇️ Grafik PNG", buf, f"boxplot_{datetime.now():%Y%m%d_%H%M}.png", "image/png")

                with c3:
                    # ── Download data edit (yang bisa di-upload kembali) ──
                    export_rows = []
                    for g in cat_strings:
                        c = st.session_state.data_config[g]
                        export_rows.append({
                            'Group': g,
                            'n': c['n'],
                            'Median': round(c['med'], 4),
                            'Q1': round(c['q1'], 4),
                            'Q3': round(c['q3'], 4),
                            'Min_whisker': round(c['whislo'], 4),
                            'Max_whisker': round(c['whishi'], 4),
                            'Lebar_kotak': round(c['width'], 3)
                        })

                    df_export = pd.DataFrame(export_rows)

                    buf_csv = io.BytesIO()
                    df_export.to_csv(buf_csv, index=False, encoding='utf-8-sig')
                    buf_csv.seek(0)

                    st.download_button(
                        "⬇️ Data Edit (bisa di-upload lagi)",
                        buf_csv,
                        f"boxplot_custom_{datetime.now():%Y%m%d_%H%M}.csv",
                        "text/csv",
                        help="File ini bisa di-upload kembali → grafik akan sama dengan sekarang"
                    )

    except Exception as e:
        st.error(f"Error: {e}")
        if st.button("Reset aplikasi"):
            st.session_state.clear()
            st.rerun()
