# --- LIBRERIAS --- #
import socket
import time
import cv2
from flask import Flask, render_template, Response, redirect, url_for

# --- CLASE --- #
class RobotComm:

    # - Metodo constructor - #
    def __init__(self, ip="255.255.255.255", port=8888, timeout=0.2, logfile="datalog.txt"):
        # Atributos Comunicación UDP
        self.IP = ip
        self.PORT = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.bind(("", port))
        self.sock.settimeout(timeout)

        # Atributos Robots registrados y estados
        self.robots = []
        self.robot_states = {}
        self.logfile = logfile

        # Respuestas
        self.respuesta = None
        self.mensaje_inicial = True

        # Webcam
        self.camera = cv2.VideoCapture(0)

        # Flask
        self.app = Flask(__name__)
        self._setup_routes()


    # - Metodo escribir datalog - #
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
            print(f"[REGISTRADO] Robot ID {robot_id}")
            self.log("REGISTRO →", f"Robot {robot_id}")

    # - Metodo enviar comando robot por UDP - #
    def enviarRobot(self, id_robot, ang, dist, out):
        """
        Descripcion: Esta funcion envia un mensaje al robot maestro por UDP, indicando el id del robot de destino
        Args: id_robot, angulo, distancia, in/out
        Returns: None
        """
        if self.respuesta or self.mensaje_inicial:
            self.mensaje_inicial = False

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
            self.respuesta = data.decode(errors="ignore").strip()
            if self.respuesta.startswith("OK"):
                print(f"[RESPUESTA ← ESP] {self.respuesta}")
                self.log("RECIBIDO ←", self.respuesta)

        except socket.timeout:
            print("Respuesta no recibida")

    def gen_frames(self):
        while True:
            success, frame = self.camera.read()
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    def _setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template('index.html', states=self.robot_states)

        @self.app.route('/video_feed')
        def video_feed():
            return Response(self.gen_frames(),
                            mimetype='multipart/x-mixed-replace; boundary=frame')

        @self.app.route('/start')
        def start_fight():
            for rid in self.robot_states:
                self.robot_states[rid] = "peleando"
            self.log("PELEA →", "Se inició la pelea")
            return redirect(url_for('index'))

        @self.app.route('/stop')
        def stop_fight():
            for rid in self.robot_states:
                self.robot_states[rid] = "fuera de combate"
            self.log("PELEA →", "Se detuvo la pelea")
            return redirect(url_for('index'))

    def run_server(self, host="0.0.0.0", port=5000):
        self.app.run(host=host, port=port, debug=True)
