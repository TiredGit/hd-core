from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import String, Text, ForeignKey, Enum, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base
from typing import Optional


class UserRole(PyEnum):
    USER = "user"
    EMPLOYEE = "employee"
    ADMIN = "admin"


class EmployeeType(PyEnum):
    PLUMBER = "plumber"
    ELECTRICIAN = "electrician"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, default=UserRole.USER)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    profile: Mapped[Optional["UserProfile"]] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    employee_profile: Mapped[Optional["EmployeeProfile"]] = relationship(back_populates="user", uselist=False,
                                                               cascade="all, delete-orphan")

    @property
    def address(self) -> Optional[str]:
        return self.profile.address if self.profile else None

    @property
    def apartment(self) -> Optional[str]:
        return self.profile.apartment if self.profile else None

    @property
    def personal_account(self) -> Optional[str]:
        return self.profile.personal_account if self.profile else None

    @property
    def employee_type(self) -> Optional[EmployeeType]:
        return self.employee_profile.employee_type if self.employee_profile else None


class UserProfile(Base):
    __tablename__ = "user_profile"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    apartment: Mapped[str | None] = mapped_column(String(10), nullable=True)
    personal_account: Mapped[str | None] = mapped_column(String(20), nullable=True)

    user: Mapped["User"] = relationship(back_populates="profile")


class EmployeeProfile(Base):
    __tablename__ = "employee_profile"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    employee_type: Mapped[EmployeeType] = mapped_column(Enum(EmployeeType), nullable=False)

    user: Mapped["User"] = relationship(back_populates="employee_profile")