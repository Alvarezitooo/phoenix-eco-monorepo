#!/bin/bash

# 🚀 Phoenix Ecosystem - Setup Development Environment
# Script d'installation complète pour l'environnement de développement
# Author: Claude Phoenix DevSecOps Guardian

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if running on macOS or Linux
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    else
        echo "unknown"
    fi
}

# Install system dependencies
install_system_deps() {
    local os=$(detect_os)
    log_info "Installing system dependencies for $os..."
    
    case $os in
        "macos")
            if ! command -v brew &> /dev/null; then
                log_error "Homebrew not found. Please install it first: https://brew.sh"
                exit 1
            fi
            brew install python@3.11 node@20 git pre-commit
            ;;
        "linux")
            sudo apt update
            sudo apt install -y python3.11 python3-pip nodejs npm git
            ;;
        *)
            log_error "Unsupported OS: $OSTYPE"
            exit 1
            ;;
    esac
    
    log_success "System dependencies installed"
}

# Install Python dependencies
setup_python_env() {
    log_info "Setting up Python environment..."
    
    # Check Python version
    if ! python3.11 --version &> /dev/null; then
        log_error "Python 3.11 not found"
        exit 1
    fi
    
    # Install Poetry if not exists
    if ! command -v poetry &> /dev/null; then
        log_info "Installing Poetry..."
        curl -sSL https://install.python-poetry.org | python3 -
        export PATH="$HOME/.local/bin:$PATH"
    fi
    
    # Install Python dependencies
    log_info "Installing Python dependencies with Poetry..."
    poetry install --with dev
    
    log_success "Python environment configured"
}

# Setup Node.js environment
setup_node_env() {
    log_info "Setting up Node.js environment..."
    
    # Install Node dependencies for website
    if [ -d "apps/phoenix-website" ]; then
        cd apps/phoenix-website
        log_info "Installing Node.js dependencies for website..."
        npm ci
        cd ../..
    fi
    
    log_success "Node.js environment configured"
}

# Setup Git hooks
setup_git_hooks() {
    log_info "Setting up Git pre-commit hooks..."
    
    # Install pre-commit hooks
    poetry run pre-commit install
    poetry run pre-commit install --hook-type pre-push
    poetry run pre-commit install --hook-type commit-msg
    
    # Run pre-commit once to cache
    log_info "Running initial pre-commit check..."
    poetry run pre-commit run --all-files || log_warning "Some pre-commit checks failed - this is normal on first run"
    
    log_success "Git hooks configured"
}

# Create environment files
setup_env_files() {
    log_info "Creating environment configuration files..."
    
    # Create .env template if not exists
    if [ ! -f ".env" ]; then
        cat > .env << 'EOF'
# 🔐 Phoenix Ecosystem - Environment Variables
# Copy this file and fill in your actual values

# Supabase Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here

# Stripe Configuration
STRIPE_SECRET_KEY=your_stripe_secret_key_here
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key_here
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret_here

# Price IDs pour les produits Phoenix
STRIPE_PRICE_LETTERS_PREMIUM=price_1RraAcDcM3VIYgvyEBNFXfbR
STRIPE_PRICE_CV_PREMIUM=price_1RraUoDcM3VIYgvy0NXiKmKV
STRIPE_PRICE_BUNDLE=price_1RraWhDcM3VIYgvyGykPghCc

# Google Gemini API
GOOGLE_API_KEY=your_gemini_api_key_here

# Phoenix Event Bridge Configuration
PHOENIX_EVENT_PERSISTENCE=true
PHOENIX_EVENT_LOGGING=true

# Development Configuration
ENVIRONMENT=development
DEBUG=true
EOF
        log_success "Created .env template file"
        log_warning "Please fill in your actual environment variables in .env file"
    else
        log_info ".env file already exists"
    fi
}

# Validate installation
validate_installation() {
    log_info "Validating installation..."
    
    local errors=0
    
    # Check Poetry
    if ! poetry --version &> /dev/null; then
        log_error "Poetry not properly installed"
        ((errors++))
    fi
    
    # Check Python dependencies
    if ! poetry run python -c "import streamlit, supabase, stripe" &> /dev/null; then
        log_error "Python dependencies not properly installed"
        ((errors++))
    fi
    
    # Check pre-commit
    if ! poetry run pre-commit --version &> /dev/null; then
        log_error "Pre-commit not properly installed"
        ((errors++))
    fi
    
    # Check Node.js (if website exists)
    if [ -d "apps/phoenix-website" ] && ! node --version &> /dev/null; then
        log_error "Node.js not properly installed"
        ((errors++))
    fi
    
    if [ $errors -eq 0 ]; then
        log_success "All validations passed!"
        return 0
    else
        log_error "$errors validation(s) failed"
        return 1
    fi
}

# Main installation process
main() {
    echo "🚀 Phoenix Ecosystem Development Environment Setup"
    echo "================================================="
    
    # Check if we're in the right directory
    if [ ! -f "pyproject.toml" ]; then
        log_error "Please run this script from the Phoenix monorepo root directory"
        exit 1
    fi
    
    log_info "Starting development environment setup..."
    
    # Installation steps
    install_system_deps
    setup_python_env
    setup_node_env
    setup_git_hooks
    setup_env_files
    
    # Validation
    if validate_installation; then
        echo ""
        echo "🎉 Phoenix Development Environment Setup Complete!"
        echo "================================================="
        echo ""
        log_success "Next steps:"
        echo "  1. Fill in your environment variables in .env file"
        echo "  2. Test the setup: poetry run python -m pytest"
        echo "  3. Start Phoenix CV: poetry run python launch_cv.py"
        echo "  4. Start Phoenix Letters: poetry run python launch_letters.py"
        echo ""
        log_info "Happy coding! 🚀"
    else
        log_error "Setup completed with some issues. Please check the errors above."
        exit 1
    fi
}

# Run main function
main "$@"