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

        existing_user_count = list(result.values())[0]

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

@app.route('/student_dashboard')
def student_dashboard():
    if 'user_id' not in session or session['user_type'] != 'Cliente':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('index'))
    return render_template('student_dashboard.html', user_name=session['user_name'])

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session['user_type'] != 'Administrador':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('index'))
    return render_template('admin_dashboard.html', user_name=session['user_name'])

@app.route('/student/create_enrollment', methods=['GET', 'POST'])
def create_enrollment():
    if 'user_id' not in session or session['user_type'] != 'Cliente':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('index'))

    active_offers = execute_query(
        'SELECT id_oferta, periodo_academico, titulo_conduce, P.nombre AS programa_nombre FROM "Oferta" O JOIN "Programa" P ON O.id_programa = P.id_programa WHERE activa = \'S\' ORDER BY periodo_academico DESC',
        fetchall=True
    )
    if active_offers is None:
        flash('Error al cargar las ofertas académicas.', 'danger')
        active_offers = []

    if request.method == 'POST':
        id_oferta = request.form['id_oferta']
        tipo_prospecto = request.form['tipo_prospecto']

        selected_offer = execute_query('SELECT id_oferta FROM "Oferta" WHERE id_oferta = :id_oferta AND activa = \'S\'', {'id_oferta': id_oferta}, fetchone=True)
        if not selected_offer:
            flash('La oferta seleccionada no es válida o no está activa.', 'danger')
            return render_template('enrollment/create_enrollment.html', active_offers=active_offers)

        check_inscription_query = """
        SELECT COUNT(*)
        FROM "Inscripcion" I
        JOIN "Oferta" O ON I.id_oferta = O.id_oferta
        WHERE I.id_usuario = :user_id 
        AND O.id_oferta = :id_oferta
        """
        result = execute_query(check_inscription_query, {'user_id': session['user_id'], 'id_oferta': id_oferta}, fetchone=True)
        existing_inscription_count = result[0] if result else 0

        if existing_inscription_count > 0:
            flash('Ya tienes una inscripción activa para esta oferta académica.', 'warning')
            return render_template('enrollment/create_enrollment.html', active_offers=active_offers)

        insert_query = """
        INSERT INTO "Inscripcion" (id_usuario, id_oferta, tipo_prospecto, fecha_inscripcion, estado_inscripcion)
        VALUES (:id_usuario, :id_oferta, :tipo_prospecto, SYSDATE, 'En progreso')
        """
        params = {
            'id_usuario': session['user_id'],
            'id_oferta': id_oferta,
            'tipo_prospecto': tipo_prospecto
        }

        success = execute_query(insert_query, params, commit=True)

        if success:
            flash('Tu inscripción ha sido creada exitosamente.', 'success')
            return redirect(url_for('student_view_enrollments'))
        else:
            flash('Error al crear la inscripción.', 'danger')

    return render_template('enrollment/create_enrollment.html', active_offers=active_offers)

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

    return render_template('enrollment/view_enrollments.html', enrollments=enrollments)

@app.route('/admin/manage_academic_offer')
def admin_manage_academic_offer():
    if 'user_id' not in session or session['user_type'] != 'Administrador':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('index'))
    flash('Sección para gestión de oferta académica.', 'info')
    return render_template('admin_basic_action.html', title="Gestionar Oferta Académica")

@app.route('/admin/review_enrollments')
def admin_review_enrollments():
    if 'user_id' not in session or session['user_type'] != 'Administrador':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('index'))

    all_enrollments = execute_query("""
        SELECT 
            I.id_inscripcion, U.nombre || ' ' || U.apellido AS nombre_prospecto,
            O.periodo_academico, P.nombre AS programa_nombre, I.estado_inscripcion, I.tipo_prospecto
        FROM 
            "Inscripcion" I
        JOIN "Usuario" U ON I.id_usuario = U.id_usuario
        JOIN "Oferta" O ON I.id_oferta = O.id_oferta
        JOIN "Programa" P ON O.id_programa = P.id_programa
        ORDER BY I.fecha_inscripcion DESC
    """, fetchall=True)

    if all_enrollments is None:
        flash('Error al cargar las inscripciones.', 'danger')
        all_enrollments = []

    return render_template('admin_review_enrollments.html', all_enrollments=all_enrollments)

if __name__ == '__main__':
    app.run(debug=True)
