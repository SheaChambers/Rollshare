from flask import Blueprint, request
from app.controllers import video_analyser_controller as v
from app.decorators.auth_decorators import jwt_required

video_analyser_bp = Blueprint("video_analyser_bp", __name__)

@video_analyser_bp.route("/api/v1.0/techniques/<string:technique_id>/analyse", methods=["POST"])
@jwt_required
def analyse_video(technique_id, current_user, is_admin):
    return v.request_analysis(technique_id, current_user)