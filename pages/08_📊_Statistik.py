import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm

# --- FUNGSI HITUNG CRONBACH'S ALPHA (Manual tanpa library tambahan) ---
def calculate_cronbach_alpha(df_items):
    item_scores = df_items
    item_variances = item_scores.var(axis=0, ddof=1)
    total_score_variance = item_scores.sum(axis=1).var(ddof=1)
    n_items = item_scores.shape[1]
    
    if total_score_variance == 0:
        return 0
    
    return (n_items / (n_items - 1)) * (1 - (item_variances.sum() / total_score_variance))

# --- HALAMAN UTAMA ---
st.set_page_config(page_title="Kalkulator Statistik Lengkap")
st.title("🧮 Kalkulator Statistik 8 Variabel")
st.markdown("Aplikasi ini menghitung 8 poin statistik sesuai tabel referensi (Mean, StDev, P-value, R-Square, Alpha, dll).")

# 1. UPLOAD DATA
uploaded_file = st.file_uploader("Upload Data Excel/CSV", type=["xlsx", "csv"])

if uploaded_file is not None:
    # Load Data
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.write("### Preview Data:")
        st.dataframe(df.head())
        
        # Ambil nama kolom angka saja
        numeric_columns = df.select_dtypes(include=np.number).columns.tolist()
        all_columns = df.columns.tolist()

        # --- TAB MENU PERHITUNGAN ---
        tab1, tab2, tab3, tab4 = st.tabs(["Deskriptif & Normalitas", "Hubungan (Korelasi/Regresi)", "Komparasi (T-Test)", "Reliabilitas (Cronbach)"])

        # === 1. MEAN, STDEV & NORMALITAS ===
        with tab1:
            st.header("1, 2, 8: Deskriptif & Normalitas")
            col_target = st.selectbox("Pilih Kolom Data:", numeric_columns, key="desc_col")
            
            if col_target:
                data_col = df[col_target].dropna()
                
                # Hitung Mean & StDev
                mean_val = np.mean(data_col)
                std_val = np.std(data_col, ddof=1) # ddof=1 untuk sampel
                
                # Uji Normalitas (Shapiro-Wilk)
                stat_norm, p_norm = stats.shapiro(data_col)
                norm_status = "Normal" if p_norm > 0.05 else "Tidak Normal"
                
                col_res1, col_res2 = st.columns(2)
                with col_res1:
                    st.metric("Mean (Rata-rata)", f"{mean_val:.2f}")
                    st.metric("Standar Deviasi", f"{std_val:.2f}")
                with col_res2:
                    st.metric("Uji Normalitas (Shapiro-Wilk)", f"{p_norm:.4f}")
                    st.info(f"Distribusi data: **{norm_status}** (Syarat P > 0.05)")

        # === 2. KORELASI, R-SQUARE, F-HITUNG ===
        with tab2:
            st.header("4, 5, 6: Regresi Linear (Pengaruh)")
            st.write("Menguji pengaruh Variabel X (Penyebab) terhadap Y (Akibat).")
            
            col_x = st.selectbox("Pilih Variabel X (Independent):", numeric_columns, key="reg_x")
            col_y = st.selectbox("Pilih Variabel Y (Dependent):", numeric_columns, key="reg_y")
            
            if col_x and col_y:
                X = df[col_x]
                Y = df[col_y]
                
                # Tambahkan konstanta untuk statsmodels
                X_const = sm.add_constant(X)
                
                # Buat Model Regresi
                model = sm.OLS(Y, X_const).fit()
                
                # Ambil nilai-nilai penting
                r_value = np.sqrt(model.rsquared) # Koefisien Korelasi (r)
                r_squared = model.rsquared      # Koefisien Determinasi (R2)
                f_value = model.fvalue          # F-Hitung
                f_pvalue = model.f_pvalue       # Sig F
                
                st.write("#### Hasil Analisis:")
                c1, c2, c3 = st.columns(3)
                c1.metric("Korelasi (r)", f"{r_value:.3f}")
                c2.metric("R-Square (Pengaruh %)", f"{r_squared*100:.1f}%")
                c3.metric("F-Hitung", f"{f_value:.3f}")
                
                if f_pvalue < 0.05:
                    st.success(f"**Signifikan!** (P-value F: {f_pvalue:.4f} < 0.05). Variabel X berpengaruh nyata terhadap Y.")
                else:
                    st.warning(f"**Tidak Signifikan.** (P-value F: {f_pvalue:.4f} > 0.05).")

        # === 3. T-TEST & P-VALUE ===
        with tab3:
            st.header("3, 6: Uji Beda (T-Test)")
            st.write("Membandingkan apakah ada perbedaan signifikan antara data A dan data B.")
            
            # Pilihan metode input
            compare_method = st.radio("Metode Perbandingan:", ["Dua Kolom Berbeda (Paired/Independent)", "Satu Kolom dikelompokkan (Group By)"])
            
            if compare_method == "Dua Kolom Berbeda (Paired/Independent)":
                col_a = st.selectbox("Pilih Data A:", numeric_columns, key="ttest_a")
                col_b = st.selectbox("Pilih Data B:", numeric_columns, key="ttest_b")
                
                if col_a and col_b:
                    # Melakukan Independent T-test
                    t_stat, p_val = stats.ttest_ind(df[col_a], df[col_b])
                    
                    st.metric("t-hitung", f"{t_stat:.3f}")
                    st.metric("P-value (Sig.)", f"{p_val:.4f}")
                    
                    if p_val < 0.05:
                        st.success("Hipotesis Diterima (Ada Perbedaan Signifikan)")
                    else:
                        st.error("Hipotesis Ditolak (Tidak Ada Perbedaan)")

        # === 4. CRONBACH'S ALPHA ===
        with tab4:
            st.header("7: Cronbach's Alpha (Reliabilitas)")
            st.write("Pilih kolom-kolom pertanyaan kuesioner (Item 1, Item 2, dst).")
            
            cols_items = st.multiselect("Pilih Item Pertanyaan:", numeric_columns)
            
            if len(cols_items) > 1:
                df_items = df[cols_items]
                alpha = calculate_cronbach_alpha(df_items)
                
                st.metric("Nilai Cronbach's Alpha", f"{alpha:.3f}")
                
                if alpha > 0.6:
                    st.success("✅ Reliabel (Konsisten)")
                else:
                    st.warning("⚠️ Tidak Reliabel (Kurang Konsisten)")
            else:
                st.info("Pilih minimal 2 kolom item pertanyaan.")

    except Exception as e:
        st.error(f"Terjadi kesalahan saat membaca data: {e}")
        st.write("Pastikan file Excel bersih (baris pertama adalah header/nama kolom).")

else:
    st.info("Silakan upload file Excel atau CSV berisi data angkamu.")
