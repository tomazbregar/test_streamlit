import streamlit as st

st.set_page_config(page_title='Vibroisolation Calculator',
                   page_icon="https://gitlab.com/pyFBS/pyFBS/-/raw/master/docs/logo/logo-small.png")

import pandas as pd
import numpy as np
import altair as alt


def sfmono():
    font = "SF Mono"

    return {
        "config": {
            "title": {'font': font},
            "axis": {
                "labelFont": font,
                "titleFont": font
            }
        }
    }


alt.themes.register('sfmono', sfmono)
alt.themes.enable('sfmono')


def header():
    st.title("Vibroisolation calculator", anchor=None)

    col1, col2 = st.columns([3,1])
    with col1:
        st.markdown("Choosing an optimal vibroisolation can be a cumbersome task. Majority of complex dynamic systems cannot be simplified into a simple 1-DoF system. However, to quickly access a simple vibroisolation prediction, we can utilize a simple 1-DoF dynamic systen to determine the influence of oscilating mass $m$, damping $c$ and stifness $k$ on the natural frequncy and later on isolation effectiveness.")
    with col2:
        st.image("sdof.png", width = 100)

    st.sidebar.image("https://pyfbs.readthedocs.io/en/latest/_static/logo-big.png",width = 250)
    st.sidebar.title("A simple 1-DoF calculator")
    st.sidebar.write("We present to you a vibroisolation calculator, based on a simple 1-DoF dynamic system. After defining mass, stiffness and damping characteristics, frequency response function is automaticaly generated. Based on the rotatinal speed we can estimate the isolation effectiveness. ")

def app():

    st.header("Math theory")
    my_expander = st.expander(label='Math is hidden by default to not scare people, click to expand!')
    with my_expander:
        st.markdown("Consider a simple 1-DoF system with a mass $m$, suspended on a support with a stiffness $k$ and damping $c$. The displacement of mass is denoted with a variable $u$ and the mass is excited with a harmonic force denoted with $f$.")

        st.markdown("The equation of motion for the particular 1-DoF system can be written as follows:")

        st.markdown(r"""$m \ddot{u} + c\dot{u} + k u = f$""")
        st.markdown("The equation can be solved analyticaly, by defining: ")
        st.markdown(r""" $\frac{k}{m} = \omega_0^2  \quad \text{and} \quad \frac{c}{m}=2\delta\omega_0$""")
        st.markdown("By substituting back into equation we can derive:")


        #st.markdown(r"""$(-\omega^2m+i c\omega + k)u = \frac{f}{m}$""")
        #st.markdown("... ")

        #st.markdown("... ")

        st.markdown(r""" $\bigg(1-\big(\frac{\omega_0}{\omega}\big)^2+2i\delta\big(\frac{\omega_0}{\omega}\big)\bigg)u = \frac{f}{m}$""")
        st.markdown("Finnaly frequency response function is defined as an inverse:")
        st.markdown(r""" $Y = \bigg(1-\big(\frac{\omega_0}{\omega}\big)^2+2i\delta\big(\frac{\omega_0}{\omega}\big)\bigg)^{-1}$ """)






    st.header("Frequency Response Function")

    col1, col2, col3 = st.columns(3)

    with col1:

        stifness = st.number_input(r"""Stiffness [N/m]""", min_value=.1,value =1.,format = "%f")

    with col2:
        mass = st.number_input('Mass [kg]', min_value=.1,value =1.,format = "%f")

    with col3:
        damping = st.number_input('Damping [/]', min_value=0.0001,value =0.01,format = "%f")


    k = stifness
    m = mass
    d = damping

    w0 = np.sqrt(k / m)

    w = np.linspace(0, 3 * w0, 2000)
    r = w / w0

    T = 1/(np.sqrt(1 + (2 * d * r) ** 2) / np.sqrt((1 - r ** 2) ** 2 + (2 * d * r) ** 2))
    Y = (1-(w/w0)**2+2*1j*damping*(w/w0))**(-1)

    Y_angle = np.angle(Y,deg=True)
    Y_abs = np.abs(Y)

    resize = alt.selection_interval(bind='scales')

    source = pd.DataFrame({
        'Frequency': w,
        'Phase': Y_angle,
        'Amplitude': Y_abs,
        'Effectiveness': T

    })

    width = 610
    height = 500
    phase = alt.Chart(source).mark_line().encode(
        x = alt.X('Frequency'),
        y= alt.Y('Phase', scale=alt.Scale(type = "linear",base=10,domain=(-190, 10)))
    ).add_selection(resize).properties(height=1 / 3* height).configure_axis(
    labelFontSize=14,
    titleFontSize=14
    ).configure_line(
    size=5
)
    #.properties(width=width, height=1 / 3 * height)

    amplitude = alt.Chart(source).mark_line().encode(
        x='Frequency',
        y=alt.Y('Amplitude', scale=alt.Scale(type="log", base=10))
    ).add_selection(resize).properties(height=1 / 2 * height).configure_axis(
    labelFontSize=14,
    titleFontSize=14
    ).configure_line(
    size=5
)
    #.properties(width=width, height=1 / 2 * height)

    #AP = alt.vconcat(amplitude,phase).configure_axis(
    #abelFontSize=14,
    #titleFontSize=14
    #).configure_line(
    #size=5
    #)

    nearest = alt.selection(type='single', nearest=True, on='mouseover',
                            fields=['Frequency'], empty='none')

    effectiveness = alt.Chart(source).mark_line(color="#FFAA00").encode(
        x=alt.X('Frequency'),
        y=alt.Y('Effectiveness', scale=alt.Scale(type="log", base=10))
    )
    selectors = alt.Chart(source).mark_point().encode(
        x='Frequency',
        opacity=alt.value(0),
    ).add_selection(
        nearest
    )

    points = effectiveness.mark_point().encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )

    # Draw text labels near the points, and highlight based on selection
    text = effectiveness.mark_text(align='left', dx=5, dy=-5).encode(
        text=alt.condition(nearest, 'Effectiveness', alt.value(' '),format=',.2f')
    ).encode(size=alt.value(16))

    # Draw a rule at the location of the selection
    rules = alt.Chart(source).mark_rule(color='gray').encode(
        x='Frequency',
    ).transform_filter(
        nearest
    )

    #st.altair_chart(AP, use_container_width=True)
    st.altair_chart(amplitude, use_container_width=True)
    st.altair_chart(phase, use_container_width=True)

    st.header("Isolation Effectiveness")

    #st.markdown("Bla bla bla")

    gg = alt.layer(effectiveness, selectors, points, rules, text).properties(width=width, height=300).add_selection(resize).configure_axis(labelFontSize=14,titleFontSize=14).configure_line(size=5)
    st.altair_chart(gg, use_container_width=True)


    st.subheader("Isolation from operating speed")

    col1, col2 = st.columns([0.9, 2])



    with col1:
        operating = st.number_input(r"""Rotational speed [rpm]""", min_value=.1,value =1.,format = "%f")
        operating_omega = operating/60
        r = operating_omega / w0
        effect = 1/(np.sqrt(1 + (2 * d * r) ** 2) / np.sqrt((1 - r ** 2) ** 2 + (2 * d * r) ** 2))

    with col2:
        st.markdown(r"""Natural frequency of the sytem is equal to $\omega_0 = %4.1f \text{ Hz}$""" % (w0))
        st.markdown(r"""Rotational speed is equal to $\omega = %4.2f \text{ Hz}$""" % operating_omega)

        st.markdown("Isolation effectiveness is equal to  $E = %4.2f$" % effect)


def get_in_touch():
    st.sidebar.header(":mailbox: Get In Touch With Us!")
    st.sidebar.markdown(r"""Let us know what you think. Do you have an idea for a simple webapp for structural dynamics? 
    """)

    contact_form = """
    <form 
    action="https://formsubmit.co/bregar.toma@gmail.com" 
    method="POST">
        <input type = "text" name= "name" placeholder = "Your name" required>
        <input type = "email" name= "email" placeholder = "Your email" required>
        <textarea name= "message" placeholder = "Your message here" required>
        <button type = "submit">Send</button>
    """

    def local_css(file_name):
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html= True)

    local_css("style/style.css")

    st.sidebar.markdown(contact_form, unsafe_allow_html= True)

    st.sidebar.markdown(r"""<div style="text-align: right"> <b>pyFBS Team</b> </div>""", unsafe_allow_html= True)


hide_st_style = """ 
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """
st.markdown(hide_st_style, unsafe_allow_html=True)

if __name__ == '__main__':
    header()
    app()
    get_in_touch()

