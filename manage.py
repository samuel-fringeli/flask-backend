#!/usr/bin/env python
import os
from app import create_app, db
from app.models import User, Role, Reservation, Room, Timeslot, Weekday, reservations_users, reservations_timeslots, Item, Item_Type
from flask_script import Manager, Shell, Server
from flask_migrate import Migrate, MigrateCommand

# génération schéma relationnel
try:
    import sadisplay
except:
    print("Impossible de charger le module sadisplay ==> génération du modèle relationnel impossible")

# interface d'administration
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

try:
    from data.utils import extract_sigles, extract_timeslots, extract_rooms
    from load_csv import load_teachers, load_reservations, load_items
except:
    print('Impossible de charger les données')

# On passe les modèles à la création de l'application pour pouvoir y initialiser Flask-Restless 
models = dict(
    User=User,
    Role=Role,
    Reservation=Reservation,
    Room=Room,
    Timeslot=Timeslot,
    Weekday=Weekday
)

app = create_app(os.getenv('FLASK_CONFIG') or 'default', models)
# une page qui s'affiche à chaque redirection en mode développement
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

manager = Manager(app)
migrate = Migrate(app, db)

# initialisation de Admin
admin = Admin(app, name='CSUD Réservation : admin', template_mode='bootstrap3')

for model in models.values():
    admin.add_view(ModelView(model, db.session))


def make_shell_context():
    preloaded = dict(app=app, db=db)
    preloaded.update(models)
    print(preloaded)
    return preloaded
    

if os.getenv('C9_HOSTNAME'):
    manager.add_command("runserver", Server(
        host=os.getenv('C9_IP'),
        port=os.getenv('C9_PORT')
    ))
    print("App started on Cloud9, available on", 'https://' + os.getenv('C9_HOSTNAME'))


manager.add_command("shell", Shell(make_context=make_shell_context, use_ipython=True))
manager.add_command('db', MigrateCommand)

tmp_timetable_txt = "data/timetable.txt"
tmp_rooms_txt = "data/rooms.txt"
@manager.command
def txt(input_pdf, out_txt):
    try:
        from sh import pdf2txt, rm
    except:
        print("impossible d'exécuter la commande pdf2txt nécessaire à la conversion du fichier. Installer d'abord le package python pdf miner avec sudo apt-get install python-pdfminer")
        
    pdf2txt(input_pdf, _out = out_txt)


    
    
@manager.command
def initdb():
    db.drop_all()
    db.create_all()
    
    timeslots = extract_timeslots()
    rooms = extract_rooms()
    sigles = extract_sigles()
    teachers_edt = load_teachers('data/teachers_edt.csv')
    teachers_admin = load_teachers('data/teachers_admin.csv')
    
    items = load_items()
    
    # auto data loading from different datasources
    Timeslot.insert_timeslots(timeslots)
    Weekday.insert_days()
    Role.insert_roles()
    User.insert_admin()
    User.insert_teachers(teachers_edt, teachers_admin)
    Room.insert_rooms(rooms)
    
    Item_Type.insert_item_types()
    
    Item.insert_items(items)
    
    
    
@manager.command
def erd():
    ''' outputs entity relationship diagram into erd.png '''
    try:
        from sh import eralchemy, mv
        eralchemy('-i', app.config['SQLALCHEMY_DATABASE_URI'], '-o', 'app/static/erd.png')
    except ImportError as e:
        print(str(e))  
        

@manager.command
def rel(file_format):
    ''' outputs relational diagram into rel.png '''
    try:
        from sh import dot, cp
        desc = sadisplay.describe([
            User,
            Role,
            Reservation,
            Room,
            Timeslot,
            Weekday,
            reservations_users,
            reservations_timeslots
        ])
        with open('schema.dot', 'w', encoding='utf-8') as f:
            f.write(sadisplay.dot(desc))
            
        
        dot("-T"+file_format, "schema.dot", "-o", "app/static/rel."+file_format)
        
        
    except ImportError as e:
        print(str(e))

@manager.command
def sqldump():
    from sqlalchemy import create_engine
    from sqlalchemy.schema import CreateTable
    
    models = [User, Role, Reservation, Room, Timeslot, Weekday]
    association_tables = [reservations_users, reservations_timeslots]

    sql_url = app.config['SQLALCHEMY_DATABASE_URI']
    db_engine = create_engine(sql_url)
    
    with open('app/static/data-dev-ddl.sql', 'w') as fd:
        for model in models:
            sql_ddl = CreateTable(model.__table__).compile(db_engine)
            sql_ddl = str(sql_ddl).strip()
            fd.write(str(sql_ddl)  + ';\n\n')
        for table in association_tables:
            sql_ddl = CreateTable(table).compile(db_engine)
            sql_ddl = str(sql_ddl).strip()
            fd.write(str(sql_ddl)  + ';\n\n')
            
    try:
        from sh import c9
        c9('app/static/data-dev-ddl.sql')
    except:
        pass
    

@manager.command
def clean():
    files = [
        'rel.*',
        'schema.*'
    ]
    
    from sh import rm
            
    for file in files:
        rm("-f", file)
    

@manager.command
def load(data_file='data/edt.csv'):
    from datetime import date
    """ Loads data from CSV file generated by EDT (Emploi Du Temps) """
    load_reservations(
        db,
        start_date=date(2016, 8, 29), 
        end_date=date(2017, 6, 30),
        filename=data_file)
    

@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)



if __name__ == '__main__':
    manager.run()

