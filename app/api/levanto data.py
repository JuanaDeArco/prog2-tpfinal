import pandas as pd 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Establishments

df = pd.read_csv("C:/Users/Usuario/prog2-tpfinal/app/assets/static/data/ARCHIVO.csv")
print(df)
df = df.where(pd.notnull(df), None)

df['codigo_postal'] = df['codigo_postal'].fillna(0).astype(float)
df['calle_altura'] = df['calle_altura'].fillna(0).astype(float)


engine = create_engine("mysql+pymysql://root:Luchi0803@127.0.0.1/test")
Session = sessionmaker(bind=engine)
session = Session()

for index, row in df.iterrows():
    try:
        establishment = Establishments(
            est_name=row['nombre'],
            est_address=row['direccion_completa'],
            est_postal_code=row['codigo_postal'],
            est_es_usuario=False,
            long=row['long'],
            lat=row['lat'],
            categoria=row['categoria'],
            cocina=row['cocina'],
            ambientacion=row['ambientacion'],
            telefono=row['telefono'],
            mail=row['mail'],
            horario=row['horario'],
            calle_nombre=row['calle_nombre'],
            calle_altura=row['calle_altura'],
            calle_cruce=row['calle_cruce'],
            barrio=row['barrio'],
            comuna=row['comuna']
        )
        session.add(establishment)
    except Exception as e:
        pass
session.commit()
session.close()