from PCComm import RobotComm
import time
# Crear instancia con datalog activo
robot_comm = RobotComm(logfile="datalog.txt")

# Registrar robots
robot_comm.addRobot(0)
#robot_comm.addRobot(1)

ang = 10.0
dist = 0.0
out = 0.0

def comm_loop():
    global ang, dist, out
    i = 0
    while True:
        enter = input("Presiona enter")
        
        if enter == "":
            id_robot = robot_comm.robots[i]

            ang += 5

            robot_comm.enviarRobot(id_robot, ang, dist, out)

        i += 1
        if i >= len(robot_comm.robots):
            i = 0

if __name__ == "__main__":
    comm_loop()