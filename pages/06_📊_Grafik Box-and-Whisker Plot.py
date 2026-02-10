import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io
import re
import copy

# --- SETUP HALAMAN ---
st.set_page_config(page_title="Replika R - Edit Boxplot Persisten di Data", layout="wide")
st.title("📊 Grafik Box-and-Whisker Plot dengan Edit Tersimpan di File Data")
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
uploaded_file = st.file_uploader("Upload File Excel/CSV (jika Excel dengan sheet 'BoxplotConfig' → edit sebelumnya akan otomatis muncul)", type=["xlsx", "csv"])

if uploaded_file:
    try:
        # Baca data
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, header=0)
            loaded_config = None
            st.info("📄 File CSV → tidak ada config edit sebelumnya. Edit baru akan dimulai dari data asli.")
        else:
            # Excel: coba baca sheet config jika ada
            xls = pd.ExcelFile(uploaded_file)
            if 'DataPoints' in xls.sheet_names:
                df = pd.read_excel(uploaded_file, sheet_name='DataPoints')
            else:
                df = pd.read_excel(uploaded_file, sheet_name=0)  # sheet pertama
            
            if 'BoxplotConfig' in xls.sheet_names:
                config_df = pd.read_excel(uploaded_file, sheet_name='BoxplotConfig')
                # Convert ke dict {group_str: {stats}}
                loaded_config = {}
                for _, row in config_df.iterrows():
                    group = str(row['Group'])
                    loaded_config[group] = {
                        'med': float(row['med']),
                        'q1': float(row['q1']),
                        'q3': float(row['q3']),
                        'whislo': float(row['whislo']),
                        'whishi': float(row['whishi']),
                        'width': float(row['width'])
                    }
                st.success("✅ Config edit sebelumnya ditemukan di sheet 'BoxplotConfig' → kotak akan persis seperti editan terakhir!")
            else:
                loaded_config = None
                st.info("📄 File Excel tanpa sheet 'BoxplotConfig' → mulai dari data asli.")

        df.columns = df.columns.astype(str).str.strip()
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
       
        # --- PILIH KOLOM ---
        c1, c2 = st.columns(2)
        with c1:
            x_col = st.selectbox("Sumbu X (Kategori):", df.columns, key="x_col_select")
        with c2:
            y_col = st.selectbox("Sumbu Y (Angka):", df.columns, index=1 if len(df.columns) > 1 else 0, key="y_col_select")
        
        if x_col and y_col:
            # Reset jika file/kolom berubah
            current_key = f"{x_col}_{y_col}_{uploaded_file.name}"
            if 'last_state_key' not in st.session_state or st.session_state.last_state_key != current_key:
                st.session_state.data_config = {}
                st.session_state.original_config = {}
                st.session_state.last_state_key = current_key
            
            df[y_col] = pd.to_numeric(df[y_col], errors='coerce')
            df = df.dropna(subset=[x_col, y_col])
           
            raw_cats = df[x_col].unique()
            cats = sorted(raw_cats, key=natural_sort_key)
            
            # Hitung original config dari data asli (selalu)
            st.session_state.original_config = {}
            for cat in cats:
                cat_str = str(cat)
                sub_data = df[df[x_col] == cat][y_col]
                stats = sub_data.describe()
                st.session_state.original_config[cat_str] = {
                    'med': float(stats['50%']),
                    'q1': float(stats['25%']),
                    'q3': float(stats['75%']),
                    'whislo': float(stats['min']),
                    'whishi': float(stats['max']),
                    'width': 0.65
                }
            
            # Inisialisasi data_config: prioritaskan loaded_config → fallback ke original
            if 'data_config' not in st.session_state or not st.session_state.data_config:
                st.session_state.data_config = copy.deepcopy(st.session_state.original_config)
                if loaded_config:
                    for cat_str, vals in loaded_config.items():
                        if cat_str in st.session_state.data_config:
                            st.session_state.data_config[cat_str].update(vals)
            
            # Tambah group baru jika ada
            for cat in cats:
                cat_str = str(cat)
                if cat_str not in st.session_state.data_config:
                    st.session_state.data_config[cat_str] = st.session_state.original_config[cat_str].copy()
            
            st.write("---")
            col_kiri, col_kanan = st.columns([1, 2])
            with col_kiri:
                # --- GLOBAL SETTINGS ---
                with st.expander("1️⃣ Pengaturan Gambar (Global)", expanded=False):
                    fig_w = st.slider("Lebar Gambar", 3.0, 15.0, 6.0)
                    fig_h = st.slider("Tinggi Gambar", 3.0, 10.0, 5.0)
                    point_size = st.slider("Ukuran Titik", 2.0, 15.0, 7.0)
                    jitter_val = st.slider("Jitter (Sebaran)", 0.0, 0.4, 0.12)
                    seed_val = st.number_input("Seed (Acak)", value=42)
                    
                    if st.button("🔄 Reset Semua ke Data Asli"):
                        st.session_state.data_config = copy.deepcopy(st.session_state.original_config)
                        st.rerun()
                
                st.write("")
                st.subheader("2️⃣ Edit Kotak & Whisker")
                st.caption("🔹 Label dengan `*` = kotak telah diedit manual (berbeda dari data asli)")
                
                pilih_group = st.selectbox("Pilih Group:", options=[str(c) for c in cats])
                if pilih_group:
                    conf = st.session_state.data_config[pilih_group]
                    orig = st.session_state.original_config[pilih_group]
                    is_edited = any(abs(conf[k] - orig[k]) > 1e-6 for k in conf)  # toleransi float
                    st.info(f"🛠️ Sedang mengedit: **{pilih_group}** {'(✅ Sudah diedit)' if is_edited else '(Belum diedit)'}")
                    
                    if st.button(f"⏪ Reset {pilih_group} ke Asli"):
                        st.session_state.data_config[pilih_group] = orig.copy()
                        st.rerun()
                    
                    new_width = st.slider(f"Lebar Kotak ({pilih_group})", 0.1, 1.0, conf['width'])
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        new_q1 = st.number_input("Q1 (Bawah)", value=conf['q1'], format="%.4f", key=f"q1_{pilih_group}")
                        new_med = st.number_input("Median", value=conf['med'], format="%.4f", key=f"med_{pilih_group}")
                        new_whislo = st.number_input("Whisker Bawah (Min)", value=conf['whislo'], format="%.4f", key=f"whislo_{pilih_group}")
                    with c2:
                        new_q3 = st.number_input("Q3 (Atas)", value=conf['q3'], format="%.4f", key=f"q3_{pilih_group}")
                        new_whishi = st.number_input("Whisker Atas (Max)", value=conf['whishi'], format="%.4f", key=f"whishi_{pilih_group}")
                    
                    st.session_state.data_config[pilih_group].update({
                        'width': new_width, 'q1': new_q1, 'med': new_med,
                        'q3': new_q3, 'whislo': new_whislo, 'whishi': new_whishi
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
                list_widths = []
                
                for cat in cats:
                    cat_str = str(cat)
                    c = st.session_state.data_config[cat_str]
                    o = st.session_state.original_config[cat_str]
                    is_edited = any(abs(c[k] - o[k]) > 1e-6 for k in c)
                    label = cat_str + (" *" if is_edited else "")
                    
                    bxp_stats.append({
                        'label': label,
                        'med': c['med'], 'q1': c['q1'], 'q3': c['q3'],
                        'whislo': c['whislo'], 'whishi': c['whishi'],
                        'fliers': []
                    })
                    list_widths.append(c['width'])
                
                ax.bxp(bxp_stats, showfliers=False, widths=list_widths,
                       patch_artist=True,
                       boxprops=dict(facecolor='#CCCCCC', edgecolor='#595959', linewidth=0.9),
                       medianprops=dict(color='#595959', linewidth=2),
                       whiskerprops=dict(color='#595959', linewidth=0.9),
                       capprops=dict(color='#595959', linewidth=0.9))
                
                # Scatter tetap dari data asli
                cat_map = {str(c): i+1 for i, c in enumerate(cats)}
                df['x_idx'] = df[x_col].astype(str).map(cat_map)
                
                np.random.seed(int(seed_val))
                noise = np.random.uniform(-jitter_val, jitter_val, size=len(df))
                
                ax.scatter(df['x_idx'] + noise, df[y_col],
                           s=point_size**1.5, c='orange', edgecolor='red',
                           linewidth=0.7, alpha=0.8, zorder=3)
                
                ax.set_xlabel(x_col, fontweight='bold')
                ax.set_ylabel(y_col, fontweight='bold')
                st.pyplot(fig)
                
                # --- DOWNLOAD ---
                st.write("---")
                st.subheader("📥 Download Hasil")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    dpi = st.selectbox("Resolusi PNG", [300, 600], format_func=lambda x: f"{x} DPI")
                    buf_img = io.BytesIO()
                    fig.savefig(buf_img, format="png", dpi=dpi, bbox_inches='tight')
                    buf_img.seek(0)
                    st.download_button("⬇️ PNG Grafik", buf_img, "grafik_edited.png", "image/png")
                
                with col2:
                    # Download data asli (CSV)
                    buf_csv = io.BytesIO()
                    df.to_csv(buf_csv, index=False)
                    buf_csv.seek(0)
                    st.download_button("⬇️ Data Asli (CSV)", buf_csv, "data_asli.csv", "text/csv")
                
                with col3:
                    # Download data edited (XLSX dengan config)
                    config_for_save = []
                    for cat_str, vals in st.session_state.data_config.items():
                        config_for_save.append({
                            'Group': cat_str,
                            'q1': vals['q1'],
                            'q3': vals['q3'],
                            'med': vals['med'],
                            'whislo': vals['whislo'],
                            'whishi': vals['whishi'],
                            'width': vals['width']
                        })
                    config_df_save = pd.DataFrame(config_for_save)
                    
                    buf_xlsx = io.BytesIO()
                    with pd.ExcelWriter(buf_xlsx, engine='openpyxl') as writer:
                        df.to_excel(writer, sheet_name='DataPoints', index=False)
                        config_df_save.to_excel(writer, sheet_name='BoxplotConfig', index=False)
                    buf_xlsx.seek(0)
                    st.download_button(
                        "⬇️ Data Edited (XLSX)",
                        buf_xlsx,
                        "data_dengan_edit_boxplot.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                
                st.success("""
                **Cara kerja persisten edit kotak:**  
                1. Edit kotak sesukamu → bentuk grafik jadi A.  
                2. Download **Data Edited (XLSX)** → ini file B (berisi data asli + config edit kotak).  
                3. Nanti upload file B lagi → grafik **otomatis berbentuk A** (kotak persis seperti editan terakhir).  
                → Titik orange, garis, dll tetap dari data asli (tidak berubah).  
                → Label `*` = kotak diedit manual.  
                → Jika upload CSV atau XLSX tanpa sheet 'BoxplotConfig' → mulai dari bentuk asli.
                """)
                
    except Exception as e:
        st.error(f"Error: {e}")
        if st.button("Reset Aplikasi"):
            st.session_state.clear()
            st.rerun()
