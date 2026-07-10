# app/services/email_service.py
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from app.config import settings
# import logging

# logger = logging.getLogger(__name__)


# class EmailService:
#     def __init__(self):
#         # Prefer configuration from app.config.settings (pydantic)
#         self.host = getattr(settings, "EMAIL_HOST", "smtp.gmail.com")
#         configured_port = getattr(settings, "EMAIL_PORT", None)
#         self.use_tls = getattr(settings, "MAIL_TLS", True)
#         self.use_ssl = getattr(settings, "MAIL_SSL", False)

#         # Determine port: prefer explicit config, otherwise choose standard ports
#         if configured_port:
#             try:
#                 self.port = int(configured_port)
#             except Exception:
#                 self.port = 465 if self.use_ssl else 587
#         else:
#             self.port = 465 if self.use_ssl else 587

#         # Reconcile common port/flag mismatches
#         if self.port == 465 and not self.use_ssl:
#             logger.warning("Port 465 normally requires SSL; enabling use_ssl=True")
#             self.use_ssl = True
#         if self.port == 587 and self.use_ssl:
#             logger.warning("Port 587 normally uses STARTTLS; disabling use_ssl and enabling TLS")
#             self.use_ssl = False
#             self.use_tls = True

#         self.username = getattr(settings, "EMAIL_USERNAME", None)
#         self.password = getattr(settings, "EMAIL_PASSWORD", None)
#         self.from_email = getattr(settings, "EMAIL_FROM", None)
#         self.from_name = getattr(settings, "EMAIL_FROM_NAME", "GPS Tracker")

#         # Log configuration (do not log passwords)
#         logger.info(f"Email service initialized with host: {self.host}:{self.port}")
#         logger.info(f"Username: {self.username}")
#         logger.info(f"From: {self.from_name} <{self.from_email}>")
#         logger.info(f"TLS: {self.use_tls}, SSL: {self.use_ssl}")

#         # Validate configuration
#         if not all([self.host, self.port, self.username, self.password, self.from_email]):
#             logger.error("Missing email configuration in settings! Check .env and app.config")

#     async def send_email(self, to_email: str, subject: str, body: str, is_html: bool = False) -> bool:
#         """Send email to recipient"""
#         try:
#             logger.info(f"Attempting to send email to: {to_email}")
#             logger.info(f"Subject: {subject}")
            
#             # Create message
#             msg = MIMEMultipart()
#             msg['From'] = f"{self.from_name} <{self.from_email}>"
#             msg['To'] = to_email
#             msg['Subject'] = subject

#             # Attach body
#             if is_html:
#                 msg.attach(MIMEText(body, 'html'))
#                 logger.debug("HTML email body attached")
#             else:
#                 msg.attach(MIMEText(body, 'plain'))
#                 logger.debug("Plain text email body attached")

#             # Connect to server
#             logger.info(f"Connecting to SMTP server: {self.host}:{self.port}")

#             # Use a timeout to avoid hanging
#             timeout = 20

#             # Attempt primary connection mode, with a fallback to the alternate mode
#             server = None
#             primary_mode = "SSL" if self.use_ssl else "STARTTLS" if self.use_tls else "PLAIN"
#             logger.info("Primary SMTP mode: %s", primary_mode)

#             try:
#                 if self.use_ssl:
#                     logger.info("Using SMTP_SSL connection")
#                     server = smtplib.SMTP_SSL(self.host, self.port, timeout=timeout)
#                 else:
#                     server = smtplib.SMTP(self.host, self.port, timeout=timeout)
#                     server.ehlo()
#                     if self.use_tls:
#                         server.starttls()
#                         server.ehlo()
#                         logger.info("STARTTLS negotiated")
#             except Exception as e_primary:
#                 logger.warning("Primary SMTP connection (%s) failed: %s", primary_mode, e_primary)
#                 # Try alternate mode once
#                 try:
#                     alt_mode = "STARTTLS" if self.use_ssl else "SSL"
#                     logger.info("Attempting alternate SMTP mode: %s", alt_mode)
#                     if self.use_ssl:
#                         # primary was SSL, try STARTTLS
#                         server = smtplib.SMTP(self.host, 587, timeout=timeout)
#                         server.ehlo()
#                         server.starttls()
#                         server.ehlo()
#                     else:
#                         # primary was STARTTLS or PLAIN, try SSL
#                         server = smtplib.SMTP_SSL(self.host, 465, timeout=timeout)
#                     logger.info("Alternate SMTP mode %s connected successfully", alt_mode)
#                 except Exception as e_alt:
#                     logger.error("Alternate SMTP connection failed: %s", e_alt)
#                     raise
            
#             # Login
#             logger.info("Logging into SMTP server...")
#             server.login(self.username, self.password)
#             logger.info("Login successful")
            
#             # Send email
#             logger.info("Sending email...")
#             server.send_message(msg)
#             logger.info(f"Email sent successfully to {to_email}")
            
#             # Quit
#             server.quit()
#             logger.info("SMTP connection closed")
            
#             return True
            
#         except smtplib.SMTPAuthenticationError as e:
#             logger.error(f"SMTP Authentication Error: {e}")
#             logger.error("Check your email username and password (App Password for Gmail)")
#             return False
#         except (ConnectionRefusedError, OSError) as e:
#             logger.error(f"Connection error when connecting to SMTP server: {e}")
#             return False
#         except smtplib.SMTPException as e:
#             logger.error(f"SMTP Error: {e}")
#             return False
#         except Exception as e:
#             logger.error(f"Failed to send email: {e}")
#             logger.exception("Full traceback:")
#             return False

#     async def send_password_reset_email(self, to_email: str, reset_token: str, user_name: str = None):
#         """Send password reset email with token"""
#         # For testing, use localhost frontend URL
#         reset_link = f"http://localhost:3000/reset-password?token={reset_token}"
        
#         html_content = f"""
#         <!DOCTYPE html>
#         <html>
#         <head>
#             <meta charset="UTF-8">
#             <title>Password Reset</title>
#             <style>
#                 body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
#                 .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
#                 .header {{ background-color: #4CAF50; color: white; padding: 10px; text-align: center; }}
#                 .content {{ padding: 20px; background-color: #f9f9f9; }}
#                 .button {{ display: inline-block; padding: 10px 20px; background-color: #4CAF50; 
#                          color: white; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
#                 .token {{ background-color: #eee; padding: 10px; border-radius: 5px; 
#                          font-family: monospace; margin: 10px 0; }}
#                 .footer {{ margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd; 
#                          font-size: 12px; color: #777; }}
#             </style>
#         </head>
#         <body>
#             <div class="container">
#                 <div class="header">
#                     <h1>Password Reset Request</h1>
#                 </div>
#                 <div class="content">
#                     <p>Hello {user_name or 'User'},</p>
#                     <p>You have requested to reset your password for your GPS Tracker account.</p>
#                     <p>Click the button below to reset your password:</p>
#                     <p><a href="{reset_link}" class="button">Reset Password</a></p>
#                     <p>Or copy and paste this link in your browser:</p>
#                     <p><code>{reset_link}</code></p>
#                     <p>Your reset token is:</p>
#                     <div class="token">{reset_token}</div>
#                     <p><strong>This link will expire in 15 minutes.</strong></p>
#                     <p>If you didn't request a password reset, please ignore this email or contact support.</p>
#                 </div>
#                 <div class="footer">
#                     <p>Best regards,<br>{self.from_name}<br>GPS Tracker System</p>
#                     <p>This is an automated message, please do not reply to this email.</p>
#                 </div>
#             </div>
#         </body>
#         </html>
#         """
        
#         plain_text = f"""
#         Password Reset Request
        
#         Hello {user_name or 'User'},
        
#         You have requested to reset your password for your GPS Tracker account.
        
#         To reset your password, click this link:
#         {reset_link}
        
#         Or use this token: {reset_token}
        
#         This link will expire in 15 minutes.
        
#         If you didn't request this, please ignore this email.
        
#         Best regards,
#         {self.from_name}
#         GPS Tracker System
#         """
        
#         subject = "GPS Tracker - Password Reset Request"
        
#         # Try HTML first, fallback to plain text
#         success = await self.send_email(to_email, subject, html_content, is_html=True)

#         if not success:
#             logger.warning("HTML email failed, trying plain text...")
#             success = await self.send_email(to_email, subject, plain_text, is_html=False)

#         return success

#     async def send_password_reset_otp(self, to_email: str, otp: str, user_name: str = None, expiry_minutes: int = 10):
#         """Send OTP code for password reset"""
#         subject = "GPS Tracker - Password Reset Code"

#         html_content = f"""
#         <html>
#         <body>
#             <p>Hi {user_name or 'User'},</p>
#             <p>We received a request to reset your password. Your verification code is:</p>
#             <h2>{otp}</h2>
#             <p>Please enter this code on the password reset page to complete the process. If you did not request a password reset, please ignore this email or contact support if you have concerns.</p>
#             <p>For security reasons, this code will expire in {expiry_minutes} minutes.</p>
#             <p>Best regards,<br>{self.from_name}<br>GPS Tracker System</p>
#             <p><small>This is an automated message, please do not reply to this email.</small></p>
#         </body>
#         </html>
#         """

#         plain_text = f"Your verification code is: {otp}\nThis code will expire in {expiry_minutes} minutes."

#         # Try HTML first, fallback to plain text
#         success = await self.send_email(to_email, subject, html_content, is_html=True)
#         if not success:
#             logger.warning("OTP HTML email failed, trying plain text...")
#             success = await self.send_email(to_email, subject, plain_text, is_html=False)

#         return success

# # Create global instance
# email_service = EmailService()

# app/services/email_service.py

import smtplib
import logging
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        """
        Email provider selection based on ENV:
        - EMAIL_PROVIDER=smtp   -> Local (Gmail SMTP)
        - EMAIL_PROVIDER=resend -> Render (Resend API)
        """

        # Decide provider (default = smtp for safety)
        self.provider = getattr(settings, "EMAIL_PROVIDER", "smtp").lower()

        # Common
        self.from_email = getattr(settings, "EMAIL_FROM", None)
        self.from_name = getattr(settings, "EMAIL_FROM_NAME", "GPS Tracker")

        # ===== SMTP CONFIG (LOCAL) =====
        self.smtp_host = getattr(settings, "EMAIL_HOST", "smtp.gmail.com")
        self.smtp_port = int(getattr(settings, "EMAIL_PORT", 465))
        self.smtp_user = getattr(settings, "EMAIL_USERNAME", None)
        self.smtp_password = getattr(settings, "EMAIL_PASSWORD", None)
        self.use_tls = getattr(settings, "MAIL_TLS", True)
        self.use_ssl = getattr(settings, "MAIL_SSL", False)

        # ===== RESEND CONFIG (RENDER) =====
        self.resend_api_key = getattr(settings, "RESEND_API_KEY", None)

        logger.info(f"Email provider selected: {self.provider}")
        logger.info(f"From: {self.from_name} <{self.from_email}>")

    # ==========================================================
    # PUBLIC METHOD (used everywhere in project)
    # ==========================================================
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        is_html: bool = True
    ) -> bool:
        """
        Unified email sender
        Automatically routes to SMTP or Resend
        """

        try:
            if self.provider == "resend":
                return await self._send_via_resend(to_email, subject, body)
            else:
                return await self._send_via_smtp(to_email, subject, body, is_html)

        except Exception as e:
            logger.error(f"Email send failed: {e}", exc_info=True)
            return False

    # ==========================================================
    # SMTP (LOCAL – GMAIL)
    # ==========================================================
    async def _send_via_smtp(
        self,
        to_email: str,
        subject: str,
        body: str,
        is_html: bool
    ) -> bool:

        try:
            msg = MIMEMultipart()
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email
            msg["Subject"] = subject

            msg.attach(MIMEText(body, "html" if is_html else "plain"))

            logger.info("Connecting to SMTP server...")

            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=20)
            else:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=20)
                if self.use_tls:
                    server.starttls()

            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)
            server.quit()

            logger.info(f"SMTP email sent to {to_email}")
            return True

        except Exception as e:
            logger.error(f"SMTP email failed: {e}", exc_info=True)
            return False

    # ==========================================================
    # RESEND (RENDER – PRODUCTION)
    # ==========================================================
    async def _send_via_resend(
        self,
        to_email: str,
        subject: str,
        html_body: str
    ) -> bool:

        try:
            url = "https://api.resend.com/emails"
            headers = {
                "Authorization": f"Bearer {self.resend_api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "from": f"{self.from_name} <{self.from_email}>",
                "to": [to_email],
                "subject": subject,
                "html": html_body
            }

            response = requests.post(url, json=payload, headers=headers, timeout=15)

            if response.status_code in (200, 201):
                logger.info(f"Resend email sent to {to_email}")
                return True

            logger.error(f"Resend failed: {response.text}")
            return False

        except Exception as e:
            logger.error(f"Resend exception: {e}", exc_info=True)
            return False

    # ==========================================================
    # PASSWORD RESET EMAIL (LINK)
    # ==========================================================
    async def send_password_reset_email(
        self,
        to_email: str,
        reset_token: str,
        user_name: str = None
    ) -> bool:

        reset_link = f"http://localhost:3000/reset-password?token={reset_token}"

        subject = "GPS Tracker - Password Reset"

        html_content = f"""
        <html>
        <body>
            <p>Hello {user_name or 'User'},</p>
            <p>You requested a password reset.</p>
            <p>
                <a href="{reset_link}" style="padding:10px 15px;background:#4CAF50;color:#fff;text-decoration:none;">
                    Reset Password
                </a>
            </p>
            <p>This link will expire in 15 minutes.</p>
            <br/>
            <p>Regards,<br>{self.from_name}</p>
        </body>
        </html>
        """

        return await self.send_email(to_email, subject, html_content, is_html=True)

    # ==========================================================
    # PASSWORD RESET OTP
    # ==========================================================
    async def send_password_reset_otp(
        self,
        to_email: str,
        otp: str,
        user_name: str = None,
        expiry_minutes: int = 10
    ) -> bool:

        subject = "GPS Tracker - Password Reset OTP"

        html_content = f"""
        <html>
        <body>
            <p>Hi {user_name or 'User'},</p>
            <p>Your password reset OTP is:</p>
            <h2>{otp}</h2>
            <p>This OTP expires in {expiry_minutes} minutes.</p>
            <br/>
            <p>Regards,<br>{self.from_name}</p>
        </body>
        </html>
        """

        return await self.send_email(to_email, subject, html_content, is_html=True)


# Global instance
email_service = EmailService()
