from batteryCAN import App
import sys

# TODO
# finire gestione enable/disable: clicco enable charge, si disabilita il discharge  e viceversa, quando disabilito in tutti i casi devo mandare tutti zeri
# aggiungere un notebook per sniffer del canbus (usare Listbox con scrollbar)  https://www.youtube.com/watch?v=n_4eDWTou08
# aggiungere  un notebook per le celle

if __name__ == '__main__':
    app = App()
    app.mainloop()





