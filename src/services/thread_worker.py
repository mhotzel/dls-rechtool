from abc import ABC
from enum import Enum
from queue import Queue, SimpleQueue
from threading import Thread
import traceback
from typing import Optional

from pydantic import BaseModel

class Status(BaseModel):
    evt_warn_lvl: str = ''
    evt_type: str
    payload: str = ''


class Message(BaseModel):
    evt_type: str
    payload: str = ''

class ThreadWorker(ABC):
    """
    Der Worker kann genutzt werden, um einen Daemon-Thread zu starten. Dieser läuft dann,
    bis er ein Stop-Signal erhält. Starten und Stoppen erfolgt über die Methoden
    'start()' und 'stop()'. Nach dem Start wird die Methode 'on_start' einmalig ausgeführt.
    Dann wartet der Worker auf eine Nachricht per 'send_message(msg_type, payload)' und arbeitet dann bei 
    Erhalt die Methode 'on_message(msg)' ab. Danach wartet er wieder auf die nächste Nachricht.
    Die Methode 'on_stop()' wird einmalig am Ende nach Erhalt der Nachricht 'quit' bzw. 
    Aufruf der Methode 'stop()' aufgerufen.
    """

    def __init__(self, name: str, status_queue: SimpleQueue):
        self.__in_queue: Queue[Message] = Queue(maxsize=5)
        self.__out_queue: SimpleQueue[Status] = status_queue
        self.__thread: Optional[Thread] = None
        self._name = name
        self.__stopping = False

    def start(self) -> None:
        """Startet den Worker"""
        if self.__thread and self.__thread.is_alive():
            return

        self.__stopping = False
        self.__thread = Thread(target=self.__run, name=self._name, daemon=True)
        self.__thread.start()
        self._emit(Status(evt_type='THREADWORKER', payload='Lesemodell-Aufbereitung ist gestartet'))

    def on_start(self) -> bool:
        """
        Durch Überschreiben kann hier auf den Start des Workers reagiert werden. 
        Auf das Überschreiben der eigentlichen Start-Methode sollte verzichtet werden.
        Gibt die Funktion 'False' zurück, wird der Thread beendet.
        """
        return True

    def on_stop(self) -> None:
        """Durch Überschreiben kann hier auf das Stoppen des Workers reagiert werden. 
        Auf das Überschreiben der eigentlichen Stop-Methode sollte verzichtet werden."""
        pass

    def on_message(self, msg: Message) -> None:
        """Durch Überschreiben kann hier auf Ereignisse reagiert werden. 
        Auf 'quit' wird immer reagiert, auch ohne diese Methode nutzen"""
        pass

    def send_message(self, msg_type: str, payload: str) -> None:
        """
        Sendet eine Nachricht an den Worker. Der Worker reagiert standardmäßig auf 
        die Nachricht vom Typ 'quit', indem er sich beendet. Der Aufruf der Methode 
        'stop()' erledigt das Gleiche.
        """
        msg = Message(evt_type=msg_type, payload=payload)
        self.__in_queue.put(msg)

    def stop(self) -> None:
        """Sendet eine Stop-Nachricht an den Worker"""
        if self.__stopping:
            return
        self.__stopping = True

        self.__in_queue.put(Message(evt_type="quit"))
        if self.__thread:
            self.__thread.join()

    def get_status_queue(self) -> SimpleQueue[Status]:
        """Gib die Outbox zurück (Konsument kann blocking/nonblocking lesen)."""
        # Im HauptThread kann man mit 'status_q.get_nowait()' auf die Queue z.B. sekuendlich pollen
        return self.__out_queue

    # --- interner Thread ---
    def _emit(self, status: Status) -> None:
        """
        Dient der Benachrichtigung über Ereignisse im Worker. Kann z.B. innerhalb 'on_message'
        genutzt werden.
        """
        # NIE blockierend. Im HauptThread kann man mit
        self.__out_queue.put(status)

    def __run(self) -> None:
        try:
            if not self.on_start():
                return
            while True:
                msg: Message = self.__in_queue.get()  # BLOCKIERT bis Message eintrifft
                try:
                    if msg.evt_type == 'quit':
                        self.on_stop()
                        break
                    else:
                        self.on_message(msg)
                except Exception as e:
                    self._emit(Status(evt_type="Exception", payload=str(e), evt_warn_lvl="ERROR"))
                    print(f"Fehler im Workers: {e}")
                finally:
                    self.__in_queue.task_done()

        except Exception as e:
            # hier ggf. Logging/Callback einbauen
            self._emit(Status(evt_type="STOPPED", payload=str(e), evt_warn_lvl="FATAL"))
            print(f"Abbruch des Workers: {traceback.format_exc()}")
