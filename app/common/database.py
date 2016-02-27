import mysql.connector
import logging
from config import DB_CONFIG
from mysql.connector import errorcode


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
    def execute_insert_query(query, data):
        cnx = Db.get_connection()
        cursor = cnx.cursor()
        row_id = -1
        try:
            cursor.execute(query, data)
            row_id = cursor.lastrowid
            cnx.commit()
        except mysql.connector.Error as err:
            print err
        finally:
            cursor.close()
            cnx.close()
        return row_id

    @staticmethod
    def execute_select_query(query, parameters):
        cnx = Db.get_connection()
        cursor = cnx.cursor(dictionary=True)
        result = []
        cursor.execute(query % parameters)
        for row in cursor:
            result.append(row)
        cursor.close()
        cnx.close()
        return result

