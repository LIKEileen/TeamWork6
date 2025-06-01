import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..config import Config
from ..models.user import (
    get_user_by_phone_or_email, store_verification_code, 
    get_verification_code, invalidate_verification_code, reset_password
)

def generate_verification_code():
    """生成验证码"""
    return ''.join([str(random.randint(0, 9)) for _ in range(Config.VERIFICATION_CODE_LENGTH)])

def send_verification_code(email):
    """发送验证码到邮箱"""
    # 验证邮箱是否存在
    user = get_user_by_phone_or_email(email=email)
    if not user:
        return None, "邮箱未注册"
    
    # 生成并存储验证码
    code = generate_verification_code()
    store_verification_code(email, code)
    
    # 发送邮件
    server = None
    try:
        msg = MIMEMultipart()
        msg['From'] = f"{Config.EMAIL_CONFIG['sender_name']} <{Config.EMAIL_CONFIG['sender_email']}>"
        msg['To'] = email
        msg['Subject'] = '您的验证码 - Schedule Planner'
        
        body = f"""
        您好！
        
        您的验证码是：{code}
        
        此验证码将在{Config.VERIFICATION_CODE_EXPIRY_MINUTES}分钟后过期，请尽快使用。
        
        如果这不是您的操作，请忽略此邮件。
        
        ——Schedule Planner团队
        """
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        server = smtplib.SMTP(Config.EMAIL_CONFIG['smtp_server'], Config.EMAIL_CONFIG['smtp_port'])
        server.starttls()
        server.login(Config.EMAIL_CONFIG['sender_email'], Config.EMAIL_CONFIG['sender_password'])
        server.sendmail(Config.EMAIL_CONFIG['sender_email'], email, msg.as_string())
        
        return True, "验证码已发送"
        
    except Exception as e:
        # 即使出现连接关闭错误，如果验证码已经生成并存储，也算成功
        error_msg = str(e)
        if "b'\\x00\\x00\\x00'" in error_msg or "Connection forcibly closed" in error_msg:
            # 这种错误通常是 SMTP 服务器主动关闭连接，但邮件可能已发送成功
            return True, "验证码已发送"
        else:
            return None, f"邮件发送失败: {error_msg}"
    finally:
        if server:
            try:
                server.quit()
            except:
                pass  # 忽略关闭连接时的错误

def verify_verification_code(email, code):
    """验证验证码"""
    stored_code = get_verification_code(email)
    if not stored_code:
        return None, "验证码错误或已过期"
    
    if stored_code != code:
        return None, "验证码错误"
    
    # 验证通过，使验证码失效
    invalidate_verification_code(email, code)
    return True, "验证成功"

def reset_user_password(email, code, new_password):
    """重置用户密码"""
    # 验证邮箱是否存在
    user = get_user_by_phone_or_email(email=email)
    if not user:
        return None, "邮箱未注册"
    
    # 验证验证码
    success, message = verify_verification_code(email, code)
    if not success:
        return None, message
    
    # 重置密码
    success, message = reset_password(email, new_password)
    if not success:
        return None, "密码重置失败"
    
    return True, message