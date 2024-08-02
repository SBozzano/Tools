import json
import struct

class Parameter:
    def __init__(self, name, arbitration_id, data, format, is_extended_id, scale):
        self.name = name
        self.arbitration_id = arbitration_id
        self.data = data
        self.format = format
        self.is_extended_id = is_extended_id
        self.scale = scale

    def __repr__(self):
        return (f"Parameter(name={self.name}, arbitration_id={hex(self.arbitration_id)}, "
                f"data={self.data}, format='{self.format}', "
                f"is_extended_id={self.is_extended_id}, scale={self.scale})")

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
            "scale": self.scale
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
            scale=data["scale"]
        )

def load_parameters_from_json(file_path):
    """Carica una lista di oggetti Parameter da un file JSON"""
    with open(file_path, 'r') as file:
        data = json.load(file)
        return [Parameter.from_dict(item) for item in data]

def save_parameters_to_json(file_path, parameters):
    """Salva una lista di oggetti Parameter in un file JSON"""
    with open(file_path, 'w') as file:
        json.dump([param.to_dict() for param in parameters], file, indent=4)

# Esempio di utilizzo
parameters = [
    Parameter(name=["max_voltage_cell", "min_voltage_cell", "sbilanciamento", "cicli", "SoH%"],
              arbitration_id=0x1007,
              data=[0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07],
              format='<HHHBB',
              is_extended_id=True,
              scale=[1, 1, 1, 1, 1])
]

# Salva i parametri in un file JSON
save_parameters_to_json('parameters.json', parameters)

# Carica i parametri dal file JSON
loaded_parameters = load_parameters_from_json('parameters.json')

# Stampa i parametri caricati
for param in loaded_parameters:
    print(param)
