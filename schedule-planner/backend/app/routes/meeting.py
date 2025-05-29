from flask import Blueprint, request, jsonify
from ..services.meeting_service import find_meeting_times

meeting_bp = Blueprint('meeting', __name__)

@meeting_bp.route('/suggest', methods=['POST'])
def suggest_meeting():
    """根据成员、时长和偏好推荐会议时间"""
    data = request.get_json()
    members = data.get('members', [])
    duration = int(data.get('duration', 60))
    preferences = data.get('preferences', '')
    suggestions = find_meeting_times(members, duration, preferences)
    return jsonify(suggestions)