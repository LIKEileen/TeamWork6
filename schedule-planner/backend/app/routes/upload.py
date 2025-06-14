from flask import Blueprint, request, jsonify, send_from_directory, abort
import os
import logging
from ..services.upload_service import process_schedule_file

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/schedule', methods=['POST'])
def upload_schedule():
    """处理上传的日程文件（CSV/Excel）"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    file = request.files['file']
    try:
        result = process_schedule_file(file)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@upload_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """提供上传文件的访问服务"""
    try:
        # 安全检查，防止路径遍历攻击
        if '..' in filename or filename.startswith('/'):
            abort(404)
        
        upload_folder = 'uploads'
        file_path = os.path.join(upload_folder, filename)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            abort(404)
        
        # 获取文件目录和文件名
        directory = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        
        return send_from_directory(directory, filename)
        
    except Exception as e:
        logging.error(f"Error serving uploaded file: {str(e)}")
        abort(404)

@upload_bp.route('/uploads/avatars/<filename>')
def avatar_file(filename):
    """专门提供头像文件的访问服务"""
    try:
        # 安全检查
        if '..' in filename or filename.startswith('/'):
            abort(404)
        
        avatars_folder = os.path.join('uploads', 'avatars')
        
        # 检查文件是否存在
        file_path = os.path.join(avatars_folder, filename)
        if not os.path.exists(file_path):
            abort(404)
        
        return send_from_directory(avatars_folder, filename)
        
    except Exception as e:
        logging.error(f"Error serving avatar file: {str(e)}")
        abort(404)