import autoit
from time import sleep


def await_screen(control, text):
    """
    Aguarda até que uma janela seja aberta
    """
    while not autoit.win_exists(title=control, text=text):
        sleep(1)

    autoit.win_activate(control, text=text)


def get_number_tabs_rescission(motivo):
    """
    Retorna o número de tabs necessários para chegar no campo
    data de pagamento conforme o motivo da rescisão
    """
    number_tabs = {
        '1': 16,
        '2': 17,
        '3': 16,
        '4': 19,
        '5': 16,
        '6': 15,
        '8': 17,
        '10': 16,
        '11': 16,
        '12': 16,
        '13': 17,
        '14': 17,
        '22': 16,
        '23': 16,
        '24': 16,
        '27': 15,
        '28': 16,
        '29': 16,
        '30': 16,
        '40': 17,
        '41': 16,
        '42': 16,
        '44': 16,
        '46': 16
    }

    if number_tabs.get(motivo):
        return number_tabs.get(motivo)
    else:
        return 1
