import time
import tkinter as tk
from tkinter import ttk
import classes
import struct
import threading
import json_management


class DefaultNotebook:
    """ Classe madre per tutti i notebook """

    def __init__(self, root):

        ttk.Style(root).configure('red.TButton', background='red')
        ttk.Style(root).configure('green.TButton', background='green')
        ttk.Style(root).configure('white.TButton', background='white')
        self.frame = ttk.Frame(root)  # , style='green.TButton'
        self.receiver = None
        self.sender = None

        self.subscribers_list = []

    def set_receiver(self, new_receiver):
        self.receiver = new_receiver

    def set_sender(self, new_sender):
        self.sender = new_sender

    def configure_grid(self, rows, columns, row_min_size, column_min_size):
        """ configurazione dimensione celle:
            rows = numero di righe da configurare
            columns = numero di colonne da configurare
            row_min_size = dimensione minima della riga
            column_min_size = dimensione minima della colonna
            """

        for row in range(rows):
            self.frame.grid_rowconfigure(row, minsize=row_min_size)
        for column in range(columns):
            self.frame.grid_columnconfigure(column, minsize=column_min_size)

    def set_subscribers(self) -> None:
        pass

    def receive(self, message_rec) -> None:
        pass

class CustomWidget(DefaultNotebook):
    """ finestra cusom configuata con bottoni e output """

    def __init__(self, root):
        super().__init__(root)
        max_rows = 3
        max_columns = classes.max_columns
        row_min_size = 20
        column_min_size = 130
        self.is_connected = False

        self.fault_text = tk.StringVar()

        self.button_enable_charge = ttk.Button(self.frame, text="ENABLE CHARGE",
                                               command=self.charge,
                                               style='white.TButton')
        self.button_enable_discharge = ttk.Button(self.frame, text="ENABLE DISCHARGE",
                                                  command=self.discharge,
                                                  style='white.TButton')
        self.label_sw1 = tk.Label(self.frame, text="CHARGE", borderwidth=2, relief="groove", bg="white", width=12,
                                  height=1)
        self.label_sw2 = tk.Label(self.frame, text="DISCHARGE", borderwidth=2, relief="groove", bg="white", width=12,
                                  height=1)
        self.label_fault = tk.Label(self.frame, text="FAULT", borderwidth=2, relief="groove", bg="white", width=6,
                                    height=1)
        self.button_reset_fault = ttk.Button(self.frame, text="RESET FAULT",
                                             command=self.reset_fault,
                                             style='white.TButton')
        self.label_fault_text = tk.Label(self.frame, textvariable=self.fault_text)
        self.configure_grid(max_rows, max_columns, row_min_size, column_min_size)

        self.running = False
        self.monitor_thread = threading.Thread(target=self.monitor_connection)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        self.create_custom_widgets()

    def set_is_connected(self, status: bool):                                                               # cambiare
        """ status = status da settare"""

        self.is_connected = status

    def monitor_connection(self) -> None:
        """ controllo periodicamente se la connessione è attiva, se non lo è disabilito tuttii bottoni"""

        self.running = True
        while self.running:
            if not self.is_connected:
                self.button_enable_charge.config(state='disable')
                self.button_enable_discharge.config(state='disable')
                self.button_reset_fault.config(state='disable')
            time.sleep(0.5)

    def stop(self) -> None:
        self.running = False

    def create_custom_widgets(self) -> None:
        """ posiziono i widgets """
        self.button_enable_charge.grid(column=0, row=0, padx=10, pady=10)
        self.button_enable_discharge.grid(column=1, row=0, padx=10, pady=10)

        self.label_sw1.grid(column=0, row=1, padx=10, pady=10)
        self.label_sw2.grid(column=1, row=1, padx=10, pady=10)
        self.label_fault.grid(column=0, row=2, padx=10, pady=10, columnspan=2)
        self.button_reset_fault.grid(column=0, row=3, padx=10, pady=10, columnspan=2)
        self.label_fault_text.grid(column=0, row=4, padx=10, pady=10, sticky='w', columnspan=2)

    def reset_fault(self) -> None:
        """ invio un messaggio per resettare il fault del master """

        if self.sender is not None:
            self.sender.send_one_message(classes.m0x1008_NULL)

    def discharge(self) -> None:
        """  """

        if self.sender is not None:
            if self.button_enable_discharge['text'] == 'ENABLE DISCHARGE':
                self.sender.send_one_message(classes.m0x1008_DISCHARGE)

            elif self.button_enable_discharge['text'] == 'DISABLE DISCHARGE':
                self.sender.send_one_message(classes.m0x1008_NULL)

    def charge(self) -> None:
        """  """

        if self.sender is not None:
            if self.button_enable_charge['text'] == 'ENABLE CHARGE':
                self.sender.send_one_message(classes.m0x1008_CHARGE)

            elif self.button_enable_charge['text'] == 'DISABLE CHARGE':
                self.sender.send_one_message(classes.m0x1008_NULL)

    def set_subscribers(self) -> None:
        """ setto i messaggi da scrivere / leggere quando sono in questa pagina"""
        self.receiver.subscribe(message_id=classes.m0x1003.arbitration_id, callback=self.receive)
        self.sender.subscribe(message=classes.m0x1002)

    def receive(self, message_rec) -> None:
        """ elaborazione messaggio 0x1003 """
        if classes.m0x1003.arbitration_id != message_rec.arbitration_id:
            print("ERROR -- custom callback ")

        else:
            classes.m0x1003.data = message_rec.data
            datas = struct.unpack(classes.m0x1003.format, classes.m0x1003.data)
            fault = ''

            state_charge = datas[1]
            state_charge_bits = [int(bit) for bit in bin(state_charge)[2:]]
            while len(state_charge_bits) != 8:
                state_charge_bits.insert(0, 0)

            if bool(state_charge_bits[6]):
                self.label_sw1.config(bg="red")
                if self.label_fault['bg'] == 'white':
                    self.button_enable_discharge.config(state='disable', text='ENABLE DISCHARGE')
                    self.button_enable_charge.config(state='enable', text='DISABLE CHARGE')
            else:
                self.label_sw1.config(bg="white")

            if bool(state_charge_bits[7]):
                self.label_sw2.config(bg="red")
                if self.label_fault['bg'] == 'white':
                    self.button_enable_charge.config(state='disable', text='ENABLE CHARGE')
                    self.button_enable_discharge.config(state='enable', text='DISABLE DISCHARGE')
            else:
                self.label_sw2.config(bg="white")

            if bool(state_charge_bits[6]) and bool(state_charge_bits[7]):
                if self.label_fault['bg'] == 'white':
                    self.button_enable_charge.config(state='enable', text='DISABLE CHARGE')
                    self.button_enable_discharge.config(state='enable', text='DISABLE DISCHARGE')

            if not (bool(state_charge_bits[6])) and not (bool(state_charge_bits[7])):
                if self.label_fault['bg'] == 'white':
                    self.button_enable_charge.config(state='enable', text='ENABLE CHARGE')
                    self.button_enable_discharge.config(state='enable', text='ENABLE DISCHARGE')

            fault_init = 'Fault: '
            state_fault = datas[2]
            state_fault_bits = [int(bit) for bit in bin(state_fault)[2:]]

            while len(state_fault_bits) != 8:
                state_fault_bits.insert(0, 0)

            if bool(state_fault_bits[7]):
                fault += " Overcurrent "

            if bool(state_fault_bits[6]):
                fault += " OverTemperature "

            if bool(state_fault_bits[5]):
                fault += " UnderTemperature "

            if bool(state_fault_bits[4]):
                fault += " OverVoltage "

            if bool(state_fault_bits[3]):
                fault += " UnderVoltage "

            if bool(state_fault_bits[2]):
                fault += " Timeout can BMS "

            if bool(state_fault_bits[1]):
                fault += " Offset calibration failed "

            if bool(state_fault_bits[0]):
                fault += " Reference fuori specifica "

            if state_fault == 0:
                self.label_fault.config(bg="white")
                self.button_reset_fault.config(state="disable")
                self.fault_text.set("")
            else:
                self.label_fault.config(bg="red")
                self.button_enable_charge.config(state="disable")
                self.button_enable_discharge.config(state="disable")
                self.button_reset_fault.config(state="normal")
                self.fault_text.set(fault_init + fault[1:])


class DefaultWidget(DefaultNotebook):
    """ visualizzazione di default: tutti i parametri della lista classes.rx_messages_main vengono visualizzati, eccetto
    i nomi nella lista classes.rx_message_main_exception """
    def __init__(self, root):
        super().__init__(root)
        self.label_names_main = []
        self.label_messages_main = []
        self.rx_messages_main = None
        self.tx_messages_main = None

        self.max_rows = 5
        self.max_columns = classes.max_columns
        row_min_size = 20
        column_min_size = 130

        self.configure_grid(self.max_rows, self.max_columns, row_min_size, column_min_size)
        self.get_messages()
        self.create_default_widgets()

    def get_messages(self):
        json_management.load_parameters_from_json('parameters.json')
    def create_default_widgets(self) -> None:
        """ Crea un label per ogni name di ogni messaggio, ordinandoli nella griglia del frame "default" """

        column_counter = 0
        row_counter = 0

        for message in classes.rx_messages_main:
            for name in message.name:
                if not (name in classes.rx_message_main_exception):
                    new_label_name = tk.Label(self.frame, text=(name + ":"))
                    new_label_name.grid(column=column_counter, row=row_counter, padx=8, pady=8, sticky='w')
                    new_label_message = tk.Label(self.frame, text="None")
                    new_label_message.grid(column=column_counter + 1, row=row_counter, padx=8, pady=8, sticky='w')
                    self.label_names_main.append(new_label_name)
                    self.label_messages_main.append(new_label_message)
                    row_counter += 1
                    if row_counter > self.max_rows:
                        column_counter += 2

                        if column_counter > self.max_columns:
                            print("numero massimo di parametri visualizzati")
                            break
                        row_counter = 0

    def set_subscribers(self) -> None:
        self.receiver.subscribe_list(classes.rx_messages_main, self.receive)
        self.sender.subscribe_list(classes.tx_messages_main)

    def receive(self, message_rec) -> None:
        if message_rec is None:
            print("errore nella ricezione del messaggio")
        else:
            for message in classes.rx_messages_main:

                if message.arbitration_id == message_rec.arbitration_id:
                    message.data = message_rec.data
                    datas = struct.unpack(message.format, message.data)
                    for i, name in enumerate(message.name, start=0):
                        if not (name in classes.rx_message_main_exception):
                            for k, label_name in enumerate(self.label_names_main, start=0):
                                #  print ("label_name['text'][:1]: ", label_name['text'][:-1])
                                #  print ( "name: ", name)
                                if label_name['text'][:-1] == name:
                                    self.label_messages_main[k].config(text=float(datas[i]) * message.scale[i])
