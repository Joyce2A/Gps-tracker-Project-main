# debug_email.py
import os
import sys
import asyncio
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

print("=" * 60)
print("EMAIL DEBUGGER - GPS TRACKER PROJECT")
print("=" * 60)

# 1. Check current directory
print("\n1. CURRENT DIRECTORY STRUCTURE:")
current_dir = os.getcwd()
print(f"Working directory: {current_dir}")

# List files
for root, dirs, files in os.walk(current_dir):
    level = root.replace(current_dir, '').count(os.sep)
    indent = ' ' * 2 * level
    print(f'{indent}{os.path.basename(root)}/')
    subindent = ' ' * 2 * (level + 1)
    for file in files[:10]:  # Show first 10 files
        if file.endswith('.py') or file.endswith('.env'):
            print(f'{subindent}{file}')

# 2. Check .env file
print("\n2. CHECKING .ENV FILE:")
env_path = os.path.join(current_dir, '.env')
if os.path.exists(env_path):
    print(f"✅ .env file found at: {env_path}")
    
    # Read and display email config (mask password)
    with open(env_path, 'r') as f:
        env_content = f.read()
        lines = env_content.split('\n')
        email_lines = [line for line in lines if 'EMAIL' in line or 'MAIL' in line]
        
        for line in email_lines:
            if 'PASSWORD' in line:
                parts = line.split('=')
                if len(parts) == 2:
                    print(f"   {parts[0]}=[HIDDEN] ({len(parts[1])} chars)")
            else:
                print(f"   {line}")
else:
    print(f"❌ .env file NOT found at: {env_path}")

# 3. Test SMTP connection directly
print("\n3. TESTING SMTP CONNECTION DIRECTLY:")

# Load environment variables
load_dotenv()

EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM")

print(f"   Host: {EMAIL_HOST}")
print(f"   Port: {EMAIL_PORT}")
print(f"   Username: {EMAIL_USERNAME}")
print(f"   From: {EMAIL_FROM}")
print(f"   Password set: {'YES' if EMAIL_PASSWORD else 'NO'}")

# Test SMTP connection
def test_smtp():
    try:
        print(f"\n   Connecting to {EMAIL_HOST}:{EMAIL_PORT}...")
        
        # Test without auth first
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=10)
        server.ehlo()
        
        # Try STARTTLS
        if EMAIL_PORT == 587:
            print("   Testing STARTTLS...")
            server.starttls()
            server.ehlo()
            print("   ✅ STARTTLS successful")
        
        # Try login
        if EMAIL_USERNAME and EMAIL_PASSWORD:
            print("   Testing login...")
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            print("   ✅ Login successful")
            
            # Try to send a test email
            print("   Testing email send...")
            msg = MIMEText("Test email from debugger")
            msg['From'] = EMAIL_FROM
            msg['To'] = "test@example.com"
            msg['Subject'] = "SMTP Test"
            
            # Don't actually send, just check if we can
            print("   ✅ SMTP connection and auth successful")
            
        server.quit()
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"   ❌ Authentication failed: {e}")
        print("   ⚠️  Common causes:")
        print("      - Using regular Gmail password (need App Password)")
        print("      - 2-Step Verification not enabled")
        print("      - Incorrect username/password")
        return False
    except smtplib.SMTPException as e:
        print(f"   ❌ SMTP error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return False

# Run SMTP test
smtp_ok = test_smtp()

# 4. Check FastAPI email service
print("\n4. CHECKING FASTAPI EMAIL SERVICE:")
try:
    # Add to path
    sys.path.append(current_dir)
    
    from app.services.email_service import email_service
    
    print(f"   Email service imported")
    print(f"   Service host: {email_service.host}")
    print(f"   Service username: {email_service.username}")
    
    # Test sending email
    async def test_send():
        print("\n   Testing email send via service...")
        test_email = input("   Enter your email to test: ").strip()
        
        if test_email:
            print(f"   Sending test to: {test_email}")
            success = await email_service.send_email(
                test_email,
                "GPS Tracker - Debug Test",
                "This is a test email from the debugger.",
                is_html=False
            )
            
            if success:
                print(f"   Email service reports SUCCESS")
                print(f"   Check inbox (and spam folder) of: {test_email}")
            else:
                print(f"   Email service reports FAILURE")
                print(f"   Check server logs for detailed error")
        
    # Run async test
    if smtp_ok:
        asyncio.run(test_send())
    
except ImportError as e:
    print(f"    Cannot import email service: {e}")
    print("   Make sure you have app/services/email_service.py")
except Exception as e:
    print(f"    Error: {e}")

print("\n" + "=" * 60)
print("DEBUG COMPLETE")
print("=" * 60)

# 5. Quick fixes to try
print("\n5. QUICK FIXES TO TRY:")
print("   a) Use Google App Password, not regular password")
print("   b) Enable 'Less secure app access' (if not using 2FA)")
print("   c) Try port 465 with SSL:")
print("      EMAIL_PORT=465")
print("      MAIL_TLS=False")
print("      MAIL_SSL=True")
print("   d) Allow access from: https://accounts.google.com/b/0/DisplayUnlockCaptcha")
print("   e) Check firewall/antivirus blocking port 587/465")