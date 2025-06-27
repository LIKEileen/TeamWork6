import pytest
import json
import io
import os

def test_upload_schedule_success(test_client, mocker):
    """测试成功上传日程文件。"""
    # 模拟 service 层，我们只关心路由是否正确调用了服务
    mock_service = mocker.patch('app.routes.upload.process_schedule_file', return_value={"status": "success", "message": "File processed."})
    
    # 创建一个模拟的内存文件
    file_data = (io.BytesIO(b'dummy,csv,data'), 'schedule.csv')
    
    response = test_client.post(
        '/upload/schedule',
        data={'file': file_data},
        content_type='multipart/form-data'
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data['status'] == 'success'
    mock_service.assert_called_once()


def test_upload_schedule_no_file(test_client):
    """测试上传日程时没有提供文件。"""
    response = test_client.post(
        '/upload/schedule',
        content_type='multipart/form-data'
    )
    data = response.get_json()

    assert response.status_code == 400
    assert 'No file provided' in data['error']


def test_uploaded_file_success(test_client, mocker):
    """测试成功获取已上传的文件。"""
    # 模拟 os.path.exists 使其返回 True
    mocker.patch('app.routes.upload.os.path.exists', return_value=True)
    # 模拟 send_from_directory
    mock_send = mocker.patch('app.routes.upload.send_from_directory', return_value="file content")
    
    response = test_client.get('/upload/uploads/some_file.txt')

    assert response.status_code == 200
    assert response.data == b"file content"
    mock_send.assert_called_once()


def test_uploaded_file_not_found(test_client, mocker):
    """测试获取不存在的文件。"""
    # 模拟 os.path.exists 使其返回 False
    mocker.patch('app.routes.upload.os.path.exists', return_value=False)
    
    response = test_client.get('/upload/uploads/non_existent_file.txt')
    
    assert response.status_code == 404


def test_avatar_file_success(test_client, mocker):
    """测试成功获取头像文件。"""
    mocker.patch('app.routes.upload.os.path.exists', return_value=True)
    mock_send = mocker.patch('app.routes.upload.send_from_directory', return_value="avatar content")
    
    response = test_client.get('/upload/uploads/avatars/my_avatar.jpg')

    assert response.status_code == 200
    assert response.data == b"avatar content"
    mock_send.assert_called_once_with(os.path.join('uploads', 'avatars'), 'my_avatar.jpg')

