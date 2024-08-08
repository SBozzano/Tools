import tkinter as tk
from tkinter import ttk
import classes
import ast
import json_management


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
        self.combobox_baudrate['state'] = 'disabled'
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
        scale=ttk.Entry(frame, width=20)))

    messages_widget[-1].name.grid(row=len(messages_widget) + 1, column=0)
    messages_widget[-1].arbitration_id.grid(row=len(messages_widget) + 1, column=1)
    messages_widget[-1].data.grid(row=len(messages_widget) + 1, column=2)
    messages_widget[-1].format.grid(row=len(messages_widget) + 1, column=3)
    messages_widget[-1].is_extended_id.grid(row=len(messages_widget) + 1, column=4)
    messages_widget[-1].scale.grid(row=len(messages_widget) + 1, column=5)


def get_entry_as_type(entry, type_data):
    entry_content = entry.get()

    try:
        if type_data == "bool":
            return bool(entry_content)

        elif type_data == "int":
            return int(entry_content)

        elif type_data == "str":
            return entry_content

        elif type_data == "str_list":
            content_list = ast.literal_eval(entry_content)  # Converti la stringa in una lista
            if isinstance(content_list, list) and all(isinstance(item, str) for item in content_list):
                return content_list
            else:
                print("Errore: Il contenuto non è una lista di stringhe.")

        elif type_data == "int_list":
            content_list = ast.literal_eval(entry_content)  # Converti la stringa in una lista
            if isinstance(content_list, list) and all(isinstance(item, int) for item in content_list):
                return content_list
            else:
                print("Errore: Il contenuto non è una lista di stringhe.")

        elif type_data == "float_list":
            content_list = ast.literal_eval(entry_content)  # Converti la stringa in una lista
            if isinstance(content_list, list) and all(isinstance(item, float) for item in content_list):
                return content_list
            else:
                print("Errore: Il contenuto non è una lista di stringhe.")


        else:
            print("Errore: tipo indicato non è tra 'bool', 'int', 'str', 'str_list', 'int_list', 'float_list' ")

    except (ValueError, SyntaxError):
        print("Errore: Formato non valido.")
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
    def __init__(self, root, tx_messages, rx_messages, ignore):
        super().__init__()

        self.tx_frame = None
        self.rx_frame = None
        self.tx_messages = tx_messages
        self.rx_messages = rx_messages
        self.ignore = ignore

        self.rx_messages_widget = []
        self.tx_messages_widget = []
        self.transient(root)  # Mantiene la finestra modale sopra la finestra principale
        self.grab_set()  # Rende la finestra modale

        self.title('Settings')
        self.resizable(True, True)  # Permetti il ridimensionamento
        self.geometry("1000x400")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.create_widget_rx()
        self.create_widget_tx()

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
        self.rx_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=self.rx_frame, anchor="nw")

        def update_scrollregion(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        ttk.Button(self.rx_frame, text="+", command=lambda: add_row(self.rx_frame, self.rx_messages_widget),
                   style='white.TButton').grid(row=0, column=5,
                                               padx=10, pady=10,
                                               sticky="e")
        for i, message in enumerate(self.rx_messages, start=0):
            add_row(self.rx_frame, self.rx_messages_widget)
            print("NME: ", message.name)
            self.rx_messages_widget[i].name.insert(0, str(message.name))
            self.rx_messages_widget[i].arbitration_id.insert(0, message.arbitration_id)
            self.rx_messages_widget[i].data.insert(0, str(message.data))
            self.rx_messages_widget[i].format.insert(0, message.format)
            self.rx_messages_widget[i].is_extended_id.insert(0, message.is_extended_id)
            self.rx_messages_widget[i].scale.insert(0, str(message.scale))
        # Aggiornare la scrollregion quando il frame cambia dimensioni
        self.rx_frame.bind("<Configure>", update_scrollregion)

    def create_widget_tx(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        group = ttk.LabelFrame(self, text="Messages TX", padding=(10, 10, 10, 10))
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
        self.tx_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=self.tx_frame, anchor="nw")

        def update_scrollregion(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        ttk.Button(self.tx_frame, text="+", command=lambda: add_row(self.tx_frame, self.tx_messages_widget),
                   style='white.TButton').grid(row=0, column=5,
                                               padx=10, pady=10,
                                               sticky="e")
        for i, message in enumerate(self.tx_messages, start=0):
            add_row(self.tx_frame, self.tx_messages_widget)

            self.tx_messages_widget[i].name.insert(0, str(message.name))
            self.tx_messages_widget[i].arbitration_id.insert(0, message.arbitration_id)
            self.tx_messages_widget[i].data.insert(0, str(message.data))
            self.tx_messages_widget[i].format.insert(0, message.format)
            self.tx_messages_widget[i].is_extended_id.insert(0, message.is_extended_id)
            self.tx_messages_widget[i].scale.insert(0, str(message.scale))
        # Aggiornare la scrollregion quando il frame cambia dimensioni
        self.tx_frame.bind("<Configure>", update_scrollregion)

    def on_closing(self):
        """
        Se la riga è valida: la scrivo nel json
        Se un parametro non è valido, NON chiudo la finestra e faccio apparire un popup
        Se la riga è vuota non la considero e chiudo correttamente la finestra
        """
        rx_list = []
        for entrys in self.rx_messages_widget:
            if (get_entry_as_type(entrys.name, "str_list") or
                get_entry_as_type(entrys.arbitration_id, "int") or
                get_entry_as_type(entrys.format, "str") or
                get_entry_as_type(entrys.is_extended_id, "bool") or
                get_entry_as_type(entrys.scale, "float_list")) is None:
                print("POP UP C'E UN ERRORE")

            else:
                rx_list.append(classes.Parameter(name=get_entry_as_type(entrys.name, "str_list"),
                                                 arbitration_id=get_entry_as_type(entrys.arbitration_id, "int"),
                                                 data=[],
                                                 format=get_entry_as_type(entrys.format, "str"),
                                                 is_extended_id=get_entry_as_type(entrys.is_extended_id, "bool"),
                                                 scale=get_entry_as_type(entrys.scale, "float_list")))
        print("RX temp list: ", rx_list)

        tx_list = []
        for entrys in self.tx_messages_widget:

            if (get_entry_as_type(entrys.name, "str_list") or
                get_entry_as_type(entrys.arbitration_id, "int") or
                get_entry_as_type(entrys.format, "str") or
                get_entry_as_type(entrys.is_extended_id, "bool") or
                get_entry_as_type(entrys.scale, "float_list")) is None:

                print("POP UP C'E UN ERRORE")

            else:
                tx_list.append(classes.Parameter(name=get_entry_as_type(entrys.name, "str_list"),
                                                 arbitration_id=get_entry_as_type(entrys.arbitration_id, "int"),
                                                 data=get_entry_as_type(entrys.data, "int"),
                                                 format=get_entry_as_type(entrys.format, "str"),
                                                 is_extended_id=get_entry_as_type(entrys.is_extended_id, "bool"),
                                                 scale=get_entry_as_type(entrys.scale, "float_list")))
        print("TX temp list: ", tx_list)

        # json_management.save_parameters_to_json()
        print(
            "TODO: scrivere sul json questi valori, se la riga è bianca non scriverla, se trova un errore allora non scrive il parametro non chiude la finestra  ed esce un popup")
        self.destroy()


if __name__ == '__main__':
    roott = tk.Tk()
    roott.geometry("800x600")
    app = MessagesMenu(roott, [], [], [])
    roott.mainloop()
