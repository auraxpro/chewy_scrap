from sqlalchemy import create_engine, Column, String, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL

Base = declarative_base()

class ProductList(Base):
    __tablename__ = 'products_list'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_url = Column(String, unique=True, nullable=False, index=True)
    page_num = Column(Integer, nullable=False)
    scraped = Column(Boolean, default=False, nullable=False)
    product_image_url = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<Product(id={self.id}, url={self.product_url}, page={self.page_num}, scraped={self.scraped})>"

# Create engine and session
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

