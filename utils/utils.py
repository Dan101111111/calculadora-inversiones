import streamlit as st

# Funciones auxiliares
def convertir_tea_a_periodica(tea, frecuencia):
    """Convierte TEA a tasa periódica"""
    periodos = {
        'Mensual': 12, 'Bimestral': 6, 'Trimestral': 4,
        'Cuatrimestral': 3, 'Semestral': 2, 'Anual': 1
    }
    n = periodos.get(frecuencia, 12)
    return (1 + tea / 100) ** (1 / n) - 1

def formato_moneda(valor):
    """Formatea valores en dólares"""
    return f"${valor:,.2f}"

def mostrar_ayuda(texto):
    """Muestra texto de ayuda"""
    return st.markdown(f'<p class="help-text">💡 {texto}</p>', unsafe_allow_html=True)