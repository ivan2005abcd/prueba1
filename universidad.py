import streamlit as st
import mysql.connector
from datetime import date, time
import datetime # <-- Añade esta línea
import bcrypt # Importar la librería bcrypt


st.set_page_config(page_title="Sistema de Asesorías - USB", page_icon="🎓", layout="centered")

st.markdown("""
    <style>
        body {
            background-color: #ffffff;
            color: #004d00;
        }
        .titulo-usb {
            background-color: #004d00;
            color: white;
            padding: 1rem;
            border-radius: 0.5rem;
            text-align: center;
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 1rem;
        }
        .stButton > button {
            background-color: #004d00;
            color: white;
        }
        .stButton > button:hover {
            background-color: #007300;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="titulo-usb">UNIVERSIDAD SIMÓN BOLÍVAR</div>', unsafe_allow_html=True)

# --- 1. Configuración de la Conexión a la Base de Datos ---
@st.cache_resource
def get_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="021005Valiva02", # ¡Asegúrate de que esta sea tu contraseña real!
            database="probandopython2"
        )
        return conn
    except mysql.connector.Error as err:
        st.error(f"Error al conectar a la base de datos: {err}")
        st.stop() # Detiene la ejecución si no hay conexión

conn = get_connection()
cursor = conn.cursor(dictionary=True)

# --- 2. Funciones de Autenticación (se quedan al principio) ---

def hash_password(password):
    """Genera un hash seguro de la contraseña usando bcrypt."""
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def check_password(plain_password, hashed_password):
    """Verifica si una contraseña en texto plano coincide con un hash."""
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except ValueError:
        return False

def get_monitor_info(id_estudiante):
    """Obtiene la información del monitor y su carrera."""
    try:
        cursor.execute("""
            SELECT e.id_estudiante, e.nombre, e.apellido, c.nombre_carrera
            FROM Estudiante e
            JOIN Carrera c ON e.id_carrera = c.id_carrera
            JOIN Monitor m ON e.id_estudiante = m.id_estudiante
            WHERE e.id_estudiante = %s
        """, (id_estudiante,))
        return cursor.fetchone()
    except mysql.connector.Error as err:
        st.error(f"Error al buscar información del monitor: {err}")
        return None

def get_user_password_hash(username):
    """Obtiene el hash de la contraseña de la tabla usuarios."""
    try:
        cursor.execute("SELECT contraseña FROM usuarios WHERE usuario = %s", (username,))
        result = cursor.fetchone()
        return result['contraseña'] if result else None
    except mysql.connector.Error as err:
        st.error(f"Error al buscar el hash de la contraseña: {err}")
        return None

def set_user_password(username, plain_password):
    """Inserta o actualiza el hash de la contraseña para un usuario."""
    hashed_pwd = hash_password(plain_password)
    try:
        cursor.execute("INSERT INTO usuarios (usuario, contraseña) VALUES (%s, %s)", (username, hashed_pwd))
        conn.commit()
        st.success("Contraseña creada correctamente. Ya puedes iniciar sesión.")
    except mysql.connector.IntegrityError:
        conn.rollback()
        cursor.execute("UPDATE usuarios SET contraseña = %s WHERE usuario = %s", (hashed_pwd, username))
        conn.commit()
        st.success("Contraseña actualizada correctamente. Ya puedes iniciar sesión.")
    except mysql.connector.Error as err:
        st.error(f"Error al guardar la contraseña: {err}")
        conn.rollback()

# --- 3. Inicialización del Estado de Sesión ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'monitor_id' not in st.session_state:
    st.session_state.monitor_id = None
if 'monitor_info' not in st.session_state:
    st.session_state.monitor_info = None

# --- 4. Bloque de Lógica de Login (LO PRIMERO QUE SE EJECUTA VISIBLEMENTE) ---
st.sidebar.title("Navegación")

if not st.session_state.logged_in:
    st.header("Inicio de Sesión para Monitores")
    login_id = st.text_input("Código de Estudiante (ID de Monitor)")
    login_password = st.text_input("Contraseña", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Iniciar Sesión"):
            if not login_id or not login_password:
                st.warning("Por favor, ingrese su código y contraseña.")
            else:
                monitor_info = get_monitor_info(login_id)
                if monitor_info:
                    st.session_state.monitor_info = monitor_info

                    stored_hash = get_user_password_hash(login_id)

                    if stored_hash:
                        if check_password(login_password, stored_hash):
                            st.session_state.logged_in = True
                            st.session_state.monitor_id = login_id
                            st.rerun() # ¡Importante para recargar y mostrar la app principal!
                        else:
                            st.error("Contraseña incorrecta.")
                    else:
                        st.warning("Parece que es tu primer inicio de sesión o no tienes contraseña registrada.")
                        st.info("Por favor, crea una nueva contraseña abajo.")
                else:
                    st.error("Código de estudiante no encontrado o no está registrado como monitor.")

    with col2:
        # Usaremos una variable de estado para controlar la visibilidad de los campos de nueva contraseña
        if 'show_password_fields' not in st.session_state:
            st.session_state.show_password_fields = False
        if 'temp_login_id_for_password' not in st.session_state:
            st.session_state.temp_login_id_for_password = None


        if st.button("Crear/Restablecer Contraseña"):
            if not login_id:
                st.warning("Por favor, ingresa tu Código de Estudiante para crear/restablecer la contraseña.")
                st.session_state.show_password_fields = False # Asegurar que no se muestren
            else:
                monitor_info = get_monitor_info(login_id)
                if monitor_info:
                    st.session_state.monitor_info = monitor_info
                    st.session_state.show_password_fields = True # Mostrar los campos de contraseña
                    st.session_state.temp_login_id_for_password = login_id # Guardar ID temporalmente
                    st.rerun() # Re-ejecutar para mostrar los campos
                else:
                    st.error("Código de estudiante no encontrado o no está registrado como monitor.")
                    st.session_state.show_password_fields = False

        # Solo mostrar los campos de nueva contraseña si la variable de estado es True
        if st.session_state.show_password_fields and st.session_state.temp_login_id_for_password == login_id:
            st.info(f"Vas a crear/restablecer la contraseña para el monitor con ID: {st.session_state.temp_login_id_for_password}")
            new_password = st.text_input("Nueva Contraseña", type="password", key="new_pwd")
            confirm_password = st.text_input("Confirmar Contraseña", type="password", key="confirm_pwd")

            if st.button("Guardar Nueva Contraseña", key="save_new_pwd_btn"): # Nuevo botón para guardar
                if new_password and confirm_password:
                    if new_password == confirm_password:
                        set_user_password(st.session_state.temp_login_id_for_password, new_password)
                        st.session_state.show_password_fields = False # Ocultar campos después de guardar
                        st.session_state.temp_login_id_for_password = None
                        st.rerun() # Opcional: Re-ejecutar para limpiar la interfaz
                    else:
                        st.error("Las contraseñas no coinciden.")
                else:
                    st.warning("Por favor, ingresa y confirma tu nueva contraseña.")

    # Detener la ejecución si no está logueado para no mostrar el resto de la app
    st.stop()

# --- 5. Bloque de la Aplicación Principal (solo se ejecuta si st.session_state.logged_in es True) ---
# Este es el código que ya tienes para el registro de asesorías.
# Puedes pegarlo aquí, después del 'st.stop()'
# ----------------------------------------------------------------------
# (Aquí comienza tu código para el registro de asesorías)
# ----------------------------------------------------------------------


st.sidebar.success(f"Sesión iniciada como: {st.session_state.monitor_info['nombre']} {st.session_state.monitor_info['apellido']}")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.logged_in = False
    st.session_state.monitor_id = None
    st.session_state.monitor_info = None
    st.rerun()
opcion = st.sidebar.radio("Seleccione una opción", ["Registrar", "Actualizar", "Horas de monitor", "Eliminar asesoría"])
# --- Créditos en la barra lateral (pequeños) ---
st.sidebar.markdown("---") # Opcional: una línea para separar
st.sidebar.caption("Desarrollado por:")
st.sidebar.caption("IVAN CONTRERAS")
st.sidebar.caption("JULIANA SANMIGUEL")
st.sidebar.caption("TAYLIN RINCON")

if opcion == "Registrar":
    st.title("Registro de Asesorías")

    # Paso 1: Ingresar código del estudiante que recibirá la asesoría
    codigo_estudiante_recibe = st.text_input("Ingrese el código del estudiante que recibirá la asesoría")

    if codigo_estudiante_recibe:
        # Buscar datos del estudiante que recibe la asesoría
        try:
            cursor.execute("""
                SELECT e.id_estudiante, e.nombre, e.apellido, c.nombre_carrera
                FROM Estudiante e
                JOIN Carrera c ON e.id_carrera = c.id_carrera
                WHERE e.id_estudiante = %s
            """, (codigo_estudiante_recibe,))
            estudiante_recibe = cursor.fetchone()
        except mysql.connector.Error as err:
            st.error(f"Error al buscar estudiante: {err}")
            estudiante_recibe = None

        if estudiante_recibe:
            st.success("Estudiante que recibe la asesoría encontrado:")
            st.write(f"**Nombre:** {estudiante_recibe['nombre']} {estudiante_recibe['apellido']}")
            st.write(f"**Carrera:** {estudiante_recibe['nombre_carrera']}")

            st.subheader("Datos de la Asesoría")

            # Paso 2: Seleccionar el Monitor
            cursor.execute("""
                SELECT m.id_monitor, e.nombre, e.apellido
                FROM Monitor m
                JOIN Estudiante e ON m.id_estudiante = e.id_estudiante
            """)
            monitores_db = cursor.fetchall()
            monitor_opciones = {f"{m['nombre']} {m['apellido']}": m['id_monitor'] for m in monitores_db}
            monitor_seleccionado_nombre = st.selectbox("Seleccione el Monitor", list(monitor_opciones.keys()))
            id_monitor_seleccionado = monitor_opciones.get(monitor_seleccionado_nombre)

            if id_monitor_seleccionado:
                # Paso 3: Seleccionar el Curso
                cursor.execute("""
                    SELECT DISTINCT c.id_curso, c.nombre_curso
                    FROM Monitor_Curso mc
                    JOIN Curso c ON mc.id_curso = c.id_curso
                    WHERE mc.id_monitor = %s
                """, (id_monitor_seleccionado,))
                cursos_monitor_db = cursor.fetchall()

                if cursos_monitor_db:
                    curso_opciones = {c['nombre_curso']: c['id_curso'] for c in cursos_monitor_db}
                    curso_seleccionado_nombre = st.selectbox("Seleccione el Curso", list(curso_opciones.keys()))
                    id_curso_seleccionado = curso_opciones.get(curso_seleccionado_nombre)
                else:
                    st.warning("El monitor seleccionado no tiene cursos asignados.")
                    id_curso_seleccionado = None

                if id_curso_seleccionado:
                    # Paso 4: Seleccionar el Lugar
                    cursor.execute("""
                        SELECT DISTINCT nombre_lugar
                        FROM Monitor_Curso
                        WHERE id_monitor = %s AND id_curso = %s
                    """, (id_monitor_seleccionado, id_curso_seleccionado))
                    lugares_monitor_curso_db = cursor.fetchall()

                    if lugares_monitor_curso_db:
                        lugar_opciones = [l['nombre_lugar'] for l in lugares_monitor_curso_db]
                        nombre_lugar_seleccionado = st.selectbox("Seleccione el Lugar", lugar_opciones)
                    else:
                        st.warning("No hay lugares definidos para este curso con el monitor seleccionado.")
                        nombre_lugar_seleccionado = None

                    if nombre_lugar_seleccionado:
                        # Obtener id_monitor_curso
                        cursor.execute("""
                            SELECT id_monitor_curso
                            FROM Monitor_Curso
                            WHERE id_monitor = %s AND id_curso = %s AND nombre_lugar = %s
                        """, (id_monitor_seleccionado, id_curso_seleccionado, nombre_lugar_seleccionado))
                        monitor_curso_row = cursor.fetchone()

                        if monitor_curso_row:
                            id_monitor_curso_seleccionado = monitor_curso_row['id_monitor_curso']
                        else:
                            st.error("No se pudo encontrar la combinación Monitor-Curso-Lugar.")
                            id_monitor_curso_seleccionado = None

                        if id_monitor_curso_seleccionado:
                            # Modalidad
                            cursor.execute("SELECT id_modalidad, tipo_modalidad FROM Modalidad")
                            modalidades = cursor.fetchall()
                            modalidad_opciones = {m['tipo_modalidad']: m['id_modalidad'] for m in modalidades}
                            modalidad = st.selectbox("Modalidad", list(modalidad_opciones.keys()))

                            # Sede
                            cursor.execute("SELECT id_sede, nombre_sede FROM Sede")
                            sedes = cursor.fetchall()
                            sede_opciones = {s['nombre_sede']: s['id_sede'] for s in sedes}
                            sede = st.selectbox("Sede", list(sede_opciones.keys()))

                            # Periodo
                            cursor.execute("SELECT id_periodo, nombre_periodo FROM Periodo")
                            periodos = cursor.fetchall()
                            periodo_opciones = {p['nombre_periodo']: p['id_periodo'] for p in periodos}
                            periodo = st.selectbox("Periodo", list(periodo_opciones.keys()))

                            # Fecha y hora
                            fecha = st.date_input("Fecha de la asesoría", value=date.today())
                            hora_inicio = st.time_input("Hora de inicio")
                            hora_fin = st.time_input("Hora de fin")

                            if st.button("Registrar asesoría"):
                                try:
                                    cursor.execute("""
                                        INSERT INTO Asesoria
                                        (id_monitor_curso, id_modalidad, id_sede, id_periodo, fecha, hora_inicio, hora_fin)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                                    """, (
                                        id_monitor_curso_seleccionado,
                                        modalidad_opciones[modalidad],
                                        sede_opciones[sede],
                                        periodo_opciones[periodo],
                                        fecha,
                                        hora_inicio,
                                        hora_fin
                                    ))
                                    conn.commit()

                                    id_asesoria = cursor.lastrowid

                                    cursor.execute("""
                                        INSERT INTO Asesoria_Estudiante (id_asesoria, id_estudiante)
                                        VALUES (%s, %s)
                                    """, (id_asesoria, estudiante_recibe['id_estudiante']))
                                    conn.commit()

                                    st.success("Asesoría registrada correctamente.")
                                except mysql.connector.Error as err:
                                    st.error(f"Error al registrar asesoría: {err}")
                                    conn.rollback()
                        else:
                            st.warning("Seleccione una combinación válida de monitor, curso y lugar.")
                    else:
                        st.warning("Por favor, seleccione un lugar para la asesoría.")
                else:
                    st.warning("Por favor, seleccione un curso para la asesoría.")
            else:
                st.warning("Por favor, seleccione un monitor.")
        else:
            st.error("Estudiante no encontrado.")

elif opcion == "Actualizar":
    st.title("Actualizar Asesoría")

    codigo_estudiante = st.text_input("Ingrese el código del estudiante que recibió la asesoría")

    if codigo_estudiante:
        try:
            cursor.execute("""
                SELECT e.id_estudiante, e.nombre, e.apellido
                FROM Estudiante e
                WHERE e.id_estudiante = %s
            """, (codigo_estudiante,))
            estudiante = cursor.fetchone()
        except mysql.connector.Error as err:
            st.error(f"Error al buscar estudiante: {err}")
            estudiante = None

        if estudiante:
            st.success(f"Estudiante encontrado: {estudiante['nombre']} {estudiante['apellido']}")

            cursor.execute("""
                SELECT a.id_asesoria, a.fecha, c.nombre_curso, mc.nombre_lugar, a.id_modalidad, a.id_sede, a.id_periodo
                FROM Asesoria_Estudiante ae
                JOIN Asesoria a ON ae.id_asesoria = a.id_asesoria
                JOIN Monitor_Curso mc ON a.id_monitor_curso = mc.id_monitor_curso
                JOIN Curso c ON mc.id_curso = c.id_curso
                WHERE ae.id_estudiante = %s
            """, (estudiante['id_estudiante'],))
            asesorias = cursor.fetchall()

            if asesorias:
                asesoria_opciones = {
                    f"{a['id_asesoria']} - {a['fecha']} - {a['nombre_curso']} ({a['nombre_lugar']})": a['id_asesoria']
                    for a in asesorias
                }
                seleccion = st.selectbox("Seleccione la asesoría a actualizar", list(asesoria_opciones.keys()))
                id_asesoria = asesoria_opciones[seleccion]

                # Aquí seleccionamos los 4 campos que quieres actualizar
                cursor.execute("""
                    SELECT a.id_modalidad, mc.nombre_lugar, a.id_sede, a.id_periodo, a.id_monitor_curso
                    FROM Asesoria a
                    JOIN Monitor_Curso mc ON a.id_monitor_curso = mc.id_monitor_curso
                    WHERE a.id_asesoria = %s
                """, (id_asesoria,))
                asesoria_datos = cursor.fetchone()

                if asesoria_datos:
                    # 1. Modalidad
                    cursor.execute("SELECT id_modalidad, tipo_modalidad FROM Modalidad")
                    modalidades = cursor.fetchall()
                    modalidad_opciones = {m['tipo_modalidad']: m['id_modalidad'] for m in modalidades}
                    modalidad_nombre_actual = next((k for k, v in modalidad_opciones.items() if v == asesoria_datos['id_modalidad']), None)
                    nueva_modalidad = st.selectbox("Modalidad", list(modalidad_opciones.keys()),
                                                    index=list(modalidad_opciones.keys()).index(modalidad_nombre_actual))

                    # 2. Lugar (nombre_lugar en Monitor_Curso)
                    lugar_actual = asesoria_datos['nombre_lugar']
                    
                    # Obtener opciones de lugar de Monitor_Curso (solo lugares asociados a ese monitor/curso si fuera posible)
                    # Para simplificar y dar opciones válidas, obtenemos todos los nombres de lugar distintos de Monitor_Curso
                    cursor.execute("SELECT DISTINCT nombre_lugar FROM Monitor_Curso")
                    lugares_db = cursor.fetchall()
                    lugar_opciones_nombres = [l['nombre_lugar'] for l in lugares_db]

                    if lugar_actual not in lugar_opciones_nombres:
                        lugar_opciones_nombres.append(lugar_actual)
                        lugar_opciones_nombres.sort()

                    nuevo_lugar = st.selectbox("Lugar", lugar_opciones_nombres,
                                                index=lugar_opciones_nombres.index(lugar_actual))
                    
                    # 3. Sede
                    cursor.execute("SELECT id_sede, nombre_sede FROM Sede")
                    sedes = cursor.fetchall()
                    sede_opciones = {s['nombre_sede']: s['id_sede'] for s in sedes}
                    sede_nombre_actual = next((k for k, v in sede_opciones.items() if v == asesoria_datos['id_sede']), None)
                    nueva_sede = st.selectbox("Sede", list(sede_opciones.keys()),
                                                index=list(sede_opciones.keys()).index(sede_nombre_actual))

                    # 4. Periodo
                    cursor.execute("SELECT id_periodo, nombre_periodo FROM Periodo")
                    periodos = cursor.fetchall()
                    periodo_opciones = {p['nombre_periodo']: p['id_periodo'] for p in periodos}
                    periodo_nombre_actual = next((k for k, v in periodo_opciones.items() if v == asesoria_datos['id_periodo']), None)
                    nuevo_periodo = st.selectbox("Periodo", list(periodo_opciones.keys()),
                                                  index=list(periodo_opciones.keys()).index(periodo_nombre_actual))


                    if st.button("Actualizar asesoría"):
                        try:
                            # El id_monitor_curso actual de la asesoría
                            monitor_curso_id_to_update = asesoria_datos['id_monitor_curso']

                            # Actualizar el nombre_lugar en Monitor_Curso
                            # Necesitamos encontrar el id_monitor_curso que corresponde al nuevo lugar
                            # Esto es un poco más complejo si la combinación monitor-curso-lugar es única
                            # Asumimos que queremos actualizar el nombre_lugar para el id_monitor_curso actual
                            cursor.execute("""
                                UPDATE Monitor_Curso
                                SET nombre_lugar = %s
                                WHERE id_monitor_curso = %s
                            """, (nuevo_lugar, monitor_curso_id_to_update))

                            # Actualizar Modalidad, Sede, Periodo en Asesoria
                            cursor.execute("""
                                UPDATE Asesoria
                                SET id_modalidad = %s,
                                    id_sede = %s,
                                    id_periodo = %s
                                WHERE id_asesoria = %s
                            """, (
                                modalidad_opciones[nueva_modalidad],
                                sede_opciones[nueva_sede],
                                periodo_opciones[nuevo_periodo],
                                id_asesoria
                            ))

                            conn.commit()
                            st.success("Asesoría actualizada correctamente.")
                        except mysql.connector.Error as err:
                            st.error(f"Error al actualizar asesoría: {err}")
                            conn.rollback()
                else:
                    st.warning("No se encontraron los datos de la asesoría seleccionada.")
            else:
                st.warning("No se encontraron asesorías para este estudiante.")
        else:
            st.error("Estudiante no encontrado.")

elif opcion == "Horas de monitor":
    st.title("Mis horas de Monitoría")

    # Obtener ID del monitor a partir del ID del estudiante logueado
    cursor.execute("SELECT id_monitor FROM Monitor WHERE id_estudiante = %s", (st.session_state.monitor_id,))
    resultado = cursor.fetchone()

    if resultado:
        id_monitor = resultado['id_monitor']

        # Consulta de horas acumuladas y estado
        cursor.execute("""
            SELECT SUM(TIME_TO_SEC(a.hora_fin) - TIME_TO_SEC(a.hora_inicio)) AS total_segundos
            FROM Asesoria a
            JOIN Monitor_Curso mc ON a.id_monitor_curso = mc.id_monitor_curso
            WHERE mc.id_monitor = %s
        """, (id_monitor,))
        resultado = cursor.fetchone()

        if resultado and resultado['total_segundos']:
            total_segundos = resultado['total_segundos']
            total_horas = round(total_segundos / 3600, 2)
            horas_restantes = max(0, round(52 - total_horas, 2))

            st.subheader(f"✅ Horas acumuladas: {total_horas} horas")
            st.subheader(f"🕒 Horas restantes para completar las 52: {horas_restantes} horas")

            if total_horas >= 52:
                st.success("🎉 ¡Felicidades! Ya cumpliste las 52 horas requeridas como monitor.")
            else:
                st.info("💪 Sigue adelante, ¡cada hora cuenta para tu crecimiento!")
        else:
            st.info("No tienes asesorías registradas aún.")
    else:
        st.error("No se pudo encontrar tu información como monitor.")

elif opcion == "Eliminar asesoría":
    st.title("Eliminar Asesoría")

    CLAVE_ADMIN = "admin123"  # Puedes ponerla más segura o sacarla de la BD

    # Obtener ID del monitor
    cursor.execute("SELECT id_monitor FROM Monitor WHERE id_estudiante = %s", (st.session_state.monitor_id,))
    resultado = cursor.fetchone()

    if resultado:
        id_monitor = resultado['id_monitor']

        # Obtener asesorías del monitor
        cursor.execute("""
            SELECT a.id_asesoria, a.fecha, a.hora_inicio, a.hora_fin, c.nombre_curso, mc.nombre_lugar
            FROM Asesoria a
            JOIN Monitor_Curso mc ON a.id_monitor_curso = mc.id_monitor_curso
            JOIN Curso c ON mc.id_curso = c.id_curso
            WHERE mc.id_monitor = %s
            ORDER BY a.fecha DESC
        """, (id_monitor,))
        asesorias = cursor.fetchall()

        if asesorias:
            opciones = {
                f"{a['fecha']} | {a['hora_inicio']} - {a['hora_fin']} | {a['nombre_curso']} ({a['nombre_lugar']})": a['id_asesoria']
                for a in asesorias
            }
            seleccion = st.selectbox("Seleccione la asesoría a eliminar", list(opciones.keys()))
            id_asesoria = opciones[seleccion]

            clave_ingresada = st.text_input("Código de autorización del administrador", type="password")

            if st.button("Eliminar asesoría"):
                if clave_ingresada == CLAVE_ADMIN:
                    try:
                        # Eliminar primero el vínculo con el estudiante
                        cursor.execute("DELETE FROM Asesoria_Estudiante WHERE id_asesoria = %s", (id_asesoria,))
                        # Luego eliminar la asesoría
                        cursor.execute("DELETE FROM Asesoria WHERE id_asesoria = %s", (id_asesoria,))
                        conn.commit()
                        st.success("✅ Asesoría eliminada correctamente.")
                        st.rerun()
                    except mysql.connector.Error as err:
                        conn.rollback()
                        st.error(f"Error al eliminar asesoría: {err}")
                else:
                    st.error("❌ Código de autorización incorrecto.")
        else:
            st.info("No hay asesorías registradas para eliminar.")
    else:
        st.error("No se pudo identificar al monitor actual.")

