import socket
import time

class RobotComm:
    def __init__(self, ip="255.255.255.255", port=8888, timeout=0.2, logfile="datalog.txt"):
        self.IP = ip
        self.PORT = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.bind(("", port))
        self.sock.settimeout(timeout)

        self.robots = []
        self.logfile = logfile

    # DATALOG
    def log(self, tipo, mensaje):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] {tipo} {mensaje}\n"

        with open(self.logfile, "a", encoding="utf-8") as f:
            f.write(line)


    def addRobot(self, robot_id):
        if robot_id not in self.robots:
            self.robots.append(robot_id)
            print(f"[REGISTRADO] Robot ID {robot_id}")
            self.log("REGISTRO →", f"Robot {robot_id}")


    def enviarRobot(self, id_robot, ang, dist, out):
        if id_robot not in self.robots:
            msg = f"[ERROR] Robot ID {id_robot} no está registrado. Ignorando mensaje."
            print(msg)
            self.log("ERROR →", msg)
            return

        msg = f"id={id_robot}, ang={ang}, dist={dist}, Out={out}"
        self.sock.sendto(msg.encode(), (self.IP, self.PORT))

        print(f"[ENVIADO → Robot {id_robot}] {msg}")
        self.log("ENVIADO →", msg)


    def recibirRespuesta(self):
        try:
            data, addr = self.sock.recvfrom(1024)
            msg = data.decode(errors="ignore").strip()

            if msg.startswith("OK"):
                print(f"[RESPUESTA ← ESP] {msg}")
                self.log("RECIBIDO ←", msg)

        except socket.timeout:
            pass