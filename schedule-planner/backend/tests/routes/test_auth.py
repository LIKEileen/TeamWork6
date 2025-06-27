import pytest
import json

def test_register_success(test_client):
    """
    测试成功注册一个新用户。
    """
    response = test_client.post('/auth/register', json={
        "nickname": "NewUser",
        "email": "new@example.com",
        "password": "password123"
    })
    data = json.loads(response.data)

    assert response.status_code == 200
    assert data['code'] == 1
    assert data['message'] == 'success'
    assert data['data']['nickname'] == 'NewUser'
    assert data['data']['email'] == 'new@example.com'
    assert 'token' in data['data'] # 注册成功后应自动登录并返回token

def test_register_duplicate_email(test_client):
    """
    测试使用已存在的邮箱进行注册。
    """
    # `test_client` fixture 来自 conftest.py，它已经填充了 'creator1@test.com'
    response = test_client.post('/auth/register', json={
        "nickname": "AnotherUser",
        "email": "creator1@test.com",
        "password": "password123"
    })
    data = json.loads(response.data)
    
    assert response.status_code == 400
    assert data['code'] == 0
    assert "该邮箱已被注册" in data['message']


def test_register_missing_fields(test_client):
    """
    测试注册时缺少必要字段。
    """
    response = test_client.post('/auth/register', json={
        "nickname": "MissingEmail",
        "password": "password123"
    })
    data = json.loads(response.data)
    
    assert response.status_code == 400
    assert data['code'] == 0
    assert "缺少必填字段: email" in data['message']


def test_login_success(test_client):
    """
    测试使用正确的凭据成功登录。
    """
    response = test_client.post('/auth/login', json={
        "email": "creator1@test.com",
        "password": "pass1" # pass1 是在 conftest.py 中为该用户设置的密码
    })
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['code'] == 1
    assert data['message'] == 'success'
    assert data['data']['user']['email'] == 'creator1@test.com'
    assert 'token' in data['data']


def test_login_wrong_password(test_client):
    """
    测试使用错误的密码登录。
    """
    response = test_client.post('/auth/login', json={
        "email": "creator1@test.com",
        "password": "wrongpassword"
    })
    data = json.loads(response.data)
    
    assert response.status_code == 400
    assert data['code'] == 0
    assert "密码错误" in data['message']


def test_login_nonexistent_user(test_client):
    """
    测试使用不存在的用户登录。
    """
    response = test_client.post('/auth/login', json={
        "email": "nonexistent@example.com",
        "password": "anypassword"
    })
    data = json.loads(response.data)
    
    assert response.status_code == 400
    assert data['code'] == 0
    assert "用户不存在" in data['message']


def test_logout_success(test_client):
    """
    测试登出功能，需要先登录以获取有效的token。
    """
    # 步骤1: 登录获取token
    login_response = test_client.post('/auth/login', json={
        "email": "creator1@test.com",
        "password": "pass1"
    })
    login_data = json.loads(login_response.data)
    token = login_data['data']['token']

    # 步骤2: 使用获取到的token进行登出
    logout_response = test_client.post('/auth/logout', json={"token": token})
    logout_data = json.loads(logout_response.data)

    assert logout_response.status_code == 200
    assert logout_data['code'] == 1
    assert "退出成功" in logout_data['message']

    # (可选) 验证token是否已被加入黑名单
    # 这一步需要直接查询数据库，或者尝试用旧token访问一个受保护的接口
    # from app.models.user import is_token_blacklisted
    # assert is_token_blacklisted(token) is True


def test_send_verification_code(test_client, mocker):
    """
    测试发送验证码的接口。
    我们将使用 `mocker` 来模拟（mock）真正的邮件发送服务，以避免在测试中发送真实邮件。
    """
    # 使用 pytest-mock 来模拟 'send_email' 函数，使其总是返回 True
    mocker.patch('app.services.verification_service.send_email', return_value=True)

    response = test_client.post('/auth/send-verification-code', json={
        "email": "reset_pass@example.com",
        "type": "reset_password"
    })
    data = json.loads(response.data)

    assert response.status_code == 200
    assert data['code'] == 1
    assert "验证码已发送" in data['message']

