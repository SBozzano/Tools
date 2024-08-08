import tkinter as tk
from tkinter import ttk
# import sys


class TracksWindow(tk.Toplevel):
    def __init__(self, parent, names_list: list):
        super().__init__(parent)
        # self.geometry("400x500")
        # self.maxsize(0, 600)
        self.canvas = None
        self.scrollbar = None
        self.cancel = False
        self.title('Select tracks (maximum 8)')
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.names_list = names_list
        self.check_var = []
        self.valid_names_index_list = []
        # self.geometry("200x500")
        self.create_widget()

        self.wait_window(self)

    def create_widget(self) -> None:
        """

        Inizializzaione finestra
        :return: None
        """
        ttk.Button(self, text="Done", command=self.done_command).grid(row=1, column=0, pady=10)
        ttk.Button(self, text="Cancel", command=self.cancel_command).grid(row=1, column=1, pady=10)

        # Creazione del canvas
        self.canvas = tk.Canvas(self)
        self.canvas.grid(row=0, column=0, sticky='nsew', columnspan=2)

        # Creazione della scrollbar verticale
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollbar.grid(row=0, column=1, sticky='nse')

        # Configurazione del canvas con la scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Creazione di un frame interno al canvas
        self.frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame, anchor='nw')

        # Popolazione del frame con i widget
        group = ttk.LabelFrame(self.frame, text="Tracks", padding=(10, 10, 10, 10))
        group.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        for i, name in enumerate(self.names_list, start=0):

            if i < 8:
                status = True
                self.valid_names_index_list.append(i)
            else:
                status = False

            self.check_var.append(tk.IntVar(value=status))
            self.create_check_button(group, name, i)

        # Aggiunge un evento per aggiornare la scrollregion del canvas
        self.frame.bind("<Configure>", self.on_frame_configure)

    def create_check_button(self, root, name, index) -> None:
        """

        :param root: finestra su cui creare i check button
        :param name: nome da inserire vicino al check button
        :param index: numero da restituire alla funzione callback
        :return: None
        """
        tk.Checkbutton(root, text=name, variable=self.check_var[-1],
                       command=lambda: self.callback(index)).grid(row=index, column=1, padx=5, pady=5)

    def on_frame_configure(self, event) -> None:
        # Aggiorna la regione scrollabile del canvas
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def done_command(self) -> None:
        """

        Quando l'utente clicca il button "Done"
        :return: None
        """
        if self.valid_names_index_list is None:
            self.cancel = True
        self.destroy()

    def cancel_command(self):
        """
        Quando l'utente clicca il button "Cancel"
        :return:
        """
        self.on_closing()

    def callback(self, index) -> None:
        """

        Ogni volta che clicco un check button entro in questo metodo
        :param index: indirizzo del check button che è stato cliccato
        :return: None
        """
        if self.check_var[index].get():
            if len(self.valid_names_index_list) == 8:
                self.check_var[index].set(False)
            else:
                self.valid_names_index_list.append(index)
        else:
            self.valid_names_index_list.remove(index)

    def get_names_index(self) -> list:
        """

        :return: restituisce la lista contente gli indirizzi delle variabili che si vogliono visualizzare sul SSC
        """
        if not self.cancel:
            return self.valid_names_index_list
        else:
            return []

    def on_closing(self) -> None:
        """
        Quando la finestra viene chiusa
        :return: None
        """
        self.cancel = True
        self.destroy()


class WaitingPopup(tk.Toplevel):
    def __init__(self, parent, text):
        super().__init__(parent)
        self.status = True
        self.progress = None
        self.text = text
        self.attributes("-topmost", 1)
        self.title("Please Wait")
        self.geometry("200x100")
        self.create_widgets()
        #  self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Disabilita la chiusura della finestra
        self.protocol("WM_DELETE_WINDOW", lambda: None)
        self.resizable(False, False)
        # self.wait_window(self)

    def create_widgets(self) -> None:
        """

        Inizializzazione del popup
        :return: None
        """
        label = ttk.Label(self, text=self.text)
        label.pack(pady=20)

        self.progress = ttk.Progressbar(self, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=20)
        self.progress.start()

    def close_popup(self) -> None:
        """
        Per chiudere il popup
        :return: None
        """
        self.progress.stop()
        self.destroy()

    def on_closing(self) -> None:
        """

        NON IN USO
        Quando la finestra viene chiusa tramite la "X"
        :return: None
        """
        self.status = False
        self.after(2000, self.close_popup())

    def get_status(self) -> bool:
        """

        NON IN USO
        :return: lo stato della finstra waiting, per capire se è stata chiusa
        """
        return self.status
