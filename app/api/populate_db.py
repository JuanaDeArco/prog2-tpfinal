import pandas as pd 
from ..src import iterator
import numpy as np

def populate_table_from_csv(csv_path, model_class, db_session):
    df = pd.read_csv(csv_path, na_values='0')
    df = df.where(pd.notnull(df), None)

    if 'codigo_postal' in df.columns:
        df['codigo_postal'] = df['codigo_postal'].fillna(0).astype(float)
    if 'calle_altura' in df.columns:
        df['calle_altura'] = df['calle_altura'].fillna(0).astype(float)
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.fillna(0)
    

    for row in iterator.DataFrameIterator(csv_path):
        try:
            establishment = model_class(
                est_name=row['nombre'],
                est_address=row['direccion_completa'],
                est_postal_code=row['codigo_postal'],
                est_es_usuario=False,
                long=row['long'],
                lat=row['lat'],
                categoria=row['categoria'],
                cocina=row['cocina'],
                ambientacion=row['ambientacion'],
                telefono=str(row['telefono']).replace(' ','').split('/')[0],
                mail=row['mail'],
                horario=row['horario'],
                calle_nombre=row['calle_nombre'],
                calle_altura=row['calle_altura'],
                calle_cruce=row['calle_cruce'],
                barrio=row['barrio'],
                comuna=row['comuna']
            )
        except Exception as e:
            print(f'Falla {row} | {e} ')
            continue
        try:
            db_session.add(establishment)
        except Exception as e:
            print(f'Falla {row} | {e} ')
            continue
    try:
        db_session.commit()
    except Exception as e:
        pass

        