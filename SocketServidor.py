import socket
import threading
import json
import mysql.connector
import decimal
from datetime import datetime, date

class SocketServer:
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.db_config = {
            'host': '127.0.0.1',
            'user': 'root',
            'password': 'Samuel0205',
            'database': 'PersisDatos'
        }

    def get_db_connection(self):
        try:
            return mysql.connector.connect(**self.db_config)
        except mysql.connector.Error as err:
            print(f"Error de conexión a BD: {err}")
            return None

    def json_serial(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.strftime('%Y-%m-%d')
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        raise TypeError(f"Tipo no serializable: {type(obj)}")

    def send_message(self, client_socket, message):
        try:
            message_bytes = message.encode('utf-8')
            message_size = len(message_bytes)
            client_socket.sendall(message_size.to_bytes(4, byteorder='big'))
            client_socket.sendall(message_bytes)
            return True
        except Exception as e:
            print(f"Error enviando mensaje: {e}")
            return False

    def receive_message(self, client_socket):
        try:
            size_data = client_socket.recv(4)
            if not size_data:
                return None
            message_size = int.from_bytes(size_data, byteorder='big')
            message_data = b''
            while len(message_data) < message_size:
                chunk = client_socket.recv(min(4096, message_size - len(message_data)))
                if not chunk:
                    return None
                message_data += chunk
            return message_data.decode('utf-8')
        except Exception as e:
            print(f"Error recibiendo mensaje: {e}")
            return None

    def handle_client(self, client_socket, address):
        print(f"Conexión establecida con {address}")
        try:
            while True:
                data = self.receive_message(client_socket)
                if not data:
                    print(f"Cliente {address} desconectado")
                    break

                try:
                    request = json.loads(data)
                    operation = request.get('operation')
                    print(f"Procesando operación: {operation} de {address}")

                    if operation == 'SELECT':
                        response = self.select_empleado(request.get('emp_id'))
                    elif operation == 'DELETE':
                        response = self.delete_empleado(request.get('emp_id'))
                    elif operation == 'INSERT':
                        response = self.insert_empleado(request.get('data'))
                    elif operation == 'UPDATE':
                        response = self.update_empleado(request.get('data'))
                    else:
                        response = {"status": "error", "message": "Operación no implementada"}

                    response_json = json.dumps(response, ensure_ascii=False, default=self.json_serial)
                    if not self.send_message(client_socket, response_json):
                        break

                except json.JSONDecodeError:
                    error_response = {"status": "error", "message": "JSON inválido"}
                    self.send_message(client_socket, json.dumps(error_response, ensure_ascii=False))
                except Exception as e:
                    error_response = {"status": "error", "message": f"Error del servidor: {str(e)}"}
                    self.send_message(client_socket, json.dumps(error_response, ensure_ascii=False))
        finally:
            try:
                client_socket.shutdown(socket.SHUT_RDWR)
            except:
                pass
            client_socket.close()
            print(f"Conexión cerrada con {address}")

    def select_empleado(self, emp_id):
        conn = self.get_db_connection()
        if not conn:
            return {"status": "error", "message": "Error de conexión a BD"}
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
            SELECT e.*, c.Cargo_Nombre, d.Depto_Nombre, 
                   g.Emp_Nombre as Gerente_Nombre, g.Emp_Apellidos as Gerente_Apellidos
            FROM Empleados e
            LEFT JOIN Cargos c ON e.Emp_Cargo_ID = c.Cargo_ID
            LEFT JOIN Departamentos d ON e.Emp_Depto_ID = d.Depto_ID
            LEFT JOIN Empleados g ON e.Emp_Gerente_ID = g.Emp_ID
            WHERE e.Emp_ID = %s
            """
            cursor.execute(query, (emp_id,))
            empleado = cursor.fetchone()
            return {"status": "success", "data": empleado} if empleado else {"status": "error", "message": "Empleado no encontrado"}
        except mysql.connector.Error as err:
            return {"status": "error", "message": f"Error en consulta: {err}"}
        finally:
            conn.close()

    def delete_empleado(self, emp_id):
        conn = self.get_db_connection()
        if not conn:
            return {"status": "error", "message": "Error de conexión a BD"}
        try:
            cursor = conn.cursor()
            query = "DELETE FROM Empleados WHERE Emp_ID = %s"
            cursor.execute(query, (emp_id,))
            conn.commit()
            return {"status": "success", "message": "Empleado eliminado correctamente"} if cursor.rowcount else {"status": "error", "message": "Empleado no encontrado"}
        except mysql.connector.Error as err:
            return {"status": "error", "message": f"Error al eliminar: {err}"}
        finally:
            conn.close()

    def insert_empleado(self, datos):
        conn = self.get_db_connection()
        if not conn:
            return {"status": "error", "message": "Error de conexión a BD"}
        try:
            cursor = conn.cursor()
            query = """
            INSERT INTO Empleados (
                Emp_Nombre, Emp_Apellidos, Emp_Correo,
                Emp_Fecha_Nacimiento, Emp_Sueldo, Emp_Comision,
                Emp_Fecha_Ingreso, Emp_Cargo_ID, Emp_Gerente_ID, Emp_Depto_ID
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                datos['nombre'],
                datos['apellidos'],
                datos['correo'],
                datos['fecha_nacimiento'],
                datos['sueldo'],
                datos.get('comision'),
                datos['fecha_ingreso'],
                datos['cargo_id'],
                datos.get('gerente_id'),
                datos['depto_id']
            ))
            conn.commit()
            return {"status": "success", "message": f"Empleado insertado con ID {cursor.lastrowid}"}
        except mysql.connector.Error as err:
            conn.rollback()
            return {"status": "error", "message": f"Error al insertar: {err}"}
        finally:
            conn.close()

    def update_empleado(self, datos):
        conn = self.get_db_connection()
        if not conn:
            return {"status": "error", "message": "Error de conexión a BD"}
        try:
            cursor = conn.cursor()
            query = """
            UPDATE Empleados SET
                Emp_Nombre = %s,
                Emp_Apellidos = %s,
                Emp_Correo = %s,
                Emp_Fecha_Nacimiento = %s,
                Emp_Sueldo = %s,
                Emp_Comision = %s,
                Emp_Cargo_ID = %s,
                Emp_Gerente_ID = %s,
                Emp_Depto_ID = %s
            WHERE Emp_ID = %s
            """
            cursor.execute(query, (
                datos['nombre'],
                datos['apellidos'],
                datos['correo'],
                datos['fecha_nacimiento'],
                datos['sueldo'],
                datos.get('comision'),
                datos['cargo_id'],
                datos.get('gerente_id'),
                datos['depto_id'],
                datos['emp_id']
            ))
            conn.commit()
            if cursor.rowcount:
                return {"status": "success", "message": "Empleado actualizado correctamente"}
            else:
                return {"status": "error", "message": "Empleado no encontrado o sin cambios"}
        except mysql.connector.Error as err:
            conn.rollback()
            return {"status": "error", "message": f"Error al actualizar: {err}"}
        finally:
            conn.close()

    def start_server(self):
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            print(f"Servidor iniciado en {self.host}:{self.port}")
            while True:
                client_socket, address = self.socket.accept()
                threading.Thread(target=self.handle_client, args=(client_socket, address), daemon=True).start()
        except KeyboardInterrupt:
            print("Servidor detenido por el usuario")
        finally:
            self.socket.close()
            print("Servidor cerrado")

if __name__ == "__main__":
    server = SocketServer()
    server.start_server()