from storage.database import get_db_connection

def get_notifications():
    """Получает уведомления из БД"""
    pass

# Создание пользователя
def create_user(name, surname, family_name):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO users (name, surname, family_name) VALUES (%s, %s, %s) RETURNING id",
            (name, surname, family_name)
        )
        user_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return user_id

# Добавление предмета
def add_subject(user_id, subject_name):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO t_subject (name, user_id) VALUES (%s, %s) RETURNING id",
            (subject_name, user_id)
        )
        subject_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return subject_id

# Добавление дедлайна
def add_deadline(subject_id, deadline_name, deadline_type):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO t_deadline (name, deadline_type, user_id) VALUES (%s, %s, %s)",
            (deadline_name, deadline_type, subject_id)
        )
    conn.commit()
    conn.close()
