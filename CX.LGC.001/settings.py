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
        self.combobox_com['values'] = self.com_list #('Opzione 1', 'Opzione 2', 'Opzione 3')
        self.combobox_com['state'] = 'readonly'
        self.combobox_com.set(self.init_com)
        self.combobox_com.grid(row=1, column=1, padx=5, pady=5)


        ttk.Label(group, text="Baudrate [kBaud]").grid(row=2, column=0, padx=5, pady=5)

        self.combobox_baudrate = ttk.Combobox(group)
        self.combobox_baudrate['values'] = classes.baudrate_list
        self.combobox_baudrate['state'] = 'disabled' # readonly
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

if __name__ == '__main__':
    roott = tk.Tk()
    app = SettingsMenu(roott)
    # Accedi ai valori selezionati dopo che la finestra è stata chiusa
    print("Selected COM Port:", app.selected_com_port)
    # print("Selected Baudrate:", app.selected_baudrate)
    app.mainloop()