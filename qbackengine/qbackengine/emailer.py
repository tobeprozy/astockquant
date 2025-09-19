import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional


class SmtpEmailer:
    def __init__(
        self,
        smtp_host: Optional[str] = None,
        smtp_port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        use_tls: bool = True,
        from_addr: Optional[str] = None,
        to_addrs: Optional[str] = None,
    ) -> None:
        self.smtp_host = smtp_host or os.getenv('SMTP_HOST')
        self.smtp_port = int(smtp_port or os.getenv('SMTP_PORT', '587'))
        self.username = username or os.getenv('SMTP_USER')
        self.password = password or os.getenv('SMTP_PASS')
        self.use_tls = use_tls if use_tls is not None else os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
        self.from_addr = from_addr or os.getenv('SMTP_FROM') or self.username
        self.to_addrs = to_addrs or os.getenv('SMTP_TO')

        
    def send(self, subject: str, body: str, to_addrs: Optional[str] = None) -> None:
        to_addrs = to_addrs or self.to_addrs
        if not all([self.smtp_host, self.smtp_port, self.username, self.password, self.from_addr, to_addrs]):
            raise RuntimeError('SMTP config incomplete. Set SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_FROM, SMTP_TO')

        msg = MIMEMultipart()
        msg['From'] = self.from_addr
        msg['To'] = to_addrs
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        if self.use_tls:
            server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=30)
        else:
            server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) 

        try:
            server.login(self.username, self.password)
            server.sendmail(self.from_addr, to_addrs.split(','), msg.as_string())
        finally:
            server.quit()
