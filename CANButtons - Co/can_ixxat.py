import threading
import sys
# Custom Thread Class
#class CanIxxat(threading.Thread):
from manage_CAN import manage_can

    # Custom Exception Class
class SampleException(Exception):
    pass

    # Custom Thread Class
class CanIxxat(threading.Thread):
    def __init__(self):
        super().__init__()
        self.a = manage_can()

    # Function  raising the custom exception
    def start_(self):
        name = threading.current_thread().name
        self.a = manage_can()

        #raise SampleException("An error occurred in thread " + name)

    def run(self):

        # Variable storing the exception, if raised by sampleFunction
        self.ex = None
        try:
            self.start_()
        except BaseException as e:
            self.ex = e

    def join(self):
        threading.Thread.join(self)
        # Since join() returns in caller thread
        # we re-raise the caught exception
        # if any was caught
        if self.ex:
            raise self.ex

def main():

    # Create a new Thread t
    # Here Main is the caller thread
    t = SampleThread()
    t.start()

    # Exception handled in the Caller thread
    try:
        t.join()
    except Exception as e:
        print("The exception has been Handled in the Main, Details of the Exception are:\n", e)

if __name__ == '__main__':
    main()
