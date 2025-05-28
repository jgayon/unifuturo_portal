-- Entregable #4: Script SQL para Ingresar Datos Básicos de Prueba
-- Asegúrate de que las tablas ya estén creadas (Ejecutable #3).

-- Desactivar temporalmente la comprobación de restricciones de clave foránea
-- Esto es útil para insertar datos en un orden que podría violar temporalmente las FKs,
-- aunque en este script se intenta un orden lógico.
-- ALTER TABLE USUARIO DISABLE CONSTRAINT FK_USUARIO_ROL; -- Si tuvieras una tabla de roles separada
-- ALTER TABLE INSCRIPCION DISABLE CONSTRAINT FK_INSCRIPCION_USUARIO;
-- ... y así sucesivamente para todas las FKs si fuera necesario.
-- Sin embargo, el orden de inserción aquí está diseñado para evitar esto.

-- Inserción de datos en la tabla USUARIO
INSERT INTO "Usuario" (nombre, apellido, telefono, direccion, tipo_documento, num_documento, fecha_nacimiento, correo, contrasena, tipo_usuario) VALUES
('Juan', 'Perez', '3001234567', 'Calle 10 # 20-30', 'CC', '1001234567', TO_DATE('1990-05-15', 'YYYY-MM-DD'), 'juan.perez@example.com', 'password123', 'Cliente');

INSERT INTO "Usuario" (nombre, apellido, telefono, direccion, tipo_documento, num_documento, fecha_nacimiento, correo, contrasena, tipo_usuario) VALUES
('Maria', 'Gomez', '3109876543', 'Carrera 5 # 15-25', 'TI', '1002345678', TO_DATE('2002-11-22', 'YYYY-MM-DD'), 'maria.gomez@example.com', 'maria123', 'Cliente');

INSERT INTO "Usuario" (nombre, apellido, telefono, direccion, tipo_documento, num_documento, fecha_nacimiento, correo, contrasena, tipo_usuario) VALUES
('Carlos', 'Ramirez', '3201112233', 'Avenida 7 # 8-90', 'CC', '9000102030', TO_DATE('1985-03-01', 'YYYY-MM-DD'), 'carlos.admin@unifuturo.edu', 'adminsecure', 'Administrador');

INSERT INTO "Usuario" (nombre, apellido, telefono, direccion, tipo_documento, num_documento, fecha_nacimiento, correo, contrasena, tipo_usuario) VALUES
('Ana', 'Diaz', '3014445566', 'Calle 3 # 4-56', 'CE', 'EXT500123', TO_DATE('1995-07-30', 'YYYY-MM-DD'), 'ana.diaz@transfer.com', 'anapass', 'Cliente');

-- Inserción de datos en la tabla REQUISITOS
INSERT INTO "Requisitos" (nombre_doc) VALUES ('Copia Documento de Identidad');
INSERT INTO "Requisitos" (nombre_doc) VALUES ('Certificado de Notas de Bachiller');
INSERT INTO "Requisitos" (nombre_doc) VALUES ('Diploma de Bachiller');
INSERT INTO "Requisitos" (nombre_doc) VALUES ('Foto Tipo Documento');
INSERT INTO "Requisitos" (nombre_doc) VALUES ('Certificado de Homologación de Asignaturas');
INSERT INTO "Requisitos" (nombre_doc) VALUES ('Recibo de Pago de Inscripción');


-- Inserción de datos en la tabla ASIGNATURAS
INSERT INTO "Asignaturas" (nombre, semestre, descripcion) VALUES ('Introducción a la Programación', 1, 'Fundamentos de lógica y programación.');
INSERT INTO "Asignaturas" (nombre, semestre, descripcion) VALUES ('Cálculo Diferencial', 1, 'Estudio de las derivadas y sus aplicaciones.');
INSERT INTO "Asignaturas" (nombre, semestre, descripcion) VALUES ('Bases de Datos I', 2, 'Introducción a los sistemas de gestión de bases de datos relacionales.');
INSERT INTO "Asignaturas" (nombre, semestre, descripcion) VALUES ('Algoritmos y Estructuras de Datos', 2, 'Diseño y análisis de algoritmos eficientes.');
INSERT INTO "Asignaturas" (nombre, semestre, descripcion) VALUES ('Derecho Romano', 1, 'Principios fundamentales del derecho romano.');
INSERT INTO "Asignaturas" (nombre, semestre, descripcion) VALUES ('Introducción a la Sociología', 1, 'Estudio de la sociedad y el comportamiento humano.');

-- Inserción de datos en la tabla PROGRAMA
INSERT INTO "Programa" (nombre, num_semestres, descripcion) VALUES ('Ingeniería de Sistemas', 10, 'Carrera enfocada en el desarrollo de software y gestión de TI.');
INSERT INTO "Programa" (nombre, num_semestres, descripcion) VALUES ('Derecho', 10, 'Formación integral en el ámbito jurídico y legal.');

-- Inserción de datos en la tabla OFERTA
-- Oferta para Ingeniería de Sistemas, periodo 2025-10
INSERT INTO "Oferta" (id_programa, periodo_academico, titulo_conduce, costo_inscripcion, costo_programa, descripcion_oferta, activa) VALUES
((SELECT id_programa FROM "Programa" WHERE nombre = 'Ingeniería de Sistemas'), '2025-10', 'Ingeniero de Sistemas', 150000.00, 15000000.00, 'Oferta para el primer periodo de 2025 de Ingeniería de Sistemas.', 'S');

-- Oferta para Derecho, periodo 2025-10
INSERT INTO "Oferta" (id_programa, periodo_academico, titulo_conduce, costo_inscripcion, costo_programa, descripcion_oferta, activa) VALUES
((SELECT id_programa FROM "Programa" WHERE nombre = 'Derecho'), '2025-10', 'Abogado', 120000.00, 12000000.00, 'Oferta para el primer periodo de 2025 de Derecho.', 'S');

-- Oferta para Ingeniería de Sistemas, periodo 2025-30 (inactiva para ejemplo)
INSERT INTO "Oferta" (id_programa, periodo_academico, titulo_conduce, costo_inscripcion, costo_programa, descripcion_oferta, activa) VALUES
((SELECT id_programa FROM "Programa" WHERE nombre = 'Ingeniería de Sistemas'), '2025-30', 'Ingeniero de Sistemas', 160000.00, 16000000.00, 'Oferta para el segundo periodo de 2025 de Ingeniería de Sistemas.', 'N');


-- Inserción de datos en la tabla OFERTA_REQUISITO (Tabla de Unión)
-- Requisitos para la oferta de Ingeniería de Sistemas 2025-10
INSERT INTO "Oferta_Requisito" (id_oferta, id_requisito) VALUES
((SELECT id_oferta FROM "Oferta" WHERE periodo_academico = '2025-10' AND id_programa = (SELECT id_programa FROM Programa WHERE nombre = 'Ingeniería de Sistemas')), (SELECT id_requisito FROM Requisitos WHERE nombre_doc = 'Copia Documento de Identidad'));
INSERT INTO "Oferta_Requisito" (id_oferta, id_requisito) VALUES
((SELECT id_oferta FROM "Oferta" WHERE periodo_academico = '2025-10' AND id_programa = (SELECT id_programa FROM Programa WHERE nombre = 'Ingeniería de Sistemas')), (SELECT id_requisito FROM Requisitos WHERE nombre_doc = 'Certificado de Notas de Bachiller'));
INSERT INTO "Oferta_Requisito" (id_oferta, id_requisito) VALUES
((SELECT id_oferta FROM "Oferta" WHERE periodo_academico = '2025-10' AND id_programa = (SELECT id_programa FROM Programa WHERE nombre = 'Ingeniería de Sistemas')), (SELECT id_requisito FROM Requisitos WHERE nombre_doc = 'Diploma de Bachiller'));
INSERT INTO "Oferta_Requisito" (id_oferta, id_requisito) VALUES
((SELECT id_oferta FROM "Oferta" WHERE periodo_academico = '2025-10' AND id_programa = (SELECT id_programa FROM Programa WHERE nombre = 'Ingeniería de Sistemas')), (SELECT id_requisito FROM Requisitos WHERE nombre_doc = 'Foto Tipo Documento'));


-- Requisitos para la oferta de Derecho 2025-10
INSERT INTO "Oferta_Requisito" (id_oferta, id_requisito) VALUES
((SELECT id_oferta FROM "Oferta" WHERE periodo_academico = '2025-10' AND id_programa = (SELECT id_programa FROM Programa WHERE nombre = 'Derecho')), (SELECT id_requisito FROM Requisitos WHERE nombre_doc = 'Copia Documento de Identidad'));
INSERT INTO "Oferta_Requisito" (id_oferta, id_requisito) VALUES
((SELECT id_oferta FROM "Oferta" WHERE periodo_academico = '2025-10' AND id_programa = (SELECT id_programa FROM Programa WHERE nombre = 'Derecho')), (SELECT id_requisito FROM Requisitos WHERE nombre_doc = 'Diploma de Bachiller'));


-- Inserción de datos en la tabla PROGRAMA_ASIGNATURA (Tabla de Unión)
-- Asignaturas para Ingeniería de Sistemas
INSERT INTO "Programa_Asignatura" (id_programa, id_asignatura, semestre_en_programa) VALUES
((SELECT id_programa FROM "Programa" WHERE nombre = 'Ingeniería de Sistemas'), (SELECT id_asignatura FROM Asignaturas WHERE nombre = 'Introducción a la Programación'), 1);
INSERT INTO "Programa_Asignatura" (id_programa, id_asignatura, semestre_en_programa) VALUES
((SELECT id_programa FROM "Programa" WHERE nombre = 'Ingeniería de Sistemas'), (SELECT id_asignatura FROM Asignaturas WHERE nombre = 'Cálculo Diferencial'), 1);
INSERT INTO "Programa_Asignatura" (id_programa, id_asignatura, semestre_en_programa) VALUES
((SELECT id_programa FROM "Programa" WHERE nombre = 'Ingeniería de Sistemas'), (SELECT id_asignatura FROM Asignaturas WHERE nombre = 'Bases de Datos I'), 2);
INSERT INTO "Programa_Asignatura" (id_programa, id_asignatura, semestre_en_programa) VALUES
((SELECT id_programa FROM "Programa" WHERE nombre = 'Ingeniería de Sistemas'), (SELECT id_asignatura FROM Asignaturas WHERE nombre = 'Algoritmos y Estructuras de Datos'), 2);

-- Asignaturas para Derecho
INSERT INTO "Programa_Asignatura" (id_programa, id_asignatura, semestre_en_programa) VALUES
((SELECT id_programa FROM "Programa" WHERE nombre = 'Derecho'), (SELECT id_asignatura FROM Asignaturas WHERE nombre = 'Derecho Romano'), 1);
INSERT INTO "Programa_Asignatura" (id_programa, id_asignatura, semestre_en_programa) VALUES
((SELECT id_programa FROM "Programa" WHERE nombre = 'Derecho'), (SELECT id_asignatura FROM Asignaturas WHERE nombre = 'Introducción a la Sociología'), 1);


-- Inserción de datos en la tabla INSCRIPCION
-- Inscripción de Juan Perez (Nuevo) a Ingeniería de Sistemas 2025-10
INSERT INTO "Inscripcion" (id_usuario, id_oferta, tipo_prospecto, fecha_inscripcion, estado_inscripcion) VALUES
((SELECT id_usuario FROM "Usuario" WHERE correo = 'juan.perez@example.com'), (SELECT id_oferta FROM Oferta WHERE periodo_academico = '2025-10' AND id_programa = (SELECT id_programa FROM Programa WHERE nombre = 'Ingeniería de Sistemas')), 'Nuevo', SYSDATE, 'En progreso');

-- Inscripción de Ana Diaz (Transferencia externa) a Derecho 2025-10
INSERT INTO "Inscripcion" (id_usuario, id_oferta, tipo_prospecto, fecha_inscripcion, estado_inscripcion) VALUES
((SELECT id_usuario FROM "Usuario" WHERE correo = 'ana.diaz@transfer.com'), (SELECT id_oferta FROM Oferta WHERE periodo_academico = '2025-10' AND id_programa = (SELECT id_programa FROM Programa WHERE nombre = 'Derecho')), 'Transferencia externa', SYSDATE, 'Homologacion Pendiente');

-- Inscripción de Maria Gomez (Nuevo) a Derecho 2025-10
INSERT INTO "Inscripcion" (id_usuario, id_oferta, tipo_prospecto, fecha_inscripcion, estado_inscripcion) VALUES
((SELECT id_usuario FROM "Usuario" WHERE correo = 'maria.gomez@example.com'), (SELECT id_oferta FROM Oferta WHERE periodo_academico = '2025-10' AND id_programa = (SELECT id_programa FROM Programa WHERE nombre = 'Derecho')), 'Nuevo', SYSDATE, 'Pagado');


-- Inserción de datos en la tabla PAGO
-- Pago de Juan Perez para su inscripción (id_inscripcion 1)
INSERT INTO "Pago" (id_inscripcion, monto_pago, fecha_pago, estado_pago, referencia_pago) VALUES
((SELECT id_inscripcion FROM "Inscripcion" WHERE id_usuario = (SELECT id_usuario FROM Usuario WHERE correo = 'juan.perez@example.com') AND tipo_prospecto = 'Nuevo'), 150000.00, SYSDATE, 'Aprobado', 'PAGO_IS_202510_JP001');

-- Pago de Maria Gomez para su inscripción (id_inscripcion 3)
INSERT INTO Pago (id_inscripcion, monto_pago, fecha_pago, estado_pago, referencia_pago) VALUES
((SELECT id_inscripcion FROM Inscripcion WHERE id_usuario = (SELECT id_usuario FROM Usuario WHERE correo = 'maria.gomez@example.com') AND tipo_prospecto = 'Nuevo'), 120000.00, SYSDATE, 'Aprobado', 'PAGO_D_202510_MG001');


-- Inserción de datos en la tabla DOCUMENTOS
-- Documentos de Juan Perez (Inscripcion 1)
INSERT INTO Documentos (id_inscripcion, id_requisito, nombre_archivo, ruta_archivo, tipo_mime, fecha_subida, estado_documento) VALUES
((SELECT id_inscripcion FROM Inscripcion WHERE id_usuario = (SELECT id_usuario FROM Usuario WHERE correo = 'juan.perez@example.com')), (SELECT id_requisito FROM Requisitos WHERE nombre_doc = 'Copia Documento de Identidad'), 'dni_juan_perez.pdf', '/docs/juan/dni_juan_perez.pdf', 'application/pdf', SYSDATE, 'Aprobado');
INSERT INTO Documentos (id_inscripcion, id_requisito, nombre_archivo, ruta_archivo, tipo_mime, fecha_subida, estado_documento) VALUES
((SELECT id_inscripcion FROM Inscripcion WHERE id_usuario = (SELECT id_usuario FROM Usuario WHERE correo = 'juan.perez@example.com')), (SELECT id_requisito FROM Requisitos WHERE nombre_doc = 'Certificado de Notas de Bachiller'), 'notas_juan_perez.pdf', '/docs/juan/notas_juan_perez.pdf', 'application/pdf', SYSDATE, 'Pendiente');
INSERT INTO Documentos (id_inscripcion, id_requisito, nombre_archivo, ruta_archivo, tipo_mime, fecha_subida, estado_documento) VALUES
((SELECT id_inscripcion FROM Inscripcion WHERE id_usuario = (SELECT id_usuario FROM Usuario WHERE correo = 'juan.perez@example.com')), (SELECT id_requisito FROM Requisitos WHERE nombre_doc = 'Recibo de Pago de Inscripción'), 'recibo_juan_perez.pdf', '/docs/juan/recibo_juan_perez.pdf', 'application/pdf', SYSDATE, 'Aprobado');


-- Documentos de Ana Diaz (Inscripcion 2)
INSERT INTO Documentos (id_inscripcion, id_requisito, nombre_archivo, ruta_archivo, tipo_mime, fecha_subida, estado_documento) VALUES
((SELECT id_inscripcion FROM Inscripcion WHERE id_usuario = (SELECT id_usuario FROM Usuario WHERE correo = 'ana.diaz@transfer.com')), (SELECT id_requisito FROM Requisitos WHERE nombre_doc = 'Copia Documento de Identidad'), 'dni_ana_diaz.pdf', '/docs/ana/dni_ana_diaz.pdf', 'application/pdf', SYSDATE, 'Aprobado');


-- Inserción de datos en la tabla HOMOLOGACION
-- Solicitud de homologación de Ana Diaz (Inscripcion 2)
INSERT INTO Homologacion (id_inscripcion, id_asignatura_programa, nombre_asignatura_externa, justificacion, estado_homologacion) VALUES
((SELECT id_inscripcion FROM Inscripcion WHERE id_usuario = (SELECT id_usuario FROM Usuario WHERE correo = 'ana.diaz@transfer.com')), (SELECT id_asignatura FROM Asignaturas WHERE nombre = 'Derecho Romano'), 'Historia del Derecho I', 'Misma temática y contenidos cubiertos en la universidad anterior.', 'Pendiente');

INSERT INTO Homologacion (id_inscripcion, id_asignatura_programa, nombre_asignatura_externa, justificacion, estado_homologacion) VALUES
((SELECT id_inscripcion FROM Inscripcion WHERE id_usuario = (SELECT id_usuario FROM Usuario WHERE correo = 'ana.diaz@transfer.com')), (SELECT id_asignatura FROM Asignaturas WHERE nombre = 'Introducción a la Sociología'), 'Sociología General', 'Curso equivalente con excelente rendimiento académico.', 'Aprobada');


-- Confirmar la transacción
COMMIT;

-- Opcional: Reactivar las restricciones de clave foránea si se desactivaron
-- ALTER TABLE INSCRIPCION ENABLE CONSTRAINT FK_INSCRIPCION_USUARIO;
-- ... y así sucesivamente para todas las FKs si fuera necesario.