from database_module import parsing_module
from database_module.database_module import DataBaseConnector

db = DataBaseConnector()


if __name__ == '__main__':
    #db.drop_table()
    parsing_module.collect_data(1)
