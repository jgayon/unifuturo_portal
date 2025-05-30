from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import execute_query
import hashlib
import oracledb as cx_Oracle

app = Flask(__name__)
app.config.from_object(Config)

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

        success = execute_query(query, params, commit=True)

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
    columns = ['nombre', 'apellido', 'telefono', 'direccion', 'correo']
    user_data = None

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

        success = execute_query(update_query, params, commit=True)

        if success:
            flash('Tu información ha sido actualizada correctamente.', 'success')
            session['user_name'] = nombre  # Actualiza en la sesión
            return redirect(url_for('student_dashboard'))
        else:
            flash('Hubo un error al actualizar tu información.', 'danger')

    # Siempre cargamos los datos actuales del usuario para mostrarlos en el formulario
    user_data = execute_query('SELECT nombre, apellido, telefono, direccion, correo FROM "Usuario" WHERE id_usuario = :id', {'id': user_id}, fetchone=True)

    if user_data is None:
        flash('Error al cargar tus datos.', 'danger')
        return redirect(url_for('student_dashboard'))

    user_data = dict(zip(columns, user_data))

    return render_template('student/edit_profile.html', user_data=user_data)



@app.route('/create_enrollment', methods=['GET', 'POST'])
def create_enrollment():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']

    # Cargar las ofertas activas desde la BD
    query_ofertas = 'SELECT id_oferta, periodo_academico, titulo_conduce FROM "Oferta" WHERE activa = \'S\''
    ofertas = execute_query(query_ofertas, fetchall=True)

    if request.method == 'POST':
        oferta_id = request.form.get('oferta_id')
        tipo_prospecto = request.form.get('tipo_prospecto')

        # Validaciones básicas
        if not oferta_id or not tipo_prospecto:
            flash('Todos los campos son obligatorios.', 'danger')
            return render_template('enrollment/create_enrollment.html', ofertas=ofertas)

        # Verificar si el usuario ya tiene inscripción para esa oferta
        check_query = """
            SELECT COUNT(*) AS cantidad
            FROM "Inscripcion"
            WHERE id_usuario = :id_usuario AND id_oferta = :id_oferta
        """
        check_params = {'id_usuario': user_id, 'id_oferta': oferta_id}
        result = execute_query(check_query, check_params, fetchone=True)

        existing_inscription_count = result['CANTIDAD'] if result else 0

        if existing_inscription_count > 0:
            flash('Ya tienes una inscripción para esta oferta.', 'warning')
            return render_template('enrollment/create_enrollment.html', ofertas=ofertas)

        # Crear nueva inscripción
        insert_query = """
            INSERT INTO "Inscripcion" (
                id_usuario, id_oferta, tipo_prospecto, fecha_inscripcion, estado_inscripcion
            ) VALUES (
                :id_usuario, :id_oferta, :tipo_prospecto, SYSDATE, 'En progreso'
            )
        """
        insert_params = {
            'id_usuario': user_id,
            'id_oferta': oferta_id,
            'tipo_prospecto': tipo_prospecto
        }

        print("Insertando inscripción con:", insert_params)

        success = execute_query(insert_query, insert_params, commit=True)

        if success is not None:
            flash('Inscripción realizada exitosamente.', 'success')
            return redirect('/student_dashboard')
        else:
            flash('Ocurrió un error al guardar la inscripción.', 'danger')

    return render_template('enrollment/create_enrollment.html', ofertas=ofertas)

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
def manage_requirements():
    if 'user_id' not in session or session['user_type'] != 'Administrador':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        action = request.form['action']
        req_id = request.form['id_requisito']

        if action == 'Editar':
            nuevo_nombre = request.form['nombre']
            update_query = '''
                UPDATE "Requisitos"
                SET nombre = :nombre
                WHERE id_requisito = :id_requisito
            '''
            execute_query(update_query, {'nombre': nuevo_nombre, 'id_requisito': req_id}, commit=True)
            flash('Requisito actualizado.', 'success')
        elif action == 'Eliminar':
            delete_query = 'DELETE FROM "Requisitos" WHERE id_requisito = :id_requisito'
            execute_query(delete_query, {'id_requisito': req_id}, commit=True)
            flash('Requisito eliminado.', 'info')

    requisitos = execute_query('SELECT * FROM "Requisitos"', fetchall=True)
    if requisitos is None:
        requisitos = []
    return render_template('admin/manage_requirements.html', requisitos=requisitos)

#Revisar Programa
@app.route('/admin/manage_programs')
def manage_programs():
    if 'user_id' not in session or session['user_type'] != 'Administrador':
        return redirect(url_for('index'))

    programas = execute_query('SELECT * FROM "Programa"', fetchall=True)
    return render_template('admin/manage_programs.html', programas=programas)

#Revisar Asignaturas
@app.route('/admin/manage_subjects')
def manage_subjects():
    if 'user_id' not in session or session['user_type'] != 'Administrador':
        return redirect(url_for('index'))

    asignaturas = execute_query('SELECT * FROM "Asignaturas"', fetchall=True)
    return render_template('admin/manage_subjects.html', asignaturas=asignaturas)

#Revisar Inscripciones
@app.route('/admin/review_enrollments')
def admin_review_enrollments():
    if 'user_id' not in session or session['user_type'] != 'Administrador':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('index'))

    query = '''
        SELECT i.id_inscripcion, u.nombre, u.apellido, o.periodo_academico, p.nombre AS programa, i.estado_inscripcion
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
            titulo = request.form['titulo_conduce']
            periodo = request.form['periodo_academico']
            activa = request.form['activa']

            update_query = '''
                UPDATE "Oferta"
                SET titulo_conduce = :titulo_conduce,
                    periodo_academico = :periodo_academico,
                    activa = :activa
                WHERE id_oferta = :id_oferta
            '''
            execute_query(update_query, {
                'titulo_conduce': titulo,
                'periodo_academico': periodo,
                'activa': activa,
                'id_oferta': oferta_id
            }, commit=True)
            flash('Oferta actualizada.', 'success')

        elif action == 'Eliminar':
            delete_query = 'DELETE FROM "Oferta" WHERE id_oferta = :id_oferta'
            execute_query(delete_query, {'id_oferta': oferta_id}, commit=True)
            flash('Oferta eliminada.', 'info')

    ofertas = execute_query('SELECT * FROM "Oferta"', fetchall=True)
    return render_template('admin/manage_offers.html', ofertas=ofertas)



#Run
if __name__ == '__main__':
    app.run(debug=True)
