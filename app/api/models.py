from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, Date, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import VARCHAR, BLOB
from datetime import datetime

db = SQLAlchemy()

class ConfirmedUser(db.Model):
    __tablename__ = "USERS"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow)  # Fecha de creación de cuenta
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_first_name = Column(VARCHAR(100), nullable=False)  
    user_last_name = Column(VARCHAR(100), nullable=False) 
    date_of_birth = Column(Date, nullable=False)  
    gender = Column(VARCHAR(20), nullable=True)  
    user_phone_number = Column(VARCHAR(15), unique=False, nullable=False)
    user_document_type = Column(VARCHAR(20), nullable=False)  
    user_document = Column(VARCHAR(50), unique=True, nullable=False)  
    user_email = Column(VARCHAR(200), unique=True, nullable=False)
    user_username = Column(VARCHAR(50), unique=True, nullable=False)  
    password_hash = Column(VARCHAR(255), nullable=False)
    user_type = Column(VARCHAR(10), unique=True, nullable=False)
    is_verified = Column(Boolean, default=False)
    bio = Column(Text, nullable=True)
    profile_pictures = relationship("ProfilePicture", back_populates="user_confirmed", cascade="all, delete-orphan")

class PotentialUser(db.Model):
    __tablename__ = "POTENTIAL_USERS"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow)  # Fecha de creación de cuenta
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_first_name = Column(VARCHAR(100), nullable=False)  
    user_last_name = Column(VARCHAR(100), nullable=False) 
    date_of_birth = Column(Date, nullable=False)  
    gender = Column(VARCHAR(20), nullable=True)  
    user_phone_number = Column(VARCHAR(15), unique=False, nullable=False)
    user_document_type = Column(VARCHAR(20), nullable=False)  
    user_document = Column(VARCHAR(50), unique=True, nullable=False)  
    user_email = Column(VARCHAR(200), unique=True, nullable=False)
    user_username = Column(VARCHAR(50), unique=True, nullable=False)  
    password_hash = Column(VARCHAR(255), nullable=False)
    user_type = Column(VARCHAR(10), nullable=False)
    is_verified = Column(Boolean, default=False)
    bio = Column(Text, nullable=True)
    profile_pictures = relationship("ProfilePicture", back_populates="user_potential", cascade="all, delete-orphan")

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