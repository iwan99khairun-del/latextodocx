import streamlit as st
import pandas as pd

st.set_page_config(page_title="List jurnal", page_icon="📚", layout="wide")

st.title("📚 Daftar Referensi Jurnal")
st.write("Daftar jurnal terindeks SINTA & Scopus (Elektro, Mesin, Informatika):")

# DATA JURNAL
data_jurnal = [
    {"No": 1, "Jurnal": "International Journal of Technology (IJTech)", "Index": "SINTA 1 (SCOPUS Q2)", "Penerbit": "UI", "Link": "https://ijtech.eng.ui.ac.id/"},
    {"No": 2, "Jurnal": "Indonesian Journal of Science and Technology (IJoST)", "Index": "SINTA 1 (SCOPUS Q1)", "Penerbit": "UPI", "Link": "https://ejournal.upi.edu/index.php/ijost/"},
    {"No": 3, "Jurnal": "Telkomnika", "Index": "SINTA 1 (SCOPUS Q2)", "Penerbit": "UAD", "Link": "http://journal.uad.ac.id/index.php/TELKOMNIKA"},
    {"No": 4, "Jurnal": "Automotive Experiences", "Index": "SINTA 1 (SCOPUS Q2)", "Penerbit": "UM Magelang", "Link": "https://journal.unimma.ac.id/index.php/automotive"},
    {"No": 5, "Jurnal": "Journal of Engineering and Technological Sciences", "Index": "SINTA 1 (SCOPUS Q3)", "Penerbit": "ITB", "Link": "https://journals.itb.ac.id/index.php/jets"},
    {"No": 6, "Jurnal": "IJECE", "Index": "SINTA 1 (SCOPUS Q2)", "Penerbit": "IAES", "Link": "http://ijece.iaescore.com/"},
    {"No": 7, "Jurnal": "Bulletin of EEI", "Index": "SINTA 1 (SCOPUS Q3)", "Penerbit": "UAD", "Link": "http://beei.org/"},
    {"No": 8, "Jurnal": "Makara Journal of Technology", "Index": "SINTA 1 (SCOPUS Q4)", "Penerbit": "UI", "Link": "https://scholarhub.ui.ac.id/mjt/"},
    {"No": 9, "Jurnal": "EMITTER", "Index": "SINTA 1 (SCOPUS)", "Penerbit": "PENS", "Link": "https://emitter.pens.ac.id/index.php/emitter"},
    {"No": 10, "Jurnal": "MEV Journal", "Index": "SINTA 1 (SCOPUS)", "Penerbit": "BRIN", "Link": "https://mevjournal.com/index.php/mev"},
    {"No": 11, "Jurnal": "JNTETI", "Index": "SINTA 2", "Penerbit": "UGM", "Link": "https://jurnal.ugm.ac.id/v3/JNTETI"},
    {"No": 12, "Jurnal": "Jurnal Elektronika dan Telekomunikasi", "Index": "SINTA 2", "Penerbit": "BRIN", "Link": "https://www.jurnalet.com/jet"},
    {"No": 13, "Jurnal": "Jurnal Rekayasa Mesin", "Index": "SINTA 2", "Penerbit": "UB", "Link": "https://jrm.ub.ac.id/"},
    {"No": 14, "Jurnal": "JITEKI", "Index": "SINTA 2", "Penerbit": "UAD", "Link": "http://journal.uad.ac.id/index.php/JITEKI"},
    {"No": 15, "Jurnal": "ELKOMIKA", "Index": "SINTA 2", "Penerbit": "Itenas", "Link": "https://ejurnal.itenas.ac.id/index.php/elkomika"},
    {"No": 16, "Jurnal": "Jurnal Teknologi dan Sistem Komputer", "Index": "SINTA 2", "Penerbit": "Undip", "Link": "https://jtsiskom.undip.ac.id/"},
    {"No": 17, "Jurnal": "Jurnal RESTI", "Index": "SINTA 2", "Penerbit": "PNP", "Link": "http://jurnal.iaii.or.id/index.php/RESTI"},
    {"No": 18, "Jurnal": "IPTEK Journal", "Index": "SINTA 1", "Penerbit": "ITS", "Link": "https://iptek.its.ac.id/index.php/jts"},
    {"No": 19, "Jurnal": "Register", "Index": "SINTA 2", "Penerbit": "Unipdu", "Link": "https://journal.unipdu.ac.id/index.php/register"},
    {"No": 20, "Jurnal": "Jurnal Pendidikan Teknologi & Kejuruan", "Index": "SINTA 2", "Penerbit": "UNY", "Link": "https://journal.uny.ac.id/index.php/jptk"},
]

df = pd.DataFrame(data_jurnal)
st.dataframe(
    df,
    column_config={"Link": st.column_config.LinkColumn("Website")},
    hide_index=True,
    use_container_width=True
)
