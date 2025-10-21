import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# --- Función para calcular similitud simple ---
def similitud_simple(cv_texto, palabras_puesto):
    cv_palabras = set(cv_texto.lower().replace(",", "").split())
    palabras_puesto = set(p.strip().lower() for p in palabras_puesto.split(","))
    interseccion = cv_palabras & palabras_puesto
    similitud = len(interseccion) / len(palabras_puesto)
    return similitud, interseccion

# --- Generar PDF ---
def generar_pdf(nombre, puesto, similitud, palabras_faltantes):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(100, 750, f"CV Optimizado - {nombre}")
    c.setFont("Helvetica", 12)
    c.drawString(100, 720, f"Puesto: {puesto}")
    c.drawString(100, 700, f"Similitud con el puesto: {similitud*100:.1f}%")
    c.drawString(100, 670, "Palabras clave que podrías agregar:")
    y = 650
    for palabra in palabras_faltantes:
        c.drawString(120, y, f"- {palabra}")
        y -= 20
    c.save()
    buffer.seek(0)
    return buffer

# --- Interfaz Streamlit ---
st.set_page_config(page_title="Generador de CV Inteligente", layout="centered")

st.title("🤖 Generador de CV Inteligente")
st.write("Compara tu perfil con puestos del mundo de la Ciencia de Datos e IA.")

# Cargar CSV
puestos_df = pd.read_csv("puestos.csv")

# Seleccionar puesto
puesto_seleccionado = st.selectbox("Seleccioná el puesto deseado:", puestos_df["puesto"])

# Ingreso de datos del usuario
nombre = st.text_input("Tu nombre completo:")
cv_texto = st.text_area("Pegá tu descripción o texto de tu CV:")

if st.button("Analizar similitud"):
    if nombre and cv_texto:
        fila = puestos_df[puestos_df["puesto"] == puesto_seleccionado].iloc[0]
        similitud, coincidencias = similitud_simple(cv_texto, fila["palabras_clave"])
        palabras_puesto = set(p.strip().lower() for p in fila["palabras_clave"].split(","))
        faltantes = palabras_puesto - coincidencias

        st.metric("Similitud con el puesto", f"{similitud*100:.1f}%")
        st.subheader("🟢 Palabras en común")
        st.write(", ".join(coincidencias) if coincidencias else "Ninguna coincidencia aún.")
        st.subheader("🔴 Palabras sugeridas para agregar")
        st.write(", ".join(faltantes) if faltantes else "Ya tenés todas las palabras clave 😎")

        # Generar PDF
        pdf = generar_pdf(nombre, puesto_seleccionado, similitud, faltantes)
        st.download_button(
            label="📄 Descargar CV Optimizado (PDF)",
            data=pdf,
            file_name=f"CV_{nombre.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
    else:
        st.warning("Por favor, completá tu nombre y texto del CV.")
