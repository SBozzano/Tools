import canopen
import time
import struct
import can
from can import CyclicSendTaskABC
import threading



class manage_can(canopen.Network):
    def __init__(self):
        super().__init__()
        self.debug = False
        self.bitrate = 500000

       # self.test=CanIxxat()

        self.inizialize()
        self.subscribe(int("0x1003", 16), callback=self.call1003)
        self.subscribe(int("0x1005", 16), callback=self.call1005)
        self.soc = 0
        self.output = 0
        self.sw1 = 0
        self.sw2 = 0
        self.fault = 0
        self.fault_array = [0, 0, 0, 0, 0, 0, 0, 0]
        self.min_temp = 0
        self.max_temp = 0
        self.time_to_full_charge = 0
        self.warnings = 0
        self.voltage = 0
        self.current = 0

       # self.node = self.add_node(1)
       # local_node = canopen.LocalNode(1, 'NOFAULT2-AxX_1.eds')
      #  self.node = self.add_node(local_node)
     #   self.create_node(0)

    def inizialize(self):
       # can.exceptions.CanOperationError(message='AAAAAA', error_code=None)
       #https://python-can.readthedocs.io/en/stable/configuration.html#interface-names%3E
        self.connect(bustype='ixxat', channel=0, bitrate=self.bitrate)
      #  self.check()





      #   bus = self.bus#.bus
      #
      # #  bus = self.bus
      #   bus._periodic_tasks = []
      #   self.buss = bus

    def nodes_search(self) -> list:
        self.scanner.search()
        nodes_connected = []
        time.sleep(0.5)

        # cerco i nodi disponibili e li inizializzo
        for node_id in self.scanner.nodes:
            nodes_connected.append(node_id)

        return nodes_connected

    def stop_comunication(self) -> None:
        self.unsubscribe(int("0x1003", 16))
        self.unsubscribe(int("0x1005", 16))
        self.disconnect()

    def call1003(self,id,bytearray,timestamp) ->None:

        self.soc,  self.output,  self.fault, self.min_temp,  self.max_temp,  self.time_to_full_charge, self. warnings = struct.unpack('<BBBbbhB',bytearray)    #
        output = [int(bit) for bit in bin(self.output)[2:]]
        fault = [int(bit) for bit in bin(self.fault)[2:]]
        while len(output) != 8:
            output.insert(0, 0)
        while len(fault) != 8:
            fault.insert(0, 0)

        self.sw1 = output[6]
        self.sw2 = output[7]
        self.fault_array = fault

        if self.debug:
            print("soc: ",  self.soc)
            print("output: ", output)
            print("self.sw1: ",  self.sw1)
            print("self.sw2: ", self.sw2)
            print("fault: ",  self.fault_array)
            print("min_temp: ",  self.min_temp)
            print("max_temp: ",  self.max_temp)
            print("time_to_full_charge: ",  self.time_to_full_charge)
            print("warnings: ",  self.warnings)
            print("")

    def call1005(self,id,bytearray,timestamp) ->None:

        # bytearray(b'0\x00\x00\x17\x18\xff\xff\x12')

       # print(struct.unpack('>BBBbbhB',bytearray))
        self.voltage,  self.current = struct.unpack('<Ii',bytearray)    # b'\x30\x00\x00\x17\x18\xff\xff\x12'
        if self.debug:
            print("voltage: ",  self.voltage)
            print("current: ",  self.current)
            print("")

    def send_a_message(self, can_id: int, data: bytes, remote: bool): #, can_id: int, data: bytes, remote: bool
        print("a")
        self.send_message(can_id, data, remote)
        print("b")

    def send_a_periodic_message(self):
        period = self.send_periodic(can_id=0x1002,data= b'\x00\x00\x00\x00',remote= True, period=2)
       # sync = self.send_periodic(0x79, b'\x01\x02\x03\x04\x05', 2)




    def get_values(self):
        return self.soc,  self.output,  self.fault, self.min_temp,  self.max_temp,  self.time_to_full_charge, self. warnings
#unsubscribe(can_id)