from sqlalchemy import Table, MetaData, create_engine, Column, Integer, String, Float, DateTime, ForeignKey, event
from sqlalchemy.orm import scoped_session, sessionmaker, backref, relation
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import json


Base = declarative_base()


def add(data):
    with open('db.setting.json') as f:
        db_setting = json.load(f)
    dbengine = create_engine(db_setting['db_connection'], echo = True)
    Base = declarative_base()
    if not dbengine.dialect.has_table(dbengine, db_setting['table_name']):  # If table don't exist, Create.
        metadata = MetaData(dbengine)
        create_table(metadata,dbengine,db_setting['table_name'])
    Session = sessionmaker(bind=dbengine)
    session = Session()

    data = json.loads(data)
    
    for source, rate in data['dolarpy'].items():
        rateHistory = RateHistory(compra=rate['compra'], venta=rate['venta'], source=source, updateDateTime=data['updated'])
        session.add(rateHistory)
        session.commit()
    session.close()

def update(id , rateHistory):
    with open('db.setting.json') as f:
        db_setting = json.load(f)
    dbengine = create_engine(db_setting['db_connection'], echo = True)
    Base = declarative_base()
    if not dbengine.dialect.has_table(dbengine, db_setting['table_name']):  # If table don't exist, Create.
        return False 
    Session = sessionmaker(bind=dbengine)
    session = Session()
    session.query(RateHistory).filter(RateHistory.id == str(id)). \
    update({RateHistory.compra:rateHistory.compra, RateHistory.venta:rateHistory.venta, RateHistory.source:rateHistory.source, RateHistory.updateDateTime:datetime.now()}, synchronize_session = False)
    session.commit()
    session.close()

def get(id):
    with open('db.setting.json') as f:
        db_setting = json.load(f)
    dbengine = create_engine(db_setting['db_connection'], echo = True)
    Base = declarative_base()
    if not dbengine.dialect.has_table(dbengine, db_setting['table_name']):  # If table don't exist, Create.
        return False 
    Session = sessionmaker(bind=dbengine)
    session = Session()
    x = session.query(RateHistory).get(id)
    session.close()
    rateHistory = RateHistory(id=x.id, compra=x.compra, venta=x.venta, source=x.source, updateDateTime=x.updateDateTime.strftime('%Y-%m-%d %H:%M:%S'))
    return rateHistory

def getall():
    with open('db.setting.json') as f:
        db_setting = json.load(f)
    dbengine = create_engine(db_setting['db_connection'], echo = True)
    Base = declarative_base()
    if not dbengine.dialect.has_table(dbengine, db_setting['table_name']):  # If table don't exist, Create.
        return False 
    Session = sessionmaker(bind=dbengine)
    session = Session()
    x = session.query(RateHistory).all()
    session.close()
    return x

def create_table(metadata, dbengine, tablename):
    thetable = Table(
        tablename, metadata, 
        Column('history_id', Integer, primary_key = True, autoincrement=True), 
        Column('compra', Float), 
        Column('venta', Float), 
        Column('source', String(16)), 
        Column('update_datetime', DateTime), 
    )
    metadata.create_all(dbengine)

class RateHistory(Base):
    __tablename__ = 'rate_history'
    id = Column('history_id', Integer, primary_key=True)
    compra = Column('compra', Float)
    venta = Column('venta', Float)
    source = Column('source', String(16))
    updateDateTime = Column('update_datetime', DateTime)

    def __init__(self, compra, venta, source, updateDateTime):
        self.compra = compra
        self.venta = venta
        self.source = source
        self.updateDateTime = datetime.strptime(updateDateTime, '%Y-%m-%d %H:%M:%S')

    def __init__(self, compra, venta, source, updateDateTime, id=None):
        self.id = id
        self.compra = compra
        self.venta = venta
        self.source = source
        self.updateDateTime = datetime.strptime(updateDateTime, '%Y-%m-%d %H:%M:%S')
    
    def __str__(self):
        return f'ID={self.id}, SRC={self.source}, COMPRA={self.compra}, VENTA={self.venta}, UDT={self.updateDateTime}'


#add()
#rateHistory = RateHistory(compra=1111.0, venta=2222.3, source="THA", updateDateTime="2020-01-01 12:23:33")
#update(2 , rateHistory)
# rateHistory = get(2)
# print(rateHistory)

# theall = getall()
# for row in theall:
#     print(str(row))