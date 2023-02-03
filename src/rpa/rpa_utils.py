import autoit
from time import sleep


def await_screen(control, text):
    """
    Aguarda até que uma janela seja aberta
    """
    while not autoit.win_exists(title=control, text=text):
        sleep(1)

    autoit.win_activate(control, text=text)
