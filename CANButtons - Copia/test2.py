import can
import logging


class CanInterface:
    def __init__(self, interface='ixxat', channel=0, bitrate=500000):
        # Abilita il logging di debug
        logging.basicConfig(level=logging.DEBUG)

        try:
            self.bus = can.interface.Bus(interface=interface, channel=channel, bitrate=bitrate)
            print("Interfaccia CAN configurata correttamente")
        except can.CanError as e:
            print(f"Errore nella configurazione dell'interfaccia CAN: {e}")
            self.bus = None

    def send_message(self, arbitration_id, data, is_extended_id=False):
        if self.bus is None:
            print("Bus CAN non configurato correttamente. Impossibile inviare il messaggio.")
            return

        msg = can.Message(arbitration_id=arbitration_id, data=data, is_extended_id=is_extended_id)

        try:
            self.bus.send(msg)
            print("Messaggio inviato correttamente")
        except can.CanError as e:
            print(f"Errore durante l'invio del messaggio: {e}")

    def receive_message(self, expected_id=None, timeout=1.0):
        if self.bus is None:
            print("Bus CAN non configurato correttamente. Impossibile ricevere messaggi.")
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

    def shutdown(self):
        if self.bus is not None:
            self.bus.shutdown()
            print("Bus CAN chiuso correttamente")