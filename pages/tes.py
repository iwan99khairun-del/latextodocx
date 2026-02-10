import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
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
            y_col = st.selectbox("Sumbu Y (Angka):", df.columns, index=1 if len(df.columns) > 1 else 0, key="y_col_select")

        if x_col and y_col:
            # RESET LOGIC: Jika kolom/file berubah, hapus config lama
            current_cols = f"{x_col}_{y_col}_{uploaded_file.name}"
            if 'last_state_key' not in st.session_state or st.session_state['last_state_key'] != current_cols:
                st.session_state['data_config'] = {}
                st.session_state['last_state_key'] = current_cols

            df[y_col] = pd.to_numeric(df[y_col], errors='coerce')
            df = df.dropna(subset=[x_col, y_col])
            
            raw_cats = df[x_col].unique()
            cats = sorted(raw_cats, key=natural_sort_key)

            if 'data_config' not in st.session_state:
                st.session_state['data_config'] = {}
            
            # Inisialisasi Data jika belum ada
            for cat in cats:
                cat_str = str(cat)
                if cat_str not in st.session_state['data_config']:
                    sub_data = df[df[x_col] == cat][y_col]
                    stats = sub_data.describe()
                    st.session_state['data_config'][cat_str] = {
                        'med': float(stats['50%']),
                        'q1': float(stats['25%']),
                        'q3': float(stats['75%']),
                        'whislo': float(stats['min']),
                        'whishi': float(stats['max']),
                        'width': 0.65
                    }

            st.write("---")
            col_kiri, col_kanan = st.columns([1, 2])

            with col_kiri:
                # --- A. GLOBAL SETTINGS ---
                with st.expander("1️⃣ Pengaturan Gambar (Global)", expanded=False):
                    fig_w = st.slider("Lebar Gambar", 3.0, 15.0, 6.0)
                    fig_h = st.slider("Tinggi Gambar", 3.0, 10.0, 5.0)
                    point_size = st.slider("Ukuran Titik", 2.0, 15.0, 7.0)
                    jitter_val = st.slider("Jitter (Sebaran)", 0.0, 0.4, 0.12)
                    seed_val = st.number_input("Seed (Acak)", value=42)
                    
                    if st.button("🔄 Reset Semua ke Data Asli"):
                        st.session_state['data_config'] = {}
                        st.rerun()

                st.write("")
                st.subheader("2️⃣ Edit Kotak")
                
                pilih_group = st.selectbox(
                    "Pilih Group yang mau diedit:",
                    options=[str(c) for c in cats]
                )

                if pilih_group:
                    st.info(f"🛠️ Sedang mengedit: **{pilih_group}**")
                    conf = st.session_state['data_config'].get(pilih_group)

                    # Tombol Reset Spesifik per Group
                    if st.button(f"⏪ Reset {pilih_group} ke Nilai Asli"):
                        orig_data = df[df[x_col].astype(str) == pilih_group][y_col]
                        orig_stats = orig_data.describe()
                        st.session_state['data_config'][pilih_group] = {
                            'med': float(orig_stats['50%']),
                            'q1': float(orig_stats['25%']),
                            'q3': float(orig_stats['75%']),
                            'whislo': float(orig_stats['min']),
                            'whishi': float(orig_stats['max']),
                            'width': 0.65
                        }
                        st.rerun()

                    # Input Fields
                    new_width = st.slider(f"Lebar Kotak", 0.1, 1.0, float(conf['width']))
                    
                    c_h1, c_h2 = st.columns(2)
                    with c_h1:
                        new_q3 = st.number_input("Atas (Q3)", value=float(conf['q3']), format="%.4f")
                        new_q1 = st.number_input("Bawah (Q1)", value=float(conf['q1']), format="%.4f")
                    with c_h2:
                        new_med = st.number_input("Tengah (Median)", value=float(conf['med']), format="%.4f")
                        st.caption("Ubah angka untuk kustomisasi.")

                    # Simpan perubahan
                    st.session_state['data_config'][pilih_group].update({
                        'width': new_width, 'q3': new_q3, 'q1': new_q1, 'med': new_med
                    })

            with col_kanan:
                # --- B. PREVIEW GRAFIK ---
                st.subheader("🖼️ Preview Grafik")
                fig, ax = plt.subplots(figsize=(fig_w, fig_h))
                ax.set_facecolor('white')
                
                for spine in ax.spines.values():
                    spine.set_visible(True)
                    spine.set_color('#595959')
                    spine.set_linewidth(1)

                bxp_stats = []
                list_widths = []
                
                for cat in cats:
                    cat_str = str(cat)
                    c = st.session_state['data_config'][cat_str]
                    bxp_stats.append({
                        'label': cat_str, 'med': c['med'], 'q1': c['q1'], 'q3': c['q3'],
                        'whislo': c['whislo'], 'whishi': c['whishi'], 'fliers': []
                    })
                    list_widths.append(c['width'])

                ax.bxp(bxp_stats, showfliers=False, widths=list_widths,
                       patch_artist=True,
                       boxprops=dict(facecolor='#CCCCCC', edgecolor='#595959', linewidth=0.9),
                       medianprops=dict(color='#595959', linewidth=2),
                       whiskerprops=dict(color='#595959', linewidth=0.9),
                       capprops=dict(color='#595959', linewidth=0.9))

                cat_map = {str(c): i+1 for i, c in enumerate(cats)}
                df['x_idx'] = df[x_col].astype(str).apply(lambda x: cat_map[x])
                
                np.random.seed(int(seed_val))
                noise = np.random.uniform(-jitter_val, jitter_val, size=len(df))
                
                ax.scatter(df['x_idx'] + noise, df[y_col],
                           s=point_size**1.5,
                           c='orange', edgecolor='red', linewidth=0.7, alpha=0.8,
                           zorder=3)

                ax.set_xlabel(x_col, fontweight='bold')
                ax.set_ylabel(y_col, fontweight='bold')
                st.pyplot(fig)

                # --- C. DOWNLOAD SECTION ---
                st.write("---")
                st.subheader("📥 Download Output")
                
                d_col1, d_col2 = st.columns(2)
                
                with d_col1:
                    st.write("**1. Download Gambar**")
                    dpi = st.selectbox("Resolusi PNG", [300, 600], format_func=lambda x: f"{x} DPI")
                    buf_img = io.BytesIO()
                    fig.savefig(buf_img, format="png", dpi=dpi, bbox_inches='tight')
                    st.download_button("⬇️ Download PNG", buf_img.getvalue(), "grafik_boxplot.png", "image/png")

                with d_col2:
                    st.write("**2. Download Statistik Terkini**")
                    
                    # Membuat DataFrame dari data yang sudah diedit
                    export_list = []
                    for cat in cats:
                        c_str = str(cat)
                        conf_data = st.session_state['data_config'][c_str]
                        # Menambahkan label group ke dalam dictionary data
                        row = {'Group': c_str}
                        row.update(conf_data)
                        export_list.append(row)
                    
                    df_export = pd.DataFrame(export_list)
                    
                    # Konversi ke CSV
                    csv_buffer = io.StringIO()
                    df_export.to_csv(csv_buffer, index=False)
                    
                    st.write("") # Spacer agar sejajar dengan tombol sebelah
                    st.write("")
                    st.download_button(
                        label="⬇️ Download CSV Data",
                        data=csv_buffer.getvalue(),
                        file_name="statistik_grafik.csv",
                        mime="text/csv"
                    )
                    st.caption("File CSV berisi: Median, Q1, Q3, Min, Max, dan Lebar kotak.")

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
        if st.button("🔄 Reset Paksa Aplikasi"):
            st.session_state.clear()
            st.rerun()
