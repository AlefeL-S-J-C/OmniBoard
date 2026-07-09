import os
import firebase_admin
from firebase_admin import credentials, messaging
from src.database.postgres import get_session
from src.database.models import User
from sqlalchemy import select

# Initialize Firebase Admin SDK once
if not firebase_admin._apps:
    cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    if cred_path and os.path.isfile(cred_path):
        cred = credentials.Certificate(cred_path)
    else:
        # fallback to default credentials (e.g., GOOGLE_APPLICATION_CREDENTIALS)
        cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred)


async def send_push(user_id: int, title: str, body: str, data: dict | None = None):
    """
    Send a push notification to the user's FCM token (if any).
    """
    async for db in get_session():
        stmt = select(User).where(User.id == user_id)
        user = (await db.execute(stmt)).scalar_one_or_none()
        if not user or not user.fcm_token:
            return
        token = user.fcm_token
        break

    message = messaging.Message(
        token=token,
        notification=messaging.Notification(title=title, body=body),
        data=data or {},
        apns=messaging.APNSConfig(
            payload=messaging.APNSPayload(
                aps=messaging.Aps(alert=messaging.ApsAlert(title=title, body=body), sound="default")
            )
        ),
    )
    try:
        messaging.send(message)
    except Exception as exc:
        # log but don't raise
        print(f"[push] failed to send to user {user_id}: {exc}")