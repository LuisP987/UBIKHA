import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def enviar_codigo_verificacion(destinatario: str, codigo: str):
    smtp_user = "eff1a789204198"  # tu usuario real aquí
    smtp_password = "937b6421ec095b"

    remitente = "Ubikha App <no-reply@ubikha.com>"
    asunto = "Código de verificación"
    cuerpo = f"Tu código de verificación es: {codigo}"

    mensaje = MIMEMultipart()
    mensaje["From"] = remitente
    mensaje["To"] = destinatario
    mensaje["Subject"] = asunto
    mensaje.attach(MIMEText(cuerpo, "plain"))

    try:
        with smtplib.SMTP("sandbox.smtp.mailtrap.io", 2525) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(remitente, destinatario, mensaje.as_string())
            print("Correo enviado correctamente.")
    except Exception as e:
        print("Error al enviar correo:", e)
        raise
