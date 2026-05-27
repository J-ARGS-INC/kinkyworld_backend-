from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, EmailStr, field_validator


# ── Auth ─────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AdminLoginRequest(BaseModel):
    key: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


class UserOut(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    phone: Optional[str]
    role: str
    is_active: bool = False
    avatar_url: Optional[str]
    membership_since: Optional[datetime]

    class Config:
        from_attributes = True


class PasswordResetRequest(BaseModel):
    email: EmailStr


# ── Locations ─────────────────────────────────────────────
class LocationOut(BaseModel):
    id: str
    city: str
    country: str
    region: Optional[str]
    address: Optional[str]
    is_active: bool
    rooms_count: int

    class Config:
        from_attributes = True


class LocationCreate(BaseModel):
    city: str
    country: str
    region: Optional[str] = None
    address: Optional[str] = None
    is_active: bool = True
    rooms_count: int = 0


class LocationUpdate(BaseModel):
    city: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None
    rooms_count: Optional[int] = None


# ── Rooms ─────────────────────────────────────────────────
class RoomOut(BaseModel):
    id: str
    name: str
    slug: str
    category: str
    type: str
    description: Optional[str]
    short_description: Optional[str]
    price: float
    original_price: Optional[float]
    price_unit: str
    max_guests: int
    beds: Optional[str]
    amenities: List[str]
    images: List[str]
    is_featured: bool
    is_available: bool
    location_id: Optional[str]

    class Config:
        from_attributes = True


class RoomPriceUpdate(BaseModel):
    price: float


class RoomUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    price: Optional[float] = None
    original_price: Optional[float] = None
    max_guests: Optional[int] = None
    beds: Optional[str] = None
    amenities: Optional[List[str]] = None
    images: Optional[List[str]] = None
    is_featured: Optional[bool] = None
    is_available: Optional[bool] = None


# ── Packages ─────────────────────────────────────────────
class PackageOut(BaseModel):
    id: str
    name: str
    slug: str
    description: Optional[str]
    type: Optional[str]
    duration_days: int
    price: float
    original_price: Optional[float]
    includes: List[str]
    is_featured: bool
    is_active: bool

    class Config:
        from_attributes = True


class PackageUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    original_price: Optional[float] = None
    includes: Optional[List[str]] = None
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None


# ── Bookings ─────────────────────────────────────────────
class BookingCreate(BaseModel):
    room_id: Optional[str] = None
    package_id: Optional[str] = None
    location_id: Optional[str] = None
    booking_type: str
    check_in: datetime
    check_out: datetime
    guests_count: int = 1
    special_requests: Optional[str] = None
    guest_name: str
    guest_email: EmailStr
    guest_phone: Optional[str] = None


class BookingOut(BaseModel):
    id: str
    booking_ref: str
    booking_type: str
    check_in: datetime
    check_out: datetime
    guests_count: int
    guest_name: str
    guest_email: str
    guest_phone: Optional[str]
    total_price: float
    status: str
    special_requests: Optional[str]
    admin_notes: Optional[str]
    room_id: Optional[str]
    package_id: Optional[str]
    location_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class BookingStatusUpdate(BaseModel):
    status: Literal["pending", "confirmed", "cancelled", "rejected", "completed"]
    admin_notes: Optional[str] = None


# ── Messages ─────────────────────────────────────────────
class MessageCreate(BaseModel):
    subject: Optional[str] = None
    content: str
    booking_id: Optional[str] = None


class MessageOut(BaseModel):
    id: str
    from_user_id: Optional[str]
    to_user_id: Optional[str]
    subject: Optional[str]
    content: str
    is_from_admin: bool
    is_read: bool
    created_at: datetime
    sender_name: Optional[str] = None

    class Config:
        from_attributes = True


class AdminReplyCreate(BaseModel):
    to_user_id: str
    subject: Optional[str] = None
    content: str
    booking_id: Optional[str] = None


# ── Gallery ─────────────────────────────────────────────
class GalleryImageOut(BaseModel):
    id: str
    title: Optional[str]
    url: str
    category: str
    sort_order: int
    is_active: bool

    class Config:
        from_attributes = True


# ── Site Content ─────────────────────────────────────────
class SiteContentUpdate(BaseModel):
    value: str
    value_type: Optional[str] = None


# ── Contact Inquiries ─────────────────────────────────────
class ContactInquiryCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    message: str


class ContactInquiryOut(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str]
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


TokenResponse.model_rebuild()
