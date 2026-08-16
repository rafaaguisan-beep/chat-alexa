import streamlit as st
import asyncio
import os
from google import genai
from alexapy import AlexaLogin, AlexaAPI
import nest_asyncio

# O Render vai puxar os dados salvos lá de forma segura
CHAVE_GEMINI = os.environ.get("CHAVE_GEMINI")
EMAIL_AMAZON = os.environ.get("EMAIL_AMAZON")
SENHA_AMAZON = os.environ.get("SENHA_AMAZON")
NOME_TV = os.environ.get("NOME_TV")

st.title("💬 Chat Alexa + Gemini")

async def falar(txt):
    login = AlexaLogin("amazon.com.br", EMAIL_AMAZON, SENHA_AMAZON, output_path="./alexa_session")
    try:
        await login.login_with_cookie()
        alexa = AlexaAPI(login)
        await alexa.send_tts(txt, customer_id=login.customer_id, device_serial=NOME_TV)
        return True
    except Exception as e:
        return str(e)

if p := st.chat_input("Pergunte algo..."):
    with st.chat_message("user"):
        st.markdown(p)
    with st.chat_message("assistant"):
        st.write("Pensando...")
        client = genai.Client(api_key=CHAVE_GEMINI)
        res = client.models.generate_content(
            model='gemini-2.5-flash',
            contents="Responda curto para ler em voz alta: " + p
        )
        st.markdown(res.text)
        nest_asyncio.apply()
        ok = asyncio.run(falar(res.text))
        if ok == True:
            st.success("🗣️ Enviado para a TV!")
        else:
            st.error(ok)
