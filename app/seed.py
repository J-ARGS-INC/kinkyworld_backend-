import logging
from sqlalchemy.orm import Session
from .database import SessionLocal
from .auth import hash_password, verify_password
from .config import settings
from . import models

_log = logging.getLogger("kinkyworld.seed")


def run():
    db: Session = SessionLocal()
    try:
        _seed_admin(db)
        _seed_locations(db)
        _seed_rooms(db)
        _seed_packages(db)
        _seed_content(db)
        _seed_testimonials(db)
    finally:
        db.close()


def _seed_admin(db: Session):
    existing = db.query(models.User).filter(models.User.role == "admin").first()
    if existing:
        _log.info(f"Admin already exists — email={existing.email}, skipping seed")
        return
    db.add(models.User(
        email=settings.ADMIN_EMAIL,
        full_name="Admin",
        hashed_password=hash_password(settings.ADMIN_PASSWORD),
        role="admin",
        is_active=True,
    ))
    db.commit()
    _log.info(f"Admin created — email={settings.ADMIN_EMAIL}")


def _seed_locations(db: Session):
    if db.query(models.Location).first():
        return
    locations = [
        ("New York", "USA", "North America", 3),
        ("Los Angeles", "USA", "North America", 2),
        ("London", "UK", "Europe", 3),
        ("Berlin", "Germany", "Europe", 2),
        ("Amsterdam", "Netherlands", "Europe", 2),
        ("Sydney", "Australia", "Oceania", 2),
        ("Toronto", "Canada", "North America", 2),
        ("Taipei", "Taiwan", "Asia", 1),
        ("Mexico City", "Mexico", "Latin America", 2),
    ]
    for city, country, region, rooms_count in locations:
        db.add(models.Location(city=city, country=country, region=region, rooms_count=rooms_count))
    db.commit()


def _seed_rooms(db: Session):
    if db.query(models.Room).first():
        return
    rooms = [
        {
            "name": "Standard Twin Suite",
            "slug": "standard-twin",
            "category": "standard",
            "type": "hotel",
            "description": "Dark luxury twin suite with premium linens and climate control.",
            "short_description": "Dark luxury for two. Elegant and discreet.",
            "price": 150000,
            "original_price": 180000,
            "max_guests": 2,
            "beds": "2 Single Beds",
            "price_unit": "night",
            "is_featured": False,
        },
        {
            "name": "Standard King Suite",
            "slug": "standard-king",
            "category": "standard",
            "type": "hotel",
            "description": "King suite with marble bathroom and Egyptian cotton sheets.",
            "short_description": "Spacious king suite with premium amenities.",
            "price": 200000,
            "original_price": 250000,
            "max_guests": 2,
            "beds": "1 King Bed",
            "price_unit": "night",
            "is_featured": False,
        },
        {
            "name": "Deluxe Suite",
            "slug": "deluxe-river-view",
            "category": "deluxe",
            "type": "hotel",
            "description": "Premium deluxe suite with panoramic views and deep soaking tub.",
            "short_description": "Premium views and five-star comfort.",
            "price": 350000,
            "original_price": 400000,
            "max_guests": 2,
            "beds": "1 King Bed",
            "price_unit": "night",
            "is_featured": True,
        },
        {
            "name": "Executive Suite",
            "slug": "executive-suite",
            "category": "suite",
            "type": "hotel",
            "description": "Separate living area and butler service for the discerning guest.",
            "short_description": "Separate living area with butler service.",
            "price": 600000,
            "original_price": 750000,
            "max_guests": 3,
            "beds": "1 King + Sofa Bed",
            "price_unit": "night",
            "is_featured": True,
        },
        {
            "name": "The Main Room",
            "slug": "main-room",
            "category": "dungeon",
            "type": "dungeon",
            "description": "Premium BDSM playroom with St. Andrew's Cross, bondage chair, cage and full toy chest.",
            "short_description": "Full bondage furniture and comprehensive toy chest.",
            "price": 410,
            "original_price": 500,
            "max_guests": 4,
            "beds": "Dungeon Setup",
            "price_unit": "day",
            "is_featured": True,
        },
        {
            "name": "The Dungeon",
            "slug": "the-dungeon",
            "category": "dungeon",
            "type": "dungeon",
            "description": "The ultimate immersive dungeon experience with surprise elements and advanced BDSM installations.",
            "short_description": "The ultimate immersive dungeon experience.",
            "price": 500,
            "original_price": 600,
            "max_guests": 4,
            "beds": "Dungeon Setup",
            "price_unit": "day",
            "is_featured": True,
        },
    ]
    for r in rooms:
        db.add(models.Room(**r, amenities=[], images=[]))
    db.commit()


def _seed_packages(db: Session):
    if db.query(models.Package).first():
        return
    packages = [
        ("Main Room Day Pass", "main-room-day", "dungeon", 1, 410, False),
        ("Dungeon Day Pass", "dungeon-day", "dungeon", 1, 500, True),
        ("Main Room Weekend", "main-room-2day", "dungeon", 2, 700, False),
        ("Dungeon Weekend VIP", "dungeon-2day", "dungeon", 2, 800, False),
        ("Hotel Suite Stay", "hotel-suite", "hotel", 1, 350, False),
        ("Ultimate VIP Experience", "combined-vip", "combined", 2, 1100, True),
    ]
    for name, slug, ptype, days, price, featured in packages:
        db.add(models.Package(
            name=name, slug=slug, type=ptype,
            duration_days=days, price=price, is_featured=featured,
            includes=[],
        ))
    db.commit()


def _seed_content(db: Session):
    if db.query(models.SiteContent).first():
        return
    entries = [
        ("home", "hero_title", "Welcome to Kinky World", "text"),
        ("home", "hero_subtitle", "Exclusive Dungeons & Luxury Hotels — Discreet, Premium, Unforgettable.", "text"),
        ("home", "announcement", "", "text"),
        ("home", "featured_title", "Featured Experiences", "text"),
        ("home", "cta_title", "Ready for the Experience?", "text"),
        ("home", "cta_subtitle", "Book your exclusive stay today. Complete discretion guaranteed.", "text"),
        ("rooms", "hero_title", "Our Rooms & Suites", "text"),
        ("rooms", "hero_subtitle", "From opulent hotel suites to fully equipped dungeon playrooms.", "text"),
        ("packages", "hero_title", "VIP Packages", "text"),
        ("packages", "hero_subtitle", "Curated experiences for the discerning guest.", "text"),
        ("dungeon", "hero_title", "The Dungeon Experience", "text"),
        ("dungeon", "hero_subtitle", "Enter a world of controlled intensity.", "text"),
        ("about", "hero_title", "About Kinky World", "text"),
        ("about", "body_text", "Kinky World is a premier luxury destination blending high-end hotel accommodations with exclusive dungeon facilities. Founded on the principles of discretion, consent, and luxury.", "text"),
        ("gym", "hero_title", "ZENRGY Gym & Sauna", "text"),
        ("gym", "hero_subtitle", "Premium fitness facility for hotel guests.", "text"),
    ]
    for page, key, value, vtype in entries:
        db.add(models.SiteContent(page=page, key=key, value=value, value_type=vtype))
    db.commit()


def _seed_testimonials(db: Session):
    if db.query(models.Testimonial).first():
        return
    testimonials = [
        {
            "name": "A. Blackwood",
            "role": "Member — New York, USA",
            "quote": "The dungeon suite exceeded every expectation. Fully equipped, immaculately clean, and the staff's discretion was impeccable. The St. Andrew's Cross alone is worth every cent.",
            "rating": 5,
            "sort_order": 0,
        },
        {
            "name": "S. Mercer",
            "role": "Member — London, UK",
            "quote": "We booked the 2-day hotel + dungeon package. The complimentary champagne on arrival, the premium suite, and the private dungeon access made for an unforgettable weekend.",
            "rating": 5,
            "sort_order": 1,
        },
        {
            "name": "V. Hartmann",
            "role": "Member — Berlin, Germany",
            "quote": "What sets Kinky World apart is the absolute privacy and professionalism. No judgement, only luxury. The Main Room's equipment is top-tier and the surprise elements in the dungeon are extraordinary.",
            "rating": 5,
            "sort_order": 2,
        },
    ]
    for t in testimonials:
        db.add(models.Testimonial(**t))
    db.commit()
