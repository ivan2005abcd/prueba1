DROP DATABASE IF EXISTS probandopython2;
CREATE DATABASE probandopython2;
USE probandopython2;

CREATE TABLE Carrera (
    id_carrera INT AUTO_INCREMENT PRIMARY KEY,
    nombre_carrera VARCHAR(100) NOT NULL
);

CREATE TABLE Estudiante (
    id_estudiante BIGINT PRIMARY KEY,  -- aquí pongo BIGINT para códigos largos
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    id_carrera INT NOT NULL,
    FOREIGN KEY (id_carrera) REFERENCES Carrera(id_carrera)
);

CREATE TABLE Sede (
    id_sede INT AUTO_INCREMENT PRIMARY KEY,
    nombre_sede VARCHAR(100) NOT NULL
);

CREATE TABLE Periodo (
    id_periodo INT AUTO_INCREMENT PRIMARY KEY,
    nombre_periodo VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE Monitor (
    id_monitor INT AUTO_INCREMENT PRIMARY KEY,
    id_estudiante BIGINT NOT NULL,
    FOREIGN KEY (id_estudiante) REFERENCES Estudiante(id_estudiante)
);

CREATE TABLE Curso (
    id_curso INT AUTO_INCREMENT PRIMARY KEY,
    nombre_curso VARCHAR(100) NOT NULL
);

CREATE TABLE Monitor_Curso (
    id_monitor_curso INT AUTO_INCREMENT PRIMARY KEY,
    id_monitor INT NOT NULL,
    id_curso INT NOT NULL,
    nombre_lugar VARCHAR(100) NOT NULL,
    FOREIGN KEY (id_monitor) REFERENCES Monitor(id_monitor),
    FOREIGN KEY (id_curso) REFERENCES Curso(id_curso)
);

CREATE TABLE Modalidad (
    id_modalidad INT AUTO_INCREMENT PRIMARY KEY,
    tipo_modalidad VARCHAR(50) NOT NULL
);

CREATE TABLE Asesoria (
    id_asesoria INT AUTO_INCREMENT PRIMARY KEY,
    id_monitor_curso INT NOT NULL,
    id_modalidad INT NOT NULL,
    id_sede INT NOT NULL,
    id_periodo INT NOT NULL,
    fecha DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    FOREIGN KEY (id_monitor_curso) REFERENCES Monitor_Curso(id_monitor_curso),
    FOREIGN KEY (id_modalidad) REFERENCES Modalidad(id_modalidad),
    FOREIGN KEY (id_sede) REFERENCES Sede(id_sede),
    FOREIGN KEY (id_periodo) REFERENCES Periodo(id_periodo)
);

CREATE TABLE Asesoria_Estudiante (
    id_asesoria INT NOT NULL,
    id_estudiante BIGINT NOT NULL,
    PRIMARY KEY (id_asesoria, id_estudiante),
    FOREIGN KEY (id_asesoria) REFERENCES Asesoria(id_asesoria),
    FOREIGN KEY (id_estudiante) REFERENCES Estudiante(id_estudiante)
);

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(50) NOT NULL UNIQUE,
    contraseña VARCHAR(255) NOT NULL
);



-- Desactivar temporalmente las comprobaciones de claves foráneas para facilitar la inserción
SET FOREIGN_KEY_CHECKS = 0;

-- Seleccionar la base de datos
USE probandopython2;

-- 1. Insertar datos en la tabla Carrera
INSERT INTO Carrera (nombre_carrera) VALUES
('Sistemas'),
('Industrial'),
('Multimedia');

-- 2. Insertar datos en la tabla Estudiante
-- Los IDs de carrera se obtienen de la tabla Carrera
INSERT INTO Estudiante (id_estudiante, nombre, apellido, id_carrera) VALUES
(202313226590, 'Ivan', 'Contreras', (SELECT id_carrera FROM Carrera WHERE nombre_carrera = 'Sistemas')),
(201929820635, 'Juliana', 'Sanmiguel', (SELECT id_carrera FROM Carrera WHERE nombre_carrera = 'Industrial')),
(202313226093, 'Taylin', 'Rincon', (SELECT id_carrera FROM Carrera WHERE nombre_carrera = 'Multimedia')),
(202400000001, 'Julian', 'Mantilla', (SELECT id_carrera FROM Carrera WHERE nombre_carrera = 'Sistemas')), -- Monitor
(202400000002, 'Cristian', 'Perez', (SELECT id_carrera FROM Carrera WHERE nombre_carrera = 'Sistemas')),   -- Monitor
(202400000003, 'Sneider', 'Rojas', (SELECT id_carrera FROM Carrera WHERE nombre_carrera = 'Sistemas'));    -- Monitor

-- 3. Insertar datos en la tabla Sede
INSERT INTO Sede (nombre_sede) VALUES
('Sede1'),
('Sede2'),
('Sede3'),
('Sede4');

-- 4. Insertar datos en la tabla Periodo
INSERT INTO Periodo (nombre_periodo) VALUES
('2024-2'),
('2025-1'),
('2025-2');

-- 5. Insertar datos en la tabla Monitor
-- Los IDs de estudiante se obtienen de la tabla Estudiante para los monitores
INSERT INTO Monitor (id_estudiante) VALUES
((SELECT id_estudiante FROM Estudiante WHERE nombre = 'Julian' AND apellido = 'Mantilla')),
((SELECT id_estudiante FROM Estudiante WHERE nombre = 'Cristian' AND apellido = 'Perez')),
((SELECT id_estudiante FROM Estudiante WHERE nombre = 'Sneider' AND apellido = 'Rojas'));

-- 6. Insertar datos en la tabla Curso
INSERT INTO Curso (nombre_curso) VALUES
('POO'),
('Calculo Diferencial'),
('Programacion Web'),
('Bases de Datos');

-- 7. Insertar datos en la tabla Modalidad
INSERT INTO Modalidad (tipo_modalidad) VALUES
('Virtual'),
('Presencial');

-- 8. Insertar datos en la tabla Monitor_Curso
-- Se asocian monitores con cursos y se define el lugar de la asesoría
INSERT INTO Monitor_Curso (id_monitor, id_curso, nombre_lugar) VALUES
((SELECT id_monitor FROM Monitor WHERE id_estudiante = (SELECT id_estudiante FROM Estudiante WHERE nombre = 'Julian' AND apellido = 'Mantilla')), (SELECT id_curso FROM Curso WHERE nombre_curso = 'POO'), 'Biblioteca'),
((SELECT id_monitor FROM Monitor WHERE id_estudiante = (SELECT id_estudiante FROM Estudiante WHERE nombre = 'Cristian' AND apellido = 'Perez')), (SELECT id_curso FROM Curso WHERE nombre_curso = 'Calculo Diferencial'), 'Salon de Computo'),
((SELECT id_monitor FROM Monitor WHERE id_estudiante = (SELECT id_estudiante FROM Estudiante WHERE nombre = 'Sneider' AND apellido = 'Rojas')), (SELECT id_curso FROM Curso WHERE nombre_curso = 'Programacion Web'), 'Salon X'),
((SELECT id_monitor FROM Monitor WHERE id_estudiante = (SELECT id_estudiante FROM Estudiante WHERE nombre = 'Julian' AND apellido = 'Mantilla')), (SELECT id_curso FROM Curso WHERE nombre_curso = 'Bases de Datos'), 'Salon de Computo');

-- 9. Insertar datos en la tabla Asesoria
-- Se crean algunas asesorías de ejemplo
INSERT INTO Asesoria (id_monitor_curso, id_modalidad, id_sede, id_periodo, fecha, hora_inicio, hora_fin) VALUES
(1, (SELECT id_modalidad FROM Modalidad WHERE tipo_modalidad = 'Presencial'), (SELECT id_sede FROM Sede WHERE nombre_sede = 'Sede1'), (SELECT id_periodo FROM Periodo WHERE nombre_periodo = '2024-2'), '2024-11-15', '10:00:00', '11:00:00'),
(2, (SELECT id_modalidad FROM Modalidad WHERE tipo_modalidad = 'Virtual'), (SELECT id_sede FROM Sede WHERE nombre_sede = 'Sede2'), (SELECT id_periodo FROM Periodo WHERE nombre_periodo = '2025-1'), '2025-02-20', '14:00:00', '15:30:00'),
(3, (SELECT id_modalidad FROM Modalidad WHERE tipo_modalidad = 'Presencial'), (SELECT id_sede FROM Sede WHERE nombre_sede = 'Sede3'), (SELECT id_periodo FROM Periodo WHERE nombre_periodo = '2025-2'), '2025-08-01', '09:00:00', '10:00:00'),
(4, (SELECT id_modalidad FROM Modalidad WHERE tipo_modalidad = 'Virtual'), (SELECT id_sede FROM Sede WHERE nombre_sede = 'Sede4'), (SELECT id_periodo FROM Periodo WHERE nombre_periodo = '2024-2'), '2024-12-01', '16:00:00', '17:00:00');

-- 10. Insertar datos en la tabla Asesoria_Estudiante
-- Se asocian estudiantes a las asesorías
INSERT INTO Asesoria_Estudiante (id_asesoria, id_estudiante) VALUES
(1, (SELECT id_estudiante FROM Estudiante WHERE nombre = 'Ivan' AND apellido = 'Contreras')),
(1, (SELECT id_estudiante FROM Estudiante WHERE nombre = 'Juliana' AND apellido = 'Sanmiguel')),
(2, (SELECT id_estudiante FROM Estudiante WHERE nombre = 'Taylin' AND apellido = 'Rincon')),
(3, (SELECT id_estudiante FROM Estudiante WHERE nombre = 'Ivan' AND apellido = 'Contreras'));

-- Reactivar las comprobaciones de claves foráneas
SET FOREIGN_KEY_CHECKS = 1;





-- Insertar asociaciones adicionales de Monitor-Curso-Lugar

-- Julian Mantilla (Monitor para POO)
-- Ya tenía 'Biblioteca'. Agregamos 'Salón de Computo' y 'Salón X'.
INSERT INTO Monitor_Curso (id_monitor, id_curso, nombre_lugar) VALUES
((SELECT id_monitor FROM Monitor WHERE id_estudiante = 202400000001), (SELECT id_curso FROM Curso WHERE nombre_curso = 'POO'), 'Salón de Computo'),
((SELECT id_monitor FROM Monitor WHERE id_estudiante = 202400000001), (SELECT id_curso FROM Curso WHERE nombre_curso = 'POO'), 'Salón X');

-- Julian Mantilla (Monitor para Bases de Datos)
-- Ya tenía 'Salón de Computo'. Agregamos 'Biblioteca' y 'Salón X'.
INSERT INTO Monitor_Curso (id_monitor, id_curso, nombre_lugar) VALUES
((SELECT id_monitor FROM Monitor WHERE id_estudiante = 202400000001), (SELECT id_curso FROM Curso WHERE nombre_curso = 'Bases de Datos'), 'Biblioteca'),
((SELECT id_monitor FROM Monitor WHERE id_estudiante = 202400000001), (SELECT id_curso FROM Curso WHERE nombre_curso = 'Bases de Datos'), 'Salón X');


-- Cristian Perez (Monitor para Calculo Diferencial)
-- Ya tenía 'Salón de Computo'. Agregamos 'Biblioteca' y 'Salón X'.
INSERT INTO Monitor_Curso (id_monitor, id_curso, nombre_lugar) VALUES
((SELECT id_monitor FROM Monitor WHERE id_estudiante = 202400000002), (SELECT id_curso FROM Curso WHERE nombre_curso = 'Calculo Diferencial'), 'Biblioteca'),
((SELECT id_monitor FROM Monitor WHERE id_estudiante = 202400000002), (SELECT id_curso FROM Curso WHERE nombre_curso = 'Calculo Diferencial'), 'Salón X');

-- Sneider Rojas (Monitor para Programacion Web)
-- Ya tenía 'Salón X'. Agregamos 'Biblioteca' y 'Salón de Computo'.
INSERT INTO Monitor_Curso (id_monitor, id_curso, nombre_lugar) VALUES
((SELECT id_monitor FROM Monitor WHERE id_estudiante = 202400000003), (SELECT id_curso FROM Curso WHERE nombre_curso = 'Programacion Web'), 'Biblioteca'),
((SELECT id_monitor FROM Monitor WHERE id_estudiante = 202400000003), (SELECT id_curso FROM Curso WHERE nombre_curso = 'Programacion Web'), 'Salón de Computo');

















































SELECT * FROM Carrera;
SELECT * FROM Estudiante;
SELECT * FROM Sede;
SELECT * FROM Periodo;
SELECT * FROM Monitor;
SELECT * FROM Curso;
SELECT * FROM monitor_curso;
SELECT * FROM Modalidad;
SELECT * FROM Asesoria;
SELECT * FROM Asesoria_Estudiante;
SELECT * FROM usuarios;
DELETE FROM Estudiante;



SELECT m.id_monitor, 
       SEC_TO_TIME(SUM(TIME_TO_SEC(a.hora_fin) - TIME_TO_SEC(a.hora_inicio))) AS horas_acumuladas,
       CASE 
           WHEN SUM(TIME_TO_SEC(a.hora_fin) - TIME_TO_SEC(a.hora_inicio)) >= 52 * 3600 
           THEN 'Cumplió las 52 horas'
           ELSE 'Aún no cumple las 52 horas'
       END AS estado
FROM Asesoria a
JOIN Monitor_Curso mc ON a.id_monitor_curso = mc.id_monitor_curso
JOIN Monitor m ON mc.id_monitor = m.id_monitor
GROUP BY m.id_monitor;
