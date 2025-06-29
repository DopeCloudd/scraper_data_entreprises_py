import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Mailer:
    """
    Envoie un email avec un fichier attaché en utilisant Gmail SMTP.
    """
    def __init__(self, user: str, password: str):
        self.user = user
        self.password = password

    def send_email(self, to: list[str], subject: str, body: str, attachment: str):
        # Création du message
        msg = MIMEMultipart()
        msg["From"] = self.user
        msg["To"] = ", ".join(to)
        msg["Subject"] = subject

        # Corps
        msg.attach(MIMEText(body, "plain"))

        # Pièce jointe
        filename = os.path.basename(attachment)
        with open(attachment, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={filename}")
            msg.attach(part)

        # Envoi
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(self.user, self.password)
            server.sendmail(
                self.user,
                to,  # Ici une liste de destinataires
                msg.as_string()
            )
