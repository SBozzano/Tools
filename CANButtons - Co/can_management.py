import can
import logging
import time
import threading
import classes


class CanInterface:
    def __init__(self, interface='ixxat', channel=0, bitrate=500000):
        # Parametri di configurazione
        self.interface = interface
        self.channel = channel
        self.bitrate = bitrate
       # self.stop_event = threading.Event()
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

    #
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

    def reconnect(self, retries=5, delay=2):
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

    # def is_ixxat_available(self):
    #     """Controlla se l'interfaccia ixxat è disponibile."""
    #     try:
    #         test_bus = can.interface.Bus(interface='ixxat', channel=0, bitrate=500000)
    #         test_bus.shutdown()
    #         return True
    #     except can.CanError as e:
    #         print(f"L'interfaccia ixxat non è disponibile: {e}")
    #         return False

    # def reconnect(self):
    #     """Tenta di riconnettere l'interfaccia CAN in modo continuo."""
    #     while True:
    #
    #         print("Tentativo di riconnessione...")
    #         self.shutdown()  # Chiude qualsiasi connessione CAN esistente
    #         time.sleep(1)  # Attendere prima di tentare di riconnettersi
    #         self.configure_bus()  # Tenta di riconnettersi
    #         if self.is_connected():
    #             print("Riconnessione riuscita.")
    #
    #             if self.sending_params is not None:
    #                 arbitration_id, data, is_extended_id, interval = self.sending_params
    #                 print("inizio ad inviare singolo")
    #                 time.sleep(1)
    #                 self.start_sending_thread(arbitration_id,data,is_extended_id, interval)  # Riprendi l'invio dei messaggi in loop
    #                 break  # Esci dal ciclo se la riconnessione ha avuto successo
    #             elif self.sending_params_array is not None:
    #                 print("inizio ad inviare array")
    #                 for message in self.sending_params_array:
    #                     arbitration_id = message.arbitration_id
    #                     data = message.data
    #                     is_extended_id = message.is_extended_id
    #
    #                     self.send_message(arbitration_id, data, is_extended_id)
    #                 interval = 1  # to fix
    #                 time.sleep(interval)
    #
    def shutdown_(self):

        #self.stop_event.set()
        if self.bus is not None:
            try:
                self.bus.shutdown()
                print("Bus CAN chiuso correttamente")
                self.bus = None
            except can.CanError as e:
                print(f"Errore durante l'invio del messaggio: {e}")





    #
    # def send_message(self, arbitration_id, data, is_extended_id=False):
    #     if self.bus is None or not self.is_connected():
    #         print("Bus CAN non configurato o non connesso. Tentativo di riconnessione...")
    #
    #         self.reconnect()
    #         if not self.is_connected():
    #             print("Riconnessione fallita. Impossibile inviare il messaggio.")
    #             return
    #
    #     msg = can.Message(arbitration_id=arbitration_id, data=data, is_extended_id=is_extended_id)
    #
    #     try:
    #         self.bus.send(msg)
    #         print("Messaggio inviato correttamente")
    #     except can.CanError as e:
    #         print(f"Errore durante l'invio del messaggio: {e}")
    #         self.reconnect()  # Tenta di riconnettersi se c'è un errore durante l'invio
    #
    # def receive_message(self, expected_id=None, timeout=1.0):
    #     if self.bus is None or not self.is_connected():
    #         print("Bus CAN non configurato o non connesso. Tentativo di riconnessione...")
    #         self.reconnect()
    #         if not self.is_connected():
    #             print("Riconnessione fallita. Impossibile ricevere messaggi.")
    #             return None
    #
    #     try:
    #         while True:
    #             message = self.bus.recv(timeout)
    #             if message is None:
    #                 print("Nessun messaggio ricevuto entro il timeout")
    #                 return None
    #             if expected_id is None or message.arbitration_id == expected_id:
    #                 print(f"Messaggio ricevuto: {message}")
    #                 return message
    #             print(f"Messaggio scartato con ID: {message.arbitration_id}")
    #     except can.CanError as e:
    #         print(f"Errore durante la ricezione del messaggio: {e}")
    #         return None
    #
    # def subscribe(self, message_id, callback):
    #     """Sottoscrivi un messaggio con l'ID specificato e associa una callback per la gestione del messaggio."""
    #     if message_id not in self.subscribers:
    #         self.subscribers[message_id] = []
    #
    #     self.subscribers[message_id].append(callback)
    #
    # def receive_messages(self):
    #     """Ricevi e gestisci i messaggi sulla rete CAN."""
    #     if self.bus is None or not self.is_connected():
    #         print("Bus CAN non configurato o non connesso. Tentativo di riconnessione...")
    #         self.reconnect()
    #         if not self.is_connected():
    #             print("Riconnessione fallita. Impossibile ricevere messaggi.")
    #             return None
    #     try:
    #         while not self.stop_event.is_set():
    #             message = self.bus.recv(10)
    #             if message is None:
    #                 print("Nessun messaggio ricevuto entro il timeout")
    #                 return None
    #             if message.arbitration_id in self.subscribers:
    #                 for callback in self.subscribers[message.arbitration_id]:
    #                     callback(message)
    #     except can.CanError as e:
    #         print(f"Errore durante la ricezione del messaggio: {e}")
    #         return None
    #
    # def subscribe(self, message_id, callback):
    #     """Sottoscrivi un messaggio con l'ID specificato e associa una callback per la gestione del messaggio."""
    #     if message_id not in self.subscribers:
    #         self.subscribers[message_id] = []
    #
    #     self.subscribers[message_id].append(callback)

    # def start_sending_package(self, array_messages: list):
    #     """Inizia a inviare messaggi in loop con un intervallo specificato."""
    #     print("invio0")
    #     self.running_sending = True
    #     self.shutdown_event.clear()
    #
    #     self.sending_params_array = array_messages
    #     self.sending_params = None
    #
    #     def send_loop():
    #         while self.running_sending and not self.shutdown_event.is_set():
    #             if self.sending_params_array is not None:
    #                 for message in self.sending_params_array:
    #                     arbitration_id = message.arbitration_id
    #                     data = message.data
    #                     is_extended_id = message.is_extended_id
    #
    #                     self.send_message(arbitration_id, data, is_extended_id)
    #                 interval = 1                                                            #to fix
    #                 time.sleep(interval)
    #             # else:
    #             #     time.sleep(1)
    #
    #     self.timer_thread_sending = threading.Thread(target=send_loop)
    #     self.timer_thread_sending.start()
    #
    # # def start_reading_package(self):
    # #     self.running_reading = True
    # #     self.shutdown_event.clear()
    #
    #
    # def start_sending_thread(self, arbitration_id, data, is_extended_id=False, interval=1.0):
    #     """Inizia a inviare messaggi in loop con un intervallo specificato."""
    #     print("invio0")
    #     self.running_sending = True
    #     self.shutdown_event.clear()
    #     self.sending_params = (arbitration_id, data, is_extended_id, interval)
    #     self.sending_params_array = None
    #
    #     def send_loop():
    #         while self.running_sending and not self.shutdown_event.is_set():
    #             if self.sending_params is not None:
    #                 arbitration_id, data, is_extended_id, interval = self.sending_params
    #                 self.send_message(arbitration_id, data, is_extended_id)
    #                 time.sleep(interval)
    #             # else:
    #             #     time.sleep(1)
    #
    #     self.timer_thread_sending = threading.Thread(target=send_loop)
    #     self.timer_thread_sending.start()
    #
    # def start_receiving_thread(self):
    #     """Avvia il thread per la ricezione dei messaggi."""
    #     self.receive_thread = threading.Thread(target=self.receive_messages)
    #     self.receive_thread.start()
    #
    # def stop_receiving_thread(self):
    #     """Ferma il thread per la ricezione dei messaggi."""
    #     self.stop_event.set()
    #     self.receive_thread.join()
    #
    #
    #
    # def stop_sending_thread(self):
    #     print("stopped")
    #     """Ferma l'invio dei messaggi in loop."""
    #     self.running_sending = False
    #     self.shutdown_event.set()
    #     if self.timer_thread_sending is not None and threading.current_thread() != self.timer_thread_sending:
    #         self.timer_thread_sending.join()
    #         self.timer_thread_sending = None
    #     else:
    #         print(
    #             "Attenzione: Il thread di invio sta tentando di unirsi a se stesso o il thread non è stato inizializzato correttamente.")


class CANReceiver(CanInterface):
    def __init__(self):

        super().__init__()
        self.receive_thread = None

        self.subscribers = {}  # Dizionario degli ID di arbitraggio con i relativi callback
        self.stop_receiving_event = threading.Event()

    def subscribe(self, message_id, callback):
        """Sottoscrivi un messaggio con l'ID specificato e associa una callback per la gestione del messaggio."""

        if message_id not in self.subscribers:
            self.subscribers[message_id] = []

        self.subscribers[message_id].append(callback)
        print(self.subscribers)

    def receive_messages(self):
        """Ricevi e gestisci i messaggi sulla rete CAN."""
      #  print("test")
        while not self.stop_receiving_event.is_set():

            if not self.ensure_connection():
                time.sleep(1)  # Aspetta un po' prima di riprovare a connettersi
                continue

            try:
                message = self.bus.recv(1000)
                if message is None:
                    print("Nessun messaggio ricevuto entro il timeout")
                    continue

                if message.arbitration_id in self.subscribers:
                    print("fine: ",message.arbitration_id)
                    for callback in self.subscribers[message.arbitration_id]:
                        callback(message)

            except can.CanError as e:
                print(f"Errore durante la ricezione del messaggio: {e}")
                time.sleep(1)  # Aspetta un po' prima di riprovare a ricevere



    def start_receiving(self):
        """Avvia il thread per ricevere i messaggi."""
      #  print("start reciving")
        self.stop_receiving_event.clear()
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.start()

    def stop_receiving(self):
        """Ferma il thread di ricezione."""
       # self.subscribers = {}
      #  self.rest_subscribers()

        self.stop_receiving_event.set()

#        self.receive_thread.set()
        if self.receive_thread.is_alive():

            self.receive_thread.join(1)

     #   self.stop_event.set()
        print("stop")

    def rest_subscribers(self):
        self.subscribers = {}
    def attivi(self):

        # Ottieni tutti i thread attivi
        thread_attivi = threading.enumerate()


        # Stampa i thread attivi
        print("Thread attivi:", thread_attivi)

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
        #print("sent")
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
                    print(msg)
                    time.sleep(0.5)
                    self.bus.send(msg)
                time.sleep(interval)
            except can.CanError as e:
                print(f"Errore durante l'invio del messaggio: {e}")
                time.sleep(1)  # Aspetta un po' prima di riprovare a inviare


    def start_sending(self, messages=None, interval=None):
        """Avvia il thread per inviare messaggi periodici."""
       # print("start sending")
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
            print("start")
            self.send_thread.start()

        else:
            print("Messaggio e intervallo devono essere specificati prima di avviare l'invio.")

    def stop_sending(self):
        """Ferma il thread di invio."""
        self.is_sending = False
        self.stop_sending_event.set()

 #       self.send_thread.set()
        if self.send_thread.is_alive():
            self.send_thread.join()#timeout=1
   #     self.stop_event.set()

    def attivi(self):

        # Ottieni tutti i thread attivi
        thread_attivi = threading.enumerate()

        # Stampa i thread attivi
        print("Thread attivi:", thread_attivi)

    def send_one_message(self, message):
        try:
            arbitration_id = message.arbitration_id
            data = message.data
            is_extended_id = message.is_extended_id
            msg = can.Message(arbitration_id=arbitration_id, data=data, is_extended_id=is_extended_id)
            print(msg)

            self.bus.send(msg)

        except can.CanError as e:
            print(f"Errore durante l'invio del messaggio: {e}")
