
from typing import Any, List, Mapping
from domain.find_inv_order_events_cmd import Document
from services.readmodels.base_data_store import DataStore, Product
from services.sqlite_conn_manager import SqliteConnectionManager

def _product_from_dict(db_row: Mapping[str, Any]) -> Product:
    return Product(
        suppl_id=db_row['suppl_id'],
        suppl_name=db_row['suppl_name'],
        issue_type=db_row['issue_type'],
        issue_id=db_row['issue_id'],
        issue_date=db_row['issue_date'],
        seller_assigned_id=db_row['seller_assigned_id'],
        global_id=db_row['global_id'],
        name=db_row['name'],
        price=db_row['price']
    )

def _doc_from_dict(db_row: Mapping[str, Any]) -> Document:
    return Document.model_validate(db_row)

class SqliteDataStore(DataStore):

    def __init__(self, conn_mgr: SqliteConnectionManager):
        super().__init__()
        self.conn_manager = conn_mgr

    def get_product_list(self) -> List[Product]:
        """Liefert die Liste der Artikel mit Einzelpreisen"""

        sql = """
        SELECT pl.suppl_id, pl.suppl_name, pl.issue_type, pl.issue_id, pl.issue_date, pl.seller_assigned_id, pl.global_id, pl.name, pl.price
        FROM rm_product_list_t AS pl
        """

        conn = self.conn_manager.get_connection()

        result: List[Product] = None
        with conn:
            data = conn.execute(sql).fetchall()
            result = [_product_from_dict(row) for row in data]

        self.conn_manager.close_connection()

        return result

    def get_doc_list(self):
        """Liefert die Liste aller Dokumente"""

        sql = """
        SELECT suppl_id, suppl_name, doc_id, doc_type, doc_date, doc_state, updated_ts FROM rm_documents_t
        """
        doclist: List[Document] = []
        
        conn = self.conn_manager.get_connection()
        with conn:
            data = conn.execute(sql).fetchall()       
            doclist: List[Document] = [_doc_from_dict(row) for row in data]

        self.conn_manager.close_connection()

        return doclist
