import os
import sys

import psycopg2
from psycopg2 import errors, sql


DB_NAME = os.getenv("PGDATABASE", "tarea1")
DB_HOST = os.getenv("PGHOST", "localhost")
DB_PORT = os.getenv("PGPORT", "5432")
DB_USER = os.getenv("PGUSER", "postgres")
DB_PASSWORD = os.getenv("PGPASSWORD", "")
MAINTENANCE_DB = os.getenv("PGMAINTDB", "postgres")


def conectar(nombre_bd=DB_NAME):
    return psycopg2.connect(
        dbname=nombre_bd,
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def crear_base_datos():
    try:
        conn = conectar(MAINTENANCE_DB)
        conn.autocommit = True
        cur = conn.cursor()

        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
        existe = cur.fetchone()

        if not existe:
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
            print(f"Base de datos '{DB_NAME}' creada correctamente.")

        cur.close()
        conn.close()
    except psycopg2.OperationalError as e:
        print("No se pudo conectar a PostgreSQL.")
        print("Revisa que el servidor este activo y que tus credenciales sean correctas.")
        print(f"Detalle: {e}")
        sys.exit(1)
    except errors.InsufficientPrivilege:
        print(f"No tienes permisos para crear la base de datos '{DB_NAME}'.")
        print("Creala manualmente y ejecuta el programa otra vez.")
        sys.exit(1)


def crear_tabla():
    conn = conectar()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS alumno (
            id SERIAL PRIMARY KEY,
            carnet VARCHAR(15) UNIQUE NOT NULL,
            nombre VARCHAR(100) NOT NULL,
            apellido VARCHAR(100) NOT NULL,
            carrera VARCHAR(150),
            email VARCHAR(150),
            telefono VARCHAR(20),
            fecha_registro DATE DEFAULT CURRENT_DATE
        );
        """
    )
    conn.commit()
    cur.close()
    conn.close()


def leer_texto(mensaje, obligatorio=False, maximo=None):
    while True:
        valor = input(mensaje).strip()
        if obligatorio and not valor:
            print("Este campo es obligatorio.")
            continue
        if maximo and len(valor) > maximo:
            print(f"El texto no debe superar {maximo} caracteres.")
            continue
        return valor or None


def agregar_alumno():
    print("\n--- Agregar alumno ---")
    carnet = leer_texto("Carnet: ", obligatorio=True, maximo=15)
    nombre = leer_texto("Nombre: ", obligatorio=True, maximo=100)
    apellido = leer_texto("Apellido: ", obligatorio=True, maximo=100)
    carrera = leer_texto("Carrera: ", maximo=150)
    email = leer_texto("Email: ", maximo=150)
    telefono = leer_texto("Telefono: ", maximo=20)

    conn = None
    cur = None
    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO alumno (carnet, nombre, apellido, carrera, email, telefono)
            VALUES (%s, %s, %s, %s, %s, %s);
            """,
            (carnet, nombre, apellido, carrera, email, telefono),
        )
        conn.commit()
        print("Alumno agregado correctamente.")
    except errors.UniqueViolation:
        if conn:
            conn.rollback()
        print("Error: ya existe un alumno con ese carnet.")
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        print(f"Error al agregar alumno: {e}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def buscar_por_carnet(carnet):
    conn = conectar()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, carnet, nombre, apellido, carrera, email, telefono, fecha_registro
        FROM alumno
        WHERE carnet = %s;
        """,
        (carnet,),
    )
    alumno = cur.fetchone()
    cur.close()
    conn.close()
    return alumno


def modificar_alumno():
    print("\n--- Modificar alumno ---")
    carnet = leer_texto("Carnet del alumno a modificar: ", obligatorio=True, maximo=15)
    alumno = buscar_por_carnet(carnet)

    if not alumno:
        print("No se encontro un alumno con ese carnet.")
        return

    print("Deja un campo vacio para conservar el valor actual.")
    nombre = leer_texto(f"Nombre [{alumno[2]}]: ", maximo=100) or alumno[2]
    apellido = leer_texto(f"Apellido [{alumno[3]}]: ", maximo=100) or alumno[3]
    carrera = leer_texto(f"Carrera [{alumno[4] or ''}]: ", maximo=150) or alumno[4]
    email = leer_texto(f"Email [{alumno[5] or ''}]: ", maximo=150) or alumno[5]
    telefono = leer_texto(f"Telefono [{alumno[6] or ''}]: ", maximo=20) or alumno[6]

    conn = None
    cur = None
    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE alumno
            SET nombre = %s,
                apellido = %s,
                carrera = %s,
                email = %s,
                telefono = %s
            WHERE carnet = %s;
            """,
            (nombre, apellido, carrera, email, telefono, carnet),
        )
        conn.commit()
        print("Alumno modificado correctamente.")
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        print(f"Error al modificar alumno: {e}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def listar_alumnos():
    print("\n--- Listado de alumnos ---")
    conn = conectar()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, carnet, nombre, apellido, carrera, email, telefono, fecha_registro
        FROM alumno
        ORDER BY id;
        """
    )
    alumnos = cur.fetchall()
    cur.close()
    conn.close()

    if not alumnos:
        print("No hay alumnos registrados.")
        return

    print("-" * 120)
    print(
        f"{'ID':<4} {'Carnet':<15} {'Nombre':<18} {'Apellido':<18} "
        f"{'Carrera':<20} {'Email':<25} {'Telefono':<12} {'Fecha'}"
    )
    print("-" * 120)
    for a in alumnos:
        print(
            f"{a[0]:<4} {a[1]:<15} {a[2]:<18} {a[3]:<18} "
            f"{(a[4] or ''):<20} {(a[5] or ''):<25} {(a[6] or ''):<12} {a[7]}"
        )
    print("-" * 120)


def eliminar_alumno():
    print("\n--- Eliminar alumno ---")
    carnet = leer_texto("Carnet del alumno a eliminar: ", obligatorio=True, maximo=15)
    alumno = buscar_por_carnet(carnet)

    if not alumno:
        print("No se encontro un alumno con ese carnet.")
        return

    confirmar = input(f"Seguro que deseas eliminar a {alumno[2]} {alumno[3]}? (s/n): ")
    if confirmar.strip().lower() != "s":
        print("Eliminacion cancelada.")
        return

    conn = None
    cur = None
    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute("DELETE FROM alumno WHERE carnet = %s;", (carnet,))
        conn.commit()
        print("Alumno eliminado correctamente.")
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        print(f"Error al eliminar alumno: {e}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def mostrar_menu():
    print("\n===== CRUD ALUMNOS - POSTGRESQL =====")
    print("1. Agregar alumno")
    print("2. Modificar datos de un alumno")
    print("3. Listar todos los alumnos")
    print("4. Eliminar alumno")
    print("5. Salir")


def main():
    crear_base_datos()
    crear_tabla()

    while True:
        mostrar_menu()
        opcion = input("Elige una opcion: ").strip()

        if opcion == "1":
            agregar_alumno()
        elif opcion == "2":
            modificar_alumno()
        elif opcion == "3":
            listar_alumnos()
        elif opcion == "4":
            eliminar_alumno()
        elif opcion == "5":
            print("Programa finalizado.")
            break
        else:
            print("Opcion invalida. Intenta de nuevo.")


if __name__ == "__main__":
    main()
