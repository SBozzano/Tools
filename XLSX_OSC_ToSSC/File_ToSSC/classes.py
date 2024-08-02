import tkinter as tk
from tkinter import ttk

class TracksWindow(tk.Tk):
    def __init__(self, names_list: list):
        super().__init__()
       # self.geometry("400x500")
       # self.maxsize(0, 600)
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
            self.check_var.append(tk.IntVar())
            self.create_check_button(group, name, i)



        # Aggiunge un evento per aggiornare la scrollregion del canvas
        self.frame.bind("<Configure>", self.on_frame_configure)

    def create_check_button(self, root, name, index):
        tk.Checkbutton(root, text=name, variable=self.check_var[-1],
                       command=lambda: self.callback(index)).grid(row=index, column=1, padx=5, pady=5)

    def on_frame_configure(self, event):
        # Aggiorna la regione scrollabile del canvas
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def done_command(self):
        self.destroy()

    def cancel_command(self):
        self.on_closing()

    def callback(self, index):
        print(self.check_var[index].get(), index)
        print("")
        if self.check_var[index].get():
            if len(self.valid_names_index_list) == 8:
                self.check_var[index].set(False)
            else:
                self.valid_names_index_list.append(index)
        else:
            self.valid_names_index_list.remove(index)

        print(self.valid_names_index_list)
        print("")

    def get_names_index(self):
        if not self.cancel:
            return self.valid_names_index_list
        else:
            return [0, 1, 2, 3, 4, 5, 6, 7]
        self.on_closing()

    def on_closing(self):
        self.cancel = True
        self.destroy()

# # Esempio di utilizzo
# names = ['a', 'b', 'c', 'a', 'b', 'c', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k']
# app = TracksWindow(names)
# app.mainloop()
