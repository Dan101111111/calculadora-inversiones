from utils.utils import convertir_tea_a_periodica, formato_moneda, mostrar_ayuda
import pandas as pd 
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
def show_mod_c_form():
    st.header("📊 Módulo C: Valoración de Bonos")
    st.markdown("Calcula el valor presente de un bono según sus características.")
    
    with st.expander("⚙️ Parámetros del Bono", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            valor_nominal = st.number_input(
                "Valor Nominal (USD)",
                min_value=100.0, value=1000.0, step=100.0,
                help="Valor que recibirás al vencimiento del bono"
            )
            
            tasa_cupon = st.number_input(
                "Tasa Cupón (% TEA)",
                min_value=0.0, max_value=50.0, value=6.0, step=0.1,
                help="Tasa de interés que paga el bono anualmente"
            )
        
        with col2:
            frecuencia_bono = st.selectbox(
                "Frecuencia de Pago",
                ['Mensual', 'Bimestral', 'Trimestral', 'Cuatrimestral', 'Semestral', 'Anual'],
                index=4,
                help="Cada cuánto tiempo recibirás los cupones"
            )
            
            plazo_bono = st.number_input(
                "Plazo (Años)",
                min_value=1, max_value=50, value=5, step=1,
                help="Años hasta el vencimiento del bono"
            )
        
        with col3:
            tea_bono = st.number_input(
                "Tasa de Retorno Esperada (% TEA)",
                min_value=0.0, max_value=50.0, value=7.0, step=0.1,
                help="Tasa de descuento para calcular el valor presente"
            )
    
    # Cálculos del bono
    periodos_bono = {
        'Mensual': 12, 'Bimestral': 6, 'Trimestral': 4,
        'Cuatrimestral': 3, 'Semestral': 2, 'Anual': 1
    }
    
    num_periodos_bono = periodos_bono[frecuencia_bono]
    total_periodos_bono = plazo_bono * num_periodos_bono
    
    tasa_cupon_periodica = convertir_tea_a_periodica(tasa_cupon, frecuencia_bono)
    tasa_descuento_periodica = convertir_tea_a_periodica(tea_bono, frecuencia_bono)
    
    cupon = valor_nominal * tasa_cupon_periodica
    
    # Calcular flujos y valor presente
    flujos = []
    valor_presente_total = 0
    
    for i in range(1, total_periodos_bono + 1):
        if i == total_periodos_bono:
            flujo = cupon + valor_nominal
        else:
            flujo = cupon
        
        vp = flujo / ((1 + tasa_descuento_periodica) ** i)
        valor_presente_total += vp
        
        flujos.append({
            'Periodo': i,
            'Año': round(i / num_periodos_bono, 2),
            'Flujo': flujo,
            'Valor Presente': vp
        })
    
    df_flujos = pd.DataFrame(flujos)
    
    # Métricas del bono
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💎 Valor Presente", formato_moneda(valor_presente_total))
    
    with col2:
        st.metric("📄 Valor Nominal", formato_moneda(valor_nominal))
    
    with col3:
        st.metric("💰 Cupón Periódico", formato_moneda(cupon))
    
    with col4:
        diferencia = valor_presente_total - valor_nominal
        tipo = "Premium" if diferencia > 0 else "Descuento" if diferencia < 0 else "Par"
        st.metric("Tipo de Bono", tipo, delta=formato_moneda(diferencia))
    
    # Interpretación
    st.divider()
    if valor_presente_total > valor_nominal:
        st.success(f"✅ El bono cotiza con **prima** (sobre par). El VP es {formato_moneda(valor_presente_total - valor_nominal)} mayor que el valor nominal.")
    elif valor_presente_total < valor_nominal:
        st.warning(f"⚠️ El bono cotiza con **descuento** (bajo par). El VP es {formato_moneda(valor_nominal - valor_presente_total)} menor que el valor nominal.")
    else:
        st.info("ℹ️ El bono cotiza **a la par**. El valor presente es igual al valor nominal.")
    
    # Gráfica de flujos
    st.divider()
    st.subheader("📊 Análisis de Flujos")
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_flujos['Año'],
        y=df_flujos['Flujo'],
        name='Flujo de Caja',
        marker_color='#3B82F6'
    ))
    
    fig.add_trace(go.Bar(
        x=df_flujos['Año'],
        y=df_flujos['Valor Presente'],
        name='Valor Presente',
        marker_color='#10B981'
    ))
    
    fig.update_layout(
        xaxis_title="Año",
        yaxis_title="Valor (USD)",
        barmode='group',
        height=400,
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabla de flujos
    st.divider()
    st.subheader("📋 Detalle de Flujos")
    
    df_mostrar = df_flujos.copy()
    df_mostrar['Flujo'] = df_mostrar['Flujo'].apply(formato_moneda)
    df_mostrar['Valor Presente'] = df_mostrar['Valor Presente'].apply(formato_moneda)
    
    st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
    
    # Resumen final
    st.divider()
    with st.container():
        st.subheader("📌 Resumen del Bono")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Valor Nominal:** {formato_moneda(valor_nominal)}")
            st.write(f"**Tasa Cupón:** {tasa_cupon}% TEA")
            st.write(f"**Frecuencia:** {frecuencia_bono}")
            st.write(f"**Cupón por Período:** {formato_moneda(cupon)}")
        
        with col2:
            st.write(f"**Plazo:** {plazo_bono} años ({total_periodos_bono} períodos)")
            st.write(f"**Tasa de Descuento:** {tea_bono}% TEA")
            st.write(f"**Total de Flujos:** {formato_moneda(df_flujos['Flujo'].sum())}")
            st.write(f"**Valor Presente:** {formato_moneda(valor_presente_total)}")
    
    # Descarga
    csv = df_flujos.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar flujos en CSV",
        data=csv,
        file_name=f"valoracion_bono_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )