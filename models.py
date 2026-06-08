from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Boolean, Text, Date, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

class User(db.Model):
  __tablename__ = 'users'

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
  email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
  password: Mapped[str] = mapped_column(String(255), nullable=False)
  created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

  # Relation
  tasks: Mapped[list['Task']] = relationship('Task', back_populates='user', cascade='all, delete')

  def __repr__(self):
    return f'<User {self.username}>'


class Category(db.Model):
  __tablename__ = 'categories'

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  name: Mapped[str] = mapped_column(String(50), nullable=False)
  color: Mapped[str | None] = mapped_column(String(7))

  # Relation
  tasks: Mapped[list['Task']] = relationship('Task', back_populates='category')

  def __repr__(self):
    return f'<Category {self.name}>'


class Task(db.Model):
  __tablename__ = 'tasks'

  __table_args__ = (
    CheckConstraint("priority IN ('low', 'medium', 'high')", name='check_priority'),
  )

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
  category_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('categories.id', ondelete='SET NULL'))
  title: Mapped[str] = mapped_column(String(255), nullable=False)
  description: Mapped[str | None] = mapped_column(Text)
  done: Mapped[bool] = mapped_column(Boolean, default=False)
  priority: Mapped[str] = mapped_column(String(10), default='medium')
  start_date: Mapped[datetime | None] = mapped_column(Date)
  end_date: Mapped[datetime | None] = mapped_column(Date)
  created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
  updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

  # Relations
  user: Mapped['User'] = relationship('User', back_populates='tasks')
  category: Mapped['Category | None'] = relationship('Category', back_populates='tasks')

  def __repr__(self):
    return f'<Task {self.title}>'