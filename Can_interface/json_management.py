import json
import struct
import classes


class Parameter:
    def __init__(self, name, arbitration_id, data, format, is_extended_id, scale, period):
        self.name = name
        self.arbitration_id = arbitration_id
        self.data = data
        self.format = format
        self.is_extended_id = is_extended_id
        self.scale = scale
        self.period = period

    def __repr__(self):
        return (f"Parameter(name={self.name}, arbitration_id={hex(self.arbitration_id)}, "
                f"data={self.data}, format='{self.format}', "
                f"is_extended_id={self.is_extended_id}, scale={self.scale}, period={self.period})")

    def read_data(self):
        """Metodo per leggere i dati in base al formato specificato"""
        return struct.unpack(self.format, bytes(self.data))

    def set_data(self, *values):
        """Metodo per impostare i dati in base ai valori e al formato specificato"""
        self.data = list(struct.pack(self.format, *values))

    def get_scaled_data(self):
        """Metodo per ottenere i dati scalati"""
        raw_data = self.read_data()
        return [value * scale for value, scale in zip(raw_data, self.scale)]

    def to_dict(self):
        """Metodo per convertire l'oggetto in un dizionario"""
        return {
            "name": self.name,
            "arbitration_id": self.arbitration_id,
            "data": self.data,
            "format": self.format,
            "is_extended_id": self.is_extended_id,
            "scale": self.scale,
            "period": self.period
        }

    @classmethod
    def from_dict(cls, data):
        """Metodo per creare un oggetto Parameter da un dizionario"""
        return cls(
            name=data["name"],
            arbitration_id=data["arbitration_id"],
            data=data["data"],
            format=data["format"],
            is_extended_id=data["is_extended_id"],
            scale=data["scale"],
            period=data["period"]
        )

class Led:
    def __init__(self, led, name, value):
        self.led = led
        self.name = name
        self.value = value

    def __repr__(self):
        return (f"Led(led={self.led}, name={self.name}, value={self.value}")


    def to_dict(self):
        """Metodo per convertire l'oggetto in un dizionario"""
        return {
            "led": self.led,
            "name": self.name,
            "value": self.value,
        }

    @classmethod
    def from_dict(cls, data):
        """Metodo per creare un oggetto Parameter da un dizionario"""
        return cls(
            led=data["led"],
            name=data["name"],
            value=data["value"]
        )


def load_parameters_from_json(file_path):
    """Carica i parametri da un file JSON"""
    with open(file_path, 'r') as file:
        data = json.load(file)
        tx_params = [Parameter.from_dict(item) for item in data.get("tx_parameters", [])]
        rx_params = [Parameter.from_dict(item) for item in data.get("rx_parameters", [])]
        ignore_params = data.get("ignore", [])
        leds = [Led.from_dict(item) for item in data.get("leds", [])]
        print("JSON: ",  data.get("leds", []))
        print("JSON2: ", data.get("tx_parameters", []))
        return tx_params, rx_params, ignore_params, leds


def save_parameters_to_json(file_path, tx_params, rx_params, ignore_params, leds_params):
    """Salva i parametri in un file JSON"""
    data = {
        "tx_parameters": [param.to_dict() for param in tx_params],
        "rx_parameters": [param.to_dict() for param in rx_params],
        "ignore": ignore_params,
        "leds": [param.to_dict() for param in leds_params],
    }
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)


# Esempio di utilizzo
rx_parameters = [
    Parameter(
        name=["Soc [%]", "output", "fault", "Min_temp [°C]", "Max_temp [°C]", "time_to_full_charge", "warnings"],
        arbitration_id=0x1003,
        data=[],
        format='>BBBbbhB',
        is_extended_id=True,
        scale=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        period=0),
    Parameter(name=["Voltage [V]", "Current [A]"],
              arbitration_id=0x1005,
              data=[],
              format='<Ii',
              is_extended_id=True,
              scale=[0.001, 0.001],
              period=0),
    Parameter(name=["max_voltage_cell", "min_voltage_cell", "sbilanciamento", "cicli", "SoH%"],
              arbitration_id=0x1007,
              data=[],
              format='<HHHBB',
              is_extended_id=True,
              scale=[1.0, 1.0, 1.0, 1.0, 1.0],
              period=0),
]

tx_parameters = [
    Parameter(name=["momo"],
              arbitration_id=0x1002,
              data=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
              format="<H",
              is_extended_id=True,
              scale=[1.0],
              period=0)
]

ignore_parameters = [
    "parameter1",
    "parameter2",
    "parameter3"
]

# Salva i parametri in un file JSON
# save_parameters_to_json('parameters.json', tx_parameters, rx_parameters, ignore_parameters)
#
# # Carica i parametri dal file JSON
# loaded_tx_parameters, loaded_rx_parameters, loaded_ignore_parameters = load_parameters_from_json('parameters.json')
#
# print("\nTX Parameters:")
# for param in loaded_tx_parameters:
#     print(param)
#
# print("\nRX Parameters:")
# for param in loaded_rx_parameters:
#     print(param)
#
# print("\nIgnore Parameters:")
# print(loaded_ignore_parameters)
