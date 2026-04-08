from contextlib import asynccontextmanager
from http import HTTPStatus
from typing import Any, AsyncIterator, Generic

import structlog
from database_manager.blueprints.base_entity import (
    BaseEntityCreateRequestType,
    BaseEntityDeleteRequestType,
    BaseEntityModelType,
    BaseEntityQueryType,
    BaseEntitySearchResponse,
    BaseEntityType,
    BaseEntityUpdateRequestType,
    SearchResponseMetadata,
)
from database_manager.clients.database_client import database_client
from database_manager.utils.transaction_handler import get_current_session
from fastapi.exceptions import HTTPException
from sieve_types.query import SortOrder
from logging_manager.logger import get_logger
from sqlalchemy import UnaryExpression, asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.sql import Select


class BaseEntityStore(
    Generic[
        BaseEntityModelType,
        BaseEntityType,
        BaseEntityQueryType,
        BaseEntityCreateRequestType,
        BaseEntityUpdateRequestType,
        BaseEntityDeleteRequestType,
    ]
):
    entity_model: type[BaseEntityModelType]
    entity: type[BaseEntityType]
    entity_query: type[BaseEntityQueryType]
    entity_create_request: type[BaseEntityCreateRequestType]
    entity_update_request: type[BaseEntityUpdateRequestType]
    entity_delete_request: type[BaseEntityDeleteRequestType]

    selectinload_fields: list[Any] = []

    def __init__(self, logger_override: structlog.stdlib.BoundLogger | None = None):
        self.client = database_client
        if logger_override:
            self.logger = logger_override
        else:
            self.logger = get_logger()

    def convert_model_to_entity(self, model: BaseEntityModelType) -> BaseEntityType:
        return self.entity.model_validate(model.to_dict())

    @asynccontextmanager
    async def _query_session(self) -> AsyncIterator[AsyncSession]:
        """Context manager for query operations. Ensures session cleanup on exceptions."""
        existing_session = get_current_session()
        if existing_session is not None:
            # Use existing session from transaction context (caller manages lifecycle)
            yield existing_session
        else:
            # Create new session and ensure cleanup
            session = database_client.session_maker()
            try:
                yield session
            finally:
                await session.close()

    @asynccontextmanager
    async def _mutation_session(self) -> AsyncIterator[AsyncSession]:
        """Context manager for mutation operations. Handles commit/rollback and cleanup."""
        existing_session = get_current_session()
        if existing_session is not None:
            # Use existing session from transaction context (caller manages lifecycle)
            yield existing_session
        else:
            # Create new session with proper transaction handling
            session = database_client.session_maker()
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    def convert_create_request_to_dict(self, request: BaseEntityCreateRequestType) -> dict[str, Any]:
        """Converts a database entity to the output entity."""
        return request.model_dump()

    def apply_update_to_model(
        self, request: BaseEntityUpdateRequestType, existing_entity: BaseEntityModelType
    ) -> BaseEntityModelType:
        """Converts an update request to an actual update."""
        updates = request.model_dump(exclude_unset=True)
        for field, new_value in updates.items():
            setattr(existing_entity, field, new_value)
        return existing_entity

    async def get_entity_by_id(self, id: int) -> BaseEntityType | None:
        """Fetch an entity by ID"""
        async with self._query_session() as session:
            stmt = select(self.entity_model).where(self.entity_model.id == id)
            if self.selectinload_fields:
                stmt = stmt.options(*self.selectinload_fields)

            result = await session.execute(stmt)
            entity = result.scalar_one_or_none()

            if not entity:
                return None

            return self.convert_model_to_entity(entity)

    async def _get_entity_model_by_id(self, id: int, session: AsyncSession) -> BaseEntityModelType | None:
        """Fetch an entity by ID"""
        if not id:
            return None

        stmt = select(self.entity_model).where(self.entity_model.id == id)
        if self.selectinload_fields:
            stmt = stmt.options(*self.selectinload_fields)

        result = await session.execute(stmt)
        entity = result.scalar_one_or_none()
        return entity

    def _apply_base_search(
        self, query: BaseEntityQueryType, stmt: Select[tuple[BaseEntityModelType]]
    ) -> Select[tuple[BaseEntityModelType]]:
        """Search specific filters."""
        return stmt

    def _apply_entity_specific_search(
        self, query: BaseEntityQueryType, stmt: Select[tuple[BaseEntityModelType]]
    ) -> Select[tuple[BaseEntityModelType]]:
        """Search specific filters."""
        # We allow the specific stores to override this, but don't throw an exception
        # in case the service doesn't override
        return stmt

    def create_search_response_metadata(self, query: BaseEntityQueryType, total_count: int) -> SearchResponseMetadata:
        return SearchResponseMetadata(total_count=total_count, offset=query.offset, limit=query.limit)

    async def search_entities(self, query: BaseEntityQueryType) -> BaseEntitySearchResponse[BaseEntityType]:
        """Search entities with filtering and pagination"""
        async with self._query_session() as session:
            stmt = select(self.entity_model)
            if self.selectinload_fields:
                stmt = stmt.options(*self.selectinload_fields)

            stmt = self._apply_base_search(query, stmt)
            stmt = self._apply_entity_specific_search(query, stmt)

            # Get total count
            count_stmt = select(func.count()).select_from(stmt.subquery())
            count_result = await session.execute(count_stmt)
            total_count = count_result.scalar() or 0

            # Apply sorting
            if query.sort_order and query.sort_by:
                order_by_func: UnaryExpression[Any] = (
                    asc(query.sort_by) if query.sort_order == SortOrder.asc else desc(query.sort_by)
                )
                stmt = stmt.order_by(order_by_func)

            # Apply pagination
            stmt = stmt.limit(query.limit).offset(query.offset)

            result = await session.execute(stmt)
            entities = result.scalars().all()

            converted_results = [self.convert_model_to_entity(a) for a in entities]
            return BaseEntitySearchResponse[BaseEntityType](
                entities=converted_results,
                metadata=self.create_search_response_metadata(query, total_count),
            )

    def get_conflict_columns(self) -> list[InstrumentedAttribute[Any]]:
        return [self.entity_model.id]

    async def _after_create(
        self,
        request: BaseEntityCreateRequestType,
        entity_model: BaseEntityModelType,
        session: AsyncSession,
    ) -> None:
        """Hook for subclasses to add post-create logic (e.g., association tables)."""
        pass

    async def create_entity(self, request: BaseEntityCreateRequestType) -> BaseEntityType:
        """Create an entity (simple insert)"""
        async with self._mutation_session() as session:
            # Create a new model instance from the request
            entity_model = self.entity_model(**self.convert_create_request_to_dict(request))
            session.add(entity_model)
            await session.flush()  # Ensures the entity gets an ID if it's auto-incremented

            # Allow subclasses to add post-create logic
            await self._after_create(request, entity_model, session)

            # Re-fetch with selectinload to avoid lazy loading issues in async context
            if self.selectinload_fields:
                stmt = select(self.entity_model).where(self.entity_model.id == entity_model.id)
                stmt = stmt.options(*self.selectinload_fields)
                result = await session.execute(stmt)
                entity_model = result.scalar_one()

            return self.convert_model_to_entity(entity_model)

    async def _after_update(
        self,
        request: BaseEntityUpdateRequestType,
        entity_model: BaseEntityModelType,
        session: AsyncSession,
    ) -> None:
        """Hook for subclasses to add post-update logic (e.g., association tables)."""
        pass

    async def update_entity(self, request: BaseEntityUpdateRequestType) -> BaseEntityType:
        """Update an entity"""
        async with self._mutation_session() as session:
            existing_entity = await self._get_entity_model_by_id(request.id, session)
            if not existing_entity:
                raise HTTPException(HTTPStatus.NOT_FOUND, "No entity with ID found")
            updated_entity = self.apply_update_to_model(request, existing_entity)
            session.add(updated_entity)
            await session.flush()

            # Allow subclasses to add post-update logic
            await self._after_update(request, updated_entity, session)

            # Re-fetch with selectinload to get updated relationships
            if self.selectinload_fields:
                stmt = select(self.entity_model).where(self.entity_model.id == updated_entity.id)
                stmt = stmt.options(*self.selectinload_fields)
                result = await session.execute(stmt)
                updated_entity = result.scalar_one()
            else:
                await session.refresh(updated_entity)

            return self.convert_model_to_entity(updated_entity)

    async def handle_backpopulation_deletion(self, entity: BaseEntityModelType, session: AsyncSession):
        pass

    async def delete_entity(self, request: BaseEntityDeleteRequestType) -> BaseEntityType:
        """Delete an entity"""
        async with self._mutation_session() as session:
            existing_entity = await self._get_entity_model_by_id(request.id, session)
            if not existing_entity:
                raise HTTPException(HTTPStatus.NOT_FOUND, "No entity with ID found")

            await self.handle_backpopulation_deletion(existing_entity, session)

            session.add(existing_entity)
            return self.convert_model_to_entity(existing_entity)
