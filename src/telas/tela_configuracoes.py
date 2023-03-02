from PySide6.QtWidgets import QMainWindow, QMessageBox
from PySide6.QtCore import Signal
import src.utils.components as components
from src.ui.dialog_configuaracoes import Ui_MainWindow as DialogConfiguracoes

class eSocialConfiguracoes(QMainWindow):
    config_run = Signal(dict)

    def __init__(self):
        super().__init__()
        self.__window = DialogConfiguracoes()

    def init_gui(self, configuracao):
        """
        Declarar componentes que serão utilizados da interface
        """
        self.__window.setupUi(self)
        self.setWindowTitle('Configurações')

        self.__btn_diretorio_trabalho = self.__window.btn_diretorio_trabalho
        self.__btn_cancelar = self.__window.btn_concertar_configuracoes
        self.__btn_confirmar_configuracoes = self.__window.btn_confirmar_configuracoes

        self.__edit_diretorio_trabalho = self.__window.edit_diretorio_trabalho
        self.__edit_banco_dominio = self.__window.edit_banco_dominio
        self.__edit_usuario_dominio = self.__window.edit_usuario_dominio
        self.__edit_senha_dominio = self.__window.edit_senha_dominio
        self.__edit_empresa_rubricas_dominio = self.__window.edit_empresa_rubricas_dominio
        
        self.__edit_usuario_sgd = self.__window.edit_usuario_sgd
        self.__edit_senha_sgd = self.__window.edit_senha_sgd

        self.__btn_diretorio_trabalho.clicked.connect(self.busca_diretorio)
        self.__btn_cancelar.clicked.connect(self.close)
        self.__btn_confirmar_configuracoes.clicked.connect(self.salvar)

        self.__edit_diretorio_trabalho.setText(configuracao["diretorio_trabalho"])
        self.__edit_banco_dominio.setText(configuracao["base_dominio"])
        self.__edit_usuario_dominio.setText(configuracao["usuario_dominio"])
        self.__edit_senha_dominio.setText(configuracao["senha_dominio"])
        self.__edit_empresa_rubricas_dominio.setText(str(configuracao["empresa_padrao_rubricas"]))
        self.__edit_usuario_sgd.setText(configuracao["usuario_sgd"])
        self.__edit_senha_sgd.setText(configuracao["senha_sgd"])

        self.show()

    def busca_diretorio(self):
        path = components.ask_directory(self.window(), 'Selecione o diretório de trabalho.')
        self.__edit_diretorio_trabalho.setText(path)

    def alerta(self, mensagem, titulo = "Atenção"):
        msg = QMessageBox()
        msg.setWindowTitle(titulo)
        msg.setText(mensagem)
        msg.exec()

    def salvar(self):
        if self.__edit_diretorio_trabalho.text()=="":
            self.alerta("Preencha o diretório de trabalho.","Atenção")
            self.busca_diretorio()

        dados = {
            "diretorio_trabalho": self.__edit_diretorio_trabalho.text(),
            "base_dominio": self.__edit_banco_dominio.text(),
            "usuario_dominio": self.__edit_usuario_dominio.text(),
            "senha_dominio": self.__edit_senha_dominio.text(),
            "empresa_padrao_rubricas": self.__edit_empresa_rubricas_dominio.text(),
            "usuario_sgd": self.__edit_usuario_sgd.text(),
            "senha_sgd": self.__edit_senha_sgd.text()
        }
        
        self.config_run.emit(dados)
        self.close()