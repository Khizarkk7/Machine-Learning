from pydantic import BaseModel, Field, field_validator, ConfigDict
from fastapi import FastAPI, HTTPException, status, Depends, Query 
from typing import List, Optional, Dict, Any, Annotated
from datetime import datetime
import uuid
import logging
from enum import Enum
from contextlib import asynccontextmanager

# ==================== CONFIGURATION ====================
class Config:
    """Application configuration"""
    API_VERSION = "1.0.0"
    API_TITLE = "Book Management API"
    API_DESCRIPTION = "A scalable API for managing book inventory"
    MAX_TITLE_LENGTH = 200
    MAX_AUTHOR_LENGTH = 100
    MIN_YEAR = 1000
    MAX_PRICE = 1000000  # Prevent unrealistic prices

# ==================== LOGGING ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== ENUMS ====================
class SortField(str, Enum):
    """Fields available for sorting"""
    TITLE = "title"
    AUTHOR = "author"
    PRICE = "price"
    PUBLISHED_YEAR = "published_year"
    CREATED_AT = "created_at"

class SortOrder(str, Enum):
    """Sorting order options"""
    ASC = "asc"
    DESC = "desc"

# ==================== MODELS ====================
class BookBase(BaseModel):
    """Base book model with validation"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "The Great Gatsby",
                "aux_year": 1925
            }
        }
    )
    
    title: str = Field(
        ...,
        min_length=1,
        max_length=Config.MAX_TITLE_LENGTH,
        description="Title of the book"
    )
    author: str = Field(
        ...,
        min_length=1,
        max_length=Config.MAX_AUTHOR_LENGTH,
        description="Author of the book"
    )
    price: float = Field(
        ...,
        gt=0,
        le=Config.MAX_PRICE,
        description="Price of the book (must be greater than 0)"
    )
    in_stock: bool = Field(
        True,
        description="Whether the book is in stock"
    )
    published_year: Optional[int] = Field(
        None,
        ge=Config.MIN_YEAR,
        le=datetime.now().year,
        description="Year the book was published"
    )
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, value: float) -> float:
        """Validate price is reasonable"""
        if value <= 0:
            raise ValueError('Price must be greater than 0')
        if value > Config.MAX_PRICE:
            raise ValueError(f'Price cannot exceed {Config.MAX_PRICE}')
        return round(value, 2)  # Round to 2 decimal places
    
    @field_validator('published_year')
    @classmethod
    def validate_published_year(cls, value: Optional[int]) -> Optional[int]:
        """Validate published year"""
        if value is not None and value > datetime.now().year:
            raise ValueError('Published year cannot be in the future')
        return value

class BookCreate(BookBase):
    """Model for creating a book"""
    pass

class BookUpdate(BaseModel):
    """Model for updating a book (all fields optional)"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Updated Title",
                "price": 15.99,
                "in_stock": False
            }
        }
    )
    
    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=Config.MAX_TITLE_LENGTH
    )
    author: Optional[str] = Field(
        None,
        min_length=1,
        max_length=Config.MAX_AUTHOR_LENGTH
    )
    price: Optional[float] = Field(
        None,
        gt=0,
        le=Config.MAX_PRICE
    )
    in_stock: Optional[bool] = None
    published_year: Optional[int] = Field(
        None,
        ge=Config.MIN_YEAR,
        le=datetime.now().year
    )

class BookResponse(BookBase):
    """Response model for book operations"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(..., description="Unique identifier for the book")
    created_at: datetime = Field(..., description="When the book was created")
    updated_at: datetime = Field(..., description="When the book was last updated")

# ==================== DATA LAYER ====================
class BookRepository:
    """Repository pattern for data access"""
    
    def __init__(self):
        """Initialize in-memory storage"""
        self._books: Dict[str, Dict] = {}
        self._indexes = {
            'author': {},
            'published_year': {},
            'in_stock': set()
        }
        logger.info("Book repository initialized")
    
    def _update_indexes(self, book_id: str, book_data: Dict):
        """Update search indexes"""
        # Index by author
        author = book_data.get('author')
        if author:
            if author not in self._indexes['author']:
                self._indexes['author'][author] = set()
            self._indexes['author'][author].add(book_id)
        
        # Index by published year
        year = book_data.get('published_year')
        if year:
            if year not in self._indexes['published_year']:
                self._indexes['published_year'][year] = set()
            self._indexes['published_year'][year].add(book_id)
        
        # Index by stock status
        if book_data.get('in_stock'):
            self._indexes['in_stock'].add(book_id)
        elif book_id in self._indexes['in_stock']:
            self._indexes['in_stock'].remove(book_id)
    
    def _remove_from_indexes(self, book_id: str, old_book: Dict):
        """Remove book from indexes"""
        author = old_book.get('author')
        if author and author in self._indexes['author']:
            self._indexes['author'][author].discard(book_id)
        
        year = old_book.get('published_year')
        if year and year in self._indexes['published_year']:
            self._indexes['published_year'][year].discard(book_id)
        
        self._indexes['in_stock'].discard(book_id)
    
    def create(self, book_data: Dict) -> Dict:
        """Create a new book"""
        book_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        book = {
            **book_data,
            'id': book_id,
            'created_at': timestamp,
            'updated_at': timestamp
        }
        
        self._books[book_id] = book
        self._update_indexes(book_id, book)
        
        logger.info(f"Book created: {book_id}")
        return book
    
    def get(self, book_id: str) -> Optional[Dict]:
        """Get a book by ID"""
        return self._books.get(book_id)
    
    def get_all(self) -> List[Dict]:
        """Get all books"""
        return list(self._books.values())
    
    def update(self, book_id: str, update_data: Dict) -> Optional[Dict]:
        """Update a book"""
        if book_id not in self._books:
            return None
        
        old_book = self._books[book_id]
        self._remove_from_indexes(book_id, old_book)
        
        # Update book data
        updated_book = {**old_book, **update_data, 'updated_at': datetime.now()}
        self._books[book_id] = updated_book
        
        # Update indexes with new data
        self._update_indexes(book_id, updated_book)
        
        logger.info(f"Book updated: {book_id}")
        return updated_book
    
    def delete(self, book_id: str) -> bool:
        """Delete a book"""
        if book_id not in self._books:
            return False
        
        old_book = self._books[book_id]
        self._remove_from_indexes(book_id, old_book)
        del self._books[book_id]
        
        logger.info(f"Book deleted: {book_id}")
        return True
    
    def search(self, query: str) -> List[Dict]:
        """Search books by title or author"""
        query = query.lower()
        results = []
        
        for book in self._books.values():
            if (query in book['title'].lower() or 
                query in book['author'].lower()):
                results.append(book)
        
        return results
    
    def filter_by(self, 
                  author: Optional[str] = None,
                  in_stock: Optional[bool] = None,
                  min_price: Optional[float] = None,
                  max_price: Optional[float] = None,
                  min_year: Optional[int] = None,
                  max_year: Optional[int] = None) -> List[Dict]:
        """Filter books by various criteria"""
        results = []
        
        for book in self._books.values():
            # Apply filters
            if author and author.lower() not in book['author'].lower():
                continue
            if in_stock is not None and book['in_stock'] != in_stock:
                continue
            if min_price is not None and book['price'] < min_price:
                continue
            if max_price is not None and book['price'] > max_price:
                continue
            if min_year is not None and (
                book['published_year'] is None or 
                book['published_year'] < min_year):
                continue
            if max_year is not None and (
                book['published_year'] is None or 
                book['published_year'] > max_year):
                continue
            
            results.append(book)
        
        return results
    
    def sort_books(self, books: List[Dict], 
                   sort_by: SortField = SortField.CREATED_AT,
                   order: SortOrder = SortOrder.DESC) -> List[Dict]:
        """Sort books by specified field and order"""
        reverse = (order == SortOrder.DESC)
        
        def get_sort_key(book: Dict) -> Any:
            value = book.get(sort_by.value)
            # Handle None values for sorting
            if value is None:
                return "" if sort_by in [SortField.TITLE, SortField.AUTHOR] else 0
            return value
        
        return sorted(books, key=get_sort_key, reverse=reverse)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about books"""
        if not self._books:
            return {
                "total_books": 0,
                "total_value": 0,
                "in_stock": 0,
                "out_of_stock": 0,
                "average_price": 0
            }
        
        total_value = sum(book['price'] for book in self._books.values())
        in_stock_count = sum(1 for book in self._books.values() if book['in_stock'])
        
        return {
            "total_books": len(self._books),
            "total_value": round(total_value, 2),
            "in_stock": in_stock_count,
            "out_of_stock": len(self._books) - in_stock_count,
            "average_price": round(total_value / len(self._books), 2)
        }

# ==================== SERVICE LAYER ====================
class BookService:
    """Service layer for business logic"""
    
    def __init__(self, repository: BookRepository):
        self.repository = repository
        logger.info("Book service initialized")
    
    def create_book(self, book_create: BookCreate) -> BookResponse:
        """Create a new book with validation"""
        book_data = book_create.model_dump()
        created_book = self.repository.create(book_data)
        return BookResponse(**created_book)
    
    def get_book(self, book_id: str) -> BookResponse:
        """Get a book by ID"""
        book = self.repository.get(book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with ID {book_id} not found"
            )
        return BookResponse(**book)
    
    def get_all_books(self, 
                      skip: int = 0,
                      limit: int = 100,
                      sort_by: SortField = SortField.CREATED_AT,
                      order: SortOrder = SortOrder.DESC) -> List[BookResponse]:
        """Get all books with pagination and sorting"""
        all_books = self.repository.get_all()
        sorted_books = self.repository.sort_books(all_books, sort_by, order)
        
        # Apply pagination
        paginated_books = sorted_books[skip:skip + limit]
        
        return [BookResponse(**book) for book in paginated_books]
    
    def update_book(self, book_id: str, book_update: BookUpdate) -> BookResponse:
        """Update a book"""
        update_data = book_update.model_dump(exclude_unset=True)
        
        updated_book = self.repository.update(book_id, update_data)
        if not updated_book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with ID {book_id} not found"
            )
        
        return BookResponse(**updated_book)
    
    def delete_book(self, book_id: str) -> Dict[str, str]:
        """Delete a book"""
        if not self.repository.delete(book_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with ID {book_id} not found"
            )
        
        return {"message": f"Book with ID {book_id} deleted successfully"}
    
    def search_books(self, query: str) -> List[BookResponse]:
        """Search books by title or author"""
        results = self.repository.search(query)
        return [BookResponse(**book) for book in results]
    
    def filter_books(self,
                     author: Optional[str] = None,
                     in_stock: Optional[bool] = None,
                     min_price: Optional[float] = None,
                     max_price: Optional[float] = None,
                     min_year: Optional[int] = None,
                     max_year: Optional[int] = None,
                     sort_by: SortField = SortField.TITLE,
                     order: SortOrder = SortOrder.ASC) -> List[BookResponse]:
        """Filter books with various criteria"""
        filtered_books = self.repository.filter_by(
            author=author,
            in_stock=in_stock,
            min_price=min_price,
            max_price=max_price,
            min_year=min_year,
            max_year=max_year
        )
        
        sorted_books = self.repository.sort_books(filtered_books, sort_by, order)
        return [BookResponse(**book) for book in sorted_books]
    
    def get_book_stats(self) -> Dict[str, Any]:
        """Get book statistics"""
        return self.repository.get_stats()

# ==================== DEPENDENCIES ====================
def get_repository() -> BookRepository:
    """Dependency to get book repository"""
    return BookRepository()

def get_service(repository: BookRepository = Depends(get_repository)) -> BookService:
    """Dependency to get book service"""
    return BookService(repository)

# ==================== LIFESPAN MANAGEMENT ====================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    # Startup
    logger.info("Starting Book Management API...")
    
    # Initialize with sample data
    repository = get_repository()
    service = BookService(repository)
    
    # Add sample books
    sample_books = [
        BookCreate(
            title="The Great Gatsby",
            author="F. Scott Fitzgerald",
            price=12.99,
            in_stock=True,
            published_year=1925
        ),
        BookCreate(
            title="To Kill a Mockingbird",
            author="Harper Lee",
            price=14.99,
            in_stock=True,
            published_year=1960
        ),
        BookCreate(
            title="1984",
            author="George Orwell",
            price=10.99,
            in_stock=False,
            published_year=1949
        ),
        BookCreate(
            title="Pride and Prejudice",
            author="Jane Austen",
            price=9.99,
            in_stock=True,
            published_year=1813
        ),
        BookCreate(
            title="The Hobbit",
            author="J.R.R. Tolkien",
            price=15.99,
            in_stock=True
        )
    ]
    
    for book in sample_books:
        service.create_book(book)
    
    logger.info(f"Initialized with {len(repository.get_all())} sample books")
    logger.info("API is ready to accept requests")
    
    yield  # App is running
    
    # Shutdown
    logger.info("Shutting down Book Management API...")

# ==================== FASTAPI APPLICATION ====================
app = FastAPI(
    title=Config.API_TITLE,
    description=Config.API_DESCRIPTION,
    version=Config.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# ==================== MIDDLEWARE ====================
@app.middleware("http")
async def log_requests(request, call_next):
    """Middleware to log all requests"""
    logger.info(f"Request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response

# ==================== API ENDPOINTS ====================
@app.get("/", tags=["Root"])
async def root():
    """API root endpoint"""
    return {
        "message": "Welcome to Book Management API",
        "version": Config.API_VERSION,
        "docs": "/docs",
        "endpoints": [
            {"GET /books": "Get all books with filtering and sorting"},
            {"POST /books": "Create a new book"},
            {"GET /books/{id}": "Get a specific book"},
            {"PUT /books/{id}": "Update a book"},
            {"DELETE /books/{id}": "Delete a book"},
            {"GET /books/search/{query}": "Search books by title or author"},
            {"GET /books/stats": "Get book statistics"}
        ]
    }

@app.post("/books/", 
          response_model=BookResponse,
          status_code=status.HTTP_201_CREATED,
          tags=["Books"],
          summary="Create a new book")
async def create_book(
    book: BookCreate,
    service: BookService = Depends(get_service)
):
    """
    Create a new book with the following information:
    
    - **title**: Title of the book (required)
    - **author**: Author of the book (required)
    - **price**: Price (must be greater than 0)
    - **in_stock**: Stock status (default: True)
    - **published_year**: Optional publication year
    """
    return service.create_book(book)

@app.get("/books/", 
         response_model=List[BookResponse],
         tags=["Books"],
         summary="Get all books")
async def get_all_books(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    sort_by: SortField = Query(SortField.CREATED_AT, description="Field to sort by"),
    order: SortOrder = Query(SortOrder.DESC, description="Sort order"),
    service: BookService = Depends(get_service)
):
    """
    Get all books with pagination and sorting options.
    
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return (1-1000)
    - **sort_by**: Field to sort by (title, author, price, published_year, created_at)
    - **order**: Sort order (asc or desc)
    """
    return service.get_all_books(skip, limit, sort_by, order)

@app.get("/books/filter", 
         response_model=List[BookResponse],
         tags=["Books"],
         summary="Filter books")
async def filter_books(
    author: Optional[str] = Query(None, description="Filter by author (partial match)"),
    in_stock: Optional[bool] = Query(None, description="Filter by stock status"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    min_year: Optional[int] = Query(None, ge=Config.MIN_YEAR, description="Minimum published year"),
    max_year: Optional[int] = Query(None, le=datetime.now().year, description="Maximum published year"),
    sort_by: SortField = Query(SortField.TITLE, description="Field to sort by"),
    order: SortOrder = Query(SortOrder.ASC, description="Sort order"),
    service: BookService = Depends(get_service)
):
    """
    Filter books by various criteria with sorting options.
    
    All filters are optional. Combine multiple filters for precise results.
    """
    return service.filter_books(
        author=author,
        in_stock=in_stock,
        min_price=min_price,
        max_price=max_price,
        min_year=min_year,
        max_year=max_year,
        sort_by=sort_by,
        order=order
    )

@app.get("/books/{book_id}", 
         response_model=BookResponse,
         tags=["Books"],
         summary="Get a book by ID")
async def get_book(
    book_id: str,
    service: BookService = Depends(get_service)
):
    """
    Get a specific book by its unique ID.
    
    - **book_id**: The unique identifier of the book
    """
    return service.get_book(book_id)

@app.put("/books/{book_id}", 
         response_model=BookResponse,
         tags=["Books"],
         summary="Update a book")
async def update_book(
    book_id: str,
    book_update: BookUpdate,
    service: BookService = Depends(get_service)
):
    """
    Update a book's information.
    
    - **book_id**: The unique identifier of the book to update
    - All fields are optional - only provided fields will be updated
    """
    return service.update_book(book_id, book_update)

@app.delete("/books/{book_id}", 
            tags=["Books"],
            summary="Delete a book")
async def delete_book(
    book_id: str,
    service: BookService = Depends(get_service)
):
    """
    Delete a book by its ID.
    
    - **book_id**: The unique identifier of the book to delete
    """
    return service.delete_book(book_id)

@app.get("/books/search/{query}", 
         response_model=List[BookResponse],
         tags=["Search"],
         summary="Search books")
async def search_books(
    query: str,
    service: BookService = Depends(get_service)
):
    """
    Search books by title or author (case-insensitive partial match).
    
    - **query**: Search term to match against book titles and authors
    """
    return service.search_books(query)

@app.get("/books/stats", 
         tags=["Analytics"],
         summary="Get book statistics")
async def get_stats(
    service: BookService = Depends(get_service)
):
    """
    Get statistics about the book collection.
    
    Returns:
    - Total number of books
    - Total inventory value
    - Number of books in stock
    - Number of books out of stock
    - Average book price
    """
    return service.get_book_stats()

# ==================== HEALTH CHECK ====================
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": Config.API_TITLE
    }

# ==================== ERROR HANDLERS ====================
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    logger.error(f"HTTP error: {exc.status_code} - {exc.detail}")
    return {
        "error": {
            "status_code": exc.status_code,
            "detail": exc.detail,
            "path": request.url.path
        }
    }

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unexpected error: {str(exc)}")
    return {
        "error": {
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "detail": "An unexpected error occurred",
            "path": request.url.path
        }
    }

# ==================== MAIN ENTRY POINT ====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)