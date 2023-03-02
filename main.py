from PySide6.QtWidgets import QApplication
from src.telas.tela_inicial import eSocial

if __name__ == '__main__':
    app = QApplication([])
    window = eSocial()
    window.init_gui()
    app.exec()
