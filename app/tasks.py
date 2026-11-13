import time
from datetime import datetime, timezone

from app.celery_app import celery_app
from app.config import RECEIPT_SECONDS


@celery_app.task(name="send_receipt")
def send_receipt(order_id, email, total_price):
    time.sleep(RECEIPT_SECONDS)

    return {
        "order_id": order_id,
        "sent_to": email,
        "message": f"Чек по заказу №{order_id} на сумму {total_price:.2f} ₽ отправлен на {email}",
        "sent_at": datetime.now(timezone.utc).isoformat(),
    }
