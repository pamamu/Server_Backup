import Pyro4

server_ip="158.49.241.14"
server_port="4040"
PyBackup = Pyro4.Proxy("PYRO:PyBackup@{}:{}".format(server_ip, server_port))


PyBackup.start()
