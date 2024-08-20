import tkinter as tk
from tkinter import ttk
import classes
# import threading
from can_management import CanInterface
from can_management import CANReceiver
from can_management import CANSender

from can_management import SimplyCanInterface
from menu import SettingsMenu
from menu import MessagesMenu
# from can.interfaces.ixxat import get_ixxat_hwids
# import struct
import time
from custom import CustomWidget
from custom import DefaultWidget
from tkinter import messagebox

import serial.tools.list_ports
import threading
import json_management


def show_messagebox(text) -> None:
    messagebox.showinfo("IXXAT", text)


def get_com_ports() -> list:
    return [port.device for port in serial.tools.list_ports.comports()]


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.leds = None
        self.can_interface_simply = None
        self.sender = None
        self.receiver = None
        self.can_interface = None
        self.actual_com = ["None"]
        # self.actual_com = self.get_com_ports()[0]
        self.actual_baudrate = 125
        self.actual_ixxat = classes.ixxat_available[0]
        self.title('Battery CAN')
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.tx_messages, self.rx_messages, self.ignore, self.leds = self.get_messages_list()

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, fill='both', expand=True)

        # Menu bar
        # Crea il menu "File"
        menubar = tk.Menu(self)

        self.file_menu = tk.Menu(menubar, tearoff=0)

        self.file_menu.add_command(label=classes.menu_connect, command=self.ixxat_connect)
        self.file_menu.add_command(label=classes.menu_disconnect, command=self.stop_connection, state=tk.DISABLED)

        self.config(menu=menubar)

        self.file_menu.add_separator()
        self.file_menu.add_command(label=classes.menu_exit, command=self.on_closing)

        # Aggiungi il menu "File" alla menubar
        menubar.add_cascade(label="File", menu=self.file_menu)

        # frame1: costituito da widget_default e widget_custom
        self.frame1 = ttk.Frame(self.notebook)
        self.widget_default = DefaultWidget(self.frame1, self.tx_messages, self.rx_messages, self.ignore)
        self.widget_custom = CustomWidget(self.frame1, self.tx_messages, self.rx_messages, self.leds)

        self.frame_standard = self.widget_default.frame
        self.frame_custom = self.widget_custom.frame  # ttk.Frame(self.frame1, style='red.TButton')
        self.frame_standard.pack(side='bottom', fill='both', expand=True)  # bottom
        self.frame_custom.pack(side='top', fill='both', expand=True)  # bottom
        self.frame1.pack(fill='both')
        self.notebook.add(self.frame1, text=classes.title_page0)

        # Aggiungi la linea di separazione
        separator = ttk.Separator(self.frame1, orient='horizontal')
        separator.pack(fill='x', pady=5)

        # frame2: per vedere tutte le celle
        # self.frame2 = ttk.Frame(self.notebook)
        # self.label2 = ttk.Label(self.frame2, text="This is Page 2")
        # self.label2.pack(pady=20, padx=20)
        # self.notebook.add(self.frame2, text=classes.title_page1)

        # Aggiungi il menu "Settings" alla menubar
        self.settings_menu = tk.Menu(menubar, tearoff=0)
        self.settings_menu.add_command(label="Communication settings", command=self.show_settings)
        self.settings_menu.add_command(label="Messages settings", command=self.show_menu_messages)

        menubar.add_cascade(label="Settings", menu=self.settings_menu)
        self.config(menu=menubar)

        self.frames = [self.frame_standard, self.frame_custom]
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        self.led = LED(self, size=15)
        self.led.pack(side="bottom", anchor="se")

        self.running = False
        self.monitor_thread = threading.Thread(target=self.monitor_connection)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def get_messages_list(self):
        return json_management.load_parameters_from_json("parameters.json")

    def monitor_connection(self) -> None:
        """ controlla lo stato della connessione ogni X ms """
        while True:
            if self.running:
                if self.receiver.get_receive_error():
                    self.stop_connection()
                    messagebox.showinfo("IXXAT", "Ixxat Message reception error")

                elif self.receiver.get_timeout_error():
                    self.stop_connection()
                    messagebox.showinfo("IXXAT", "Ixxat Timeout error")
                #
                elif self.sender.get_send_error():
                    self.stop_connection()
                    messagebox.showinfo("IXXAT", "Ixxat Message sending error")

                elif self.actual_ixxat == classes.ixxat_available[0]:
                    if self.can_interface_simply is not None:

                        if not (self.can_interface_simply.get_status()):
                            self.stop_connection()
                            messagebox.showinfo("IXXAT", "Message sending error")

                # elif self.actual_ixxat == classes.ixxat_available[1]:
                # if self.can_interface is not None:
                #     if not self.can_interface.ensure_connection():
                #         self.stop_connection()
                #         messagebox.showinfo("IXXAT", "Ixxat fail2")

                time.sleep(1)  # Controlla ogni secondo

    def ixxat_connect(self) -> None:
        """ prova a connettersi al busCAN """

        self.receiver = CANReceiver()
        self.sender = CANSender()
        self.receiver.set_ixxat(self.actual_ixxat)
        self.sender.set_ixxat(self.actual_ixxat)

        if self.actual_ixxat == classes.ixxat_available[1]:
            self.can_interface = CanInterface(interface='ixxat', channel=0, bitrate=self.actual_baudrate * 1000)
            if self.can_interface.get_bus():

                self.receiver.set_bus(self.can_interface.get_bus())
                self.sender.set_bus(self.can_interface.get_bus())
                self.running = True
                self.file_menu.entryconfig(classes.menu_connect, state=tk.DISABLED)
                self.file_menu.entryconfig(classes.menu_disconnect, state=tk.NORMAL)
                self.led.toggle(True)
                self.widget_custom.set_is_connected(True)
                self.after(500, show_messagebox("Ixxat is connected"))

            else:
                self.can_interface.ensure_connection()
                self.file_menu.entryconfig(classes.menu_connect, state=tk.NORMAL)
                self.file_menu.entryconfig(classes.menu_disconnect, state=tk.DISABLED)
                self.after(500, show_messagebox("IXXAT Compact: Configuration error"))
                self.stop_connection()

        elif self.actual_ixxat == classes.ixxat_available[0]:
            if self.can_interface_simply is None:
                self.can_interface_simply = SimplyCanInterface(self.actual_com, self.actual_baudrate)
            if self.can_interface_simply.get_status():
                self.receiver.set_bus(self.can_interface_simply.get_bus())
                self.sender.set_bus(self.can_interface_simply.get_bus())
                self.running = True
                self.file_menu.entryconfig(classes.menu_connect, state=tk.DISABLED)
                self.file_menu.entryconfig(classes.menu_disconnect, state=tk.NORMAL)
                self.led.toggle(True)
                self.widget_custom.set_is_connected(True)
                self.after(500, show_messagebox("Ixxat is connected"))
            else:
                self.after(500, show_messagebox("IXXAT SimplyCAN: Configuration error"))
                self.stop_connection()

        self.widget_default.set_sender(self.sender)
        self.widget_default.set_receiver(self.receiver)
        self.widget_custom.set_sender(self.sender)
        self.widget_custom.set_receiver(self.receiver)
        self.simulate_tab_change(classes.title_page0)

    def on_closing(self) -> None:
        """ stoppo la comunicazione e chiudo il programma """

        self.stop_connection()
        self.quit()
        self.destroy()

    def stop_connection(self) -> None:
        """ smetto di inviare e ricevere, disconnetto dal bus CAN resetto gli oggetti"""
        print("provo a sisconnettere 0")
        self.running = False
        print("provo a sisconnettere 1 ")
        self.file_menu.entryconfig(classes.menu_connect, state=tk.NORMAL)
        self.file_menu.entryconfig(classes.menu_disconnect, state=tk.DISABLED)
        print("provo a sisconnettere 2")
        if self.sender is not None:
            self.sender.stop_sending_periodically()

        if self.receiver is not None:
            self.receiver.stop_receiving()

        if self.can_interface is not None:
            self.can_interface.shutdown_()
            self.receiver = None
            self.sender = None

        if self.can_interface_simply is not None:
            self.can_interface_simply.signal_handler()
            self.can_interface_simply = None
        print("provo a sisconnettere 3")
        self.widget_custom.set_is_connected(False)
        self.led.toggle(False)
        print("provo a sisconnettere 4")

    def reset_tx_rx(self) -> None:
        """ resetto le liste delle variabili da inviare e ricevere: a seconda della pagina incui sono posso
        scegliere di leggere/inviare determinati messaggi """
        self.receiver.reset_subscribers()
        self.sender.reset_subscribers()

    def stop_tx_rx(self) -> None:
        """ fermo l'invio e la ricezione di messaggi """
        if self.receiver.status():
            self.receiver.stop_receiving()

        if self.sender.status():
            self.sender.stop_sending_periodically()

    def start_tx_rx(self) -> None:
        """ inizio a inviare e ricevere messaggi periodicamente """
        if not self.receiver.status():
            self.receiver.start_receiving()

        if not self.sender.status():
            self.sender.start_sending_periodically(classes.interval_periodic_messages)

    def simulate_tab_change(self, tab_text) -> None:
        """ simulo di aver cambiato pagina per scatenare l'evento """
        for index in range(self.notebook.index("end")):
            if self.notebook.tab(index, "text") == tab_text:
                event = tk.Event()
                event.widget = self.notebook
                self.notebook.select(index)
                self.on_tab_changed(event)
                break

    def on_tab_changed(self, event) -> None:
        """ quando cambio pagina decido cosa iniziare a leggere/inviare"""
        selected_tab = event.widget.index("current")
        selected_tab_text = self.notebook.tab(selected_tab, "text")
        if selected_tab_text == classes.title_page0:
            print("User is on Page 0")
            if self.receiver is not None and self.sender is not None:
                self.stop_tx_rx()
                self.reset_tx_rx()
                self.widget_custom.set_subscribers()
                self.widget_default.set_subscribers()
                self.start_tx_rx()

        elif selected_tab_text == classes.title_page1:
            print("User is on Page 1")
            if self.receiver is not None and self.sender is not None:
                self.stop_tx_rx()
                self.reset_tx_rx()

        else:
            raise ValueError("Error: battery CAN - on_tab_changed ")

    def show_settings(self) -> None:
        """ menu pop up settings"""
        ports = get_com_ports()
        settings_window = SettingsMenu(self, ports, self.actual_ixxat, self.actual_com, self.actual_baudrate)
        if settings_window.selected_ixxat is not None:
            self.actual_ixxat = settings_window.selected_ixxat
            self.actual_com = settings_window.selected_com_port
            self.actual_baudrate = int(settings_window.selected_baudrate)

    def show_menu_messages(self) -> None:
        """ menu pop up settings"""
        # tx_messages, rx_messages, ignore = json_management.load_parameters_from_json("parameters.json")
        self.tx_messages, self.rx_messages, self.ignore, self.leds = self.get_messages_list()
        settings = MessagesMenu(self, self.tx_messages, self.rx_messages, self.ignore, self.leds)
        self.wait_window(settings)
        self.tx_messages, self.rx_messages, self.ignore, self.leds = self.get_messages_list()
        print("REFRESHA")
        self.after(50, self.widget_custom.refresh_messages(self.tx_messages, self.rx_messages, self.ignore, self.leds))
        self.widget_default.refresh_messages(self.tx_messages, self.rx_messages, self.ignore, self.leds)

       # self.after(200, self.simulate_tab_change(classes.title_page0))
        # self.widget_default.create_default_widgets()

class LED(tk.Canvas):
    def __init__(self, master, size=10, **kwargs) -> None:
        super().__init__(master, width=size, height=size, **kwargs)
        self.size = size
        self.create_oval(1, 1, size - 1, size - 1, fill="gray", outline="black", width=1)
        self.state = False  # Stato iniziale: spento

    def toggle(self, state) -> None:
        self.state = state
        if self.state:
            self.itemconfig(1, fill="green")  # Acceso
        else:
            self.itemconfig(1, fill="gray")  # Spento
