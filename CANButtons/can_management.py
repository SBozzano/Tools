import can
import logging
import time
import threading
import queue

import classes

class CanInterface:
    def __init__(self, interface='ixxat', channel=0, bitrate=500000):
        self.bus = None
        self.interface = interface
        self.channel = channel
        self.bitrate = bitrate
        self.configure_bus()

        logging.basicConfig(level=logging.DEBUG)

    def configure_bus(self):
        try:
            self.bus = can.interface.Bus(interface=self.interface, channel=self.channel, bitrate=self.bitrate)
            print("Interfaccia CAN configurata correttamente")
        except can.CanError as e:
            print(f"Errore nella configurazione dell'interfaccia CAN: {e}")
            self.bus = None

    def get_bus(self):
        return self.bus

    def is_connected(self):
        if self.bus is None:
            return False
        try:
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

class CANReceiver:
    def __init__(self):
        self.bus = None
        self.receive_thread = None
        self.subscribers = {}  # Dizionario degli ID di arbitraggio con i relativi callback
        self.stop_receiving_event = threading.Event()
        self.message_queue = queue.Queue()
        self.processing_thread = threading.Thread(target=self.process_messages)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        self.is_receiving = False

    def set_bus(self, bus):
        self.bus = bus

    def subscribe(self, message_id, callback):
        """Sottoscrivi un messaggio con l'ID specificato e associa una callback per la gestione del messaggio."""
        if message_id not in self.subscribers:
            self.subscribers[message_id] = []
        self.subscribers[message_id].append(callback)

    def subscribe_list(self, message_list, callback):
        """Sottoscrivi tutti i messaggi con l'ID specificato e associa una callback per la gestione del messaggio."""
        for message in message_list:
            self.subscribe(message.arbitration_id, callback)

    def receive_messages(self):
        """Ricevi e gestisci i messaggi sulla rete CAN."""
        while not self.stop_receiving_event.is_set():
            if self.bus is None:
                time.sleep(1)
                continue

            try:
                message = self.bus.recv(5)
                if message is None:
                    logging.debug("Nessun messaggio ricevuto entro il timeout")
                    continue

                self.message_queue.put(message)
            except can.CanError as e:
                logging.error(f"Errore durante la ricezione del messaggio: {e}")
                time.sleep(1)

    def process_messages(self):
        """Elabora i messaggi dalla coda e chiama le callback appropriate."""
        while True:
            message = self.message_queue.get()
            if message is None:
                break
            print("size recive: ", self.message_queue.qsize())
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
        if self.receive_thread is not None and self.receive_thread.is_alive():
            logging.warning("Il thread di ricezione è già in esecuzione.")
            return

        self.is_receiving = True
        self.stop_receiving_event.clear()
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.start()

    def stop_receiving(self):
        """Ferma il thread di ricezione."""
        self.is_receiving = False
        self.stop_receiving_event.set()
        if self.receive_thread is not None:
            self.receive_thread.join()
        self.receive_thread = None
        self.message_queue.put(None)  # Per sbloccare il thread di elaborazione


    def reset_subscribers(self):
        self.subscribers = {}

    def status(self):
        return self.is_receiving

class CANSender:
    def __init__(self):
        self.send_thread = None
        self.bus = None
        self.message_queue = queue.Queue()
        self.lock = threading.Lock()
        self.stop_sending_event = threading.Event()
        self.sending_thread = threading.Thread(target=self.process_queue)
        self.sending_thread.daemon = True
        self.sending_thread.start()
        self.messages_to_send = []
        self.is_sending = False
        self.interval = None

    def set_bus(self, bus):
        self.bus = bus

    def process_queue(self):
        while True:
            message = self.message_queue.get()
            if message is None:
                break
            print("size sender: ", self.message_queue.qsize())
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
           #     print(f"Messaggio inviato: {msg}")
        except can.CanError as e:
            print(f"Errore durante l'invio del messaggio: {e}")

    def add_message_to_queue(self, message):
        self.message_queue.put(message)

    def send_messages_periodically(self):
        while not self.stop_sending_event.is_set():
            if self.bus is None:
                time.sleep(1)
                continue
            for message in self.messages_to_send:
                self.add_message_to_queue(message)
             #   time.sleep(0.5)  # Ritardo tra i messaggi
            time.sleep(self.interval)  # Intervallo tra i cicli

    def subscribe(self, message):
        self.messages_to_send.append(message)

    def reset_subscribers(self):
        self.messages_to_send = []

    def subscribe_list(self, message_list):
        for message in message_list:
            self.subscribe(message)

    def start_sending_periodically(self, interval):
        self.interval = interval
        self.is_sending = True
        if self.send_thread is not None and self.send_thread.is_alive():
            print("Il thread di invio è già in esecuzione.")
            return
        self.stop_sending_event.clear()
        self.send_thread = threading.Thread(target=self.send_messages_periodically)
        self.send_thread.start()

    def stop_sending_periodically(self):
        self.is_sending = False
        self.stop_sending_event.set()
        if self.send_thread is not None:
            self.send_thread.join()
        self.send_thread = None

    def status(self):
        return self.is_sending

def attivi():
    thread_attivi = threading.enumerate()
    print("Thread attivi:", thread_attivi)


class ConnectionMonitor:
    def __init__(self, can_interface):
        self.can_interface = can_interface
        self.monitor_thread = threading.Thread(target=self.monitor_connection)
        self.monitor_thread.daemon = True
        self.running = False

    def start(self):
        self.running = True
        self.monitor_thread.start()

    def stop(self):
        self.running = False

    def monitor_connection(self):
        while self.running:
            if not self.can_interface.is_connected():
                print("Connessione persa. Tentativo di riconnessione...")
                self.can_interface.reconnect()
            time.sleep(1)  # Controllo ogni secondo