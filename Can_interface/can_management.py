import can
import logging
import threading
import queue
import simply_can
import classes
from simply_can import Message
import time
import struct


def thread_attivi():
    print("Thread attivi:", threading.enumerate())


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
        self.ixxat_name = None
        self.receive_thread = None
        self.timeout = classes.timeout
        self.subscribers = {}  # Dizionario degli ID di arbitraggio con i relativi callback
        self.stop_receiving_event = threading.Event()
        self.message_queue = queue.Queue()
        self.processing_thread = threading.Thread(target=self.process_messages)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        self.is_receiving = False
        self.timeout_error = False
        self.receive_error = False

    def set_bus(self, bus):
        self.bus = bus

    def set_ixxat(self, ixxat_name):
        self.ixxat_name = ixxat_name

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

        self.timeout_error = False
        self.receive_error = False
        while not self.stop_receiving_event.is_set() and self.bus is not None:
            # if self.bus is None:
            #     time.sleep(1)
            #     continue
            message = None

            try:
                #  print("NAME: ", self.ixxat_name )
                if self.ixxat_name == classes.ixxat_available[1]:
                    message = self.bus.recv(self.timeout)
                    if message is None:
                        # logging.error("Nessun messaggio ricevuto entro il timeout")
                        if self.timeout:
                            self.timeout_error = True
                        continue
                elif self.ixxat_name == classes.ixxat_available[0]:
                    start_time = time.time()
                    # print("HERE: ", message)

                    while time.time() - start_time <= self.timeout and message is None:
                        res, message = self.bus.receive()
                        time.sleep(0.1)
                        #   print("time.time() - start_time: ", time.time() - start_time)
                        if time.time() - start_time >= self.timeout:
                            # logging.error("Nessun messaggio ricevuto entro il timeout")
                            if self.timeout:
                                self.timeout_error = True

                self.message_queue.put(message)
            except can.CanError as e:
                self.receive_error = True
                logging.error(f"Errore durante la ricezione del messaggio: {e}")
                time.sleep(1)

    def process_messages(self):
        """Elabora i messaggi dalla coda e chiama le callback appropriate."""
        message = None
        while True:
            message_gen = self.message_queue.get()
            if message_gen is None:
                break
            # print("size recive: ", self.message_queue.qsize())
            logging.debug(f"Elaborazione del messaggio: {message_gen}")

            if self.ixxat_name == classes.ixxat_available[0]:
                if message_gen.flags == 'E':
                    message = can.Message(arbitration_id=message_gen.ident, data=message_gen.payload,
                                          is_extended_id=True)
                else:
                    message = can.Message(arbitration_id=message_gen.ident, data=message_gen.payload,
                                          is_extended_id=False)

            elif self.ixxat_name == classes.ixxat_available[1]:
                message = message_gen

            if message.arbitration_id in self.subscribers:
                for callback in self.subscribers[message.arbitration_id]:
                    try:
                        if message.is_error_frame:
                            print("EROOR FRAMMEEEEE")
                        #  print("message: ", message)
                        callback(message)

                    except Exception as e:
                        logging.error(f"Errore durante l'elaborazione del messaggio: {e}")
            # print("AAAAA")

            self.message_queue.task_done()

    def get_timeout_error(self):
        return self.timeout_error

    def get_receive_error(self):
        return self.receive_error

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
        self.ixxat_name = None
        self.send_error = False
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

    def set_ixxat(self, ixxat_name):
        self.ixxat_name = ixxat_name

    def process_queue(self):
        while True:
            message = self.message_queue.get()
            if message is None:
                break
            # print("size sender: ", self.message_queue.qsize())
            self.send_one_message(message)
            self.message_queue.task_done()
            time.sleep(classes.time_between_two_messages)



    def send_one_message(self, message):
        try:
            with self.lock:
                arbitration_id = message.arbitration_id
                datas = message.data
                datas_scaled = []
                for i in range(len(datas)):
                    datas_scaled.append(datas[i] * message.scale[i])

                datas_pack = struct.pack(message.format, *datas_scaled)
                is_extended_id = message.is_extended_id
                if self.ixxat_name == classes.ixxat_available[1]:

                    msg = can.Message(arbitration_id=arbitration_id, data=datas_pack, is_extended_id=is_extended_id)
                    try:
                        self.bus.send(msg)
                        print("mess send: ", arbitration_id, datas_pack, is_extended_id)
                    except Exception as e:
                        logging.error(f"Errore durante il controllo della connessione: {e}")
                        self.send_error = True

                elif self.ixxat_name == classes.ixxat_available[0]:
                    if is_extended_id:
                        msg = Message(ident=arbitration_id, payload=datas_pack, flags='E')
                    else:
                        msg = Message(ident=arbitration_id, payload=datas_pack)  # , flags='R'

                    self.send_message(self.bus, msg)

        except can.CanError as e:
            logging.error(f"Errore durante l'invio del messaggio: {e}")
            self.send_error = True

    def add_message_to_queue(self, message):

        self.message_queue.put(message)

    def send_messages_periodically(self):

        while not self.stop_sending_event.is_set() and self.bus is not None:

            for message in self.messages_to_send:
                self.add_message_to_queue(message)

            time.sleep(self.interval)  # Intervallo tra i cicli

    def subscribe(self, message):
        self.messages_to_send.append(message)

    def reset_subscribers(self):
        self.messages_to_send = []

    def subscribe_list(self, message_list):
        for message in message_list:

            if int(message.period) == -1:

                self.subscribe(message)

    def get_send_error(self):
        return self.send_error

    def start_sending_periodically(self, interval):

        self.interval = interval
        self.is_sending = True
        self.send_error = False
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

    def send_message(self, simply, msg):
        try:
            simply.send(msg)
            #   print("messaggio inviato: ", msg)
            simply.flush_tx_fifo()
        except Exception as e:
            self.send_error = True
            logging.error(f"Errore durante il controllo della connessione: {e}")


class SimplyCanInterface:
    def __init__(self, ser_port, baudrate):
        self.status = False
        self.SimplyObj = None
        self.ser_port = ser_port
        self.baudrate = baudrate
        self.simply = None
        self.configure_bus()
        self.running = False
        self.monitor_thread = threading.Thread(target=self.monitor_connection)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def get_status(self):
        return self.status

    def configure_bus(self):
        print("\n#### simplyCAN 2.0 (c) 2018-2022 HMS ####\n")

        self.simply = simply_can.SimplyCAN()
        self.SimplyObj = self.simply
        if not self.simply.open(self.ser_port):
            self.error(self.simply)

        else:
            print(f"Serial port {self.ser_port} opened successfully.")
            identify = self.simply.identify()
            if not identify:
                self.error(self.simply)
            else:
                print("Firmware version:", identify.fw_version.decode("utf-8"))
                print("Hardware version:", identify.hw_version.decode("utf-8"))
                print("Product version: ", identify.product_version.decode("utf-8"))
                print("Product string:  ", identify.product_string.decode("utf-8"))
                print("Serial number:   ", identify.serial_number.decode("utf-8"))

                res = self.simply.stop_can()  # to be on the safer side
                res &= self.simply.initialize_can(self.baudrate)
                res &= self.simply.start_can()
                self.status = True

    def error(self, simply):
        err = simply.get_last_error()
        print("Error:", simply.get_error_string(err))

    def get_bus(self):
        return self.simply

    def monitor_connection(self):
        self.running = False  # TRUE
        while self.running:
            time.sleep(2)

            err = self.simply.get_last_error()
            if err:
                error_message = self.simply.get_error_string(err)
                logging.error(f"c: {error_message}")
                if ("API is busy" or "Serial communication port is closed") in error_message:
                    time.sleep(1)  # Attendi un po' prima di ritentare
                else:
                    self.status = False
        #     self.send_error = True

        # if not self.check_connection():
        #     print("Connessione persa.")
        #     self.status = False
        #

    # def check_connection(self):
    #     try:
    #         logging.debug("Inizio verifica connessione")
    #         # Invia un messaggio di test per verificare la connessione
    #         test_message = Message(ident=0x7FF, payload=b'\x00')
    #         self.simply.send(test_message)
    #         self.simply.flush_tx_fifo()
    #         logging.debug("Verifica connessione riuscita")
    #         return True
    #     except Exception as e:
    #         logging.error(f"Errore durante il controllo della connessione: {e}")
    #         time.sleep(1)  # Pausa prima di ritentare
    #         return False
    #     finally:
    #         err = self.simply.get_last_error()
    #         if err:
    #             error_message = self.simply.get_error_string(err)
    #             logging.error(f"Errore rilevato: {error_message}")
    #             if "API is busy" in error_message:
    #                 time.sleep(1)  # Attendi un po' prima di ritentare
    #                 return True
    #             self.running = False
    #             return False
    #         return True

    def close(self):
        self.running = False
        if self.simply:
            self.simply.close()
        print(f"Serial port {self.ser_port} closed successfully.")

    def signal_handler(self):
        self.status = False
        if self.SimplyObj:
            self.SimplyObj.close()
        self.close()
