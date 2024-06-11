import can
import logging
import time
import threading
import queue

import classes


class CanInterface:
    def __init__(self, interface='ixxat', channel=0, bitrate=500000):
        # Parametri di configurazione
        self.bus = None
        self.interface = interface
        self.channel = channel
        self.bitrate = bitrate
        self.configure_bus()

        # Abilita il logging di debug
        logging.basicConfig(level=logging.DEBUG)

    def configure_bus(self):
        try:
            self.bus = can.interface.Bus(interface=self.interface, channel=self.channel, bitrate=self.bitrate)
            print("Interfaccia CAN configurata correttamente")

        except can.CanError as e:
            print(f"Errore nella configurazione dell'interfaccia CAN: {e}")
            self.bus = None

    def get_bus_status(self):
        return self.bus

    def is_connected(self):
        """Controlla se il bus CAN è ancora connesso."""
        if self.bus is None:
            return False
        try:
            # Tentiamo di ricevere un messaggio con un timeout molto breve per verificare lo stato della connessione
            self.bus.recv(timeout=0.1)
            return True
        except (can.CanError, AttributeError):
            print("Bus CAN non connesso o errore nella comunicazione.")
            return False

    def reconnect(self, retries=1, delay=2):
        for attempt in range(retries):
            print(f"Tentativo di riconnessione al bus CAN... (Tentativo {attempt + 1} di {retries})")
            self.shutdown_()
            time.sleep(delay)
            self.configure_bus()
            if self.is_connected():
                print("Riconnessione riuscita.")
                return True
        print("Riconnessione fallita.")
        return False

    def ensure_connection(self):
        if self.bus is None or not self.is_connected():
            if not self.reconnect():
                print("Riconnessione fallita.")
                return False
        return True

    def shutdown_(self):
        if self.bus is not None:
            try:
                self.bus.shutdown()
                print("Bus CAN chiuso correttamente")
                self.bus = None
            except can.CanError as e:
                print(f"Errore durante l'invio del messaggio: {e}")


class CANReceiver(CanInterface):
    def __init__(self):
        super().__init__()
        self.receive_thread = None
        self.subscribers = {}  # Dizionario degli ID di arbitraggio con i relativi callback
        self.stop_receiving_event = threading.Event()
        self.message_queue = queue.Queue()
        self.processing_thread = threading.Thread(target=self.process_messages) #self.process_messages
        self.processing_thread.daemon = True
        self.processing_thread.start()
        print("is_aliveRECIVEEEEEEEEEEEE(): ", self.processing_thread.is_alive())
        self.is_receiving = False

    def subscribe(self, message_id: classes.Parameter, callback):
        """Sottoscrivi un messaggio con l'ID specificato e associa una callback per la gestione del messaggio."""
        if message_id not in self.subscribers:
            self.subscribers[message_id] = []
        self.subscribers[message_id].append(callback)

    def subscribe_list(self, message_list: list, callback):
        """Overwrite: Sottoscrivi tutti i messaggi con l'ID specificato e associa una callback per la gestione del
        messaggio."""
        for message in message_list:
            self.subscribe(message_id=message.arbitration_id, callback=callback)

    def receive_messages(self):
        """Ricevi e gestisci i messaggi sulla rete CAN."""
        while not self.stop_receiving_event.is_set():
            if not self.ensure_connection():
                time.sleep(1)  # Aspetta un po' prima di riprovare a connettersi
                continue

            try:
                message = self.bus.recv(5)  # TO CHANGE
                print("can_ : ",message )
                print("is_aliveRECIVE(): ", self.processing_thread.is_alive())

                if message is None:
                    print("Nessun messaggio ricevuto entro il timeout")
                    continue

                self.message_queue.put(message)

            except can.CanError as e:
                print(f"Errore durante la ricezione del messaggio: {e}")
                time.sleep(1)  # Aspetta un po' prima di riprovare a ricevere

    def process_messages(self):
        """Elabora i messaggi dalla coda e chiama le callback appropriate."""

        while not self.stop_receiving_event.is_set():
            print("size: ", self.message_queue.qsize())
            message = self.message_queue.get()
            if message is None:
                break
            logging.debug(f"Elaborazione del messaggio: {message}")
            if message.arbitration_id in self.subscribers:
                for callback in self.subscribers[message.arbitration_id]:
                    try:
                        callback(message)
                    except Exception as e:
                        logging.error(f"Errore durante l'elaborazione del messaggio: {e}")

            self.message_queue.task_done()

    def start_receiving(self):
        """Avvia il thread per ricevere i messaggi."""

        self.is_receiving = True
        self.stop_receiving_event.clear()
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.start()

    def stop_receiving(self):
        """Ferma il thread di ricezione."""
        print("STOP RECEIVING")
        self.is_receiving = False
        self.stop_receiving_event.set()
        if self.receive_thread.is_alive():
            self.receive_thread.join(1)
        self.message_queue.put(None)
        self.processing_thread.join()

    def reset_subscribers(self):
        self.subscribers = {}

    def status(self):
        return self.is_receiving


class CANSender(CanInterface):
    def __init__(self):
        super().__init__()
        self.send_thread = None
        self.message_queue = queue.Queue()
        self.lock = threading.Lock()
        self.stop_sending_event = threading.Event()
        self.sending_thread = threading.Thread(target=self.process_queue)
        self.sending_thread.daemon = True
        self.sending_thread.start()
        self.messages_to_send = []
        self.is_sending = False

    def process_queue(self):
        while not self.stop_sending_event.is_set():
            message = self.message_queue.get()
            print("QUI FUNZIONA")
            if message is None:
                break
            self.send_one_message(message)
            self.message_queue.task_done()

    def send_one_message(self, message):
        try:
            with self.lock:

                arbitration_id = message.arbitration_id
                data = message.data
                is_extended_id = message.is_extended_id
                msg = can.Message(arbitration_id=arbitration_id, data=data, is_extended_id=is_extended_id)
                self.bus.send(msg)
                print(f"Messaggio inviato: {msg}")

        except can.CanError as e:
            print(f"Errore durante l'invio del messaggio: {e}")

    def add_message_to_queue(self, message):
        self.message_queue.put(message)

    def stop_sending(self):
        self.stop_sending_event.set()
        self.message_queue.put(None)
        self.sending_thread.join()

    def send_messages_periodically(self, messages, interval):

        while not self.stop_sending_event.is_set():
            print("is_aliveSENDER(): ", self.sending_thread.is_alive())
            if not self.ensure_connection():
                time.sleep(1)
                continue

            for message in messages:
                self.add_message_to_queue(message)
                time.sleep(0.5)

            time.sleep(interval)

    def subscribe(self, message):
        # fare un confronto con tutti i subscribe
        self.messages_to_send.append(message)

    def reset_subscribers(self):
        self.messages_to_send = []

    def subscribe_list(self, message_list):
        for message in message_list:
            self.subscribe(message)

    def start_sending_periodically(self, interval):
        self.is_sending = True
        if self.send_thread is not None and self.send_thread.is_alive():
            print("Il thread di invio è già in esecuzione.")
            return

        self.stop_sending_event.clear()
        self.send_thread = threading.Thread(target=self.send_messages_periodically, args=(self.messages_to_send,
                                                                                          interval))
        self.send_thread.start()

    def stop_sending_periodically(self):
        self.is_sending = False
        self.stop_sending_event.set()
        if self.send_thread is not None:
            self.send_thread.join()

    def status(self):
        return self.is_sending


def attivi():
    # Ottieni tutti i thread attivi
    thread_attivi = threading.enumerate()
    print("Thread attivi:", thread_attivi)
