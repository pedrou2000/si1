# -*- coding: utf-8 -*-

import os
import sys, traceback, time

from sqlalchemy import create_engine
from pymongo import MongoClient

# configurar el motor de sqlalchemy
db_engine = create_engine("postgresql://alumnodb:alumnodb@localhost/si1", echo=False, execution_options={"autocommit":False})

# Crea la conexión con MongoDB
mongo_client = MongoClient()

def getMongoCollection(mongoDB_client):
    mongo_db = mongoDB_client.si1
    return mongo_db.topUK

def mongoDBCloseConnect(mongoDB_client):
    mongoDB_client.close()

def dbConnect():
    return db_engine.connect()

def dbCloseConnect(db_conn):
    db_conn.close()
  
def delCity(city, bFallo, bSQL, duerme, bCommit):
    
    # Array de trazas a mostrar en la página
    dbr=[]
    db_conn = dbConnect()
    # TODO: Ejecutar consultas de borrado
    # - ordenar consultas según se desee provocar un error (bFallo True) o no
    # - ejecutar commit intermedio si bCommit es True
    # - usar sentencias SQL ('BEGIN', 'COMMIT', ...) si bSQL es True
    # - suspender la ejecución 'duerme' segundos en el punto adecuado para forzar deadlock
    # - ir guardando trazas mediante dbr.append()
    
    try:
        # TODO: ejecutar consultas
        customerid_list = get_customers_from_city(db_conn, city)
        orderid_list =get_orders_from_customer(db_conn, customerid_list)

        if bFallo:
            delete_customers(customerid_list)
            delete_orders(orderid_list)
            delete_orderdetails(orderid_list)

        else:
            delete_orderdetails(customerid_list)
            delete_orders(orderid_list)
            delete_customers(orderid_list)
        
        pass
    except Exception as e:
        # TODO: deshacer en caso de error
        pass
    else:
        # TODO: confirmar cambios si todo va bien
        pass
        
    return dbr

def get_customers_from_city(db_conn, city):

    query = 'select customers.customerid '\
            'from customers '\
            'where customers.city = ' + str(city)
    
    return list(db_conn.execute(query)) 

def get_orders_from_customer(db_conn, customerid_list):

    query = 'select orders.orderid '\
            'from orders '\
            'where orders.customerid in {}'.format(tuple(customerid_list))

    return list(db_conn.execute(query))

def delete_customers(db_conn, customerid_list):

    query = 'delete from customers '\
            'where customerid in {}'.format(tuple(customerid_list))
    
    db_conn.execute(query)

def delete_orders(db_conn, orderid_list):

    query = 'delete from orders '\
            'where orderid in {}'.format(tuple(orderid_list))
    
    db_conn.execute(query)

def delete_orderdetails(db_conn, orderid_list):

    query = 'delete from orderdetail '\
            'where orderid in {}'.format(tuple(orderid_list))
    
    db_conn.execute(query)