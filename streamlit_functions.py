import numpy as np
import pandas as pd
import scipy.fft as fft
import plotly.express as px
import wave
import streamlit as st
from scipy.io.wavfile import write
import scipy.signal as sig
import plotly.graph_objs as go
import streamlit_vertical_slider as svs
from PIL import Image
import librosa
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import streamlit.components.v1 as components

def signalTransform():
    if st.session_state["uploaded_file"]:
        global yf,duration
        audio = wave.open(st.session_state["uploaded_file"], 'rb')
        sample_rate = audio.getframerate()
        n_channels = audio.getnchannels()
        n_samples = audio.getnframes()
        duration = n_samples / sample_rate
        signal_wave = audio.readframes(-1)   

        signal_x_axis = np.arange(0,duration,1/sample_rate)
        signal_y_axis = np.frombuffer(signal_wave, dtype=np.int16)

        yf = fft.rfft(signal_y_axis)
        xf = fft.rfftfreq(n_samples,1/sample_rate)
        equalizerModes(duration,yf,xf)

        modified_signal = fft.irfft(yf)
        
        male_modified_signal = librosa.effects.pitch_shift(modified_signal, sr = 44100, n_steps= -5)
    
        modified_signal_channel = np.int16(male_modified_signal if (st.session_state["gender"] == "Male" and st.session_state["current_page"] == "VoiceChanger") else modified_signal)

        if n_channels == 1:
            write("Modified.wav", sample_rate, modified_signal_channel)
            return  signal_x_axis,signal_y_axis,modified_signal,sample_rate,duration
        
        else:
            write("Modified.wav", sample_rate*2, modified_signal_channel)
            return  signal_x_axis,signal_y_axis[:len(signal_x_axis)],modified_signal[:len(signal_x_axis)],sample_rate,duration

    else:
        return np.arange(0,1,0.1),np.zeros(10),np.zeros(10),1,1

def plotSignals():
    signal_x_axis,signal_y_axis,modified_signal,sample_rate,duration = signalTransform()
    signal_figure = px.line(x = signal_x_axis,y = modified_signal)
    signal_figure['data'][0]['showlegend'] = True
    signal_figure['data'][0]['name'] = 'Modified'
    signal_figure.add_scatter(name="Original", x=signal_x_axis,y=signal_y_axis, line_color="#FF4B4B",visible="legendonly")
    signal_figure.update_layout(margin=dict(l=0, r=0, t=0, b=0), legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
    signal_figure.update_xaxes(title="Time", linewidth=2, linecolor='black',gridcolor='#5E5E5E', title_font=dict(size=24, family='Arial'))
    signal_figure.update_yaxes(title="Amplitude", linewidth=2, linecolor='black',gridcolor='#5E5E5E', title_font=dict(size=24, family='Arial'))
 
    original_freqs, original_time, original_Pxx = sig.spectrogram(signal_y_axis, sample_rate)
    modified_freqs, modified_time, modified_Pxx = sig.spectrogram(modified_signal, sample_rate)

    traces = [go.Heatmap(x= modified_time, y= modified_freqs, z= 10*np.log10(modified_Pxx),name="Modified"),go.Heatmap(x= original_time, y= original_freqs, z= 10*np.log10(original_Pxx), visible="legendonly",name="Original")]
    layout = go.Layout(yaxis = dict(title = 'Frequency'), xaxis = dict(title = 'Time'), margin= dict(l=0, r=0, t=0, b=0))
    spec_figure = go.Figure(data=traces, layout=layout)
    spec_figure.update_traces(showlegend=True,colorscale='Jet')
    spec_figure.update_layout(showlegend=True,legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
    spec_figure.update_xaxes(title_font=dict(size=24, family='Arial'))
    spec_figure.update_yaxes(title_font=dict(size=24, family='Arial'))

    return signal_figure, spec_figure


def set_ranges(dict):

    for item in dict:
            yf[int(duration*dict[item][0]):int(duration* dict[item][1])] *= st.session_state[f"{item}"]

def equalizerModes(duration,yf,xf):
    
    if st.session_state["current_page"] == "Default":
        ranges = np.arange(0,np.abs(xf.max()),np.abs(xf.max())/10)
        for i in range(10):
            if i < 9:
                yf[int(duration*ranges[i]):int(duration* ranges[i+1])] *= st.session_state.get(f"slider{i+1}")
            else:
                yf[int(duration*ranges[-1]):int(duration* xf.max())] *= st.session_state.get(f"slider10")

    if st.session_state["current_page"] == "Music":
        instruments = {"drum_value":[0,1000],"piano_value":[1000,5000],"violin_value":[5000,10000]}
        
        set_ranges(instruments)

    if st.session_state["current_page"] == "Vowels":
        letters = {"letterA_value":[0,1000],"letterB_value":[1000,5000],"letterT_value":[5000,10000],"letterK_value":[10000,20000]}
       
        set_ranges(letters)
            
    if st.session_state["current_page"] == "Medical":
        arrhythmias = {"Arrhythmia1_value":[60,90],"Arrhythmia2_value":[90,250],"Arrhythmia3_value":[250,300]}
        
        set_ranges(arrhythmias)

    

def defaultPage():
    columns = st.columns(10)
    for index in range(len(columns)):
        if f"slider{index+1}" not in st.session_state:
            st.session_state[f"slider{index+1}"] = 1

    for column in columns:
        with column:
            svs.vertical_slider(key = f"slider{columns.index(column)+1}", 
                                min_value=0,
                                max_value=5,
                                step=1,
                                default_value=1,
                                thumb_color="#2481ce",
                                slider_color="#061724",
                                track_color="lightgray")


def musicSlidersAndIcons(path='',sliderName='',key=''):

    image = Image.open(path)
    st.image(image,width=150)
    st.slider(sliderName,0,5,1,1,key=key,label_visibility="collapsed")

def musicPage():
    instrument1_col,instrument2_col,instrument3_col = st.columns(3)
    with instrument1_col:
       
        musicSlidersAndIcons('icons/drum.png',"Drum Sound","drum_value")

    with instrument2_col:
       
        musicSlidersAndIcons('icons/violin.png',"Violin Sound","violin_value")
    with instrument3_col:
        
        musicSlidersAndIcons('icons/piano.png',"Piano Sound","piano_value")

def vowelsPage():
    letters = ["A","B","T","K"]
    letters_columns = st.columns(4)
    for column in letters_columns:
        i = letters_columns.index(column)
        with column:
            st.slider(f"letter {letters[i]}",0,5,1,1,key=f"letter{letters[i]}_value")

def voiceChangerPage():
    female_col,selectbox_col,male_col = st.columns((1,2,1))
    with female_col:
        female_image = Image.open('icons/female.png')
        st.image(female_image,width=150)
   
    with selectbox_col:
        for _ in range(4):
            st.markdown("",unsafe_allow_html=True)
        st.select_slider("Change Voice to:",options=["Female","Male"],key="gender",label_visibility="collapsed")

    with male_col:
        male_image = Image.open('icons/male.png')
        st.image(male_image,width=150)

def medicalPage():
    columns = st.columns(3)
    for column in columns:
        i = columns.index(column)+1
        with column:
            st.slider(f"Arrhythmia{i}",0,5,1,1,key=f"Arrhythmia{i}_value")


def dynamicPlot():
    signal_x_axis,signal_y_axis,modified_signal,sample_rate,duration = signalTransform()
    
    plt.style.use('dark_background')

    under_x = signal_x_axis[::len(signal_x_axis)//400]
    under_y = signal_y_axis[::len(signal_y_axis)//400]

    fig, ax1 = plt.subplots()
    fig.set_figwidth(10)
    fig.set_figheight(3)
    line, = ax1.plot([], [])
    plt.ylim(under_y.min()*1.5,under_y.max()*1.5)
    
    tempx = []
    tempy = []

    def animate(i):
        tempx.append(under_x[i])
        tempy.append(under_y[i])
        line.set_data(tempx,tempy)
        if i>50:
            tempx.pop(0)
            tempy.pop(0)
        plt.xlim(tempx[0],tempx[-1])
        return line,

    ani = animation.FuncAnimation(fig, animate, interval=20, blit=True, frames=len(under_x))

    components.html(ani.to_jshtml(default_mode="once"),height=400,)

# def AnimatedPlot():
#     signal_x_axis,signal_y_axis,modified_signal,sample_rate,duration = signalTransform()
#     df = pd.DataFrame({"amplitude":signal_y_axis,"time":signal_x_axis})
#     if len(df) != 0:
#         df = df[::(len(df)//1000)]
#     Frame_1 = []
#     time_list=[0]
#     amplitude_list=[df["amplitude"][0]]
#     for ind,df_r in df.iterrows():
#         time_list.append(df_r["time"])
#         amplitude_list.append(df_r["amplitude"])
#         Frame_1.append(go.Frame(data=[go.Scatter(x=time_list,y=amplitude_list,mode="lines")]))
#     fig = go.Figure(
#         data=[go.Scatter(x=[0, 0], y=[0, 0])],
#         layout=go.Layout(
#             xaxis=dict(range=[0, time_list[-1]], autorange=False),
#             yaxis=dict(range=[df["amplitude"].min()*1.5, df["amplitude"].max()*1.5], autorange=False),
#             margin= dict(l=0, r=0, t=0, b=0)
#     ),
#         frames=Frame_1
#     )

#     fig["layout"]["updatemenus"] = [
#         {
#             "buttons": [
#                 {
#                     "args": [None, {"frame": {"duration": 1, "redraw": False},
#                                     "fromcurrent": True, "transition": {"duration": 0}}],
#                     "label": "Play",
#                     "method": "animate"
#                 },
#                 {
#                     "args": [[None], {"frame": {"duration": 0, "redraw": False},
#                                     "mode": "immediate",
#                                     "transition": {"duration": 0}}],
#                     "label": "Pause",
#                     "method": "animate"
#                 }
#             ],
#             "direction": "left",
#             "pad": {"t": 50},
#             "showactive": False,
#             "type": "buttons",
#             "x": 0.1,
#             "xanchor": "right",
#             "y": 0,
#             "yanchor": "top"
#         }
#     ]

#     st.plotly_chart(fig)