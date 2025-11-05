import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Calculadora Financiera de Inversiones", layout="wide")

st.title("💰 Calculadora Financiera de Inversiones")


elije = st.sidebar.radio("Procedimiento a hacer:",["Simulación de cartera y jubilación", "Bonos"])

if elije == "Simulación de cartera y jubilación":


    st.header("Parámetros de Inversión")

    edad_actual = st.number_input("Edad actual", value=30)
    if edad_actual < 18 or edad_actual > 100:
        st.error("La edad debe estar entre 18 y 100 años.")


    monto_inicial = st.number_input("Monto inicial (USD)", step=100)
    if monto_inicial < 0:
        st.error("El monto no debe ser negativo.")

    aporte_periodico = st.number_input("Aporte periódico (USD) (opcional)", min_value=0.0, value=0.0, step=50.0)

    frecuencia_aporte = st.selectbox(
        "Frecuencia de aportes",
        ["Mensual", "Trimestral", "Semestral", "Anual"]
    )

    opcion_plazo = st.radio("Selecciona el tipo de plazo", ["Años", "Edad de jubilación"])
    if opcion_plazo == "Años":
        plazo = st.slider("Plazo (años)", min_value=1, max_value=100, value=30)
    else:
        edad_jubilacion = st.slider("Edad de jubilación", min_value=30, max_value=100, value=60)
        plazo = edad_jubilacion - edad_actual

    TEA = st.number_input("Tasa Efectiva Anual (TEA) %", min_value=0.0, max_value=100.0, value=10.0, step=0.1)

    tipo_impuesto = st.selectbox(
        "Tipo de impuesto",
        ["5% bolsa local", "29.5% fuente extranjera"]
    )

