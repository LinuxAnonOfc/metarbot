import os
import telebot
import requests
from decouple import config

BOT_TOKEN = config('BOT_TOKEN')
REDEMET_API_URL = 'https://api-redemet.decea.mil.br/aerodromos/status/localidades/'
REDEMET_API_KEY = config('REDEMET_API_KEY')

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message,
        f"Olá, {message.chat.first_name}! Espero que você esteja bem. Por favor, digite os códigos dos aeródromos (ICAO) separados por vírgula para que eu possa fornecer informações."
    )


@bot.message_handler(func=lambda message: True)
def get_aerodromo_info(message):
    airport_codes = message.text.strip().upper().split(',')
    try:
        aerodromo_info = fetch_aerodromo_info(airport_codes)
        bot.reply_to(message, aerodromo_info)
    except Exception as e:
        bot.reply_to(
            message,
            f"Desculpe, não foi possível obter informações para os aeródromos {', '.join(airport_codes)}. Certifique-se de fornecer códigos de aeródromos válidos."
        )
        print(f"Erro na chamada da API: {str(e)}")


def fetch_aerodromo_info(airport_codes):
    endpoint = f"{REDEMET_API_URL}{','.join(airport_codes)}"
    params = {'api_key': REDEMET_API_KEY}
    response = requests.get(endpoint, params=params)
    data = response.json()

    print("Resposta da API:", data)  # Impressão da resposta da API para depuração

    aerodromo_info = ''
    if data and isinstance(data, dict) and 'data' in data:
        aerodromo_list = data['data']
        for aerodromo in aerodromo_list:
            aerodromo_info += f"Informações do aeródromo {aerodromo[0]}:\n\n"
            aerodromo_info += f"Nome: {aerodromo[1]}\n"
            aerodromo_info += f"Latitude: {aerodromo[2]}\n"
            aerodromo_info += f"Longitude: {aerodromo[3]}\n"
            aerodromo_info += f"Grupo: {aerodromo[4]}\n"
            aerodromo_info += f"Mensagem: {aerodromo[5]}\n\n"
    else:
        aerodromo_info = f"Não foi possível obter informações para os aeródromos {', '.join(airport_codes)}."

    return aerodromo_info


bot.infinity_polling()
