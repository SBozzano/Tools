from enum import Enum
from dataclasses import dataclass
import tkinter as tk
from tkinter import ttk


@dataclass
class Parameter:
    name: list
    arbitration_id: int
    data: list
    format: str
    is_extended_id: bool


# COSTANTS
title_page0 = "page0"
title_page1 = "page1"

menu_connect = "connect"
menu_disconnect = "disconnect"
menu_com = "COM"





# RX
m0x1003 = Parameter(name=["soc", "output", "fault", "min_temp", "max_temp", "time_to_full_charge", "warnings"],
                    arbitration_id=0x1003,
                    data=[],
                    format='>BBBbbhB',
                    is_extended_id=True)
m0x1005 = Parameter(name=["voltage", "current"],
                    arbitration_id=0x1005,
                    data=[],
                    format='<Ii',
                    is_extended_id=True)
m0x1007 = Parameter(name=["max_voltage_cell", "min_voltage_cell", "sbilanciamento", "cicli", "SoH%"],
                    arbitration_id=0x1007,
                    data=[],
                    format='<HHHBB',
                    is_extended_id=True)
# TX
m0x1002 = Parameter(name=[],
                    arbitration_id=0x1002,
                    data=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    format="",
                    is_extended_id=True)
m0x1004 = Parameter(name=[],
                    arbitration_id=0x1004,
                    data=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    format="",
                    is_extended_id=True)

m0x1006 = Parameter(name=[],
                    arbitration_id=0x1006,
                    data=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    format="",
                    is_extended_id=True)

m0x1008_CHARGE = Parameter(name=[],
                    arbitration_id=0x1008,
                    data=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01],
                    format="",
                    is_extended_id=True)

m0x1008_DISCHARGE = Parameter(name=[],
                    arbitration_id=0x1008,
                    data=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00],
                    format="",
                    is_extended_id=True)
m0x1008_NULL = Parameter(name=[],
                    arbitration_id=0x1008,
                    data=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    format="",
                    is_extended_id=True)

t0 = Parameter(name=[],
               arbitration_id=0x601,
               data=[0x40, 0x41, 0x61, 0x00, 0x00, 0x00, 0x00, 0x00],
               format="",
               is_extended_id=False)
t1 = Parameter(name=[],
               arbitration_id=0x601,
               data=[0x40, 0x40, 0x60, 0x00, 0x00, 0x00, 0x00, 0x00],
               format="",
               is_extended_id=False)
t2 = Parameter(name=["oila", "prova"],
               arbitration_id=0x581,
               data=[0x40, 0x40, 0x60, 0x00, 0x00, 0x00, 0x00, 0x00],
               format="<Ii",
               is_extended_id=False)

rx_messages_main = [t2]
tx_messages_main = [t0, t1]
rx_message_main_exception = ["output", "fault", "time_to_full_charge", "warnings"]#["output", "fault", "min_temp", "max_temp", "time_to_full_charge", "warnings"]


