
from contextlib import closing
from csv import DictReader
from datetime import datetime, date
import re
import uuid

from application.app_event import AppEvent
from domain.order_confirmation import OrderConfirmation, OrderItem
from services.event_store.event import Event
from services.event_store.eventstore import EventStore


class PaxanOrderConfirmationImportCmd:

    def __init__(self, filename: str, seller_id: str):
        self.filename = filename
        self.seller_id = seller_id
        match = re.search(r"(\d{8}-\d{6})", filename)
        self.order_id = None
        if match:
            self.order_id = match.group(1)  # 20250826-173018
        else:
            raise LookupError(
                f"Es konnte keine Bestell-ID aus dem Dateinamen '{filename}' extrahiert werden.")

    def createEvent(self) -> Event:
        item = None
        with closing(open(self.filename, encoding='utf8')) as csv_file:
            reader = DictReader(csv_file)
            order_conf = OrderConfirmation(
                seller_id=self.seller_id,
                order_confirm=self.order_id,
                # erstmal ein Dummy, wird mit der ersten Position gefixt
                order_date=datetime.now().date()
            )
            for row in reader:
                position = row['Position']
                order_date = datetime.strptime(
                    row['Datum'], '%d.%m.%Y').date()
                seller_assigned_id = row['ArtNr']
                global_id = row['EAN']
                name = row['Regaltext']
                quantity = self.getFloat(row['Anzahl'])

                price = self.getFloat(row['Preis'])
                order_conf.order_date = order_date

                item = OrderItem(
                    idx=position,
                    seller_assigned_id=seller_assigned_id,
                    global_id=global_id,
                    name=name,
                    quantity=quantity,
                    price=price
                )
                order_conf.positions.append(item)

        subject = f'orderconfirmation-{order_conf.order_confirm}'
        evt = Event.createEvent(
            uuid.uuid1(),
            subject=subject,
            type='order.imported',
            data=order_conf.model_dump_json()
        )
        return evt

    def getFloat(self, data: str) -> float:
        data = data.replace('.', '')
        data = data.replace(',', '.')
        return float(data)
