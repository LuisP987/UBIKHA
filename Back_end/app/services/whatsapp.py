import random
from typing import Dict
import requests
from dotenv import load_dotenv
import os

load_dotenv()

class WhatsAppService:
    def __init__(self):
        self.verification_codes: Dict[str, str] = {}
        self.WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
        self.WHATSAPP_URL = os.getenv("WHATSAPP_URL")

    def generate_code(self, phone_number: str) -> str:
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        self.verification_codes[phone_number] = code
        return code

    async def send_code(self, phone_number: str) -> bool:
        code = self.generate_code(phone_number)
        
        headers = {
            "Authorization": f"Bearer {self.WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "template",
            "template": {
                "name": "verification_code",
                "language": {
                    "code": "es"
                },
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {
                                "type": "text",
                                "text": code
                            }
                        ]
                    }
                ]
            }
        }

        try:
            response = requests.post(self.WHATSAPP_URL, headers=headers, json=data)
            return response.status_code == 200
        except:
            return False

    def verify_code(self, phone_number: str, code: str) -> bool:
        stored_code = self.verification_codes.get(phone_number)
        if stored_code and stored_code == code:
            del self.verification_codes[phone_number]
            return True
        return False
