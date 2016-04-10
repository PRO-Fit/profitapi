import mysql.connector
import logging
from mysql.connector import errors
from mysql.connector import errorcode

from config import DB_CONFIG
from util import Util


class Db():
    @staticmethod
    def get_connection():
        try:
            cnx = mysql.connector.connect(**DB_CONFIG)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                logging.log(logging.DEBUG, "Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                logging.log(logging.DEBUG,"Database does not exist")
            else:
                print(err)
        else:
            logging.log(logging.DEBUG, "connection successful")
            return cnx

    @staticmethod
    def execute_insert_query(query, data=None):
        cnx = Db.get_connection()
        cursor = cnx.cursor()
        row_id = -1
        try:
            if data:
                cursor.execute(query, data)
            else:
                cursor.execute(query)
            row_id = cursor.lastrowid
            cnx.commit()
        except mysql.connector.Error as err:
            print err
        finally:
            cursor.close()
            cnx.close()
        return row_id

    @staticmethod
    def execute_select_query(query, parameters=None):
        cnx = Db.get_connection()
        cursor = cnx.cursor(dictionary=True)
        result = []
        try:
            if parameters:
                cursor.execute(query % parameters)
            else:
                cursor.execute(query)
            for row in cursor:
                result.append(row)
        except errors.InternalError or errors.DatabaseError as err:
            print err
        finally:
            cursor.close()
            cnx.close()
        cursor.close()
        cnx.close()
        return result

    @staticmethod
    def execute_update_query(query, parameters=None):
        cnx = Db.get_connection()
        cursor = cnx.cursor()
        success = 1
        try:
            if parameters:
                cursor.execute(query % parameters)
            else:
                cursor.execute(query)
            cnx.commit()
        except mysql.connector.Error as err:
            print err
            success = -1
        finally:
            cursor.close()
            cnx.close()
        return success
