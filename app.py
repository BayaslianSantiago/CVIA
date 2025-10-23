import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import re

# --- Configuración de página ---
st.set_page_config(
    page_title="Generador Inteligente de CVs",
    page_icon="📝",
    layout="wide"
)

# --- Base de datos de puestos (puedes cargar desde CSV) ---
PUESTOS_DATA = {
    # --- SECTOR DATOS / IA / TECNOLOGÍA ---
    "Data Scientist": {
        "palabras_clave": ["Python", "Machine Learning", "SQL", "Estadística", "Pandas", "Scikit-learn", "TensorFlow", "Visualización de datos", "A/B Testing"],
        "habilidades_tecnicas": ["Python", "R", "SQL", "Machine Learning", "Deep Learning", "Estadística", "Big Data"],
        "herramientas": ["Jupyter", "Git", "Docker", "AWS", "Azure", "Tableau", "Power BI"],
        "nivel": "Senior"
    },
    "Data Analyst": {
        "palabras_clave": ["SQL", "Excel", "Power BI", "Tableau", "Análisis de datos", "Dashboard", "KPI", "Reporting"],
        "habilidades_tecnicas": ["SQL", "Excel avanzado", "Power BI", "Tableau", "Python básico", "Estadística descriptiva"],
        "herramientas": ["Excel", "Power BI", "Tableau", "SQL Server", "Google Analytics"],
        "nivel": "Junior"
    },
    "ML Engineer": {
        "palabras_clave": ["Python", "TensorFlow", "PyTorch", "MLOps", "Docker", "Kubernetes", "CI/CD", "Cloud", "Deployment"],
        "habilidades_tecnicas": ["Python", "Machine Learning", "Deep Learning", "MLOps", "DevOps", "Cloud Computing"],
        "herramientas": ["TensorFlow", "PyTorch", "Docker", "Kubernetes", "AWS", "MLflow", "Git"],
        "nivel": "Senior"
    },
    "AI Research Scientist": {
        "palabras_clave": ["PhD", "Research", "Publicaciones", "Deep Learning", "NLP", "Computer Vision", "PyTorch", "Paper"],
        "habilidades_tecnicas": ["Deep Learning", "NLP", "Computer Vision", "Reinforcement Learning", "Matemáticas avanzadas"],
        "herramientas": ["PyTorch", "TensorFlow", "JAX", "Weights & Biases", "Papers with Code"],
        "nivel": "Alto"
    },

    # --- DESARROLLO Y TECNOLOGÍA ---
    "Software Engineer": {
        "palabras_clave": ["Java", "Python", "C++", "Git", "APIs", "Microservicios", "Testing", "Backend", "Frontend"],
        "habilidades_tecnicas": ["Programación", "Diseño de sistemas", "Estructuras de datos", "Algoritmos", "Bases de datos"],
        "herramientas": ["Git", "Docker", "VS Code", "Postman", "AWS", "Jenkins"],
        "nivel": "Intermedio"
    },
    "Frontend Developer": {
        "palabras_clave": ["HTML", "CSS", "JavaScript", "React", "Vue", "Angular", "UX/UI", "Responsive Design"],
        "habilidades_tecnicas": ["HTML5", "CSS3", "JavaScript", "React", "UX/UI", "Testing de interfaces"],
        "herramientas": ["Figma", "VS Code", "Git", "React", "Next.js"],
        "nivel": "Intermedio"
    },
    "Backend Developer": {
        "palabras_clave": ["Node.js", "Python", "Java", "SQL", "APIs REST", "Microservicios", "Seguridad", "Escalabilidad"],
        "habilidades_tecnicas": ["Desarrollo backend", "Bases de datos", "API design", "Testing", "Optimización de rendimiento"],
        "herramientas": ["PostgreSQL", "MongoDB", "Docker", "Express", "FastAPI", "Git"],
        "nivel": "Intermedio"
    },
    "DevOps Engineer": {
        "palabras_clave": ["CI/CD", "Docker", "Kubernetes", "AWS", "Azure", "Infraestructura", "Pipelines"],
        "habilidades_tecnicas": ["Automatización", "Cloud", "Despliegue continuo", "Infraestructura como código"],
        "herramientas": ["Jenkins", "GitLab CI", "Terraform", "Docker", "Kubernetes", "Ansible"],
        "nivel": "Senior"
    },

    # --- RECURSOS HUMANOS ---
    "HR Analyst": {
        "palabras_clave": ["Recursos Humanos", "Selección", "Capacitación", "Evaluaciones", "Indicadores", "Clima laboral"],
        "habilidades_tecnicas": ["Reclutamiento", "Entrevistas", "Gestión de desempeño", "Análisis de personal"],
        "herramientas": ["SAP HR", "Excel", "LinkedIn Recruiter", "BambooHR"],
        "nivel": "Intermedio"
    },
    "Talent Acquisition Specialist": {
        "palabras_clave": ["Reclutamiento", "Selección", "Onboarding", "Head Hunting", "Entrevistas", "LinkedIn"],
        "habilidades_tecnicas": ["Sourcing", "Entrevistas por competencias", "Gestión de candidatos", "Employer branding"],
        "herramientas": ["LinkedIn Recruiter", "Workday", "BambooHR", "Excel"],
        "nivel": "Intermedio"
    },

    # --- ADMINISTRACIÓN Y FINANZAS ---
    "Administrative Assistant": {
        "palabras_clave": ["Atención al cliente", "Facturación", "Gestión de documentos", "Agenda", "Proveedores"],
        "habilidades_tecnicas": ["Organización", "Comunicación", "Gestión administrativa", "Soporte a equipos"],
        "herramientas": ["Excel", "Word", "Google Workspace", "ERP"],
        "nivel": "Junior"
    },
    "Accountant": {
        "palabras_clave": ["Contabilidad", "Balances", "Impuestos", "Liquidación", "Conciliaciones bancarias"],
        "habilidades_tecnicas": ["Análisis contable", "Normas fiscales", "Gestión de impuestos", "Control financiero"],
        "herramientas": ["Tango", "SAP", "Excel", "AFIP"],
        "nivel": "Senior"
    },
    "Financial Analyst": {
        "palabras_clave": ["Finanzas", "Presupuesto", "Forecast", "Análisis financiero", "Inversiones"],
        "habilidades_tecnicas": ["Modelos financieros", "Control de gestión", "Excel avanzado", "Análisis de rentabilidad"],
        "herramientas": ["Excel", "Power BI", "SAP", "QuickBooks"],
        "nivel": "Intermedio"
    },

    # --- LOGÍSTICA Y OPERACIONES ---
    "Logistics Coordinator": {
        "palabras_clave": ["Logística", "Inventario", "Distribución", "Transporte", "Depósito"],
        "habilidades_tecnicas": ["Gestión de stock", "Optimización de rutas", "Planificación logística", "Coordinación"],
        "herramientas": ["SAP", "Excel", "Google Maps", "ERP"],
        "nivel": "Intermedio"
    },
    "Supply Chain Analyst": {
        "palabras_clave": ["Cadena de suministro", "Demanda", "Planificación", "Proveedores", "Optimización"],
        "habilidades_tecnicas": ["Análisis de datos logísticos", "Gestión de proveedores", "Forecasting", "Compras"],
        "herramientas": ["Excel", "Power BI", "SAP SCM", "ERP"],
        "nivel": "Intermedio"
    },

    # --- VENTAS Y MARKETING ---
    "Sales Executive": {
        "palabras_clave": ["Ventas", "Prospección", "Negociación", "CRM", "Cierre de ventas"],
        "habilidades_tecnicas": ["Comunicación", "Gestión de clientes", "Análisis de mercado", "Negociación"],
        "herramientas": ["Salesforce", "HubSpot", "Excel", "CRM"],
        "nivel": "Intermedio"
    },
    "Digital Marketing Specialist": {
        "palabras_clave": ["SEO", "SEM", "Google Ads", "Social Media", "Estrategia", "Contenido", "Email Marketing"],
        "habilidades_tecnicas": ["Analítica web", "Publicidad online", "Gestión de campañas", "Copywriting"],
        "herramientas": ["Google Analytics", "Google Ads", "Meta Business Suite", "Canva", "HubSpot"],
        "nivel": "Intermedio"
    },

    # --- ATENCIÓN AL CLIENTE ---
    "Customer Service Representative": {
        "palabras_clave": ["Atención al cliente", "Resolución de problemas", "Soporte", "CRM", "Comunicación"],
        "habilidades_tecnicas": ["Empatía", "Comunicación efectiva", "Gestión de reclamos", "Orientación al cliente"],
        "herramientas": ["Zendesk", "HubSpot", "CRM", "Microsoft Teams"],
        "nivel": "Junior"
    },

    # --- SALUD ---
    "Healthcare Assistant": {
        "palabras_clave": ["Pacientes", "Asistencia", "Turnos", "Clínica", "Salud"],
        "habilidades_tecnicas": ["Atención sanitaria", "Comunicación", "Organización", "Apoyo clínico"],
        "herramientas": ["Excel", "Sistemas médicos", "Google Calendar"],
        "nivel": "Junior"
    },
    "Nurse": {
        "palabras_clave": ["Enfermería", "Pacientes", "Cuidados", "Hospital", "Urgencias", "Tratamientos"],
        "habilidades_tecnicas": ["Cuidados básicos", "Administración de medicamentos", "Trabajo en equipo", "Atención primaria"],
        "herramientas": ["Historias clínicas digitales", "Sistemas hospitalarios", "Equipos médicos"],
        "nivel": "Intermedio"
    }
}


# --- Funciones auxiliares ---
def generar_sugerencias(campo, puesto_data):
    """Genera sugerencias contextuales según el campo"""
    sugerencias = {
        "resumen": f"Incluí palabras como: {', '.join(puesto_data['palabras_clave'][:5])}",
        "experiencia": "Usá verbos de acción: Desarrollé, Implementé, Lideré, Optimicé, Analicé",
        "habilidades": f"Sugerencias: {', '.join(puesto_data['habilidades_tecnicas'])}",
        "proyectos": "Describí el impacto cuantificable (ej: 'Reduje el tiempo de procesamiento en 40%')"
    }
    return sugerencias.get(campo, "")

def calcular_score_ats(cv_data, puesto_data):
    """Calcula el score ATS basado en palabras clave"""
    texto_completo = " ".join([
        cv_data.get("resumen", ""),
        " ".join([exp.get("descripcion", "") for exp in cv_data.get("experiencias", [])]),
        " ".join(cv_data.get("habilidades", [])),
        " ".join([proy.get("descripcion", "") for proy in cv_data.get("proyectos", [])])
    ]).lower()
    
    palabras_encontradas = []
    for palabra in puesto_data["palabras_clave"]:
        if palabra.lower() in texto_completo:
            palabras_encontradas.append(palabra)
    
    score = len(palabras_encontradas) / len(puesto_data["palabras_clave"])
    return score, palabras_encontradas

def generar_cv_pdf(cv_data, puesto):
    """Genera un PDF profesional del CV"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    style_nombre = ParagraphStyle(
        'Nombre',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor("#2C3E50"),
        spaceAfter=6,
        alignment=TA_CENTER
    )
    
    style_contacto = ParagraphStyle(
        'Contacto',
        parent=styles['Normal'],
        fontSize=10,
        textColor=HexColor("#7F8C8D"),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    style_seccion = ParagraphStyle(
        'Seccion',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=HexColor("#3498DB"),
        spaceAfter=10,
        spaceBefore=15,
        borderWidth=0,
        borderColor=HexColor("#3498DB"),
        borderPadding=5
    )
    
    # Encabezado
    story.append(Paragraph(cv_data["nombre"], style_nombre))
    contacto = f"{cv_data.get('email', '')} | {cv_data.get('telefono', '')} | {cv_data.get('ubicacion', '')}"
    story.append(Paragraph(contacto, style_contacto))
    
    # Puesto objetivo
    story.append(Paragraph(f"<b>Puesto objetivo:</b> {puesto}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Resumen profesional
    if cv_data.get("resumen"):
        story.append(Paragraph("RESUMEN PROFESIONAL", style_seccion))
        story.append(Paragraph(cv_data["resumen"], styles['Normal']))
    
    # Experiencia
    if cv_data.get("experiencias"):
        story.append(Paragraph("EXPERIENCIA PROFESIONAL", style_seccion))
        for exp in cv_data["experiencias"]:
            story.append(Paragraph(f"<b>{exp['puesto']}</b> - {exp['empresa']}", styles['Normal']))
            story.append(Paragraph(f"<i>{exp['periodo']}</i>", styles['Normal']))
            story.append(Paragraph(exp['descripcion'], styles['Normal']))
            story.append(Spacer(1, 10))
    
    # Educación
    if cv_data.get("educacion"):
        story.append(Paragraph("EDUCACIÓN", style_seccion))
        for edu in cv_data["educacion"]:
            story.append(Paragraph(f"<b>{edu['titulo']}</b> - {edu['institucion']}", styles['Normal']))
            story.append(Paragraph(f"<i>{edu['periodo']}</i>", styles['Normal']))
            story.append(Spacer(1, 10))
    
    # Habilidades técnicas
    if cv_data.get("habilidades"):
        story.append(Paragraph("HABILIDADES TÉCNICAS", style_seccion))
        habilidades_texto = " • ".join(cv_data["habilidades"])
        story.append(Paragraph(habilidades_texto, styles['Normal']))
    
    # Proyectos
    if cv_data.get("proyectos"):
        story.append(Paragraph("PROYECTOS DESTACADOS", style_seccion))
        for proy in cv_data["proyectos"]:
            story.append(Paragraph(f"<b>{proy['nombre']}</b>", styles['Normal']))
            story.append(Paragraph(proy['descripcion'], styles['Normal']))
            story.append(Spacer(1, 10))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# --- Interfaz principal ---
st.title("📝 Generador Inteligente de CVs")
st.markdown("### Creá un CV optimizado para sistemas ATS (Applicant Tracking Systems)")

# Sidebar
with st.sidebar:
    st.header("💡 ¿Cómo funciona?")
    st.markdown("""
    **Los sistemas ATS escanean CVs buscando:**
    - Palabras clave específicas del puesto
    - Formato estructurado y legible
    - Información clara y cuantificable
    - Coincidencia con requisitos
    
    **Esta herramienta te ayuda a:**
    1. Estructurar tu CV correctamente
    2. Incluir palabras clave relevantes
    3. Optimizar tu contenido para ATS
    4. Generar un PDF profesional
    """)
    
    st.divider()
    st.metric("Score ATS objetivo", "70%+", help="Porcentaje mínimo recomendado")

# Inicializar estado
if "cv_data" not in st.session_state:
    st.session_state.cv_data = {
        "nombre": "",
        "email": "",
        "telefono": "",
        "ubicacion": "",
        "resumen": "",
        "experiencias": [],
        "educacion": [],
        "habilidades": [],
        "proyectos": []
    }

# Paso 1: Selección de puesto
st.subheader("🎯 Paso 1: Seleccioná tu puesto objetivo")
col1, col2 = st.columns([2, 1])

with col1:
    puesto_objetivo = st.selectbox(
        "¿A qué puesto querés aplicar?",
        options=list(PUESTOS_DATA.keys()),
        help="Elegí el puesto para recibir sugerencias personalizadas"
    )

with col2:
    if puesto_objetivo:
        puesto_info = PUESTOS_DATA[puesto_objetivo]
        st.info(f"**Nivel:** {puesto_info['nivel']}")

if puesto_objetivo:
    with st.expander("📋 Ver requisitos del puesto"):
        st.write("**Palabras clave importantes:**")
        st.write(", ".join(puesto_info["palabras_clave"]))
        st.write("**Habilidades técnicas:**")
        st.write(", ".join(puesto_info["habilidades_tecnicas"]))

st.divider()

# Paso 2: Información personal
st.subheader("👤 Paso 2: Información personal")
col1, col2 = st.columns(2)

with col1:
    st.session_state.cv_data["nombre"] = st.text_input(
        "Nombre completo*",
        value=st.session_state.cv_data["nombre"],
        placeholder="Juan Pérez"
    )
    st.session_state.cv_data["email"] = st.text_input(
        "Email*",
        value=st.session_state.cv_data["email"],
        placeholder="juan.perez@email.com"
    )

with col2:
    st.session_state.cv_data["telefono"] = st.text_input(
        "Teléfono*",
        value=st.session_state.cv_data["telefono"],
        placeholder="+54 11 1234-5678"
    )
    st.session_state.cv_data["ubicacion"] = st.text_input(
        "Ubicación",
        value=st.session_state.cv_data["ubicacion"],
        placeholder="Buenos Aires, Argentina"
    )

st.divider()

# Paso 3: Resumen profesional
st.subheader("📄 Paso 3: Resumen profesional")
st.caption(f"💡 {generar_sugerencias('resumen', puesto_info)}")

st.session_state.cv_data["resumen"] = st.text_area(
    "Escribí un resumen de 3-4 líneas destacando tu experiencia*",
    value=st.session_state.cv_data["resumen"],
    height=100,
    placeholder="Ejemplo: Científico de datos con 5 años de experiencia desarrollando modelos de ML..."
)

st.divider()

# Paso 4: Experiencia profesional
st.subheader("💼 Paso 4: Experiencia profesional")
st.caption(f"💡 {generar_sugerencias('experiencia', puesto_info)}")

num_experiencias = st.number_input("¿Cuántas experiencias querés agregar?", min_value=0, max_value=5, value=len(st.session_state.cv_data["experiencias"]))

experiencias_temp = []
for i in range(num_experiencias):
    with st.expander(f"Experiencia #{i+1}", expanded=(i==0)):
        exp = st.session_state.cv_data["experiencias"][i] if i < len(st.session_state.cv_data["experiencias"]) else {}
        
        col1, col2 = st.columns(2)
        with col1:
            puesto = st.text_input(f"Puesto", value=exp.get("puesto", ""), key=f"exp_puesto_{i}")
            empresa = st.text_input(f"Empresa", value=exp.get("empresa", ""), key=f"exp_empresa_{i}")
        with col2:
            periodo = st.text_input(f"Período", value=exp.get("periodo", ""), placeholder="2020 - 2023", key=f"exp_periodo_{i}")
        
        descripcion = st.text_area(
            f"Descripción de responsabilidades y logros",
            value=exp.get("descripcion", ""),
            height=100,
            key=f"exp_desc_{i}",
            placeholder="• Desarrollé modelos de ML que aumentaron la precisión en 25%\n• Lideré equipo de 3 analistas..."
        )
        
        experiencias_temp.append({
            "puesto": puesto,
            "empresa": empresa,
            "periodo": periodo,
            "descripcion": descripcion
        })

st.session_state.cv_data["experiencias"] = experiencias_temp

st.divider()

# Paso 5: Educación
st.subheader("🎓 Paso 5: Educación")

num_educacion = st.number_input("¿Cuántos títulos querés agregar?", min_value=0, max_value=5, value=len(st.session_state.cv_data["educacion"]))

educacion_temp = []
for i in range(num_educacion):
    with st.expander(f"Título #{i+1}", expanded=(i==0)):
        edu = st.session_state.cv_data["educacion"][i] if i < len(st.session_state.cv_data["educacion"]) else {}
        
        col1, col2 = st.columns(2)
        with col1:
            titulo = st.text_input(f"Título", value=edu.get("titulo", ""), key=f"edu_titulo_{i}")
            institucion = st.text_input(f"Institución", value=edu.get("institucion", ""), key=f"edu_inst_{i}")
        with col2:
            periodo = st.text_input(f"Período", value=edu.get("periodo", ""), placeholder="2015 - 2019", key=f"edu_periodo_{i}")
        
        educacion_temp.append({
            "titulo": titulo,
            "institucion": institucion,
            "periodo": periodo
        })

st.session_state.cv_data["educacion"] = educacion_temp

st.divider()

# Paso 6: Habilidades técnicas
st.subheader("🛠️ Paso 6: Habilidades técnicas")
st.caption(f"💡 {generar_sugerencias('habilidades', puesto_info)}")

habilidades_sugeridas = st.multiselect(
    "Seleccioná de las habilidades sugeridas:",
    options=puesto_info["habilidades_tecnicas"] + puesto_info["herramientas"],
    default=[h for h in st.session_state.cv_data.get("habilidades", []) if h in puesto_info["habilidades_tecnicas"] + puesto_info["herramientas"]]
)

habilidades_custom = st.text_input(
    "Agregá otras habilidades (separadas por coma):",
    value=", ".join([h for h in st.session_state.cv_data.get("habilidades", []) if h not in habilidades_sugeridas]),
    placeholder="Docker, Git, AWS"
)

habilidades_final = list(habilidades_sugeridas)
if habilidades_custom:
    habilidades_final.extend([h.strip() for h in habilidades_custom.split(",")])

st.session_state.cv_data["habilidades"] = habilidades_final

st.divider()

# Paso 7: Proyectos (opcional)
st.subheader("🚀 Paso 7: Proyectos destacados (opcional)")
st.caption(f"💡 {generar_sugerencias('proyectos', puesto_info)}")

num_proyectos = st.number_input("¿Cuántos proyectos querés agregar?", min_value=0, max_value=5, value=len(st.session_state.cv_data["proyectos"]))

proyectos_temp = []
for i in range(num_proyectos):
    with st.expander(f"Proyecto #{i+1}", expanded=(i==0)):
        proy = st.session_state.cv_data["proyectos"][i] if i < len(st.session_state.cv_data["proyectos"]) else {}
        
        nombre = st.text_input(f"Nombre del proyecto", value=proy.get("nombre", ""), key=f"proy_nombre_{i}")
        descripcion = st.text_area(
            f"Descripción",
            value=proy.get("descripcion", ""),
            height=80,
            key=f"proy_desc_{i}",
            placeholder="Sistema de recomendación que aumentó las conversiones en 30%..."
        )
        
        proyectos_temp.append({
            "nombre": nombre,
            "descripcion": descripcion
        })

st.session_state.cv_data["proyectos"] = proyectos_temp

st.divider()

# Análisis ATS y generación
st.subheader("📊 Análisis y generación del CV")

if st.button("🔍 Analizar y generar CV", type="primary"):
    if st.session_state.cv_data["nombre"] and st.session_state.cv_data["resumen"]:
        with st.spinner("Analizando tu CV..."):
            score, palabras_encontradas = calcular_score_ats(st.session_state.cv_data, puesto_info)
            
            # Mostrar métricas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Score ATS", f"{score*100:.1f}%", 
                         delta="Excelente" if score >= 0.7 else "Mejorable")
            with col2:
                st.metric("Palabras clave", f"{len(palabras_encontradas)}/{len(puesto_info['palabras_clave'])}")
            with col3:
                color = "🟢" if score >= 0.7 else "🟡" if score >= 0.5 else "🔴"
                st.metric("Estado", f"{color}")
            
            st.progress(score)
            
            # Detalles
            col_det1, col_det2 = st.columns(2)
            
            with col_det1:
                st.markdown("### ✅ Palabras clave incluidas")
                for palabra in palabras_encontradas:
                    st.markdown(f"✓ {palabra}")
            
            with col_det2:
                st.markdown("### ⚠️ Palabras clave faltantes")
                faltantes = [p for p in puesto_info["palabras_clave"] if p not in palabras_encontradas]
                for palabra in faltantes:
                    st.markdown(f"• {palabra}")
            
            # Recomendaciones
            if score < 0.7:
                st.warning(f"💡 **Recomendación:** Incluí las palabras clave faltantes en tu resumen, experiencia o proyectos para mejorar tu score ATS.")
            else:
                st.success("🎉 **¡Excelente!** Tu CV está bien optimizado para sistemas ATS.")
            
            # Generar PDF
            pdf = generar_cv_pdf(st.session_state.cv_data, puesto_objetivo)
            
            st.download_button(
                label="📥 Descargar CV en PDF",
                data=pdf,
                file_name=f"CV_{st.session_state.cv_data['nombre'].replace(' ', '_')}.pdf",
                mime="application/pdf",
                type="secondary"
            )
    else:
        st.error("⚠️ Por favor, completá al menos tu nombre y resumen profesional.")

# Footer
st.divider()
st.caption("💼 Herramienta diseñada para optimizar CVs según algoritmos ATS utilizados por empresas tech")
# Footer
st.divider()
st.caption("💼 Herramienta con datos actualizados desde APIs de empleo | Optimizada para sistemas ATS")
