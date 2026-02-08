import streamlit as st
import pandas as pd

st.set_page_config(page_title="Materi & Riset", page_icon="📚", layout="wide")

st.title("📚 Daftar Referensi Jurnal")
st.write("Daftar jurnal terindeks SINTA & Scopus (Elektro, Mesin, Informatika):")

data_jurnal = [
    {"No": 1, "Jurnal": "International Journal of Technology (IJTech)", "Index": "SINTA 1 (SCOPUS Q2)", "Penerbit": "UI", "Link": "https://ijtech.eng.ui.ac.id/"},
    {"No": 2, "Jurnal": "Indonesian Journal of Science and Technology (IJoST)", "Index": "SINTA 1 (SCOPUS Q1)", "Penerbit": "UPI", "Link": "https://ejournal.upi.edu/index.php/ijost/"},
    {"No": 3, "Jurnal": "Telkomnika", "Index": "SINTA 1 (SCOPUS Q2)", "Penerbit": "UAD", "Link": "http://journal.uad.ac.id/index.php/TELKOMNIKA"},
    {"No": 4, "Jurnal": "Automotive Experiences", "Index": "SINTA 1 (SCOPUS Q2)", "Penerbit": "UM Magelang", "Link": "https://journal.unimma.ac.id/index.php/automotive"},
    {"No": 5, "Jurnal": "Journal of Engineering and Technological Sciences", "Index": "SINTA 1 (SCOPUS Q3)", "Penerbit": "ITB", "Link": "https://journals.itb.ac.id/index.php/jets"}
]

df = pd.DataFrame(data_jurnal)
st.dataframe(df, column_config={"Link": st.column_config.LinkColumn("Website")}, hide_index=True, use_container_width=True)

csv = df.to_csv(index=False).encode('utf-8')
st.download_button(label="📥 Download Data (CSV)", data=csv, file_name='Daftar_Jurnal_Pak_Iwan.csv', mime='text/csv')
