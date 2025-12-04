# --- LIBRERIAS --- #
import socket
import time
import cv2

class RobotComm:

    # - Metodo constructor - #
    def __init__(self, ip="255.255.255.255", port=8888, timeout=0.2, logfile="datalog.txt"):
        # Atributos Comunicación UDP
        self.IP = ip
        self.PORT = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # Permitir reutilizar la dirección/puerto
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.sock.bind(("", port))
        except OSError as e:
            print(f"[ERROR] No se pudo vincular el puerto {port}: {e}")
            print(f"[INFO] Intentando cerrar conexiones existentes...")
            self.sock.close()
            # Crear nuevo socket con las mismas opciones
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(("", port))
            print(f"[OK] Puerto {port} vinculado correctamente")
        
        self.sock.settimeout(timeout)

        # Atributos Robots registrados y estados
        self.robots = []
        self.robot_states = {}  #id: estado de combate
        self.robot_comm_status = {}  #id: estado de comunicación (True/False)
        self.logfile = logfile

        # Respuestas
        self.respuesta = None
        self.mensaje_inicial = True

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
            self.robot_comm_status[robot_id] = True  # Por defecto comunicación OK
            print(f"[REGISTRADO] Robot ID {robot_id}")
            self.log("REGISTRO →", f"Robot {robot_id}")
    
    def update_comm_status(self, robot_id, comm_ok):
        """
        Actualiza el estado de comunicación de un robot.
        
        Args:
            robot_id: ID del robot
            comm_ok: True si la comunicación es correcta, False si hay error
        """
        if robot_id in self.robots:
            self.robot_comm_status[robot_id] = comm_ok

    # - Metodo enviar comando robot por UDP - #
    def enviarRobot(self, id_robot, ang, dist, out):
        """
        Descripcion: Esta funcion envia un mensaje al robot maestro por UDP, indicando el id del robot de destino
        Args: id_robot, angulo, distancia, in/out
        Returns: None
        """
        if self.respuesta or self.mensaje_inicial:
            self.mensaje_inicial = False
            self.respuesta = False

            if id_robot not in self.robots:
                msg = f"[ERROR] Robot ID {id_robot} no está registrado. Ignorando mensaje."
                print(msg)
                self.log("ERROR →", msg)
                return

            msg = f"id={id_robot}, ang={ang}, dist={dist}, Out={out}"
            self.sock.sendto(msg.encode(), (self.IP, self.PORT))

            print(f"[ENVIADO → Robot {id_robot}] {msg}")
            self.log("ENVIADO →", msg)

    # - Metodo recibir respuesta robot por UDP - #
    def recibirRespuesta(self):
        """
        Descripcion: Esta funcion gestiona la respuesta recibida del maestro
        Args: None
        Returns: None
        """
        try:
            data, addr = self.sock.recvfrom(1024)
            msg = data.decode(errors="ignore").strip()
            if msg.startswith("OK"):
                print(f"[RESPUESTA ← ESP] {msg}")
                self.log("RECIBIDO ←", msg)
                self.respuesta = True
                return True
            else:
                return False
        except socket.timeout:
            print("Respuesta no recibida")

    def close(self):
        """Cierra el socket correctamente."""
        if hasattr(self, 'sock'):
            self.sock.close()
            print("[CERRADO] Socket UDP cerrado")