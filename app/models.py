import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Boolean, Integer, Numeric,
    DateTime, ForeignKey, ARRAY, CheckConstraint, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .database import Base


def gen_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String)
    phone = Column(String)
    role = Column(String, default="member")
    is_active = Column(Boolean, default=False)
    hashed_password = Column(String, nullable=False)
    avatar_url = Column(String)
    membership_since = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    bookings = relationship("Booking", back_populates="user")
    sent_messages = relationship("Message", foreign_keys="Message.from_user_id", back_populates="sender")
    received_messages = relationship("Message", foreign_keys="Message.to_user_id", back_populates="recipient")

    __table_args__ = (
        CheckConstraint("role IN ('member', 'vip', 'admin')", name="users_role_check"),
    )


class Location(Base):
    __tablename__ = "locations"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    city = Column(String, nullable=False)
    country = Column(String, nullable=False)
    region = Column(String)
    address = Column(String)
    is_active = Column(Boolean, default=True)
    rooms_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    rooms = relationship("Room", back_populates="location")


class Room(Base):
    __tablename__ = "rooms"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    location_id = Column(UUID(as_uuid=False), ForeignKey("locations.id"))
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False, index=True)
    category = Column(String, nullable=False)
    type = Column(String, nullable=False)
    description = Column(Text)
    short_description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    original_price = Column(Numeric(10, 2))
    price_unit = Column(String, default="night")
    size_sqm = Column(Integer)
    max_guests = Column(Integer, default=2)
    beds = Column(String)
    amenities = Column(ARRAY(String), default=[])
    images = Column(ARRAY(String), default=[])
    is_featured = Column(Boolean, default=False)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    location = relationship("Location", back_populates="rooms")
    bookings = relationship("Booking", back_populates="room")


class Package(Base):
    __tablename__ = "packages"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    description = Column(Text)
    type = Column(String)
    duration_days = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    original_price = Column(Numeric(10, 2))
    includes = Column(ARRAY(String), default=[])
    is_featured = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    booking_ref = Column(String, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    room_id = Column(UUID(as_uuid=False), ForeignKey("rooms.id"))
    package_id = Column(UUID(as_uuid=False), ForeignKey("packages.id"))
    location_id = Column(UUID(as_uuid=False), ForeignKey("locations.id"))
    booking_type = Column(String, nullable=False)
    check_in = Column(DateTime, nullable=False)
    check_out = Column(DateTime, nullable=False)
    guests_count = Column(Integer, default=1)
    special_requests = Column(Text)
    guest_name = Column(String, nullable=False)
    guest_email = Column(String, nullable=False)
    guest_phone = Column(String)
    total_price = Column(Numeric(10, 2), nullable=False)
    status = Column(String, default="pending")
    admin_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="bookings")
    room = relationship("Room", back_populates="bookings")


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    from_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), name="from_user")
    to_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), name="to_user")
    booking_id = Column(UUID(as_uuid=False), ForeignKey("bookings.id"))
    subject = Column(String)
    content = Column(Text, nullable=False)
    is_from_admin = Column(Boolean, default=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    sender = relationship("User", foreign_keys=[from_user_id], back_populates="sent_messages")
    recipient = relationship("User", foreign_keys=[to_user_id], back_populates="received_messages")


class GalleryImage(Base):
    __tablename__ = "gallery"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    title = Column(String)
    url = Column(String, nullable=False)
    storage_path = Column(String)
    category = Column(String, default="general")
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    uploaded_by = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)


class ContactInquiry(Base):
    __tablename__ = "contact_inquiries"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class SiteContent(Base):
    __tablename__ = "site_content"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    page = Column(String, nullable=False)
    key = Column(String, nullable=False)
    value = Column(Text)
    value_type = Column(String, default="text")  # 'text' or 'image'
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("page", "key", name="site_content_page_key_uq"),
    )
