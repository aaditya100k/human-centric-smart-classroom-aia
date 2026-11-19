import base64
import json
from typing import Optional
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from pydantic import BaseModel

from app.services.monitoring_service import MonitoringService
from app.utils.security import get_current_user, decode_access_token

router = APIRouter(prefix="/api/monitoring", tags=["Live Monitoring"])


class MonitoringStartRequest(BaseModel):
    classroom_id: Optional[int] = None
    camera_index: Optional[int] = 0
    fps: Optional[int] = 30


class MonitoringFrameRequest(BaseModel):
    image: str


@router.get("/status")
def get_status(current_user=Depends(get_current_user)):
    """
    Get current AI camera monitoring status, uptime, and state.
    Requires JWT authentication.
    """
    return MonitoringService.get_status()


@router.post("/start", status_code=status.HTTP_200_OK)
async def start_monitoring(
    request: Optional[MonitoringStartRequest] = None,
    current_user=Depends(get_current_user),
):
    """
    Start live monitoring session for a specified classroom.
    Requires JWT authentication.
    """
    cls_id = request.classroom_id if request else None
    cam_idx = request.camera_index if request and request.camera_index is not None else 0
    fps = request.fps if request and request.fps is not None else 30

    return await MonitoringService.start_monitoring(
        classroom_id=cls_id,
        camera_index=cam_idx,
        fps=fps,
        camera_active=True,
    )


@router.post("/stop", status_code=status.HTTP_200_OK)
async def stop_monitoring(current_user=Depends(get_current_user)):
    """
    Stop active monitoring session.
    Requires JWT authentication.
    """
    return await MonitoringService.stop_monitoring()


@router.post("/detect-faces", status_code=status.HTTP_200_OK)
def detect_faces_frame(
    request: MonitoringFrameRequest,
    current_user=Depends(get_current_user),
):
    """
    Process a single frame for OpenCV face detection via REST.
    Requires JWT authentication.
    """
    raw_img = request.image
    if "," in raw_img:
        raw_img = raw_img.split(",", 1)[1]
    image_bytes = base64.b64decode(raw_img)
    return MonitoringService.process_frame(image_bytes)


@router.websocket("/ws")
async def websocket_monitoring(websocket: WebSocket, token: Optional[str] = None):
    """
    WebSocket endpoint for real-time face detection & monitoring status.
    Requires valid JWT token parameter.
    Accepts ping/pong or frame payload {"type": "frame", "image": "data:image/jpeg;base64,..."}.
    """
    if not token:
        await websocket.close(code=4001, reason="Authentication token missing")
        return

    payload = decode_access_token(token)
    if payload is None:
        await websocket.close(code=4001, reason="Unauthorized or expired token")
        return

    await MonitoringService.connect_ws(websocket)
    try:
        while True:
            text_data = await websocket.receive_text()
            if text_data == "ping":
                await websocket.send_json({
                    "event": "pong",
                    "data": MonitoringService.get_status()
                })
            elif text_data.startswith("{") or "image" in text_data:
                try:
                    data_obj = json.loads(text_data)
                    raw_img = data_obj.get("image") or data_obj.get("data")
                    if raw_img:
                        if "," in raw_img:
                            raw_img = raw_img.split(",", 1)[1]
                        image_bytes = base64.b64decode(raw_img)
                        result = MonitoringService.process_frame(image_bytes)
                        await websocket.send_json(result)
                except Exception as parse_err:
                    await websocket.send_json({
                        "type": "error",
                        "detail": f"Failed to parse frame payload: {str(parse_err)}"
                    })
    except WebSocketDisconnect:
        MonitoringService.disconnect_ws(websocket)
    except Exception:
        MonitoringService.disconnect_ws(websocket)
