"""
Este es el codigo de la api
"""
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash, current_app
from flask_restx import Api, Resource, fields, Namespace
from . import api, app
from app.src import Roles
from .Auth import decode_token, generate_token
from .models import db, ConfirmedUser, PotentialUser, Folders, Establishments, MenuItems, SavedItems
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message
import os
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

        session["username"] = user.user_username 
        session["user_type"] = user.user_type
        session['user_id'] = user.id
        return redirect(url_for('home_page'))

@app.route('/home')
def home_page():
    user_type = session.get("user_type")
    return render_template('home.html', user_type=user_type)

@ns.route("home")
class Home(Resource):
    def get(self):
        user_type = session.get("user_type")
        return render_template('home.html', user_type=user_type)
    def push(self):
        # search = request.form.get("user_search")
        return redirect(url_for("search_page"))

@app.route('/search', methods=['GET', 'POST'])
def search_page():
    user_search = request.args.get('user_search') or request.form.get('user_search')
    search_criteria = request.args.get('search_criteria') or request.form.get('search_criteria')

    if not user_search:
        flash("No se proporcionó ningún término de búsqueda.", "error")
        return render_template('search_results.html', establishments=[], user_search="")

    if not search_criteria:
        flash("No se proporcionó un criterio de búsqueda.", "error")
        return render_template('search_results.html', establishments=[], user_search=user_search)

    results = []
    if search_criteria == "postal_code":
        results = Establishments.query.filter(Establishments.est_postal_code.ilike(f"%{user_search}%")).all()
    elif search_criteria == "neighborhood":
        results = Establishments.query.filter(Establishments.barrio.ilike(f"%{user_search}%")).all()
    elif search_criteria == "name":
        results = Establishments.query.filter(Establishments.est_name.ilike(f"%{user_search}%")).all()
    elif search_criteria == "user":
        results = ConfirmedUser.query.filter(ConfirmedUser.user_username.ilike(f"%{user_search}%")).all()
    elif search_criteria == "item":
        results = (
            db.session.query(MenuItems, Establishments)
            .join(Establishments, MenuItems.est_id == Establishments.id)
            .filter(MenuItems.item_name.ilike(f"%{user_search}%"))
            .all()
        )
    else:
        flash("Criterio de búsqueda no válido.", "error")
        return redirect(url_for('search_page'))

    if not results:
        flash("No se encontraron resultados.", "warning")
    return render_template('search_results.html', establishments=results, user_search=user_search, search_criteria = search_criteria)

@ns.route('/search')
class Search(Resource):
    def get(self):
        user_search = request.args.get('user_search')
        if user_search:
            return render_template('search_results.html', user_search=user_search)
        else:
            flash("No se proporciono un valor de busqueda valido", "error")
            return redirect(url_for('search_page'))
    def push(self):
        user_search = request.args.get('user_search')
        search_criteria = request.args.get('search_criteria')
        if user_search:
            if search_criteria == "postal_code":
                results = Establishments.query.filter(Establishments.est_postal_code.ilike(str(user_search))).all()
            elif search_criteria == "neighborhood":
                results = Establishments.query.filter(Establishments.barrio.ilike(user_search)).all()
            elif search_criteria == "name":
                results = Establishments.query.filter(Establishments.est_name.ilike(user_search)).all()
            elif search_criteria == "user":
                results = ConfirmedUser.query.filter(ConfirmedUser.user_username.ilike(user_search)).all()
            elif search_criteria == "item":
                results = MenuItems.query.filter(MenuItems.item_name.ilike(user_search)).all()
            else:
                flash("Criterio de búsqueda no válido.", "error")
                return redirect(url_for('search_page'))
            
            if results:
                return render_template('search_results.html', establishments=results, user_search=user_search)
            else:
                flash("No se encontraron establecimientos para la busqueda", "error")
                return redirect(url_for('search_page'))
        else:
            flash("No se proporciono un valor de busqueda valido", "error")
            return redirect(url_for('search_page'))
        
@app.route('/establecimiento/<user>')
def user_public_page(user):
    """ 
    este es el que maneja el front
    """
    establecimiento = Establishments.query.filter_by(est_name=user).first()
    est_id = establecimiento.id
    menu = MenuItems.query.filter_by(est_id = est_id).all()
    if not establecimiento:
        flash('No se encontró un establecimiento para este usuario', 'error')
        return redirect(url_for('user_public_page', user=user))

    return render_template('perfil_public.html', items=menu, user=user, session = est_id)

@app.route('/establecimiento/<user>/item/<item>')
def item_public_page(user, item):
    est = Establishments.query.filter_by(est_name=user).first()
    est_id = est.id
    menu = MenuItems.query.filter_by(est_id = est_id, item_name = item ).first()
    if not menu:
        return "No hay un item con ese nombre", 404

    return render_template('item_public_details.html', item=menu)

@app.route("save_item/<item>/<establecimiento>",methods=["GET", "POST"])
def save_item_page(item,establecimiento):
    folders = Folders.query.filter_by(user_id=session['user_id']).all()
    if request.method == "POST":
        folder_id = request.form.get("folder_id")
        menu_item = MenuItems.query.filter_by(est_id = establecimiento, item_name=item).first()

        if not folder_id or not menu_item:
            flash("Carpeta o ítem inválido.", "error")
            return redirect(url_for("save_item_page", item=item, establecimiento=establecimiento))

        saved_item = SavedItems(
            user_id=session['user_id'],
            menu_id=menu_item.menu_id,
            folder_id=folder_id
        )
        db.session.add(saved_item)
        db.session.commit()

        flash("Ítem guardado con éxito.", "success")
        return redirect(url_for("user_page", user=session["username"]))

    # Renderizar el formulario con carpetas
    return render_template(
        "save_item.html",
        item=item,
        establecimiento=establecimiento,
        folders=folders
    )

@app.route('/user/<user>')
def user_page(user):
    """ 
    este es el que maneja el front
    """
    if 'username' not in session or user != session['username']:
        return redirect(url_for('login_page'))

    user_type = session.get("user_type")

    if user_type == "P":
        folders = Folders.query.filter_by(user_id=session['user_id']).all()
        return render_template('perfil.html', user_type=user_type, folders = folders, user=session['username'], session = session)
    
    if user_type == "G":
        est = Establishments.query.filter_by(est_owner_id=session['user_id']).first()
        est_id = est.id
        menu = MenuItems.query.filter_by(est_id = est_id).all()
        if not est:
            flash('No se encontró un establecimiento para este usuario', 'error')
            return redirect(url_for('user_page', user=session['username']))

        return render_template('perfil.html', user_type=user_type, items=menu, user=session['username'], session = est_id)

@ns.route('/user/<name>')
class UserProfile(Resource):
    def get(self, name):
        if 'username' not in session or name != session['username']:
            return redirect(url_for('login_page'))

        user_type = session.get("user_type")

        if user_type == "P":
            folders = Folders.query.filter_by(user_id=session['user_id']).all()
            return render_template('perfil.html', user_type=user_type, folders = folders, session = session['user_id'])
        
        if user_type == "G":
            est = Establishments.query.filter_by(est_owner_id=session['user_id']).first()
            est_id = est.id
            menu = MenuItems.query.filter_by(est_id = est_id).all()
            if not est:
                flash('No se encontró un establecimiento para este usuario', 'error')
                return redirect(url_for('user_page', user=session['username']))

            return render_template('perfil.html', user_type=user_type, items=menu, user=session['username'], session = est_id)

@app.route('/user/<user>/folder/<folder>')
def folder_page(user, folder):
    if user != session['username']:
        return redirect(url_for('user_page'))

    folder_data = Folders.query.filter_by(user_id=session['user_id'], folder_name=folder).first()
    if not folder_data:
        return "Carpeta no encontrada", 404

    return f"ESTA ES TU CARPETA: {folder_data.folder_name}"

@app.route('/user/create_folder',  methods=['GET', 'POST'])
def create_folder_page():
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

@app.route('/user/<user>/item/<item>')
def item_page(user, item):
    if user != session['username']:
        return redirect(url_for('user_page'))

    est = Establishments.query.filter_by(est_owner_id=session['user_id']).first()
    est_id = est.id
    menu = MenuItems.query.filter_by(est_id = est_id, item_name = item ).first()
    if not menu:
        return "No hay un item con ese nombre", 404

    return render_template('item_details.html', item=menu, user=user)

@app.route('/edit_item/<item>', methods=['GET', 'POST'])
def edit_item_page(item):
    if request.method == 'POST':

        new_name = request.form.get('item_name')
        new_description = request.form.get('item_description')
        new_price = request.form.get('item_price')

        est = Establishments.query.filter_by(est_owner_id=session['user_id']).first()
        est_id = est.id

        menu_item = MenuItems.query.filter_by(item_name=item, est_id = est_id).first()
        if not menu_item:
            return "No se encontró el ítem para editar", 404
        if new_name:
            menu_item.item_name = new_name
        if new_description:
            menu_item.item_description = new_description
        if new_price:
            menu_item.item_price = float(new_price)

        db.session.commit()

        flash('Ítem actualizado con éxito', 'success')
        return redirect(url_for('item_page', user=session['username'], item=new_name))

    menu_item = MenuItems.query.filter_by(item_name=item).first()
    if not menu_item:
        return "No se encontró el ítem para editar", 404

    return render_template('edit_item.html', item=menu_item)

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

