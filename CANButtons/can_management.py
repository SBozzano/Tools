import can
import logging
import time
import threading


class CanInterface:
    def __init__(self, interface='ixxat', channel=0, bitrate=500000):
        # Parametri di configurazione
        self.interface = interface
        self.channel = channel
        self.bitrate = bitrate

        # Abilita il logging di debug
        logging.basicConfig(level=logging.DEBUG)

        # Configura il bus CAN
        self.bus = None
        self.configure_bus()

        # Timer per l'invio dei messaggi
        self.running = False
        self.shutdown_event = threading.Event()
        self.timer_thread = None
        self.sending_params = None
        self.subscribers = {}
        self.stop_event = threading.Event()

        # Crea un thread per la ricezione dei messaggi
        self.receive_thread = threading.Thread(target=self.receive_messages)

    def configure_bus(self):
        try:
            self.bus = can.interface.Bus(interface=self.interface, channel=self.channel, bitrate=self.bitrate)
            print("Interfaccia CAN configurata correttamente")
        except can.CanError as e:
            print(f"Errore nella configurazione dell'interfaccia CAN: {e}")
            self.bus = None

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

    def reconnect(self):
        """Tenta di riconnettere l'interfaccia CAN in modo continuo."""
        while True:

            print("Tentativo di riconnessione...")
            self.shutdown()  # Chiude qualsiasi connessione CAN esistente
            time.sleep(1)  # Attendere prima di tentare di riconnettersi
            self.configure_bus()  # Tenta di riconnettersi
            if self.is_connected():
                print("Riconnessione riuscita.")
                arbitration_id, data, is_extended_id, interval = self.sending_params
                print("inizio ad inviare")
                if self.running:
                    print("close")
                    self.stop_sending()
                time.sleep(1)
                self.start_sending(arbitration_id,data,is_extended_id, interval)  # Riprendi l'invio dei messaggi in loop
                break  # Esci dal ciclo se la riconnessione ha avuto successo

    def send_message(self, arbitration_id, data, is_extended_id=False):
        if self.bus is None or not self.is_connected():
            print("Bus CAN non configurato o non connesso. Tentativo di riconnessione...")

            self.reconnect()
            if not self.is_connected():
                print("Riconnessione fallita. Impossibile inviare il messaggio.")
                return

        msg = can.Message(arbitration_id=arbitration_id, data=data, is_extended_id=is_extended_id)

        try:
            self.bus.send(msg)
            print("Messaggio inviato correttamente")
        except can.CanError as e:
            print(f"Errore durante l'invio del messaggio: {e}")
            self.reconnect()  # Tenta di riconnettersi se c'è un errore durante l'invio

    def receive_message(self, expected_id=None, timeout=1.0):
        if self.bus is None or not self.is_connected():
            print("Bus CAN non configurato o non connesso. Tentativo di riconnessione...")
            self.reconnect()
            if not self.is_connected():
                print("Riconnessione fallita. Impossibile ricevere messaggi.")
                return None

        try:
            while True:
                message = self.bus.recv(timeout)
                if message is None:
                    print("Nessun messaggio ricevuto entro il timeout")
                    return None
                if expected_id is None or message.arbitration_id == expected_id:
                    print(f"Messaggio ricevuto: {message}")
                    return message
                print(f"Messaggio scartato con ID: {message.arbitration_id}")
        except can.CanError as e:
            print(f"Errore durante la ricezione del messaggio: {e}")
            return None

    def subscribe(self, message_id, callback):
        """Sottoscrivi un messaggio con l'ID specificato e associa una callback per la gestione del messaggio."""
        if message_id not in self.subscribers:
            self.subscribers[message_id] = []

        self.subscribers[message_id].append(callback)

    def receive_messages(self):
        """Ricevi e gestisci i messaggi sulla rete CAN."""
        if self.bus is None or not self.is_connected():
            print("Bus CAN non configurato o non connesso. Tentativo di riconnessione...")
            self.reconnect()
            if not self.is_connected():
                print("Riconnessione fallita. Impossibile ricevere messaggi.")
                return None
        try:
            while not self.stop_event.is_set():
                message = self.bus.recv(60)                                                                       #FFFF
                if message is None:
                    print("Nessun messaggio ricevuto entro il timeout")
                    return None
                if message.arbitration_id in self.subscribers:
                    for callback in self.subscribers[message.arbitration_id]:
                        callback(message)

              #  print(f"Messaggio scartato con ID: {message.arbitration_id}")
        except can.CanError as e:
            print(f"Errore durante la ricezione del messaggio: {e}")
            return None

    def subscribe(self, message_id, callback):
        """Sottoscrivi un messaggio con l'ID specificato e associa una callback per la gestione del messaggio."""
        if message_id not in self.subscribers:
            self.subscribers[message_id] = []

        self.subscribers[message_id].append(callback)

    def start_receive_thread(self):
        """Avvia il thread per la ricezione dei messaggi."""
        self.receive_thread.start()

    def stop_receive_thread(self):
        """Ferma il thread per la ricezione dei messaggi."""
        self.stop_event.set()
        self.receive_thread.join()
    def start_sending(self, arbitration_id, data, is_extended_id=False, interval=1.0):
        """Inizia a inviare messaggi in loop con un intervallo specificato."""
        print("invio0")
        self.running = True
        self.shutdown_event.clear()
        self.sending_params = (arbitration_id, data, is_extended_id, interval)

        def send_loop():
            while self.running and not self.shutdown_event.is_set():
                if self.sending_params is not None:
                    arbitration_id, data, is_extended_id, interval = self.sending_params
                    self.send_message(arbitration_id, data, is_extended_id)
                    time.sleep(interval)
                # else:
                #     time.sleep(1)

        self.timer_thread = threading.Thread(target=send_loop)
        self.timer_thread.start()

    def stop_sending(self):
        print("stopped")
        """Ferma l'invio dei messaggi in loop."""
        self.running = False
        self.shutdown_event.set()
        if self.timer_thread is not None and threading.current_thread() != self.timer_thread:
            self.timer_thread.join()
            self.timer_thread = None
        else:
            print(
                "Attenzione: Il thread di invio sta tentando di unirsi a se stesso o il thread non è stato inizializzato correttamente.")

    def shutdown(self):
        self.stop_sending()
        if self.bus is not None:
            try:
                self.bus.shutdown()
                print("Bus CAN chiuso correttamente")
                self.bus = None
            except can.CanError as e:
                print(f"Errore durante l'invio del messaggio: {e}")


