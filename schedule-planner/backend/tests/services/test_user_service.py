import pytest
from unittest.mock import MagicMock
from werkzeug.datastructures import FileStorage
from app.services.user_service import (
    get_user_profile,
    update_user_profile,
    change_password_service,
    bind_phone_service,
    upload_avatar,
    update_qq_avatar_service,
    get_user_statistics,
    calculate_profile_completion,
)
from app.models.user import get_user_by_id

# All test functions will use fixtures defined in conftest.py

def test_get_user_profile_service(setup_databases, creator_token):
    """Tests successfully retrieving a user's profile."""
    profile, message = get_user_profile(creator_token)
    
    assert "获取用户信息成功" in message
    assert profile is not None
    assert profile['id'] == 1
    assert profile['nickname'] == 'Creator_One'

def test_get_user_profile_invalid_token(setup_databases):
    """Tests retrieving a profile with an invalid token."""
    profile, message = get_user_profile("a.fake.invalid.token")
    assert profile is None
    assert "无效" in message


def test_update_user_profile_service(setup_databases, admin_token):
    """Tests successfully updating a user's profile information."""
    # User 2 ('Admin_Two') is updating their profile
    new_nickname = "UpdatedAdmin"
    new_phone = "22222222299"
    profile, message = update_user_profile(admin_token, nickname=new_nickname, phone=new_phone)

    assert "用户信息更新成功" in message
    assert profile is not None
    assert profile['nickname'] == new_nickname
    assert profile['phone'] == new_phone

    # Verify the changes in the database
    updated_user_in_db = get_user_by_id(2)
    assert updated_user_in_db['nickname'] == new_nickname


def test_update_user_profile_validation_fails(setup_databases, admin_token):
    """Tests profile update failures due to validation errors."""
    # Scenario 1: Invalid phone number format
    profile, message = update_user_profile(admin_token, phone="123")
    assert profile is None
    assert "手机号格式不正确" in message
    
    # Scenario 2: Email is already taken by another user
    profile, message = update_user_profile(admin_token, email="creator1@test.com")
    assert profile is None
    assert "该邮箱已被其他用户使用" in message


def test_change_password_service(setup_databases, creator_token):
    """Tests the password change service logic."""
    # Scenario 1: Correct old password
    result, message = change_password_service(creator_token, "pass1", "a_very_new_password")
    assert result is True
    assert "密码修改成功" in message

    # Scenario 2: Incorrect old password
    result, message = change_password_service(creator_token, "wrong_old_pass", "another_new_password")
    assert result is None
    assert "原密码错误" in message

    # Scenario 3: New password is too short
    result, message = change_password_service(creator_token, "a_very_new_password", "123")
    assert result is None
    assert "新密码长度至少为6位" in message


def test_upload_avatar_service(setup_databases, creator_token, mocker):
    """Tests the avatar upload service."""
    # Mock file system operations
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('os.makedirs')
    mocker.patch('os.remove')
    
    # Create a mock FileStorage object
    mock_file = MagicMock(spec=FileStorage)
    mock_file.filename = 'test_avatar.png'
    # Mock the seek and tell methods to simulate file size checking
    mock_file.tell.return_value = 1024 * 1024 # 1MB
    
    avatar_url, message = upload_avatar(creator_token, mock_file)
    
    assert "头像上传成功" in message
    assert avatar_url is not None
    assert avatar_url.startswith('/uploads/avatars/avatar_1_')
    
    # Verify file.save was called
    mock_file.save.assert_called_once()


def test_update_qq_avatar_service(setup_databases, creator_token, mocker):
    """Tests updating user avatar using a QQ URL."""
    # Mock the requests.head call to simulate a valid URL
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {'content-type': 'image/jpeg'}
    mocker.patch('requests.head', return_value=mock_response)
    
    qq_url = "https://q.qlogo.cn/g?b=qq&nk=12345&s=640"
    result, message = update_qq_avatar_service(creator_token, qq_url)

    assert result is True
    assert "QQ头像已更新" in message

    # Verify the change in the database
    updated_user = get_user_by_id(1)
    assert updated_user['avatar'] == qq_url


def test_get_user_statistics(setup_databases):
    """Tests the user statistics calculation service."""
    stats, message = get_user_statistics(1)

    assert "获取统计信息成功" in message
    assert stats is not None
    assert stats['user_id'] == 1
    assert 'join_date' in stats
    # Based on conftest data: nickname, email, phone, avatar are present. role is default 'user'.
    # 5 out of 5 fields are complete.
    assert stats['profile_completion'] == 100.0
