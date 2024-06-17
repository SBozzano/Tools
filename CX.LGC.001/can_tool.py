import tkinter as tk
from tkinter import ttk
import classes
import threading
from can_management import CanInterface
from can_management import CANReceiver
from can_management import CANSender

from can_management import SimplyCanInterface
from settings import SettingsMenu
from can.interfaces.ixxat import get_ixxat_hwids
import struct
import time
from custom import CustomWidget
from custom import DefaultWidget
from tkinter import messagebox

import serial.tools.list_ports
import threading

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.can_interface_simply = None
        self.sender = None
        self.receiver = None
        self.can_interface = None
   #     self.connection_monitor = None
        self.actual_com = ["None"]
       # self.actual_com = self.get_com_ports()[0]
        self.actual_baudrate = 500
        self.actual_ixxat = classes.ixxat_available[0]

        # self.geometry('600x400')  # ('600x400')
        self.title('Battery CAN')
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

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
        self.file_menu.add_command(label="Esci", command=self.on_closing)

        # Aggiungi il menu "File" alla menubar
        menubar.add_cascade(label="File", menu=self.file_menu)

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

        # Aggiungi il menu "Settings" alla menubar
        self.settings_menu = tk.Menu(menubar, tearoff=0)  # postcommand=self.update_com
        self.settings_menu.add_command(label="Communication settings", command=self.show_settings)

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




    def monitor_connection(self):
      #  self.running = True
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

                        if not(self.can_interface_simply.get_status()):

                            self.stop_connection()
                            messagebox.showinfo("IXXAT", "Message sending error")




                # elif self.actual_ixxat == classes.ixxat_available[1]:
                    # if self.can_interface is not None:
                    #     if not self.can_interface.ensure_connection():
                    #         self.stop_connection()
                    #         messagebox.showinfo("IXXAT", "Ixxat fail2")


                time.sleep(1)  # Controlla ogni secondo

    def ixxat_connect(self):
        self.receiver = CANReceiver()
        self.sender = CANSender()
        self.receiver.set_ixxat(self.actual_ixxat)
        self.sender.set_ixxat(self.actual_ixxat)

        if self.actual_ixxat == classes.ixxat_available[1]:
            self.can_interface = CanInterface(interface='ixxat', channel=0, bitrate=self.actual_baudrate * 1000)
            if self.can_interface.get_bus():

                self.receiver.set_bus(self.can_interface.get_bus())
                self.sender.set_bus(self.can_interface.get_bus())

               # self.connection_monitor.start()

                self.running = True
                self.file_menu.entryconfig(classes.menu_connect, state=tk.DISABLED)
                self.file_menu.entryconfig(classes.menu_disconnect, state=tk.NORMAL)
                self.led.toggle(True)
                self.widget_custom.set_is_connected(True)
                self.after(500, self.show_messagebox)

            else:
                self.can_interface.ensure_connection()
                self.file_menu.entryconfig(classes.menu_connect, state=tk.NORMAL)
                self.file_menu.entryconfig(classes.menu_disconnect, state=tk.DISABLED)
                messagebox.showinfo("IXXAT", "IXXAT Compact: Configuration error")
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
                self.after(500, self.show_messagebox)
            else:
                messagebox.showinfo("IXXAT", "IXXAT SimplyCAN: Configuration error")
                self.stop_connection()

        self.widget_default.set_sender(self.sender)
        self.widget_default.set_receiver(self.receiver)
        self.widget_custom.set_sender(self.sender)
        self.widget_custom.set_receiver(self.receiver)



        self.simulate_tab_change(classes.title_page0)
       # self.connection_monitor = ConnectionMonitor(self.can_interface)



    def show_messagebox(self):
        messagebox.showinfo("IXXAT", "Ixxat is connected")

    def on_closing(self):
        self.stop_connection()
        self.quit()
        self.destroy()

    def stop_connection(self):
        self.running = False
        self.file_menu.entryconfig(classes.menu_connect, state=tk.NORMAL)
        self.file_menu.entryconfig(classes.menu_disconnect, state=tk.DISABLED)

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

        self.widget_custom.set_is_connected(False)
        self.led.toggle(False)

        # if self.connection_monitor is not None:
        #     self.connection_monitor.stop()



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
            self.sender.start_sending_periodically(1)

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
    def get_com_ports(self):
            return [port.device for port in serial.tools.list_ports.comports()]
      
    def show_settings(self):
        # ports = serial.tools.list_ports.comports()
        ports = self.get_com_ports()



        # self.actual_com = 'COM3'
        # self.actual_baudrate = 500000
        # self.actual_ixxat = classes.ixxat_available[1]

        settings_window = SettingsMenu(self, ports, self.actual_ixxat, self.actual_com, self.actual_baudrate)
        if settings_window.selected_ixxat is not None:
            self.actual_ixxat = settings_window.selected_ixxat
            self.actual_com = settings_window.selected_com_port
            self.actual_baudrate = int(settings_window.selected_baudrate)




class LED(tk.Canvas):
    def __init__(self, master, size=10, **kwargs):
        super().__init__(master, width=size, height=size, **kwargs)
        self.size = size
        self.create_oval(1, 1, size-1, size-1, fill="gray", outline="black", width=1)
        self.state = False  # Stato iniziale: spento

    def toggle(self, state):
        self.state = state
        if self.state:
            self.itemconfig(1, fill="red")  # Acceso
        else:
            self.itemconfig(1, fill="gray")  # Spento