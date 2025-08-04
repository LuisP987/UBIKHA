from fastapi import APIRouter, HTTPException
from schemas.verification import PhoneVerification, CodeVerification
from services.whatsapp import WhatsAppService

router = APIRouter(prefix="/verification", tags=["verification"])
whatsapp_service = WhatsAppService()

@router.post("/send-code")
async def send_verification_code(phone: PhoneVerification):
    success = await whatsapp_service.send_code(phone.phone_number)
    if not success:
        raise HTTPException(status_code=500, detail="Error sending verification code")
    return {"message": "Verification code sent"}

@router.post("/verify-code")
async def verify_code(verification: CodeVerification):
    if whatsapp_service.verify_code(verification.phone_number, verification.code):
        return {"verified": True}
    raise HTTPException(status_code=400, detail="Invalid verification code")
