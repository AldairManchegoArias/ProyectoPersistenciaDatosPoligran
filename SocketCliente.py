import socket
import json
from datetime import datetime

class SocketClient:
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        self.socket = None

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(30)
            self.socket.connect((self.host, self.port))
            print(f"✓ Conectado al servidor {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return False

    def disconnect(self):
        if self.socket:
            try:
                self.socket.close()
                print("✓ Desconectado del servidor")
            except:
                pass
            finally:
                self.socket = None

    def send_message(self, message):
        try:
            message_bytes = message.encode('utf-8')
            message_size = len(message_bytes)
            self.socket.sendall(message_size.to_bytes(4, byteorder='big'))
            self.socket.sendall(message_bytes)
            return True
        except Exception as e:
            print(f"Error enviando mensaje: {e}")
            return False

    def receive_message(self):
        try:
            size_data = self.socket.recv(4)
            if not size_data:
                return None
            message_size = int.from_bytes(size_data, byteorder='big')
            message_data = b''
            while len(message_data) < message_size:
                chunk = self.socket.recv(min(4096, message_size - len(message_data)))
                if not chunk:
                    return None
                message_data += chunk
            return message_data.decode('utf-8')
        except Exception as e:
            print(f"Error recibiendo mensaje: {e}")
            return None

    def send_request(self, request):
        try:
            json_data = json.dumps(request, ensure_ascii=False)
            if not self.send_message(json_data):
                return {"status": "error", "message": "Error enviando solicitud"}
            response_data = self.receive_message()
            if not response_data:
                return {"status": "error", "message": "Sin respuesta del servidor"}
            return json.loads(response_data)
        except Exception as e:
            return {"status": "error", "message": f"Error: {str(e)}"}

    def validar_fecha(self, fecha_str):
        try:
            datetime.strptime(fecha_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def validar_email(self, email):
        return '@' in email and '.' in email.split('@')[1]

    def insertar_empleado(self):
        print("\n=== INSERTAR EMPLEADO ===")
        try:
            nombre = input("Nombre: ").strip()
            apellidos = input("Apellidos: ").strip()
            correo = input("Correo electrónico: ").strip()
            fecha_nacimiento = input("Fecha nacimiento (YYYY-MM-DD): ").strip()
            sueldo = float(input("Sueldo: "))
            fecha_ingreso = input("Fecha ingreso (YYYY-MM-DD): ").strip()
            cargo_id = int(input("ID Cargo: "))
            depto_id = int(input("ID Departamento: "))

            if not all([nombre, apellidos, correo]):
                print("❌ Campos obligatorios vacíos")
                return

            if not self.validar_email(correo) or not self.validar_fecha(fecha_nacimiento) or not self.validar_fecha(fecha_ingreso):
                print("❌ Formato incorrecto en fecha o correo")
                return

            datos = {
                'nombre': nombre,
                'apellidos': apellidos,
                'correo': correo,
                'fecha_nacimiento': fecha_nacimiento,
                'sueldo': sueldo,
                'comision': None,
                'fecha_ingreso': fecha_ingreso,
                'cargo_id': cargo_id,
                'gerente_id': None,
                'depto_id': depto_id
            }

            comision = input("Comisión (opcional): ").strip()
            if comision:
                datos['comision'] = float(comision)

            gerente_id = input("ID Gerente (opcional): ").strip()
            if gerente_id:
                datos['gerente_id'] = int(gerente_id)

            request = {'operation': 'INSERT', 'data': datos}
            response = self.send_request(request)
            print(f"{'✅' if response['status'] == 'success' else '❌'} {response['message']}")

        except Exception as e:
            print(f"❌ Error: {e}")

    def actualizar_empleado(self):
        print("\n=== ACTUALIZAR EMPLEADO ===")
        try:
            emp_id = int(input("ID del empleado: "))
            response = self.send_request({'operation': 'SELECT', 'emp_id': emp_id})
            if response['status'] != 'success':
                print(f"❌ {response['message']}")
                return

            emp = response['data']
            nombre = input(f"Nombre [{emp['Emp_Nombre']}]: ").strip() or emp['Emp_Nombre']
            apellidos = input(f"Apellidos [{emp['Emp_Apellidos']}]: ").strip() or emp['Emp_Apellidos']
            correo = input(f"Correo [{emp['Emp_Correo']}]: ").strip() or emp['Emp_Correo']
            fecha_nacimiento = input(f"Fecha nacimiento [{emp['Emp_Fecha_Nacimiento']}]: ").strip() or emp['Emp_Fecha_Nacimiento']
            sueldo = input(f"Sueldo [{emp['Emp_Sueldo']}]: ").strip() or emp['Emp_Sueldo']
            cargo_id = input(f"ID Cargo [{emp.get('Emp_Cargo_ID')}]: ").strip() or emp.get('Emp_Cargo_ID')
            depto_id = input(f"ID Departamento [{emp.get('Emp_Depto_ID')}]: ").strip() or emp.get('Emp_Depto_ID')
            comision = input(f"Comisión [{emp.get('Emp_Comision', 'N/A')}]: ").strip() or emp.get('Emp_Comision')
            gerente_id = input(f"ID Gerente [{emp.get('Emp_Gerente_ID', 'N/A')}]: ").strip() or emp.get('Emp_Gerente_ID')

            datos = {
                'emp_id': emp_id,
                'nombre': nombre,
                'apellidos': apellidos,
                'correo': correo,
                'fecha_nacimiento': fecha_nacimiento,
                'sueldo': float(sueldo),
                'cargo_id': int(cargo_id),
                'depto_id': int(depto_id),
                'comision': float(comision) if comision else None,
                'gerente_id': int(gerente_id) if gerente_id else None
            }

            request = {'operation': 'UPDATE', 'data': datos}
            response = self.send_request(request)
            print(f"{'✅' if response['status'] == 'success' else '❌'} {response['message']}")

        except Exception as e:
            print(f"❌ Error: {e}")

    def consultar_empleado(self):
        print("\n=== CONSULTAR EMPLEADO ===")
        try:
            emp_id = int(input("ID del empleado: "))
            request = {'operation': 'SELECT', 'emp_id': emp_id}
            response = self.send_request(request)
            if response['status'] == 'success':
                emp = response['data']
                print(f"\nID: {emp['Emp_ID']}\nNombre: {emp['Emp_Nombre']} {emp['Emp_Apellidos']}\nCorreo: {emp['Emp_Correo']}")
                print(f"Fecha Nacimiento: {emp['Emp_Fecha_Nacimiento']}")
                print(f"Sueldo: ${emp['Emp_Sueldo']:,.2f}")
                print(f"Comisión: {emp['Emp_Comision'] or 'N/A'}")
                print(f"Cargo: {emp.get('Cargo_Nombre', 'N/A')}")
                print(f"Departamento: {emp.get('Depto_Nombre', 'N/A')}")
                print(f"Estado: {emp.get('Emp_Estado', 'Activo')}")
                if emp.get('Gerente_Nombre'):
                    print(f"Gerente: {emp['Gerente_Nombre']} {emp['Gerente_Apellidos']}")
            else:
                print(f"❌ {response['message']}")
        except Exception as e:
            print(f"❌ Error: {e}")

    def eliminar_empleado(self):
        print("\n=== ELIMINAR EMPLEADO ===")
        try:
            emp_id = int(input("ID del empleado a eliminar: "))
            confirm = input(f"¿Eliminar empleado con ID {emp_id}? (s/n): ").strip().lower()
            if confirm != 's':
                print("❌ Operación cancelada")
                return

            request = {'operation': 'DELETE', 'emp_id': emp_id}
            response = self.send_request(request)
            print(f"{'✅' if response['status'] == 'success' else '❌'} {response['message']}")
        except Exception as e:
            print(f"❌ Error: {e}")

    def iniciar(self):
        if not self.connect():
            return

        while True:
            print("\n" + "="*40)
            print("      MENÚ CLIENTE DE EMPLEADOS")
            print("="*40)
            print("1. Insertar nuevo empleado")
            print("2. Actualizar empleado existente")
            print("3. Consultar empleado")
            print("4. Eliminar empleado")
            print("5. Salir")

            opcion = input("Seleccione una opción: ").strip()
            if opcion == '1':
                self.insertar_empleado()
            elif opcion == '2':
                self.actualizar_empleado()
            elif opcion == '3':
                self.consultar_empleado()
            elif opcion == '4':
                self.eliminar_empleado()
            elif opcion == '5':
                print(" Cerrando cliente...")
                break
            else:
                print("❌ Opción inválida. Intente de nuevo.")

        self.disconnect()


if __name__ == "__main__":
    cliente = SocketClient()
    cliente.iniciar()