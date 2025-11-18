import socket
import time

class RobotComm:
    def __init__(self, ip="255.255.255.255", port=8888, timeout=0.2):
        self.IP = ip
        self.PORT = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.bind(("", port))
        self.sock.settimeout(timeout)

        self.robots = []


    def addRobot(self, robot_id):
        if robot_id not in self.robots:
            self.robots.append(robot_id)
            print(f"[REGISTRADO] Robot ID {robot_id}")


    def enviarRobot(self, id_robot, ang, dist, out):
        if id_robot not in self.robots:
            print(f"[ERROR] Robot ID {id_robot} no está registrado. Ignorando mensaje.")
            return
        msg = f"id={id_robot}, ang={ang}, dist={dist}, Out={out}"
        self.sock.sendto(msg.encode(), (self.IP, self.PORT))
        print(f"[ENVIADO → Robot {id_robot}] {msg}")


    def recibirRespuesta(self):
        try:
            data, addr = self.sock.recvfrom(1024)
            msg = data.decode(errors="ignore").strip()
            if msg.startswith("OK"):
                print(f"[RESPUESTA ← ESP] {msg}")
        except socket.timeout:
            pass
