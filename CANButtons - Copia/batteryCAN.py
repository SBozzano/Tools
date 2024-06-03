import tkinter as tk
from abc import abstractmethod
from tkinter import ttk
import sys

import can_management
import classes

import time
from threading import Timer
import CAN_LogPlot
import threading
# from manage_CAN import manage_can
from can_management import CanInterface
from can_management import CANReceiver
from can_management import CANSender
from can.interfaces.ixxat import get_ixxat_hwids
import serial.tools.list_ports
from can_ixxat import CanIxxat
from classes import Parameter
import struct
import subprocess


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.sender = None
        self.receiver = None
        self.can_interface = None
        self.debug = False
        self.stop_timer = False
        self.can_is_connected = False

        self.row_min_size = 20
        self.column_min_size = 130

        self.width_little = 0
        self.height_little = 0
        self.width_big = 0
        self.height_big = 0

        self.title('Battery CAN')
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # self.disable_event

        # self.com_manage()

        self.fault_text = tk.StringVar()
        self.output_text = tk.StringVar()
        ttk.Style(self).configure('red.TButton', background='red')
        ttk.Style(self).configure('green.TButton', background='green')
        ttk.Style(self).configure('white.TButton', background='white')

        # self.grid_rowconfigure(0, weight=1)
        # self.grid_columnconfigure(0, weight=1)
        self.button_enable_charge = ttk.Button(self, text="ENABLE CHARGE", command=self.custom_enable_charge, style='white.TButton')
        self.button_enable_discharge = ttk.Button(self, text="ENABLE DISCHARGE", command= self.custom_enable_discharge, style='white.TButton')
        self.label_sw1 = tk.Label(self, text="CHARGE", borderwidth=2, relief="groove", bg="white", width=12, height=1)
        self.label_sw2 = tk.Label(self, text="DISCHARGE", borderwidth=2, relief="groove", bg="white", width=12, height=1)
        self.label_fault = tk.Label(self, text="FAULT", borderwidth=2, relief="groove", bg="white", width=6, height=1)
        # self.button_all_batt = ttk.Button(self, text="see all batt", command=self.enable, style='white.TButton')
        self.button_start_can = ttk.Button(self, text=">", width=1, command=self.ixxat_connect, )
        self.button_expand = ttk.Button(self, text="+", width=1, command=self.expand)

        self.label_fault_text = tk.Label(self, textvariable=self.fault_text)
        self.label_output = tk.Label(self, textvariable=self.output_text)

        self.row_little = 0
        self.column_little = 0
        self.row_big = 0
        self.column_big = 0
        self.expanded = False

        # self.geometry("%dx%d" % (self.width, self.height))

        self.label_names = []
        self.label_messages = []
        self.label_names_main = []
        self.label_messages_main = []
        self.parameter_counter_main = 0
        self.parameter_counter_exp = 0

        self.create_custom_widgets()
        self.create_default_widgets()
        self.create_main_widgets()

    # self.ixxat_connect()

    # self.label_soc = tk.Label(self, text="", width=5, height=1)
    # self.label_voltage = tk.Label(self, text="", width=5, height=1)
    # self.label_current = tk.Label(self, text="", width=5, height=1)
    def custom_enable_discharge(self):
        if self.can_is_connected:
            #  if self.button_enable['style'] == 'white.TButton':
            #  if self.button_enable_charge['style'] == 'green.TButton':
            self.sendnull()
            time.sleep(0.5)
            self.sender.send_one_message(classes.m0x1008_DISCHARGE)
            #     self.button_enable_charge.config(state='disable')
            # self.button_enable_charge.config(style='red.TButton', text="Disable")
            self.output_text.set("")
       # pass
    def custom_enable_charge(self):
        if self.can_is_connected:
            #  if self.button_enable['style'] == 'white.TButton':
          #  if self.button_enable_charge['style'] == 'green.TButton':
            self.sendnull()
            time.sleep(0.5)

            self.sender.send_one_message(classes.m0x1008_CHARGE)
       #     self.button_enable_charge.config(state='disable')
            #self.button_enable_charge.config(style='red.TButton', text="Disable")
            self.output_text.set("")

            # elif self.button_enable_charge['style'] == 'red.TButton':
            #     self.sender.send_one_message(classes.m0x1008)
            #
            #     self.button_enable_charge.config(style='green.TButton', text="Enable")
            #     self.output_text.set("")

             # else:
             #    self.output_text.set("SW1 != SW2")

    def ixxat_connect(self):

        self.can_interface = CanInterface(interface='ixxat', channel=0, bitrate=500000)
        if self.can_interface.get_bus_status():
         #   self.can_interface.shutdown()
            self.parameter_counter_main = 0
            self.parameter_counter_exp = 0
            self.receiver = CANReceiver()

            self.sender = CANSender()
            self.receiver.start_receiving()
            self.set_grind()
            self.button_start_can.config(text="||", command=self.stop_connection)
            self.can_is_connected = True



        else:

            self.output_text.set("IXXAT non configurata correttamente.")
            self.can_interface.ensure_connection()
            self.can_is_connected = False

        # time.sleep(2)

    #     self.after(1, self.ixxat_reconnected)

    def create_custom_widgets(self) -> None:
        self.button_enable_charge.grid(column=0, row=0,  padx=10, pady=10)
        self.button_enable_discharge.grid(column=1, row=0,  padx=10, pady=10)

        self.label_sw1.grid(column=0, row=1, padx=10, pady=10)
        self.label_sw2.grid(column=1, row=1, padx=10, pady=10)

    def create_default_widgets(self):

        self.label_fault.grid(column=0, row=2, columnspan=2, padx=10, pady=10)
        self.button_start_can.grid(row=4, column=5, sticky='se', padx=10, pady=10)
     #   self.button_expand.grid(row=4, column=4, sticky='se', padx=10, pady=10)

    #        if self.can_interface.ensure_connection:
    #       self.set_grind()

    def create_main_widgets(self):
        column = 2
        max_row = 2
        max_column = 20

        row = self.row_little
        for message in classes.rx_messages_main:
            for name in message.name:
                if not (name in classes.rx_message_main_exception):
                    new_label_name = tk.Label(self, text=(name + ":"))
                    new_label_name.grid(column=column, row=row, padx=8, pady=8, sticky='w')
                    new_label_message = tk.Label(self, text="None")
                    new_label_message.grid(column=column + 1, row=row, padx=8, pady=8, sticky='w')
                    self.label_names_main.append(new_label_name)
                    self.label_messages_main.append(new_label_message)
                    row += 1
                    if row > max_row:
                        column += 2

                        if column > max_column:
                            print("numero massimo di parametri visualizzati")
                        row = self.row_little

        self.button_start_can.grid(row=max_row, column=column+2, sticky='se', padx=10, pady=10)
     #   self.button_expand.grid(row=max_row, column=column + 1, sticky='se', padx=10, pady=10)

        self.row_little = max_row + 1
        self.column_little = column

    def set_subscribe(self, rx, callback):
        for message in rx:
            self.receiver.subscribe(message_id=message.arbitration_id, callback=callback)

    def recive(self, message_rec) -> None:


        if message_rec is None:
            print("errore nella ricezione del messaggio")
        elif self.expanded:
            for message in classes.rx_messages:
                if message.arbitration_id == message_rec.arbitration_id:
                    message.data = message_rec.data
                    datas = struct.unpack(message.format, message.data)
                    for data in datas:
                        #     *args

                        self.label_messages[self.parameter_counter_exp].config(text=data)
                        self.parameter_counter_exp += 1

        if self.parameter_counter_exp >= (len(self.label_messages) - 1):
            self.parameter_counter_exp = 0


    def recive_main(self, message_rec) -> None:
        print("id: ")
        if message_rec is None:
            print("errore nella ricezione del messaggio")
        else:
            for message in classes.rx_messages_main:

                if message.arbitration_id == message_rec.arbitration_id:
                    message.data = message_rec.data
                    datas = struct.unpack(message.format, message.data)

                    for i, name in enumerate(message.name, start=0):
                        #  for data in datas:
                        #     *args

                        if not (name in classes.rx_message_main_exception):

                            self.label_messages_main[self.parameter_counter_main].config(text=datas[i])
                            print("aaaa: ", self.parameter_counter_main, name)
                            self.parameter_counter_main += 1



        if self.parameter_counter_main >= (len(self.label_messages_main)):
            self.parameter_counter_main = 0

        for message in classes.rx_messages:


            if message.arbitration_id == message_rec.arbitration_id == 0x1003:


                datas = struct.unpack(message.format, message.data)
                output = datas[1]
                no_fault = [0, 0, 0, 0, 0, 0, 0, 0]
                fault = ''
                bits = [int(bit) for bit in bin(output)[2:]]
                while len(bits) != 8: bits.insert(0, 0)


                # self.can.send_a_message(int("0x1002", 16), b'\x00\x00\x00\x00', False)

                # self.entry_soc.delete(0, 'end')
                # self.entry_soc.insert(0, str(self.can.soc))

                if bool(bits[6]):
                    self.label_sw1.config(bg="red")
                else:
                    self.label_sw1.config(bg="white")

                if bool(bits[7]):
                    self.label_sw2.config(bg="red")
                else:
                    self.label_sw2.config(bg="white")

                if bool(bits[6]):

                    self.button_enable_charge.config(state='disable')
                 #   time.sleep(2)

                    self.button_enable_discharge.config(state='enable')
                elif bool(bits[7]):

                    self.button_enable_discharge.config(state='disable')
                 #   time.sleep(2)
                 #    self.sendnull()
                 #    time.sleep(0.2)
                    self.button_enable_charge.config(state='enable')
                else:
                    self.button_enable_charge.config(style="white.TButton")

                if bool(bits[0]):
                    fault += " Overcurrent "

                if bool(bits[1]):
                    fault += " OverTemperature "

                if bool(bits[2]):
                    fault += " UnderTemperature "

                if bool(bits[3]):
                    fault += " OverVoltage "

                if bool(bits[4]):
                    fault += " UnderVoltage "

                if bool(bits[5]):
                    fault += " Timeout can BMS "

                if bool(bits[6]):
                    fault += " Offset calibration failed "

                if bool(bits[7]):
                    fault += " Reference fuori specifica "

                if bits[:5] == no_fault[:5]:
                    self.label_fault.config(bg="white")
                else:
                    self.label_fault.config(bg="red")

                self.fault_text.set(fault)


        # self.upgrade_root()
    def sendnull(self):
        self.sender.send_one_message(classes.m0x1008_NULL)

    def expand(self):
        column = 0
        max_row = 12
        max_column = 20

        row = self.row_little

        if self.expanded:
            for message in classes.rx_messages:
                for i in range(len(message.name)):
                    self.label_names[0].destroy()
                    self.label_names.pop(0)
                    self.label_messages[0].destroy()
                    self.label_messages.pop(0)

            # self.create_custom_widgets()

            self.expanded = False
            self.button_expand.config(text="+")
            self.button_start_can.grid(row=self.row_little, column=self.column_little +1, sticky='se', padx=10,
                                       pady=10)
        #    self.button_expand.grid(row=self.row_little, column=self.column_little, sticky='se', padx=10, pady=10)
        else:
            self.expanded = True
            for message in classes.rx_messages:
                for name in message.name:
                    new_label_name = tk.Label(self, text=(name + ":"))
                    new_label_name.grid(column=column, row=row, padx=8, pady=8, sticky='w')
                    new_label_message = tk.Label(self, text="None")
                    new_label_message.grid(column=column + 1, row=row, padx=8, pady=8, sticky='w')

                    self.label_names.append(new_label_name)
                    self.label_messages.append(new_label_message)
                    row += 1
                    if row > max_row:
                        column += 2
                        if column > max_column:
                            print("numero massimo di parametri visualizzati")
                        row = self.row_little

            row_button = max(max_row, row, self.row_little)
            column_button = max(max_column, column, self.column_little)

            self.button_expand.config(text="-")
            self.button_start_can.grid(row=row_button, column=column_button +1, sticky='se', padx=10, pady=10)
        #    self.button_expand.grid(row=row_button, column=column_button, sticky='se', padx=10, pady=10)

        if self.receiver is not None and self.sender is not None:
            self.set_grind()

    #  for message in classes.rx_messages:

    def on_closing(self):
        #  if self.can_interface.get_bus_status() is not None:
        self.stop_connection()
        self.quit()
        self.destroy()




    def stop_connection(self):
       # self.receiver.attivi()
        if self.sender is not None:
            self.sender.stop_sending()

            self.sender.shutdown_()

        if self.receiver is not None:
            self.receiver.stop_receiving()

            self.receiver.shutdown_()
           # print("fine")



          # self.receiver.stop_receiving()

        if self.can_interface is not None:
            self.can_interface.shutdown_()
        #    self.sender.stop_sending()
         #   self.receiver.stop_receiving()

        #    self.receiver.attivi()
            # self.sender.attivi()
            self.receiver = None
            self.sender = None


        self.button_start_can.config(text=">", command=lambda: self.ixxat_connect())
        self.can_is_connected = False

    def set_grind(self):
        if self.expanded:

            if self.sender.is_sending:
                self.sender.stop_sending()
            self.sender.start_sending((classes.tx_messages + classes.tx_messages_main), interval=1)
            # self.receiver.rest_subscribers()
            self.set_subscribe(classes.rx_messages, self.recive)
            # for i in range(self.row_little):
            #     self.grid_rowconfigure(i, minsize=self.row_min_size)
            # for i in range(self.column_little):
            #     self.grid_columnconfigure(i, minsize=self.column_min_size)

        else:
            if self.sender.is_sending:
                self.sender.stop_sending()
            self.sender.start_sending(classes.tx_messages_main, interval=3)
            self.receiver.rest_subscribers()
            self.set_subscribe(classes.rx_messages_main, self.recive_main)
            # self.set_subscribe()

        for i in range(self.row_little):
            self.grid_rowconfigure(i, minsize=self.row_min_size)
        for i in range(self.column_little):
            self.grid_columnconfigure(i, minsize=self.column_min_size)

        self.update_idletasks()
        # if self.expanded:
        #     self.geometry(f"{width}x{height}")

    # self.resizable(True, True)

    # Imposta le dimensioni minime della finestra
    #   self.minsize(width, height)
    # Opzionalmente, imposta la dimensione esatta della finestra

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

        for hwid in get_ixxat_hwids():
            print("Found IXXAT with hardware id '%s'." % hwid)

    def write_messages(self):
        # print("write1")
        if not self.stop_timer:
            try:

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
