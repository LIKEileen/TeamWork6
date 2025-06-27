import pytest
from unittest.mock import MagicMock
from app.services.verification_service import (
    generate_verification_code,
    send_verification_code,
    verify_code,
    reset_user_password,
    send_email_verification_code,
)
from app.models.user import store_verification_code, get_verification_code
from app.config import Config

# 所有测试函数都将使用 conftest.py 中定义的 setup_databases fixture

def test_generate_verification_code():
    """测试验证码生成函数。"""
    code = generate_verification_code()
    assert isinstance(code, str)
    assert len(code) == Config.VERIFICATION_CODE_LENGTH
    assert code.isdigit()

def test_send_verification_code_success(setup_databases, mocker):
    """
    测试发送验证码的主流程，模拟邮件发送。
    """
    test_email = "test@example.com"
    
    # 使用 mocker 模拟（mock）底层的邮件发送函数，使其总是返回成功，避免真实发送
    mock_send_email = mocker.patch(
        'app.services.verification_service.send_email_verification_code', 
        return_value=(True, "验证码已发送（测试模式）")
    )

    success, message = send_verification_code(test_email, code_type="reset_password")

    # 验证返回结果
    assert success is True
    assert "验证码已发送" in message
    
    # 验证 send_email_verification_code 函数被正确调用
    mock_send_email.assert_called_once()
    # 验证验证码被正确存储到了数据库中
    stored_code = get_verification_code(test_email)
    assert stored_code is not None
    assert len(stored_code) == Config.VERIFICATION_CODE_LENGTH


def test_send_email_verification_code_no_config(mocker):
    """
    测试在没有邮件配置时，函数是否能优雅地进入“测试模式”。
    """
    # 模拟 Config.EMAIL_CONFIG 为空字典
    mocker.patch.object(Config, 'EMAIL_CONFIG', {})
    
    success, message = send_email_verification_code("test@example.com", "123456")
    
    assert success is True
    assert "邮件配置不完整" in message
    assert "123456" in message # 确认测试模式下返回了验证码


def test_verify_code_flow(setup_databases):
    """
    测试验证码的验证流程（正确、错误、过期）。
    """
    test_email = "verify@example.com"
    correct_code = "654321"

    # 1. 先在数据库中手动存储一个验证码
    store_verification_code(test_email, correct_code)

    # 2. 场景：使用错误的验证码
    success_fail, message_fail = verify_code(test_email, "111111")
    assert success_fail is False
    assert "验证码错误" in message_fail

    # 3. 场景：使用正确的验证码
    success_ok, message_ok = verify_code(test_email, correct_code)
    assert success_ok is True
    assert "验证码验证成功" in message_ok

    # 4. 场景：再次使用同一个验证码（此时应已被删除）
    success_expired, message_expired = verify_code(test_email, correct_code)
    assert success_expired is False
    assert "验证码不存在或已过期" in message_expired


def test_reset_user_password_success(setup_databases):
    """
    测试成功重置用户密码的流程。
    """
    # conftest 中预置了用户 'creator1@test.com'
    test_email = "creator1@test.com"
    reset_code = "999888"
    new_password = "new_password_123"

    # 1. 存入一个有效的验证码
    store_verification_code(test_email, reset_code)

    # 2. 调用重置密码服务
    success, message = reset_user_password(test_email, reset_code, new_password)

    # 3. 验证结果
    assert success is True
    assert "密码重置成功" in message

    # 4. 验证密码是否真的被修改了
    # 导入认证服务来检查新密码
    from app.services.auth_service import authenticate_user
    user, _ = authenticate_user(test_email, new_password)
    assert user is not None
    

def test_reset_user_password_invalid_code(setup_databases):
    """
    测试因验证码无效而导致重置密码失败。
    """
    test_email = "creator1@test.com"
    new_password = "another_new_password"

    success, message = reset_user_password(test_email, "invalid_code", new_password)
    
    assert success is False
    assert "验证码不存在或已过期" in message

