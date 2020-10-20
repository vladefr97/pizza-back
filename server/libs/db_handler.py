import pymysql
from flaskext.mysql import MySQL


class DBResponse:
    """Экземпляр данного класса описывает станадартный ответ на запрос к базе данных MySQL"""

    def __init__(self, status, data):
        """
        :param status: Результат запрос к базе данных (уcпешен - True, неуспешен - False)
        :param data: Данные, полученные из базы данных
        :rtype: DBResponse
        """
        self.status = status

        self.data = data


class MySQLHandler:
    """Класс для выполнения запрос к базе данных MySQL посредством хранимых процедур"""

    def __init__(self, app, db_host, db_name, db_user, db_password):
        """
        :param app: Экземпляра класса Flask
        :param db_host: Название сервера базы данных
        :param db_name: Название базы данных
        :param db_user: Логин пользователя базы данных
        :param db_password: Пароль пользователя базы данных
        """
        self._app = app
        self._mysql = MySQL()
        # MySQL configurations
        self._app.config['MYSQL_DATABASE_USER'] = db_user
        self._app.config['MYSQL_DATABASE_PASSWORD'] = db_password
        self._app.config['MYSQL_DATABASE_DB'] = db_name
        self._app.config['MYSQL_DATABASE_HOST'] = db_host

        self._mysql.init_app(self._app)
        # self.conn = self._mysql.connect()

    def close_connection(self):
        try:
            self.conn.close()
            message = "OK"
            return DBResponse(True, message)
        except pymysql.err.OperationalError as e:
            return DBResponse(False, str(e))

    def connect(self):
        try:
            self.conn = self._mysql.connect()
            message = "OK"
            return DBResponse(True, message)
        except pymysql.err.OperationalError as e:
            return DBResponse(False, str(e))

    def call_get_data_proc(self, proc_name: str, *proc_args):
        """
         Метод соединяется с базой данных MySQL и вызывает хранимую процедуру. Процедура получает некоторые данные из базы MySQL.
        :type proc_name: Название хранимой процедуры
        :param proc_args: Аргументы для вызова хранимой процедуры
        :return: Экземпляр класса DBResponse
        """
        # connect to mysql database
        try:

            cursor = self.conn.cursor()
            cursor.callproc(proc_name, proc_args)
            data = cursor.fetchall()
            return DBResponse(True, data)
        except Exception as e:
            message = str(e)
            return DBResponse(False, message)
        finally:
            cursor.close()

    def call_create_delete_proc(self, proc_name, *proc_args):
        """
          Метод соединяется с базой данных MySQL и вызывает хранимую процедуру. Процедура выполняет удаление или добавление данных.
        :param proc_name: Название хранимой процедуры
        :param proc_args: Аргументы для вызова хранимой процедуры
        :return: Экземпляр класса DBResponse
        """
        # connect to mysql database
        try:

            cursor = self.conn.cursor()
            cursor.callproc(proc_name, proc_args)
            data = cursor.fetchall()
            if len(data) is 0:
                self.conn.commit()
                return DBResponse(True, data)
            else:
                return DBResponse(False, 'Не удалось выполнить действие!')
        except Exception as e:
            message = str(e)
            return DBResponse(False, message)
        finally:
            cursor.close()

    def execute_many_insert(self, query: str, data: list):
        """
        @param query: Insert query string
        @type query: str
        @param data: Insert list of data (insert several times)
        @type data: list
        @return: Response from database
        @rtype: DBResponse
        """
        try:

            cursor = self.conn.cursor()
            for elem in data:
                cursor.executemany(query, elem)
            self.conn.commit()
            return DBResponse(True, "")
        except Exception as e:
            message = str(e)
            return DBResponse(False, message)
        finally:
            cursor.close()

    def execute_insert(self, query: str, data: list) -> DBResponse:
        """
        @param query: insert query string
        @type query: str
        @param data: insert data
        @type data: list
        @return: Response from database
        @rtype: DBResponse
        """
        try:

            cursor = self.conn.cursor()
            cursor.executemany(query, data)
            self.conn.commit()
            lastid = cursor.lastrowid
            return DBResponse(True, {'lastid': lastid})
        except Exception as e:
            message = str(e)
            return DBResponse(False, message)
        finally:
            cursor.close()

    def execute_select(self, query: str, data: list = None) -> DBResponse:
        """
        @param query: Select query string
        @type query: str
        @param data: None
        @type data: None
        @return: Response from database
        @rtype: DBResponse
        """
        try:

            cursor = self.conn.cursor()
            cursor.execute(query, data)
            result = cursor.fetchall()
            return DBResponse(True, result)
        except Exception as e:
            message = str(e)
            return DBResponse(False, message)
        finally:
            cursor.close()

    def execute_update(self, query: str, data: list = None) -> DBResponse:
        """
        @param data:
        @type data:
        @param query: update query string
        @type query: str
        :type data: DBResponse
        """
        try:
            cursor = self.conn.cursor()
            cursor.executemany(query, data)
            self.conn.commit()
            return DBResponse(True, "")
        except Exception as e:
            message = str(e)
            return DBResponse(False, message)
        finally:
            cursor.close()

    def execute_delete(self, query: str, *data) -> DBResponse:
        """
        @param query: delete query string
        @type query: str
        @param data: delete data params
        @type data:
        :type data: DBResponse
        """
        try:

            cursor = self.conn.cursor()
            cursor.executemany(query, data)
            self.conn.commit()
            return DBResponse(True, "")
        except Exception as e:
            message = str(e)
            return DBResponse(False, message)
        finally:
            cursor.close()
