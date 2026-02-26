import datetime
from flask import jsonify
from bson import ObjectId
import threading

from app.services.blob_storage_service import BlobStorageService
from app.models.techniques_model import find_one_by_id, update_analysis_results



def analyse_video_task(technique_id: str):
    from ai_service.inference.predict_video_position_v2 import analyse_video
    from ai_service.feedback.feedback_engine import generate_feedback
    blob_service = BlobStorageService()

    video_doc = find_one_by_id(technique_id)
    if not video_doc:
        return

    try:
        video_url = blob_service.generate_read_url(
            video_doc["video_blob_url"], minutes=30
        )

        analysis_data = analyse_video(video_url)
        feedback = generate_feedback(analysis_data)

        analysis = {
            "timeline": analysis_data["timeline"],
            "distribution": analysis_data["distribution"],
            "top_positions": analysis_data["top_positions"],
            "feedback": feedback,
            "analysed_at": datetime.datetime.now(datetime.UTC)
        }

        update_analysis_results(
            technique_id,
            "analysed",
            analysis
        )

    except Exception as e:
        update_analysis_results(
            technique_id,
            "failed",
            {"error": str(e)}
        )

def request_analysis(technique_id: str, current_user: str):
    if not ObjectId.is_valid(technique_id):
        return jsonify({"error": "Invalid technique ID"}), 400

    t = find_one_by_id(technique_id)
    if not t:
        return jsonify({"error": "Technique not found"}), 404

    if t.get("created_by") != current_user:
        return jsonify({"error": "Not authorised"}), 403

    if t.get("analysis_status") in ["processing", "analysed"]:
        return jsonify({"message": "Nalysis already completed or running"}), 200

    update_analysis_results(technique_id, "processing", None)

    thread = threading.Thread(
        target=analyse_video_task,
        args=(technique_id,)
    )
    thread.daemon = True
    thread.start()

    return jsonify({"message": "Analysis started"}), 202