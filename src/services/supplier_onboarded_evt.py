
from dataclasses import dataclass
from datetime import datetime
import json
import uuid

from pydantic import BaseModel
from services.event import Event

EVENT_TYPE_SUPPLIER_ONBOARDED = 'supplier.onboarded'

def createEvent(id: uuid.UUID, suppl_id: str, suppl_name: str, seller_id: str) -> Event:

    evt = Event.createEvent(
        id=id, subject=f"supplier-id={suppl_id}", type=EVENT_TYPE_SUPPLIER_ONBOARDED)
    
    se = {
        'suppl_id': suppl_id,
        'suppl_name': suppl_name,
        'seller_id': seller_id
    }
    evt.data = json.dumps(se, ensure_ascii=False).encode('utf8')

    return evt
