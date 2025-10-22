import os
import time
import glob
import base64
import streamlit as st
from gtts import gTTS
from PIL import Image

# =========================
# Encabezado e imagen
# =========================
st.title("Conversión de Texto a Audio · Sisabe")
image = Image.open('luciernaga.jpg')
st.image(image, width=350)
with st.sidebar:
    st.subheader("Escribe y/o selecciona texto para escucharlo.")
    st.write("1) Revisa o edita el cuentecito.\n2) Elige el idioma.\n3) Pulsa **Convertir a audio**.")

# Carpeta temporal segura
os.makedirs("temp", exist_ok=True)

# =========================
# Microcuento (cambiado)
# =========================
st.subheader("Un cuentecito para dormir 😴")

nuevo_cuento = (
    "La luciérnaga más pequeña del bosque temblaba cada noche porque creía que su luz no alcanzaba. "
    "Un niño que no podía dormir la encontró en su ventana y le susurró: “brilla solo para mí”. "
    "Entonces, el cuarto dejó de ser oscuro y, aunque la luz era chiquita, alcanzó para espantar todas las sombras. "
    "Desde esa noche, la luciérnaga ya no tuvo miedo; descubrió que a veces, lo pequeño es exactamente lo que se necesita."
)

st.markdown("¿Quieres escucharlo? Puedes editarlo abajo antes de convertirlo.")
text = st.text_area("Texto a convertir", value=nuevo_cuento, height=150)

# =========================
# Configuración de idioma
# =========================
tld = 'com'  # afecta principalmente voces en inglés
option_lang = st.selectbox(
    "Selecciona el lenguaje de salida",
    ("Español", "English"),
    index=0
)
lg = 'es' if option_lang == "Español" else 'en'

# =========================
# Utilidades
# =========================
def safe_filename(s: str, fallback: str = "audio"):
    s = (s or "").strip()
    if not s:
        return fallback
    # Limita y limpia el nombre
    base = "".join(c for c in s[:32] if c.isalnum() or c in ("-", "_", " "))
    base = base.strip().replace(" ", "_")
    return base or fallback

def text_to_speech(text: str, tld: str, lg: str):
    # gTTS usa tld para variantes de acento (más notable en 'en')
    tts = gTTS(text, lang=lg, tld=tld, slow=False)
    file_stub = safe_filename(text)
    file_path = f"temp/{file_stub}.mp3"
    tts.save(file_path)
    return file_stub, text, file_path

# =========================
# Conversión
# =========================
if st.button("Convertir a audio"):
    if not text.strip():
        st.warning("Primero escribe o pega algún texto.")
    else:
        try:
            result, output_text, file_path = text_to_speech(text, tld, lg)
            st.success("¡Listo! Tu audio está abajo.")

            # Reproduce
            with open(file_path, "rb") as f:
                audio_bytes = f.read()
            st.markdown("### 🎧 Tu audio")
            st.audio(audio_bytes, format="audio/mp3", start_time=0)

            # Descarga directa
            st.download_button("⬇️ Descargar MP3", data=audio_bytes, file_name=f"{result}.mp3")

            # (Opcional) Enlace HTML simple como extra
            def get_binary_file_downloader_html(data_bytes, filename="audio.mp3", label="Descargar (HTML)"):
                bin_str = base64.b64encode(data_bytes).decode()
                href = f'<a href="data:audio/mp3;base64,{bin_str}" download="{filename}">{label}</a>'
                return href

            st.markdown(get_binary_file_downloader_html(audio_bytes, filename=f"{result}.mp3"),
                        unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Ocurrió un problema al generar el audio: {e}")

# =========================
# Limpieza de archivos viejos
# =========================
def remove_files(n_days: int):
    mp3_files = glob.glob("temp/*.mp3")
    if not mp3_files:
        return
    now = time.time()
    horizon = now - n_days * 86400
    for f in mp3_files:
        try:
            if os.stat(f).st_mtime < horizon:
                os.remove(f)
        except Exception:
            pass

remove_files(7)
