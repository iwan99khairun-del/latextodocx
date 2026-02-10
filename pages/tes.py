import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io
import re

# --- SETUP HALAMAN ---
st.set_page_config(page_title="Replika R - Edit Per Group", layout="wide")
st.title("📊 Grafik Box-and-Whisker Plot")

# --- FUNGSI PENGURUTAN ALAMI ---
def natural_sort_key(s):
    s = str(s)
    angka = re.search(r'(\d+)', s)
    if angka: return int(angka.group(1))
    return s

# --- 1. UPLOAD FILE ---
uploaded_file = st.file_uploader("Upload File Excel/CSV", type=["xlsx", "csv"])

if uploaded_file:
    try:
        # OTOMATISASI: Mencoba baca dengan desimal titik atau koma
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, header=0, sep=None, engine='python')
        else:
            df = pd.read_excel(uploaded_file, header=0)

        df.columns = df.columns.astype(str).str.strip()
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        
        # --- PILIH KOLOM ---
        c1, c2 = st.columns(2)
        with c1:
            x_col = st.selectbox("Sumbu X (Kategori):", df.columns, key="x_col_select")
        with c2:
            y_col = st.selectbox("Sumbu Y (Angka):", df.columns, index=1 if len(df.columns) > 1 else 0, key="y_col_select")

        if x_col and y_col:
            # Konversi paksa ke angka, tangani koma sebagai desimal jika perlu
            if df[y_col].dtype == 'object':
                df[y_col] = df[y_col].str.replace(',', '.')
            df[y_col] = pd.to_numeric(df[y_col], errors='coerce')
            df = df.dropna(subset=[x_col, y_col])

            # Logic Reset
            curr_state = f"{x_col}_{y_col}_{uploaded_file.name}"
            if 'last_key' not in st.session_state or st.session_state['last_key'] != curr_state:
                st.session_state['data_config'] = {}
                st.session_state['last_key'] = curr_state

            raw_cats = df[x_col].unique()
            cats = sorted(raw_cats, key=natural_sort_key)

            if 'data_config' not in st.session_state:
                st.session_state['data_config'] = {}
            
            # Hitung Statistik Awal
            for cat in cats:
                cat_str = str(cat)
                if cat_str not in st.session_state['data_config']:
                    sub = df[df[x_col] == cat][y_col]
                    s = sub.describe()
                    # Proteksi jika data cuma 1 atau null
                    st.session_state['data_config'][cat_str] = {
                        'med': float(s.get('50%', 0)),
                        'q1': float(s.get('25%', 0)),
                        'q3': float(s.get('75%', 0)),
                        'whislo': float(s.get('min', 0)),
                        'whishi': float(s.get('max', 0)),
                        'width': 0.65,
                        'count': int(s.get('count', 0))
                    }

            st.write("---")
            col_kiri, col_kanan = st.columns([1, 2])

            with col_kiri:
                with st.expander("1️⃣ Global Settings", expanded=False):
                    fig_w = st.slider("Lebar Gambar", 3.0, 15.0, 6.0)
                    fig_h = st.slider("Tinggi Gambar", 3.0, 10.0, 5.0)
                    point_size = st.slider("Ukuran Titik", 2.0, 15.0, 7.0)
                    jitter_val = st.slider("Jitter", 0.0, 0.4, 0.12)
                    seed_val = st.number_input("Seed", value=42)
                    if st.button("🔄 Reset Semua"):
                        st.session_state['data_config'] = {}
                        st.rerun()

                st.subheader("2️⃣ Edit Kotak")
                pilih_group = st.selectbox("Pilih Group:", options=[str(c) for c in cats])

                if pilih_group:
                    conf = st.session_state['data_config'][pilih_group]
                    
                    if conf['count'] < 2:
                        st.warning(f"⚠️ Grup '{pilih_group}' hanya punya {conf['count']} data. Boxplot akan terlihat datar.")
                    
                    if st.button(f"⏪ Reset {pilih_group}"):
                        del st.session_state['data_config'][pilih_group]
                        st.rerun()

                    # Input dengan step agar mudah diubah
                    new_w = st.slider("Lebar Kotak", 0.1, 1.0, float(conf['width']))
                    new_q3 = st.number_input("Atas (Q3)", value=float(conf['q3']), step=0.01, format="%.4f")
                    new_med = st.number_input("Tengah (Median)", value=float(conf['med']), step=0.01, format="%.4f")
                    new_q1 = st.number_input("Bawah (Q1)", value=float(conf['q1']), step=0.01, format="%.4f")

                    st.session_state['data_config'][pilih_group].update({
                        'width': new_w, 'q3': new_q3, 'q1': new_q1, 'med': new_med
                    })

            with col_kanan:
                st.subheader("🖼️ Preview Grafik")
                fig, ax = plt.subplots(figsize=(fig_w, fig_h))
                
                bxp_stats = []
                list_widths = []
                for cat in cats:
                    c_str = str(cat)
                    cf = st.session_state['data_config'][c_str]
                    bxp_stats.append({
                        'label': c_str, 'med': cf['med'], 'q1': cf['q1'], 'q3': cf['q3'],
                        'whislo': cf['whislo'], 'whishi': cf['whishi'], 'fliers': []
                    })
                    list_widths.append(cf['width'])

                # Render Boxplot
                ax.bxp(bxp_stats, showfliers=False, widths=list_widths, patch_artist=True,
                       boxprops=dict(facecolor='#CCCCCC', edgecolor='#595959'),
                       medianprops=dict(color='red', linewidth=2))

                # Render Jitter Points
                cat_map = {str(c): i+1 for i, c in enumerate(cats)}
                df['x_idx'] = df[x_col].astype(str).apply(lambda x: cat_map[x])
                np.random.seed(seed_val)
                noise = np.random.uniform(-jitter_val, jitter_val, len(df))
                ax.scatter(df['x_idx'] + noise, df[y_col], s=point_size**1.5, c='orange', alpha=0.6)

                ax.set_ylabel(y_col, fontweight='bold')
                st.pyplot(fig)

                # --- DOWNLOAD SECTION ---
                st.write("---")
                d1, d2 = st.columns(2)
                with d1:
                    buf = io.BytesIO()
                    fig.savefig(buf, format="png", dpi=300, bbox_inches='tight')
                    st.download_button("⬇️ Download Gambar", buf.getvalue(), "plot.png")
                with d2:
                    res_df = pd.DataFrame([{'Group': k, **v} for k, v in st.session_state['data_config'].items()])
                    st.download_button("⬇️ Download CSV Statistik", res_df.to_csv(index=False), "statistik.csv")

    except Exception as e:
        st.error(f"Error: {e}")
