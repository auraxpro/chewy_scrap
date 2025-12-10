from sqlalchemy import create_engine, Column, String, Integer, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from config import DATABASE_URL

Base = declarative_base()

class ProductList(Base):
    __tablename__ = 'products_list'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_url = Column(String, unique=True, nullable=False, index=True)
    page_num = Column(Integer, nullable=False)
    scraped = Column(Boolean, default=False, nullable=False)
    skipped = Column(Boolean, default=False, nullable=False, index=True)
    product_image_url = Column(String, nullable=True)
    
    # Relationship to ProductDetails
    details = relationship("ProductDetails", back_populates="product", uselist=False)
    
    def __repr__(self):
        return f"<Product(id={self.id}, url={self.product_url}, page={self.page_num}, scraped={self.scraped})>"

class ProductDetails(Base):
    __tablename__ = 'product_details'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products_list.id'), unique=True, nullable=False, index=True)
    
    # Basic information (copied from product list)
    product_category = Column(String, nullable=True)
    product_name = Column(String, nullable=True)
    img_link = Column(String, nullable=True)  # copied from product list
    product_url = Column(String, nullable=True)  # copied from product list
    
    # Scraped details
    price = Column(String, nullable=True)
    size = Column(String, nullable=True)
    details = Column(Text, nullable=True)
    more_details = Column(Text, nullable=True)
    specifications = Column(Text, nullable=True)
    ingredients = Column(Text, nullable=True)
    caloric_content = Column(Text, nullable=True)
    guaranteed_analysis = Column(Text, nullable=True)
    feeding_instructions = Column(Text, nullable=True)
    transition_instructions = Column(Text, nullable=True)
    
    # Relationship back to ProductList
    product = relationship("ProductList", back_populates="details")
    
    def __repr__(self):
        return f"<ProductDetails(id={self.id}, product_id={self.product_id}, name={self.product_name})>"

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

