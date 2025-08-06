import pytest
from unittest.mock import MagicMock

# Import the models from phoenix-cv
from phoenix_cv.models.user_profile import UserProfile, Skill, Experience, CV, Letter

# Import the module to be tested
from phoenix_cv.core.app_core import SecurePhoenixCVApp # Correcting to actual class name

# Mock Streamlit functions using pytest-mock's mocker fixture
@pytest.fixture(autouse=True)
def mock_streamlit_functions(mocker):
    mocker.patch('streamlit.set_page_config')
    mocker.patch('streamlit.markdown')
    mocker.patch('streamlit.sidebar.markdown')
    mocker.patch('streamlit.sidebar.button')
    mocker.patch('streamlit.sidebar.radio')
    mocker.patch('streamlit.button')
    mocker.patch('streamlit.columns')
    mocker.patch('streamlit.text_input')
    mocker.patch('streamlit.text_area')
    mocker.patch('streamlit.selectbox')
    mocker.patch('streamlit.checkbox')
    mocker.patch('streamlit.form')
    mocker.patch('streamlit.form_submit_button')
    mocker.patch('streamlit.error')
    mocker.patch('streamlit.success')
    mocker.patch('streamlit.info')
    mocker.patch('streamlit.spinner')
    mocker.patch('streamlit.download_button')
    mocker.patch('streamlit.metric')
    mocker.patch('streamlit.expander')
    mocker.patch('streamlit.file_uploader')
    mocker.patch('streamlit.rerun')


def test_app_core_initialization_with_user_profile():
    """Test that app_core initializes without errors after UserProfile integration."""
    # Simulate a basic run of the app_core main function
    # This test primarily checks for import errors and basic initialization flow
    # without deep interaction with Streamlit widgets.
    
    # We need to mock the phoenix_cv_auth_integration.main call if it's still present
    # in app.py's __main__ block for non-test mode.
    with patch('phoenix_cv_auth_integration.main') as mock_auth_main:
        main() # Call the main function of app.py
        mock_auth_main.assert_called_once() # Ensure the auth flow is initiated

    # Assert that no critical errors occurred during initialization
    # (This is a very basic check, more specific assertions will come with feature tests)
    assert True