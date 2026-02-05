#!/bin/bash
# Quick build and deploy script for custom Moodle

set -e

echo "=========================================="
echo "Moodle Custom Docker Build & Deploy"
echo "=========================================="
echo ""

# Check if websoft9 network exists
if ! docker network inspect websoft9 &>/dev/null; then
    echo "Creating websoft9 network..."
    docker network create websoft9
else
    echo "✓ websoft9 network exists"
fi

echo ""
echo "Building custom Moodle image..."
docker build -t websoft9dev/moodle:5.1 .

echo ""
echo "Starting services..."
docker compose -f docker-compose-custom.yml up -d

echo ""
echo "Waiting for services to be ready..."
sleep 10

echo ""
echo "=========================================="
echo "Deployment complete!"
echo "=========================================="
echo ""
echo "Access Moodle at: http://localhost:9001"
echo ""
echo "Default credentials:"
echo "  Username: admin"
echo "  Password: Check .env file (W9_POWER_PASSWORD)"
echo ""
echo "Useful commands:"
echo "  View logs:    docker compose -f docker-compose-custom.yml logs -f"
echo "  Stop:         docker compose -f docker-compose-custom.yml down"
echo "  Restart:      docker compose -f docker-compose-custom.yml restart"
echo "  Remove all:   docker compose -f docker-compose-custom.yml down -v"
echo ""
