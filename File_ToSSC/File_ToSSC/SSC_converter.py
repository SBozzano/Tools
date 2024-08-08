from tkinter import filedialog
import numpy as np
import openpyxl
import pandas as pd
import os
import ssc_texts
from classes import TracksWindow
from classes import WaitingPopup
from tkinter import messagebox
import tkinter as tk
import threading
# import time as tm
# import sys


# TODO
# gestione Abort durante il caricamento

def find(string, word_to_find, ignore_font) -> bool:
    """

    :param string: stringa incui cercare la parola
    :param word_to_find: parola da cercare nella stringa
    :param ignore_font: ignora se i caratteri sono maiuscoli o minuscoli
    :return:
        True: se la parola è presente nella stringa
        False: se la parola non è presente nella stringa
    """

    word_to_use = word_to_find
    string_to_use = string
    if ignore_font:
        string_to_use = string.casefold()
        word_to_use = word_to_find.casefold()

    if word_to_use in string_to_use:
        return True
    else:
        return False


def file_path_request() -> str:
    """

    Finestra dove l'utente sceglie il percorso file

    :return: Percorso del file da convertire
    """
    current_directory = os.getcwd()
    # parent_directory = os.path.dirname(current_directory)
    return filedialog.askopenfilename(
        title="V1.3.00 - Select file",
        initialdir=current_directory,
        filetypes=(
            ("All files", "*.xlsx *.OSC *.csv"),
            ("Excel files", "*.xlsx"),
            ("OSC files", "*.OSC"),
            ("csv files", "*.csv")
        ))


class App(tk.Tk):
    """
    Uso una Classe tk.Tk per facilitare la creazione delle altre finestre.
    La finestra principale verrà infatti nascosta.
    """
    def __init__(self):
        super().__init__()
        self.main_thread = None
        self.file_path = None
        self.excel_path = None
        self.waiting_popup = None
        self.stop_event = threading.Event()
        self.withdraw()
        self.after(0, self.start_thread)

    def start_thread(self) -> None:
        """

        Affinche se esegua il mainloop faccio partire l'app come thread dopo 0ms
        :return: None
        """
        self.main_thread = threading.Thread(target=self.start_app)
        # self.main_thread.setDaemon(True)
        self.main_thread.daemon = True
        self.main_thread.start()

    def start_app(self) -> None:
        """

        metodo principale: sequenza dei metodi da eseguire
        :return: None
        """

        self.file_path = file_path_request()

        if bool(self.file_path) is not False:
            if self.file_converter_to_excel(self.file_path):
                self.excel_to_ssc(self.excel_path)

            else:
                messagebox.showerror("Alarm A2", "Aborted")
                self.stop_event.set()
                self.destroy()
        else:
            messagebox.showerror("Alarm A0", "Aborted")
            self.stop_event.set()
            self.destroy()

    def wait_popup(self, text) -> None:
        """

        :param text: Testo da scrivere nel popup di attesa
        :return: None
        """
        self.waiting_popup = WaitingPopup(self, text)

    # def check_status_popup(self):
    #     if self.waiting_popup is not None:
    #         if not self.waiting_popup.get_status():
    #             #  self.stop_event.set()
    #             # t.join()
    #             self.stop_event.set()
    #             self.destroy()
    #
    #             sys.exit(-1)
    #
    #     time.sleep(1)
    #     self.check_status_popup()

    def file_converter_to_excel(self, path) -> bool:
        """

        file ammessi per la converisone: .xlsx, .OSC, .csv
        :param path: percorso del file da convertire in excel
        :return:
            True: se il file è stato convertito correttamente
            False: se c'è stato un problema nella conversione
        """
        self.wait_popup("Creating Excel file...")

        if path[-5:] == ".xlsx":
            self.excel_path = path
            self.waiting_popup.close_popup()
            return True

        elif path[-4:] == ".OSC":
            print("Reading file.OSC...")
            data = pd.read_csv(filepath_or_buffer=path, delimiter='\t')

            # Se l'utente lascia aperto il file Excel gli do la possibilità di chiudere e clicare riprova
            while True:
                try:
                    data.to_excel(excel_writer=path[:-4] + '.xlsx', index=False)
                    self.excel_path = path[:-4] + '.xlsx'
                    self.waiting_popup.close_popup()
                    return True

                except:
                    if not messagebox.askretrycancel("Alarm A1", "Excel error"):
                        self.excel_path = None
                        self.waiting_popup.close_popup()
                        return False

        elif path[-4:] == ".csv":
            print("Reading file.csv...")
            try:
                data = pd.read_csv(filepath_or_buffer=path, delimiter=',')
                data.to_excel(excel_writer=path[:-4] + '.xlsx', index=False)
                self.excel_path = path[:-4] + '.xlsx'
                self.waiting_popup.close_popup()
                return True

            except:
                self.excel_path = None
                self.waiting_popup.close_popup()
                return False

    def excel_to_ssc(self, path_excel) -> None:
        """

        :param path_excel: percorso file dell'excel
        :return: None
        """
        self.wait_popup("Creating file.SSC...")
        print("Creating file.SSC...")

        wb = openpyxl.load_workbook(path_excel)
        sheet = wb.worksheets[0]

        # leggo l'intera matrice
        all_cells = np.array([[cell.value for cell in row] for row in sheet.iter_rows()]).T

        # se nella cella 0 0 c'è la parola "Time" uso quella colonna come asse dei tempi
        if find(all_cells[0][0], "Time", True):
            time_found = True
        else:
            time_found = False

        # creo il file SSC
        file_ssc = open(path_excel[:-5] + '.SSC', "w")
        file_ssc.write(ssc_texts.Text_intro)

        all_parameters_names_list = []
        for name in range(int(time_found), len(all_cells)):
            all_parameters_names_list.append(all_cells[name][0])

        self.waiting_popup.close_popup()
        tracks_window = TracksWindow(self, all_parameters_names_list)

        # Se l'utente chiude la finestra o non seleziona tracce non creo il file SSC
        if not tracks_window.get_names_index():
            messagebox.showerror("Alarm", "Aborted")
            file_ssc.close()
            os.remove(path_excel[:-5] + '.SSC')
            self.stop_event.set()
            self.destroy()

        else:
            if not time_found:
                file_ssc.write(ssc_texts.Text00 + "Time" + ssc_texts.Text01)

            for index in tracks_window.get_names_index():

                if all_cells[index + int(time_found)][0] is not None:
                    file_ssc.write(ssc_texts.Text00 + all_cells[index + int(time_found)][0] + ssc_texts.Text01)
                else:
                    break

            file_ssc.write(ssc_texts.TextCentral)

            row = 0
            column = 0


            for color, index in enumerate(tracks_window.get_names_index(), start=0):
                column = index + 2

                if all_cells[index + int(time_found)][0] is not None:
                    file_ssc.write(
                        ssc_texts.Text10 + all_cells[index + int(time_found)][0] + ssc_texts.Text11 +
                        ssc_texts.ColorString[
                            color] + ssc_texts.Text12)
                    time = 0
                    for sample in range(1, len(all_cells[0])):
                        row = sample + 1
                        try:
                            if time_found:
                                # time_to_use = all_cells[0][sample]
                                num_str = str(all_cells[0][sample])
                                # Sostituisci la virgola con un punto
                                num_str_corrected = num_str.replace(',', '.')
                                # Converti la stringa in un numero float
                                time = float(num_str_corrected)
                            else:
                                time += 1
                            data_str = str(all_cells[index + int(time_found)][sample])
                            data_str_corrected = data_str.replace(',', '.')
                            data = float(data_str_corrected)
                            file_ssc.write(
                                ssc_texts.Text13 + str(time) + ssc_texts.Text14 + str(data) + ssc_texts.Text15)
                        except:
                            pass
                            # messagebox.showwarning("Error", f"Error in excel file: [{row} ; {column}]")

                    file_ssc.write(ssc_texts.Text16)
                else:
                    break
            file_ssc.write(ssc_texts.TextEnd)
            file_ssc.close()


            # file_ssc.close()
            # os.remove(path_excel[:-5] + '.SSC')

            print("SSC creato")
            messagebox.showinfo("Info", "Done")

        self.destroy()
