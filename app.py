import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import date, time as dt_time
import time
import base64
import json 

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
        return ""

logo_base64 = get_image_base64("logo.jpg")

# --- CSS BLINDADO ---
css_code = f"""
    <style>
        .stApp {{ background-color: {NEGRO}; color: {NEGRO}; }}
        h1 {{ color: {BLANCO} !important; text-transform: uppercase; font-family: 'Arial Black', sans-serif; }}
        h3, h4 {{ color: {ROJO} !important; }}
        label, .stMarkdown p, .stCaption {{ color: {BLANCO} !important; }}
        .stCaption {{ text-align: center; }}
        
        .floating-logo {{
            position: fixed; top: 25px; left: 25px; z-index: 9999; width: 205px; 
            filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.5));
        }}
        @media (max-width: 640px) {{ .floating-logo {{ width: 120px; top: 15px; left: 15px; }} }}

        div[data-baseweb="select"] > div, div[data-baseweb="base-input"], div[data-baseweb="input"], div[data-baseweb="timepicker"] {{
            background-color: {GRIS_INPUT} !important; border: 1px solid {BLANCO} !important; border-radius: 8px !important; color: {BLANCO} !important;
        }}
        input {{ color: {BLANCO} !important; }}
        
        div[data-testid="stNumberInput"] button {{ background-color: {ROJO} !important; color: {BLANCO} !important; border: 1px solid {ROJO} !important; }}
        div[data-testid="stNumberInput"] button svg {{ fill: {BLANCO} !important; }}
        
        div.stButton > button {{
            background-color: {ROJO} !important; color: {BLANCO} !important; border: 2px solid {ROJO} !important;
            font-weight: 800 !important; font-size: 20px !important; text-transform: uppercase; padding: 15px; width: 100%; border-radius: 8px; transition: all 0.2s ease;
        }}
        div.stButton > button p {{ color: {BLANCO} !important; }}
        div.stButton > button:hover {{ background-color: {BLANCO} !important; border-color: {ROJO} !important; transform: scale(1.02); }}
        div.stButton > button:hover p {{ color: {ROJO} !important; }}

        div.stSlider > div > div > div > div {{ background-color: {ROJO}; }}
        div[data-baseweb="timepicker"] svg {{ fill: {BLANCO} !important; }}
        #MainMenu, footer, header {{visibility: hidden;}} .stDeployButton {{display:none;}}
    </style>
"""
st.markdown(css_code, unsafe_allow_html=True)

if logo_base64:
    st.markdown(f'<img src="{logo_base64}" class="floating-logo">', unsafe_allow_html=True)

# --- 2. CONEXIÓN INTELIGENTE (ESTA ES LA CLAVE) ---
@st.cache_resource
def conectar_sheet():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

    # PRUEBA 1: Intentar leer de la Caja Fuerte (Nube)
    if "gcp_service_account" in st.secrets:
        try:
            info_dict = dict(st.secrets["gcp_service_account"]) # Forzamos formato dict
            creds = Credentials.from_service_account_info(info_dict, scopes=scopes)
            client = gspread.authorize(creds)
            return client.open("Mirandes B 2026").worksheet("CONTROL_CARGA")
        except Exception as ex:
            st.error(f"Error leyendo Secretos: {ex}")
            st.stop()
            
    # PRUEBA 2: Intentar leer archivo local (Solo si falla la nube)
    try:
        creds = Credentials.from_service_account_file("mirandes_secret.json", scopes=scopes)
        client = gspread.authorize(creds)
        return client.open("Mirandes B 2026").worksheet("CONTROL_CARGA")
    except FileNotFoundError:
        st.error("❌ ERROR CRÍTICO: No encuentro las llaves.")
        st.info("Si estás en la Nube: Verifica que has configurado los 'Secrets' con el título [gcp_service_account].")
        st.stop()

try:
    hoja = conectar_sheet()
except Exception as e:
    st.error(f"Error Conexión: {e}")
    st.stop()

# --- 3. INTERFAZ ---
c_escudo, c_texto = st.columns([1, 3.5])
with c_escudo:
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/c/c9/CD_Mirandes_logo.svg/1200px-CD_Mirandes_logo.svg.png", width=110)
with c_texto:
    st.title("CD MIRANDÉS B")
    st.markdown(f"<span style='color:{ROJO}; font-weight:bold; letter-spacing:1px; font-size:18px;'>🔴⚫ CONTROL DE RENDIMIENTO</span>", unsafe_allow_html=True)

st.write("---")

# --- 4. FORMULARIO ---
with st.form("mi_formulario", clear_on_submit=True):
    c1, c2 = st.columns(2)
    dorsal = c1.selectbox("DORSAL", list(range(1, 26)))
    fecha = c2.date_input("FECHA", date.today())
    st.write("")
    
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
    enviar = st.form_submit_button("ENVIAR DATOS")

    if enviar:
        try:
            with st.spinner('Enviando al cuerpo técnico...'):
                fecha_str = fecha.strftime("%Y-%m-%d")
                sRPE = rpe * minutos
                sueno_horas_decimal = hora_input.hour + (hora_input.minute / 60)
                datos = [fecha_str, dorsal, sueno_calidad, sueno_horas_decimal, fatiga, dolor, estres, rpe, sRPE]
                hoja.append_row(datos)
                time.sleep(1)
            st.success(f"✅ REGISTRO COMPLETADO. GRACIAS, DORSAL {dorsal}")
            time.sleep(2)
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")



