from pydantic import BaseModel

class PhoneVerification(BaseModel):
    phone_number: str

class CodeVerification(BaseModel):
    phone_number: str
    code: str
