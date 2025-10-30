"""
Tests for dependency injection.

Verify that dependencies are properly configured and services are injected correctly.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.api.dependencies import (
    get_crm_service,
    get_scheduler_service,
    get_ai_agent,
    get_email_service,
    get_dashboard_service,
)
from app.services.crm_service import CRMService
from app.services.scheduler_service import SchedulerService
from app.services.ai_agent import AIAgent
from app.services.email_service import EmailService
from app.services.dashboard_service import DashboardService

class TestDependencies:
    """Test cases for dependency injection."""
    
    @pytest.mark.asyncio
    @patch('app.api.dependencies.get_database')
    async def test_get_crm_service(self, mock_get_database):
        """Test that get_crm_service returns a CRMService instance."""
        # Mock database connection
        mock_db = Mock()
        mock_db.clients = Mock()
        mock_get_database.return_value = mock_db
        
        service = await get_crm_service()
        assert isinstance(service, CRMService)
        assert service.db is not None
        assert hasattr(service, 'clients_collection')
    
    @pytest.mark.asyncio
    @patch('app.api.dependencies.get_database')
    async def test_get_scheduler_service(self, mock_get_database):
        """Test that get_scheduler_service returns a SchedulerService instance."""
        # Mock database connection
        mock_db = Mock()
        mock_db.tasks = Mock()
        mock_get_database.return_value = mock_db
        
        service = await get_scheduler_service()
        assert isinstance(service, SchedulerService)
        assert service.db is not None
        assert hasattr(service, 'tasks_collection')
    
    @pytest.mark.asyncio
    async def test_get_ai_agent(self):
        """Test that get_ai_agent returns an AIAgent instance."""
        agent = await get_ai_agent()
        assert isinstance(agent, AIAgent)
        assert hasattr(agent, 'model')
        assert hasattr(agent, 'max_tokens')
    
    @pytest.mark.asyncio
    @patch('app.api.dependencies.get_database')
    async def test_get_email_service(self, mock_get_database):
        """Test that get_email_service returns an EmailService instance."""
        # Mock database connection
        mock_db = Mock()
        mock_db.email_logs = Mock()
        mock_get_database.return_value = mock_db
        
        service = await get_email_service()
        assert isinstance(service, EmailService)
        assert service.db is not None
        assert hasattr(service, 'emails_collection')
    
    @pytest.mark.asyncio
    @patch('app.api.dependencies.get_database')
    async def test_get_dashboard_service(self, mock_get_database):
        """Test that get_dashboard_service returns a DashboardService instance."""
        # Mock database connection
        mock_db = Mock()
        mock_db.clients = Mock()
        mock_db.tasks = Mock()
        mock_db.email_logs = Mock()
        mock_get_database.return_value = mock_db
        
        service = await get_dashboard_service()
        assert isinstance(service, DashboardService)
        assert service.db is not None
        assert hasattr(service, 'clients_collection')
    
    @pytest.mark.asyncio
    @patch('app.api.dependencies.get_database')
    async def test_all_db_services_have_database(self, mock_get_database):
        """Test that all services (except AIAgent) have database connection."""
        # Mock database connection
        mock_db = Mock()
        mock_db.clients = Mock()
        mock_db.tasks = Mock()
        mock_db.email_logs = Mock()
        mock_get_database.return_value = mock_db
        
        services = [
            await get_crm_service(),
            await get_scheduler_service(),
            await get_email_service(),
            await get_dashboard_service(),
        ]
        
        for service in services:
            assert hasattr(service, 'db')
            assert service.db is not None
