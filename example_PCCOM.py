from ComRobotLib import RobotComm, Interface
import time
import threading
import cv2

# Crear instancia con datalog activo
robot_comm = RobotComm(logfile="datalog.txt")

# Registrar robots
robot_comm.addRobot(0)
robot_comm.addRobot(1)
robot_comm.addRobot(2)

# Abrir cámara PRIMERO
print("Abriendo cámara...")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: No se puede abrir la cámara ID 0")
    exit(1)

print("✓ Cámara abierta correctamente")

# Verificar que puede capturar
ret, test_frame = cap.read()
if not ret:
    print("ERROR: La cámara se abrió pero no puede capturar frames")
    cap.release()
    exit(1)

print(f"✓ Frame de prueba capturado: {test_frame.shape}")

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

def camera_loop():
    """Captura frames y los envía a la interfaz"""
    print("Iniciando bucle de cámara...")
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if ret:
            interface.update_frame(frame)
            frame_count += 1
            if frame_count % 100 == 0:
                print(f"Frames capturados: {frame_count}")
        else:
            print("WARNING: No se pudo leer frame de la cámara")
            time.sleep(0.1)  # Esperar un poco antes de reintentar
        time.sleep(0.033)  # ~30 FPS

# Crear interfaz web
interface = Interface(robot_comm)

# Lanzar el bucle de comunicación en un hilo aparte
t_comm = threading.Thread(target=comm_loop, daemon=True)
t_comm.start()
print("✓ Thread de comunicación iniciado")

# Lanzar el bucle de la cámara en un hilo aparte
t_camera = threading.Thread(target=camera_loop, daemon=True)
t_camera.start()
print("✓ Thread de cámara iniciado")

# Arrancar el servidor Flask en el hilo principal (o en otro thread si prefieres)
print("\n" + "="*60)
print("Iniciando servidor web en http://localhost:5000")
print("Presiona Ctrl+C para detener")
print("="*60 + "\n")

try:
    # OPCIÓN 1: Flask en el hilo principal (bloquea pero los threads siguen corriendo)
    interface.run_server(debug=False)
    
    # OPCIÓN 2: Flask en otro thread (permite hacer más cosas en el main)
    # t_flask = threading.Thread(target=lambda: interface.run_server(debug=False), daemon=True)
    # t_flask.start()
    # 
    # # Mantener el programa vivo
    # while True:
    #     time.sleep(1)
    
except KeyboardInterrupt:
    print("\n[CTRL+C] Deteniendo programa...")
    cap.release()
    robot_comm.close()
    print("✓ Recursos liberados")
