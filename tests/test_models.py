
from sqlalchemy import exc
from app.api.models import *
from app.api import db, app, engine
import pytest
from werkzeug.security import generate_password_hash


# Fixtures
# Estos fixtures los hago para crear el elemento y luego presentarlo para el test
# y luego del yield (el yield presenta el objeto al test) puedo borrar el elemento de la db

@pytest.fixture
def Confirmeduserfixture():
    user = ConfirmedUser(
            user_nombre_comercial   = "Mi nombre",
            user_phone_number       = "Un Numero de telefono que no deberia ser un string",
            user_document_type      = 12345674,
            user_document           = "DNI",

            user_rep_legal          = "Representante legal",
            user_province           = "Una provincia que no existe",
            user_postal_code        = 2300,
            user_username           = 'nico',
            user_email              = 'un mail ilegal@gmail.com',
            user_raz_soc            = 'Test S.A',
            user_rep_legal_doc      = 'No me acuerdo que hace este field',
            user_address            = 'Una direccion',
            password_hash           = generate_password_hash('patito123', method='pbkdf2:sha256', salt_length=16),
            user_type               = "user_type",
            is_verified             = True
        )
    with app.app_context():
        db.session.add(user)
        db.session.commit()
        yield user
        db.session.delete(user)
        db.session.commit()

@pytest.fixture
def Potentialuserfixture():
    user = PotentialUser(
            user_nombre_comercial   = "Mi nombre",
            user_phone_number       = "Un Numero de telefono que no deberia ser un string",
            user_document_type      = 12345674,
            user_document           = "DNI",
            user_rep_legal          = "Representante legal",
            user_province           = "Una provincia que no existe",
            user_postal_code        = 2300,
            user_username           = 'nico',
            user_email              = 'un mail ilegal@gmail.com',
            user_raz_soc            = 'Test S.A',
            user_rep_legal_doc      = 'No me acuerdo que hace este field',
            user_address            = 'Una direccion',
            password_hash           = generate_password_hash('patito123', method='pbkdf2:sha256', salt_length=16),
            user_type               = "user_type",
            is_verified             = True
        )
    with app.app_context():
        db.session.add(user)
        db.session.commit()
        yield user
        db.session.delete(user)
        db.session.commit()


@pytest.fixture
def Establishmentfixture(Confirmeduserfixture):
    establishment = Establishments(
            est_name                =   'Muchas eñes :ñandú',
            est_desc                =   "Description del coso",
            est_owner_id            =   Confirmeduserfixture.id,
            est_address              =   "Calle Falsa 123",
            est_postal_code         =   "23400",
            est_es_usuario          =   True,
            long                    =   2300,
            lat                     =   1000,
            categoria               =   "Pato",
            cocina                  =   "Parrilla",
            ambientacion            =   "huele a viejo",
            telefono                =   123455,
            mail                    =   "pajarito@gmail.com",
            horario                 =   "de 2 a 4",
            calle_nombre            =   "Falsa",
            calle_altura            =   "123",
            calle_cruce             =   "Entre moreno y lincoln",
            barrio                  =   "No se",
            comuna                  =   "Aca en provincia no hay comunas"
    )
    with app.app_context():
        db.session.add(establishment)
        db.session.commit()
        yield establishment
        db.session.delete(establishment)
        db.session.commit()

@pytest.fixture
def Foldersfixture(Confirmeduserfixture):
    folder = Folders(
        user_id         = Confirmeduserfixture.id,
        folder_name     = "A Folder Name",
        editable        = True,
        exclusive       = True
    )
    with app.app_context():
        db.session.add(folder)
        db.session.commit()
        yield folder
        db.session.delete(folder)
        db.session.commit()

@pytest.fixture
def Menuitemsfixture(Establishmentfixture):
    menu_item = MenuItems(
        est_id              =   Establishmentfixture.id,
        item_name           =   "Pato a la naranja",
        item_description    =   "Un pato marinado con una naranja",
        item_price          =   41321.2
    )
    with app.app_context():
        db.session.add(menu_item)
        db.session.commit()
        yield menu_item
        db.session.delete(menu_item)
        db.session.commit()

@pytest.fixture
def Saveditemsfixture(Confirmeduserfixture,Menuitemsfixture,Foldersfixture):
    saved_item = SavedItems(
        user_id             =   Confirmeduserfixture.id,
        menu_id             =   Menuitemsfixture.menu_id,
        folder_id           =   Foldersfixture.folder_id
    )
    with app.app_context():
        db.session.add(saved_item)
        db.session.commit()
        yield saved_item
        db.session.delete(saved_item)
        db.session.commit()

@pytest.fixture
def Reviewsfixture(Confirmeduserfixture,Menuitemsfixture):
    review = Reviews(
        user_id             = Confirmeduserfixture.id,
        menu_id             =  Menuitemsfixture.menu_id,
        review_rating       = 2.9,
        review_comment      = "El pato era una paloma y la naranja era una mandarina"
    )
    with app.app_context():
        db.session.add(review)
        db.session.commit()
        yield review
        db.session.delete(review)
        db.session.commit()

@pytest.fixture(autouse=True)
def cleanup_db(monkeypatch):
    """
    Teardown de los cambios que hago con la base de datos
    """

    def teardown():
        db.session.rollback()

    monkeypatch.setattr(db.session, 'rollback', teardown)
    yield


def test_create_confirmed_user(Confirmeduserfixture):
    assert Confirmeduserfixture.id is not None

def test_confirmed_user_data_empty():
    user = ConfirmedUser()
    with pytest.raises(exc.IntegrityError):
        with app.app_context():
            db.session.add(user)
            db.session.commit()


def test_create_potential_user(Potentialuserfixture):
    assert Potentialuserfixture.id is not None

def test_create_establishment(Establishmentfixture):
    assert Establishmentfixture is not None

def test_create_folder(Foldersfixture):
    assert Foldersfixture is not None

def test_crete_menu_item(Menuitemsfixture):
    assert Menuitemsfixture is not None

def test_create_saved_item(Saveditemsfixture):
    assert Saveditemsfixture is not None

def test_create_profile_pic_with_confirmed(Confirmeduserfixture):
    pf = ProfilePicture(
        confirmed_user_id   = Confirmeduserfixture.id,
        image_data          = b'test_image_data',
        file_name           = 'test_image.jpg'
    )
    db.session.add(pf)
    db.session.flush()

    assert pf.id is not None
    assert pf.confirmed_user_id == Confirmeduserfixture.id
    assert pf.user_confirmed is Confirmeduserfixture

def test_create_profile_pic_with_potential(Potentialuserfixture):
    pf = ProfilePicture(
        potential_user_id   = Potentialuserfixture.id,
        image_data          = b'test_image_data',
        file_name           = 'test_image.jpg'
    )
    db.session.add(pf)
    db.session.flush()
    
    assert pf.id is not None
    assert pf.potential_user_id == Potentialuserfixture.id
    assert pf.user_potential is Potentialuserfixture

def test_create_profile_picture_missing_data():
    """
    Muestra que esto se rompe con un integrity error si
    creamos una profilepic vacia
    """
    profile_picture = ProfilePicture()

    with pytest.raises(exc.IntegrityError):
        with app.app_context():
            db.session.add(profile_picture)
            db.session.commit()

def test_update_profile_picture(Confirmeduserfixture):
    """
    Testea update de user profile
    """
    profile_picture = ProfilePicture(
        confirmed_user_id=Confirmeduserfixture.id,
        image_data=b"test_image_data",
        file_name="test_image.jpg",
    )

    db.session.add(profile_picture)
    db.session.commit()

    profile_picture.image_data = b"Ahoralafotoesdistinta"
    profile_picture.file_name = "updated_image.png"

    db.session.commit()

    fetched_picture = ProfilePicture.query.get(profile_picture.id)

    assert fetched_picture.image_data == b"Ahoralafotoesdistinta"