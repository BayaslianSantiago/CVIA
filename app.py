import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import requests

# --- Configuración ---
st.set_page_config(page_title="Generador de CVs", page_icon="📄", layout="centered")

# URL del CSV en GitHub (ejemplo - reemplazar con tu URL)
CSV_URL = "https://raw.githubusercontent.com/tu-usuario/tu-repo/main/puestos.csv"

# Estilos por categoría
ESTILOS = {
    "Tecnología": {
        "color_primario": "#2C3E50",
        "color_secundario": "#3498DB",
        "layout": "moderno"
    },
    "Marketing": {
        "color_primario": "#E91E63",
        "color_secundario": "#FF6F00",
        "layout": "creativo"
    },
    "Finanzas": {
        "color_primario": "#1A237E",
        "color_secundario": "#5C6BC0",
        "layout": "formal"
    },
    "Salud": {
        "color_primario": "#1976D2",
        "color_secundario": "#4FC3F7",
        "layout": "profesional"
    },
    "Educación": {
        "color_primario": "#FF9800",
        "color_secundario": "#FFC107",
        "layout": "amigable"
    },
    "Ventas": {
        "color_primario": "#D32F2F",
        "color_secundario": "#FF5252",
        "layout": "dinámico"
    },
    "General": {
        "color_primario": "#424242",
        "color_secundario": "#757575",
        "layout": "clásico"
    }
}

# --- Funciones ---
@st.cache_data(ttl=3600)
def cargar_puestos():
    """Carga puestos desde CSV en GitHub o usa datos de ejemplo"""
    try:
        df = pd.read_csv(CSV_URL)
        return df
    except:
        # Datos de ejemplo si falla la carga
        data = {
            "puesto": ["Data Scientist", "Marketing Manager", "Contador", "Enfermero/a", "Profesor/a"],
            "categoria": ["Tecnología", "Marketing", "Finanzas", "Salud", "Educación"],
            "palabras_clave": [
                "Python,Machine Learning,SQL,Análisis de datos",
                "SEO,Google Ads,Redes sociales,Analytics",
                "Contabilidad,Impuestos,Auditoría,NIIF",
                "Atención al paciente,RCP,Administración de medicamentos",
                "Planificación didáctica,Evaluación,Pedagogía"
            ],
            "verbos_accion": [
                "Desarrollé,Implementé,Optimicé,Analicé",
                "Lancé,Aumenté,Gestioné,Posicioné",
                "Preparé,Audité,Concilié,Analicé",
                "Atendí,Administré,Monitoricé,Asistí",
                "Planifiqué,Enseñé,Evalué,Desarrollé"
            ],
            "habilidades_sugeridas": [
                "Python,SQL,Machine Learning,Pandas,Tableau",
                "Google Ads,SEO,Facebook Ads,Analytics,Copywriting",
                "Excel,SAP,Tango,Contabilidad,Impuestos",
                "RCP,Primeros auxilios,Administración de medicamentos",
                "Pedagogía,Manejo de aula,Herramientas digitales"
            ]
        }
        return pd.DataFrame(data)

def generar_pdf(cv_data, estilo):
    """Genera PDF con diseño según categoría"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                           topMargin=0.5*inch, bottomMargin=0.5*inch,
                           leftMargin=0.75*inch, rightMargin=0.75*inch)
    story = []
    styles = getSampleStyleSheet()
    
    # Colores según categoría
    color_1 = HexColor(estilo["color_primario"])
    color_2 = HexColor(estilo["color_secundario"])
    
    # Estilos personalizados
    style_nombre = ParagraphStyle(
        'Nombre',
        parent=styles['Heading1'],
        fontSize=26,
        textColor=color_1,
        spaceAfter=4,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    style_contacto = ParagraphStyle(
        'Contacto',
        parent=styles['Normal'],
        fontSize=10,
        textColor=HexColor("#666666"),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    style_seccion = ParagraphStyle(
        'Seccion',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=color_2,
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold',
        borderWidth=1,
        borderColor=color_2,
        borderPadding=3
    )
    
    # Header - Nombre y contacto
    story.append(Paragraph(cv_data["nombre"], style_nombre))
    
    contacto_parts = []
    if cv_data.get("email"):
        contacto_parts.append(cv_data["email"])
    if cv_data.get("telefono"):
        contacto_parts.append(cv_data["telefono"])
    if cv_data.get("ubicacion"):
        contacto_parts.append(cv_data["ubicacion"])
    if cv_data.get("linkedin"):
        contacto_parts.append(cv_data["linkedin"])
    
    contacto = " | ".join(contacto_parts)
    story.append(Paragraph(contacto, style_contacto))
    
    # Puesto objetivo
    if cv_data.get("puesto_objetivo"):
        story.append(Paragraph(f"<b>Objetivo:</b> {cv_data['puesto_objetivo']}", styles['Normal']))
        story.append(Spacer(1, 15))
    
    # Resumen
    if cv_data.get("resumen"):
        story.append(Paragraph("RESUMEN PROFESIONAL", style_seccion))
        story.append(Paragraph(cv_data["resumen"], styles['Normal']))
    
    # Experiencia
    if cv_data.get("experiencias") and len(cv_data["experiencias"]) > 0:
        story.append(Paragraph("EXPERIENCIA PROFESIONAL", style_seccion))
        for exp in cv_data["experiencias"]:
            if exp.get("puesto") or exp.get("empresa"):
                titulo = f"<b>{exp.get('puesto', '')}</b>"
                if exp.get("empresa"):
                    titulo += f" - {exp['empresa']}"
                story.append(Paragraph(titulo, styles['Normal']))
                
                if exp.get("periodo"):
                    story.append(Paragraph(f"<i>{exp['periodo']}</i>", styles['Normal']))
                
                if exp.get("descripcion"):
                    story.append(Paragraph(exp['descripcion'], styles['Normal']))
                
                story.append(Spacer(1, 10))
    
    # Educación
    if cv_data.get("educacion") and len(cv_data["educacion"]) > 0:
        story.append(Paragraph("EDUCACIÓN", style_seccion))
        for edu in cv_data["educacion"]:
            if edu.get("titulo") or edu.get("institucion"):
                titulo = f"<b>{edu.get('titulo', '')}</b>"
                if edu.get("institucion"):
                    titulo += f" - {edu['institucion']}"
                story.append(Paragraph(titulo, styles['Normal']))
                
                if edu.get("periodo"):
                    story.append(Paragraph(f"<i>{edu['periodo']}</i>", styles['Normal']))
                
                story.append(Spacer(1, 10))
    
    # Habilidades
    if cv_data.get("habilidades") and len(cv_data["habilidades"]) > 0:
        story.append(Paragraph("HABILIDADES", style_seccion))
        habilidades_texto = " • ".join(cv_data["habilidades"])
        story.append(Paragraph(habilidades_texto, styles['Normal']))
    
    # Certificaciones
    if cv_data.get("certificaciones"):
        story.append(Paragraph("CERTIFICACIONES", style_seccion))
        story.append(Paragraph(cv_data["certificaciones"], styles['Normal']))
    
    # Idiomas
    if cv_data.get("idiomas"):
        story.append(Paragraph("IDIOMAS", style_seccion))
        story.append(Paragraph(cv_data["idiomas"], styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# --- Interfaz ---
st.title("📄 Generador de CVs")
st.markdown("Completá el formulario y descargá tu CV profesional en PDF")

# Cargar datos
df_puestos = cargar_puestos()

# Inicializar estado
if "cv_data" not in st.session_state:
    st.session_state.cv_data = {
        "nombre": "",
        "email": "",
        "telefono": "",
        "ubicacion": "",
        "linkedin": "",
        "puesto_objetivo": "",
        "resumen": "",
        "experiencias": [],
        "educacion": [],
        "habilidades": [],
        "certificaciones": "",
        "idiomas": ""
    }

# --- PASO 1: Selección de puesto ---
st.subheader("1️⃣ Tu puesto")

col1, col2 = st.columns(2)

with col1:
    categorias = ["Todas"] + sorted(df_puestos["categoria"].unique().tolist())
    categoria_sel = st.selectbox("Categoría", categorias)

with col2:
    if categoria_sel == "Todas":
        puestos_filtrados = df_puestos["puesto"].tolist()
    else:
        puestos_filtrados = df_puestos[df_puestos["categoria"] == categoria_sel]["puesto"].tolist()
    
    puesto_sel = st.selectbox("Puesto", puestos_filtrados)

# Obtener datos del puesto
if puesto_sel:
    puesto_data = df_puestos[df_puestos["puesto"] == puesto_sel].iloc[0]
    st.session_state.cv_data["puesto_objetivo"] = puesto_sel
    categoria_final = puesto_data["categoria"]
else:
    categoria_final = "General"

st.divider()

# --- PASO 2: Datos personales ---
st.subheader("2️⃣ Datos personales")

col1, col2 = st.columns(2)
with col1:
    st.session_state.cv_data["nombre"] = st.text_input("Nombre completo *", st.session_state.cv_data["nombre"])
    st.session_state.cv_data["email"] = st.text_input("Email *", st.session_state.cv_data["email"])
    st.session_state.cv_data["ubicacion"] = st.text_input("Ubicación", st.session_state.cv_data["ubicacion"], placeholder="Buenos Aires, Argentina")

with col2:
    st.session_state.cv_data["telefono"] = st.text_input("Teléfono", st.session_state.cv_data["telefono"], placeholder="+54 11 1234-5678")
    st.session_state.cv_data["linkedin"] = st.text_input("LinkedIn", st.session_state.cv_data["linkedin"], placeholder="linkedin.com/in/tu-perfil")

st.divider()

# --- PASO 3: Resumen ---
st.subheader("3️⃣ Resumen profesional")

if puesto_sel and "palabras_clave" in puesto_data:
    st.caption(f"💡 Palabras clave sugeridas: {puesto_data['palabras_clave']}")

st.session_state.cv_data["resumen"] = st.text_area(
    "Resumen (3-4 líneas) *",
    st.session_state.cv_data["resumen"],
    height=100,
    placeholder="Profesional con X años de experiencia en..."
)

st.divider()

# --- PASO 4: Experiencia ---
st.subheader("4️⃣ Experiencia laboral")

if puesto_sel and "verbos_accion" in puesto_data:
    st.caption(f"💡 Verbos de acción: {puesto_data['verbos_accion']}")

num_exp = st.number_input("Cantidad de experiencias", 0, 5, len(st.session_state.cv_data["experiencias"]))

experiencias_temp = []
for i in range(num_exp):
    with st.expander(f"Experiencia {i+1}", expanded=(i==0)):
        exp = st.session_state.cv_data["experiencias"][i] if i < len(st.session_state.cv_data["experiencias"]) else {}
        
        col1, col2 = st.columns(2)
        with col1:
            puesto = st.text_input("Puesto", exp.get("puesto", ""), key=f"exp_p_{i}")
            empresa = st.text_input("Empresa", exp.get("empresa", ""), key=f"exp_e_{i}")
        with col2:
            periodo = st.text_input("Período", exp.get("periodo", ""), placeholder="2020 - 2023", key=f"exp_per_{i}")
        
        desc = st.text_area("Descripción", exp.get("descripcion", ""), height=80, key=f"exp_d_{i}",
                           placeholder="• Logro 1\n• Logro 2")
        
        experiencias_temp.append({"puesto": puesto, "empresa": empresa, "periodo": periodo, "descripcion": desc})

st.session_state.cv_data["experiencias"] = experiencias_temp

st.divider()

# --- PASO 5: Educación ---
st.subheader("5️⃣ Educación")

num_edu = st.number_input("Cantidad de títulos", 0, 5, len(st.session_state.cv_data["educacion"]))

educacion_temp = []
for i in range(num_edu):
    with st.expander(f"Título {i+1}", expanded=(i==0)):
        edu = st.session_state.cv_data["educacion"][i] if i < len(st.session_state.cv_data["educacion"]) else {}
        
        col1, col2 = st.columns(2)
        with col1:
            titulo = st.text_input("Título", edu.get("titulo", ""), key=f"edu_t_{i}")
            institucion = st.text_input("Institución", edu.get("institucion", ""), key=f"edu_i_{i}")
        with col2:
            periodo = st.text_input("Período", edu.get("periodo", ""), placeholder="2015 - 2019", key=f"edu_p_{i}")
        
        educacion_temp.append({"titulo": titulo, "institucion": institucion, "periodo": periodo})

st.session_state.cv_data["educacion"] = educacion_temp

st.divider()

# --- PASO 6: Habilidades ---
st.subheader("6️⃣ Habilidades")

if puesto_sel and "habilidades_sugeridas" in puesto_data:
    habilidades_sugeridas = [h.strip() for h in puesto_data["habilidades_sugeridas"].split(",")]
    st.caption(f"💡 Sugerencias: {', '.join(habilidades_sugeridas)}")
    
    hab_sel = st.multiselect(
        "Seleccioná de las sugeridas",
        habilidades_sugeridas,
        default=[h for h in st.session_state.cv_data.get("habilidades", []) if h in habilidades_sugeridas]
    )
else:
    hab_sel = []

hab_custom = st.text_input(
    "Agregá otras (separadas por coma)",
    ", ".join([h for h in st.session_state.cv_data.get("habilidades", []) if h not in hab_sel])
)

habilidades_final = list(hab_sel)
if hab_custom:
    habilidades_final.extend([h.strip() for h in hab_custom.split(",")])

st.session_state.cv_data["habilidades"] = habilidades_final

st.divider()

# --- PASO 7: Extras (opcional) ---
with st.expander("➕ Información adicional (opcional)"):
    st.session_state.cv_data["certificaciones"] = st.text_area(
        "Certificaciones",
        st.session_state.cv_data.get("certificaciones", ""),
        placeholder="• Certificación 1\n• Certificación 2"
    )
    
    st.session_state.cv_data["idiomas"] = st.text_area(
        "Idiomas",
        st.session_state.cv_data.get("idiomas", ""),
        placeholder="• Español: Nativo\n• Inglés: Avanzado"
    )

st.divider()

# --- Generar PDF ---
st.subheader("7️⃣ Generar CV")

if st.button("📥 Descargar CV en PDF", type="primary", use_container_width=True):
    if not st.session_state.cv_data["nombre"]:
        st.error("⚠️ Por favor completá tu nombre")
    elif not st.session_state.cv_data["resumen"]:
        st.error("⚠️ Por favor completá el resumen profesional")
    else:
        with st.spinner("Generando tu CV..."):
            estilo = ESTILOS.get(categoria_final, ESTILOS["General"])
            pdf = generar_pdf(st.session_state.cv_data, estilo)
            
            st.success("✅ ¡CV generado exitosamente!")
            
            st.download_button(
                label="💾 Descargar PDF",
                data=pdf,
                file_name=f"CV_{st.session_state.cv_data['nombre'].replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

# Footer
st.divider()
st.caption("💼 Generador simple de CVs profesionales")
