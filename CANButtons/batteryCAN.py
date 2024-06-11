import tkinter as tk
from tkinter import ttk
import classes
import threading
from can_management import CanInterface
from can_management import CANReceiver
from can_management import CANSender
from can_management import ConnectionMonitor
from can.interfaces.ixxat import get_ixxat_hwids
import struct
import time
from custom import CustomWidget
from custom import DefaultWidget
from tkinter import messagebox

import serial.tools.list_ports


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.simplycan = False
        self.sender = None
        self.receiver = None
        self.can_interface = None
        self.connection_monitor = None
        self.actual_com = ""
        self.com_bool = {}

        self.geometry('600x400')  # ('600x400')
        self.title('Battery CAN')
        # self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, fill='both', expand=True)
        # Menu bar
        # Crea il menu "File"
        menubar = tk.Menu(self)

        self.file_menu = tk.Menu(menubar, tearoff=0)
        self.com_menu = tk.Menu(self.file_menu, tearoff=0, postcommand=self.update_com)

        self.file_menu.add_command(label=classes.menu_connect, command=self.ixxat_connect)
        self.file_menu.add_command(label=classes.menu_disconnect, command=self.stop_connection, state=tk.DISABLED)

        self.file_menu.add_separator()
        self.file_menu.add_command(label="Esci", command=self.on_closing)

        # Aggiungi il menu "File" alla menubar
        menubar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_cascade(label=classes.menu_com, menu=self.com_menu)
        self.config(menu=menubar)

        # frame1: costituito da widget_default e widget_custom
        self.frame1 = ttk.Frame(self.notebook)
        self.widget_default = DefaultWidget(self.frame1)
        self.widget_custom = CustomWidget(self.frame1)
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



        self.frames = [self.frame_standard, self.frame_custom]
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        self.button_start_can = ttk.Button(self, text=">", width=1, command=self.ixxat_connect, )

    def ixxat_connect(self):

        if not self.simplycan:
            self.can_interface = CanInterface(interface='ixxat', channel=0, bitrate=500000)
            if self.can_interface.get_bus():

                self.receiver = CANReceiver()
                self.sender = CANSender()

                self.receiver.set_bus(self.can_interface.get_bus())
                self.sender.set_bus(self.can_interface.get_bus())

                self.widget_default.set_sender(self.sender)
                self.widget_default.set_receiver(self.receiver)
                self.widget_custom.set_sender(self.sender)
                self.widget_custom.set_receiver(self.receiver)

                self.file_menu.entryconfig(classes.menu_connect, state=tk.DISABLED)
                self.file_menu.entryconfig(classes.menu_disconnect, state=tk.NORMAL)

                self.simulate_tab_change(classes.title_page0)
                self.connection_monitor = ConnectionMonitor(self.can_interface)
                self.connection_monitor.start()

                #  self.on_tab_changed(self.notebook.select())

          #      self.receiver.start_receiving()

                messagebox.showinfo("IXXAT", "Ixxat is connected")

            #     self.start_tx_rx()

            # self.sender.subscribe(classes.m0x1002)

            # self.receiver.start_receiving()
            # self.sender.start_sending_periodically(2)

            else:
                # self.output_text.set("IXXAT non configurata correttamente.")
                self.can_interface.ensure_connection()
                # self.can_is_connected = False
                self.file_menu.entryconfig(classes.menu_connect, state=tk.NORMAL)
                self.file_menu.entryconfig(classes.menu_disconnect, state=tk.DISABLED)
                messagebox.showinfo("IXXAT", "Ixxat fail")

    def on_closing(self):
        self.stop_connection()
        self.quit()
        self.destroy()

    def stop_connection(self):
        # self.receiver.attivi()
        if self.sender is not None:
            self.sender.stop_sending_periodically()
        #    self.sender.shutdown_()

        if self.receiver is not None:
            self.receiver.stop_receiving()
            # self.receiver.shutdown_()

        if self.can_interface is not None:
            self.can_interface.shutdown_()
            self.receiver = None
            self.sender = None

        self.connection_monitor.stop()

        # self.button_start_can.config(text=">", command=lambda: self.ixxat_connect())
        # self.can_is_connected = False

    def update_com(self):

        ports = serial.tools.list_ports.comports()
        if self.com_menu.index("end") is not None:
            for index in range(self.com_menu.index("end") + 1):
                #         print("index: ", index)
                self.com_menu.delete(0)
        #         print("Voce 'Save' cancellata.")

        for port in ports:
            #      print("ports: ", port.name)
            self.create_com_menu(port.name)

    def create_com_menu(self, com_name):
        self.com_bool[com_name] = []
        if self.actual_com == com_name:
            self.com_bool[com_name].append(tk.BooleanVar(value=True))
        else:
            self.com_bool[com_name].append(tk.BooleanVar())

        self.com_menu.add_checkbutton(label=com_name, variable=self.com_bool[com_name],
                                      command=lambda: self.set_com(com_name))

    def set_com(self, com_name):
        self.com_bool = {}
        self.actual_com = com_name

    def reset_tx_rx(self):
        self.receiver.reset_subscribers()
        self.sender.reset_subscribers()
        # self.sender.subscribe(classes.m0x1002)
        #
        # self.receiver.start_receiving()
        # self.sender.start_sending_periodically(2)

    def stop_tx_rx(self):

        if self.receiver.status():
            self.receiver.stop_receiving()

        if self.sender.status():
            self.sender.stop_sending_periodically()
            # self.sender.stop_sending()

    def start_tx_rx(self):

        if not self.receiver.status():
            self.receiver.start_receiving()

        if not self.sender.status():
            self.sender.start_sending_periodically(0.1)

    def simulate_tab_change(self, tab_text):
        for index in range(self.notebook.index("end")):
            if self.notebook.tab(index, "text") == tab_text:
                event = tk.Event()
                event.widget = self.notebook
                self.notebook.select(index)
                self.on_tab_changed(event)
                break

    def on_tab_changed(self, event):
#        print("event: ",event )
        # Get the selected tab index
        selected_tab = event.widget.index("current")
        # Get the tab text
        selected_tab_text = self.notebook.tab(selected_tab, "text")
        #    print(f"Tab changed to: {selected_tab_text}")
        # You can also perform different actions based on the selected tab
        if selected_tab_text == classes.title_page0:
            print("User is on Page 0")
            if self.receiver is not None and self.sender is not None:
                self.stop_tx_rx()
                self.reset_tx_rx()
                self.widget_custom.set_subscribers()
                self.widget_default.set_subscribers()
                self.start_tx_rx()

        elif selected_tab_text == classes.title_page1:
            print("User is on Page 2")
            if self.receiver is not None and self.sender is not None:
                self.stop_tx_rx()
                self.reset_tx_rx()


        else:
            raise ValueError("Error: battery CAN - on_tab_changed ")
