import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io
import re
import copy

# --- SETUP HALAMAN ---
st.set_page_config(page_title="Replika R - Edit Box & Points Persisten", layout="wide")
st.title("📊 Grafik Box-and-Whisker Plot dengan Edit Kotak & Bulatan Persisten")
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
uploaded_file = st.file_uploader(
    "Upload File Excel/CSV (jika Excel punya sheet 'DataPoints' & 'BoxplotConfig' → edit sebelumnya otomatis muncul)",
    type=["xlsx", "csv"]
)

if uploaded_file:
    try:
        # --- BACA DATA & CONFIG ---
        if uploaded_file.name.endswith('.csv'):
            df_raw = pd.read_csv(uploaded_file, header=0)
            loaded_config = None
            st.info("📄 File CSV → hanya data points, tidak ada config kotak manual sebelumnya.")
        else:
            xls = pd.ExcelFile(uploaded_file)
            if 'DataPoints' in xls.sheet_names:
                df_raw = pd.read_excel(uploaded_file, sheet_name='DataPoints')
            else:
                df_raw = pd.read_excel(uploaded_file, sheet_name=0)
            
            if 'BoxplotConfig' in xls.sheet_names:
                config_df = pd.read_excel(uploaded_file, sheet_name='BoxplotConfig')
                loaded_config = {}
                for _, row in config_df.iterrows():
                    group = str(row['Group'])
                    loaded_config[group] = {
                        'med': float(row['med']), 'q1': float(row['q1']), 'q3': float(row['q3']),
                        'whislo': float(row['whislo']), 'whishi': float(row['whishi']),
                        'width': float(row['width'])
                    }
                st.success("✅ Config kotak manual sebelumnya ditemukan → kotak akan persis seperti editan terakhir!")
            else:
                loaded_config = None

        df_raw.columns = df_raw.columns.astype(str).str.strip()
        df_raw = df_raw.loc[:, ~df_raw.columns.str.contains('^Unnamed')]

        # --- PILIH KOLOM ---
        c1, c2 = st.columns(2)
        with c1:
            x_col = st.selectbox("Sumbu X (Kategori):", df_raw.columns, key="x_col_select")
        with c2:
            y_col = st.selectbox("Sumbu Y (Angka):", df_raw.columns, index=1 if len(df_raw.columns) > 1 else 0, key="y_col_select")
        
        if x_col and y_col:
            # Reset state jika file/kolom baru
            current_key = f"{x_col}_{y_col}_{uploaded_file.name}"
            if 'last_state_key' not in st.session_state or st.session_state.last_state_key != current_key:
                st.session_state.clear()  # bersihkan semua agar fresh
                st.session_state.last_state_key = current_key
            
            # Simpan df editable di session_state
            if 'df' not in st.session_state:
                st.session_state.df = df_raw.copy()
            
            df = st.session_state.df  # gunakan yang editable
            
            df[y_col] = pd.to_numeric(df[y_col], errors='coerce')
            df = df.dropna(subset=[x_col, y_col])
            st.session_state.df = df  # update kembali
            
            raw_cats = df[x_col].unique()
            cats = sorted(raw_cats, key=natural_sort_key)
            
            # Hitung stats asli dari data saat ini (bisa sudah diedit points)
            original_config = {}
            for cat in cats:
                cat_str = str(cat)
                sub_data = df[df[x_col] == cat][y_col]
                stats = sub_data.describe()
                original_config[cat_str] = {
                    'med': float(stats['50%']) if not sub_data.empty else 0,
                    'q1': float(stats['25%']) if not sub_data.empty else 0,
                    'q3': float(stats['75%']) if not sub_data.empty else 0,
                    'whislo': float(stats['min']) if not sub_data.empty else 0,
                    'whishi': float(stats['max']) if not sub_data.empty else 0,
                    'width': 0.65
                }
            
            # Inisialisasi data_config (untuk drawing kotak)
            if 'data_config' not in st.session_state:
                st.session_state.data_config = copy.deepcopy(original_config)
            
            # Apply loaded config (override manual kotak sebelumnya)
            if loaded_config:
                for cat_str, vals in loaded_config.items():
                    if cat_str in st.session_state.data_config:
                        st.session_state.data_config[cat_str].update(vals)
            
            st.write("---")
            col_kiri, col_kanan = st.columns([1.2, 2])
            with col_kiri:
                # --- GLOBAL SETTINGS ---
                with st.expander("1️⃣ Pengaturan Gambar (Global)", expanded=False):
                    fig_w = st.slider("Lebar Gambar", 3.0, 15.0, 6.0)
                    fig_h = st.slider("Tinggi Gambar", 3.0, 10.0, 5.0)
                    point_size = st.slider("Ukuran Bulatan", 2.0, 15.0, 7.0)
                    jitter_val = st.slider("Jitter (Sebaran)", 0.0, 0.4, 0.12)
                    seed_val = st.number_input("Seed (Acak)", value=42)
                    
                    if st.button("🔄 Reset Semua ke Data Asli Awal"):
                        st.session_state.df = df_raw.copy()
                        st.session_state.data_config = copy.deepcopy(original_config)
                        st.rerun()
                
                st.write("")
                st.subheader("2️⃣ Edit Kotak & Whisker Manual")
                st.caption("🔹 Override kotak tanpa ubah data points/bulatan")
                
                pilih_group_box = st.selectbox("Pilih Group untuk edit kotak:", options=[str(c) for c in cats], key="box_group")
                if pilih_group_box:
                    conf = st.session_state.data_config[pilih_group_box]
                    orig = original_config[pilih_group_box]
                    is_edited = any(abs(conf[k] - orig[k]) > 1e-6 for k in ['med','q1','q3','whislo','whishi','width'])
                    st.info(f"🛠️ Edit kotak: **{pilih_group_box}** {'(✅ Manual override)' if is_edited else '(Pakai dari data)'}")
                    
                    if st.button(f"⏪ Reset kotak {pilih_group_box} ke data saat ini"):
                        st.session_state.data_config[pilih_group_box] = orig.copy()
                        st.rerun()
                    
                    new_width = st.slider(f"Lebar Kotak ({pilih_group_box})", 0.1, 1.0, conf['width'], key=f"width_{pilih_group_box}")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        new_q1 = st.number_input("Q1 (Bawah)", value=conf['q1'], format="%.4f", key=f"q1b_{pilih_group_box}")
                        new_med = st.number_input("Median", value=conf['med'], format="%.4f", key=f"medb_{pilih_group_box}")
                        new_whislo = st.number_input("Whisker Bawah", value=conf['whislo'], format="%.4f", key=f"wl_{pilih_group_box}")
                    with c2:
                        new_q3 = st.number_input("Q3 (Atas)", value=conf['q3'], format="%.4f", key=f"q3b_{pilih_group_box}")
                        new_whishi = st.number_input("Whisker Atas", value=conf['whishi'], format="%.4f", key=f"wh_{pilih_group_box}")
                    
                    st.session_state.data_config[pilih_group_box].update({
                        'width': new_width, 'q1': new_q1, 'med': new_med,
                        'q3': new_q3, 'whislo': new_whislo, 'whishi': new_whishi
                    })
                
                st.write("---")
                st.subheader("3️⃣ Edit Data Points (Bulatan Orange)")
                st.caption("🔹 Ubah nilai → posisi bulatan berubah, kotak otomatis ikut (kecuali dioverride manual di atas)")
                
                pilih_group_points = st.selectbox("Pilih Group untuk edit bulatan:", options=[str(c) for c in cats], key="points_group")
                if pilih_group_points:
                    # Ambil sub data
                    sub_df = df[df[x_col] == pilih_group_points].copy()
                    if sub_df.empty:
                        st.warning("Group ini kosong.")
                    else:
                        # Data editor: allow tambah/kurang baris, edit hanya y_col
                        edited_sub = st.data_editor(
                            sub_df,
                            num_rows="dynamic",
                            use_container_width=True,
                            column_config={
                                col: st.column_config.Column(disabled=True) if col != y_col else None
                                for col in sub_df.columns
                            },
                            hide_index=False
                        )
                        
                        # Simpan perubahan
                        if st.button(f"💾 Simpan Perubahan Bulatan untuk {pilih_group_points}"):
                            # Hapus data lama group ini
                            st.session_state.df = st.session_state.df[st.session_state.df[x_col] != pilih_group_points]
                            # Pastikan x_col benar
                            edited_sub[x_col] = pilih_group_points
                            # Gabung kembali
                            st.session_state.df = pd.concat([st.session_state.df, edited_sub], ignore_index=True)
                            st.success(f"✅ Bulatan untuk {pilih_group_points} telah diupdate!")
                            st.rerun()
            
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
                    o = original_config[cat_str]
                    is_edited = any(abs(c[k] - o[k]) > 1e-6 for k in ['med','q1','q3','whislo','whishi','width'])
                    label = cat_str + (" *" if is_edited else "")
                    
                    bxp_stats.append({
                        'label': label, 'med': c['med'], 'q1': c['q1'], 'q3': c['q3'],
                        'whislo': c['whislo'], 'whishi': c['whishi'], 'fliers': []
                    })
                    list_widths.append(c['width'])
                
                ax.bxp(bxp_stats, showfliers=False, widths=list_widths,
                       patch_artist=True,
                       boxprops=dict(facecolor='#CCCCCC', edgecolor='#595959', linewidth=0.9),
                       medianprops=dict(color='#595959', linewidth=2),
                       whiskerprops=dict(color='#595959', linewidth=0.9),
                       capprops=dict(color='#595959', linewidth=0.9))
                
                # Bulatan dari data saat ini
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
                
                col1, col2 = st.columns(2)
                with col1:
                    dpi = st.selectbox("Resolusi PNG", [300, 600], format_func=lambda x: f"{x} DPI")
                    buf_img = io.BytesIO()
                    fig.savefig(buf_img, format="png", dpi=dpi, bbox_inches='tight')
                    buf_img.seek(0)
                    st.download_button("⬇️ PNG Grafik", buf_img, "grafik_edited.png", "image/png")
                
                with col2:
                    # Download file edited (XLSX dengan data points + config kotak)
                    config_for_save = []
                    for cat_str, vals in st.session_state.data_config.items():
                        o = original_config[cat_str]
                        # Hanya simpan jika benar-benar dioverride manual
                        if any(abs(vals[k] - o[k]) > 1e-6 for k in vals):
                            config_for_save.append({
                                'Group': cat_str, 'q1': vals['q1'], 'q3': vals['q3'],
                                'med': vals['med'], 'whislo': vals['whislo'],
                                'whishi': vals['whishi'], 'width': vals['width']
                            })
                    config_df_save = pd.DataFrame(config_for_save) if config_for_save else pd.DataFrame(columns=['Group','q1','q3','med','whislo','whishi','width'])
                    
                    buf_xlsx = io.BytesIO()
                    with pd.ExcelWriter(buf_xlsx, engine='openpyxl') as writer:
                        st.session_state.df.to_excel(writer, sheet_name='DataPoints', index=False)
                        config_df_save.to_excel(writer, sheet_name='BoxplotConfig', index=False)
                    buf_xlsx.seek(0)
                    st.download_button(
                        "⬇️ File Edited (XLSX) - Termasuk Edit Bulatan & Kotak",
                        buf_xlsx,
                        "data_dengan_edit_lengkap.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                
                st.success("""
                **Cara kerja (sekarang termasuk bulatan):**  
                1. Upload data asli → grafik normal.  
                2. Edit kotak manual (override) dan/atau edit bulatan (ubah/tambah/hapus nilai di table) → grafik jadi bentuk A.  
                3. Download **File Edited (XLSX)** → ini file B.  
                4. Upload file B lagi → grafik **otomatis persis bentuk A** (bulatan & kotak sama seperti editan terakhir).  
                → Edit bulatan → posisi/jumlah bulatan berubah + kotak otomatis ikut (kecuali kamu override manual).  
                → Edit kotak manual → kotak berubah tanpa ubah bulatan.  
                → Label dengan `*` = kotak dioverride manual.  
                """)
                
    except Exception as e:
        st.error(f"Error: {e}")
        if st.button("Reset Aplikasi"):
            st.session_state.clear()
            st.rerun()
