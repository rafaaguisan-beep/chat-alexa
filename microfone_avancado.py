import asyncio
import os
from google import genai
from alexapy import AlexaLogin, AlexaAPI
import nest_asyncio

# O Render vai puxar os dados salvos nas configurações por segurança
CHAVE_GEMINI = os.environ.get("CHAVE_GEMINI")
EMAIL_AMAZON = os.environ.get("EMAIL_AMAZON")
SENHA_AMAZON = os.environ.get("SENHA_AMAZON")
NOME_TV = os.environ.get("NOME_TV")

async def escutar_tv():
    login = AlexaLogin("amazon.com.br", EMAIL_AMAZON, SENHA_AMAZON, output_path="./alexa_session")
    await login.login_with_cookie()
    alexa = AlexaAPI(login)
    client = genai.Client(api_key=CHAVE_GEMINI)
    
    print("🎙️ [ROBÔ AVANÇADO ATIVADO NO MICROFONE]")
    
    # LISTA EXPANDIDA DE PREFIXOS (Todos os que você pediu!)
    palavras_chave = [
        "perguntar ao robô", "falar com o gênio", "chamar a máquina", "pergunta pro robo",
        "o que significa", "modo gemini", "pergunte ao gemini", "pergunte ao computador",
        "chame o gemini", "fale com a ia", "pesquise", "modo ia"
    ]
    
    ultimo_id = ""
    while True:
        try:
            historico = await alexa.get_history()
            if historico:
                texto_falado = historico.get("summary", "").lower()
                id_cmd = historico.get("id", "")
                
                # Verifica se você usou QUALQUER uma das palavras-chave no controle da TV
                if id_cmd != ultimo_id and any(frase in texto_falado for frase in palavras_chave):
                    ultimo_id = id_cmd
                    
                    # Descobre qual das frases você usou para conseguir recortar o texto certo
                    frase_usada = next(frase for frase in palavras_chave if frase in texto_falado)
                    pergunta = texto_falado.split(frase_usada)[-1].strip()
                    
                    if pergunta:
                        print(f"\n🎙️ Ouvido na TV: '{pergunta}' (Ativado por: '{frase_usada}')")
                        
                        # Ajustamos o prompt para o Gemini entender melhor buscas que começam com "pesquise" ou "o que significa"
                        prompt_final = f"Responda de forma curta, direta e amigável para ser lida em voz alta: {pergunta}"
                        
                        res = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=prompt_final
                        )
                        
                        print(f"🗣️ Enviando resposta para a TV...")
                        await alexa.send_tts(res.text, customer_id=login.customer_id, device_serial=NOME_TV)
            await asyncio.sleep(3)
        except Exception:
            await asyncio.sleep(3)

if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(escutar_tv())
