import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io
import re

# --- SETUP HALAMAN ---
st.set_page_config(page_title="Replika R - Boxplot Pro", layout="wide")
st.title("📊 Grafik Box-and-Whisker Plot")

# --- FUNGSI PENGURUTAN ALAMI ---
def natural_sort_key(s):
    s = str(s)
    angka = re.search(r'(\d+)', s)
    if angka: return int(angka.group(1))
    return s

# --- 1. UPLOAD FILE ---
uploaded_file = st.file_uploader("Upload File Excel/CSV (Data Asli atau Data Edit)", type=["xlsx", "csv"])

if uploaded_file:
    try:
        # Baca Data
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, header=0)
        else:
            df = pd.read_excel(uploaded_file, header=0)

        df.columns = df.columns.astype(str).str.strip()
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        # DETEKSI FILE HASIL EDIT
        is_edited_file = 'Is_Edited_Summary' in df.columns

        if is_edited_file:
            st.success("✅ Menggunakan data hasil edit. Titik scatter akan disimulasikan.")
            x_col = df['Original_X_Label'].iloc[0]
            y_col = df['Original_Y_Label'].iloc[0]
            cats = df['Group_Name'].tolist()
        else:
            c1, c2 = st.columns(2)
            with c1:
                x_col = st.selectbox("Sumbu X (Kategori):", df.columns, key="x_col_select")
            with c2:
                y_col = st.selectbox("Sumbu Y (Angka):", df.columns, index=1 if len(df.columns) > 1 else 0, key="y_col_select")

        if x_col and y_col:
            # RESET LOGIC
            curr_state = f"{x_col}_{y_col}_{uploaded_file.name}"
            if 'last_key' not in st.session_state or st.session_state['last_key'] != curr_state:
                st.session_state['data_config'] = {}
                st.session_state['last_key'] = curr_state

            if not is_edited_file:
                df[y_col] = pd.to_numeric(df[y_col], errors='coerce')
                df = df.dropna(subset=[x_col, y_col])
                raw_cats = df[x_col].unique()
                cats = sorted(raw_cats, key=natural_sort_key)

            if 'data_config' not in st.session_state:
                st.session_state['data_config'] = {}
            
            # INISIALISASI DATA CONFIG
            for _, row in df.iterrows():
                cat_str = str(row['Group_Name']) if is_edited_file else str(row[x_col])
                if cat_str not in st.session_state['data_config'] or 'width' not in st.session_state['data_config'][cat_str]:
                    if is_edited_file:
                        st.session_state['data_config'][cat_str] = {
                            'med': float(row['med']), 'q1': float(row['q1']), 'q3': float(row['q3']),
                            'whislo': float(row['whislo']), 'whishi': float(row['whishi']),
                            'width': float(row['width'])
                        }
                    else:
                        sub = df[df[x_col] == row[x_col]][y_col]
                        stats = sub.describe()
                        st.session_state['data_config'][cat_str] = {
                            'med': float(stats['50%']), 'q1': float(stats['25%']), 'q3': float(stats['75%']),
                            'whislo': float(stats['min']), 'whishi': float(stats['max']), 'width': 0.65
                        }

            st.write("---")
            col_kiri, col_kanan = st.columns([1, 2])

            with col_kiri:
                with st.expander("1️⃣ Pengaturan Global", expanded=True):
                    fig_w = st.slider("Lebar Gambar", 3.0, 15.0, 6.0)
                    fig_h = st.slider("Tinggi Gambar", 3.0, 10.0, 5.0)
                    jitter_val = st.slider("Jitter (Sebaran Titik)", 0.0, 0.4, 0.15)
                    dot_color = st.color_picker("Warna Titik", "#FFA500") 
                    dot_size = st.slider("Ukuran Titik", 2.0, 15.0, 8.0)
                    dot_opacity = st.slider("Transparansi Titik", 0.1, 1.0, 0.6)
                    
                st.subheader("2️⃣ Edit Kotak")
                pilih_group = st.selectbox("Pilih Group:", options=[str(c) for c in cats])
                if pilih_group:
                    conf = st.session_state['data_config'][pilih_group]
                    new_w = st.slider(f"Lebar Kotak", 0.1, 1.0, float(conf['width']))
                    c_h1, c_h2 = st.columns(2)
                    with c_h1:
                        new_q3 = st.number_input("Atas (Q3)", value=float(conf['q3']), format="%.4f")
                        new_q1 = st.number_input("Bawah (Q1)", value=float(conf['q1']), format="%.4f")
                    with c_h2:
                        new_med = st.number_input("Tengah (Median)", value=float(conf['med']), format="%.4f")
                    
                    st.session_state['data_config'][pilih_group].update({
                        'width': new_w, 'q3': new_q3, 'q1': new_q1, 'med': new_med
                    })

            with col_kanan:
                st.subheader("🖼️ Preview Grafik")
                fig, ax = plt.subplots(figsize=(fig_w, fig_h))
                ax.set_facecolor('white')
                
                bxp_stats = []
                list_widths = []
                for cat in cats:
                    c_str = str(cat)
                    c = st.session_state['data_config'][c_str]
                    bxp_stats.append({
                        'label': c_str, 'med': c['med'], 'q1': c['q1'], 'q3': c['q3'],
                        'whislo': c['whislo'], 'whishi': c['whishi'], 'fliers': []
                    })
                    list_widths.append(c['width'])

                # Render Boxplot (Z-order rendah agar di bawah titik)
                ax.bxp(bxp_stats, showfliers=False, widths=list_widths, patch_artist=True,
                       boxprops=dict(facecolor='#E6E6E6', edgecolor='#595959', linewidth=1, zorder=2),
                       medianprops=dict(color='red', linewidth=2.5, zorder=3))

                # LOGIKA TITIK (SCATTER)
                cat_map = {str(c): i+1 for i, c in enumerate(cats)}
                
                if not is_edited_file:
                    # DATA ASLI: Gambar titik nyata
                    df['x_idx'] = df[x_col].astype(str).apply(lambda x: cat_map[x])
                    np.random.seed(42)
                    noise = np.random.uniform(-jitter_val, jitter_val, size=len(df))
                    ax.scatter(df['x_idx'] + noise, df[y_col], s=dot_size**1.5, 
                               c=dot_color, alpha=dot_opacity, zorder=5, edgecolor='black', linewidth=0.3)
                else:
                    # DATA EDIT: Gambar titik simulasi agar grafik tidak kosong
                    st.info("💡 Menampilkan titik simulasi (random jitter) berdasarkan rentang Q1-Q3.")
                    np.random.seed(42)
                    for i, cat in enumerate(cats):
                        c_str = str(cat)
                        conf = st.session_state['data_config'][c_str]
                        # Buat 10 titik acak di sekitar median
                        sim_y = np.random.uniform(conf['q1'], conf['q3'], size=10)
                        sim_x = np.full(10, i + 1) + np.random.uniform(-jitter_val, jitter_val, size=10)
                        ax.scatter(sim_x, sim_y, s=dot_size**1.5, c=dot_color, alpha=dot_opacity, zorder=5)

                ax.set_xlabel(x_col, fontweight='bold')
                ax.set_ylabel(y_col, fontweight='bold')
                st.pyplot(fig)

                # DOWNLOAD
                st.write("---")
                d_c1, d_c2 = st.columns(2)
                with d_c1:
                    buf = io.BytesIO()
                    fig.savefig(buf, format="png", dpi=300, bbox_inches='tight')
                    st.download_button("⬇️ Download Gambar", buf.getvalue(), "plot.png", "image/png")
                with d_c2:
                    export_rows = []
                    for cat_name in cats:
                        row = {'Is_Edited_Summary': True, 'Original_X_Label': x_col, 'Original_Y_Label': y_col,
                               'Group_Name': str(cat_name), **st.session_state['data_config'][str(cat_name)]}
                        export_rows.append(row)
                    st.download_button("⬇️ Download Data Edit (.csv)", pd.DataFrame(export_rows).to_csv(index=False), "data_edit.csv", "text/csv")

    except Exception as e:
        st.error(f"Eror: {e}")
