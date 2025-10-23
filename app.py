import streamlit as st
import pandas as pd
from fpdf import FPDF

# --- Cargar dataset desde GitHub ---
DATA_URL = "https://raw.githubusercontent.com/tu_usuario/tu_repo/main/data/puestos.csv"

@st.cache_data
def cargar_puestos():
    return pd.read_csv(DATA_URL)

puestos = cargar_puestos()

# --- Interfaz Streamlit ---
st.title("Generador de Currículum Inteligente")

puesto = st.selectbox("Seleccioná un puesto", puestos["puesto"])

nombre = st.text_input("Nombre completo")
email = st.text_input("Email")
experiencia = st.text_area("Resumen de tu experiencia")

if st.button("Generar CV"):
    datos_puesto = puestos[puestos["puesto"] == puesto].iloc[0]
    palabras = datos_puesto["palabras_clave"]

    # --- Crear PDF ---
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f"Nombre: {nombre}\nEmail: {email}\n\nPuesto: {puesto}")
    pdf.multi_cell(0, 10, f"\nExperiencia:\n{experiencia}")
    pdf.multi_cell(0, 10, f"\nPalabras clave del puesto:\n{palabras}")

    # --- Guardar y descargar ---
    pdf.output("cv_generado.pdf")
    with open("cv_generado.pdf", "rb") as f:
        st.download_button("Descargar CV", f, file_name="cv.pdf", mime="application/pdf")

