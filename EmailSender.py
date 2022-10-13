import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


def email_sender(file, name):
    try:
        f = open("email_info.txt", "r")
        data = f.read()
        f.close()
        data = data.split("\n")
        fromaddr = data[0]
        toaddr = data[2]
        msg = MIMEMultipart()

        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = "Alteração do " + name

        body = "\n[Mensagem automática de nova versão BaCen]\n\n Foram identificadas mudanças nos arquivo: " + \
               name + "\n\nAtenciosamente,\nBaCenPixScraper\nhttps://github.com/LucasLaheras/BaCenPixScraper "

        msg.attach(MIMEText(body, 'plain'))

        if os.path.getsize(file) <= 24000000:
            attachment = open(file, 'rb')

            part = MIMEBase('application', 'octet-stream')
            part.set_payload((attachment).read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', "attachment; filename= %s" % (name))

            msg.attach(part)

            attachment.close()

        server = smtplib.SMTP('smtp.outlook.com', 587)
        server.starttls()
        server.login(fromaddr, data[1])
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        server.quit()
        print('Email successfully sent!')
    except:
        print('Error sending email')
