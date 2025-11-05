from utils.utils import convertir_tea_a_periodica, formato_moneda, mostrar_ayuda
import pandas as pd 
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
def show_mod_a_form():
    st.header("📈 Módulo A: Crecimiento de Cartera")
    st.markdown("Calcula cómo crece tu capital en dólares según tus aportes e inversiones.")
    
    # Parámetros de entrada
    with st.expander("⚙️ Parámetros de Inversión", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            edad_actual = st.number_input(
                "Edad Actual",
                min_value=18, max_value=100, value=30, step=1,
                help="Tu edad actual en años"
            )
            
            monto_inicial = st.number_input(
                "Monto Inicial (USD)",
                min_value=0.0, value=10000.0, step=100.0,
                help="Capital inicial que invertirás"
            )
        
        with col2:
            aporte_periodico = st.number_input(
                "Aporte Periódico (USD)",
                min_value=0.0, value=500.0, step=50.0,
                help="Cantidad que aportarás regularmente"
            )
            
            frecuencia = st.selectbox(
                "Frecuencia de Aportes",
                ['Mensual', 'Trimestral', 'Semestral', 'Anual'],
                help="Con qué regularidad realizarás tus aportes"
            )
        
        with col3:
            plazo_anios = st.number_input(
                "Plazo (Años)",
                min_value=1, max_value=70, value=30, step=1,
                help="Número de años que mantendrás tu inversión"
            )
            
            tea_cartera = st.number_input(
                "Tasa Efectiva Anual (%)",
                min_value=0.0, max_value=50.0, value=8.0, step=0.1,
                help="Rentabilidad anual esperada (ej: 8% para fondos diversificados)"
            )
    
    # Validaciones
    if monto_inicial == 0 and aporte_periodico == 0:
        st.warning("⚠️ Debes ingresar un monto inicial o un aporte periódico.")
    else:
        # Cálculos
        periodos_por_anio = {'Mensual': 12, 'Trimestral': 4, 'Semestral': 2, 'Anual': 1}
        num_periodos = periodos_por_anio[frecuencia]
        total_periodos = plazo_anios * num_periodos
        tasa_periodica = convertir_tea_a_periodica(tea_cartera, frecuencia)
        
        # Simulación período a período
        saldo = monto_inicial
        aporte_acumulado = monto_inicial
        datos = []
        
        datos.append({
            'Periodo': 0,
            'Edad': edad_actual,
            'Saldo Inicial': monto_inicial,
            'Intereses': 0,
            'Aporte': 0,
            'Saldo Final': monto_inicial,
            'Aportes Acumulados': monto_inicial
        })
        
        for i in range(1, total_periodos + 1):
            saldo_inicial = saldo
            intereses = saldo * tasa_periodica
            saldo = saldo + intereses + aporte_periodico
            aporte_acumulado += aporte_periodico
            
            # Guardar datos anuales
            if i % num_periodos == 0 or i == total_periodos:
                datos.append({
                    'Periodo': i,
                    'Edad': edad_actual + i // num_periodos,
                    'Saldo Inicial': saldo_inicial,
                    'Intereses': intereses,
                    'Aporte': aporte_periodico,
                    'Saldo Final': saldo,
                    'Aportes Acumulados': aporte_acumulado
                })
        
        df_cartera = pd.DataFrame(datos)
        saldo_final = saldo
        ganancia_total = saldo_final - aporte_acumulado
        
        # Métricas principales
        st.divider()
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "💰 Capital Acumulado",
                formato_moneda(saldo_final),
                f"A los {edad_actual + plazo_anios} años"
            )
        
        with col2:
            st.metric(
                "💵 Total Aportado",
                formato_moneda(aporte_acumulado),
                "Capital invertido"
            )
        
        with col3:
            st.metric(
                "📈 Ganancia Total",
                formato_moneda(ganancia_total),
                f"{(ganancia_total/aporte_acumulado*100):.1f}% ROI"
            )
        
        # Gráfica de crecimiento
        st.divider()
        st.subheader("📊 Proyección de Crecimiento")
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df_cartera['Edad'],
            y=df_cartera['Aportes Acumulados'],
            mode='lines',
            name='Aportes Acumulados',
            fill='tozeroy',
            line=dict(color='#3B82F6', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=df_cartera['Edad'],
            y=df_cartera['Saldo Final'],
            mode='lines',
            name='Capital Total',
            fill='tonexty',
            line=dict(color='#10B981', width=2)
        ))
        
        fig.update_layout(
            xaxis_title="Edad (años)",
            yaxis_title="Valor (USD)",
            hovermode='x unified',
            height=450,
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabla detallada
        st.divider()
        st.subheader("📋 Detalle por Período")
        
        # Mostrar solo datos anuales
        df_mostrar = df_cartera[df_cartera['Periodo'] % num_periodos == 0].copy()
        df_mostrar['Saldo Inicial'] = df_mostrar['Saldo Inicial'].apply(formato_moneda)
        df_mostrar['Intereses'] = df_mostrar['Intereses'].apply(formato_moneda)
        df_mostrar['Aportes Acumulados'] = df_mostrar['Aportes Acumulados'].apply(formato_moneda)
        df_mostrar['Saldo Final'] = df_mostrar['Saldo Final'].apply(formato_moneda)
        
        st.dataframe(
            df_mostrar[['Edad', 'Saldo Inicial', 'Intereses', 'Aportes Acumulados', 'Saldo Final']],
            use_container_width=True,
            hide_index=True
        )
        
        # Botón de descarga
        csv = df_cartera.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar datos en CSV",
            data=csv,
            file_name=f"proyeccion_cartera_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
