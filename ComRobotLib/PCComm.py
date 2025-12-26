# !/usr/bin/env python3
# Autor: Ruben Sahuquillo y Pablo Navarro
# Libreria de comunicacion con modulos robot utilizando TCP y gestion de interfaz web con Flask.


# --- LIBRERIAS --- #
import socket
import time
import cv2
from flask import Flask, render_template, Response, redirect, url_for
import struct

# --- CLASE INTERFAZ FLASK --- #
class Interface:
    """Clase para manejar la interfaz web Flask del sistema de robots."""
    
    def __init__(self, robot_comm):
        """
        Inicializa la interfaz web.
        
        Args:
            robot_comm: Instancia de RobotComm para acceder a estados y log
        """
        self.robot_comm = robot_comm
        self.current_frame = None
        
        # Flask
        self.app = Flask(__name__)
        self._setup_routes()
    
    def update_frame(self, frame):
        """
        Actualiza el frame actual para el streaming.
        
        Args:
            frame: Frame de OpenCV (numpy array) a mostrar
        """
        self.current_frame = frame
    
    def gen_frames(self):
        """Generador de frames para el streaming de video."""
        while True:
            if self.current_frame is not None:
                ret, buffer = cv2.imencode('.jpg', self.current_frame)
                if ret:
                    frame = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.033)  # ~30 FPS
    
    def _setup_routes(self):
        """Configura las rutas de Flask."""
        @self.app.route('/')
        def index():
            return render_template('index.html', 
                                   states=self.robot_comm.robot_states,
                                   comm_status=self.robot_comm.robot_comm_status)

        @self.app.route('/video_feed')
        def video_feed():
            return Response(self.gen_frames(),
                            mimetype='multipart/x-mixed-replace; boundary=frame')

        @self.app.route('/start')
        def start_fight():
            for rid in self.robot_comm.robot_states:
                self.robot_comm.robot_states[rid] = "peleando"
            self.robot_comm.log("PELEA ->", "Se inició la pelea")
            return redirect(url_for('index'))

        @self.app.route('/stop')
        def stop_fight():
            for rid in self.robot_comm.robot_states:
                self.robot_comm.robot_states[rid] = "fuera de combate"
            self.robot_comm.log("PELEA ->", "Se detuvo la pelea")
            return redirect(url_for('index'))
    
    def run_server(self, host="0.0.0.0", port=5000, debug=True):
        """
        Inicia el servidor Flask.
        
        Args:
            host: Host donde correrá el servidor
            port: Puerto donde correrá el servidor
            debug: Modo debug de Flask
        """
        self.app.run(host=host, port=port, debug=debug)


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

    # - Metodo enviar comando robot por UDP - #
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
        

    # - Metodo recibir respuesta robot por UDP - #
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
            print("[CERRADO] Socket UDP cerrado")