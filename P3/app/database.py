# -*- coding: utf-8 -*-

import os
import sys, traceback, time

from sqlalchemy import create_engine
from pymongo import MongoClient
from sqlalchemy.orm import Session

# configurar el motor de sqlalchemy
db_engine = create_engine("postgresql://alumnodb:alumnodb@localhost/si1_p3", echo=False, execution_options={"autocommit":False})

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
    # TODO: Ejecutar consultas de borrado
    # - ordenar consultas según se desee provocar un error (bFallo True) o no
    # - ejecutar commit intermedio si bCommit es True
    # - usar sentencias SQL ('BEGIN', 'COMMIT', ...) si bSQL es True
    # - suspender la ejecución 'duerme' segundos en el punto adecuado para forzar deadlock
    # - ir guardando trazas mediante dbr.append()
    if bSQL == 1:
        # SQL transaction 
        db_conn = dbConnect()
        dbr.append("The transaction is going to be managed by SQL")
        try:
            # TODO: ejecutar consultas
            dbr = begin(db_conn, dbr)
            customerid_list = get_customers_from_city(db_conn, city)
            if len(customerid_list) == 0:
                dbr.append("No results found for the introduced city (" + city + ")")
                db_conn.close()
                return dbr
            
            orderid_list = get_orders_from_customer(db_conn, customerid_list)
            if len(orderid_list) == 0:
                dbr.append("No orders associated with the customers that live in " + city )
                dbr = delete_customers(db_conn, customerid_list, dbr, city)
                dbr = commit(db_conn, dbr)
                db_conn.close()
                return dbr
            
            if bFallo:
                dbr = delete_customers(db_conn, customerid_list, dbr, city)
                dbr = delete_orders(db_conn, orderid_list, dbr, city)
                dbr = delete_orderdetails(db_conn, orderid_list, dbr, city)

            else:
                dbr = delete_orderdetails(db_conn, orderid_list, dbr, city)
                dbr = delete_orders(db_conn, orderid_list, dbr, city)
                dbr = delete_customers(db_conn, customerid_list, dbr, city)
            
            #pass
        except Exception as e:
            # TODO: deshacer en caso de error
            #pass
            print(e)
            dbr = rollback(db_conn, dbr)
        else:
            # TODO: confirmar cambios si todo va bien
            #pass
            dbr = commit(db_conn, dbr)
        db_conn.close()
    
    else:
        # SQLAlhemy transaction
        dbr.append("The transaction is going to be managed by SQLAlchemy")
        session = Session(db_engine)
        dbr.append("Begin")
        try:
            # TODO: ejecutar consultas
            # begin is done automatically when an execute is done
            customerid_list = get_customers_from_city_sqlalchemy(session, city)
            if len(customerid_list) == 0:
                dbr.append("No results found for the introduced city (" + city + ")")
                session.close()
                return dbr
            
            orderid_list = get_orders_from_customer_sqlalchemy(session, customerid_list)
            if len(orderid_list) == 0:
                dbr.append("No orders associated with the customers that live in " + city )
                dbr = delete_customers_sqlalchemy(session, customerid_list, dbr, city)
                session.commit()
                dbr.append("Commit")
                session.close()
                return dbr
            
            if bFallo:
                dbr = delete_customers_sqlalchemy(session, customerid_list, dbr, city)
                dbr = delete_orders_sqlalchemy(session, orderid_list, dbr, city)
                dbr = delete_orderdetails_sqlalchemy(session, orderid_list, dbr, city)

            else:
                dbr = delete_orderdetails_sqlalchemy(session, orderid_list, dbr, city)
                dbr = delete_orders_sqlalchemy(session, orderid_list, dbr, city)
                dbr = delete_customers_sqlalchemy(session, customerid_list, dbr, city)
        
        #pass
        except Exception as e:
        # TODO: deshacer en caso de error
        #pass
            print(e)
            session.rollback()
            dbr.append("Rollback")
        else:
            # TODO: confirmar cambios si todo va bien
            #pass
            session.commit()
            dbr.append("Commit")
        session.close()

    return dbr

#SQL auxiliar functions
def get_customers_from_city(db_conn, city):

    query = 'select customerid '\
            'from customers '\
            'where city = ' + "'" + str(city) + "'" 
    
    result_list = list(db_conn.execute(query)) 
    real_list = []
    for item in result_list:
        real_list.append(item[0])
    
    return real_list

def get_orders_from_customer(db_conn, customerid_list):
    if len(customerid_list) == 1:
         aux_tuple = "(" + str(customerid_list[0]) + ")"
    
    else:
        aux_tuple = tuple(customerid_list)
    
    query = 'select orderid '\
            'from orders '\
            'where customerid in {}'.format(aux_tuple)

    result_list = list(db_conn.execute(query))
    real_list = []
    for item in result_list:
        real_list.append(item[0])
    
    return real_list

def delete_customers(db_conn, customerid_list, dbr, city):
    dbr.append("Trying to delete the customers that live in " + city )
    if len(customerid_list) == 1:
        aux_tuple = "(" + str(customerid_list[0]) + ")"
    
    else:
        aux_tuple = tuple(customerid_list)
    
    query = 'delete from customers '\
            'where customerid in {}'.format(aux_tuple)

    db_conn.execute(query)
    dbr.append("Customers that live in " + city + " DELETED")

    return dbr 

def delete_orders(db_conn, orderid_list, dbr, city):
    dbr.append("Trying to delete the orders from the customers that live in " + city )
    if len(orderid_list) == 1:
        aux_tuple = "(" + str(orderid_list[0]) + ")"
    
    else:
        aux_tuple = tuple(orderid_list)
    
    query = 'delete from orders '\
            'where orderid in {}'.format(aux_tuple)
    
    db_conn.execute(query)
    dbr.append("Orders associated with the customers that live in " + city + " DELETED")
    
    return dbr

def delete_orderdetails(db_conn, orderid_list, dbr, city):
    dbr.append("Trying to delete the order details associated with the order of the customers that live in " + city)
    if len(orderid_list) == 1:
        aux_tuple = "(" + str(orderid_list[0]) + ")"
    
    else:
        aux_tuple = tuple(orderid_list)
    
    query = 'delete from orderdetail '\
            'where orderid in {}'.format(aux_tuple)
    
    db_conn.execute(query)
    dbr.append("Order details associated with the order of the customers that live in " + city + " DELETED")

    return dbr

#  SQLAlchemy auxiliar functions
def get_customers_from_city_sqlalchemy(session, city):

    query = 'select customerid '\
            'from customers '\
            'where city = ' + "'" + str(city) + "'" 
    
    result_list = list(session.execute(query)) 
    real_list = []
    for item in result_list:
        real_list.append(item[0])
    
    return real_list

def get_orders_from_customer_sqlalchemy(session, customerid_list):
    if len(customerid_list) == 1:
         aux_tuple = "(" + str(customerid_list[0]) + ")"
    
    else:
        aux_tuple = tuple(customerid_list)
    
    query = 'select orderid '\
            'from orders '\
            'where customerid in {}'.format(aux_tuple)

    result_list = list(session.execute(query))
    real_list = []
    for item in result_list:
        real_list.append(item[0])
    
    return real_list

def delete_customers_sqlalchemy(session, customerid_list, dbr, city):
    dbr.append("Trying to delete the customers that live in " + city )
    if len(customerid_list) == 1:
        aux_tuple = "(" + str(customerid_list[0]) + ")"
    
    else:
        aux_tuple = tuple(customerid_list)
    
    query = 'delete from customers '\
            'where customerid in {}'.format(aux_tuple)

    session.execute(query)
    dbr.append("Customers that live in " + city + " DELETED")

    return dbr 

def delete_orders_sqlalchemy(session, orderid_list, dbr, city):
    dbr.append("Trying to delete the orders from the customers that live in " + city )
    if len(orderid_list) == 1:
        aux_tuple = "(" + str(orderid_list[0]) + ")"
    
    else:
        aux_tuple = tuple(orderid_list)
    
    query = 'delete from orders '\
            'where orderid in {}'.format(aux_tuple)
    
    session.execute(query)
    dbr.append("Orders associated with the customers that live in " + city + " DELETED")
    
    return dbr

def delete_orderdetails_sqlalchemy(session, orderid_list, dbr, city):
    dbr.append("Trying to delete the order details associated with the order of the customers that live in " + city)
    if len(orderid_list) == 1:
        aux_tuple = "(" + str(orderid_list[0]) + ")"
    
    else:
        aux_tuple = tuple(orderid_list)
    
    query = 'delete from orderdetail '\
            'where orderid in {}'.format(aux_tuple)
    
    session.execute(query)
    dbr.append("Order details associated with the order of the customers that live in " + city + " DELETED")

    return dbr

def begin(db_conn, dbr):
    query = 'begin'
    
    db_conn.execute(query)
    dbr.append("Begin")

    return dbr

def rollback(db_conn, dbr):
    query = 'rollback'
    
    db_conn.execute(query)
    dbr.append("Rollback")

    return dbr

def commit(db_conn, dbr):
    query = 'commit'
    
    db_conn.execute(query)
    dbr.append("Commit")

    return dbr