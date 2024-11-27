"""
Este es el codigo de la api
"""
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash, current_app
from flask_restx import Api, Resource, fields, Namespace
from . import api, app
from app.src import Roles
from .Auth import decode_token, generate_token, token_required
from .models import db, ConfirmedUser, PotentialUser, Folders, Establishments, MenuItems
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message
import config


ns = Namespace("meriendas", description="merienda operations")

user = api.model(
    "Usuario", {
        "username": fields.String(required=True, description="El usuario"),
        "password": fields.String(required=True, description="La contraseña"),
        "email": fields.String(required=True, description="El correo"),
        "rol": fields.String(required=False, description="Rol del usuario (resto, persona, etc)")
    }
)

userList = api.model(
    "Usuarios", {
        "id": fields.String(required=True, description="id de usuario"),
        "username": fields.Nested(user, description="El usuario"),
    }
)

# Diccionario para mapear opciones visibles a roles internos
role_mapping = {
    "Personal": Roles.PersonRole,
    "Gastronómico": Roles.GastroRole
}

parser = api.parser()
parser.add_argument(
    "username", type=str, required=True, help="usuario", location="form"
)
parser.add_argument(
    "password", type=str, required=True, help="<PASSWORD>", location="form"
)
parser.add_argument(
    "email", type=str, required=True, help="correo", location="form"
)
parser.add_argument(
    "role", type=str, required=False, help="Rol", location="form", choices=list(role_mapping.keys())
)

@app.route('/routes')
def show_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append(f'{rule.endpoint}: {rule.rule}')
    return "<br>".join(routes)

### APP.ROUTE son las visualizaciones de la PAGINA
# O sea, los render template
@app.route('/')
def Index():
    return render_template('index.html')

### NS.ROUTE son los controles de la API
# o sea, los GETS-POSTS
@ns.route('/')
@ns.doc(description="Este seria un endpoint normal")
class Index(Resource):
    def get(self):
        return jsonify({"hotel":"trivago"})

@app.route('/select')
def register_select():
    return render_template('select_usertype.html')

@app.route('/personal')
def register_personal_page():
    return render_template('register_personal.html')

@app.route('/gastronomic')
def register_gastronomic_page():
    return render_template('register_gastronomic.html')
@ns.route('/personal')
class RegisterPersonal(Resource):
    def get(self):
        return render_template('register_personal.html')
        
    def post(self):
        '''Crea un usuario nuevo y lo agrega al archivo de texto donde por ahora tenemos todos los usuarios.
        Esto más adelante va a ser una base de datos.
        Restricciones:
        - Todos los campos tienen que ser completados
        - La contraseña tiene que tener mínimo 8 caracteres
        - Para que el mail sea válido, tiene que tener un @ en algún lado
        - No se pueden repetir usuarios ni emails'''

        user_first_name = request.form.get("user_first_name")
        user_last_name = request.form.get("user_last_name")
        date_of_birth = request.form.get("date_of_birth")
        gender = request.form.get("gender")
        user_phone_number = request.form.get("user_phone_number")
        user_document_type = request.form.get("user_document_type")
        user_document = request.form.get("user_document")
        user_email = request.form.get("user_email")
        user_username = request.form.get("user_username")
        password = request.form.get("password")
        user_type = "P"
        user_province = request.form.get("user_province")
        user_postal_code = request.form.get("user_postal_code")
        
        if not all([user_first_name, user_last_name, date_of_birth, gender, user_phone_number, 
                    user_document_type, user_document, user_email, user_username, password, user_province, user_postal_code]):
            flash('Todos los campos son obligatorios', 'error')
            return redirect(url_for('register_personal_page'))

        if "@" not in user_email:
            flash('El correo electrónico debe tener un formato válido', 'error')
            return redirect(url_for('register_personal_page'))
        
        if len(password) < 8:
            flash('La contraseña debe tener al menos 8 caracteres', 'error')
            return redirect(url_for('register_personal_page'))
        
        existing_user = ConfirmedUser.query.filter(
            (ConfirmedUser.user_username == user_username)).first()
        if existing_user:
            flash('El nombre de usuario', 'error')
            return redirect(url_for('register_personal_page'))
        
        existing_user = ConfirmedUser.query.filter(
            (ConfirmedUser.user_email == user_email)).first()
        if existing_user:
            flash('El correo electrónico ya está registrado', 'error')
            return redirect(url_for('register_personal_page'))
        
        existing_user = ConfirmedUser.query.filter((ConfirmedUser.user_phone_number == user_phone_number)
        ).first()
        if existing_user:
            flash('El numero de telefono ya está registrado', 'error')
            return redirect(url_for('register_personal_page'))
        
        potential_user = PotentialUser.query.filter((PotentialUser.user_phone_number == user_phone_number)
        ).first()
        if potential_user:
            flash('El numero de telefono ya está registrado', 'error')
            return redirect(url_for('register_personal_page'))
        
        potential_user = PotentialUser.query.filter(
            (PotentialUser.user_username == user_username)).first()
        if potential_user:
            flash('El nombre de usuario ya está registrado', 'error')
            return redirect(url_for('register_personal_page'))
        
        potential_user = PotentialUser.query.filter(
            (PotentialUser.user_email == user_email)).first()
        if potential_user:
            flash('El correo electrónico ya está registrado', 'error')
            return redirect(url_for('register_personal_page'))
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        
        new_user = PotentialUser(
            user_province=user_province,
            user_postal_code=user_postal_code,
            user_first_name=user_first_name,
            user_last_name=user_last_name,
            date_of_birth=datetime.strptime(date_of_birth, "%Y-%m-%d"),
            gender=gender,
            user_phone_number=user_phone_number,
            user_document_type=user_document_type,
            user_document=user_document,
            user_email=user_email,
            user_username=user_username,
            password_hash=hashed_password,
            user_type=user_type,
            is_verified=False
        )
        new_confirmed_user = ConfirmedUser(
            user_province=user_province,
            user_postal_code=user_postal_code,
            user_first_name=user_first_name,
            user_last_name=user_last_name,
            date_of_birth=datetime.strptime(date_of_birth, "%Y-%m-%d"),
            gender=gender,
            user_phone_number=user_phone_number,
            user_document_type=user_document_type,
            user_document=user_document,
            user_email=user_email,
            user_username=user_username,
            password_hash=hashed_password,
            user_type=user_type,
            is_verified=False
        )

        db.session.add(new_user)
        db.session.add(new_confirmed_user)
        db.session.commit()

        id = new_confirmed_user.id
        to_visit = Folders(user_id = id,
            folder_name = "Por visitar",
            exclusive = True)
        
        visited = Folders(user_id = id,
            folder_name = "Visitados",
            exclusive = True)
        
        db.session.add(to_visit)
        db.session.add(visited)
        db.session.commit()
        if app.config['TESTING'] == True:
            db.session.delete(new_confirmed_user)
            db.session.delete(new_user)
            db.session.delete(to_visit)
            db.session.delete(visited)
            db.session.commit()

        token = generate_confirmation_token(user_email)

        return redirect(url_for('confirm_page', token = token))

@ns.route('/gastronomic')
class RegisterGatronomic(Resource):
    def get(self):
        return render_template('register_gastronomic.html')
        
    def post(self):
        '''Crea un usuario nuevo y lo agrega al archivo de texto donde por ahora tenemos todos los usuarios.
        Esto más adelante va a ser una base de datos.
        Restricciones:
        - Todos los campos tienen que ser completados
        - La contraseña tiene que tener mínimo 8 caracteres
        - Para que el mail sea válido, tiene que tener un @ en algún lado
        - No se pueden repetir usuarios ni emails'''

        user_nombre_comercial = request.form.get("user_nombre_comercial")
        user_phone_number = request.form.get("user_phone_number")
        user_document_type = request.form.get("user_document_type")
        user_document = request.form.get("user_document")
        user_rep_legal = request.form.get("user_rep_legal")
        user_province = request.form.get("user_province")
        user_postal_code = request.form.get("user_postal_code")
        user_username = request.form.get("user_username")
        user_email = request.form.get("user_email")
        user_raz_soc = request.form.get("user_raz_soc")
        user_rep_legal_doc = request.form.get("user_rep_legal_doc")
        user_address = request.form.get("user_address")
        password = request.form.get("password")
        user_type = "G" 
        
        if not all([
            user_nombre_comercial, user_phone_number, user_document_type, user_document,
            user_province, user_postal_code, user_username, user_email, password
        ]):
            flash("Todos los campos obligatorios deben ser completados.", "error")
            return redirect(url_for('register_gastronomic_page'))
        
        if "@" not in user_email:
            flash("El correo electrónico debe tener un formato válido.", "error")
            return redirect(url_for('register_gastronomic_page'))
        
        if len(password) < 8:
            flash("La contraseña debe tener al menos 8 caracteres.", "error")
            return redirect(url_for('register_gastronomic_page'))
        
        existing_user = ConfirmedUser.query.filter(
            (ConfirmedUser.user_username == user_username)).first()
        if existing_user:
            flash('El nombre de usuario ya existe', 'error')
            return redirect(url_for('register_gastronomic_page'))
        
        existing_user = ConfirmedUser.query.filter(
            (ConfirmedUser.user_email == user_email)).first()
        
        if existing_user:
            flash('El correo electrónico ya está registrado', 'error')
            return redirect(url_for('register_gastronomic_page'))
        
        existing_user = ConfirmedUser.query.filter((ConfirmedUser.user_phone_number == user_phone_number)
        ).first()
        if existing_user:
            flash('El numero de telefono ya está registrado', 'error')
            return redirect(url_for('register_gastronomic_page'))
        
        potential_user = PotentialUser.query.filter((PotentialUser.user_phone_number == user_phone_number)
        ).first()
        if potential_user:
            flash('El numero de telefono ya está registrado', 'error')
            return redirect(url_for('register_gastronomic_page'))
        
        potential_user = PotentialUser.query.filter(
            (PotentialUser.user_username == user_username)).first()
        if potential_user:
            flash('El nombre de usuario ya está registrado', 'error')
            return redirect(url_for('register_gastronomic_page'))
        
        potential_user = PotentialUser.query.filter(
            (PotentialUser.user_email == user_email)).first()
        if potential_user:
            flash('El correo electrónico ya está registrado', 'error')
            return redirect(url_for('register_gastronomic_page'))
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        new_user = PotentialUser(
            user_nombre_comercial=user_nombre_comercial,
            user_phone_number=user_phone_number,
            user_document_type=user_document_type,
            user_document=user_document,
            user_rep_legal=user_rep_legal,
            user_province=user_province,
            user_postal_code=user_postal_code,
            user_username=user_username,
            user_email=user_email,
            user_raz_soc=user_raz_soc,
            user_rep_legal_doc=user_rep_legal_doc,
            user_address=user_address,
            password_hash=hashed_password,
            user_type=user_type,
            is_verified=False
        )

        new_confirmed_user = ConfirmedUser(
            user_nombre_comercial=user_nombre_comercial,
            user_phone_number=user_phone_number,
            user_document_type=user_document_type,
            user_document=user_document,

            user_rep_legal=user_rep_legal,
            user_province=user_province,
            user_postal_code=user_postal_code,
            user_username=user_username,
            user_email=user_email,
            user_raz_soc=user_raz_soc,
            user_rep_legal_doc=user_rep_legal_doc,
            user_address=user_address,
            password_hash=hashed_password,
            user_type=user_type,
            is_verified=False
        )

        db.session.add(new_user)
        db.session.add(new_confirmed_user)
        db.session.commit()
        
        owner_id = new_confirmed_user.id
        if not id:
            flash("Error: No se generó el ID del usuario confirmado.", "error")
            return redirect(url_for('register_gastronomic_page'))

        establecimiento = Establishments(
            est_name = user_nombre_comercial,
            est_owner_id = owner_id,
            est_address =  user_address,
            est_postal_code = user_postal_code,
            est_es_usuario = True,
            telefono = user_phone_number,
            mail = user_email,
            barrio = user_province,
        )

        db.session.add(establecimiento)
        db.session.commit()

        if app.config['TESTING'] == True:
            db.session.delete(new_confirmed_user)
            db.session.delete(new_user)
            db.session.commit()

        return redirect(url_for('confirm_page'))
    
@app.route('/confirm')
def confirm_page():
    return render_template('confirm.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@ns.route('/login')
class Login(Resource):
    def get(self):
        return render_template('login.html')
    
    def post(self):
        username_or_email = request.form.get("username")
        password = request.form.get("password")

        if not username_or_email or not password:
            flash("Ambos campos son obligatorios.", "error")
            return redirect(url_for('login_page'))
        
        user = ConfirmedUser.query.filter(
            (ConfirmedUser.user_username == username_or_email) | 
            (ConfirmedUser.user_email == username_or_email)
        ).first()

        if not user:
            flash("Usuario o correo no registrado.", "error")
            return redirect(url_for('login_page'))
        
        if not check_password_hash(user.password_hash, password):
            flash("Contraseña incorrecta.", "error")
            return redirect(url_for('login_page'))

        session['username'] = user.user_username 
        session["user_type"] = user.user_type
        session['user_id'] = user.id
        session['token'] = generate_token(user.user_username)
        session['Authorization'] = session['token']
        app.logger.debug(f'DEBUG>>>> Login for {session["token"]}, {session["user_id"]}, {session["user_type"]}, {session["username"]}')
        app.logger.debug(f'url for {url_for("api.meriendas_home")}')
        return redirect(url_for('home_page'))
        

@app.route('/home')
def home_page():
    try:
        data = decode_token(session['token'])
        if data['exp'] <= datetime.now(timezone.utc).timestamp():
            #token expired
            print(session['roto'])
            return redirect(url_for('Index'))
    except KeyError:
        session.clear()
        return redirect(url_for('Index'))
    app.logger.debug('Estoy en app./home con un GET')
    user_type = session.get("user_type")
    return render_template('home.html', user_type=user_type)

@ns.route("/home")
class Home(Resource):
    @token_required
    def get(self):
        app.logger.debug('Estoy en ns./home con un GET')
        user_type = session.get("user_type")
        return render_template('home.html', user_type=user_type)
    @token_required
    def push(self):
        # search = request.form.get("user_search")
        return redirect(url_for("search_page"))

@app.route('/search')
def search_page():
    try:
        data = decode_token(session['token'])
        if data['exp'] <= datetime.now(timezone.utc).timestamp():
            #token expired
            print(session['roto'])
            return redirect(url_for('Index'))
    except KeyError:
        session.clear()
        flash("No se puede buscar sin loguearte antes ;)", "error")
        return redirect(url_for('Index'))
    user_search = request.args.get('user_search')
    if user_search:
        return render_template('search_results.html', user_search=user_search)
    else:
        return "No se proporcionó ningún término de búsqueda."

@app.route('/logout')
def logout():
    session.clear()
    flash('Gracias por merendar! :)', 'info')
    return redirect(url_for('Index'))


@ns.route('/search')
class Search(Resource):
    @token_required
    def get(self):
        user_search = request.args.get('user_search')
        if user_search:
            return render_template('search_results.html', user_search=user_search)
        else:
            flash("No se proporciono un valor de busqueda valido", "error")
            return redirect(url_for('search_page'))
    @token_required
    def push(self):
        user_search = request.args.get('user_search')
        search_criteria = request.args.get('search_criteria')
        if user_search:
            if search_criteria == "postal_code":
                establishments = Establishments.query.filter(Establishments.est_postal_code == user_search)
            elif search_criteria == "neighborhood":
                establishments = Establishments.query.filter(Establishments.neighborhood == user_search)
            elif search_criteria == "name":
                establishments = Establishments.query.filter(Establishments.name.contains(user_search))
            elif search_criteria == "user":
                establishments = Establishments.query.filter(Establishments.user.contains(user_search))
            else:
                flash("Criterio de búsqueda no válido.", "error")
                return redirect(url_for('search_page'))
            
            if establishments:
                return render_template('search_results.html', establishments=establishments, user_search=user_search)
            else:
                flash("No se encontraron establecimientos para la busqueda", "error")
                return redirect(url_for('search_page'))
        else:
            flash("No se proporciono un valor de busqueda valido", "error")
            return redirect(url_for('search_page'))

@app.route('/user/<user>')
def user_page(user):
    """ 
    este es el que maneja el front
    """
    if 'username' not in session or user != session['username']:
        flash('Por favor logueate :D', 'error')
        return redirect(url_for('login_page'))
    try:
        data = decode_token(session['token'])
        if data['exp'] <= datetime.now(timezone.utc).timestamp():
            #token expired
            print(session['roto'])
            return redirect(url_for('Index'))
    except KeyError:
        session.clear()
        flash("No se puede buscar sin loguearte antes ;)", "error")
        return redirect(url_for('Index'))

    user_type = session.get("user_type")

    if user_type == "P":
        folders = Folders.query.filter_by(user_id=session['user_id']).all()
        return render_template('perfil.html', user_type=user_type, folders = folders, user=session['username'], session = session)
    
    if user_type == "G":
        est = Establishments.query.filter_by(est_owner_id=session['user_id']).all()
        app.logger.info(f"la query es - {est}, session_id = {session['user_id']}")
        if not est:
            flash('No se encontró un establecimiento para este usuario', 'error')
            return redirect(url_for('user_page', user=session['username']))

        return render_template('perfil.html', user_type=user_type, items=est, user=session['username'], session = session)

@ns.route('/user/<name>')
class UserProfile(Resource):
    @token_required
    def get(self, name):
        if 'username' not in session or name != session['username']:
            return redirect(url_for('login_page'))

        user_type = session.get("user_type")

        if user_type == "P":
            folders = Folders.query.filter_by(user_id=session['user_id']).all()
            return render_template('perfil.html', user_type=user_type, folders = folders, session = session['user_id'])
        
        if user_type == "G":
            est = Establishments.query.filter_by(est_owner_id=session['user_id']).all()
            app.logger.info(f"la query es - {est}, session_id = {session['user_id']}")
            if not est:
                flash('No se encontró un establecimiento para este usuario', 'error')
                return redirect(url_for('user_page', user=session['username']))

            return render_template('perfil.html', user_type=user_type, items=est, user=session['username'], session = session)

@app.route('/user/<user>/<folder>')
def folder_page(user, folder):
    if user != session['username']:
        flash('Por favor logueate antes :D', "error")
        return redirect(url_for('user_page'))
    try:
        data = decode_token(session['token'])
        if data['exp'] <= datetime.now(timezone.utc).timestamp():
            #token expired
            print(session['roto'])
            return redirect(url_for('Index'))
    except KeyError:
        session.clear()
        flash("No se puede buscar sin loguearte antes ;)", "error")
        return redirect(url_for('Index'))


    folder_data = Folders.query.filter_by(user_id=session['user_id'], folder_name=folder).first()
    if not folder_data:
        return "Carpeta no encontrada", 404

    return f"ESTA ES TU CARPETA: {folder_data.folder_name}"

@app.route('/user/create_folder',  methods=['GET', 'POST'])
def create_folder_page():
    try:
        data = decode_token(session['token'])
        if data['exp'] <= datetime.now(timezone.utc).timestamp():
            #token expired
            flash("No se puede buscar sin loguearte antes ;)", "error")
            return redirect(url_for('Index'))
    except KeyError:
        session.clear()
        flash("No se puede buscar sin loguearte antes ;)", "error")
        return redirect(url_for('Index'))

    if request.method == 'POST':
        folder_name = request.form.get("folder_name")
        exclusive = request.form.get("exclusive")

        if not all([folder_name, exclusive]):
            flash('Todos los campos son obligatorios', 'error')
            return redirect(url_for('create_folder_page'))

        carpeta = Folders(
            user_id=session['user_id'],
            folder_name=folder_name,
            editable=True,
            exclusive=bool(exclusive)
        )

        db.session.add(carpeta)
        db.session.commit()

        if app.config['TESTING'] == True:
            db.session.add(carpeta)
            db.session.commit()

        return redirect(url_for('user_page', user=session['username']))
    
    return render_template('create_folder.html')

@app.route('/user/create_menu_item',  methods=['GET', 'POST'])
def create_menu_item():
    try:
        data = decode_token(session['token'])
        if data['exp'] <= datetime.now(timezone.utc).timestamp():
            #token expired
            flash("No se puede buscar sin loguearte antes ;)", "error")
            return redirect(url_for('Index'))
    except KeyError:
        session.clear()
        flash("No se puede buscar sin loguearte antes ;)", "error")
        return redirect(url_for('Index'))

    if request.method == 'POST':
        item_name = request.form.get("item_name")
        item_description = request.form.get("item_description")
        item_price = request.form.get("item_price")

        if not all([item_name, item_description, item_price]):
            flash('Todos los campos son obligatorios', 'error')
            return redirect(url_for('create_menu_item_page'))
        
        est = Establishments.query.filter_by(est_owner_id = session.get('user_id')).first()
        
        if est is None:
            flash('No se encontró un establecimiento para este usuario', 'error')
            return redirect(url_for('create_menu_item_page'))
        
        est_id = est.id

        item = MenuItems(
            est_id = est_id,
            item_name = item_name,
            item_description = item_description,
            item_price = item_price
        )

        db.session.add(item)
        db.session.commit()
        print(f"Item creado: {item.item_name}, ID: {item.menu_id}, Establecimiento: {item.est_id}")


        if app.config['TESTING'] == True:
            db.session.add(item)
            db.session.commit()

        return redirect(url_for('user_page', user=session['username']))
    
    return render_template('create_item.html')

token_request = api.model(
    "Token Request" , {
        "username": fields.String(required=True, description="Nombre de usuario"),
        "password=": fields.Nested(user, description="El usuario"),
    }
)

@ns.route('/gettoken')
class GetToken(Resource):
    @ns.expect(token_request)
    @ns.marshal_with(token_request)
    def post(self):
        pass

# @ns.route('/user/create_folder')
# class CreateFolder(Resource):
#     def get(self):
#         return render_template('create_folder.html')

#     def post(self):
#         folder_name = request.form.get("folder_name")
#         exclusive = request.form.get("exclusive")

#         if not all([folder_name, exclusive]):
#             flash('Todos los campos son obligatorios', 'error')
#             return redirect(url_for('create_folder_page'))

#         carpeta = Folders(
#             user_id=session['user_id'],
#             folder_name=folder_name,
#             editable=True,
#             exclusive=bool(exclusive)
#         )

#         db.session.add(carpeta)
#         db.session.commit()

#         if app.config['TESTING'] == True:
#             db.session.add(carpeta)
#             db.session.commit()

#         return redirect(url_for('user_page', user=session['username']))


##----------------------------------------------------------------------------------------
# UTILS
#-----------------------------------------------------------------------------------------
def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.secret_key)
    return serializer.dumps(email, salt=config.Config.SECURITY_PASSWORD_SALT)

