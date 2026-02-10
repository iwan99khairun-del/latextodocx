import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import io
import re
from datetime import datetime

# --- SETUP HALAMAN ---
st.set_page_config(page_title="Replika R - Edit Per Group", layout="wide")
st.title("📊 Grafik Box-and-Whisker Plot (Customizable)")
st.markdown("""
<style>
    .stNumberInput input { background-color: #f0f2f6; }
    .block-container { padding-top: 2rem; }
    .stButton button { width: 100%; }
</style>
""", unsafe_allow_html=True)

# --- FUNGSI PENGURUTAN ALAMI ---
def natural_sort_key(s):
    s = str(s)
    angka = re.search(r'(\d+)', s)
    if angka:
        return int(angka.group(1))
    return s

# --- 1. UPLOAD FILE ---
uploaded_file = st.file_uploader("Upload File Excel/CSV", type=["xlsx", "csv"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, header=0)
        else:
            df = pd.read_excel(uploaded_file, header=0)
        
        df.columns = df.columns.astype(str).str.strip()
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
       
        # --- PILIH KOLOM ---
        c1, c2 = st.columns(2)
        with c1:
            x_col = st.selectbox("Sumbu X (Kategori):", df.columns, key="x_col_select")
        with c2:
            y_col = st.selectbox("Sumbu Y (Angka):", df.columns, index=1 if len(df.columns)>1 else 0, key="y_col_select")

        if x_col and y_col:
            current_key = f"{uploaded_file.name}__{x_col}__{y_col}"
            
            # Reset config jika file/kolom berubah
            if 'last_config_key' not in st.session_state or st.session_state.last_config_key != current_key:
                st.session_state.data_config = {}
                st.session_state.last_config_key = current_key
                st.session_state.original_stats = {}   # simpan nilai asli untuk perbandingan

            df[y_col] = pd.to_numeric(df[y_col], errors='coerce')
            df = df.dropna(subset=[x_col, y_col])

            raw_cats = df[x_col].unique()
            cats = sorted(raw_cats, key=natural_sort_key)

            # Inisialisasi data config & simpan original stats
            for cat in cats:
                cat_str = str(cat)
                if cat_str not in st.session_state.data_config:
                    sub = df[df[x_col] == cat][y_col]
                    stats = sub.describe()
                    
                    conf = {
                        'med': float(stats['50%']),
                        'q1': float(stats['25%']),
                        'q3': float(stats['75%']),
                        'whislo': float(stats['min']),
                        'whishi': float(stats['max']),
                        'width': 0.65
                    }
                    st.session_state.data_config[cat_str] = conf
                    
                    # Simpan nilai asli (hanya sekali)
                    if cat_str not in st.session_state.original_stats:
                        st.session_state.original_stats[cat_str] = conf.copy()

            st.write("---")
            col_kiri, col_kanan = st.columns([1, 2])

            with col_kiri:
                # ── GLOBAL SETTINGS ──
                with st.expander("1️⃣ Pengaturan Gambar (Global)", expanded=False):
                    fig_w = st.slider("Lebar Gambar", 3.0, 15.0, 6.0, step=0.5)
                    fig_h = st.slider("Tinggi Gambar", 3.0, 10.0, 5.0, step=0.5)
                    point_size = st.slider("Ukuran Titik", 2.0, 15.0, 7.0, step=0.5)
                    jitter_val = st.slider("Jitter (Sebaran)", 0.0, 0.4, 0.12, step=0.02)
                    seed_val = st.number_input("Seed (Acak)", value=42, step=1)

                    if st.button("🔄 Reset Semua ke Data Asli"):
                        st.session_state.data_config = {}
                        st.session_state.original_stats = {}
                        st.rerun()

                st.subheader("2️⃣ Edit Kotak per Group")
                pilih_group = st.selectbox("Pilih Group:", options=[str(c) for c in cats])

                if pilih_group:
                    st.info(f"Sedang mengedit: **{pilih_group}**")
                    conf = st.session_state.data_config[pilih_group]
                    orig = st.session_state.original_stats[pilih_group]

                    if st.button(f"⏪ Reset {pilih_group} ke nilai asli"):
                        st.session_state.data_config[pilih_group] = orig.copy()
                        st.rerun()

                    new_width = st.slider("Lebar Kotak", 0.1, 1.0, float(conf['width']), step=0.05)

                    c_h1, c_h2 = st.columns(2)
                    with c_h1:
                        new_q3 = st.number_input("Q3 (Atas)", value=float(conf['q3']), format="%.4f")
                        new_q1 = st.number_input("Q1 (Bawah)", value=float(conf['q1']), format="%.4f")
                    with c_h2:
                        new_med = st.number_input("Median", value=float(conf['med']), format="%.4f")

                    # Simpan perubahan
                    st.session_state.data_config[pilih_group].update({
                        'width': new_width,
                        'q3': new_q3,
                        'q1': new_q1,
                        'med': new_med
                    })

            with col_kanan:
                st.subheader("🖼️ Preview Grafik")

                fig, ax = plt.subplots(figsize=(fig_w, fig_h))
                ax.set_facecolor('white')

                for spine in ax.spines.values():
                    spine.set_visible(True)
                    spine.set_color('#595959')
                    spine.set_linewidth(1)

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
                       boxprops=dict(facecolor='#CCCCCC', edgecolor='#595959', linewidth=0.9),
                       medianprops=dict(color='#595959', linewidth=2),
                       whiskerprops=dict(color='#595959', linewidth=0.9),
                       capprops=dict(color='#595959', linewidth=0.9))

                # Scatter points
                cat_map = {str(c): i+1 for i, c in enumerate(cats)}
                df['x_idx'] = df[x_col].astype(str).map(cat_map)
                
                np.random.seed(int(seed_val))
                noise = np.random.uniform(-jitter_val, jitter_val, len(df))

                ax.scatter(df['x_idx'] + noise, df[y_col],
                           s=point_size**1.5,
                           c='orange', edgecolor='red', linewidth=0.7,
                           alpha=0.8, zorder=3)

                ax.set_xlabel(x_col, fontweight='bold')
                ax.set_ylabel(y_col, fontweight='bold')

                st.pyplot(fig)

                # ── DOWNLOAD GRAFIK & DATA ──
                st.write("---")

                col_d1, col_d2, col_d3 = st.columns([2, 1.2, 1.2])

                with col_d1:
                    dpi = st.selectbox("Resolusi Gambar", [150, 300, 600], index=1)

                with col_d2:
                    buf_img = io.BytesIO()
                    fig.savefig(buf_img, format="png", dpi=dpi, bbox_inches='tight')
                    buf_img.seek(0)
                    st.download_button(
                        label="⬇️ Download PNG",
                        data=buf_img,
                        file_name=f"boxplot_custom_{datetime.now().strftime('%Y%m%d_%H%M')}.png",
                        mime="image/png",
                        use_container_width=True
                    )

                with col_d3:
                    # Buat dataframe statistik custom
                    data_rows = []
                    for cat_str in st.session_state.data_config:
                        c = st.session_state.data_config[cat_str]
                        o = st.session_state.original_stats[cat_str]
                        
                        data_rows.append({
                            'Group': cat_str,
                            'Median': round(c['med'], 4),
                            'Q1': round(c['q1'], 4),
                            'Q3': round(c['q3'], 4),
                            'Min (whisker)': round(c['whislo'], 4),
                            'Max (whisker)': round(c['whishi'], 4),
                            'Lebar Kotak': round(c['width'], 3),
                            'Median (asli)': round(o['med'], 4),
                            'Q1 (asli)': round(o['q1'], 4),
                            'Q3 (asli)': round(o['q3'], 4),
                            'Diubah?': 'Ya' if (abs(c['med']-o['med'])>1e-6 or 
                                               abs(c['q1']-o['q1'])>1e-6 or 
                                               abs(c['q3']-o['q3'])>1e-6 or 
                                               abs(c['width']-o['width'])>1e-6) else 'Tidak'
                        })

                    df_export = pd.DataFrame(data_rows)

                    buf_csv = io.BytesIO()
                    df_export.to_csv(buf_csv, index=False, encoding='utf-8-sig')
                    buf_csv.seek(0)

                    st.download_button(
                        label="⬇️ Download Data (CSV)",
                        data=buf_csv,
                        file_name=f"boxplot_stats_custom_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

                    # Opsional: Excel juga bisa ditambahkan
                    # buf_xlsx = io.BytesIO()
                    # with pd.ExcelWriter(buf_xlsx, engine='openpyxl') as writer:
                    #     df_export.to_excel(writer, index=False, sheet_name="Stats")
                    # buf_xlsx.seek(0)
                    # st.download_button("⬇️ Excel", buf_xlsx, "stats_custom.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
        if st.button("Reset Aplikasi"):
            st.session_state.clear()
            st.rerun()
