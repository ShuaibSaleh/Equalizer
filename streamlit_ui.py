import streamlit as st
import streamlit_functions as functions

# ---------------------- Website Settings -------------------------------- #

st.set_page_config(page_title="Equalizer",layout="wide",page_icon="🎚",initial_sidebar_state="expanded")

# ---------------------- CSS Styling ------------------------------------- #

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# ---------------------- Session States ---------------------------------- #

if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Default"
if "gender" not in st.session_state:
    st.session_state["gender"] = "Female"
if "plot_mode" not in st.session_state:
    st.session_state["plot_mode"] = "Static"

# ---------------------- Uploading Files --------------------------------- #

uploaded_file = st.sidebar.file_uploader("uploader",key="uploaded_file",label_visibility="hidden",type="wav")

# ---------------------- Main Window Elements ---------------------------- #

# Current Page
pages = {"Default":functions.defaultPage,
        "Music":functions.musicPage,
        "Vowels":functions.vowelsPage,
        "VoiceChanger":functions.voiceChangerPage,
        "Medical":functions.medicalPage
        }
for page in pages:
    if st.session_state["current_page"] == page:
        pages[page]()

# Line Break
st.markdown("***")

if st.session_state["plot_mode"] == "Static":
    # Signal Plot and spectrogram
    signal_figure,spec_figure = functions.plotSignals()
    signal_plot_col, spectrogram_col = st.columns(2,gap="large")
    with signal_plot_col:
        st.plotly_chart(signal_figure,use_container_width=True)

    with spectrogram_col:
        st.plotly_chart(spec_figure,use_container_width=True)
else:
    if st.session_state["uploaded_file"]:
        functions.dynamicPlot()
# ---------------------- Sidebar Elements --------------------------------- #

# Original Audio
st.sidebar.markdown("# Original Signal")
st.sidebar.audio(st.session_state["uploaded_file"] if st.session_state["uploaded_file"] else None,"wav")

# Modified Audio
st.sidebar.markdown("# Modified Signal")
st.sidebar.audio("Modified.wav" if st.session_state["uploaded_file"] else None,"wav")

plot_mode_col, current_page_col = st.sidebar.columns(2)

with plot_mode_col:
    # Dynamic vs. Static
    st.markdown("# Plot Mode")
    current_page = st.radio("plot mode",key="plot_mode",options=["Static", "Animated"],label_visibility="collapsed")

with current_page_col:
    # Page Selection
    st.markdown("# Pages")
    current_page = st.radio("pages",["Default","Music","Vowels","VoiceChanger","Medical"],key="current_page",label_visibility="collapsed")