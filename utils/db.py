from sqlalchemy.orm import sessionmaker
from sqlalchemy import exc
from sqlalchemy import event
from sqlalchemy.pool import Pool

# deals with mysql disconnections
@event.listens_for(Pool, "checkout")
def ping_connection(dbapi_connection, connection_record, connection_proxy):
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("SELECT 1")
    except:
        raise exc.DisconnectionError()
    cursor.close()

def load_session(engine):
    """Loads a SqlAlchemy session based on the engine parameter

    :param engine: The connection engine for the session (Mysql, postgres...)
    :returns: SqlAlchemy session 
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
