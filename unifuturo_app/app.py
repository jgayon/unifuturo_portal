from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import execute_query
import hashlib
import oracledb as cx_Oracle
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.from_object(Config)

app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/login', methods=['POST'])
def login():
    correo = request.form['correo']
    contrasena = request.form['contrasena']
    hashed_password = hashlib.sha256(contrasena.encode()).hexdigest()

    query = 'SELECT id_usuario, nombre, apellido, correo, contrasena, tipo_usuario FROM "Usuario" WHERE correo = :correo'
    user_data = execute_query(query, params={'correo': correo}, fetchone=True)

    if user_data and user_data['CONTRASENA'] == hashed_password:
        session['user_id'] = user_data['ID_USUARIO']
        session['user_name'] = user_data['NOMBRE']
        session['user_type'] = user_data['TIPO_USUARIO']
        flash(f'¡Bienvenido, {user_data["NOMBRE"]}!', 'success')

        if user_data['TIPO_USUARIO'] == 'Cliente':
            return redirect(url_for('student_dashboard'))
        elif user_data['TIPO_USUARIO'] == 'Administrador':
            return redirect(url_for('admin_dashboard'))
    else:
        flash('Credenciales incorrectas. Intenta de nuevo.', 'danger')

    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        tipo_documento = request.form['tipo_documento']
        num_documento = request.form['num_documento']
        fecha_nacimiento = request.form['fecha_nacimiento']
        correo = request.form['correo']
        contrasena = request.form['contrasena']
        tipo_usuario = request.form['tipo_usuario']
        username = request.form['username']
        admin_code = request.form.get('admin_code')

        if not all([nombre, apellido, tipo_documento, num_documento, fecha_nacimiento, correo, contrasena, tipo_usuario, username]):
            flash('Por favor, completa todos los campos obligatorios.', 'danger')
            return render_template('register.html')

        # Verificar código de administrador solo si aplica
        if tipo_usuario == 'Administrador' and admin_code != app.config['ADMIN_REGISTRATION_CODE']:
            flash('Código de autorización de administrador incorrecto.', 'danger')
            return render_template('register.html', form_data=request.form)

        hashed_password = hashlib.sha256(contrasena.encode()).hexdigest()

        # Verificar si ya existe ese correo o documento
        check_user_query = 'SELECT COUNT(*) FROM "Usuario" WHERE correo = :correo OR num_documento = :num_documento'
        result = execute_query(check_user_query, {'correo': correo, 'num_documento': num_documento}, fetchone=True)

        if result is None:
            flash('Error al verificar si el usuario ya existe.', 'danger')
            return render_template('register.html', form_data=request.form)

        #existing_user_count = list(result.values())[0]
        existing_user_count = result['COUNT(*)'] if result else 0

        if existing_user_count > 0:
            flash('El correo o número de documento ya está registrado.', 'danger')
            return render_template('register.html', form_data=request.form)

        # Crear el nuevo usuario
        query = '''
        INSERT INTO "Usuario" 
        (nombre, apellido, telefono, direccion, tipo_documento, num_documento, fecha_nacimiento, correo, contrasena, tipo_usuario, username)
        VALUES 
        (:nombre, :apellido, :telefono, :direccion, :tipo_documento, :num_documento, TO_DATE(:fecha_nacimiento, 'YYYY-MM-DD'), :correo, :contrasena, :tipo_usuario, :username)
        '''

        params = {
            'nombre': nombre,
            'apellido': apellido,
            'telefono': telefono,
            'direccion': direccion,
            'tipo_documento': tipo_documento,
            'num_documento': num_documento,
            'fecha_nacimiento': fecha_nacimiento,
            'correo': correo,
            'contrasena': hashed_password,
            'tipo_usuario': tipo_usuario,
            'username': username
        }

        success = execute_query(query, params)

        if success:
            flash('Usuario creado exitosamente. ¡Ahora puedes iniciar sesión!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Error al crear el usuario. Por favor, intenta de nuevo.', 'danger')

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_type', None)
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('index'))

@app.route('/upload_requisito', methods=['POST'])
def upload_requisito():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    oferta_id = request.form.get('oferta_id')
    requisito_id = request.form.get('requisito_id')
    file = request.files.get('archivo')

    if file and oferta_id and requisito_id:
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)

        insert = '''
        INSERT INTO "Documento_Requisito" (id_usuario, id_oferta, id_requisito, nombre_archivo, ruta_archivo)
        VALUES (:uid, :oid, :rid, :fname, :ruta)
        '''
        params = {
            'uid': user_id,
            'oid': oferta_id,
            'rid': requisito_id,
            'fname': filename,
            'ruta': path
        }
        execute_query(insert, params)
        return 'Subida exitosa'
    return 'Error en la subida'

# --- Student Side ----

@app.route('/student_dashboard')
def student_dashboard():
    if 'user_id' not in session or session['user_type'] != 'Cliente':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('index'))
    return render_template('student_dashboard.html', user_name=session['user_name'])

@app.route('/student/edit_profile', methods=['GET', 'POST'])
def student_edit_profile():
    if 'user_id' not in session or session['user_type'] != 'Cliente':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('index'))

    user_id = session['user_id']

    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        correo = request.form['correo']

        update_query = '''
        UPDATE "Usuario"
        SET nombre = :nombre,
            apellido = :apellido,
            telefono = :telefono,
            direccion = :direccion,
            correo = :correo
        WHERE id_usuario = :user_id
        '''
        params = {
            'nombre': nombre,
            'apellido': apellido,
            'telefono': telefono,
            'direccion': direccion,
            'correo': correo,
            'user_id': user_id
        }

        success = execute_query(update_query, params)

        if success:
            flash('Tu información ha sido actualizada correctamente.', 'success')
            session['user_name'] = nombre
            return redirect(url_for('student_dashboard'))
        else:
            flash('Hubo un error al actualizar tu información.', 'danger')

    # Carga de datos actual del usuario 
    user_data = execute_query(
        'SELECT nombre, apellido, telefono, direccion, correo FROM "Usuario" WHERE id_usuario = :id',
        {'id': user_id},
        fetchone=True
    )
    print("user_data:", user_data, type(user_data))
    if user_data is None:
        flash('Error al cargar tus datos.', 'danger')
        return redirect(url_for('student_dashboard'))

    return render_template('student/edit_profile.html', user_data=user_data)

#Crear Inscripciones
@app.route('/create_enrollment', methods=['GET', 'POST'])
def create_enrollment_step1():
    if 'user_id' not in session:
        return redirect('/login')

    periodos = execute_query(
        'SELECT DISTINCT periodo_academico FROM "Oferta" WHERE activa = \'S\' ORDER BY periodo_academico DESC',
        fetchall=True
    )

    selected_periodo = request.form.get('periodo_academico')
    ofertas = []

    if selected_periodo:
        ofertas = execute_query('''
            SELECT o.id_oferta, p.nombre AS nombre_programa
            FROM "Oferta" o
            JOIN "Programa" p ON o.id_programa = p.id_programa
            WHERE o.periodo_academico = :periodo AND o.activa = 'S'
        ''', {'periodo': selected_periodo}, fetchall=True)

    if request.method == 'POST' and 'siguiente' in request.form:
        oferta_id = request.form.get('oferta_id')
        tipo_prospecto = request.form.get('tipo_prospecto')
        if not oferta_id or not tipo_prospecto:
            flash('Todos los campos son obligatorios.', 'danger')
        else:
            return redirect(url_for('create_enrollment_step2', oferta_id=oferta_id, tipo_prospecto=tipo_prospecto))

    return render_template('enrollment/select_offer.html', periodos=periodos, selected_periodo=selected_periodo, ofertas=ofertas)

@app.route('/create_enrollment_step2', methods=['GET', 'POST'])
def create_enrollment_step2():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    oferta_id = request.args.get('oferta_id') or request.form.get('oferta_id')
    tipo_prospecto = request.args.get('tipo_prospecto') or request.form.get('tipo_prospecto')

    requisitos = execute_query('''
        SELECT r.id_requisito, r.nombre_requisito
        FROM "Oferta_Requisito" orq
        JOIN "Requisitos" r ON orq.id_requisito = r.id_requisito
        WHERE orq.id_oferta = :id_oferta
    ''', {'id_oferta': oferta_id}, fetchall=True)

    if request.method == 'POST' and 'inscribirse' in request.form:
        # Verificar inscripción existente
        ya_inscrito = execute_query(
            'SELECT COUNT(*) AS cantidad FROM "Inscripcion" WHERE id_usuario = :uid AND id_oferta = :oid',
            {'uid': user_id, 'oid': oferta_id}, fetchone=True
        )

        if ya_inscrito and ya_inscrito['CANTIDAD'] > 0:
            flash('Ya tienes una inscripción para esta oferta.', 'warning')
        else:
            execute_query('''
                INSERT INTO "Inscripcion" (id_usuario, id_oferta, tipo_prospecto, fecha_inscripcion, estado_inscripcion)
                VALUES (:uid, :oid, :tp, SYSDATE, 'En progreso')
            ''', {
                'uid': user_id,
                'oid': oferta_id,
                'tp': tipo_prospecto
            })

            insc = execute_query('''
                SELECT MAX(id_inscripcion) AS id FROM "Inscripcion"
                WHERE id_usuario = :uid AND id_oferta = :oid
            ''', {'uid': user_id, 'oid': oferta_id}, fetchone=True)
            id_inscripcion = insc['ID']

            for req in requisitos:
                file = request.files.get(f'doc_{req["id_requisito"]}')
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    ruta = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(ruta)
                    execute_query('''
                        INSERT INTO "Documentos" (id_inscripcion, id_requisito, nombre_archivo, ruta_archivo, tipo_mime)
                        VALUES (:iid, :rid, :fname, :ruta, :mime)
                    ''', {
                        'iid': id_inscripcion,
                        'rid': req['id_requisito'],
                        'fname': filename,
                        'ruta': ruta,
                        'mime': file.content_type
                    })

            flash('Inscripción realizada y documentos guardados.', 'success')
            return redirect('/student_dashboard')

    return render_template('enrollment/upload_documents.html', requisitos=requisitos, oferta_id=oferta_id, tipo_prospecto=tipo_prospecto)


#Ver inscripciones
@app.route('/student/view_enrollments')
def student_view_enrollments():
    if 'user_id' not in session or session['user_type'] != 'Cliente':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('index'))

    user_id = session['user_id']
    query = """
    SELECT 
        I.id_inscripcion, I.tipo_prospecto, I.fecha_inscripcion, I.estado_inscripcion,
        O.periodo_academico, P.nombre AS programa_nombre, O.titulo_conduce
    FROM 
        "Inscripcion" I
    JOIN 
        "Oferta" O ON I.id_oferta = O.id_oferta
    JOIN 
        "Programa" P ON O.id_programa = P.id_programa
    WHERE 
        I.id_usuario = :user_id
    ORDER BY 
        I.fecha_inscripcion DESC
    """
    enrollments = execute_query(query, params={'user_id': user_id}, fetchall=True)
    if enrollments is None:
        flash('Error al cargar tus inscripciones.', 'danger')
        enrollments = []

    return render_template('enrollment/view_enrollment.html', enrollments=enrollments)

#--- ADMIN SIDE ---

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session['user_type'] != 'Administrador':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('index'))
    return render_template('admin_dashboard.html', user_name=session['user_name'])

#Manejar oferta academica
@app.route('/admin/manage_academic_offer')
def admin_manage_academic_offer():
    if 'user_id' not in session or session['user_type'] != 'Administrador':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('index'))
    flash('Sección para gestión de oferta académica.', 'info')
    return render_template('admin_basic_action.html', title="Gestionar Oferta Académica")

#Manejar requisitos
@app.route('/admin/manage_requirements', methods=['GET', 'POST'])
def admin_manage_requirements():
    if 'user_id' not in session or session['user_type'] != 'Administrador':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        action = request.form.get('action')
        id_requisito = request.form.get('id_requisito')
        nombre_doc = request.form.get('nombre_doc')  

        if action == 'Agregar':
            if nombre_doc:
                insert_query = 'INSERT INTO "Requisitos" (nombre_doc) VALUES (:nombre_doc)'
                execute_query(insert_query, {'nombre_doc': nombre_doc})
                flash('Requisito agregado exitosamente.', 'success')
            else:
                flash('El nombre del requisito no puede estar vacío.', 'warning')

        elif action == 'Editar':
            if id_requisito and nombre_doc:
                update_query = '''
                    UPDATE "Requisitos"
                    SET nombre_doc = :nombre_doc
                    WHERE id_requisito = :id_requisito
                '''
                execute_query(update_query, {
                    'nombre_doc': nombre_doc,
                    'id_requisito': id_requisito
                })
                flash('Requisito actualizado correctamente.', 'success')
            else:
                flash('Faltan datos para actualizar el requisito.', 'danger')

        elif action == 'Eliminar':
            if id_requisito:
                delete_query = 'DELETE FROM "Requisitos" WHERE id_requisito = :id_requisito'
                execute_query(delete_query, {'id_requisito': id_requisito})
                flash('Requisito eliminado correctamente.', 'info')
            else:
                flash('ID de requisito no válido.', 'danger')

        return redirect(url_for('admin_manage_requirements'))

    requisitos = execute_query('SELECT id_requisito, nombre_doc FROM "Requisitos"', fetchall=True) or []
    return render_template('admin/manage_requirements.html', requisitos=requisitos)


# Revisar / Crear / Editar Programas
@app.route('/admin/manage_programs')
def manage_programs():
    if 'user_id' not in session or session['user_type'] != 'Administrador':
        return redirect(url_for('index'))

    programas = execute_query('SELECT * FROM "Programa"', fetchall=True)
    return render_template('admin/manage_programs.html', programas=programas)

# Crear Programa
@app.route('/admin/program/new', methods=['GET', 'POST'])
def create_program():
    if 'user_id' not in session or session['user_type'] != 'Administrador':
        return redirect(url_for('index'))

    if request.method == 'POST':
        nombre = request.form['nombre']
        num_semestres = request.form['num_semestres']
        descripcion = request.form.get('descripcion', '')

        execute_query('''
            INSERT INTO "Programa" (nombre, num_semestres, descripcion)
            VALUES (:nombre, :num_semestres, :descripcion)
        ''', {
            'nombre': nombre,
            'num_semestres': num_semestres,
            'descripcion': descripcion
        })

        flash('Programa creado con éxito.', 'success')
        return redirect(url_for('manage_programs'))

    return render_template('admin/create_program.html')
#Eliminar Programa
@app.route('/admin/program/<int:id_programa>/delete', methods=['POST'])
def delete_program(id_programa):
    execute_query('''
        DELETE FROM "Programa"
        WHERE id_programa = :id
    ''', {'id': id_programa})

    flash('Programa eliminado con éxito.', 'info')
    return redirect(url_for('manage_programs'))
# Editar Programa
@app.route('/admin/program/<int:id_programa>/edit', methods=['GET', 'POST'])
def update_program(id_programa):
    if 'user_id' not in session or session['user_type'] != 'Administrador':
        return redirect(url_for('index'))

    if request.method == 'POST':
        nombre = request.form['nombre']
        num_semestres = request.form['num_semestres']
        descripcion = request.form.get('descripcion', '')

        execute_query('''
            UPDATE "Programa"
            SET nombre = :nombre,
                num_semestres = :num_semestres,
                descripcion = :descripcion
            WHERE id_programa = :id
        ''', {
            'nombre': nombre,
            'num_semestres': num_semestres,
            'descripcion': descripcion,
            'id': id_programa
        })

        flash('Programa actualizado con éxito.', 'success')
        return redirect(url_for('manage_programs'))

    programa = execute_query(
        'SELECT * FROM "Programa" WHERE id_programa = :id',
        {'id': id_programa},
        fetchone=True
    )

    asignaturas = execute_query('SELECT id_asignatura, nombre FROM "Asignaturas"', fetchall=True)

    asignaturas_prog = execute_query('''
        SELECT a.id_asignatura, a.nombre, pa.semestre_en_programa
        FROM "Programa_Asignatura" pa
        JOIN "Asignaturas" a ON a.id_asignatura = pa.id_asignatura
        WHERE pa.id_programa = :id
    ''', {'id': id_programa}, fetchall=True)

    return render_template('admin/edit_program.html',
                           programa=programa,
                           asignaturas=asignaturas,
                           asignaturas_prog=asignaturas_prog)

# Agregar asignatura a programa
@app.route('/admin/program/<int:id_programa>/add_subject', methods=['POST'])
def add_subject_to_program(id_programa):
    id_asignatura = request.form['id_asignatura']
    semestre = request.form['semestre']

    execute_query('''
        INSERT INTO "Programa_Asignatura" (id_programa, id_asignatura, semestre_en_programa)
        VALUES (:id_programa, :id_asignatura, :semestre)
    ''', {
        'id_programa': id_programa,
        'id_asignatura': id_asignatura,
        'semestre': semestre
    })

    flash('Asignatura agregada al programa.', 'success')
    return redirect(url_for('update_program', id_programa=id_programa))

# Quitar asignatura del programa
@app.route('/admin/program/<int:id_programa>/remove_subject', methods=['POST'])
def remove_subject_from_program(id_programa):
    id_asignatura = request.form['id_asignatura']

    execute_query('''
        DELETE FROM "Programa_Asignatura"
        WHERE id_programa = :id_programa AND id_asignatura = :id_asignatura
    ''', {
        'id_programa': id_programa,
        'id_asignatura': id_asignatura
    })

    flash('Asignatura eliminada del programa.', 'info')
    return redirect(url_for('update_program', id_programa=id_programa))


#Revisar Asignaturas
@app.route('/admin/manage_subjects', methods=['GET'])
def manage_subjects():
    if 'user_id' not in session or session['user_type'] != 'Administrador':
        return redirect(url_for('index'))

    asignaturas = execute_query('SELECT * FROM "Asignaturas"', fetchall=True)
    return render_template('admin/manage_subjects.html', asignaturas=asignaturas)


@app.route('/admin/subject/create', methods=['POST'])
def create_subject():
    nombre = request.form.get('nombre')
    semestre = request.form.get('semestre')
    descripcion = request.form.get('descripcion')

    if nombre and semestre and descripcion:
        query = '''
            INSERT INTO "Asignaturas" (NOMBRE, SEMESTRE, DESCRIPCION)
            VALUES (:nombre, :semestre, :descripcion)
        '''
        execute_query(query, {
            'nombre': nombre,
            'semestre': semestre,
            'descripcion': descripcion
        })
        flash('Asignatura creada exitosamente.', 'success')
    else:
        flash('Todos los campos son obligatorios.', 'danger')

    return redirect(url_for('manage_subjects'))


@app.route('/admin/subject/<int:id_asignatura>/edit', methods=['POST'])
def edit_subject(id_asignatura):
    nombre = request.form.get('nombre')
    semestre = request.form.get('semestre')
    descripcion = request.form.get('descripcion')

    if nombre and semestre and descripcion:
        query = '''
            UPDATE "Asignaturas"
            SET NOMBRE = :nombre,
                SEMESTRE = :semestre,
                DESCRIPCION = :descripcion
            WHERE ID_ASIGNATURA = :id_asignatura
        '''
        execute_query(query, {
            'nombre': nombre,
            'semestre': semestre,
            'descripcion': descripcion,
            'id_asignatura': id_asignatura
        })
        flash('Asignatura actualizada correctamente.', 'info')
    else:
        flash('Todos los campos son obligatorios.', 'danger')

    return redirect(url_for('manage_subjects'))


@app.route('/admin/subject/<int:id_asignatura>/delete', methods=['POST'])
def delete_subject(id_asignatura):
    query = 'DELETE FROM "Asignaturas" WHERE ID_ASIGNATURA = :id_asignatura'
    execute_query(query, {'id_asignatura': id_asignatura})
    flash('Asignatura eliminada.', 'warning')
    return redirect(url_for('manage_subjects'))

#Revisar Inscripciones
@app.route('/admin/review_enrollments', methods=['GET', 'POST'])
def admin_review_enrollments():
    if 'user_id' not in session or session['user_type'] != 'Administrador':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        id_inscripcion = request.form.get('id_inscripcion')
        nuevo_estado = request.form.get('nuevo_estado')

        update_query = '''
            UPDATE "Inscripcion"
            SET estado_inscripcion = :nuevo_estado
            WHERE id_inscripcion = :id_inscripcion
        '''
        execute_query(update_query, {
            'nuevo_estado': nuevo_estado,
            'id_inscripcion': id_inscripcion
        })

        flash(f'Inscripción {id_inscripcion} actualizada a "{nuevo_estado}".', 'success')
        return redirect(url_for('admin_review_enrollments'))

    # Consulta para mostrar todas las inscripciones
    query = '''
        SELECT 
            i.id_inscripcion AS ID_INSCRIPCION,
            u.nombre || ' ' || u.apellido AS NOMBRE_USUARIO,
            o.periodo_academico AS PERIODO_ACADEMICO,
            p.nombre AS NOMBRE_PROGRAMA,
            i.estado_inscripcion AS ESTADO_INSCRIPCION
        FROM "Inscripcion" i
        JOIN "Usuario" u ON i.id_usuario = u.id_usuario
        JOIN "Oferta" o ON i.id_oferta = o.id_oferta
        JOIN "Programa" p ON o.id_programa = p.id_programa
    '''

    all_enrollments = execute_query(query, fetchall=True)
    return render_template('admin/review_enrollments.html', all_enrollments=all_enrollments)

#Revisar documentos
@app.route('/admin/review_documents')
def admin_review_documents():
    if 'user_id' not in session or session['user_type'] != 'Administrador':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('index'))

    query = '''
        SELECT d.id_documento, u.nombre, u.apellido, r.nombre_doc, d.estado_documento
        FROM "Documentos" d
        JOIN "Inscripcion" i ON d.id_inscripcion = i.id_inscripcion
        JOIN "Usuario" u ON i.id_usuario = u.id_usuario
        JOIN "Requisito" r ON d.id_requisito = r.id_requisito
    '''

    all_documents = execute_query(query, fetchall=True)
    return render_template('admin/review_documents.html', all_documents=all_documents)

# Crear oferta académica
@app.route('/admin/create_offer', methods=['GET', 'POST'])
def admin_create_offer():
    if 'user_id' not in session or session['user_type'] != 'Administrador':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        data = {
            'id_programa': request.form['id_programa'],
            'periodo_academico': request.form['periodo_academico'],
            'titulo_conduce': request.form['titulo_conduce'],
            'costo_inscripcion': request.form['costo_inscripcion'],
            'costo_programa': request.form['costo_programa'],
            'activa': request.form['activa'],
            'descripcion_oferta': request.form.get('descripcion_oferta', '')  # opcional
        }

        insert_query = '''
            INSERT INTO "Oferta" (id_programa, periodo_academico, titulo_conduce,
                                  costo_inscripcion, costo_programa, activa, descripcion_oferta)
            VALUES (:id_programa, :periodo_academico, :titulo_conduce,
                    :costo_inscripcion, :costo_programa, :activa, :descripcion_oferta)
        '''
        success = execute_query(insert_query, data)

        if success:
            flash('Oferta creada correctamente.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Error al crear la oferta.', 'danger')

    programas = execute_query('SELECT id_programa, nombre FROM "Programa"', fetchall=True)
    return render_template('admin/create_offer.html', programas=programas)

# Gestionar todas las ofertas: ver, editar, eliminar
@app.route('/admin/manage_offers', methods=['GET', 'POST'])
def admin_manage_offers():
    if 'user_id' not in session or session['user_type'] != 'Administrador':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        action = request.form['action']
        oferta_id = request.form['id_oferta']

        if action == 'Editar':
            try:
                titulo = request.form['titulo_conduce']
                periodo = request.form['periodo_academico']
                costo_inscripcion = float(request.form['costo_inscripcion'].replace(',', '.'))
                costo_programa = float(request.form['costo_programa'].replace(',', '.'))
                descripcion = request.form['descripcion_oferta']
                activa = request.form['activa']

                update_query = '''
                    UPDATE "Oferta"
                    SET titulo_conduce = :titulo_conduce,
                        periodo_academico = :periodo_academico,
                        costo_inscripcion = :costo_inscripcion,
                        costo_programa = :costo_programa,
                        descripcion_oferta = :descripcion_oferta,
                        activa = :activa
                    WHERE id_oferta = :id_oferta
                '''
                execute_query(update_query, {
                    'titulo_conduce': titulo,
                    'periodo_academico': periodo,
                    'costo_inscripcion': costo_inscripcion,
                    'costo_programa': costo_programa,
                    'descripcion_oferta': descripcion,
                    'activa': activa,
                    'id_oferta': oferta_id
                })
                flash('Oferta actualizada.', 'success')
            except ValueError:
                flash('Los campos de costo deben ser números válidos.', 'danger')
        
        elif action == 'Eliminar':
            delete_query = 'DELETE FROM "Oferta" WHERE id_oferta = :id_oferta'
            execute_query(delete_query, {'id_oferta': oferta_id})
            flash('Oferta eliminada.', 'info')

    ofertas = execute_query('''
    SELECT o.*, p.nombre AS PROGRAMA_NOMBRE
    FROM "Oferta" o
    JOIN "Programa" p ON o.id_programa = p.id_programa
''', fetchall=True)
    return render_template('admin/manage_offers.html', ofertas=ofertas)

@app.route('/admin/edit_profile', methods=['GET', 'POST'])
def admin_edit_profile():
    print("user_type:", session.get('user_type'))
    if 'user_id' not in session or session['user_type'] != 'Administrador':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('index'))

    user_id = session['user_id']
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        correo = request.form['correo']

        update_query = '''
            UPDATE "Usuario"
            SET nombre = :nombre,
                apellido = :apellido,
                telefono = :telefono,
                direccion = :direccion,
                correo = :correo
            WHERE id_usuario = :user_id
        '''
        params = {
            'nombre': nombre,
            'apellido': apellido,
            'telefono': telefono,
            'direccion': direccion,
            'correo': correo,
            'user_id': user_id
        }

        success = execute_query(update_query, params)
        if success:
            flash('Perfil actualizado correctamente.', 'success')
            session['user_name'] = nombre
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Hubo un error al actualizar el perfil.', 'danger')

    user_data = execute_query(
        'SELECT nombre, apellido, telefono, direccion, correo FROM "Usuario" WHERE id_usuario = :id',
        {'id': user_id}, fetchone=True
    )

    if user_data is None:
        flash('No se pudieron cargar tus datos.', 'danger')
        return redirect(url_for('admin_dashboard'))

    
    return render_template('admin/edit_profile.html', user_data=user_data)



#Run
if __name__ == '__main__':
    app.run(debug=True)
