from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Boolean, Date
from sqlalchemy.orm import relationship, sessionmaker
from enum import Enum as PyEnum
from storage.database import Base, engine

class DeadlineType(PyEnum):
    EXAM = "exam"
    HOMEWORK = "homework"
    PROJECT = "project"

class User(Base):
    __tablename__ = 't_user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    family_name = Column(String, nullable=False)
    is_foreign = Column(Boolean, default=False)
    return_date = Column(Date, nullable=True)
    subjects = relationship("Subject", back_populates="user")

class Subject(Base):
    __tablename__ = 't_subject'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey('t_user.id'), nullable=False)
    user = relationship("User", back_populates="subjects")
    deadlines = relationship("Deadline", back_populates="subject")

class Deadline(Base):
    __tablename__ = 't_deadline'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    deadline_type = Column(Enum(DeadlineType), nullable=False)
    due_date = Column(String, nullable=False)
    subject_id = Column(Integer, ForeignKey('t_subject.id'), nullable=False)
    subject = relationship("Subject", back_populates="deadlines", lazy='joined')

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)

def is_user_registered(telegram_id):
    """
    Проверяет, зарегистрирован ли пользователь по telegram_id.
    """
    session = Session()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    session.close()
    return bool(user)
def create_user(telegram_id, name, surname, family_name):
    """
    Создание пользователя. Если пользователь с данным telegram_id уже существует, возвращается его ID.
    """
    session = Session()
    existing_user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if existing_user:
        return existing_user.id

    new_user = User(
        telegram_id=telegram_id,
        name=name,
        surname=surname,
        family_name=family_name
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user.id


def subject_already_exists(telegram_id, subject_name):
    """
    Проверяет, существует ли предмет с данным названием для пользователя с указанным Telegram ID.
    Возвращает True, если предмет существует, иначе False.
    """
    session = Session()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if not user:
        raise ValueError(f"Пользователь с Telegram ID {telegram_id} не существует.")
    
    subject_exists = session.query(Subject).filter_by(user_id=user.id, name=subject_name).first()
    return bool(subject_exists)


def add_subject(telegram_id, subject_name):
    """
    Добавление предмета для пользователя по telegram_id.
    """
    session = Session()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if not user:
        raise ValueError(f"Пользователь с Telegram ID {telegram_id} не существует.")
    
    new_subject = Subject(name=subject_name, user_id=user.id)
    session.add(new_subject)
    new_subject_id = new_subject.id
    session.commit()
    return new_subject_id

def add_deadline(subject_id, deadline_name, deadline_type, due_date):
    """
    Добавляет дедлайн для указанного предмета с датой.
    """
    session = Session()
    try:
        new_deadline = Deadline(
            name=deadline_name,
            deadline_type=deadline_type,
            due_date=due_date,
            subject_id=subject_id
        )
        session.add(new_deadline)
        session.flush()
        deadline_id = new_deadline.id
        session.commit()
        return deadline_id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def set_foreign_status(user_id, is_foreign, return_date=None):
    """
    Установка статуса иностранного студента и даты возвращения.
    """
    session = Session()
    user = session.query(User).filter_by(id=user_id).first()
    if user:
        user.is_foreign = is_foreign
        user.return_date = return_date
        session.commit()

def get_notifications():
    """
    Получение списка пользователей для напоминаний.
    """
    session = Session()
    notifications = session.query(User.id).all()
    return [(user_id, "Напоминание: Внесите дедлайны для ваших предметов!") for user_id in notifications]

def get_users_for_deadline_reminders():
    """
    Получение списка пользователей для напоминаний о дедлайнах.
    """
    session = Session()
    users = session.query(User.id).all()
    return [user_id for (user_id,) in users]

def get_users_to_register_deadlines():
    """
    Получение списка пользователей, у которых есть предметы, но нет дедлайнов.
    """
    session = Session()
    users_with_subjects = session.query(User.id).join(Subject).distinct().all()
    return [user_id for (user_id,) in users_with_subjects]

def get_subjects_by_user(telegram_id):
    """
    Возвращает список предметов пользователя по его telegram_id.
    """
    session = Session()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if not user:
        session.close()
        return []
    
    subjects = session.query(Subject).filter_by(user_id=user.id).all()
    session.close()
    return subjects

def get_deadlines_by_subject(subject_id):
    """
    Получение списка дедлайнов по предмету.
    """
    session = Session()
    deadlines = session.query(Deadline).filter_by(subject_id=subject_id).all()
    session.close()
    return deadlines

def get_all_reminders_by_user(telegram_id):
    """
    Получение всех напоминаний пользователя (предметы и дедлайны) по telegram_id.
    """
    session = Session()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if not user:
        return None

    reminders = []
    for subject in user.subjects:
        subject_info = f"Предмет: {subject.name}"
        if subject.deadlines:
            for deadline in subject.deadlines:
                deadline_info = (
                    f"  - Дедлайн: {deadline.name}, "
                    f"Тип: {deadline.deadline_type.value}, "
                    f"ID предмета: {subject.id}"
                )
                reminders.append(f"{subject_info}\n{deadline_info}")
        else:
            reminders.append(f"{subject_info}\n  - Нет добавленных дедлайнов")
    session.close()
    return reminders

def delete_deadline(deadline_id):
    """
    Удаляет дедлайн из базы данных по его ID.
    """
    session = Session()
    deadline = session.query(Deadline).filter_by(id=deadline_id).first()
    if deadline:
        session.delete(deadline)
        session.commit()