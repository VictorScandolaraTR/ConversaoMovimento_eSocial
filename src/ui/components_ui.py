from PySide6.QtWidgets import (
    QMessageBox,
    QFileDialog
)


def message_error(container, message):
    return QMessageBox.critical(container, 'ERRO', message)


def message_sucess(container, message):
    return QMessageBox.information(container, 'SUCESSO', message)


def message_info(container, message):
    return QMessageBox.information(container, 'INFO', message)


def message_error_connection(container, database):
    return QMessageBox.critical(container, 'ERRO', f'Conexão com banco de dados {database} falhou!')


def confirm_message(container, message):
    option = QMessageBox.question(container, 'CONFIRMAR', message)
    if option == 16384:
        return True
    else:
        return False


def ask_directory(container, message):
    folder_path = QFileDialog.getExistingDirectory(container, message, '', options=QFileDialog.DontUseNativeDialog)
    return folder_path


def ask_file(container, message):
    file_path = QFileDialog.getOpenFileName(container, message, '', options=QFileDialog.DontUseNativeDialog)
    return file_path
