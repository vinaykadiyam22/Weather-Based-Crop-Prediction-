# Optional import
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False
    SendGridAPIClient = None
    Mail = None
    print("[EMAIL] SendGrid not installed - Email notifications will use mock mode")

from config import get_settings

settings = get_settings()

class EmailService:
    def __init__(self):
        self.api_key = settings.sendgrid_api_key
        self.from_email = settings.from_email
        self.sg = SendGridAPIClient(self.api_key) if (SendGridAPIClient and self.api_key) else None
    
    def send_email(self, to_email: str, subject: str, html_content: str, plain_content: str = None):
        """Send email using SendGrid"""
        if not self.sg:
            print(f"[EMAIL MOCK] To: {to_email}, Subject: {subject}")
            print(f"Content: {plain_content or html_content[:100]}...")
            return {"status": "mock", "message": "Email service not configured", "plain_content": plain_content}
        
        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_content,
                plain_text_content=plain_content or ""
            )
            
            response = self.sg.send(message)
            return {
                "status": "sent",
                "status_code": response.status_code,
                "message": "Email sent successfully"
            }
        except Exception as e:
            print(f"Email sending error: {e}")
            return {"status": "error", "message": str(e)}
    
    def send_otp_email(self, to_email: str, otp: str, name: str = "Farmer"):
        """Send OTP verification email"""
        subject = "Your Smart Crop Advisory Login OTP"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px;">
                    <h2 style="color: #2d5016;">Smart Crop Advisory System</h2>
                    <p>Dear {name},</p>
                    <p>Your one-time password (OTP) for login is:</p>
                    <h1 style="color: #4a7c2c; font-size: 36px; letter-spacing: 5px;">{otp}</h1>
                    <p>This OTP is valid for 10 minutes.</p>
                    <p>If you didn't request this OTP, please ignore this email.</p>
                    <hr style="margin: 30px 0;">
                    <p style="color: #666; font-size: 12px;">Smart Crop Advisory System - Empowering Farmers with AI</p>
                </div>
            </body>
        </html>
        """
        plain_content = f"Your OTP is: {otp}. Valid for 10 minutes."
        
        return self.send_email(to_email, subject, html_content, plain_content)
    
    def send_disease_alert(self, to_email: str, disease_name: str, advisory: str, name: str = "Farmer", crop_name: str = None):
        """Send disease detection alert"""
        crop_info = f" ({crop_name})" if crop_name else ""
        subject = f"⚠️ Crop Disease Detected: {disease_name}{crop_info}"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px;">
                    <h2 style="color: #d9534f;">⚠️ Disease Detection Alert</h2>
                    <p>Dear {name},</p>
                    <p>Our AI system has detected <strong>{disease_name}</strong>{f" in {crop_name}" if crop_name else " in your crop image"}.</p>
                    <div style="background-color: #f9f9f9; padding: 20px; border-left: 4px solid #d9534f; margin: 20px 0;">
                        <h3 style="margin-top: 0;">Treatment Advisory</h3>
                        <p style="white-space: pre-line;">{advisory}</p>
                    </div>
                    <p>Please take immediate action to protect your crops.</p>
                    <hr style="margin: 30px 0;">
                    <p style="color: #666; font-size: 12px;">Smart Crop Advisory System</p>
                </div>
            </body>
        </html>
        """
        plain_content = f"Disease Detected: {disease_name}\n\nAdvisory:\n{advisory}"
        
        return self.send_email(to_email, subject, html_content, plain_content)
    
    def send_climate_alert(self, to_email: str, alert_title: str, severity: str, advisory: str, name: str = "Farmer"):
        """Send climate alert"""
        severity_colors = {
            "low": "#5bc0de",
            "medium": "#f0ad4e",
            "high": "#d9534f",
            "critical": "#8b0000"
        }
        color = severity_colors.get(severity.lower(), "#f0ad4e")
        
        subject = f"🌦️ Climate Alert: {alert_title}"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px;">
                    <h2 style="color: {color};">🌦️ Climate Alert</h2>
                    <p>Dear {name},</p>
                    <div style="background-color: {color}22; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="color: {color}; margin-top: 0;">{alert_title}</h3>
                        <p><strong>Severity:</strong> <span style="text-transform: uppercase; color: {color};">{severity}</span></p>
                    </div>
                    <div style="background-color: #f9f9f9; padding: 20px; border-left: 4px solid {color}; margin: 20px 0;">
                        <h3 style="margin-top: 0;">Advisory</h3>
                        <p style="white-space: pre-line;">{advisory}</p>
                    </div>
                    <p>Please take necessary precautions to protect your crops.</p>
                    <hr style="margin: 30px 0;">
                    <p style="color: #666; font-size: 12px;">Smart Crop Advisory System</p>
                </div>
            </body>
        </html>
        """
        plain_content = f"Climate Alert: {alert_title}\nSeverity: {severity}\n\nAdvisory:\n{advisory}"
        
        return self.send_email(to_email, subject, html_content, plain_content)

email_service = EmailService()
