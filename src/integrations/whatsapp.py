# src/integrations/whatsapp.py
import os

class WhatsAppIntegration:
    def __init__(self, number=None, token=None, provider=None):
        self.number = number or os.getenv('WHATSAPP_NUMBER')
        self.token = token or os.getenv('WHATSAPP_TOKEN')
        self.provider = provider or os.getenv('WHATSAPP_PROVIDER', 'wppconnect')

    def send_message(self, to, text):
        # Aqui você implementa a chamada para o provedor (ex: wppconnect, Z-API, etc)
        # Exemplo de stub:
        print(f"[WhatsApp] Enviando para {to}: {text}")
        # TODO: chamada real à API do provedor
        return True

    def update_number(self, new_number):
        self.number = new_number
        # Opcional: salvar em config/db

    def get_number(self):
        return self.number

# Exemplo de uso plug and play:
# from src.integrations.whatsapp import WhatsAppIntegration
# wa = WhatsAppIntegration()
# wa.send_message('5511999999999', 'Olá, mundo!')
