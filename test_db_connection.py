import mysql.connector

try:
    conn = mysql.connector.connect(
        host='127.0.0.1',        # O '127.0.0.1'
        user='root',             # Cambia si usas otro usuario
        password='Samuel0205',   # Cambia a tu contraseña real
        database='PersisDatos'
    )
    if conn.is_connected():
        print("Conexión exitosa a la base de datos")
    conn.close()
except Exception as e:
    print("Error de conexión:", e)


