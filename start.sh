#!/bin/bash

# Wake Word Trainer - Quick Start Script
# This script helps you get started quickly with the Wake Word Trainer

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_header() {
    echo ""
    echo "========================================================================"
    echo -e "${BLUE}$1${NC}"
    echo "========================================================================"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        echo "Please install Docker from: https://docs.docker.com/get-docker/"
        exit 1
    fi
    print_success "Docker is installed"
}

# Check if Docker Compose is installed
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed"
        echo "Please install Docker Compose from: https://docs.docker.com/compose/install/"
        exit 1
    fi
    print_success "Docker Compose is installed"
}

# Check if port 5000 is available
check_port() {
    if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1 || netstat -an 2>/dev/null | grep -q ":5000.*LISTEN"; then
        print_warning "Port 5000 is already in use"
        read -p "Would you like to use a different port? (y/n): " use_different_port
        if [[ $use_different_port =~ ^[Yy]$ ]]; then
            read -p "Enter port number (default: 8000): " custom_port
            custom_port=${custom_port:-8000}
            export PORT=$custom_port
            print_info "Using port: $custom_port"
        else
            print_error "Please stop the service using port 5000 and try again"
            exit 1
        fi
    else
        print_success "Port 5000 is available"
    fi
}

# Create necessary directories
create_directories() {
    print_info "Creating directories..."
    mkdir -p models training_jobs
    print_success "Directories created"
}

# Create .env file if it doesn't exist
create_env_file() {
    if [ ! -f .env ]; then
        print_info "Creating .env file from template..."
        cp .env.example .env
        # Generate a random secret key
        SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1)
        sed -i.bak "s/your-secret-key-here-change-this-in-production/$SECRET_KEY/" .env && rm .env.bak 2>/dev/null || true
        print_success ".env file created"
    else
        print_info ".env file already exists"
    fi
}

# Build and start the application
start_application() {
    print_header "Starting Wake Word Trainer"
    
    print_info "Building Docker image..."
    if docker-compose build; then
        print_success "Docker image built successfully"
    else
        print_error "Failed to build Docker image"
        exit 1
    fi
    
    print_info "Starting container..."
    if docker-compose up -d; then
        print_success "Container started successfully"
    else
        print_error "Failed to start container"
        exit 1
    fi
    
    # Wait for the application to be ready
    print_info "Waiting for application to be ready..."
    sleep 5
    
    # Check if the application is accessible
    if curl -sf http://localhost:${PORT:-5000} > /dev/null; then
        print_success "Application is running!"
    else
        print_warning "Application may still be starting up..."
        print_info "Check logs with: docker-compose logs -f"
    fi
}

# Display success message
show_completion_message() {
    print_header "🎉 Setup Complete!"
    
    echo ""
    echo -e "${GREEN}Wake Word Trainer is now running!${NC}"
    echo ""
    echo "Access the web interface at:"
    echo -e "${BLUE}  http://localhost:${PORT:-5000}${NC}"
    echo ""
    echo "Useful commands:"
    echo "  View logs:          docker-compose logs -f wake-word-trainer"
    echo "  Stop application:   docker-compose down"
    echo "  Restart:            docker-compose restart"
    echo "  Update and rebuild: docker-compose up -d --build"
    echo ""
    echo "Next steps:"
    echo "  1. Open the web interface in your browser"
    echo "  2. Enter your wake word (e.g., 'hey betty')"
    echo "  3. Choose training method (OpenWakeWord recommended)"
    echo "  4. Start training!"
    echo ""
    echo "Need help? Check the README.md or visit:"
    echo "  https://www.home-assistant.io/voice_control/"
    echo ""
}

# Main execution
main() {
    clear
    print_header "🎙️  Wake Word Trainer - Quick Start"
    
    cat << "EOF"
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   Train custom wake words for Home Assistant!            ║
    ║   Web-based interface with OpenWakeWord & MicroWakeWord  ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
EOF
    
    echo ""
    print_info "This script will:"
    echo "  1. Check system requirements"
    echo "  2. Create necessary directories"
    echo "  3. Build and start the Docker container"
    echo "  4. Launch the web interface"
    echo ""
    
    read -p "Press Enter to continue or Ctrl+C to cancel..."
    
    print_header "Checking Requirements"
    check_docker
    check_docker_compose
    check_port
    
    print_header "Setting Up"
    create_directories
    create_env_file
    
    start_application
    show_completion_message
}

# Handle Ctrl+C
trap 'echo -e "\n${RED}Setup cancelled${NC}"; exit 1' INT

# Run main function
main
