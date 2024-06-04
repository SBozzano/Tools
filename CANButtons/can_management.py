import can
import logging
import time
import threading


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

        # self.stop_event.set()
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
        self.subscribers = {}                               # Dizionario degli ID di arbitraggio con i relativi callback
        self.stop_receiving_event = threading.Event()

    def subscribe(self, message_id, callback):
        """Sottoscrivi un messaggio con l'ID specificato e associa una callback per la gestione del messaggio."""
        if message_id not in self.subscribers:
            self.subscribers[message_id] = []
        self.subscribers[message_id].append(callback)


    def receive_messages(self):
        """Ricevi e gestisci i messaggi sulla rete CAN."""

        while not self.stop_receiving_event.is_set():

            if not self.ensure_connection():
                time.sleep(1)  # Aspetta un po' prima di riprovare a connettersi
                continue

            try:
                message = self.bus.recv(1)
                if message is None:
                    print("Nessun messaggio ricevuto entro il timeout")
                    continue

                if message.arbitration_id in self.subscribers:
                    for callback in self.subscribers[message.arbitration_id]:
                        callback(message)

            except can.CanError as e:
                print(f"Errore durante la ricezione del messaggio: {e}")
                time.sleep(1)  # Aspetta un po' prima di riprovare a ricevere

    def start_receiving(self):
        """Avvia il thread per ricevere i messaggi."""

        self.stop_receiving_event.clear()
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.start()

    def stop_receiving(self):
        """Ferma il thread di ricezione."""

        self.stop_receiving_event.set()
        if self.receive_thread.is_alive():
            self.receive_thread.join(1)

    def rest_subscribers(self):
        self.subscribers = {}



class CANSender(CanInterface):
    def __init__(self):
        super().__init__()
        self.send_thread = None
        self.messages = None
        self.interval = None
        self.is_sending = False
        self.stop_sending_event = threading.Event()
        self.test = False

    def send_messages(self, messages, interval):
        """Invia messaggi periodici sulla rete CAN."""
        # print("sent")
        self.messages = messages
        self.interval = interval
        while not self.stop_sending_event.is_set():
            if not self.ensure_connection():
                time.sleep(1)  # Aspetta un po' prima di riprovare a connettersi
                continue

            try:
                for message in messages:
                    arbitration_id = message.arbitration_id
                    data = message.data
                    is_extended_id = message.is_extended_id
                    msg = can.Message(arbitration_id=arbitration_id, data=data, is_extended_id=is_extended_id)
                    #print(msg)
                    time.sleep(0.5)
                    self.bus.send(msg)
                time.sleep(interval)
            except can.CanError as e:
                print(f"Errore durante l'invio del messaggio: {e}")
                time.sleep(1)  # Aspetta un po' prima di riprovare a inviare

    def start_sending(self, messages=None, interval=None):
        """Avvia il thread per inviare messaggi periodici."""

        if self.is_sending:
            print("Il thread di invio è già in esecuzione.")
            return

        if messages:
            self.messages = messages

        if interval:
            self.interval = interval

        if self.messages and self.interval:
            self.is_sending = True
            self.stop_sending_event.clear()
            self.send_thread = threading.Thread(target=self.send_messages, args=(self.messages, self.interval))
            self.send_thread.start()
        else:
            print("Messaggio e intervallo devono essere specificati prima di avviare l'invio.")

    def stop_sending(self):
        """Ferma il thread di invio."""
        self.is_sending = False
        self.stop_sending_event.set()

        if self.send_thread.is_alive():
            self.send_thread.join()

    def send_one_message(self, message):
        try:
            arbitration_id = message.arbitration_id
            data = message.data
            is_extended_id = message.is_extended_id
            msg = can.Message(arbitration_id=arbitration_id, data=data, is_extended_id=is_extended_id)
            # print(msg)
            self.bus.send(msg)

        except can.CanError as e:
            print(f"Errore durante l'invio del messaggio: {e}")


def attivi():
    # Ottieni tutti i thread attivi
    thread_attivi = threading.enumerate()
    print("Thread attivi:", thread_attivi)
