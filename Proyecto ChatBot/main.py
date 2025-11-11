#LIBRERIAS
import streamlit as st
import groq

#VARIABLES
altura_contenedor_chat = 600
stream_status = True

class Personalidad:
    def __init__(self, nombre, edad, rasgos, tono, emoji):
        self.nombre = nombre
        self.edad = edad
        self.rasgos = rasgos
        self.tono = tono
        self.emoji = emoji

    def obtener_prompt_sistema(self):
        return f"""Actúa como una persona con las siguientes características:
        - Nombre: {self.nombre}
        - Edad: {self.edad} años
        - Rasgos de personalidad: {', '.join(self.rasgos)}
        - Tono de comunicación: {self.tono}
        Mantén esta personalidad en todas tus respuestas."""

#CONSTANTES
MODELOS = ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "llama-3.3-70b-versatile"]

PERSONALIDADES = {
    "Niño": Personalidad(
        nombre="alexis",
        edad=11,
        rasgos=["Curioso", "Energético", "Inocente"],
        tono="Alegre y simple, usando palabras sencillas",
        emoji="👶"
    ),
    "Adolescente": Personalidad(
        nombre="emilio",
        edad=16,
        rasgos=["Rebelde", "Creativo", "Social," "Otaku", "formal"],
        tono="Informal",
        emoji="🤙"
    ),
    "Adulto": Personalidad(
        nombre="Thiago",
        edad=35,
        rasgos=["Profesional", "Analítico", "Maduro"],
        tono="Formal y reflexivo",
        emoji="👨‍💼"
    )
}

#FUNCIONES

#ESTA FUNCIÓN UTILIZA STREAMLIT PARA CREAR LA INTERFAZ DE LA PÁGINA Y ADEMÁS RETORNA El
#MODELO ELEGIDO POR EL USUARIO
def configurar_pagina():

    st.set_page_config(page_title="IA de informatica", page_icon= "🗣️")

    st.title("El chat de informatica")

    st.sidebar.title("Seleccion de modelos")
    # ZONA DE EDADES
    st.sidebar.markdown("### 🧭 Elige una personalidad")
    st.session_state['zona_edad'] = st.sidebar.radio(
        "Personalidad:",
        options=["Niño", "Adolescente", "Adulto"],
        index=1,
        horizontal=True
    )
    elegirModelo = st.sidebar.selectbox("Elegí un modelo", options=MODELOS, index=0)

    return elegirModelo

#ESTA FUNCION LLAMA A st.secrets PARA OBTENER LA CLAVE DE LA API DE GROQ Y CREA UN USUARIO
def crear_usuario():    
    clave_secreta = st.secrets["CLAVE_API"]
    return groq.Groq(api_key = clave_secreta)

#CONFIGURA EL MODELO DE LENGUAJE PARA QUE PROCESE EL PROMPT DEL USUARIO
def configurar_modelo(cliente, modelo_elegido, prompt_usuario, personalidad):
    return cliente.chat.completions.create(
        model = modelo_elegido,
        messages = [
            {"role": "system", "content": personalidad.obtener_prompt_sistema()},
            {"role": "user", "content": prompt_usuario}
        ],
        stream = stream_status
    )

#CREAMOS UNA SESION LLAMADA "mensajes" QUE VA A GUARDAR LO QUE LE ESCRIBIMOS AL CHATBOT
def inicializar_estado():
    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []

def actualizar_historial(rol, contenido, avatar):
    st.session_state.mensajes.append({"role" : rol, "content" : contenido, "avatar" : avatar})

def mostrar_historial():
    for mensaje in st.session_state.mensajes:
        with st.chat_message(mensaje["role"], avatar=mensaje["avatar"]):
            st.write(mensaje["content"])

def area_chat():
    contenedor = st.container(height=altura_contenedor_chat, border=True)
    with contenedor:
        mostrar_historial()

def generar_respuesta(respuesta_completa_del_bot):
    _respuesta_posta = ""
    for frase in respuesta_completa_del_bot:
        if frase.choices[0].delta.content:
            _respuesta_posta += frase.choices[0].delta.content
            yield frase.choices[0].delta.content
    return _respuesta_posta

#---------------------------IMPLEMENTACION-------------------------------------

def main():
    modelo_elegido_por_el_usuario = configurar_pagina()
    personalidad_elegida = PERSONALIDADES[st.session_state.get('zona_edad', "Adolescente")]

    cliente_usuario = crear_usuario()

    inicializar_estado()

    area_chat()

    promt_del_usuario = st.chat_input("Escribí tu prompt: ")

    if promt_del_usuario:
        actualizar_historial("user", promt_del_usuario, "😠")
        respuesta_del_bot = configurar_modelo(
            cliente_usuario, 
            modelo_elegido_por_el_usuario, 
            promt_del_usuario,
            personalidad_elegida
        )
        
        if respuesta_del_bot:
            # Capturamos los fragmentos mientras los mostramos en la interfaz
            collected_chunks = []

            def _wrapped_gen():
                for chunk in generar_respuesta(respuesta_del_bot):
                    collected_chunks.append(chunk)
                    yield chunk

            # Mostrar en streaming al usuario
            with st.chat_message("assistant"):
                st.write_stream(_wrapped_gen())

            # Guardar la respuesta completa en el historial (una sola vez)
            respuesta_posta = "".join(collected_chunks)
            actualizar_historial("assistant", respuesta_posta, personalidad_elegida.emoji)

            st.rerun()


if __name__ == "__main__":
    main()