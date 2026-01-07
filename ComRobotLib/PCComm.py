# !/usr/bin/env python3
# Autor: Ruben Sahuquillo y Pablo Navarro
# Libreria de comunicacion con modulos robot utilizando TCP y gestion de interfaz web con Flask.


# --- LIBRERIAS --- #
import socket
import time
import cv2

# --- CLASE COMUNICACION ROBOT --- #
class RobotComm:

    # - Metodo constructor - #
    def __init__(self, ip="10.74.94.237", port=8888, timeout=1, logfile="datalog.txt"):
        # Atributos Comunicación TCP
        self.IP = ip
        self.PORT = port
        self._client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._client.connect((self.IP, self.PORT))

        # Atributos Robots registrados y estados
        self.robots = []
        self.robot_states = {}  #id: estado de combate
        self.robot_comm_status = {}  #id: estado de comunicación (True/False)
        self.logfile = logfile
        self.actual_id = None

        # Webcam
        self.camera = cv2.VideoCapture(0)


    # - Metodo escribir datalog - #
    # DATALOG
    def log(self, tipo, mensaje):
        """
        Descripcion: Esta funcion crea el datalog con los datos
        Args: tipo(enviado o recibido), mensaje
        Returns: None
        """
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] {tipo} {mensaje}\n"
        with open(self.logfile, "a", encoding="utf-8") as f:
            f.write(line)


    # ROBOTS
    # - Metodo añadir robot a lista de id - #
    def addRobot(self, robot_id):
        """
        Descripcion: Esta funcion añade id del robot a la lista de robots
        Args: robot_id
        Returns: None
        """
        if robot_id not in self.robots:
            self.robots.append(robot_id)
            self.robot_states[robot_id] = "esperando"
            self.robot_comm_status[robot_id] = True
            print(f"[REGISTRADO] Robot ID {robot_id}")
            self.log("REGISTRO ->", f"Robot {robot_id}")
    
    def update_comm_status(self, robot_id, comm_ok):
        """
        Actualiza el estado de comunicación de un robot.
        
        Args:
            robot_id: ID del robot
            comm_ok: True si la comunicación es correcta, False si hay error
        """
        if robot_id in self.robots:
            self.robot_comm_status[robot_id] = comm_ok

    # - Metodo enviar comando robot por TCP - #
    def enviarRobot(self, id_robot, ang, dist, out):
        """
        Descripcion: Esta funcion envia un mensaje al robot maestro por UDP, indicando el id del robot de destino
        Args: id_robot, angulo, distancia, in/out
        """
        self.actual_id = id_robot
        if id_robot not in self.robots:
            msg = f"[ERROR] Robot ID {id_robot} no está registrado. Ignorando mensaje."
            print(msg)
            self.log("ERROR ->", msg)
            return

        msg_bytes = struct.pack('Iff?', id_robot, ang, dist, out)
        self._client.send(msg_bytes)
        
        print(f"[ENVIADO -> Robot {id_robot}] id={id_robot}, ang={ang}, dist={dist}, out={out}")
        self.log("ENVIADO ->", msg_bytes)
        

    # - Metodo recibir respuesta robot por TCP - #
    def recibirRespuesta(self):
        """
        Descripcion: Esta funcion gestiona la respuesta recibida del maestro
        Args: None
        Returns: None
        """
        try:
            self._client.settimeout(1)
            response = self._client.recv(1024)
            self._client.settimeout(None)

            if response:
                print(f"Response -> {response.decode(errors='ignore')}")
                return True
            return False
        except socket.timeout as e:
            print(f"Tiempo de espera agotado esperando al robot {self.actual_id}")
            return False

    def close(self):
        """Cierra el socket correctamente."""
        if hasattr(self, 'sock'):
            self.sock.close()
            print("[CERRADO] Socket TCP cerrado")