import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import date, time as dt_time
import time
import base64 # Necesario para leer la imagen local

# --- 1. CONFIGURACIÓN VISUAL ---
ROJO = "#D9001D"
NEGRO = "#0e1117"
BLANCO = "#FFFFFF"
GRIS_INPUT = "#262730"

st.set_page_config(page_title="CD Mirandés B", page_icon="⚽", layout="centered")

# --- FUNCIÓN PARA LEER EL LOGO LOCAL ---
def get_image_base64(path):
    try:
        with open(path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
        return f"data:image/jpg;base64,{encoded}"
    except FileNotFoundError:
        st.error(f"❌ ERROR: No encuentro el archivo '{path}' en la carpeta. Asegúrate de que está ahí.")
        st.stop()

# Leemos el logo.jpg local
logo_base64 = get_image_base64("logo.jpg")

# --- CSS BLINDADO + LOGO FLOTANTE MÁS GRANDE ---
css_code = f"""
    <style>
        /* 1. Fondo y Colores Base */
        .stApp {{ background-color: {NEGRO}; color: {NEGRO}; }}
        h1, h2 {{ color: {BLANCO} !important; text-transform: uppercase; text-align: center; }}
        h3, h4 {{ color: {ROJO} !important; }}
        label, .stMarkdown p, .stCaption {{ color: {BLANCO} !important; }}
        .stCaption {{ text-align: center; }} /* Subtítulo centrado */
        
        /* 2. LOGO FLOTANTE (AUMENTADO DE TAMAÑO) */
        .floating-logo {{
            position: fixed;
            top: 25px;
            left: 25px;
            z-index: 9999;
            width: 150px; /* <--- CAMBIADO: ANTES 100px, AHORA 150px */
            filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.5));
        }}
        /* En móviles también lo hacemos un poco más grande */
        @media (max-width: 640px) {{
             .floating-logo {{
                 width: 100px; /* <--- CAMBIADO: ANTES 70px, AHORA 100px */
                 top: 15px;
                 left: 15px;
             }}
        }}

        /* 3. Inputs y Cajas */
        div[data-baseweb="select"] > div, 
        div[data-baseweb="base-input"], 
        div[data-baseweb="input"],
        div[data-baseweb="timepicker"] {{
            background-color: {GRIS_INPUT} !important;
            border: 1px solid {BLANCO} !important;
            border-radius: 8px !important;
            color: {BLANCO} !important;
        }}
        input {{ color: {BLANCO} !important; }}
        
        /* 4. Botones +/- */
        div[data-testid="stNumberInput"] button {{
            background-color: {ROJO} !important;
            color: {BLANCO} !important;
            border: 1px solid {ROJO} !important;
        }}
        div[data-testid="stNumberInput"] button svg {{ fill: {BLANCO} !important; }}
        
        /* 5. BOTÓN ENVIAR */
        div.stButton > button {{
            background-color: {ROJO} !important;
            color: {BLANCO} !important;
            border: 2px solid {ROJO} !important;
            font-weight: 800 !important;
            font-size: 20px !important;
            text-transform: uppercase;
            padding: 15px;
            width: 100%;
            border-radius: 8px;
            letter-spacing: 1px;
            transition: all 0.2s ease;
        }}
        div.stButton > button p {{ color: {BLANCO} !important; }}
        
        /* Hover Botón Enviar */
        div.stButton > button:hover {{
            background-color: {BLANCO} !important;
            border-color: {ROJO} !important;
            transform: scale(1.02);
        }}
        div.stButton > button:hover p {{ color: {ROJO} !important; }}

        /* 6. Sliders y Reloj */
        div.stSlider > div > div > div > div {{ background-color: {ROJO}; }}
        div[data-baseweb="timepicker"] svg {{ fill: {BLANCO} !important; }}
        
        /* Limpieza */
        #MainMenu, footer, header {{visibility: hidden;}}
        .stDeployButton {{display:none;}}
    </style>
"""
# Inyectamos el CSS
st.markdown(css_code, unsafe_allow_html=True)

# INYECTAMOS EL LOGO FLOTANTE USANDO HTML DIRECTO
st.markdown(f'<img src="{logo_base64}" class="floating-logo">', unsafe_allow_html=True)


# --- 2. CONEXIÓN BLINDADA (VERSIÓN NUBE) ---
@st.cache_resource
def conectar_sheet():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    
    # CAMBIO IMPORTANTE: Leemos de st.secrets en lugar del archivo
    # Usamos .from_service_account_info en lugar de .from_service_account_file
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
    client = gspread.authorize(creds)
    return client.open("Mirandes B 2026").worksheet("CONTROL_CARGA")try:
    hoja = conectar_sheet()
except Exception as e:
    st.error(f"Error Conexión: {e}")
    st.stop()

# --- 3. TÍTULO PRINCIPAL ---
st.title("CD MIRANDÉS B")
st.caption("🔴⚫ CONTROL DE RENDIMIENTO")

st.write("---")

# --- 4. FORMULARIO ---
with st.form("mi_formulario", clear_on_submit=True):
    
    # DATOS
    c1, c2 = st.columns(2)
    dorsal = c1.selectbox("DORSAL", list(range(1, 26)))
    fecha = c2.date_input("FECHA", date.today())
    
    st.write("")
    
    # --- BIENESTAR ---
    st.markdown(f"<h4 style='color:{ROJO}'>🧩 ESTADO ACTUAL</h4>", unsafe_allow_html=True)
    
    col_sueno1, col_sueno2 = st.columns(2)
    with col_sueno1:
        st.write("💤 **CALIDAD SUEÑO**")
        txt_s = {1:"1 (Fatal)", 2:"2 (Mal)", 3:"3 (Normal)", 4:"4 (Bien)", 5:"5 (Perfecto)"}
        sueno_calidad = st.select_slider("sc", options=[1,2,3,4,5], value=3, format_func=lambda x: txt_s[x], label_visibility="collapsed")
    with col_sueno2:
        st.write("⏱️ **HORAS DORMIDAS**")
        hora_input = st.time_input("sh", value=dt_time(8, 0), label_visibility="collapsed")

    st.write("") 

    cw1, cw2 = st.columns(2)
    txt_f = {1:"1 (Fresco)", 2:"2 (Bien)", 3:"3 (Normal)", 4:"4 (Cansado)", 5:"5 (Muerto)"}
    txt_d = {1:"1 (Nada)", 2:"2 (Molestia)", 3:"3 (Pequeño)", 4:"4 (Dolor)", 5:"5 (Lesión)"}
    txt_e = {1:"1 (Muy Mal)", 2:"2 (Mal)", 3:"3 (Normal)", 4:"4 (Bien)", 5:"5 (A tope)"}

    with cw1:
        st.write("🔋 **FATIGA**")
        fatiga = st.select_slider("f", options=[1,2,3,4,5], value=3, format_func=lambda x: txt_f[x], label_visibility="collapsed")
        
        st.write("🧠 **ESTRÉS**")
        estres = st.select_slider("e", options=[1,2,3,4,5], value=3, format_func=lambda x: txt_e[x], label_visibility="collapsed")

    with cw2:
        st.write("🤕 **DOLOR**")
        dolor = st.select_slider("d", options=[1,2,3,4,5], value=1, format_func=lambda x: txt_d[x], label_visibility="collapsed")
    
    st.write("---")
    
    # --- CARGA ---
    st.markdown(f"<h4 style='color:{ROJO}'>🏃‍♂️ENTRENAMIENTO AYER</h4>", unsafe_allow_html=True)
    
    def texto_rpe(val):
        if val == 0: return "0 (Descanso)"
        if val <= 3: return f"{val} (Muy Ligero)"
        if val <= 6: return f"{val} (Moderado)"
        if val == 7: return "7 (Intenso)"
        if val == 8: return "8 (Muy Intenso)"
        if val == 9: return "9 (Casi Máximo)"
        if val == 10: return "10 (Máximo)"
        return str(val)

    ct1, ct2 = st.columns(2)
    with ct1:
        st.write("📈 **DUREZA (RPE)**")
        rpe = st.select_slider("r", options=list(range(0, 11)), value=0, format_func=texto_rpe, label_visibility="collapsed")
        
    with ct2:
        st.write("⏱️ **MINUTOS**")
        minutos = st.number_input("m", 0, 180, 0, step=5, label_visibility="collapsed")
    
    st.write("")
    
    # BOTÓN ENVIAR
    enviar = st.form_submit_button("ENVIAR DATOS")

    if enviar:
        try:
            with st.spinner('Enviando al cuerpo técnico...'):
                fecha_str = fecha.strftime("%Y-%m-%d")
                sRPE = rpe * minutos
                
                # Cálculo de hora decimal
                sueno_horas_decimal = hora_input.hour + (hora_input.minute / 60)
                
                datos = [fecha_str, dorsal, sueno_calidad, sueno_horas_decimal, fatiga, dolor, estres, rpe, sRPE]
                
                hoja.append_row(datos)
                time.sleep(1)
            
            st.success(f"✅ REGISTRO COMPLETADO. GRACIAS, DORSAL {dorsal}")
            time.sleep(2)
            st.rerun()
            
        except Exception as e:
            st.error(f"Error: {e}")