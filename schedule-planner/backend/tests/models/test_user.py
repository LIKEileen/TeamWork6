import pytest
import sqlite3
# 导入需要被测试的函数
from app.models.user import (
    create_user,
    get_user_by_id,
    get_user_by_email,
    get_user_by_phone,
    verify_password,
    change_user_password,
    update_user_info,
    store_verification_code,
    get_verification_code,
    invalidate_verification_code,
    add_token_to_blacklist,
    is_token_blacklisted,
)

# 使用 seed_data fixture，它会提供一个包含3个虚拟用户的数据库
def test_get_user_by_id(seed_data):
    """测试通过ID获取用户。"""
    user = get_user_by_id(1)
    assert user is not None
    assert user['id'] == 1
    assert user['nickname'] == 'TestUser1'
    assert user['email'] == 'user1@test.com'

    non_existent_user = get_user_by_id(999)
    assert non_existent_user is None


def test_get_user_by_email(seed_data):
    """测试通过邮箱获取用户。"""
    user = get_user_by_email('user2@test.com')
    assert user is not None
    assert user['id'] == 2
    assert user['nickname'] == 'TestUser2'

    non_existent_user = get_user_by_email('nouser@test.com')
    assert non_existent_user is None


def test_get_user_by_phone(seed_data):
    """测试通过手机号获取用户。"""
    user = get_user_by_phone('33333333333')
    assert user is not None
    assert user['id'] == 3
    assert user['role'] == 'admin'

    non_existent_user = get_user_by_phone('00000000000')
    assert non_existent_user is None


def test_create_user_success(seed_data):
    """测试成功创建新用户。"""
    new_user_data = {
        'nickname': 'Newbie',
        'email': 'newbie@test.com',
        'phone': '44444444444',
        'password': 'a_strong_password'
    }
    user, message = create_user(new_user_data)
    
    assert message == "用户创建成功"
    assert user is not None
    assert user['nickname'] == 'Newbie'
    assert user['email'] == 'newbie@test.com'
    
    # 验证密码是否被正确哈希
    assert 'password' not in user
    assert 'password_hash' in user
    assert verify_password('a_strong_password', user['password_hash'])


def test_create_user_duplicate_email(seed_data):
    """测试创建用户时邮箱重复的场景。"""
    duplicate_user_data = {
        'nickname': 'Another User',
        'email': 'user1@test.com', # 这个邮箱已存在
        'password': 'password123'
    }
    user, message = create_user(duplicate_user_data)
    assert user is None
    assert "该邮箱已被注册" in message


def test_create_user_duplicate_phone(seed_data):
    """测试创建用户时手机号重复的场景。"""
    duplicate_user_data = {
        'nickname': 'Another User',
        'email': 'another@test.com',
        'phone': '11111111111', # 这个手机号已存在
        'password': 'password123'
    }
    user, message = create_user(duplicate_user_data)
    assert user is None
    assert "该手机号已被注册" in message


def test_create_user_missing_fields(seed_data):
    """测试创建用户时缺少必要字段的场景。"""
    missing_email_data = {'nickname': 'No Email', 'password': 'pw'}
    user, message = create_user(missing_email_data)
    assert user is None
    assert "昵称和邮箱不能为空" in message

    missing_password_data = {'nickname': 'No Pass', 'email': 'nopass@test.com'}
    user, message = create_user(missing_password_data)
    assert user is None
    assert "密码不能为空" in message


def test_password_change(seed_data):
    """测试修改密码的功能。"""
    user_id = 1
    old_password_plain = 'user1_password'
    new_password_plain = 'new_strong_password'

    # 首先，我们需要为用户1设置一个已知的密码
    from werkzeug.security import generate_password_hash
    cursor = seed_data.cursor()
    hashed_old_password = generate_password_hash(old_password_plain)
    cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hashed_old_password, user_id))
    seed_data.commit()

    # 测试用错误的旧密码修改
    _, message_fail = change_user_password(user_id, 'wrong_old_password', new_password_plain)
    assert "原密码错误" in message_fail

    # 测试用正确的旧密码修改
    result_success, message_success = change_user_password(user_id, old_password_plain, new_password_plain)
    assert result_success is True
    assert "密码修改成功" in message_success

    # 验证新密码是否生效
    updated_user = get_user_by_id(user_id)
    assert verify_password(new_password_plain, updated_user['password_hash'])
    # 验证旧密码已失效
    assert not verify_password(old_password_plain, updated_user['password_hash'])


def test_update_user_info(seed_data):
    """测试更新用户信息。"""
    user_id = 2
    updates = {
        'nickname': 'UpdatedNick',
        'phone': '22222222200' # 新手机号
    }
    
    updated_user, message = update_user_info(user_id, updates)
    assert "用户信息更新成功" in message
    assert updated_user is not None
    assert updated_user['nickname'] == 'UpdatedNick'
    assert updated_user['phone'] == '22222222200'
    assert updated_user['email'] == 'user2@test.com' # 邮箱未被修改

    # 测试更新一个已被占用的邮箱
    failed_update, fail_message = update_user_info(user_id, {'email': 'user1@test.com'})
    assert failed_update is None
    assert "该邮箱已被其他用户使用" in fail_message


def test_verification_code_flow(seed_data):
    """测试验证码的存储、获取和失效流程。"""
    test_email = 'verify@test.com'
    test_code = '123456'

    # 1. 存储验证码
    store_verification_code(test_email, test_code)

    # 2. 获取验证码
    code_from_db = get_verification_code(test_email)
    assert code_from_db == test_code

    # 3. 使验证码失效
    invalidate_verification_code(test_email, test_code)
    
    # 4. 再次获取，应为None
    code_after_invalidate = get_verification_code(test_email)
    assert code_after_invalidate is None


def test_token_blacklist(seed_data):
    """测试JWT Token黑名单功能。"""
    blacklisted_token = "this.is.a.blacklisted.token"
    fresh_token = "this.is.a.fresh.token"

    # 1. 将一个token加入黑名单
    add_token_to_blacklist(blacklisted_token)

    # 2. 检查
    assert is_token_blacklisted(blacklisted_token) is True
    assert is_token_blacklisted(fresh_token) is False
