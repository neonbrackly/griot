#!/bin/bash
# =============================================================================
# Start Griot Registry Development Environment
# =============================================================================
# This script starts MongoDB and the Registry API with hot-reload enabled
#
# Usage:
#   ./scripts/start-dev.sh         # Start in foreground
#   ./scripts/start-dev.sh -d      # Start in background (detached)
#   ./scripts/start-dev.sh down    # Stop all services
#   ./scripts/start-dev.sh logs    # View logs
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$PROJECT_DIR/docker-compose.dev.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Change to monorepo root (parent of griot-registry)
cd "$PROJECT_DIR/.."

case "${1:-up}" in
    up)
        info "Starting Griot Registry development environment..."
        info "MongoDB will be available at: mongodb://localhost:27017"
        info "Registry API will be available at: http://localhost:8000"
        info "Mongo Express (admin) will be available at: http://localhost:8081"
        echo ""

        if [ "$2" = "-d" ]; then
            docker-compose -f "$COMPOSE_FILE" up -d --build
            info "Services started in background"
            info "View logs with: $0 logs"
        else
            docker-compose -f "$COMPOSE_FILE" up --build
        fi
        ;;

    down)
        info "Stopping Griot Registry development environment..."
        docker-compose -f "$COMPOSE_FILE" down
        ;;

    logs)
        docker-compose -f "$COMPOSE_FILE" logs -f "${2:-registry}"
        ;;

    restart)
        info "Restarting services..."
        docker-compose -f "$COMPOSE_FILE" restart "${2:-registry}"
        ;;

    clean)
        warn "This will remove all containers and volumes (data will be lost)!"
        read -p "Are you sure? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose -f "$COMPOSE_FILE" down -v
            info "Cleaned up all containers and volumes"
        fi
        ;;

    status)
        docker-compose -f "$COMPOSE_FILE" ps
        ;;

    *)
        echo "Usage: $0 {up|down|logs|restart|clean|status}"
        echo ""
        echo "Commands:"
        echo "  up [-d]     Start services (use -d for detached mode)"
        echo "  down        Stop all services"
        echo "  logs [svc]  View logs (default: registry)"
        echo "  restart     Restart services"
        echo "  clean       Remove all containers and volumes"
        echo "  status      Show service status"
        exit 1
        ;;
esac
