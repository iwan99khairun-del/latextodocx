import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io
import re

# --- SETUP HALAMAN ---
st.set_page_config(page_title="Replika R - Edit Per Group", layout="wide")
st.title("📊 Grafik Box-and-Whisker Plot")

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
        # Baca Data
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, header=0)
        else:
            df = pd.read_excel(uploaded_file, header=0)

        df.columns = df.columns.astype(str).str.strip()
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        # DETEKSI FILE HASIL EDIT (Berdasarkan kolom khusus)
        is_edited_file = 'Is_Edited_Summary' in df.columns

        if is_edited_file:
            st.success("✅ File hasil edit terdeteksi. Mengembalikan tampilan sesuai simpanan terakhir.")
            # Ambil nama kolom asli dari baris pertama data edit
            x_col = df['Original_X_Label'].iloc[0]
            y_col = df['Original_Y_Label'].iloc[0]
            cats = df['Group_Name'].tolist()
        else:
            # --- PILIH KOLOM (Untuk Data Mentah) ---
            c1, c2 = st.columns(2)
            with c1:
                x_col = st.selectbox("Sumbu X (Kategori):", df.columns, key="x_col_select")
            with c2:
                y_col = st.selectbox("Sumbu Y (Angka):", df.columns, index=1 if len(df.columns) > 1 else 0, key="y_col_select")

        if x_col and y_col:
            # RESET LOGIC
            current_cols = f"{x_col}_{y_col}_{uploaded_file.name}"
            if 'last_state_key' not in st.session_state or st.session_state['last_state_key'] != current_cols:
                st.session_state['data_config'] = {}
                st.session_state['last_state_key'] = current_cols

            if not is_edited_file:
                df[y_col] = pd.to_numeric(df[y_col], errors='coerce')
                df = df.dropna(subset=[x_col, y_col])
                raw_cats = df[x_col].unique()
                cats = sorted(raw_cats, key=natural_sort_key)

            if 'data_config' not in st.session_state:
                st.session_state['data_config'] = {}
            
            # INISIALISASI/UPDATE SESSION STATE (Fix KeyError 'width')
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
                        sub_data = df[df[x_col] == row[x_col]][y_col]
                        stats = sub_data.describe()
                        st.session_state['data_config'][cat_str] = {
                            'med': float(stats['50%']), 'q1': float(stats['25%']), 'q3': float(stats['75%']),
                            'whislo': float(stats['min']), 'whishi': float(stats['max']), 'width': 0.65
                        }

            st.write("---")
            col_kiri, col_kanan = st.columns([1, 2])

            with col_kiri:
                with st.expander("1️⃣ Pengaturan Gambar (Global)", expanded=False):
                    fig_w = st.slider("Lebar Gambar", 3.0, 15.0, 6.0)
                    fig_h = st.slider("Tinggi Gambar", 3.0, 10.0, 5.0)
                    point_size = st.slider("Ukuran Titik", 2.0, 15.0, 7.0)
                    jitter_val = st.slider("Jitter (Sebaran)", 0.0, 0.4, 0.12)
                    seed_val = st.number_input("Seed (Acak)", value=42)
                    if st.button("🔄 Reset Semua ke Data Asli"):
                        st.session_state['data_config'] = {}
                        st.rerun()

                st.subheader("2️⃣ Edit Kotak")
                pilih_group = st.selectbox("Pilih Group:", options=[str(c) for c in cats])

                if pilih_group:
                    conf = st.session_state['data_config'].get(pilih_group)
                    
                    # Tampilkan Slider Edit
                    new_width = st.slider(f"Lebar Kotak", 0.1, 1.0, float(conf['width']))
                    c_h1, c_h2 = st.columns(2)
                    with c_h1:
                        new_q3 = st.number_input("Atas (Q3)", value=float(conf['q3']), format="%.4f")
                        new_q1 = st.number_input("Bawah (Q1)", value=float(conf['q1']), format="%.4f")
                    with c_h2:
                        new_med = st.number_input("Tengah (Median)", value=float(conf['med']), format="%.4f")

                    st.session_state['data_config'][pilih_group].update({
                        'width': new_width, 'q3': new_q3, 'q1': new_q1, 'med': new_med
                    })

            with col_kanan:
                st.subheader("🖼️ Preview Grafik")
                fig, ax = plt.subplots(figsize=(fig_w, fig_h))
                ax.set_facecolor('white')
                
                # Plot Boxplot
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

                ax.bxp(bxp_stats, showfliers=False, widths=list_widths, patch_artist=True,
                       boxprops=dict(facecolor='#CCCCCC', edgecolor='#595959', linewidth=0.9),
                       medianprops=dict(color='red', linewidth=2))

                # Plot Scatter (Hanya jika ada data mentah)
                if not is_edited_file:
                    cat_map = {str(c): i+1 for i, c in enumerate(cats)}
                    df['x_idx'] = df[x_col].astype(str).apply(lambda x: cat_map[x])
                    np.random.seed(int(seed_val))
                    noise = np.random.uniform(-jitter_val, jitter_val, size=len(df))
                    ax.scatter(df['x_idx'] + noise, df[y_col], s=point_size**1.5, c='orange', alpha=0.6, zorder=3)

                ax.set_xlabel(x_col, fontweight='bold')
                ax.set_ylabel(y_col, fontweight='bold')
                st.pyplot(fig)

                # --- DOWNLOAD SECTION ---
                st.write("---")
                st.subheader("📥 Download Hasil")
                d_col1, d_col2 = st.columns(2)
                
                with d_col1:
                    st.write("**Gambar (PNG)**")
                    buf_img = io.BytesIO()
                    fig.savefig(buf_img, format="png", dpi=300, bbox_inches='tight')
                    st.download_button("⬇️ Download Gambar", buf_img.getvalue(), "grafik.png", "image/png")

                with d_col2:
                    st.write("**Data Edit (Bisa di-upload kembali)**")
                    # Buat file CSV yang menyimpan nama label asli agar tidak berubah saat di-upload
                    export_rows = []
                    for cat_name in cats:
                        c_str = str(cat_name)
                        vals = st.session_state['data_config'][c_str]
                        row = {
                            'Is_Edited_Summary': True,
                            'Original_X_Label': x_col,
                            'Original_Y_Label': y_col,
                            'Group_Name': c_str,
                            **vals
                        }
                        export_rows.append(row)
                    
                    csv_data = pd.DataFrame(export_rows).to_csv(index=False).encode('utf-8')
                    st.download_button("⬇️ Download Data (.csv)", csv_data, "data_edit_berkelanjutan.csv", "text/csv")

    except Exception as e:
        st.error(f"Eror: {e}")
        if st.button("🔄 Reset Paksa"):
            st.session_state.clear()
            st.rerun()
