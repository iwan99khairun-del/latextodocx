import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import re

# --- 1. SETTING HALAMAN ---
st.set_page_config(page_title="Studio Grafik Rapi", layout="wide")
st.title("🌱 Grafik Box Plot + Titik Rapi (Swarm)")

# --- 2. FUNGSI BACA DATA ---
@st.cache_data
def load_data(file):
    try:
        # Deteksi Header Otomatis
        if file.name.endswith('.csv'):
            df_temp = pd.read_csv(file, header=None)
        else:
            df_temp = pd.read_excel(file, header=None)
            
        header_idx = 0
        for i, row in df_temp.iterrows():
            row_str = row.astype(str).str.lower().to_string()
            if 'dose' in row_str or 'gy' in row_str:
                header_idx = i
                break
        
        if file.name.endswith('.csv'):
            file.seek(0)
            df = pd.read_csv(file, header=header_idx)
        else:
            df = pd.read_excel(file, header=header_idx)

        # Bersihkan data
        df = df.dropna(axis=1, how='all')
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', na=False)]
        return df
    except:
        return None

def urutan_dosis(val):
    cari = re.search(r'\d+', str(val))
    return int(cari.group()) if cari else 999

# --- 3. MAIN PROGRAM ---
uploaded_file = st.file_uploader("Upload Data Excel", type=["xlsx", "csv"])

if uploaded_file:
    df = load_data(uploaded_file)
    
    if df is not None:
        cols = df.columns.tolist()
        
        # Cari Kolom Otomatis
        try:
            col_x = next(c for c in cols if 'dose' in c.lower() or 'gy' in c.lower())
            col_y = next(c for c in cols if 'diversity' in c.lower() or 'genetic' in c.lower())
        except:
            col_x = cols[0]
            col_y = cols[1] if len(cols) > 1 else
