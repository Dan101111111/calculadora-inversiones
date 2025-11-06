from utils.utils import convertir_tea_a_periodica, formato_moneda
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime


def calcular_valor_bono(valor_nominal, tasa_cupon, tasa_descuento, plazo_anos,
                        frecuencia_cupon, tipo_tasa_cupon='anual'):
    """
    Calcula el valor presente de un bono

    tipo_tasa_cupon: 'anual' o 'mensual' (para casos como Cementos Pacasmayo)
    """
    periodos_map = {
        'Mensual': 12, 'Bimestral': 6, 'Trimestral': 4,
        'Cuatrimestral': 3, 'Semestral': 2, 'Anual': 1
    }

    num_periodos = periodos_map[frecuencia_cupon]
    total_periodos = plazo_anos * num_periodos

    # Convertir tasas a periódicas
    if tipo_tasa_cupon == 'mensual':
        # Si la tasa cupón ya es mensual, convertir a TEA primero
        tasa_cupon_anual = ((1 + tasa_cupon / 100) ** 12 - 1) * 100
        tasa_cupon_periodica = convertir_tea_a_periodica(tasa_cupon_anual, frecuencia_cupon)
    else:
        tasa_cupon_periodica = convertir_tea_a_periodica(tasa_cupon, frecuencia_cupon)

    tasa_descuento_periodica = convertir_tea_a_periodica(tasa_descuento, frecuencia_cupon)

    cupon = valor_nominal * tasa_cupon_periodica

    # Calcular valor presente
    valor_presente = 0
    flujos = []

    for i in range(1, total_periodos + 1):
        if i == total_periodos:
            flujo = cupon + valor_nominal
        else:
            flujo = cupon

        vp = flujo / ((1 + tasa_descuento_periodica) ** i)
        valor_presente += vp

        flujos.append({
            'Periodo': i,
            'Flujo': flujo,
            'VP': vp
        })

    return {
        'valor_presente': valor_presente,
        'cupon_periodico': cupon,
        'total_periodos': total_periodos,
        'tasa_cupon_periodica': tasa_cupon_periodica,
        'tasa_descuento_periodica': tasa_descuento_periodica,
        'flujos': flujos
    }


def show_evaluacion_cartera():
    st.header("🏦 Evaluación de Cartera de Bonos")
    st.markdown("**Caso: Fondo de Pensiones 'Perú Futuro'**")
    st.info("📌 Evalúa múltiples bonos simultáneamente para decidir la mejor asignación del portafolio")

    # Configuración del portafolio
    with st.expander("💰 Configuración del Portafolio", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            monto_invertir = st.number_input(
                "Monto Total a Invertir (S/)",
                min_value=100000.0,
                value=2000000.0,
                step=100000.0,
                help="Monto total disponible para inversión"
            )

        with col2:
            moneda = st.selectbox(
                "Moneda",
                ['Soles (S/)', 'Dólares (USD)'],
                help="Moneda de la inversión"
            )

    # Definición de bonos
    st.divider()
    st.subheader("📋 Bonos a Evaluar")

    # Opción: Usar datos predefinidos o personalizados
    usar_caso_estudio = st.checkbox(
        "Usar caso de estudio (Alicorp, Banco Ripley, Cementos Pacasmayo)",
        value=True
    )

    if usar_caso_estudio:
        # Bonos del caso de estudio
        bonos = [
            {
                'Emisor': 'Alicorp',
                'Tasa Cupón': 7.0,
                'Tipo Tasa': 'anual',
                'Años': 15,
                'Valor Nominal': 1000,
                'Frecuencia': 'Anual',
                'Rendimiento Requerido': 8.0
            },
            {
                'Emisor': 'Banco Ripley',
                'Tasa Cupón': 6.5,
                'Tipo Tasa': 'anual',
                'Años': 8,
                'Valor Nominal': 1000,
                'Frecuencia': 'Semestral',
                'Rendimiento Requerido': 7.5
            },
            {
                'Emisor': 'Cementos Pacasmayo',
                'Tasa Cupón': 0.9,
                'Tipo Tasa': 'mensual',
                'Años': 5,
                'Valor Nominal': 1000,
                'Frecuencia': 'Trimestral',
                'Rendimiento Requerido': 6.0
            }
        ]

        st.success("✅ Usando bonos del caso de estudio del Fondo de Pensiones")

        # Mostrar tabla de bonos
        df_bonos_info = pd.DataFrame([
            {
                'Empresa': b['Emisor'],
                'Tasa Cupón': f"{b['Tasa Cupón']}% {'anual' if b['Tipo Tasa'] == 'anual' else 'mensual'}",
                'Años': b['Años'],
                'Valor Nominal': formato_moneda(b['Valor Nominal']),
                'Pago Interés': b['Frecuencia'],
                'Rendimiento Req.': f"{b['Rendimiento Requerido']}%"
            }
            for b in bonos
        ])
        st.dataframe(df_bonos_info, use_container_width=True, hide_index=True)

    else:
        # Permitir personalización
        num_bonos = st.number_input("Número de bonos a evaluar", min_value=2, max_value=10, value=3)

        bonos = []
        for i in range(num_bonos):
            with st.expander(f"Bono {i + 1}"):
                col1, col2, col3 = st.columns(3)

                with col1:
                    emisor = st.text_input(f"Emisor", value=f"Bono {i + 1}", key=f"emisor_{i}")
                    tasa_cupon = st.number_input(f"Tasa Cupón (%)", value=6.0, key=f"cupon_{i}")
                    tipo_tasa = st.selectbox("Tipo", ['anual', 'mensual'], key=f"tipo_{i}")

                with col2:
                    anos = st.number_input(f"Años", min_value=1, value=5, key=f"anos_{i}")
                    valor_nominal = st.number_input(f"Valor Nominal", value=1000.0, key=f"vn_{i}")

                with col3:
                    frecuencia = st.selectbox(
                        f"Frecuencia",
                        ['Mensual', 'Bimestral', 'Trimestral', 'Cuatrimestral', 'Semestral', 'Anual'],
                        key=f"freq_{i}"
                    )
                    rendimiento = st.number_input(f"Rendimiento Req. (%)", value=7.0, key=f"rend_{i}")

                bonos.append({
                    'Emisor': emisor,
                    'Tasa Cupón': tasa_cupon,
                    'Tipo Tasa': tipo_tasa,
                    'Años': anos,
                    'Valor Nominal': valor_nominal,
                    'Frecuencia': frecuencia,
                    'Rendimiento Requerido': rendimiento
                })

    # PARTE 1: CÁLCULO DEL VALOR TEÓRICO
    st.divider()
    st.subheader("📊 Parte 1: Valor Teórico de Cada Bono")

    resultados = []

    for bono in bonos:
        resultado = calcular_valor_bono(
            valor_nominal=bono['Valor Nominal'],
            tasa_cupon=bono['Tasa Cupón'],
            tasa_descuento=bono['Rendimiento Requerido'],
            plazo_anos=bono['Años'],
            frecuencia_cupon=bono['Frecuencia'],
            tipo_tasa_cupon=bono['Tipo Tasa']
        )

        resultado['emisor'] = bono['Emisor']
        resultado['valor_nominal'] = bono['Valor Nominal']
        resultado['tasa_cupon'] = bono['Tasa Cupón']
        resultado['rendimiento'] = bono['Rendimiento Requerido']
        resultado['anos'] = bono['Años']
        resultado['frecuencia'] = bono['Frecuencia']

        resultados.append(resultado)

    # Tabla de valores teóricos
    df_valores = pd.DataFrame([
        {
            'Emisor': r['emisor'],
            'Valor Nominal': formato_moneda(r['valor_nominal']),
            'Valor Teórico': formato_moneda(r['valor_presente']),
            'Diferencia': formato_moneda(r['valor_presente'] - r['valor_nominal']),
            'Precio (%)': f"{(r['valor_presente'] / r['valor_nominal'] * 100):.2f}%"
        }
        for r in resultados
    ])

    st.dataframe(df_valores, use_container_width=True, hide_index=True)

    # PARTE 2: IDENTIFICACIÓN DE PRIMAS Y DESCUENTOS
    st.divider()
    st.subheader("🏷️ Parte 2: Primas y Descuentos")

    for r in resultados:
        diferencia = r['valor_presente'] - r['valor_nominal']

        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            st.write(f"**{r['emisor']}**")

        with col2:
            if diferencia > 1:  # Tolerancia para errores de redondeo
                st.success("✅ Sobre la par (Prima)")
            elif diferencia < -1:
                st.error("⚠️ Bajo la par (Descuento)")
            else:
                st.info("➖ A la par")

        with col3:
            st.metric("Diferencia", formato_moneda(diferencia))

        # Explicación
        if diferencia > 1:
            st.caption(
                f"💡 El cupón ({r['tasa_cupon']}%) es mayor que el rendimiento requerido ({r['rendimiento']}%), por lo que el bono vale más.")
        elif diferencia < -1:
            st.caption(
                f"💡 El cupón ({r['tasa_cupon']}%) es menor que el rendimiento requerido ({r['rendimiento']}%), por lo que el bono vale menos.")

    # PARTE 3: ANÁLISIS DE SENSIBILIDAD
    st.divider()
    st.subheader("📈 Parte 3: Análisis de Sensibilidad")

    sensibilidad_data = []

    for bono in bonos:
        # Escenario base
        base = calcular_valor_bono(
            bono['Valor Nominal'],
            bono['Tasa Cupón'],
            bono['Rendimiento Requerido'],
            bono['Años'],
            bono['Frecuencia'],
            bono['Tipo Tasa']
        )

        # Escenario +1%
        alto = calcular_valor_bono(
            bono['Valor Nominal'],
            bono['Tasa Cupón'],
            bono['Rendimiento Requerido'] + 1.0,
            bono['Años'],
            bono['Frecuencia'],
            bono['Tipo Tasa']
        )

        # Escenario -1%
        bajo = calcular_valor_bono(
            bono['Valor Nominal'],
            bono['Tasa Cupón'],
            bono['Rendimiento Requerido'] - 1.0,
            bono['Años'],
            bono['Frecuencia'],
            bono['Tipo Tasa']
        )

        cambio_alto = base['valor_presente'] - alto['valor_presente']
        cambio_bajo = bajo['valor_presente'] - base['valor_presente']

        sensibilidad_data.append({
            'Emisor': bono['Emisor'],
            'Rendimiento -1%': formato_moneda(bajo['valor_presente']),
            'Cambio': formato_moneda(cambio_bajo),
            'Base': formato_moneda(base['valor_presente']),
            'Rendimiento +1%': formato_moneda(alto['valor_presente']),
            'Cambio.1': formato_moneda(-cambio_alto),
            'Duración Aprox.': f"{((cambio_alto + cambio_bajo) / 2 / base['valor_presente'] / 0.01):.2f} años"
        })

    df_sensibilidad = pd.DataFrame(sensibilidad_data)
    st.dataframe(df_sensibilidad, use_container_width=True, hide_index=True)

    # Gráfico de sensibilidad
    fig_sens = go.Figure()

    for bono in bonos:
        tasas = [bono['Rendimiento Requerido'] - 2 + i * 0.25 for i in range(17)]
        valores = []

        for tasa in tasas:
            resultado = calcular_valor_bono(
                bono['Valor Nominal'],
                bono['Tasa Cupón'],
                tasa,
                bono['Años'],
                bono['Frecuencia'],
                bono['Tipo Tasa']
            )
            valores.append(resultado['valor_presente'])

        fig_sens.add_trace(go.Scatter(
            x=tasas,
            y=valores,
            mode='lines+markers',
            name=bono['Emisor'],
            line=dict(width=3),
            marker=dict(size=6)
        ))

    fig_sens.update_layout(
        title="Sensibilidad del Valor del Bono al Rendimiento Requerido",
        xaxis_title="Rendimiento Requerido (%)",
        yaxis_title="Valor del Bono (S/)",
        height=500,
        template='plotly_white',
        hovermode='x unified'
    )

    st.plotly_chart(fig_sens, use_container_width=True)

    # PARTE 4: RECOMENDACIÓN DE INVERSIÓN
    st.divider()
    st.subheader("💼 Parte 4: Recomendación de Inversión")

    # Calcular métricas para ranking
    for i, r in enumerate(resultados):
        r['rentabilidad'] = (r['valor_presente'] - r['valor_nominal']) / r['valor_nominal'] * 100

        # Calcular duración aproximada (sensibilidad)
        alto = calcular_valor_bono(
            r['valor_nominal'],
            r['tasa_cupon'],
            r['rendimiento'] + 1.0,
            r['anos'],
            r['frecuencia'],
            'anual' if r['tasa_cupon'] > 2 else 'mensual'
        )
        bajo = calcular_valor_bono(
            r['valor_nominal'],
            r['tasa_cupon'],
            r['rendimiento'] - 1.0,
            r['anos'],
            r['frecuencia'],
            'anual' if r['tasa_cupon'] > 2 else 'mensual'
        )

        cambio_promedio = ((bajo['valor_presente'] - r['valor_presente']) +
                           (r['valor_presente'] - alto['valor_presente'])) / 2
        r['duracion'] = cambio_promedio / r['valor_presente'] / 0.01
        r['volatilidad'] = abs(r['duracion'])

    # Ordenar por valor presente (mayor valor = mejor inversión si están a la par)
    resultados_ordenados = sorted(resultados, key=lambda x: x['valor_presente'], reverse=True)

    # Ranking
    st.markdown("### 🏆 Ranking de Bonos")

    df_ranking = pd.DataFrame([
        {
            'Posición': i + 1,
            'Emisor': r['emisor'],
            'Valor Teórico': formato_moneda(r['valor_presente']),
            'Prima/Descuento': f"{r['rentabilidad']:.2f}%",
            'Duración (años)': f"{r['duracion']:.2f}",
            'Riesgo': 'Alto' if r['volatilidad'] > 7 else 'Medio' if r['volatilidad'] > 4 else 'Bajo'
        }
        for i, r in enumerate(resultados_ordenados)
    ])

    st.dataframe(df_ranking, use_container_width=True, hide_index=True)

    # Asignación sugerida
    st.markdown("### 💰 Asignación Sugerida del Portafolio")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("**Estrategia Conservadora (recomendada para Fondo de Pensiones):**")

        # Asignar pesos según riesgo y valor
        peso_1 = 0.50  # 50% al mejor
        peso_2 = 0.30  # 30% al segundo
        peso_3 = 0.20  # 20% al tercero

        asignaciones = [
            {
                'Bono': resultados_ordenados[0]['emisor'],
                'Peso': f"{peso_1 * 100:.0f}%",
                'Monto': formato_moneda(monto_invertir * peso_1),
                'Unidades': int(monto_invertir * peso_1 / resultados_ordenados[0]['valor_nominal'])
            },
            {
                'Bono': resultados_ordenados[1]['emisor'],
                'Peso': f"{peso_2 * 100:.0f}%",
                'Monto': formato_moneda(monto_invertir * peso_2),
                'Unidades': int(monto_invertir * peso_2 / resultados_ordenados[1]['valor_nominal'])
            },
            {
                'Bono': resultados_ordenados[2]['emisor'],
                'Peso': f"{peso_3 * 100:.0f}%",
                'Monto': formato_moneda(monto_invertir * peso_3),
                'Unidades': int(monto_invertir * peso_3 / resultados_ordenados[2]['valor_nominal'])
            }
        ]

        df_asignacion = pd.DataFrame(asignaciones)
        st.dataframe(df_asignacion, use_container_width=True, hide_index=True)

    with col2:
        # Gráfico de torta
        fig_pie = go.Figure(data=[go.Pie(
            labels=[a['Bono'] for a in asignaciones],
            values=[peso_1, peso_2, peso_3],
            hole=0.3
        )])

        fig_pie.update_layout(
            title="Distribución del Portafolio",
            height=300
        )

        st.plotly_chart(fig_pie, use_container_width=True)

    # Justificación
    st.markdown("### 📋 Justificación de la Recomendación")

    with st.container():
        st.markdown(f"""
        **1. Orden de Preferencia:**

        - **🥇 {resultados_ordenados[0]['emisor']}**: Valor teórico de {formato_moneda(resultados_ordenados[0]['valor_presente'])}, 
          {'con prima' if resultados_ordenados[0]['rentabilidad'] > 0 else 'con descuento'} de {abs(resultados_ordenados[0]['rentabilidad']):.2f}%.
          Duración de {resultados_ordenados[0]['duracion']:.2f} años indica 
          {'alta' if resultados_ordenados[0]['volatilidad'] > 7 else 'moderada' if resultados_ordenados[0]['volatilidad'] > 4 else 'baja'} sensibilidad a tasas.

        - **🥈 {resultados_ordenados[1]['emisor']}**: Valor teórico de {formato_moneda(resultados_ordenados[1]['valor_presente'])},
          {'con prima' if resultados_ordenados[1]['rentabilidad'] > 0 else 'con descuento'} de {abs(resultados_ordenados[1]['rentabilidad']):.2f}%.
          Ofrece balance entre riesgo y retorno.

        - **🥉 {resultados_ordenados[2]['emisor']}**: Valor teórico de {formato_moneda(resultados_ordenados[2]['valor_presente'])},
          menor exposición pero diversifica el portafolio.

        **2. Criterios de Asignación:**

        - **Diversificación**: No concentrar más del 50% en un solo emisor
        - **Perfil de Riesgo**: Priorizamos bonos con menor duración para un fondo de pensiones
        - **Valoración**: Mayor peso a bonos que cotizan con descuento (oportunidad de compra)
        - **Plazo**: Balance entre corto, mediano y largo plazo

        **3. Consideraciones de Riesgo:**

        - Bonos con mayor duración son más sensibles a cambios en tasas de interés
        - La diversificación por emisor y plazo reduce el riesgo del portafolio
        - Se recomienda revisión trimestral de las valoraciones
        """)

    # Exportar reporte
    st.divider()

    # Preparar datos para exportar
    reporte_completo = {
        'Valores Teóricos': df_valores,
        'Sensibilidad': df_sensibilidad,
        'Ranking': df_ranking,
        'Asignación': df_asignacion
    }

    # Excel con múltiples hojas
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for nombre, df in reporte_completo.items():
            df.to_excel(writer, sheet_name=nombre, index=False)

    output.seek(0)

    col_exp1, col_exp2 = st.columns(2)

    with col_exp1:
        st.download_button(
            label="📊 Descargar Reporte Completo (Excel)",
            data=output,
            file_name=f"evaluacion_bonos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with col_exp2:
        # CSV consolidado
        df_consolidado = pd.DataFrame([
            {
                'Emisor': r['emisor'],
                'Valor Nominal': r['valor_nominal'],
                'Valor Teórico': r['valor_presente'],
                'Prima/Descuento %': r['rentabilidad'],
                'Duración': r['duracion'],
                'Tasa Cupón': r['tasa_cupon'],
                'Rendimiento Req.': r['rendimiento'],
                'Plazo (años)': r['anos']
            }
            for r in resultados
        ])

        csv = df_consolidado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Datos (CSV)",
            data=csv,
            file_name=f"datos_bonos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )


# Para importar en otro archivo
import io