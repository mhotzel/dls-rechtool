
from contextlib import closing
from csv import DictReader
from datetime import datetime
import re
import uuid

from application.app_event import AppEvent
from domain.event_factory import orderconfirmation_imported_event
from domain.order_confirmation import OrderConfirmation, OrderConfItem
from services.event_store.event import Event


class PaxanOrderConfirmationImportCmd:

    def __init__(self, filename: str, suppl_id: str, suppl_name: str):
        self.filename = filename
        self.suppl_id = suppl_id
        self.suppl_name = suppl_name
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
                suppl_id=self.suppl_id,
                suppl_name=self.suppl_name,
                order_confirm_id=self.order_id,
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

                item = OrderConfItem(
                    idx=position,
                    seller_assigned_id=seller_assigned_id,
                    global_id=global_id,
                    name=name,
                    quantity=quantity,
                    price=price
                )
                order_conf.positions.append(item)

        evt = orderconfirmation_imported_event(order_conf)
        return evt

    def getFloat(self, data: str) -> float:
        data = data.replace('.', '')
        data = data.replace(',', '.')
        return float(data)
