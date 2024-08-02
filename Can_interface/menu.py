import tkinter as tk
from tkinter import ttk
import classes


class SettingsMenu(tk.Toplevel):
    def __init__(self, root, com_list, init_ixxat, init_com, init_baudrate):
        super().__init__()

        self.com_list = com_list
        self.init_ixxat = init_ixxat
        self.init_com = init_com
        self.init_baudrate = init_baudrate

        self.transient(root)  # Mantiene la finestra modale sopra la finestra principale
        self.grab_set()  # Rende la finestra modale

        #  self.geometry('60x40')
        self.title('Settings')
        self.resizable(False, False)
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
        group.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        ttk.Label(group, text="Ixxat").grid(row=0, column=0, padx=5, pady=5)

        self.combobox_ixxat = ttk.Combobox(group)
        self.combobox_ixxat.bind("<<ComboboxSelected>>", self.enable_com)
        self.combobox_ixxat['values'] = classes.ixxat_available  # ('Opzione 1', 'Opzione 2', 'Opzione 3')
        self.combobox_ixxat['state'] = 'readonly'
        self.combobox_ixxat.set(self.init_ixxat)
        self.combobox_ixxat.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(group, text="Port").grid(row=1, column=0, padx=5, pady=5)

        self.combobox_com = ttk.Combobox(group)
        self.combobox_com['values'] = self.com_list  # ('Opzione 1', 'Opzione 2', 'Opzione 3')
        self.combobox_com['state'] = 'readonly'
        self.combobox_com.set(self.init_com)
        self.combobox_com.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(group, text="Baudrate [kBaud]").grid(row=2, column=0, padx=5, pady=5)

        self.combobox_baudrate = ttk.Combobox(group)
        self.combobox_baudrate['values'] = classes.baudrate_list
        self.combobox_baudrate['state'] = 'disabled'  # readonly
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


class MessagesMenu(tk.Toplevel):
    def __init__(self, root, tx_messages, rx_messages):
        super().__init__()
        self.rx_messages_widget = []
        self.transient(root)  # Mantiene la finestra modale sopra la finestra principale
        self.grab_set()  # Rende la finestra modale

        #  self.geometry('60x40')
        self.title('Settings')
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.create_widget()

    def create_widget(self) -> None:
        group = ttk.LabelFrame(self, text="Messages", padding=(10, 10, 10, 10))
        group.grid(row=0, column=0, padx=10, pady=10)

        canvas = tk.Canvas(group)
        canvas.pack(side="left", fill="both", expand=True)

        # Creare una Scrollbar verticale
        scrollbar = ttk.Scrollbar(group, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        # Collegare la scrollbar al canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Creare un frame interno al canvas
        table_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=table_frame, anchor="nw")

        def update_scrollregion(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        for i in range(20):  # Modificare il range per aggiungere più righe

            # for j in range(5):  # Modificare il range per aggiungere più colonne
            #     entry = ttk.Entry(table_frame, width=10)
            #     entry.grid(row=i, column=j)
            #     entry.insert(tk.END, f"({i}, {j})")

            self.rx_messages_widget.append(classes.ParameterWidget(
                name=ttk.Entry(table_frame, width=10),
                arbitration_id=ttk.Entry(table_frame, width=10),
                data=ttk.Entry(table_frame, width=10),
                format=ttk.Entry(table_frame, width=10),
                is_extended_id=ttk.Entry(table_frame, width=10),
                scale=ttk.Entry(table_frame, width=10),
            ))
            ttk.Entry(table_frame, width=10).grid(row=i, column=0)

            self.rx_messages_widget[i].name.grind(row=i, column=0)
            # self.rx_messages_widget[i].arbitration_id.grind(row=i, column=1)
            # self.rx_messages_widget[i].format.grind(row=i, column=2)
            # self.rx_messages_widget[i].is_extended_id.grind(row=i, column=3)
            # self.rx_messages_widget[i].scale.grind(row=i, column=4)


        # Aggiornare la scrollregion quando il frame cambia dimensioni
        table_frame.bind("<Configure>", update_scrollregion)


    def on_closing(self):
        self.destroy()


if __name__ == '__main__':
    roott = tk.Tk()
    app = SettingsMenu(roott)
    # Accedi ai valori selezionati dopo che la finestra è stata chiusa
    print("Selected COM Port:", app.selected_com_port)
    # print("Selected Baudrate:", app.selected_baudrate)
    app.mainloop()
