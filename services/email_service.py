import smtplib
import os
import unicodedata
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.header import Header
import csv
import xml.etree.ElementTree as ET
import tempfile
from datetime import datetime
import codecs

from config import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, EMAIL_FROM

def normalize_text(text):
    """Normaliza el texto para evitar problemas de codificación"""
    if text is None:
        return ""
    text = text.replace('\xa0', ' ')
    text = unicodedata.normalize('NFC', text)
    return text

def send_email(to_email, subject, body, attachments=None):
    """Envía un correo electrónico con codificación adecuada para caracteres españoles"""
    msg = MIMEMultipart()
    msg['From'] = EMAIL_FROM
    msg['To'] = to_email
    msg['Subject'] = Header(subject, 'utf-8')
    
    msg.attach(MIMEText(body, 'html', 'utf-8'))
    
    if attachments:
        for filename, content in attachments.items():
            if isinstance(content, str):
                content = content.encode('utf-8')
            
            attachment = MIMEApplication(content, Name=filename)
            attachment['Content-Disposition'] = f'attachment; filename="{filename}"'
            msg.attach(attachment)
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error de correo: {e}")
        print(f"- Servidor SMTP: {SMTP_SERVER}")
        print(f"- Puerto SMTP: {SMTP_PORT}")
        print(f"- Destinatario: {to_email}")
        return False

def send_welcome_email(to_email, user_name):
    """Envía un correo de bienvenida con formato adecuado para español"""
    subject = "Bienvenido a YALA"
    
    body = f"""
    <html>
    <body>
        <h2>Bienvenido a YALA, {user_name}!</h2>
        <p>Tu cuenta ha sido creada exitosamente.</p>
        <p>Ahora puedes comenzar a administrar tus cuentas y realizar transacciones.</p>
        <p>Gracias por elegir nuestro servicio!</p>
        <br>
        <p>Saludos cordiales,<br>El Equipo de YALA</p>
    </body>
    </html>
    """
    
    return send_email(to_email, subject, body)

def send_transaction_notification(to_email, user_name, transaction, source_currency, dest_currency, is_sender=True):
    action = "enviado" if is_sender else "recibido"
    amount = transaction.source_amount if is_sender else transaction.destination_amount
    currency = source_currency if is_sender else dest_currency
    
    subject = f"Notificación de Transacción - {action.capitalize()} {amount} {currency}"
    body = f"""
    <html>
    <body>
        <h2>Notificación de Transacción</h2>
        <p>Estimado/a {user_name},</p>
        <p>Has {action} una transacción:</p>
        <ul>
            <li>Monto: {amount} {currency}</li>
            <li>Fecha: {transaction.timestamp}</li>
            <li>Descripción: {transaction.description or 'Sin descripción'}</li>
        </ul>
        <p>¡Gracias por usar nuestro servicio!</p>
        <br>
        <p>Saludos cordiales,<br>El Equipo de YALA</p>
    </body>
    </html>
    """
    return send_email(to_email, subject, body)

def create_csv_export(user, account, transactions):
    with tempfile.NamedTemporaryFile(delete=False, mode='w', newline='', suffix='.csv') as f:
        writer = csv.writer(f)
        writer.writerow(['Estado de Cuenta'])
        writer.writerow([])
        writer.writerow(['Usuario', user.full_name])
        writer.writerow(['Correo', user.email])
        writer.writerow(['ID de Cuenta', account.id])
        writer.writerow(['Moneda', account.currency.code])
        writer.writerow(['Saldo', account.balance])
        writer.writerow(['Fecha de Generación', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow([])
        writer.writerow(['ID Transacción', 'Fecha', 'Descripción', 'Monto', 'Tipo'])
        
        for transaction in transactions:
            if transaction.source_account_id == account.id:
                amount = -transaction.source_amount
                tx_type = 'Saliente'
            else:
                amount = transaction.destination_amount
                tx_type = 'Entrante'
                
            writer.writerow([
                transaction.id,
                transaction.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                transaction.description or '',
                amount,
                tx_type
            ])
    
    with open(f.name, 'r') as f:
        content = f.read()
    
    os.unlink(f.name)
    return content

def create_xml_export(user, account, transactions):
    root = ET.Element("EstadoDeCuenta")
    
    user_element = ET.SubElement(root, "Usuario")
    ET.SubElement(user_element, "Nombre").text = user.full_name
    ET.SubElement(user_element, "Correo").text = user.email
    
    account_element = ET.SubElement(root, "Cuenta")
    ET.SubElement(account_element, "ID").text = str(account.id)
    ET.SubElement(account_element, "Moneda").text = account.currency.code
    ET.SubElement(account_element, "Saldo").text = str(account.balance)
    
    generated = ET.SubElement(root, "FechaGeneracion")
    generated.text = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    transactions_element = ET.SubElement(root, "Transacciones")
    for transaction in transactions:
        tx_element = ET.SubElement(transactions_element, "Transaccion")
        ET.SubElement(tx_element, "ID").text = str(transaction.id)
        ET.SubElement(tx_element, "Fecha").text = transaction.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        ET.SubElement(tx_element, "Descripcion").text = transaction.description or ''
        
        if transaction.source_account_id == account.id:
            ET.SubElement(tx_element, "Monto").text = str(-transaction.source_amount)
            ET.SubElement(tx_element, "Tipo").text = 'Saliente'
        else:
            ET.SubElement(tx_element, "Monto").text = str(transaction.destination_amount)
            ET.SubElement(tx_element, "Tipo").text = 'Entrante'
    
    xml_string = ET.tostring(root, encoding='utf-8', method='xml')
    return xml_string

def send_account_statement(to_email, user_name, account, transactions, format='csv'):
    subject = f"Estado de Cuenta - Cuenta en {account.currency.code}"
    body = f"""
    <html>
    <body>
        <h2>Estado de Cuenta</h2>
        <p>Estimado/a {user_name},</p>
        <p>Adjunto encontrarás tu estado de cuenta en formato {format.upper()}.</p>
        <p>¡Gracias por usar nuestro servicio!</p>
        <br>
        <p>Saludos cordiales,<br>El Equipo de YALA</p>
    </body>
    </html>
    """
    
    if format.lower() == 'csv':
        content = create_csv_export(account.user, account, transactions)
        filename = f"estado_cuenta_{account.id}_{datetime.now().strftime('%Y%m%d')}.csv"
    elif format.lower() == 'xml':
        content = create_xml_export(account.user, account, transactions)
        filename = f"estado_cuenta_{account.id}_{datetime.now().strftime('%Y%m%d')}.xml"
    else:
        raise ValueError(f"Formato no soportado: {format}")
    
    attachments = {filename: content}
    return send_email(to_email, subject, body, attachments)
