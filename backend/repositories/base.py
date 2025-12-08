"""
Base Repository

Provides generic database operations for all repositories.
"""

from typing import Generic, TypeVar, Type, List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, desc
from sqlalchemy.orm import DeclarativeBase


ModelType = TypeVar("ModelType", bound=DeclarativeBase)


class BaseRepository(Generic[ModelType]):
    """
    Base repository with common CRUD operations.
    
    Generic repository pattern for type-safe database operations.
    """
    
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        """
        Initialize repository.
        
        Args:
            model: SQLAlchemy model class
            session: Database session
        """
        self.model = model
        self.session = session
    
    async def create(self, **kwargs) -> ModelType:
        """
        Create a new record.
        
        Args:
            **kwargs: Model field values
            
        Returns:
            Created model instance
        """
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance
    
    async def get_by_id(self, id: Any) -> Optional[ModelType]:
        """
        Get record by ID.
        
        Args:
            id: Record ID
            
        Returns:
            Model instance or None
        """
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        limit: Optional[int] = None,
        offset: int = 0,
        order_by: Optional[str] = None
    ) -> List[ModelType]:
        """
        Get all records with pagination.
        
        Args:
            limit: Maximum number of records
            offset: Number of records to skip
            order_by: Column name to order by
            
        Returns:
            List of model instances
        """
        query = select(self.model)
        
        if order_by:
            if order_by.startswith("-"):
                # Descending order
                col = order_by[1:]
                query = query.order_by(desc(getattr(self.model, col)))
            else:
                # Ascending order
                query = query.order_by(getattr(self.model, order_by))
        
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def update(self, id: Any, **kwargs) -> Optional[ModelType]:
        """
        Update a record.
        
        Args:
            id: Record ID
            **kwargs: Fields to update
            
        Returns:
            Updated model instance or None
        """
        await self.session.execute(
            update(self.model)
            .where(self.model.id == id)
            .values(**kwargs)
        )
        await self.session.commit()
        return await self.get_by_id(id)
    
    async def delete(self, id: Any) -> bool:
        """
        Delete a record.
        
        Args:
            id: Record ID
            
        Returns:
            True if deleted, False if not found
        """
        result = await self.session.execute(
            delete(self.model).where(self.model.id == id)
        )
        await self.session.commit()
        return result.rowcount > 0
    
    async def filter(self, **filters) -> List[ModelType]:
        """
        Filter records by criteria.
        
        Args:
            **filters: Filter criteria (field=value)
            
        Returns:
            List of matching model instances
        """
        query = select(self.model)
        for key, value in filters.items():
            query = query.where(getattr(self.model, key) == value)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def count(self, **filters) -> int:
        """
        Count records matching criteria.
        
        Args:
            **filters: Filter criteria
            
        Returns:
            Number of matching records
        """
        from sqlalchemy import func
        
        query = select(func.count()).select_from(self.model)
        for key, value in filters.items():
            query = query.where(getattr(self.model, key) == value)
        
        result = await self.session.execute(query)
        return result.scalar() or 0
