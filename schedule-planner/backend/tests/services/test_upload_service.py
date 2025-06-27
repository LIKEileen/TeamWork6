import pytest
import pandas as pd
from unittest.mock import MagicMock
from werkzeug.datastructures import FileStorage
from app.services.upload_service import (
    process_schedule_file,
    upload_avatar,
    get_mock_schedules,
)

# 使用 clear_upload_mock fixture 确保每次测试前 mock 数据是空的
pytestmark = pytest.mark.usefixtures("clear_upload_mock")

def test_process_schedule_file_excel_success(mocker):
    """测试成功处理上传的Excel日程文件。"""
    # 1. 模拟文件系统和pandas
    mock_df = pd.DataFrame({
        'member': ['user_1', 'user_1'],
        'day': ['2025-11-20', '2025-11-21'],
        'start': ['09:00', '10:00'],
        'end': ['10:00', '11:00'],
        'event': ['Excel morning meeting', 'Excel afternoon sync']
    })
    mocker.patch('pandas.read_excel', return_value=mock_df)
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('os.makedirs')
    # 创建一个模拟的FileStorage对象
    mock_file = MagicMock(spec=FileStorage)
    mock_file.filename = 'schedule.xlsx'
    
    # 2. 调用服务
    result, message = process_schedule_file(mock_file, "valid_token")

    # 3. 验证结果
    assert "日程文件上传成功" in message
    assert result is not None
    assert result['schedules_imported'] == 2
    
    # 4. 验证内存中的mock数据是否被正确填充
    mock_data = get_mock_schedules()
    assert 'user_1' in mock_data
    assert len(mock_data['user_1']) == 2
    assert mock_data['user_1'][0]['event'] == 'Excel morning meeting'


def test_process_schedule_file_invalid_token():
    """测试使用无效token处理文件。"""
    mock_file = MagicMock(spec=FileStorage)
    mock_file.filename = 'schedule.csv'
    
    result, message = process_schedule_file(mock_file, "invalid_token")

    assert result is None
    assert "用户未登录或token无效" in message


def test_process_schedule_file_unsupported_extension():
    """测试上传不支持的文件类型。"""
    mock_file = MagicMock(spec=FileStorage)
    mock_file.filename = 'document.pdf'

    result, message = process_schedule_file(mock_file, "valid_token")

    assert result is None
    assert "只支持 CSV、TXT、JSON、Excel 格式的文件" in message


def test_upload_avatar_success(mocker):
    """测试成功上传头像。"""
    # 模拟文件系统操作
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('os.makedirs')
    
    # 创建一个模拟的FileStorage对象
    mock_file = MagicMock(spec=FileStorage)
    mock_file.filename = 'my_avatar.png'
    
    # 调用服务
    result, message = upload_avatar(mock_file, "valid_token")

    # 验证结果
    assert "头像上传成功" in message
    assert result is not None
    assert result['original_filename'] == 'my_avatar.png'
    assert result['avatar_url'].endswith('.png')
    # 验证 file.save 被调用了一次
    mock_file.save.assert_called_once()


def test_upload_avatar_invalid_file_type():
    """测试上传无效的头像文件类型。"""
    mock_file = MagicMock(spec=FileStorage)
    mock_file.filename = 'image.svg'

    result, message = upload_avatar(mock_file, "valid_token")

    assert result is None
    assert "只支持 PNG、JPG、JPEG、GIF 格式的图片" in message

