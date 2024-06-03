from batteryCAN import App
import sys

# TODO
# se va in fault la linea can ogni 5 sec riprova a collegarsi
# attaccato al quadro se espando il pannello va in fault

if __name__ == '__main__':
    app = App()
    app.mainloop()
    print("fine")




