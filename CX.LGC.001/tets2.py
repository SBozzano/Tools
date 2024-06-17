from can_management import CanInterface
from can_management import CANReceiver
from can_management import CANSender
import time
import can

if __name__ == "__main__":
    can_interface = CanInterface(interface='ixxat', channel=0, bitrate=500000)

    can_sender = CANSender()
    can_receiver = CANReceiver()

    can_sender.set_bus(can_interface.get_bus())
    can_receiver.set_bus(can_interface.get_bus())

    def on_message_received(message):
        print(f"Messaggio ricevuto: {message}")

    can_receiver.subscribe(0x1003, on_message_received)

    message1 = can.Message(arbitration_id=0x1002, data=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], is_extended_id=True)
   # message2 = can.Message(arbitration_id=0x456, data=[0x05, 0x06, 0x07, 0x08], is_extended_id=False)

    can_sender.subscribe(message1)
  #  can_sender.subscribe(message2)

    can_receiver.start_receiving()
    can_sender.start_sending_periodically(interval=2)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        can_sender.stop_sending_periodically()
        can_receiver.stop_receiving()