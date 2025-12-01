from ComRobotLib import RobotComm
import time
import threading

# Crear instancia con datalog activo
robot_comm = RobotComm(logfile="datalog.txt")

# Registrar robots
robot_comm.addRobot(0)
robot_comm.addRobot(1)
robot_comm.addRobot(2)

def comm_loop():
    i = 0
    while True:
        # Obtener el ID del robot actual
        id_robot = robot_comm.robots[i]

        ang = 99.0
        dist = 0.11
        out = 0

        # Enviar comando con parámetros
        robot_comm.enviarRobot(id_robot, ang, dist, out)

        # Intentar recibir respuesta durante 300 ms
        start = time.time()
        while time.time() - start < 0.3:
            msg = robot_comm.recibirRespuesta()

        # Avanzar al siguiente robot
        i += 1
        if i >= len(robot_comm.robots):
            i = 0

        time.sleep(0.2)

# Lanzar el bucle de comunicación en un hilo aparte
t_comm = threading.Thread(target=comm_loop, daemon=True)
t_comm.start()

# Arrancar el servidor web (habrá que comprobar si funciona de esta manera sin bloquear la comunicación)
robot_comm.run_server()
