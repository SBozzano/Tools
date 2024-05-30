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


m0x1003 = Parameter(name=["soc","output", "fault", "min_temp", "max_temp", "time_to_full_charge", "warnings"],
                                      arbitration_id=0x1003, data=[], format='>BBBbbhB')
m0x1005 = Parameter(name=["voltage", "current"],arbitration_id=0x1005, data=[], format='<Ii')

m0x1002 = Parameter(name=[], arbitration_id = 0x1002, data=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],format = "")
m0x1004 = Parameter(name=[], arbitration_id = 0x1004, data=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],format = "",)

rx_messages = [m0x1003, m0x1005]