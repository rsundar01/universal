#!/bin/bash

# Setup script for Kubernetes + Universal Service project

set -e

echo "🚀 Setting up Kubernetes + Universal Service project..."

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install it first:"
    echo "   brew install kubectl"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop first:"
    echo "   brew install --cask docker"
    exit 1
fi

# Check if Docker daemon is running
if ! docker ps &> /dev/null; then
    echo "❌ Docker daemon is not running."
    echo "   Please start Docker Desktop and wait for it to fully start."
    echo "   You can start it with: open -a Docker"
    echo ""
    echo "   Wait for Docker to start (you'll see a green indicator in the menu bar),"
    echo "   then run this script again."
    exit 1
fi

# Check if kind is installed
if ! command -v kind &> /dev/null; then
    echo "❌ kind is not installed. Please install it first:"
    echo "   brew install kind"
    exit 1
fi

# Check if Kubernetes cluster is accessible
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Kubernetes cluster is not accessible."
    echo "   Please create a kind cluster first:"
    echo "   kind create cluster --name universal-cluster"
    exit 1
fi

# Check if using kind
if ! kubectl config current-context | grep -q "kind"; then
    echo "⚠️  Warning: Not using a kind cluster. This script is optimized for kind."
    echo "   Current context: $(kubectl config current-context)"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "✅ Prerequisites check passed"

# Build Docker image
echo "📦 Building Docker image..."
cd "$(dirname "$0")/../api"
docker build -t universal:latest .

echo "✅ Docker image built successfully"

# Load image into kind if using kind
if kubectl config current-context | grep -q "kind"; then
    CLUSTER_NAME=$(kubectl config current-context | sed 's/kind-//')
    echo "🔧 Loading image into kind cluster: $CLUSTER_NAME"
    kind load docker-image universal:latest --name "$CLUSTER_NAME"
    echo "✅ Image loaded into kind cluster"
fi

# Deploy to Kubernetes
echo "🚀 Deploying to Kubernetes..."
cd "$(dirname "$0")/../k8s"
kubectl apply -f .

echo "⏳ Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=60s deployment/universal-deployment

echo "✅ Deployment successful!"
echo ""
echo "📋 Deployment status:"
kubectl get pods -l app=universal
kubectl get services -l app=universal
echo ""
echo "🌐 To access the API, run:"
echo "   kubectl port-forward service/universal-service 8000:80"
echo ""
echo "📚 Then visit:"
echo "   http://localhost:8000/docs - Interactive API documentation"

