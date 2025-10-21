import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
import re
from collections import Counter

# --- Configuración de página ---
st.set_page_config(
    page_title="Generador de CV Inteligente",
    page_icon="🤖",
    layout="wide"
)

# --- Funciones auxiliares ---
def normalizar_texto(texto):
    """Normaliza texto para mejor comparación"""
    texto = texto.lower()
    # Reemplazar separadores comunes
    texto = re.sub(r'[,;/\-]', ' ', texto)
    # Eliminar caracteres especiales pero mantener espacios
    texto = re.sub(r'[^\w\s]', '', texto)
    return texto

def extraer_tokens(texto):
    """Extrae tokens individuales y bigramas del texto"""
    texto_norm = normalizar_texto(texto)
    palabras = texto_norm.split()
    
    # Tokens individuales
    tokens = set(palabras)
    
    # Bigramas (frases de dos palabras)
    bigramas = set()
    for i in range(len(palabras) - 1):
        bigrama = f"{palabras[i]} {palabras[i+1]}"
        bigramas.add(bigrama)
    
    return tokens, bigramas

def calcular_similitud_avanzada(cv_texto, palabras_clave_str, nivel_importancia):
    """Calcula similitud considerando palabras clave y frases"""
    # Extraer palabras clave del puesto
    palabras_clave = [p.strip() for p in palabras_clave_str.split(",")]
    
    # Obtener tokens del CV
    cv_tokens, cv_bigramas = extraer_tokens(cv_texto)
    
    coincidencias = []
    faltantes = []
    puntaje_total = 0
    puntaje_max = 0
    
    for palabra in palabras_clave:
        palabra_norm = normalizar_texto(palabra)
        peso = 2 if nivel_importancia == "Alto" else 1.5 if nivel_importancia == "Medio" else 1
        puntaje_max += peso
        
        # Verificar coincidencia exacta o parcial
        encontrado = False
        if ' ' in palabra_norm:  # Es una frase
            if palabra_norm in ' '.join(cv_tokens) or palabra_norm in cv_bigramas:
                encontrado = True
        else:  # Es una palabra simple
            if palabra_norm in cv_tokens:
                encontrado = True
        
        if encontrado:
            coincidencias.append(palabra)
            puntaje_total += peso
        else:
            faltantes.append(palabra)
    
    similitud = puntaje_total / puntaje_max if puntaje_max > 0 else 0
    return similitud, coincidencias, faltantes

def generar_pdf_profesional(nombre, puesto, similitud, coincidencias, faltantes, recomendaciones):
    """Genera un PDF con diseño profesional"""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Colores
    color_primario = HexColor("#2C3E50")
    color_secundario = HexColor("#3498DB")
    color_exito = HexColor("#27AE60")
    color_alerta = HexColor("#E74C3C")
    
    # Encabezado con fondo
    c.setFillColor(color_primario)
    c.rect(0, height - 100, width, 100, fill=True, stroke=False)
    
    c.setFillColor(HexColor("#FFFFFF"))
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, height - 50, "Análisis de CV")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 75, f"Candidato: {nombre}")
    
    # Línea divisoria
    c.setStrokeColor(color_secundario)
    c.setLineWidth(2)
    c.line(50, height - 110, width - 50, height - 110)
    
    # Contenido principal
    y = height - 150
    c.setFillColor(color_primario)
    
    # Puesto objetivo
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, f"Puesto Objetivo: {puesto}")
    y -= 30
    
    # Métrica de similitud
    c.setFont("Helvetica-Bold", 16)
    color_metrica = color_exito if similitud >= 0.7 else color_alerta if similitud < 0.5 else HexColor("#F39C12")
    c.setFillColor(color_metrica)
    c.drawString(50, y, f"Compatibilidad: {similitud*100:.1f}%")
    
    # Barra de progreso
    c.setFillColor(HexColor("#ECF0F1"))
    c.rect(50, y - 25, 300, 15, fill=True, stroke=False)
    c.setFillColor(color_metrica)
    c.rect(50, y - 25, 300 * similitud, 15, fill=True, stroke=False)
    
    y -= 60
    c.setFillColor(color_primario)
    
    # Palabras en común
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(color_exito)
    c.drawString(50, y, f"✓ Fortalezas identificadas ({len(coincidencias)}):")
    y -= 20
    c.setFont("Helvetica", 10)
    c.setFillColor(color_primario)
    
    if coincidencias:
        for i, palabra in enumerate(coincidencias[:15]):  # Máximo 15
            c.drawString(70, y, f"• {palabra}")
            y -= 15
            if y < 150:  # Nueva página si es necesario
                c.showPage()
                y = height - 50
    else:
        c.drawString(70, y, "No se encontraron coincidencias")
        y -= 15
    
    y -= 20
    
    # Palabras faltantes
    if y < 200:
        c.showPage()
        y = height - 50
    
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(color_alerta)
    c.drawString(50, y, f"⚠ Áreas de mejora ({len(faltantes)}):")
    y -= 20
    c.setFont("Helvetica", 10)
    c.setFillColor(color_primario)
    
    if faltantes:
        for palabra in faltantes[:15]:
            c.drawString(70, y, f"• {palabra}")
            y -= 15
            if y < 150:
                c.showPage()
                y = height - 50
    else:
        c.drawString(70, y, "¡Excelente! Tu CV cubre todas las palabras clave")
        y -= 15
    
    y -= 20
    
    # Recomendaciones
    if recomendaciones and y > 200:
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(color_secundario)
        c.drawString(50, y, "💡 Recomendaciones:")
        y -= 20
        c.setFont("Helvetica", 9)
        c.setFillColor(color_primario)
        c.drawString(70, y, recomendaciones)
    
    # Pie de página
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColor(HexColor("#95A5A6"))
    c.drawString(50, 30, f"Generado por CV Inteligente - {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}")
    
    c.save()
    buffer.seek(0)
    return buffer

# --- Interfaz principal ---
st.title("🤖 Generador de CV Inteligente")
st.markdown("### Optimizá tu CV para puestos en Data Science e Inteligencia Artificial")

# Sidebar con información
with st.sidebar:
    st.header("📊 Acerca de esta herramienta")
    st.markdown("""
    Esta aplicación analiza tu CV y lo compara con los requisitos de diferentes puestos en el ámbito de Data Science e IA.
    
    **¿Cómo funciona?**
    1. Seleccioná el puesto al que aplicás
    2. Pegá el texto de tu CV
    3. Obtené un análisis detallado
    4. Descargá un reporte en PDF
    
    **Niveles de compatibilidad:**
    - 🟢 **70-100%**: Excelente match
    - 🟡 **50-69%**: Buen candidato
    - 🔴 **0-49%**: Necesitás mejorar tu CV
    """)

# Cargar datos
try:
    puestos_df = pd.read_csv("puestos.csv")
except FileNotFoundError:
    st.error("❌ No se encontró el archivo 'puestos.csv'. Asegurate de que esté en el mismo directorio.")
    st.stop()

# Layout en columnas
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🎯 Información del puesto")
    puesto_seleccionado = st.selectbox(
        "Seleccioná el puesto deseado:",
        puestos_df["puesto"].unique(),
        help="Elegí el puesto al que querés aplicar"
    )
    
    # Mostrar información del puesto
    fila_puesto = puestos_df[puestos_df["puesto"] == puesto_seleccionado].iloc[0]
    st.info(f"**Nivel:** {fila_puesto['nivel']}")
    
    with st.expander("Ver palabras clave del puesto"):
        palabras = [p.strip() for p in fila_puesto["palabras_clave"].split(",")]
        st.write(", ".join(palabras))

with col2:
    st.subheader("👤 Tus datos")
    nombre = st.text_input("Tu nombre completo:", placeholder="Ej: Juan Pérez")
    email = st.text_input("Email (opcional):", placeholder="tu@email.com")

st.subheader("📄 Tu CV")
cv_texto = st.text_area(
    "Pegá el texto de tu CV o descripción profesional:",
    height=200,
    placeholder="Incluí tu experiencia, habilidades técnicas, educación y proyectos relevantes..."
)

# Análisis
if st.button("🔍 Analizar compatibilidad", type="primary"):
    if nombre and cv_texto:
        with st.spinner("Analizando tu CV..."):
            fila = puestos_df[puestos_df["puesto"] == puesto_seleccionado].iloc[0]
            similitud, coincidencias, faltantes = calcular_similitud_avanzada(
                cv_texto, 
                fila["palabras_clave"],
                fila["nivel"]
            )
            
            # Generar recomendaciones
            if similitud >= 0.7:
                recomendaciones = "Tu CV está muy bien alineado con este puesto. Considerá destacar aún más tus logros cuantificables."
            elif similitud >= 0.5:
                recomendaciones = "Tenés una base sólida. Agregá las palabras clave faltantes en contextos relevantes de tu experiencia."
            else:
                recomendaciones = "Necesitás fortalecer tu CV. Agregá proyectos o cursos que demuestren las habilidades faltantes."
            
            # Mostrar resultados
            st.divider()
            st.subheader("📊 Resultados del análisis")
            
            # Métrica principal
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.metric("Compatibilidad", f"{similitud*100:.1f}%")
            with col_m2:
                st.metric("Fortalezas", len(coincidencias))
            with col_m3:
                st.metric("Áreas de mejora", len(faltantes))
            
            # Barra de progreso visual
            st.progress(similitud)
            
            # Detalles en columnas
            col_det1, col_det2 = st.columns(2)
            
            with col_det1:
                st.markdown("### 🟢 Palabras clave encontradas")
                if coincidencias:
                    for palabra in coincidencias:
                        st.markdown(f"✓ {palabra}")
                else:
                    st.write("No se encontraron coincidencias aún.")
            
            with col_det2:
                st.markdown("### 🔴 Palabras clave sugeridas")
                if faltantes:
                    for palabra in faltantes:
                        st.markdown(f"• {palabra}")
                else:
                    st.success("¡Ya tenés todas las palabras clave! 🎉")
            
            # Recomendaciones
            st.info(f"💡 **Recomendación:** {recomendaciones}")
            
            # Generar PDF
            pdf = generar_pdf_profesional(
                nombre, 
                puesto_seleccionado, 
                similitud, 
                coincidencias, 
                faltantes,
                recomendaciones
            )
            
            st.download_button(
                label="📥 Descargar análisis completo (PDF)",
                data=pdf,
                file_name=f"Analisis_CV_{nombre.replace(' ', '_')}.pdf",
                mime="application/pdf",
                type="secondary"
            )
    else:
        st.warning("⚠️ Por favor, completá tu nombre y el texto del CV.")

# Footer
st.divider()
st.caption("💼 Herramienta desarrollada para ayudarte a optimizar tu CV en el área de Data Science e IA")
