from batteryCAN import App
import sys

# TODO
# finire gestione enable/disable: clicco enable charge, si disabilita il discharge  e viceversa, quando disabilito in tutti i casi devo mandare tutti zeri
#capire gestire la possibilità di staccare il cavo della ixxat
# aggiungere un notebook per sniffer del canbus (usare Listbox con scrollbar)  https://www.youtube.com/watch?v=n_4eDWTou08


if __name__ == '__main__':
    app = App()
    app.mainloop()





