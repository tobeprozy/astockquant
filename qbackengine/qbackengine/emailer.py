import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import Optional, List, Union


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

        # 验证环境变量和参数
        if not all([self.smtp_host, self.smtp_port, self.username, self.password, self.from_addr]):
            raise ValueError("SMTP配置不完整，请提供必要的SMTP参数或设置环境变量")

    def send(self, subject: str, body: str, to_addrs: Optional[str] = None) -> None:
        """
        发送纯文本邮件

        Args:
            subject: 邮件主题
            body: 邮件正文
            to_addrs: 收件人地址，多个地址用逗号分隔
        """
        to_addrs = to_addrs or self.to_addrs
        if not all([self.smtp_host, self.smtp_port, self.username, self.password, self.from_addr, to_addrs]):
            raise RuntimeError('SMTP config incomplete. Set SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_FROM, SMTP_TO')

        msg = MIMEMultipart()
        msg['From'] = self.from_addr
        msg['To'] = to_addrs
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        self._send_message(msg, to_addrs)

    def send_email_with_attachments(
        self, 
        subject: str, 
        body: str, 
        attachments: List[str] = None, 
        to_addrs: Optional[str] = None
    ) -> None:
        """
        发送带附件的邮件

        Args:
            subject: 邮件主题
            body: 邮件正文
            attachments: 附件文件路径列表
            to_addrs: 收件人地址，多个地址用逗号分隔
        """
        to_addrs = to_addrs or self.to_addrs
        if not all([self.smtp_host, self.smtp_port, self.username, self.password, self.from_addr, to_addrs]):
            raise RuntimeError('SMTP配置不完整，请设置必要的SMTP参数')

        # 创建邮件对象
        msg = MIMEMultipart()
        msg['From'] = self.from_addr
        msg['To'] = to_addrs
        msg['Subject'] = subject

        # 添加正文
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        # 添加附件
        if attachments:
            for file_path in attachments:
                if os.path.exists(file_path):
                    try:
                        # 获取文件名
                        file_name = os.path.basename(file_path)
                        
                        # 创建附件对象
                        with open(file_path, 'rb') as f:
                            part = MIMEApplication(f.read(), Name=file_name)
                            
                        # 添加附件头信息
                        part['Content-Disposition'] = f'attachment; filename="{file_name}"'
                        
                        # 附加到邮件
                        msg.attach(part)
                    except Exception as e:
                        raise RuntimeError(f"添加附件 {file_path} 失败: {str(e)}")
                else:
                    raise FileNotFoundError(f"附件文件不存在: {file_path}")

        # 发送邮件
        self._send_message(msg, to_addrs)

    def _send_message(self, msg: MIMEMultipart, to_addrs: str) -> None:
        """
        内部方法：发送邮件消息

        Args:
            msg: 邮件消息对象
            to_addrs: 收件人地址
        """
        # 连接SMTP服务器
        if self.use_tls:
            server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=30)
        else:
            server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30)
            server.starttls()

        try:
            # 登录并发送邮件
            server.login(self.username, self.password)
            # 确保to_addrs是列表格式
            recipients = [addr.strip() for addr in to_addrs.split(',')]
            server.sendmail(self.from_addr, recipients, msg.as_string())
        except Exception as e:
            raise RuntimeError(f"发送邮件失败: {str(e)}")
        finally:
            # 关闭连接
            server.quit()
