import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io
import re
from datetime import datetime

# ========================= SETUP =========================
st.set_page_config(page_title="Boxplot Custom Editor", layout="wide")
st.title("📊 Box-and-Whisker Plot - Edit per Group")
st.markdown("""
<style>
    .stNumberInput input { background-color: #f0f2f6; }
    .block-container { padding-top: 2rem; }
    .stButton button { width: 100%; }
</style>
""", unsafe_allow_html=True)

# ========================= FUNGSI =========================
def natural_sort_key(s):
    s = str(s)
    angka = re.search(r'(\d+)', s)
    return int(angka.group(1)) if angka else s

# ========================= UPLOAD FILE =========================
uploaded_file = st.file_uploader("Upload File Excel / CSV", type=["xlsx", "csv"])

if uploaded_file:
    try:
        # Baca file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, header=0)
        else:
            df = pd.read_excel(uploaded_file, header=0)

        df.columns = df.columns.astype(str).str.strip()
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        # Pilih kolom
        c1, c2 = st.columns(2)
        with c1:
            x_col = st.selectbox("Sumbu X (Kategori/Group):", df.columns, key="x_col")
        with c2:
            y_col = st.selectbox("Sumbu Y (Nilai Numerik):", df.columns, 
                               index=1 if len(df.columns) > 1 else 0, key="y_col")

        if x_col and y_col:
            # Key untuk reset session saat file/kolom berubah
            current_key = f"{uploaded_file.name}_{x_col}_{y_col}"
            
            if 'last_key' not in st.session_state or st.session_state.last_key != current_key:
                st.session_state.data_config = {}
                st.session_state.original_stats = {}
                st.session_state.last_key = current_key

            # Bersihkan data
            df[y_col] = pd.to_numeric(df[y_col], errors='coerce')
            df = df.dropna(subset=[x_col, y_col])

            raw_cats = df[x_col].unique()
            cats = sorted(raw_cats, key=natural_sort_key)

            # Inisialisasi config
            for cat in cats:
                cat_str = str(cat)
                if cat_str not in st.session_state.data_config:
                    sub_data = df[df[x_col] == cat][y_col]
                    stats = sub_data.describe()
                    
                    config = {
                        'med': float(stats['50%']),
                        'q1': float(stats['25%']),
                        'q3': float(stats['75%']),
                        'whislo': float(stats['min']),
                        'whishi': float(stats['max']),
                        'width': 0.65,
                        'n': int(len(sub_data))
                    }
                    
                    st.session_state.data_config[cat_str] = config.copy()
                    st.session_state.original_stats[cat_str] = config.copy()

            # ====================== LAYOUT ======================
            st.write("---")
            col_kiri, col_kanan = st.columns([1, 2])

            # ==================== KIRI: Pengaturan ====================
            with col_kiri:
                with st.expander("1️⃣ Pengaturan Global", expanded=False):
                    fig_w = st.slider("Lebar Gambar", 4.0, 16.0, 8.0, 0.5)
                    fig_h = st.slider("Tinggi Gambar", 3.0, 10.0, 5.5, 0.5)
                    point_size = st.slider("Ukuran Titik", 3.0, 20.0, 8.0, 0.5)
                    jitter = st.slider("Jitter", 0.0, 0.5, 0.15, 0.01)
                    seed = st.number_input("Seed Random", value=42, step=1)

                    if st.button("🔄 Reset SEMUA ke Data Asli"):
                        st.session_state.data_config = {}
                        st.rerun()

                st.subheader("2️⃣ Edit Kotak per Group")
                pilih_group = st.selectbox("Pilih Group untuk diedit:", 
                                         options=[str(c) for c in cats])

                if pilih_group:
                    conf = st.session_state.data_config[pilih_group]
                    orig = st.session_state.original_stats[pilih_group]

                    st.info(f"**Mengedit:** {pilih_group}  (n = {conf['n']})")

                    if st.button(f"⏪ Reset {pilih_group} ke Asli"):
                        st.session_state.data_config[pilih_group] = orig.copy()
                        st.rerun()

                    new_width = st.slider("Lebar Kotak", 0.1, 1.0, float(conf['width']), 0.05)

                    c1, c2 = st.columns(2)
                    with c1:
                        new_q3 = st.number_input("Q3 (Atas)", value=float(conf['q3']), format="%.4f")
                        new_q1 = st.number_input("Q1 (Bawah)", value=float(conf['q1']), format="%.4f")
                    with c2:
                        new_med = st.number_input("Median", value=float(conf['med']), format="%.4f")

                    # Simpan perubahan
                    st.session_state.data_config[pilih_group].update({
                        'q1': new_q1, 'q3': new_q3, 'med': new_med, 'width': new_width
                    })

            # ==================== KANAN: Grafik + Download ====================
            with col_kanan:
                st.subheader("🖼️ Preview Grafik")

                fig, ax = plt.subplots(figsize=(fig_w, fig_h))
                ax.set_facecolor('white')

                for spine in ax.spines.values():
                    spine.set_color('#555555')
                    spine.set_linewidth(1.2)

                # Buat boxplot stats
                bxp_stats = []
                widths = []
                for cat in cats:
                    cat_str = str(cat)
                    c = st.session_state.data_config[cat_str]
                    bxp_stats.append({
                        'label': cat_str,
                        'med': c['med'],
                        'q1': c['q1'],
                        'q3': c['q3'],
                        'whislo': c['whislo'],
                        'whishi': c['whishi'],
                        'fliers': []
                    })
                    widths.append(c['width'])

                ax.bxp(bxp_stats, showfliers=False, widths=widths,
                       patch_artist=True,
                       boxprops=dict(facecolor='#E0E0E0', edgecolor='#333333'),
                       medianprops=dict(color='red', linewidth=2.5),
                       whiskerprops=dict(color='#333333', linewidth=1.2),
                       capprops=dict(color='#333333', linewidth=1.2))

                # Scatter points
                cat_map = {str(c): i+1 for i, c in enumerate(cats)}
                df['x_idx'] = df[x_col].astype(str).map(cat_map)

                np.random.seed(seed)
                noise = np.random.uniform(-jitter, jitter, len(df))

                ax.scatter(df['x_idx'] + noise, df[y_col],
                           s=point_size**2, c='orange', edgecolor='darkred',
                           linewidth=0.6, alpha=0.85, zorder=3)

                ax.set_xlabel(x_col, fontsize=12, fontweight='bold')
                ax.set_ylabel(y_col, fontsize=12, fontweight='bold')
                ax.grid(True, axis='y', alpha=0.3)

                st.pyplot(fig)

                # ===================== DOWNLOAD =====================
                st.write("---")
                st.subheader("⬇️ Download")

                d1, d2, d3 = st.columns([2, 1.4, 1.4])

                with d1:
                    dpi = st.selectbox("Resolusi Gambar", [300, 600, 900, 1200], index=1)

                with d2:
                    buf_png = io.BytesIO()
                    fig.savefig(buf_png, format='png', dpi=dpi, bbox_inches='tight')
                    buf_png.seek(0)
                    st.download_button(
                        "📸 Download Grafik PNG",
                        buf_png,
                        f"boxplot_custom_{datetime.now().strftime('%Y%m%d_%H%M')}.png",
                        "image/png",
                        use_container_width=True
                    )

                with d3:
                    # Buat data export
                    rows = []
                    for cat_str in sorted(st.session_state.data_config.keys(), key=natural_sort_key):
                        c = st.session_state.data_config[cat_str]
                        o = st.session_state.original_stats[cat_str]

                        changed = (abs(c['med'] - o['med']) > 1e-6 or
                                  abs(c['q1'] - o['q1']) > 1e-6 or
                                  abs(c['q3'] - o['q3']) > 1e-6 or
                                  abs(c['width'] - o['width']) > 1e-6)

                        rows.append({
                            'Group': cat_str,
                            'n': o['n'],
                            'Median_Asli': round(o['med'], 4),
                            'Q1_Asli': round(o['q1'], 4),
                            'Q3_Asli': round(o['q3'], 4),
                            'Min_Asli': round(o['whislo'], 4),
                            'Max_Asli': round(o['whishi'], 4),
                            'Lebar_Asli': round(o['width'], 3),
                            '→': '→',
                            'Median_Hasil': round(c['med'], 4),
                            'Q1_Hasil': round(c['q1'], 4),
                            'Q3_Hasil': round(c['q3'], 4),
                            'Min_Hasil': round(c['whislo'], 4),
                            'Max_Hasil': round(c['whishi'], 4),
                            'Lebar_Hasil': round(c['width'], 3),
                            'Status': 'Diubah' if changed else 'Tidak Berubah'
                        })

                    df_export = pd.DataFrame(rows)

                    buf_csv = io.BytesIO()
                    df_export.to_csv(buf_csv, index=False, encoding='utf-8-sig')
                    buf_csv.seek(0)

                    st.download_button(
                        "📊 Download Data (Asli vs Hasil)",
                        buf_csv,
                        f"boxplot_asli_vs_custom_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        "text/csv",
                        use_container_width=True,
                        help="File ini selalu menyertakan data asli dan hasil edit"
                    )

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
        if st.button("Reset Aplikasi"):
            st.session_state.clear()
            st.rerun()
