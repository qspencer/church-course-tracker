"""
Simple test to verify basic functionality
"""

import pytest
from datetime import datetime, date
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Simple test model
class TestPerson(Base):
    __tablename__ = "test_people"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)

def test_create_person(db_session):
    """Test creating a person record"""
    person = TestPerson(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com"
    )
    db_session.add(person)
    db_session.commit()
    
    assert person.id is not None
    assert person.first_name == "John"
    assert person.last_name == "Doe"
    assert person.email == "john.doe@example.com"
    assert person.is_active is True
    assert person.created_at is not None
    assert person.updated_at is not None

def test_get_person(db_session):
    """Test getting a person record"""
    person = TestPerson(
        first_name="Jane",
        last_name="Smith",
        email="jane.smith@example.com"
    )
    db_session.add(person)
    db_session.commit()
    
    # Retrieve the person
    found_person = db_session.query(TestPerson).filter(TestPerson.id == person.id).first()
    
    assert found_person is not None
    assert found_person.first_name == "Jane"
    assert found_person.last_name == "Smith"
    assert found_person.email == "jane.smith@example.com"

def test_update_person(db_session):
    """Test updating a person record"""
    person = TestPerson(
        first_name="Bob",
        last_name="Johnson",
        email="bob.johnson@example.com"
    )
    db_session.add(person)
    db_session.commit()
    
    # Update the person
    person.first_name = "Robert"
    person.email = "robert.johnson@example.com"
    db_session.commit()
    
    # Retrieve and verify
    updated_person = db_session.query(TestPerson).filter(TestPerson.id == person.id).first()
    assert updated_person.first_name == "Robert"
    assert updated_person.email == "robert.johnson@example.com"
    assert updated_person.last_name == "Johnson"  # Unchanged

def test_delete_person(db_session):
    """Test deleting a person record"""
    person = TestPerson(
        first_name="Alice",
        last_name="Brown",
        email="alice.brown@example.com"
    )
    db_session.add(person)
    db_session.commit()
    
    person_id = person.id
    
    # Delete the person
    db_session.delete(person)
    db_session.commit()
    
    # Verify deletion
    deleted_person = db_session.query(TestPerson).filter(TestPerson.id == person_id).first()
    assert deleted_person is None

def test_multiple_people(db_session):
    """Test working with multiple people"""
    people_data = [
        ("John", "Doe", "john@example.com"),
        ("Jane", "Smith", "jane@example.com"),
        ("Bob", "Johnson", "bob@example.com")
    ]
    
    # Create multiple people
    for first_name, last_name, email in people_data:
        person = TestPerson(
            first_name=first_name,
            last_name=last_name,
            email=email
        )
        db_session.add(person)
    
    db_session.commit()
    
    # Retrieve all people
    all_people = db_session.query(TestPerson).all()
    assert len(all_people) == 3
    
    # Verify data
    names = [(p.first_name, p.last_name) for p in all_people]
    assert ("John", "Doe") in names
    assert ("Jane", "Smith") in names
    assert ("Bob", "Johnson") in names
