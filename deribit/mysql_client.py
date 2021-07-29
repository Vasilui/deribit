import asyncio
import aiomysql

from base_classes import MysqlDB


def loop(connector, query):
    loop_db = asyncio.get_event_loop()
    return loop_db.run_until_complete(connector(loop_db, query))


class ClientDB:
    def __init__(self, db: MysqlDB) -> None:
        self.db = db

    async def connector_to_db(self, loop_db, query):
        conn = await aiomysql.connect(host=self.db.db_host,
                                      port=self.db.db_port,
                                      user=self.db.db_user,
                                      password=self.db.db_password,
                                      db=self.db.db_name,
                                      loop=loop_db)
        async with conn.cursor(aiomysql.cursors.DeserializationCursor,
                               aiomysql.cursors.DictCursor) as cur:
            await cur.execute(query)
            await conn.commit()
            r = await cur.fetchall()
        conn.close()
        return r

    def write_to_db(self, query):
        return loop(self.connector_to_db, query)

    def insert(self, id, type, status, amount, price):
        columns = "order_id, order_type, order_status, order_amount, order_price"
        query = f'insert into {self.db.db_table} ({columns}) values ' \
                f'("{id}","{type}","{status}",{amount},{price});'
        self.write_to_db(query)

    def update(self, id, status, price, amount):
        query = f'UPDATE {self.db.db_table} SET order_status = "{status}",' \
                f' order_price = {price}, order_amount = {amount}' \
                f'WHERE order_id = "{id}";'
        self.write_to_db(query)

    def create_db(self):
        query = f'show tables from {self.db.db_name} like "{self.db.db_table}";'
        res = self.write_to_db(query)
        if not res:
            query = """
                CREATE TABLE orders (
                    id int NOT NULL AUTO_INCREMENT,
                    order_id varchar(20) NOT NULL,
                    order_type varchar(5) NOT NULL,
                    order_status varchar(10) NOT NULL,
                    order_amount float NOT NULL,
                    order_price float NOT NULL,
                    PRIMARY KEY (id)
                ) ENGINE=InnoDB
            """
            self.write_to_db(query)
