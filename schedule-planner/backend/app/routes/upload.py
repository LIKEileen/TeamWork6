from flask import Blueprint, request, jsonify
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