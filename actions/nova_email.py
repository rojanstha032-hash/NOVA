# ============================================
# NOVA - Email System (email.py)
# ============================================
# Send emails, attach files, all by voice!
#
# What you'll learn:
# - SMTP (how emails are sent)
# - MIMEMultipart (building emails with attachments)
# - File handling in Python
# - Security best practices
# ============================================

import smtplib
import os
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class NovaEmail:
    def __init__(self):
        self.email = config.EMAIL_ADDRESS
        self.password = config.EMAIL_PASSWORD
        self.smtp_server = config.EMAIL_SMTP_SERVER
        self.smtp_port = config.EMAIL_SMTP_PORT
        
        # ---- Draft storage ----
        # Stores email being composed by voice
        self.current_draft = {
            "to": None,
            "subject": None,
            "body": None,
            "attachments": []
        }
        
        # ---- Known contacts ----
        # Add your contacts here!
        self.contacts = {
            # "name": "email@example.com"
            # Example:
            # "mom": "mom@gmail.com",
            # "boss": "boss@company.com",
        }
        
        print("✅ Email system ready!")

    # ============================================
    # SEND EMAIL
    # Core email sending function
    # ============================================
    def send_email(self, to, subject, body, attachments=[]):
        try:
            # ---- Build email ----
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = to
            msg['Subject'] = subject
            
            # ---- Add body ----
            msg.attach(MIMEText(body, 'plain'))
            
            # ---- Add attachments ----
            for file_path in attachments:
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename={os.path.basename(file_path)}'
                        )
                        msg.attach(part)
                        print(f"📎 Attached: {file_path}")
                else:
                    print(f"❌ File not found: {file_path}")
            
            # ---- Connect and send ----
            print(f"📧 Sending email to {to}...")
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Secure connection
                server.login(self.email, self.password)
                server.send_message(msg)
            
            print(f"✅ Email sent to {to}!")
            return f"Email sent to {to} successfully!"
            
        except smtplib.SMTPAuthenticationError:
            return "Email authentication failed. Check your email and app password in config.py"
        except smtplib.SMTPException as e:
            return f"Could not send email: {str(e)}"
        except Exception as e:
            return f"Email error: {str(e)}"

    # ============================================
    # ADD CONTACT
    # Save a contact by voice
    # ============================================
    def add_contact(self, name, email):
        self.contacts[name.lower()] = email
        return f"Contact saved! {name} = {email}"

    # ============================================
    # GET CONTACT EMAIL
    # Look up email by name
    # ============================================
    def get_contact_email(self, name):
        return self.contacts.get(name.lower(), None)

    # ============================================
    # PROCESS VOICE COMMAND
    # Handles email commands from voice
    # ============================================
    def process_command(self, command):
        command_lower = command.lower().strip()

        # ---- Send email command ----
        # "send email to mom"
        if "send email" in command_lower or "send an email" in command_lower:
            # Extract recipient
            if "to" in command_lower:
                recipient = command_lower.split("to")[-1].strip()
                
                # Check contacts
                email_address = self.get_contact_email(recipient)
                
                if email_address:
                    self.current_draft["to"] = email_address
                    return f"Okay! Sending email to {recipient}. What's the subject?"
                elif "@" in recipient:
                    self.current_draft["to"] = recipient
                    return f"Okay! Sending email to {recipient}. What's the subject?"
                else:
                    return f"I don't have {recipient} in contacts. Say their email address."
            
            return "Who should I send the email to?"

        # ---- Set subject ----
        if "subject is" in command_lower or "subject:" in command_lower:
            subject = command_lower.replace("subject is", "").replace("subject:", "").strip()
            self.current_draft["subject"] = subject
            return f"Subject set to: {subject}. What's the message?"

        # ---- Set body ----
        if "message is" in command_lower or "body is" in command_lower:
            body = command_lower.replace("message is", "").replace("body is", "").strip()
            self.current_draft["body"] = body
            return f"Message set. Should I send it now or attach a file?"

        # ---- Attach file ----
        if "attach" in command_lower:
            file_name = command_lower.replace("attach", "").strip()
            # Search for file in common locations
            search_paths = [
                os.path.expanduser("~/Desktop"),
                os.path.expanduser("~/Documents"),
                os.path.expanduser("~/Downloads"),
                "data/"
            ]
            
            for path in search_paths:
                full_path = os.path.join(path, file_name)
                if os.path.exists(full_path):
                    self.current_draft["attachments"].append(full_path)
                    return f"Attached {file_name}! Say send now to send."
                    
            return f"Could not find {file_name}. Which folder is it in?"

        # ---- Send now ----
        if "send now" in command_lower or "send it" in command_lower:
            if self.current_draft["to"] and self.current_draft["subject"] and self.current_draft["body"]:
                result = self.send_email(
                    to=self.current_draft["to"],
                    subject=self.current_draft["subject"],
                    body=self.current_draft["body"],
                    attachments=self.current_draft["attachments"]
                )
                # Clear draft after sending
                self.current_draft = {
                    "to": None,
                    "subject": None,
                    "body": None,
                    "attachments": []
                }
                return result
            else:
                missing = []
                if not self.current_draft["to"]:
                    missing.append("recipient")
                if not self.current_draft["subject"]:
                    missing.append("subject")
                if not self.current_draft["body"]:
                    missing.append("message body")
                return f"Still need: {', '.join(missing)}"

        # ---- Cancel draft ----
        if "cancel email" in command_lower:
            self.current_draft = {
                "to": None,
                "subject": None,
                "body": None,
                "attachments": []
            }
            return "Email cancelled!"

        # ---- Add contact ----
        if "add contact" in command_lower or "save contact" in command_lower:
            parts = command_lower.replace("add contact", "").replace("save contact", "").strip().split()
            if len(parts) >= 2:
                name = parts[0]
                email = parts[-1]
                if "@" in email:
                    return self.add_contact(name, email)
            return "Say: add contact name email@example.com"

        return None


# ============================================
# TEST
# Run: py -3.11 actions/email.py
# ============================================
if __name__ == "__main__":
    print("🔱 Testing Nova's Email System...")
    email = NovaEmail()
    
    # Test sending email to yourself
    result = email.send_email(
        to=config.EMAIL_ADDRESS,
        subject="Nova Test Email",
        body="Hello! This is a test email from Nova your AI assistant!"
    )
    print(result)