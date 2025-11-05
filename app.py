import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from ui.forms.acciones_form import show_acciones_form

st.set_page_config(page_title="Calculadora Financiera de Inversiones y bonos", layout="wide")
st.sidebar.title("Navegación")

elije = st.sidebar.radio("Procedimiento a hacer:",["Simulación de cartera y jubilación", "Bonos"])

if elije == "Simulación de cartera y jubilación":
    st.title("💰 Calculadora Financiera de Inversiones")
    show_acciones_form()
   
if elije == "Bonos":
    st.title("💰 Calculadora Financiera de Bonos")