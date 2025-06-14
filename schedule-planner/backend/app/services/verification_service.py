# Author: 唐震
import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import logging
from ..models.user import get_db_connection, store_verification_code, get_verification_code, invalidate_verification_code
from ..config import Config

def generate_verification_code():
    """生成6位数字验证码"""
    return ''.join(random.choices(string.digits, k=Config.VERIFICATION_CODE_LENGTH))

def send_verification_code(email, code_type="bind_phone"):
    """发送验证码（统一入口函数）"""
    try:
        logging.info(f"Sending verification code to {email}, type: {code_type}")
        
        # 生成验证码
        code = generate_verification_code()
        logging.info(f"Generated verification code: {code}")
        
        # 保存到数据库
        store_verification_code(email, code)
        logging.info("Verification code stored in database")
        
        # 发送邮件
        success, message = send_email_verification_code(email, code, code_type)
        
        if success:
            logging.info(f"Verification code sent successfully to {email}")
            return True, message
        else:
            logging.error(f"Failed to send verification code: {message}")
            return False, message
        
    except Exception as e:
        logging.error(f"Error in send_verification_code: {str(e)}")
        return False, f"发送验证码失败: {str(e)}"

def send_email_verification_code(email, code, email_type="bind_phone"):
    """发送邮箱验证码"""
    try:
        # 从配置文件的EMAIL_CONFIG字典获取邮件设置
        email_config = getattr(Config, 'EMAIL_CONFIG', {})
        
        smtp_server = email_config.get('smtp_server', 'smtp.qq.com')
        smtp_port = email_config.get('smtp_port', 587)
        sender_email = email_config.get('sender_email')
        sender_password = email_config.get('sender_password')
        sender_name = email_config.get('sender_name', 'Schedule Planner')
        
        logging.info(f"Email config: {smtp_server}:{smtp_port}, sender: {sender_email}")
        
        # 检查邮件配置是否完整
        if not sender_email or not sender_password:
            logging.warning("Email configuration incomplete, using test mode")
            return True, f"邮件配置不完整，测试模式验证码：{code}"
        
        # 根据类型设置邮件内容
        subject, content = get_email_content(code, email_type, sender_name)
        
        # 创建邮件
        msg = MIMEMultipart()
        msg['From'] = f"{sender_name} <{sender_email}>"
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(content, 'html', 'utf-8'))
        
        # 发送邮件
        logging.info(f"Connecting to SMTP server {smtp_server}:{smtp_port}...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, msg.as_string())
        server.quit()
        
        logging.info(f"Email sent successfully to {email}")
        return True, "验证码发送成功"
        
    except smtplib.SMTPAuthenticationError as e:
        logging.error(f"SMTP Authentication Error: {str(e)}")
        return True, f"邮件认证失败，测试模式验证码：{code}"
    except smtplib.SMTPException as e:
        logging.error(f"SMTP Error: {str(e)}")
        return True, f"邮件发送失败，测试模式验证码：{code}"
    except Exception as e:
        logging.error(f"Error sending email: {str(e)}")
        return True, f"邮件发送异常，测试模式验证码：{code}"

def get_email_content(code, email_type, sender_name):
    """根据邮件类型生成邮件内容"""
    if email_type == "reset_password":
        subject = "密码重置验证码"
        content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #409EFF; margin: 0;">{sender_name}</h1>
            </div>
            <div style="background-color: #f8f9fa; padding: 30px; border-radius: 8px;">
                <h2 style="color: #333; text-align: center; margin-top: 0;">密码重置验证码</h2>
                <p style="color: #666; font-size: 16px; line-height: 1.6;">您正在重置密码，验证码为：</p>
                <div style="text-align: center; margin: 30px 0;">
                    <span style="display: inline-block; font-size: 32px; font-weight: bold; color: #409EFF; 
                                 background-color: #fff; padding: 15px 30px; border-radius: 6px; 
                                 border: 2px solid #409EFF; letter-spacing: 8px;">{code}</span>
                </div>
                <p style="color: #666; font-size: 14px;">验证码{Config.VERIFICATION_CODE_EXPIRY_MINUTES}分钟内有效，请勿泄露给他人。</p>
                <p style="color: #999; font-size: 12px;">如果您没有进行此操作，请忽略此邮件。</p>
            </div>
            <div style="text-align: center; margin-top: 20px;">
                <p style="color: #999; font-size: 12px;">此邮件由 {sender_name} 系统自动发送，请勿回复。</p>
            </div>
        </div>
        """
    else:
        subject = "绑定手机号验证码"
        content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #409EFF; margin: 0;">{sender_name}</h1>
            </div>
            <div style="background-color: #f8f9fa; padding: 30px; border-radius: 8px;">
                <h2 style="color: #333; text-align: center; margin-top: 0;">绑定手机号验证码</h2>
                <p style="color: #666; font-size: 16px; line-height: 1.6;">您正在绑定手机号，验证码为：</p>
                <div style="text-align: center; margin: 30px 0;">
                    <span style="display: inline-block; font-size: 32px; font-weight: bold; color: #409EFF; 
                                 background-color: #fff; padding: 15px 30px; border-radius: 6px; 
                                 border: 2px solid #409EFF; letter-spacing: 8px;">{code}</span>
                </div>
                <p style="color: #666; font-size: 14px;">验证码{Config.VERIFICATION_CODE_EXPIRY_MINUTES}分钟内有效，请勿泄露给他人。</p>
                <p style="color: #999; font-size: 12px;">如果您没有进行此操作，请忽略此邮件。</p>
            </div>
            <div style="text-align: center; margin-top: 20px;">
                <p style="color: #999; font-size: 12px;">此邮件由 {sender_name} 系统自动发送，请勿回复。</p>
            </div>
        </div>
        """
    
    return subject, content

def verify_code(email, code):
    """验证验证码"""
    try:
        logging.info(f"Verifying code {code} for email {email}")
        
        # 获取存储的验证码
        stored_code = get_verification_code(email)
        
        if not stored_code:
            logging.warning(f"No verification code found for email {email}")
            return False, "验证码不存在或已过期"
        
        # 验证验证码
        if stored_code != code:
            logging.warning(f"Invalid verification code for email {email}")
            return False, "验证码错误"
        
        # 验证成功，删除验证码
        invalidate_verification_code(email, code)
        logging.info(f"Verification code verified and invalidated for email {email}")
        
        return True, "验证码验证成功"
        
    except Exception as e:
        logging.error(f"Error verifying code: {str(e)}")
        return False, f"验证码验证失败: {str(e)}"

def reset_user_password(email, code, new_password):
    """重置用户密码"""
    from ..models.user import get_user_by_phone_or_email, hash_password
    from ..services.auth_service import get_user_by_id
    
    try:
        # 验证验证码
        success, message = verify_code(email, code)
        if not success:
            return False, message
        
        # 获取用户
        user = get_user_by_phone_or_email(email=email)
        if not user:
            return False, "用户不存在"
        
        # 验证新密码
        if not new_password or len(new_password) < 6:
            return False, "新密码长度至少6位"
        
        # 更新密码
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            password_hash = hash_password(new_password)
            cursor.execute('''
                UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (password_hash, user['id']))
            
            if cursor.rowcount == 0:
                return False, "密码更新失败"
            
            conn.commit()
            logging.info(f"Password reset successfully for user {user['id']}")
            return True, "密码重置成功"
            
        finally:
            conn.close()
            
    except Exception as e:
        logging.error(f"Error resetting password: {str(e)}")
        return False, f"密码重置失败: {str(e)}"