import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io
import re
from datetime import datetime

# ── SETUP HALAMAN ──
st.set_page_config(page_title="Boxplot Editor - Asli vs Edit", layout="wide")
st.title("📊 Box-and-Whisker Plot Editor (Asli vs Custom)")
st.markdown("""
<style>
    .stNumberInput input { background-color: #f8f9fa; }
    .block-container { padding-top: 1.5rem; }
    .stButton button { width: 100%; }
</style>
""", unsafe_allow_html=True)

# ── FUNGSI HELPER ──
def natural_sort_key(s):
    s = str(s)
    match = re.search(r'(\d+)', s)
    return int(match.group(1)) if match else s

# ── UPLOAD FILE ──
uploaded_file = st.file_uploader("Upload file .csv atau .xlsx", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        # Baca data
        if uploaded_file.name.lower().endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        df.columns = df.columns.astype(str).str.strip()
        df = df.loc[:, ~df.columns.str.contains(r'^Unnamed')]

        # Pilih kolom
        col1, col2 = st.columns(2)
        with col1:
            x_col = st.selectbox("Kolom kategori (sumbu X)", df.columns.tolist(), key="xcol")
        with col2:
            y_col = st.selectbox("Kolom nilai numerik (sumbu Y)", df.columns.tolist(), 
                               index=min(1, len(df.columns)-1), key="ycol")

        if x_col and y_col:
            current_state_key = f"{uploaded_file.name}__{x_col}__{y_col}"

            # Reset session jika file atau kolom berubah
            if 'prev_state_key' not in st.session_state or st.session_state.prev_state_key != current_state_key:
                st.session_state.data_config = {}
                st.session_state.original_stats = {}
                st.session_state.prev_state_key = current_state_key

            df[y_col] = pd.to_numeric(df[y_col], errors='coerce')
            df = df.dropna(subset=[x_col, y_col])

            # Urutkan kategori secara natural
            categories = sorted(df[x_col].unique(), key=natural_sort_key)
            cat_strings = [str(c) for c in categories]

            # Inisialisasi statistik asli & config edit
            for cat in categories:
                cat_str = str(cat)
                if cat_str not in st.session_state.original_stats:
                    subset = df[df[x_col] == cat][y_col]
                    if len(subset) == 0:
                        continue
                    desc = subset.describe()

                    stats = {
                        'n': len(subset),
                        'med': float(desc['50%']),
                        'q1': float(desc['25%']),
                        'q3': float(desc['75%']),
                        'whislo': float(desc['min']),
                        'whishi': float(desc['max']),
                        'width': 0.65
                    }

                    st.session_state.original_stats[cat_str] = stats.copy()
                    st.session_state.data_config[cat_str] = stats.copy()

            # ── LAYOUT ──
            st.divider()
            left_col, right_col = st.columns([1, 2.2])

            # ── KIRI : Pengaturan ──
            with left_col:
                with st.expander("Pengaturan grafik (global)", expanded=False):
                    fig_width = st.slider("Lebar figure", 4.0, 16.0, 9.0, 0.5)
                    fig_height = st.slider("Tinggi figure", 3.0, 12.0, 6.0, 0.5)
                    point_size = st.slider("Ukuran titik", 4, 80, 25, 2)
                    jitter_amount = st.slider("Jitter", 0.00, 0.50, 0.12, 0.01)
                    random_seed = st.number_input("Random seed", value=42, step=1)

                    if st.button("Reset SEMUA ke nilai asli", type="primary"):
                        st.session_state.data_config = {}
                        st.rerun()

                st.subheader("Edit per kelompok")

                selected_group = st.selectbox(
                    "Pilih kelompok yang ingin diedit",
                    options=cat_strings
                )

                if selected_group:
                    edit_conf = st.session_state.data_config[selected_group]
                    orig_conf = st.session_state.original_stats[selected_group]

                    st.info(f"**Kelompok:** {selected_group}   (n = {orig_conf['n']})")

                    if st.button(f"Reset {selected_group} ke nilai asli"):
                        st.session_state.data_config[selected_group] = orig_conf.copy()
                        st.rerun()

                    new_width = st.slider(
                        "Lebar kotak",
                        0.15, 1.0, float(edit_conf['width']), 0.05,
                        key=f"width_{selected_group}"
                    )

                    cA, cB = st.columns(2)
                    with cA:
                        new_q3 = st.number_input("Q3", value=float(edit_conf['q3']), format="%.4f",
                                               key=f"q3_{selected_group}")
                        new_q1 = st.number_input("Q1", value=float(edit_conf['q1']), format="%.4f",
                                               key=f"q1_{selected_group}")
                    with cB:
                        new_med = st.number_input("Median", value=float(edit_conf['med']), format="%.4f",
                                                key=f"med_{selected_group}")

                    # Simpan perubahan ke config edit
                    st.session_state.data_config[selected_group].update({
                        'width': new_width,
                        'q1': new_q1,
                        'q3': new_q3,
                        'med': new_med
                    })

            # ── KANAN : Grafik + Download ──
            with right_col:
                st.subheader("Preview grafik")

                fig, ax = plt.subplots(figsize=(fig_width, fig_height))

                ax.set_facecolor('#ffffff')

                bxp_list = []
                box_widths = []

                for cat_str in cat_strings:
                    vals = st.session_state.data_config[cat_str]  # ← selalu pakai data edit
                    bxp_list.append({
                        'label': cat_str,
                        'med': vals['med'],
                        'q1': vals['q1'],
                        'q3': vals['q3'],
                        'whislo': vals['whislo'],
                        'whishi': vals['whishi'],
                        'fliers': []
                    })
                    box_widths.append(vals['width'])

                ax.bxp(bxp_list,
                       positions=range(1, len(cat_strings)+1),
                       widths=box_widths,
                       showfliers=False,
                       patch_artist=True,
                       boxprops=dict(facecolor='#d9e6ff', edgecolor='#4a6fa5'),
                       medianprops=dict(color='#d32f2f', linewidth=2.5),
                       whiskerprops=dict(color='#4a6fa5'),
                       capprops=dict(color='#4a6fa5'))

                # Scatter titik asli + jitter
                cat_to_pos = {str(c): i+1 for i, c in enumerate(categories)}
                df['pos'] = df[x_col].astype(str).map(cat_to_pos)

                np.random.seed(random_seed)
                jitter = np.random.uniform(-jitter_amount, jitter_amount, len(df))

                ax.scatter(df['pos'] + jitter, df[y_col],
                           s=point_size, color='orange', edgecolor='darkred',
                           alpha=0.7, linewidth=0.6, zorder=10)

                ax.set_xticks(range(1, len(cat_strings)+1))
                ax.set_xticklabels(cat_strings, rotation=45, ha='right')
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)
                ax.grid(True, axis='y', alpha=0.3, linestyle='--')

                st.pyplot(fig)

                st.divider()
                st.subheader("Download")

                dcol1, dcol2, dcol3 = st.columns([2, 1.3, 1.3])

                with dcol1:
                    dpi_choice = st.selectbox("Resolusi gambar (DPI)", [150, 300, 600, 900], index=1)

                with dcol2:
                    buf_img = io.BytesIO()
                    fig.savefig(buf_img, dpi=dpi_choice, bbox_inches='tight', format='png')
                    buf_img.seek(0)

                    st.download_button(
                        label="⬇️ Grafik (PNG)",
                        data=buf_img,
                        file_name=f"boxplot_{datetime.now().strftime('%Y%m%d_%H%M')}.png",
                        mime="image/png",
                        use_container_width=True
                    )

                with dcol3:
                    # ── Download Data Asli ──
                    asli_rows = []
                    for cat_str in cat_strings:
                        o = st.session_state.original_stats[cat_str]
                        asli_rows.append({
                            'Group': cat_str,
                            'n': o['n'],
                            'Median': round(o['med'], 4),
                            'Q1': round(o['q1'], 4),
                            'Q3': round(o['q3'], 4),
                            'Min_whisker': round(o['whislo'], 4),
                            'Max_whisker': round(o['whishi'], 4),
                            'Lebar_kotak': round(o['width'], 3)
                        })

                    df_asli = pd.DataFrame(asli_rows)

                    buf_asli = io.BytesIO()
                    df_asli.to_csv(buf_asli, index=False, encoding='utf-8-sig')
                    buf_asli.seek(0)

                    st.download_button(
                        label="⬇️ Data Asli (original)",
                        data=buf_asli,
                        file_name=f"boxplot_original_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv",
                        use_container_width=True,
                        help="Statistik langsung dari file upload"
                    )

                    # ── Download Data Edit / Custom ──
                    edit_rows = []
                    for cat_str in cat_strings:
                        e = st.session_state.data_config[cat_str]
                        edit_rows.append({
                            'Group': cat_str,
                            'n': e['n'],
                            'Median': round(e['med'], 4),
                            'Q1': round(e['q1'], 4),
                            'Q3': round(e['q3'], 4),
                            'Min_whisker': round(e['whislo'], 4),
                            'Max_whisker': round(e['whishi'], 4),
                            'Lebar_kotak': round(e['width'], 3)
                        })

                    df_edit = pd.DataFrame(edit_rows)

                    buf_edit = io.BytesIO()
                    df_edit.to_csv(buf_edit, index=False, encoding='utf-8-sig')
                    buf_edit.seek(0)

                    st.download_button(
                        label="⬇️ Data Edit (custom)",
                        data=buf_edit,
                        file_name=f"boxplot_edited_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv",
                        use_container_width=True,
                        help="Statistik yang digunakan di grafik (hasil edit)"
                    )

    except Exception as err:
        st.error(f"Terjadi kesalahan: {err}")
        if st.button("Reset aplikasi"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
