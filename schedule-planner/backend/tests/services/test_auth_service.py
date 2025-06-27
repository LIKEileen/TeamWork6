import pytest
from app.services.auth_service import (
    register_user,
    authenticate_user,
    generate_token,
    verify_token,
    logout_user,
    is_token_blacklisted,
    bind_user_phone,
)
from app.models.user import get_user_by_id
from app.config import Config

# 所有测试函数都将使用 setup_databases fixture
# 它提供了一个干净的、填充了虚拟数据的数据库环境
def test_register_user_success(setup_databases):
    """
    测试成功注册一个新用户。
    """
    new_user_data = {
        'nickname': 'ServiceTester',
        'email': 'service.tester@example.com',
        'password': 'a_secure_password',
        'phone': '19988887777'
    }
    user_info, message = register_user(new_user_data)

    assert "注册成功" in message
    assert user_info is not None
    assert user_info['nickname'] == 'ServiceTester'
    assert 'token' in user_info

    # 验证用户是否真的被创建在了数据库中
    new_user = get_user_by_id(5) # 虚拟数据中有4个用户，新用户ID应为5
    assert new_user is not None
    assert new_user['email'] == 'service.tester@example.com'


def test_register_user_duplicate_email(setup_databases):
    """
    测试使用重复的邮箱注册。
    """
    duplicate_data = {
        'nickname': 'Duplicate',
        'email': 'creator1@test.com', # 该邮箱已存在
        'password': 'password123'
    }
    user_info, message = register_user(duplicate_data)
    
    assert user_info is None
    assert "该邮箱已被注册" in message


def test_authenticate_user_success(setup_databases):
    """
    测试使用正确的凭据成功认证用户。
    """
    # 虚拟数据中，用户1的密码是 'pass1'
    user, message = authenticate_user('creator1@test.com', 'pass1')
    
    assert "登录成功" in message
    assert user is not None
    assert user['id'] == 1
    assert user['nickname'] == 'Creator_One'


def test_authenticate_user_wrong_password(setup_databases):
    """
    测试使用错误的密码认证用户。
    """
    user, message = authenticate_user('creator1@test.com', 'wrong_password')
    
    assert user is None
    assert "密码错误" in message


def test_token_lifecycle(setup_databases):
    """
    测试JWT Token的生成、验证、加入黑名单和失效的完整生命周期。
    """
    # 1. 获取一个用户并为他生成token
    user = get_user_by_id(1)
    token = generate_token(user)
    assert token is not None

    # 2. 验证生成的token是否有效
    payload = verify_token(token)
    assert payload is not None
    assert payload['user_id'] == user['id']
    assert payload['nickname'] == user['nickname']

    # 3. 将token加入黑名单（登出）
    success, message = logout_user(token)
    assert success is True
    assert "退出成功" in message

    # 4. 确认token已被加入黑名单
    assert is_token_blacklisted(token) is True

    # 5. 再次验证已加入黑名单的token，应返回None
    payload_after_logout = verify_token(token)
    assert payload_after_logout is None


def test_bind_user_phone_success(setup_databases, mocker):
    """
    测试成功绑定手机号。
    我们将模拟(mock)验证码服务，以隔离测试。
    """
    # 模拟 verification_service.verify_code 函数，使其总是返回成功
    mocker.patch('app.services.auth_service.verify_code', return_value=(True, "验证成功"))

    # 为用户2生成一个token
    user2 = get_user_by_id(2)
    token = generate_token(user2)
    
    new_phone_number = '19912345678'
    verification_code = '123456' # 因为服务被mock了，所以内容无所谓

    user_info, message = bind_user_phone(token, new_phone_number, verification_code)

    assert "手机号绑定成功" in message
    assert user_info is not None
    assert user_info['phone'] == new_phone_number
    
    # 验证数据库中的数据确实被更新了
    updated_user_in_db = get_user_by_id(2)
    assert updated_user_in_db['phone'] == new_phone_number


def test_bind_user_phone_code_invalid(setup_databases, mocker):
    """
    测试因验证码无效而导致手机号绑定失败。
    """
    # 模拟 verification_service.verify_code 函数，使其返回失败
    mocker.patch('app.services.auth_service.verify_code', return_value=(False, "验证码错误"))

    user2 = get_user_by_id(2)
    token = generate_token(user2)
    
    user_info, message = bind_user_phone(token, '19912345678', 'wrong_code')

    assert user_info is None
    assert "验证码错误" in message
