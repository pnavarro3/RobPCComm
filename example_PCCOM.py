from ComRobotLib import RobotComm
import time

# Crear instancia
robot_comm = RobotComm()

# Registrar robots
robot_comm.addRobot(0)
robot_comm.addRobot(1)
robot_comm.addRobot(2)

i = 0
while True:
    # Elige id robot a enviar mensaje
    id_robot = robot_comm.robots[i]

    ang = 99.0
    dist = 0.11
    out = 0

    # Enviar comando parametros
    robot_comm.enviarRobot(id_robot, ang, dist, out)

    # Recibir parametros
    start = time.time()
    while time.time() - start < 0.3:
        robot_comm.recibirRespuesta()

    # Cambiar al siguiente robot
    i = i + 1

    # Comprobar índice de robot
    if i >= len(robot_comm.robots):
        i = 0
    
    time.sleep(0.2)