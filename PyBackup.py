# saved as greeting-server.py
from PyInstall import installIfNeeded as ins


def importPackages():
    """
    Method which install all the necessaries packages for the script.
    :return: Nothing
    """
    ins('Pyro4')
    ins('simplejson')
    ins('time')
    ins('datetime')
    ins('threading')
    # ins('netifaces')
    ins('subprocess')
    ins('os')
    ins('re')
    ins('socket')


importPackages()

import Pyro4
import time, datetime
import threading, JSON_Read
# import netifaces as ni
from subprocess import Popen
import os
import socket


@Pyro4.expose
class PyBackup(object):
    """
    TODO
    """

    def __init__(self):
        self.copiando_mutex = threading.Lock()
        self.leyendo_mutex = threading.Lock()
        self.copiando = False
        self.leyendo = False
        self.configuracion = ""
        self.timeBackup = 0
        self.running = False
        self.ConfigPath = "config.json"
        self.db_backups_path = "db/"
        self.source_backups_path = "data/"
        self.dir_name = os.getcwd()
        self.hostname = socket.gethostname()

        self.read_configuration()

    def time_avaliable(self):
        """
        TODO
        :return:
        """
        now = datetime.datetime.now()
        hora_inicio, minuto_inicio = [int(i) for i in self.configuracion["start_time"].split(':')]
        hora_fin, minuto_fin = [int(i) for i in self.configuracion["end_time"].split(':')]
        start_time = now.replace(hour=hora_inicio, minute=minuto_inicio, second=0, microsecond=0)
        end_time = now.replace(hour=hora_fin, minute=minuto_fin, second=0, microsecond=0)
        return now > start_time and now < end_time

    def run(self):
        """
        TODO
        :return:
        """
        time.sleep(5)  # Delay inicial
        while self.running:
            print "COPIA"
            self.read_configuration()
            if self.configuracion["backup_time"] > 0:
                time.sleep(float(self.configuracion["backup_time"]))
            if self.time_avaliable():
                self.backup()

    def start(self):
        """
        TODO
        :return:
        """
        if not self.running:
            self.running = True
            self.timerthread = threading.Thread(target=self.run)
            self.timerthread.setDaemon(True)
            self.timerthread.start()

    def stop(self):
        """
        TODO
        :return:
        """
        self.running = False

    def hola(self):
        """
        TODO
        :return:
        """
        self.copiando_mutex.acquire()
        self.leyendo_mutex.acquire()
        self.leyendo_mutex.release()
        self.copiando_mutex.release()
        return "HOLA"

    def read_configuration(self):
        """
        TODO
        :return:
        """
        self.leyendo_mutex.acquire()
        if os.path.isfile(self.ConfigPath):
            self.configuracion = JSON_Read.JsonRead(self.ConfigPath).json
            # print self.configuracion
            self.dir_name = os.getcwd() + '/' + self.configuracion["dir_name"]
        else:
            print "No existe fichero de configuracion"
        self.leyendo_mutex.release()

    def set_configuration(self, data):
        """
        TODO
        :param data:
        :return:
        """
        self.leyendo_mutex.acquire()
        with open(self.ConfigPath, 'w') as outfile:
            outfile.write(data)
        self.leyendo_mutex.release()

    def backup(self):
        """
        TODO
        :return:
        """
        self.copiando_mutex.acquire()
        if self.copiando:
            self.copiando_mutex.release()
            return "Copia en Progreso..."
        else:
            self.copiando = True
            self.copiando_mutex.release()

            if self.mount_path():
                time.sleep(5)
                self.db_backup()
                self.folder_backup()
                time.sleep(5)
                self.unmount_path()

            self.copiando_mutex.acquire()
            self.copiando = False
            self.copiando_mutex.release()

    def mount_path(self):
        """
        TODO
        :return:
        """
        if not os.path.exists(self.dir_name):
            os.makedirs(self.dir_name)
        args = ['mount',
                self.configuracion["nfs_server"] + ':/' + self.configuracion["nfs_path"],
                self.dir_name]
        p1 = Popen(args)
        return True

    def unmount_path(self):
        """
        TODO
        :return:
        """
        args = ['umount',
                self.dir_name]
        p1 = Popen(args)

    def db_backup(self):
        """
        TODO
        :return:
        """
        db_pass, db_list, db_user = [self.configuracion["database"][i] for i in
                                     self.configuracion["database"]]
        destination_folder = self.dir_name + '/' + self.hostname + '/' + self.db_backups_path

        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)

        for route in db_list:
            destination_route = destination_folder + '/' + route
            export_name = db_list[route]
            if not os.path.exists(destination_route):
                os.makedirs(destination_route)
            args = ['mysqldump', '-u', db_user, '-p' + db_pass, '--databases', route]
            with open(destination_route + '/' + export_name + '.sql', 'wb', 0) as f:
                p1 = Popen(args, stdout=f)

    def folder_backup(self):
        """
        TODO
        :return:
        """
        path_list = self.configuracion["source"]["source_path_list"]
        destination_folder = self.dir_name + '/' + self.hostname + '/' + self.source_backups_path
        # destination_folder = self.configuracion["nfs_path"] + self.source_backups_path
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
        try:
            for route in path_list:
                if os.path.exists(path_list[route]):
                    if not os.path.exists(destination_folder + '/' + route):
                        os.makedirs(destination_folder + '/' + route)
                    args = ['rsync', '-a', path_list[route], destination_folder + '/' + route]
                    p1 = Popen(args)
                    p1.wait()
                else:
                    print "Carpeta no encontrada - " + path_list[route]

        except OSError:
            print "Ha ocurrido un error en el disco / rsync no instalado"
        except:
            print "Error en copia fichero"
            raise

    def borrar_contenido(self):
        """
        TODO
        :return:
        """
        if os.path.exists(self.dir_name):
            args = ['rm', '-rf', self.dir_name]
            p1 = Popen(args)


def getIp():
    """
    TODO
    :return:
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


if __name__ == "__main__":
    server = PyBackup()
    daemon = Pyro4.Daemon(host=getIp(), port=4040)
    uri = daemon.register(server, objectId="PyBackup")
    print("Ready. Object uri =", uri)
    daemon.requestLoop()
