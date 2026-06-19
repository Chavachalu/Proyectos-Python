import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime

def enviar_reporte_cobranza():
    # 1. Configuración de credenciales y servidor (Ejemplo con Outlook/Office365)
    smtp_server = "smtp.office365.com"
    smtp_port = 587
    sender_email = "tu_correo_mis@empresa.com"
    sender_password = "TuPasswordSeguro123"  # En producción se usan variables de entorno
    
    # Destinatarios
    to_email = "gerente_cobranza@empresa.com"
    cc_email = "director_operaciones@empresa.com"
    
    # 2. Creación del mensaje
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Cc'] = cc_email
    
    fecha_hoy = datetime.now().strftime('%Y-%m-%d')
    msg['Subject'] = f"REPORTE MIS: Rendimiento de Cobranza y Cuentas Críticas - {fecha_hoy}"
    
    # Cuerpo del correo en formato HTML para que se vea profesional
    cuerpo_html = """
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color: #2C3E50;">Control de Gestión y Analítica de Cobranza (MIS)</h2>
        <p>Estimado equipo directivo,</p>
        <p>Comparto el reporte automatizado con el cierre de métricas de cobranza correspondiente al día de hoy.</p>
        
        <table style="border-collapse: collapse; width: 100%; max-width: 500px;">
          <tr style="background-color: #2C3E50; color: white;">
            <th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Indicador Clave</th>
            <th style="padding: 8px; text-align: right; border: 1px solid #ddd;">Estado</th>
          </tr>
          <tr>
            <td style="padding: 8px; border: 1px solid #ddd;">Reporte Ejecutivo General</td>
            <td style="padding: 8px; border: 1px solid #ddd; text-align: right; color: green; font-weight: bold;">Actualizado</td>
          </tr>
          <tr>
            <td style="padding: 8px; border: 1px solid #ddd;">Top 100 Clientes Críticos</td>
            <td style="padding: 8px; border: 1px solid #ddd; text-align: right; color: red; font-weight: bold;">Mora Tardía</td>
          </tr>
        </table>
        
        <p style="margin-top: 20px;">El archivo adjunto contiene el desglose por buckets de mora y efectividad operativa.</p>
        <p>Quedo a su disposición para cualquier duda o análisis adicional.</p>
        <br>
        <hr style="border: 0; border-top: 1px solid #ccc;">
        <p style="font-size: 11px; color: #7F8C8D;">Este es un correo generado de forma automática por el pipeline del sistema MIS.</p>
      </body>
    </html>
    """
    msg.attach(MIMEText(cuerpo_html, 'html'))
    
    # 3. Adjuntar el archivo Excel generado en el paso 04
    file_path = "reportes/reporte_performance_cobranza.xlsx"
    
    if os.path.exists(file_path):
        filename = os.path.basename(file_path)
        with open(file_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )
        msg.attach(part)
    else:
        print(f"Error: No se encontró el archivo en {file_path}")
        return

    # 4. Conexión segura al servidor y envío
    try:
        # Combinar destinatarios para el envío técnico
        all_recipients = [to_email] + [cc_email]
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Cifrado de seguridad TLS
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, all_recipients, msg.as_string())
        server.quit()
        print("¡Reporte enviado exitosamente por correo!")
    except Exception as e:
        print(f"Hubo un error al enviar el correo: {e}")

if __name__ == "__main__":
    enviar_reporte_cobranza()
