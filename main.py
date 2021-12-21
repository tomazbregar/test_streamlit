import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import base64

def app():
    st.title("A simple 1-DoF calculator", anchor=None)

    col1, col2, col3 = st.columns(3)

    with col1:
        stifness = st.number_input('Stifness [N/m]', min_value=.1,value =1.,format = "%f")

    with col2:
        mass = st.number_input('Mass [kg]', min_value=.1,value =1.,format = "%f")

    with col3:
        damping = st.number_input('Damping [/]', min_value=0.0001,value =0.01,format = "%f")


    k = stifness
    m = mass
    d = damping

    w0 = np.sqrt(k / m)

    w = np.linspace(0, 3 * w0, 1000)
    r = w / w0

    T = np.sqrt(1 + (2 * d * r) ** 2) / np.sqrt((1 - r ** 2) ** 2 + (2 * d * r) ** 2)

    source = pd.DataFrame({
        'Frequency': w,
        'Transmissibility': T
    })

    c = alt.Chart(source).mark_line().encode(
        x='Frequency',
        y= alt.Y('Transmissibility', scale=alt.Scale(type = "log",base=10))
    ).interactive()

    st.altair_chart(c, use_container_width=True)


if __name__ == '__main__':
    app()

