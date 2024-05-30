import tkinter as tk
from abc import abstractmethod
from tkinter import ttk

import classes
from classes import Costants
import time
from threading import Timer
import CAN_LogPlot
import threading
# from manage_CAN import manage_can
from can_management import CanInterface
from can.interfaces.ixxat import get_ixxat_hwids
import serial.tools.list_ports
from can_ixxat import CanIxxat
from classes import Parameter


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.debug = False
        self.stop_timer = False
        self.can_is_connected = False

        self.title('Battery CAN')
        # self.com_manage()


        self.fault_text = tk.StringVar()
        self.output_text = tk.StringVar()
        ttk.Style(self).configure('red.TButton', background='red')
        ttk.Style(self).configure('green.TButton', background='green')
        ttk.Style(self).configure('white.TButton', background='white')

        # self.grid_rowconfigure(0, weight=1)
        # self.grid_columnconfigure(0, weight=1)
        self.button_enable = ttk.Button(self, text="Enable", command=self.enable, style='white.TButton')
        self.label_sw1 = tk.Label(self, text="SW1", borderwidth=2, relief="groove", bg="white", width=5, height=1)
        self.label_sw2 = tk.Label(self, text="SW2", borderwidth=2, relief="groove", bg="white", width=5, height=1)
        self.label_fault = tk.Label(self, text="FAULT", borderwidth=2, relief="groove", bg="white", width=6, height=1)

        # self.entry_soc = tk.Entry(self, textvariable=tk.StringVar())
        # self.entry_voltage = tk.Entry(self, textvariable=tk.StringVar())
        # self.entry_current = tk.Entry(self, textvariable=tk.StringVar())
        self.label_soc = tk.Label(self, text="", width=5, height=1)
        self.label_voltage = tk.Label(self, text="", width=5, height=1)
        self.label_current = tk.Label(self, text="", width=5, height=1)

        self.all_batt = ttk.Button(self, text="see all batt", command=self.enable, style='white.TButton')

        self.label_fault_text = tk.Label(self, textvariable=self.fault_text)
        self.label_output = tk.Label(self, textvariable=self.output_text)

        self.width = 0#self.winfo_width()
        self.height = 0#self.winfo_height()

       # self.geometry("%dx%d" % (self.width, self.height))
        self.resizable(False, False)

        self.protocol("WM_DELETE_WINDOW", None)  # self.disable_event
        self.create_widgets()
        self.can_interface = CanInterface(interface='ixxat', channel=0, bitrate=500000)

        self.can_interface.start_sending(arbitration_id=0x601, data=[0x40, 0x41, 0x60, 0x00, 0x00, 0x00, 0x00, 0x00])
        self.start()
        #"Overcurrent", "OverTemperature", "OverVoltage", "UnderVoltage","Timeout can BMS", "Offset calibration failed", "Reference fuori specifica"

        Parameter()

        # self.write_messages()

    def start(self):
        self.can_interface.start_sending(arbitration_id=classes.m0x1002.arbitration_id, data=classes.m0x1002.data)



    def disable_event(self):
        pass

    def can_connect(self):

        if get_ixxat_hwids():
            self.can = manage_can()
            self.can_is_connected = True

            self.write_messages()



        else:

            self.timer(2, self.can_connect)

    def create_widgets(self) -> None:
        # optionMenu_com_list = ttk.OptionMenu(self, self.StringVar_com, None, None, command=None)
        # optionMenu_com_list.place(x=self.DeltaSpaceX * 2, y=self.DeltaSpaceY * 0)

        # self.geometry("%dx%d" % (Costants().width_Main_window, Costants().height_Main_window))

        self.button_enable.grid(column=0, row=0, columnspan=2, padx=10, pady=10)
        self.label_sw1.grid(column=0, row=1, padx=10, pady=10)
        self.label_sw2.grid(column=1, row=1, padx=10, pady=10)
        self.label_fault.grid(column=0, row=2, columnspan=2, padx=10, pady=10)

        tk.Label(self, text="SOC %:").grid(column=2, row=0, padx=10, pady=10)
        self.label_soc.grid(column=3, row=0, padx=10, pady=10)
        tk.Label(self, text="V Batt:").grid(column=2, row=1, padx=10, pady=10)
        self.label_voltage.grid(column=3, row=1, padx=10, pady=10)
        tk.Label(self, text="I Batt:").grid(column=2, row=2, padx=10, pady=10)
        self.label_current.grid(column=3, row=2, padx=10, pady=10)
        self.label_fault_text.grid(column=0, row=3, padx=10, pady=10)
        ttk.Button(self, text="-", width=1, command=self.expand).grid(row=4, column=4, sticky='se', padx=10, pady=10)

    def expand(self):
      #  self,add_all_widget()
        for
        ttk.Button(self, text="-", width=1, command=self.expand).grid(row=100, column=4, sticky='se', padx=10, pady=10)
        self.update_idletasks()
        self.minsize(self.winfo_width(), self.winfo_height())
       # self.resizable(False, False)

    def enable(self):
        if self.button_enable['style'] == 'white.TButton':
            if self.button_enable['style'] == 'green.TButton':
                self.can.send_a_message(int("0x1008", 16), b'\x00\x00\x00\x00\x00\x00\x01\x01', False)
                self.button_enable.config(style='red.TButton', text="Disable")
                self.output_text.set("")

            elif self.button_enable['style'] == 'red.TButton':
                self.can.send_a_message(int("0x1008", 16), b'\x00\x00\x00\x00\x00\x00\x00\x00', False)
                self.button_enable.config(style='green.TButton', text="Enable")
                self.output_text.set("")

            else:
                self.output_text.set("SW1 != SW2")

    def com_manage(self):
        print("test: ", get_ixxat_hwids())
        for hwid in get_ixxat_hwids():
            print("Found IXXAT with hardware id '%s'." % hwid)

    def write_messages(self):
        # print("write1")
        if not self.stop_timer:
            try:
                print("send")
                self.can_interface.send_message(arbitration_id=0x601,
                                                data=[0x40, 0x41, 0x60, 0x00, 0x00, 0x00, 0x00, 0x00])
                # self.read_1003()
                # self.read_1005()
                # print("write0")
                self.timer(1, self.write_messages)
            except:
                pass

                # print("can da connettere")
                # print("stoppp")
                # self.label_output.config(text="fault: close and open again")
            # self.stop_timer = True
            # self.com_manage()
            # self.can_connect()

    def read_1003(self):
        no_fault = [0, 0, 0, 0, 0, 0, 0, 0]
        fault = ''

        self.can.send_a_message(int("0x1002", 16), b'\x00\x00\x00\x00', False)

        # self.entry_soc.delete(0, 'end')
        # self.entry_soc.insert(0, str(self.can.soc))
        self.label_soc.config(text=str(self.can.soc))
        if bool(self.can.sw1):
            self.label_sw1.config(bg="red")
        else:
            self.label_sw1.config(bg="white")

        if bool(self.can.sw2):
            self.label_sw2.config(bg="red")
        else:
            self.label_sw2.config(bg="white")

        if bool(self.can.sw2) and bool(self.can.sw1):
            self.button_enable.config(style="red.TButton")
            self.button_enable.config(style='red.TButton', text="Disable")
        elif not (bool(self.can.sw2)) and not (bool(self.can.sw1)):
            self.button_enable.config(style="green.TButton")
            self.button_enable.config(style='red.TButton', text="Enable")
        else:
            self.button_enable.config(style="white.TButton")

        if bool(self.can.fault_array[0]):
            fault += " Overcurrent "

        if bool(self.can.fault_array[1]):
            fault += " OverTemperature "

        if bool(self.can.fault_array[2]):
            fault += " UnderTemperature "

        if bool(self.can.fault_array[3]):
            fault += " OverVoltage "

        if bool(self.can.fault_array[4]):
            fault += " UnderVoltage "

        if bool(self.can.fault_array[5]):
            fault += " Timeout can BMS "

        if bool(self.can.fault_array[6]):
            fault += " Offset calibration failed "

        if bool(self.can.fault_array[7]):
            fault += " Reference fuori specifica "

        if self.can.fault_array == no_fault:
            self.label_fault.config(bg="white")
        else:
            self.label_fault.config(bg="red")

        self.fault_text.set(fault)

    def read_1005(self):
        self.can.send_a_message(int("0x1004", 16), b'\x00\x00\x00\x00', False)
        self.label_voltage.config(text=str(self.can.voltage / 1000))
        self.label_current.config(text=str(self.can.current / 1000))
        # self.entry_voltage.delete(0, 'end')
        # self.entry_voltage.insert(0, str(self.can.voltage/1000))
        # self.entry_current.delete(0, 'end')
        # self.entry_current.insert(0, str(self.can.current/1000))

    def timer(self, period, func):
        threading.Timer(interval=period, function=func).start()

    def close_all(self):
        self.stop_timer = True
        self.can.stop_comunication()
        # time.sleep(2)
        self.destroy()

# stop timer

# class allCell(tk.Tk):
#     def start(self):
#
