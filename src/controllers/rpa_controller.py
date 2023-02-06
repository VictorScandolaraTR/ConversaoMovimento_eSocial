from PySide6.QtCore import QObject, Signal
import socket
import subprocess
import tempfile


class Controller(QObject):
    finished = Signal()
    success = Signal(bool, str, list)
    progress = Signal(list)

    def init(self):
        self.__all_devices = self.list_devices()
        self.__default_port = 1112

    def devices_availables(self):
        """
        retorna quais IPs possuem o agente executando
        """
        try:
            # conta quantos dispositivos tem na rede e gera um percentual do tempo estimado
            percent = 80 / len(self.__all_devices)
            sum_percent = 20

            self.__available_devices = []
            jobs = []
            for ip in self.__all_devices:
                sum_percent += percent
                self.progress.emit([f'Verificando máquinas que possuem agente...', sum_percent])
                is_available(ip, self.__available_devices, self.__default_port)

            self.success.emit(True, '', self.__available_devices)
            self.finished.emit()
        except Exception as e:
            self.success.emit(False, 'Erro ao buscar agente!', [])
            self.finished.emit()

    def list_devices(self):
        """
        Lista todos os devices da rede
        """
        devices = subprocess.run(['arp', '-a'], stdout=subprocess.PIPE)
        stdout = devices.stdout

        # arquivo temporário
        temp = tempfile.NamedTemporaryFile(delete=False)

        # gravar saida do comando
        with open(temp.name, 'w') as output:
            try:
                output.write(stdout.decode('UTF-8'))
            except:
                output.write(stdout.decode('ANSI'))

        devices = []
        # ler dados e gerar uma lista de IPs
        with open(temp.name) as output:
            data = output.readlines()
            for line in data:
                if line.strip() == '': continue
                if 'Interface' in line: continue
                if 'Physical Address' in line: continue
                if '255.255' in line: continue
                devices.append(line[:24].strip())

        temp.close()
        return devices


def is_available(ip, devices, port):
    """
    checa se determinado IP está executando o agente
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        devices.append(ip)
    except Exception as e:
        pass
    finally:
        sock.close()
