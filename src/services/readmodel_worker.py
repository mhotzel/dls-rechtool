from queue import SimpleQueue
from typing import List
from services.rm_builder.rm_builder_base import ReadModelBaseBuilder
from services.rm_builder.rm_builder_docs import RmDocumentListBuilder
from services.rm_builder.rm_builder_prod_prices import RmProductListBuilder
from services.rm_builder.rm_builder_supplier import RmSupplierBuilder
from services.sqlite_conn_manager import SqliteConnectionManager
from services.thread_worker import ThreadWorker, Status, Message


class ReadModelWorker(ThreadWorker):
    """lauscht nach dem Start auf Events und aktualisiert dann die Read Models"""

    def __init__(self, conn_manager: SqliteConnectionManager, status_queue: SimpleQueue):
        super().__init__(name='ReadModelWorker', status_queue=status_queue)
        self.conn_manager = conn_manager
        self._handlers: List[ReadModelBaseBuilder] = [
            RmProductListBuilder(conn_manager, status_queue),
            RmSupplierBuilder(conn_manager, status_queue),
            RmDocumentListBuilder(conn_manager, status_queue)
        ]

    def on_start(self):
        for builder in self._handlers:
            builder.run()
        return True

    def on_message(self, msg):
        for builder in self._handlers:
            builder.run()

    def update(self) -> None:
        """Convinience-Methode zum Senden einer Nachricht, um ein Update anzustoßen"""
        self.send_message('update', '')
