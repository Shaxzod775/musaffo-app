from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class NewsContent(BaseModel):
    ru: str
    uz: str
    en: str

class News(BaseModel):
    id: Optional[str] = None
    titleKey: str
    title: str
    category: str
    content: NewsContent
    imageUrl: str
    timestamp: Optional[datetime] = None
    createdAt: Optional[datetime] = None

class Donation(BaseModel):
    id: Optional[str] = None
    userId: str
    amount: int
    currency: str = "UZS"
    projectId: Optional[str] = None
    status: str = "completed"  # pending, completed, failed
    timestamp: Optional[datetime] = None

class Donor(BaseModel):
    id: Optional[str] = None
    name: str
    totalDonated: int = 0
    isContributor: bool = True
    donations: List[str] = []
    createdAt: Optional[datetime] = None
    lastDonation: Optional[datetime] = None

class VoteRecord(BaseModel):
    userId: str
    vote: str  # 'up' or 'down'

class Voting(BaseModel):
    id: Optional[str] = None
    titleKey: str
    title: str
    description: str
    votesFor: int = 0
    votesAgainst: int = 0
    status: str = "active"  # active, closed
    voters: List[VoteRecord] = []
    createdAt: Optional[datetime] = None

class Report(BaseModel):
    id: Optional[str] = None
    userId: Optional[str] = None
    description: str
    location: Optional[str] = None
    photos: List[str] = []
    videos: List[str] = []
    status: str = "pending"  # pending, reviewed, resolved
    createdAt: Optional[datetime] = None

class Project(BaseModel):
    id: Optional[str] = None
    titleKey: str
    title: str
    description: str
    descKey: Optional[str] = None
    targetAmount: int
    currentAmount: int = 0
    status: str  # active, completed, voting
    image: str
    votesFor: Optional[int] = None
    votesAgainst: Optional[int] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
