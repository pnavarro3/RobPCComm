# !/usr/bin/env python3
# Autor: Ruben Sahuquillo y Pablo Navarro
# Este script prueba la comunicacion con modulos robot utilizando la libreria ComRobotLib.


# --- LIBRERIAS --- #
from ComRobotLib import RobotComm
import time

# Instanciar la comunicacion con los robots
robot_comm = RobotComm(ip="192.168.137.161", logfile="datalog.txt")

# Registrar robots
robot_comm.addRobot(0)
robot_comm.addRobot(1)
robot_comm.addRobot(2)

# Variables de prueba
ang = 0.0
dist = 0.0
out = False

# Bucle de comunicacion
def comm_loop():
    global ang, dist, out
    i = 0
    # Bucle infinito de envio y recepcion de datos
    while True:
        # Seleccionar el robot actual
        id_robot = robot_comm.robots[i]
        # Enviar comando al robot
        robot_comm.enviarRobot(id_robot, ang , dist, out)
        time.sleep(0.2)
        # Recibir respuesta del robot
        robot_comm.recibirRespuesta()

        # Actualizar variables de prueba
        if ang >= 360:
            ang = 0

        if dist >= 10:
            dist = 0

        ang += 5
        dist += 1

        # Cambiar al siguiente robot
        i += 1

        # Reiniciar el indice si se supera el numero de robots
        if i >= len(robot_comm.robots):
            i = 0


# Ejecutar el bucle de comunicacion
if __name__ == "__main__":
    comm_loop()