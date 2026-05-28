
## Base de datos

El programa intenta crear automaticamente la base de datos `tarea1` al iniciar. Si tu usuario de PostgreSQL no tiene permisos para crear bases de datos, puedes crearla manualmente:

```sql
CREATE DATABASE tarea1;
```

La tabla `alumno` se crea automaticamente si no existe:

```sql
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
```

## Configuracion de conexion

Por defecto usa:

- Host: `localhost`
- Puerto: `5432`
- Usuario: `postgres`
- Base de datos: `tarea1`

Puedes cambiar los datos con variables de entorno:

```bash
set PGHOST=localhost
set PGPORT=5432
set PGUSER=postgres
set PGPASSWORD=tu_password
set PGDATABASE=tarea1
```

En PowerShell:

```powershell
$env:PGHOST="localhost"
$env:PGPORT="5432"
$env:PGUSER="postgres"
$env:PGPASSWORD="tu_password"
$env:PGDATABASE="tarea1"
```

## Ejecutar

```bash
python main.py
```

## Operaciones del menu

1. Agregar alumno
2. Modificar datos de un alumno buscando por carnet
3. Listar todos los alumnos
4. Eliminar alumno por carnet
5. Salir
