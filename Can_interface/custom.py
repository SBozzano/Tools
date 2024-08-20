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

    def refresh_messages(self, tx_messages, rx_messages, ignore_messages, leds_messages):
        pass


class CustomWidget(DefaultNotebook):
    """ finestra cusom configuata con bottoni e output """

    def __init__(self, root, tx_messages, rx_messages, leds_messages):
        super().__init__(root)
        self.is_refreshing = False
        self.tx_messages = tx_messages
        self.rx_messages = rx_messages
        self.leds_messages = leds_messages
        max_rows = 3
        max_columns = classes.max_columns
        row_min_size = 20
        column_min_size = 130
        # self.max_custom_gadgets = 5
        self.is_connected = False
        self.buttons = []
        self.leds = []

        self.create_widget()

        self.configure_grid(max_rows, max_columns, row_min_size, column_min_size)

        self.running = False
        self.monitor_thread = threading.Thread(target=self.monitor_connection)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        # self.create_custom_widgets()

    def refresh_messages(self, tx_messages, rx_messages, ignore_messages, leds_messages):
        self.is_refreshing = True
        self.tx_messages = tx_messages
        self.rx_messages = rx_messages
        self.leds_messages = leds_messages

        for index in range(classes.max_custom_gadgets):
            self.buttons[index].destroy()
            self.leds[index].destroy()

        self.buttons = []
        self.leds = []
        self.create_widget()

        self.is_refreshing = False

    def create_widget(self):
        for index in range(classes.max_custom_gadgets):
            flag = False
            for tx_message in self.tx_messages:
                if tx_message.period == index and flag is False:
                    self.create_button(tx_message)
                    flag = True

            if flag is False:
                self.create_button(None)

            self.create_led(self.leds_messages[index])

    def create_button(self, message):

        if message is None:
            self.buttons.append(ttk.Button(self.frame, text="DI" + str(len(self.buttons)),
                                           command=None,
                                           style='white.TButton',state='disable'))
        else:

            self.buttons.append(ttk.Button(self.frame, text=str(message.name),
                                           command=lambda: self.sender.send_one_message(message),
                                           style='white.TButton',state='disable'))

        self.buttons[-1].grid(column=len(self.buttons) - 1, row=0, padx=10, pady=10)

    def create_led(self, message):
        if message.name == '':
            self.leds.append(
                tk.Label(self.frame, text="DO" + str(len(self.leds)), borderwidth=2, relief="groove", bg="white",
                         width=12,
                         height=1))
        else:
            self.leds.append(
                tk.Label(self.frame, text=message.name, borderwidth=2, relief="groove", bg="white",
                         width=12,
                         height=1))
        self.leds[-1].grid(column=len(self.leds) - 1, row=1, padx=10, pady=10)

    def set_is_connected(self, status: bool):  # cambiare
        """ status = status da settare"""

        self.is_connected = status

    def monitor_connection(self) -> None:
        """ controllo periodicamente se la connessione è attiva, se non lo è disabilito tuttii bottoni"""

        self.running = True
        while self.running:
            if not self.is_refreshing:
                try:
                    if not self.is_connected:
                        for button in range(classes.max_custom_gadgets):
                            #    self.leds[button_led].config(state='disable')

                            self.buttons[button].config(state='disable')
                    else:
                        for button in range(classes.max_custom_gadgets):
                            # self.leds[button_led].config(state='enable')

                            if self.buttons[button].cget("command") == '' or self.buttons[button].cget(
                                    "command") is None:
                                self.buttons[button].config(state='disable')
                            else:
                                self.buttons[button].config(state='enable')
                except:
                    pass
            time.sleep(0.5)

    def stop(self) -> None:
        self.running = False

    def set_subscribers(self) -> None:
        """ setto i messaggi da scrivere / leggere quando sono in questa pagina"""

        self.receiver.subscribe_list(self.rx_messages, self.receive)

    # self.receiver.subscribe(message_id=classes.m0x1003.arbitration_id, callback=self.receive)
    #  self.sender.subscribe(message=classes.m0x1002)

    def receive(self, message_rec) -> None:
        """ elaborazione messaggio 0x1003 """
        print("CAPIRE COME GESTIRlO")
        if message_rec is None:
            print("errore nella ricezione del messaggio")
        else:
            for message in self.rx_messages:

                if message.arbitration_id == message_rec.arbitration_id:
                    for i_led, led in enumerate(self.leds_messages, start=0):
                        for i_name, name in enumerate(message.name, start=0):

                            if led.name == name:

                                message.data = message_rec.data
                                datas = struct.unpack(message.format, message.data)
                                print("ACCENDO IL LED? ", datas[i_name], led.value)
                                if float(datas[i_name]) == led.value:
                                    print("DEVO ACCENDERE LED: ", i_led)
                                    self.leds[i_led].config(bg="red")
                                else:
                                    self.leds[i_led].config(bg="white")


class DefaultWidget(DefaultNotebook):
    """ visualizzazione di default: tutti i parametri della lista classes.rx_messages_main vengono visualizzati, eccetto
    i nomi nella lista classes.rx_message_main_exception """

    def __init__(self, root, tx_messages, rx_messages, ignore_messages):
        super().__init__(root)
        self.tx_messages = tx_messages
        self.rx_messages = rx_messages
        self.ignore_messages = ignore_messages

        self.label_names_main = []
        self.label_messages_main = []

        self.max_rows = 5
        self.max_columns = classes.max_columns
        row_min_size = 20
        column_min_size = 130

        self.configure_grid(self.max_rows, self.max_columns, row_min_size, column_min_size)

        self.create_default_widgets()

    def create_default_widgets(self) -> None:
        """ Crea un label per ogni name di ogni messaggio, ordinandoli nella griglia del frame "default" """

        column_counter = 0
        row_counter = 0

        for message in self.rx_messages:
            for name in message.name:
                if not (name in self.ignore_messages):
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
        self.receiver.subscribe_list(self.rx_messages, self.receive)
        self.sender.subscribe_list(self.tx_messages)

    def receive(self, message_rec) -> None:
        if message_rec is None:
            print("errore nella ricezione del messaggio")
        else:
            for message in self.rx_messages:

                if message.arbitration_id == message_rec.arbitration_id:
                    message.data = message_rec.data
                    datas = struct.unpack(message.format, message.data)
                    for i, name in enumerate(message.name, start=0):
                        if not (name in self.ignore_messages):
                            for k, label_name in enumerate(self.label_names_main, start=0):
                                #  print ("label_name['text'][:1]: ", label_name['text'][:-1])
                                #  print ( "name: ", name)
                                if label_name['text'][:-1] == name:
                                    self.label_messages_main[k].config(text=float(datas[i]) * message.scale[i])
                                    print("TOLOG: ", message_rec.timestamp, label_name['text'][:-1], float(datas[i]) * message.scale[i], message.arbitration_id)

    def refresh_messages(self, tx_messages, rx_messages, ignore_messages, leds_messages):
        self.tx_messages = tx_messages
        self.rx_messages = rx_messages
        self.ignore_messages = ignore_messages

        print("refresh default")
        for label in self.label_names_main:
            label.destroy()

        for label in self.label_messages_main:
            label.destroy()

        self.label_names_main = []
        self.label_messages_main = []

        self.create_default_widgets()



