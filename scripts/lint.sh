#!/bin/bash

# Ruff linting and formatting script for FastAPI TDD Docker project
# Usage: ./scripts/lint.sh [check|format|fix|all]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default paths to check
PATHS="app/ tests/"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker Compose is running
check_docker() {
    if ! docker-compose ps web | grep -q "Up"; then
        print_error "Docker containers are not running. Please start them first:"
        echo "docker-compose up -d"
        exit 1
    fi
}

# Run ruff check (linting)
run_check() {
    print_status "Running ruff linting checks..."
    docker-compose exec web uv run ruff check $PATHS
}

# Run ruff check with auto-fix
run_fix() {
    print_status "Running ruff linting with auto-fix..."
    docker-compose exec web uv run ruff check $PATHS --fix
}

# Run ruff format
run_format() {
    print_status "Running ruff formatting..."
    docker-compose exec web uv run ruff format $PATHS
}

# Show help
show_help() {
    echo "Ruff linting and formatting script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  check     Run linting checks only (default)"
    echo "  fix       Run linting checks with auto-fix"
    echo "  format    Run code formatting"
    echo "  all       Run both linting with auto-fix and formatting"
    echo "  diff      Show what changes would be made (dry run)"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 check           # Check code quality"
    echo "  $0 fix             # Fix linting issues"
    echo "  $0 format          # Format code"
    echo "  $0 all             # Fix linting and format code"
    echo "  $0 diff            # Show potential changes"
}

# Show diff of what would change
run_diff() {
    print_status "Showing potential linting changes..."
    docker-compose exec web uv run ruff check $PATHS --diff
    
    print_status "Showing potential formatting changes..."
    docker-compose exec web uv run ruff format $PATHS --diff
}

# Main script logic
main() {
    # Check Docker first
    check_docker

    case "${1:-check}" in
        "check")
            run_check
            ;;
        "fix")
            run_fix
            ;;
        "format")
            run_format
            ;;
        "all")
            run_fix
            echo ""
            run_format
            print_status "Code quality checks and formatting complete!"
            ;;
        "diff")
            run_diff
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"