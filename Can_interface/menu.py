import tkinter as tk
from tkinter import ttk
import classes
import ast
import json_management
import struct
from tkinter import messagebox

class SettingsMenu(tk.Toplevel):
    def __init__(self, root, com_list, init_ixxat, init_com, init_baudrate):
        super().__init__()

        self.com_list = com_list
        self.init_ixxat = init_ixxat
        self.init_com = init_com
        self.init_baudrate = init_baudrate

        self.transient(root)  # Mantiene la finestra modale sopra la finestra principale
        self.grab_set()  # Rende la finestra modale

        self.title('Settings')
        self.resizable(True, True)  # Permetti il ridimensionamento
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.combobox = None

        self.selected_ixxat = None
        self.selected_com_port = None
        self.selected_baudrate = None

        self.create_widget()
        self.enable_com()
        self.wait_window(self)

    def create_widget(self) -> None:
        group = ttk.LabelFrame(self, text="Communication", padding=(10, 10, 10, 10))
        group.grid(row=0, column=0, padx=10, pady=10, columnspan=2, sticky="nsew")

        ttk.Label(group, text="Ixxat").grid(row=0, column=0, padx=5, pady=5)

        self.combobox_ixxat = ttk.Combobox(group)
        self.combobox_ixxat.bind("<<ComboboxSelected>>", self.enable_com)
        self.combobox_ixxat['values'] = classes.ixxat_available
        self.combobox_ixxat['state'] = 'readonly'
        self.combobox_ixxat.set(self.init_ixxat)
        self.combobox_ixxat.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(group, text="Port").grid(row=1, column=0, padx=5, pady=5)

        self.combobox_com = ttk.Combobox(group)
        self.combobox_com['values'] = self.com_list
        self.combobox_com['state'] = 'readonly'
        self.combobox_com.set(self.init_com)
        self.combobox_com.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(group, text="Baudrate [kBaud]").grid(row=2, column=0, padx=5, pady=5)

        self.combobox_baudrate = ttk.Combobox(group)
        self.combobox_baudrate['values'] = classes.baudrate_list
        self.combobox_baudrate['state'] = 'readonly'
        self.combobox_baudrate.set(self.init_baudrate)
        self.combobox_baudrate.grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(self, text="OK", command=self.get_settings).grid(row=1, column=0, pady=10)
        ttk.Button(self, text="Cancel", command=self.on_closing).grid(row=1, column=1, pady=10)

    def enable_com(self, *args):
        if self.combobox_ixxat.get() == classes.ixxat_available[0]:
            self.combobox_com['state'] = 'readonly'
        elif self.combobox_ixxat.get() == classes.ixxat_available[1]:
            self.combobox_com['state'] = 'disabled'

        if self.com_list == ["None"]:
            self.combobox_com['state'] = 'disabled'

    def get_settings(self):
        self.selected_ixxat = self.combobox_ixxat.get()
        self.selected_com_port = self.combobox_com.get()
        self.selected_baudrate = self.combobox_baudrate.get()

        self.on_closing()

    def on_closing(self):
        self.destroy()


def add_row(frame, messages_widget):
    messages_widget.append(classes.ParameterWidget(
        name=ttk.Entry(frame, width=100),
        arbitration_id=ttk.Entry(frame, width=10),
        data=ttk.Entry(frame, width=10),
        format=ttk.Entry(frame, width=10),
        is_extended_id=ttk.Entry(frame, width=10),
        scale=ttk.Entry(frame, width=20),
        period=ttk.Entry(frame, width=20)))

    messages_widget[-1].name.grid(row=len(messages_widget) + 1, column=0)
    messages_widget[-1].arbitration_id.grid(row=len(messages_widget) + 1, column=1)
    messages_widget[-1].data.grid(row=len(messages_widget) + 1, column=2)
    messages_widget[-1].format.grid(row=len(messages_widget) + 1, column=3)
    messages_widget[-1].is_extended_id.grid(row=len(messages_widget) + 1, column=4)
    messages_widget[-1].scale.grid(row=len(messages_widget) + 1, column=5)
    messages_widget[-1].period.grid(row=len(messages_widget) + 1, column=6)


def is_valid_format(format_string, name_list):
    try:
        # Prova a calcolare la dimensione dell'oggetto per il formato specificato
        struct.calcsize(format_string.get())
        if name_list is not None:
            if len(format_string.get()) == len(name_list) + 1 and (
                    format_string.get()[0] == '<' or format_string.get()[0] == '>'):
                return get_entry_as_type(format_string, "str")
            else:
                print("la lunghezza del formato non è coerente con il numero di nomi: ", len(format_string.get()),
                      len(name_list) + 1)
                return None
        else:

            print("Il nome è None")
            return None
    except struct.error:
        return None


def bit_string_to_byte(input_str):
    ''' NOT USED'''
    try:
        # Converti la stringa in una lista di interi
        bit_list = ast.literal_eval(input_str)
    except:
        raise ValueError("Input non è una stringa valida di bit")

    # Controlla che ogni elemento sia 0 o 1 e che la lunghezza sia esattamente 8
    if len(bit_list) != 8 or any(bit not in [0, 1] for bit in bit_list):
        raise ValueError("La lista deve contenere esattamente 8 bit (0 o 1)")

    # Costruisci il byte combinando i bit
    byte_value = 0
    for bit in bit_list:
        byte_value = (byte_value << 1) | bit

    # Converti il valore in un byte
    return struct.pack('B', byte_value)


def convert_to_struct_format(input_str, expected_format):
    try:
        elements = ast.literal_eval(input_str)
    except:
        return None  # Ritorna None se l'input non è una lista valida

    if not isinstance(elements, list) or len(elements) != len(expected_format) - 1:
        return None  # Ritorna None se il numero di elementi non corrisponde al formato

    # Mappa per i tipi di conversione
    type_map = {
        'b': int,  # signed char
        'B': int,  # unsigned char
        'h': int,  # signed short
        'H': int,  # unsigned short
        'i': int,  # signed int
        'I': int,  # unsigned int
        'l': int,  # signed long
        'L': int,  # unsigned long
        'q': int,  # signed long long
        'Q': int,  # unsigned long long
        'n': int,  # ssize_t
        'N': int,  # size_t
        'P': int,  # void pointer

        'e': float,  # half-precision float
        'f': float,  # single-precision float
        'd': float,  # double-precision float

        'c': lambda x: x.encode() if isinstance(x, str) else bytes([x]),  # char
        's': lambda x: x.encode(),  # string (fixed size)
        'p': lambda x: x.encode(),  # pascal string
        '?': lambda x: x if isinstance(x, bool) else bool(int(x))  # boolean
    }

    converted_elements = []

    for element, fmt in zip(elements, expected_format[1:]):
        try:
            # Converti l'elemento nel tipo corretto
            converted_element = type_map[fmt](element)
            # Verifica se può essere impacchettato senza errori
            struct.pack(fmt, converted_element)
            converted_elements.append(converted_element)


        except (KeyError, struct.error, TypeError) as e:

            return None  # Ritorna None se la conversione fallisce

    return converted_elements


def get_entry_as_type(entry, type_data):
    entry_content = entry.get()

    if entry_content == '':
        return None
    else:
        try:
            if type_data == "bool":

                return bool(int(entry_content))

            elif type_data == "int":

                return int(entry_content)

            elif type_data == "hex":
                return int(entry_content, 16)

            elif type_data == "str":

                return entry_content

            elif type_data == "float":

                return float(entry_content)

            elif type_data == "str_list":
                content_list = ast.literal_eval(entry_content)  # Converti la stringa in una lista
                if isinstance(content_list, list) and all(isinstance(item, str) for item in content_list):
                    return content_list
                else:
                    print("Errore: Il contenuto non è una lista di stringhe: ", entry_content)
                    return None

            elif type_data == "int_list":
                content_list = ast.literal_eval(entry_content)  # Converti la stringa in una lista
                if isinstance(content_list, list) and all(isinstance(item, int) for item in content_list):
                    return content_list
                else:
                    print("Errore: Il contenuto non è una lista di interi: ", entry_content)
                    return None

            elif type_data == "float_list":
                content_list = ast.literal_eval(entry_content)  # Converti la stringa in una lista
                if isinstance(content_list, list) and all(isinstance(item, float) for item in content_list):
                    return content_list
                else:
                    print("Errore: Il contenuto non è una lista di float: ", entry_content)
                    return None


            else:
                print(
                    "Errore: il tipo {type_data} non è tra 'bool', 'int', 'hex', 'str', 'float', 'str_list', 'int_list', 'float_list' ")
                return None

        except (ValueError, SyntaxError):
            print("Errore: Formato non valido: ", entry_content)
        return None


# def get_entry_as_list():
#     entry_content = entry.get()  # Ottieni il contenuto dell'Entry come stringa
#     try:
#         content_list = ast.literal_eval(entry_content)  # Converti la stringa in una lista
#         if isinstance(content_list, list) and all(isinstance(item, str) for item in content_list):
#             print("Lista letta correttamente:", content_list)
#         else:
#             print("Errore: Il contenuto non è una lista di stringhe.")
#     except (ValueError, SyntaxError):
#         print("Errore: Formato non valido.")


class MessagesMenu(tk.Toplevel):
    def __init__(self, root, tx_messages, rx_messages, ignore, leds):
        super().__init__()

        self.ignore_entry = None

        self.tx_messages = tx_messages
        self.rx_messages = rx_messages
        self.ignore = ignore
        self.leds = leds

        self.rx_messages_widget = []
        self.tx_messages_widget = []
        self.leds_widget = []

        self.transient(root)  # Mantiene la finestra modale sopra la finestra principale
        self.grab_set()  # Rende la finestra modale

        self.title('Settings')
        self.resizable(True, True)  # Permetti il ridimensionamento
        self.geometry("1200x600")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.create_widget_rx()
        self.create_widget_tx()
        self.create_widget_leds()
        self.create_widget_ignore()
        ttk.Button(self, text="Done", command=self.done).grid(row=4, column=0, pady=10)

        print(
            "Se la riga è tutta bianca cancello quella riga\n"
            "Se c'è un errore non permetto la chiusura\n"
            "Non sono gestiti i nomi uguali e un period superiore a 5"
            "TODO: \n"
            "Aggiungere popup per gli errori\n"
            "Su custom devono essere messi 5 button e 5 led:\n"
            "Aggiungere un gruppo 'TX BUtton ' --> possibilità di configurare messaggi fino a 5 bottoni'\n "
            "Aggiungere un gruppo 'RX Led ' --> possibilità di configurare messaggi fino a 5 led ' \n",
            "GEstire i nomi uguali e i period tra 0 e 4 uguali o se sono superiori a 5")

    def create_widget_ignore(self) -> None:
        # self.columnconfigure(0, weight=1)
        # self.rowconfigure(3, weight=1)

        group = ttk.LabelFrame(self, text="Ignore", padding=(10, 10, 10, 10))
        group.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

        canvas = tk.Canvas(group)
        canvas.pack(side="left", fill="x", expand=True)
        canvas.configure(height=50)

        ignore_frame = ttk.Frame(canvas)

        canvas.create_window((0, 0), window=ignore_frame, anchor="nw")

        self.ignore_entry = ttk.Entry(ignore_frame, width=1000)
        self.ignore_entry.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.ignore_entry.insert(0, str(self.ignore))

    def create_widget_rx(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        group = ttk.LabelFrame(self, text="Messages RX", padding=(10, 10, 10, 10))
        group.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        canvas = tk.Canvas(group)
        canvas.pack(side="left", fill="both", expand=True)

        # Creare una Scrollbar verticale
        scrollbar = ttk.Scrollbar(group, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        # Collegare la scrollbar al canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Creare un frame interno al canvas
        rx_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=rx_frame, anchor="nw")

        def update_scrollregion(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        ttk.Button(rx_frame, text="+", command=lambda: add_row(rx_frame, self.rx_messages_widget),
                   style='white.TButton').grid(row=0, column=6,
                                               padx=10, pady=10,
                                               sticky="e")
        for i, message in enumerate(self.rx_messages, start=0):
            add_row(rx_frame, self.rx_messages_widget)
            self.rx_messages_widget[i].name.insert(0, str(message.name))
            self.rx_messages_widget[i].arbitration_id.insert(0, hex(message.arbitration_id)[2:])
            self.rx_messages_widget[i].data.insert(0, str(message.data))
            self.rx_messages_widget[i].format.insert(0, message.format)
            self.rx_messages_widget[i].is_extended_id.insert(0, message.is_extended_id)
            self.rx_messages_widget[i].scale.insert(0, str(message.scale))
            self.rx_messages_widget[i].period.insert(0, str(message.period))
        # Aggiornare la scrollregion quando il frame cambia dimensioni
        rx_frame.bind("<Configure>", update_scrollregion)

    def create_widget_tx(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        group = ttk.LabelFrame(self, text="Messages TX (1s)", padding=(10, 10, 10, 10))
        group.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        canvas = tk.Canvas(group)
        canvas.pack(side="left", fill="both", expand=True)

        # Creare una Scrollbar verticale
        scrollbar = ttk.Scrollbar(group, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        # Collegare la scrollbar al canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Creare un frame interno al canvas
        tx_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=tx_frame, anchor="nw")

        def update_scrollregion(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        ttk.Button(tx_frame, text="+", command=lambda: add_row(tx_frame, self.tx_messages_widget),
                   style='white.TButton').grid(row=0, column=6,
                                               padx=10, pady=10,
                                               sticky="e")
        for i, message in enumerate(self.tx_messages, start=0):
            add_row(tx_frame, self.tx_messages_widget)

            self.tx_messages_widget[i].name.insert(0, str(message.name))
            self.tx_messages_widget[i].arbitration_id.insert(0, hex(message.arbitration_id)[2:])
            self.tx_messages_widget[i].data.insert(0, str(message.data))
            self.tx_messages_widget[i].format.insert(0, message.format)
            self.tx_messages_widget[i].is_extended_id.insert(0, message.is_extended_id)
            self.tx_messages_widget[i].scale.insert(0, str(message.scale))
            self.tx_messages_widget[i].period.insert(0, str(message.period))
        # Aggiornare la scrollregion quando il frame cambia dimensioni
        tx_frame.bind("<Configure>", update_scrollregion)

    def create_widget_leds(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        group = ttk.LabelFrame(self, text="Leds", padding=(10, 10, 10, 10))
        group.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        canvas = tk.Canvas(group)
        canvas.pack(side="left", fill="both", expand=True)

        # Creare una Scrollbar verticale
        scrollbar = ttk.Scrollbar(group, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        # Collegare la scrollbar al canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Creare un frame interno al canvas
        leds_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=leds_frame, anchor="nw")

        def update_scrollregion(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        # for i, message in enumerate(self.tx_messages, start=0):

        for row in range(classes.max_custom_gadgets):  # TODO mettere in range (len(leds_json))
            self.leds_widget.append(classes.LedsWidget(led=ttk.Label(leds_frame, text="DO" + str(row), width=20),
                                                       name=ttk.Entry(leds_frame, width=20),
                                                       value=ttk.Entry(leds_frame, width=20)))

        for index, led_widget in enumerate(self.leds_widget, start=0):
            led_widget.led.config(text="DO" + str(index))
            led_widget.name.insert(0, self.leds[index].name)
            led_widget.value.insert(0, self.leds[index].value)
            led_widget.led.grid(row=index, column=0, padx=10, pady=10, sticky="nsew")
            led_widget.name.grid(row=index, column=1, padx=10, pady=10, sticky="nsew")
            led_widget.value.grid(row=index, column=2, padx=10, pady=10, sticky="nsew")

        # Aggiornare la scrollregion quando il frame cambia dimensioni
        leds_frame.bind("<Configure>", update_scrollregion)

    def on_closing(self):
        self.destroy()

    def done(self):
        """
        Se la riga è valida: la scrivo nel json
        Se un parametro non è valido, NON chiudo la finestra e faccio apparire un popup
        Se la riga è vuota non la considero e chiudo correttamente la finestra
        """

        destroy = True
        rx_list = []

        for entrys in self.rx_messages_widget:

            name = get_entry_as_type(entrys.name, "str_list")
            arbitration_id = get_entry_as_type(entrys.arbitration_id, "hex")
            format_ = is_valid_format(entrys.format, get_entry_as_type(entrys.name, "str_list"))
            is_extended_id = get_entry_as_type(entrys.is_extended_id, "bool")
            scale = get_entry_as_type(entrys.scale, "float_list")
            period = get_entry_as_type(entrys.period, "int")

            if (
                    name is None and arbitration_id is None and format_ is None and is_extended_id is None and scale is None and period is None):
                print("\ncancello riga\n")
                pass

            else:
                if (
                        name is None or arbitration_id is None or format_ is None or is_extended_id is None or scale is None or period is None):

                    messagebox.showwarning("Warning", "'RX' syntax error")

                    destroy = False

                else:

                    rx_list.append(json_management.Parameter(name=name,
                                                             arbitration_id=arbitration_id,
                                                             data=[],
                                                             format=str(format_),
                                                             is_extended_id=int(is_extended_id),
                                                             scale=scale,
                                                             period=period))

        tx_list = []
        for entrys in self.tx_messages_widget:
            name = get_entry_as_type(entrys.name, "str_list")
            arbitration_id = get_entry_as_type(entrys.arbitration_id, "hex")

            format_ = is_valid_format(entrys.format, get_entry_as_type(entrys.name, "str_list"))

            data = convert_to_struct_format(entrys.data.get(), format_)

            is_extended_id = get_entry_as_type(entrys.is_extended_id, "bool")
            scale = convert_to_struct_format(entrys.scale.get(), format_)

            # scale = get_entry_as_type(entrys.scale, "float_list")
            period = get_entry_as_type(entrys.period, "int")

            if (
                    name is None and arbitration_id is None and data is None and format_ is None and is_extended_id is None and
                    scale is None and period is None):

                pass

            else:
                if (
                        name is None or arbitration_id is None or data is None or format_ is None or is_extended_id is None or
                        scale is None or period is None):


                    messagebox.showwarning("Warning", "'TX' syntax error")
                    destroy = False

                else:

                    tx_list.append(json_management.Parameter(name=name,
                                                             arbitration_id=arbitration_id,
                                                             data=data,
                                                             format=str(format_),
                                                             is_extended_id=int(is_extended_id),
                                                             scale=scale,
                                                             period=period))

        ignore_list = get_entry_as_type(self.ignore_entry, "str_list")
        if ignore_list is None:
            messagebox.showwarning("Warning", "'Ignore' syntax error")
            destroy = False

        leds_list = []
        for led in self.leds_widget:
            if get_entry_as_type(led.value, "float") is not None:
                leds_list.append(json_management.Led(led=led.led.cget("text"), name=led.name.get(), value=get_entry_as_type(led.value, "float")))
            else:
                messagebox.showwarning("Led", "RX syntax error")
                destroy = False

        if destroy is True:
            json_management.save_parameters_to_json(file_path='parameters.json',
                                                    ignore_params=ignore_list,
                                                    tx_params=tx_list, rx_params=rx_list, leds_params=leds_list)
            self.destroy()


if __name__ == '__main__':
    roott = tk.Tk()
    roott.geometry("800x600")
    app = MessagesMenu(roott, [], [], [], [])
    roott.mainloop()
