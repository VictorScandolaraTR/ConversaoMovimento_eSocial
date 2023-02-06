from PySide6.QtCore import Signal, QThread
from PySide6.QtWidgets import QMainWindow

from src.ui.dialog_rpa import UI_dialog_rpa as DialogRPA
from src.controllers.rpa_controller import Controller
import src.ui.components_ui as components_ui


class RPAConfiguracoes(QMainWindow):
    config_run = Signal(bool, list)

    def __init__(self):
        super().__init__()
        self.__window = DialogRPA()

    def init_gui(self):
        """
        Declarar componentes que serão utilizados da interface
        """
        self.__window.setupUi(self)
        self.__widget = self.__window.centralwidget

        self.setWindowTitle('Configurar Execução RPA')

        self.checkbox_run_local = self.__window.checkbox__run_local
        self.button_run_in_network = self.__window.checkbox__run_in_network
        self.label_run_network = self.__window.label__run_in_network
        self.listbox_options_machines = self.__window.listbox__options_machines
        self.progressbar_rpa = self.__window.progressbar__rpa
        self.label_progressbar = self.__window.label__action_progress
        self.button_run_rpa = self.__window.button__run_rpa

        self.progressbar_rpa.setValue(0)
        self.label_progressbar.setText('')

        self.button_run_rpa.clicked.connect(self.start)
        self.button_run_in_network.clicked.connect(self.execute_in_vm)
        self.execute_in_vm()

        self.show()

    def execute_in_vm(self):
        if self.button_run_in_network.isChecked():
            self.label_run_network.setEnabled(True)
            self.listbox_options_machines.setEnabled(True)
            self.button_run_rpa.setEnabled(False)
            self.button_run_in_network.setEnabled(False)
            self.list_agents()
        else:
            self.label_run_network.setEnabled(False)
            self.listbox_options_machines.setEnabled(False)

    def list_agents(self):
        """
        Preenche a lista de máquinas com os IPs disponíveis para execução
        """
        def update_progress(progress):
            self.set_progress(progress[0], progress[1])

        def finish_process(success, message, list_devices):
            self.button_run_rpa.setEnabled(True)
            self.button_run_in_network.setEnabled(True)
            if success:
                if len(list_devices) == 0:
                    self.set_progress('Nenhuma máquina encontrada..', 100)
                    return

                for ip in list_devices:
                    self.listbox_options_machines.addItem(ip)

                self.set_progress('Busca completa...', 100)
            else:
                self.set_progress(message, 0)

        self.listbox_options_machines.clear()
        self.set_progress('Buscando máquinas disponíveis na rede...', 10)

        # abre uma nova thread que irá executar o processamento
        self.thread = QThread()
        self.controller = Controller()

        self.controller.moveToThread(self.thread)
        self.controller.init()

        self.set_progress('Verificando máquinas que possuem agente...', 20)

        self.thread.started.connect(self.controller.devices_availables)
        self.controller.finished.connect(self.thread.quit)
        self.controller.finished.connect(self.controller.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

        # vai recebendo sinais conforme avança o processamento
        self.controller.progress.connect(update_progress)

        # quando a thread é finalizada, é enviado um sinal boolean indicando sucesso(True) ou erro (False)
        self.controller.success.connect(finish_process)

    def start(self):

        if self.checkbox_run_local.isChecked():
            local = True
        else:
            local = False

        if self.button_run_in_network.isChecked():
            machines = self.listbox_options_machines.selectedItems()
            if machines:
                list_machines = []
                for i in range(len(machines)):
                    list_machines.append(machines[i].text())
            else:
                components_ui.message_error(self.__widget, 'Selecione uma máquina para executar!')
                return
        else:
            list_machines = []

        self.config_run.emit(local, list_machines)
        self.close()

    def set_progress(self, text, percent):
        self.label_progressbar.setText(text)
        self.progressbar_rpa.setValue(percent)
