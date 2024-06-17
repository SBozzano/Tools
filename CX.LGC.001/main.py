from can_tool import App
import sys

# TODO
# finire gestione enable/disable: clicco enable charge, si disabilita il discharge  e viceversa, quando disabilito in tutti i casi devo mandare tutti zeri
#finire di  gestire la possibilità lo stop e ristart con la simpycan
# aggiungere un notebook per sniffer del canbus (usare Listbox con scrollbar)  https://www.youtube.com/watch?v=n_4eDWTou08


if __name__ == '__main__':
    app = App()
    app.mainloop()





