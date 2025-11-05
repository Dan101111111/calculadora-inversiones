from utils.utils import convertir_tea_a_periodica, formato_moneda, mostrar_ayuda
import pandas as pd 
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
def show_mod_b_form():
    st.header("🏦 Módulo B: Proyección de Retiro")
    st.markdown("Calcula tu pensión mensual o retiro total según el capital acumulado.")
    
    # Primero calculamos la cartera (igual que módulo A)
    with st.expander("⚙️ Parámetros de Acumulación", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            edad_actual = st.number_input("Edad Actual", 18, 100, 30, 1)
            monto_inicial = st.number_input("Monto Inicial (USD)", 0.0, value=10000.0, step=100.0)
        
        with col2:
            aporte_periodico = st.number_input("Aporte Periódico (USD)", 0.0, value=500.0, step=50.0)
            frecuencia = st.selectbox("Frecuencia", ['Mensual', 'Trimestral', 'Semestral', 'Anual'])
        
        with col3:
            plazo_anios = st.number_input("Plazo (Años)", 1, 70, 30, 1)
            tea_cartera = st.number_input("TEA Acumulación (%)", 0.0, 50.0, 8.0, 0.1)
    
    # Cálculo de capital acumulado
    periodos_por_anio = {'Mensual': 12, 'Trimestral': 4, 'Semestral': 2, 'Anual': 1}
    num_periodos = periodos_por_anio[frecuencia]
    total_periodos = plazo_anios * num_periodos
    tasa_periodica = convertir_tea_a_periodica(tea_cartera, frecuencia)
    
    saldo = monto_inicial
    aporte_total = monto_inicial
    
    for i in range(1, total_periodos + 1):
        intereses = saldo * tasa_periodica
        saldo = saldo + intereses + aporte_periodico
        aporte_total += aporte_periodico
    
    capital_acumulado = saldo
    ganancia_total = capital_acumulado - aporte_total
    edad_retiro = edad_actual + plazo_anios
    
    # Parámetros de retiro
    st.divider()
    with st.expander("🎯 Opciones de Retiro", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            tipo_retiro = st.radio(
                "Tipo de Retiro",
                ['Retiro Total', 'Pensión Mensual'],
                help="Elige si deseas retirar todo o recibir pensión mensual"
            )
            
            tipo_impuesto = st.selectbox(
                "Tipo de Impuesto",
                ['Bolsa Local (5%)', 'Fuente Extranjera (29.5%)'],
                help="Impuesto aplicable según el origen de las inversiones"
            )
        
        with col2:
            if tipo_retiro == 'Pensión Mensual':
                tea_retiro = st.number_input(
                    "TEA Durante Retiro (%)",
                    0.0, 50.0, 5.0, 0.1,
                    help="Rentabilidad esperada durante el retiro"
                )
                
                anios_retiro = st.number_input(
                    "Años de Retiro",
                    1, 50, 25, 1,
                    help="Durante cuántos años recibirás pensión"
                )
    
    # Cálculo de impuestos
    tasa_impuesto = 0.295 if 'Extranjera' in tipo_impuesto else 0.05
    impuesto = ganancia_total * tasa_impuesto
    capital_neto = capital_acumulado - impuesto
    
    # Resultados
    st.divider()
    st.subheader("💼 Resumen Financiero")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Capital Total", formato_moneda(capital_acumulado))
    
    with col2:
        st.metric("Ganancia", formato_moneda(ganancia_total), delta="Antes de impuestos")
    
    with col3:
        st.metric("Impuesto", formato_moneda(impuesto), delta=f"-{tasa_impuesto*100}%", delta_color="inverse")
    
    with col4:
        st.metric("Capital Neto", formato_moneda(capital_neto), delta="Disponible")
    
    st.divider()
    
    if tipo_retiro == 'Retiro Total':
        st.success(f"### 💰 Retiro Total: {formato_moneda(capital_neto)}")
        st.info(f"📅 Este monto estará disponible cuando cumplas {edad_retiro} años.")
        
    else:  # Pensión Mensual
        tasa_mensual = convertir_tea_a_periodica(tea_retiro, 'Mensual')
        meses_retiro = anios_retiro * 12
        
        # Fórmula de anualidad: PMT = PV * r / (1 - (1 + r)^-n)
        pension_mensual = capital_neto * tasa_mensual / (1 - (1 + tasa_mensual) ** -meses_retiro)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.success(f"### 💵 Pensión Mensual: {formato_moneda(pension_mensual)}")
            st.info(f"📅 Durante {anios_retiro} años ({meses_retiro} meses)")
            st.info(f"🎂 Desde los {edad_retiro} hasta los {edad_retiro + anios_retiro} años")
        
        with col2:
            total_recibido = pension_mensual * meses_retiro
            st.metric("Total a Recibir", formato_moneda(total_recibido))
            st.metric("Pensión Anual", formato_moneda(pension_mensual * 12))
    
    # Comparación de escenarios
    st.divider()
    st.subheader("🔄 Comparación de Escenarios")
    
    col1, col2 = st.columns(2)
    
    with col1:
        edad_comp_1 = st.number_input("Edad Retiro 1", edad_actual + 1, 100, edad_retiro, 1)
    
    with col2:
        edad_comp_2 = st.number_input("Edad Retiro 2", edad_actual + 1, 100, min(edad_retiro + 5, 70), 1)
    
    def calcular_escenario(edad_ret):
        anios = edad_ret - edad_actual
        if anios <= 0:
            return None
        
        total_per = anios * num_periodos
        s = monto_inicial
        ap = monto_inicial
        
        for i in range(1, total_per + 1):
            s = s + s * tasa_periodica + aporte_periodico
            ap += aporte_periodico
        
        gan = s - ap
        imp = gan * tasa_impuesto
        cap_net = s - imp
        
        if tipo_retiro == 'Pensión Mensual':
            tm = convertir_tea_a_periodica(tea_retiro, 'Mensual')
            mr = anios_retiro * 12
            pens = cap_net * tm / (1 - (1 + tm) ** -mr)
        else:
            pens = 0
        
        return {
            'edad': edad_ret,
            'capital': s,
            'neto': cap_net,
            'pension': pens
        }
    
    esc1 = calcular_escenario(edad_comp_1)
    esc2 = calcular_escenario(edad_comp_2)
    
    if esc1 and esc2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Escenario 1: Retiro a los {esc1['edad']} años**")
            st.metric("Capital Neto", formato_moneda(esc1['neto']))
            if tipo_retiro == 'Pensión Mensual':
                st.metric("Pensión Mensual", formato_moneda(esc1['pension']))
        
        with col2:
            st.markdown(f"**Escenario 2: Retiro a los {esc2['edad']} años**")
            diferencia = esc2['neto'] - esc1['neto']
            st.metric("Capital Neto", formato_moneda(esc2['neto']), delta=formato_moneda(diferencia))
            if tipo_retiro == 'Pensión Mensual':
                dif_pension = esc2['pension'] - esc1['pension']
                st.metric("Pensión Mensual", formato_moneda(esc2['pension']), delta=formato_moneda(dif_pension))