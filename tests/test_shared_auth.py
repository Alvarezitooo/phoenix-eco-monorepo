"""
🧪 Tests pour l'authentification partagée Phoenix
Tests unitaires pour valider le fonctionnement du AuthManager unifié

Author: Claude Phoenix DevSecOps Guardian
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from packages.phoenix_shared_auth.client import AuthManager, get_auth_manager


class TestAuthManager:
    """Tests pour la classe AuthManager"""
    
    def setup_method(self):
        """Setup pour chaque test"""
        # Mock des variables d'environnement
        self.env_vars = {
            'SUPABASE_URL': 'https://test.supabase.co',
            'SUPABASE_ANON_KEY': 'test-anon-key'
        }
    
    @patch.dict(os.environ, {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_ANON_KEY': 'test-anon-key'
    })
    @patch('packages.phoenix_shared_auth.client.create_client')
    def test_auth_manager_initialization(self, mock_create_client):
        """Test l'initialisation de AuthManager"""
        # Arrange
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        
        # Act
        auth_manager = AuthManager()
        
        # Assert
        assert auth_manager.client == mock_client
        mock_create_client.assert_called_once_with(
            'https://test.supabase.co',
            'test-anon-key'
        )
    
    def test_auth_manager_missing_env_vars(self):
        """Test que AuthManager lève une erreur si les variables d'env sont manquantes"""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="SUPABASE_URL and SUPABASE_ANON_KEY must be set"):
            AuthManager()
    
    @patch.dict(os.environ, {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_ANON_KEY': 'test-anon-key'
    })
    @patch('packages.phoenix_shared_auth.client.create_client')
    def test_sign_up_success(self, mock_create_client):
        """Test inscription utilisateur réussie"""
        # Arrange
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        
        # Mock Supabase response
        mock_user = Mock()
        mock_user.id = 'test-user-id'
        mock_auth_response = Mock()
        mock_auth_response.user = mock_user
        mock_client.auth.sign_up.return_value = mock_auth_response
        
        mock_table_response = Mock()
        mock_table_response.execute.return_value = None
        mock_client.table.return_value.insert.return_value = mock_table_response
        
        auth_manager = AuthManager()
        
        # Act
        success, user, message = auth_manager.sign_up(
            'test@example.com',
            'password123',
            {'full_name': 'Test User'}
        )
        
        # Assert
        assert success is True
        assert user is not None
        assert user.user_id == 'test-user-id'
        assert user.email == 'test@example.com'
        assert user.subscription_tier == 'free'
        assert message == "Account created successfully"
    
    @patch.dict(os.environ, {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_ANON_KEY': 'test-anon-key'
    })
    @patch('packages.phoenix_shared_auth.client.create_client')
    def test_sign_in_success(self, mock_create_client):
        """Test connexion utilisateur réussie"""
        # Arrange
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        
        # Mock Supabase auth response
        mock_user = Mock()
        mock_user.id = 'test-user-id'
        mock_auth_response = Mock()
        mock_auth_response.user = mock_user
        mock_client.auth.sign_in_with_password.return_value = mock_auth_response
        
        # Mock profile response
        mock_profile_data = {
            'id': 'test-user-id',
            'email': 'test@example.com',
            'subscription_tier': 'premium',
            'full_name': 'Test User'
        }
        mock_profile_response = Mock()
        mock_profile_response.data = mock_profile_data
        mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_profile_response
        
        auth_manager = AuthManager()
        
        # Act
        success, user, message = auth_manager.sign_in('test@example.com', 'password123')
        
        # Assert
        assert success is True
        assert user is not None
        assert user.user_id == 'test-user-id'
        assert user.subscription_tier == 'premium'
        assert message == "Successfully signed in"
    
    @patch.dict(os.environ, {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_ANON_KEY': 'test-anon-key'
    })
    @patch('packages.phoenix_shared_auth.client.create_client')
    def test_get_user_authenticated(self, mock_create_client):
        """Test récupération utilisateur connecté"""
        # Arrange
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        
        # Mock user response
        mock_user = Mock()
        mock_user.id = 'test-user-id'
        mock_get_user_response = Mock()
        mock_get_user_response.user = mock_user
        mock_client.auth.get_user.return_value = mock_get_user_response
        
        # Mock profile response
        mock_profile_data = {
            'id': 'test-user-id',
            'email': 'test@example.com',
            'subscription_tier': 'cv_premium',
            'created_at': '2024-01-01T00:00:00Z'
        }
        mock_profile_response = Mock()
        mock_profile_response.data = mock_profile_data
        mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_profile_response
        
        auth_manager = AuthManager()
        
        # Act
        user_data = auth_manager.get_user()
        
        # Assert
        assert user_data is not None
        assert user_data['user_id'] == 'test-user-id'
        assert user_data['stream_id'] == 'test-user-id'  # Clé pour Event Store
        assert user_data['subscription_tier'] == 'cv_premium'
        assert user_data['is_premium'] is True
    
    @patch.dict(os.environ, {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_ANON_KEY': 'test-anon-key'
    })
    @patch('packages.phoenix_shared_auth.client.create_client')
    def test_has_premium_access_bundle(self, mock_create_client):
        """Test accès Premium avec pack bundle"""
        # Arrange
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        
        auth_manager = AuthManager()
        
        # Mock get_user pour retourner bundle premium
        with patch.object(auth_manager, 'get_user') as mock_get_user:
            mock_get_user.return_value = {
                'user_id': 'test-user-id',
                'subscription_tier': 'pack_premium'
            }
            
            # Act & Assert
            assert auth_manager.has_premium_access() is True
            assert auth_manager.has_premium_access('cv') is True
            assert auth_manager.has_premium_access('letters') is True
    
    @patch.dict(os.environ, {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_ANON_KEY': 'test-anon-key'
    })
    @patch('packages.phoenix_shared_auth.client.create_client')
    def test_has_premium_access_specific_app(self, mock_create_client):
        """Test accès Premium spécifique à une app"""
        # Arrange
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        
        auth_manager = AuthManager()
        
        # Mock get_user pour retourner CV premium seulement
        with patch.object(auth_manager, 'get_user') as mock_get_user:
            mock_get_user.return_value = {
                'user_id': 'test-user-id',
                'subscription_tier': 'cv_premium'
            }
            
            # Act & Assert
            assert auth_manager.has_premium_access('cv') is True
            assert auth_manager.has_premium_access('letters') is False
            assert auth_manager.has_premium_access() is False


class TestAuthManagerFactory:
    """Tests pour la factory get_auth_manager"""
    
    @patch.dict(os.environ, {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_ANON_KEY': 'test-anon-key'
    })
    @patch('packages.phoenix_shared_auth.client.create_client')
    def test_get_auth_manager_singleton(self, mock_create_client):
        """Test que get_auth_manager retourne toujours la même instance"""
        # Arrange
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        
        # Act
        auth1 = get_auth_manager()
        auth2 = get_auth_manager()
        
        # Assert
        assert auth1 is auth2  # Même instance (singleton)
    
    @patch.dict(os.environ, {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_ANON_KEY': 'test-anon-key'
    })
    @patch('packages.phoenix_shared_auth.client.create_client')
    def test_get_auth_manager_returns_auth_manager_instance(self, mock_create_client):
        """Test que get_auth_manager retourne bien une instance AuthManager"""
        # Arrange
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        
        # Act
        auth_manager = get_auth_manager()
        
        # Assert
        assert isinstance(auth_manager, AuthManager)


# Tests d'intégration (nécessitent une vraie DB Supabase en test)
@pytest.mark.integration
class TestAuthManagerIntegration:
    """Tests d'intégration nécessitant une vraie DB Supabase"""
    
    @pytest.mark.skip(reason="Nécessite une DB Supabase de test configurée")
    def test_full_auth_flow_integration(self):
        """Test complet du flux d'authentification"""
        # Ce test nécessiterait une vraie instance Supabase de test
        pass


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])