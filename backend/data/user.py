from . import init
from backend.model.user import User
from backend.errors import Missing, Duplicate


def create_table():
    init.curs.execute("DROP TABLE IF EXISTS users")
    init.curs.execute(
        """
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            first_name TEXT,
            last_name TEXT,
            pssword TEXT NOT NULL,
        )
        """
    )
    init.curs.execute("DROP TABLE IF EXISTS xusers")
    init.curs.execute(
        """
        CREATE TABLE IF NOT EXISTS xusers(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
        )
        """
    )
    init.conn.commit()

def row_to_model(row: tuple) -> User:
    (id, username, first_name, last_name, password) = row
    return User(
        id=id, 
        username=username,
        first_name=first_name,
        last_name=last_name,
        password=password
    )

def model_to_dict(user: User) -> dict:
    return user.model_dump()

def get_one(id: int) -> User:
    query = "SELECT * FROM users WHERE id = ?"
    init.curs.execute(query, (id,))
    row = init.curs.fetchone()
    init.conn.commit()

    if row:
        return row_to_model(row)
    else:
        raise Missing(msg=f"Такого пользователя не существует")
    
def get_one_by_username(username: str) -> User:
    query = "SELECT * FROM users WHERE username = ?"
    init.curs.execute(query, (username, ))
    row = init.curs.fetchone()
    init.conn.commit()

    if row:
        return row_to_model(row)
    else:
        raise Missing(msg=f"Такого пользователя не существует")

def get_all() -> list[User]:
    query = "SELECT * FROM users"
    init.curs.execute(query)
    rows = list(init.curs.fetchall())
    init.conn.commit()

    return [row_to_model(row) for row in rows]

def create(user: User, table: str = "users") -> User:
    query = f"""
        INSERT INTO {table} (username, first_name, last_name, password) 
        VALUES (:username, :first_name, :last_name, :password)
    """
    params = model_to_dict(user)

    try:
        init.curs.execute(query, params)
        init.conn.commit()
        return get_one(init.curs.lastrowid)
    except init.IntegrityError:
        raise Duplicate(
            msg=f"Такой пользователь c никнеймом {user.username} уже существует"
        )
        

def modify(user: User) -> User:
    if not user: return None
    query = """
        UPDATE users SET
            username = :username,
            last_name = :last_name,
            fist_name = :fist_name,
        WHERE id = :id
    """
    params = model_to_dict(user)
    init.curs.execute(query, params)
    init.conn.commit()

    if init.curs.rowcount == 1:
        return get_one(user.id)
    else:
        raise Missing(msg=f"Такого пользователя не существует.")

def delete(id: int):
    user = get_one(id)
    query = "DELETE FROM users WHERE id = ?"
    init.curs.execute(query, (id,))
    init.conn.commit()
    if init.curs.rowcount != 1:
        raise Missing(msg=f"Такого пользователя не существует.")
    create(user=user, table="xusers")
    return True