"""
Domain Models for URL shortening service
SQLModel entities with validation and business logic
"""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class URLBase(SQLModel):
    """Base URL model with shared fields"""
    short_code: str = Field(
        min_length=4,
        max_length=8,
        regex=r'^[A-Za-z0-9]+$',
        description="Base62 short code"
    )
    original_url: str = Field(
        max_length=2048,
        description="Original long URL"
    )
    title: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional page title"
    )
    is_active: bool = Field(
        default=True,
        description="Whether URL is active and can be accessed"
    )


class URL(URLBase, table=True):
    """URL table model for database"""
    __tablename__ = "urls"

    id: Optional[str] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(None)

    # Performance tracking
    click_count: int = Field(default=0, ge=0)
    last_clicked_at: Optional[datetime] = Field(None)

    # User tracking (for future auth)
    user_id: Optional[str] = Field(None)

    # Analytics optimization
    domain: Optional[str] = Field(None, max_length=255)

    def is_expired(self) -> bool:
        """Check if URL is expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    def can_redirect(self) -> bool:
        """Check if URL can be used for redirection"""
        return self.is_active and not self.is_expired()


class URLCreate(SQLModel):
    """Model for creating new URLs"""
    original_url: str = Field(
        max_length=2048,
        description="Original long URL"
    )
    title: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional page title"
    )
    is_active: bool = Field(
        default=True,
        description="Whether URL is active and can be accessed"
    )


class URLResponse(URLBase):
    """Model for URL API responses"""
    id: str
    created_at: datetime
    click_count: int
    last_clicked_at: Optional[datetime]
    domain: Optional[str]


class ClickBase(SQLModel):
    """Base Click model for analytics"""
    url_id: str = Field(description="URL ID reference")
    short_code: str = Field(description="Short code for performance")

    # Request metadata
    ip_address: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = Field(None)
    referer: Optional[str] = Field(None)

    # Parsed analytics data
    country_code: Optional[str] = Field(None, max_length=2)
    country_name: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)

    # Device detection
    device_type: Optional[str] = Field(None, max_length=20)
    browser_name: Optional[str] = Field(None, max_length=50)
    os_name: Optional[str] = Field(None, max_length=50)

    # Traffic source analysis
    referrer_domain: Optional[str] = Field(None, max_length=255)
    referrer_type: Optional[str] = Field(None, max_length=20)


class Click(ClickBase, table=True):
    """Click table model for analytics database"""
    __tablename__ = "clicks"

    id: Optional[str] = Field(default=None, primary_key=True)
    clicked_at: datetime = Field(default_factory=datetime.utcnow)
    response_time_ms: Optional[int] = Field(None, ge=0)