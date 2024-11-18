from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String,Float, Text, Date, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import VARCHAR, BLOB
from datetime import datetime

db = SQLAlchemy()

class ConfirmedUser(db.Model):
    __tablename__ = "USERS"

    ##comun a ambos
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_phone_number = Column(VARCHAR(15),unique=True, nullable=False)
    user_email = Column(VARCHAR(200), unique=True, nullable=False)
    user_province = Column(VARCHAR(100)) 
    user_postal_code = Column(VARCHAR(10))
    user_username = Column(VARCHAR(50), unique=True, nullable=False)  
    password_hash = Column(VARCHAR(255), nullable=False)
    user_type = Column(VARCHAR(10), nullable=False)
    is_verified = Column(Boolean, default=False)
    bio = Column(Text)
    profile_pictures = relationship("ProfilePicture", back_populates="user_confirmed", cascade="all, delete-orphan")

    ##personal
    user_first_name = Column(VARCHAR(100))  
    user_last_name = Column(VARCHAR(100)) 
    date_of_birth = Column(Date)  
    gender = Column(VARCHAR(20))
    user_document_type = Column(VARCHAR(20))  
    user_document = Column(VARCHAR(50))   

    ##gastro
    user_nombre_comercial =  Column(VARCHAR(100)) 
    user_raz_soc =  Column(VARCHAR(100)) 
    user_cuit = Column(Integer)
    user_rep_legal =  Column(VARCHAR(100)) 
    user_rep_legal_doc =  Column(VARCHAR(100)) 
    user_address = Column(VARCHAR(255))  
      
class PotentialUser(db.Model):
    __tablename__ = "POTENTIAL_USERS"

    ##comun a ambos
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_phone_number = Column(VARCHAR(15),unique=True, nullable=False)
    user_email = Column(VARCHAR(200), unique=True, nullable=False)
    user_province = Column(VARCHAR(100)) 
    user_postal_code = Column(VARCHAR(10))
    user_username = Column(VARCHAR(50), unique=True, nullable=False)  
    password_hash = Column(VARCHAR(255), nullable=False)
    user_type = Column(VARCHAR(10), nullable=False)
    is_verified = Column(Boolean, default=False)
    bio = Column(Text)
    profile_pictures = relationship("ProfilePicture", back_populates="user_potential", cascade="all, delete-orphan")

    ##personal
    user_first_name = Column(VARCHAR(100))  
    user_last_name = Column(VARCHAR(100)) 
    date_of_birth = Column(Date)  
    gender = Column(VARCHAR(20))
    user_document_type = Column(VARCHAR(20))  
    user_document = Column(VARCHAR(50))   

    ##gastro
    user_nombre_comercial =  Column(VARCHAR(100)) 
    user_raz_soc =  Column(VARCHAR(100)) 
    user_cuit = Column(Integer)
    user_rep_legal =  Column(VARCHAR(100)) 
    user_rep_legal_doc =  Column(VARCHAR(100)) 
    user_address = Column(VARCHAR(255))  

class Folders(db.Model):
    __tablename__ = "USER_FOLDERS"

    folder_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('USERS.id'))
    folder_name = Column(VARCHAR(200), nullable=False)
    editable = Column(Boolean, default=False)
    exclusive = Column(Boolean, default=False)

class MenuItems(db.Model):
    __tablename__ = "MENU_ITEMS"

    menu_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('USERS.id'))
    item_name = Column(VARCHAR(200), nullable=False)
    item_description = Column(VARCHAR(200))
    item_price = Column(Float)
    item_photo = relationship("ProfilePicture", back_populates="user_potential", cascade="all, delete-orphan")
class SavedItems(db.Model):
    __tablename__ = "USER_SAVED_ITEMS"

    saved_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('USERS.id'))
    menu_id = Column(Integer, ForeignKey('MENU_ITEMS.menu_id'))
    folder_id =  Column(Integer, ForeignKey('USER_FOLDERS.folder_id'))

class Reviews(db.Model):
    __tablename__ = "USER_REVIEWS"

    review_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('USERS.id'))
    menu_id = Column(Integer, ForeignKey('MENU_ITEMS.menu_id'))
    review_rating = Column(Float)
    review_comment = Column(VARCHAR(2000))

class ProfilePicture(db.Model):
    __tablename__ = "PROFILE_PICTURES"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    confirmed_user_id = Column(Integer, ForeignKey('USERS.id'), nullable=True)
    potential_user_id = Column(Integer, ForeignKey('POTENTIAL_USERS.id'), nullable=True)
    
    image_data = Column(BLOB, nullable=False)
    file_name = Column(VARCHAR(255), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    user_confirmed = relationship("ConfirmedUser", back_populates="profile_pictures")
    user_potential = relationship("PotentialUser", back_populates="profile_pictures")

class MenuPicture(db.Model):
    __tablename__ = "MENU_ITEM_PICTURE"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id =  Column(Integer, ForeignKey('MENU_ITEMS.menu_id'))
    image_data = Column(BLOB, nullable=False)
    file_name = Column(VARCHAR(255), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    menu_item = relationship("MenuItem", back_populates="profile_pictures")
    