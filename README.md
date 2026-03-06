# Kubernetes + REST API Interview Assessment

This project demonstrates the Universal Service (a REST API service) deployed on a local Kubernetes cluster.

## Prerequisites

### For Mac:
1. **Docker Desktop**
   ```bash
   brew install --cask docker
   # Launch Docker Desktop and ensure it's running
   ```

2. **kind** (Kubernetes in Docker - lightweight local Kubernetes)
   ```bash
   brew install kind
   ```

3. **kubectl** (Kubernetes CLI)
   ```bash
   brew install kubectl
   ```

4. **Python 3.8+**
   ```bash
   brew install python3
   ```

## Project Structure

```
.
├── api/                  # Universal Service (REST API)
│   ├── app.py           # FastAPI application
│   ├── requirements.txt # Python dependencies
│   └── Dockerfile       # Container image
├── k8s/                 # Kubernetes manifests
│   ├── deployment.yaml  # Pod deployment
│   └── service.yaml     # Service definition
├── opa/                 # Open Policy Agent – authorization policy engine
│   ├── policies/        # Rego policies (authz by path + method + Auth0 permissions)
│   ├── data/            # Optional policy data (e.g. roles)
│   ├── input-examples/  # Example inputs for testing
│   └── README.md        # OPA setup, Auth0 integration, API contract
├── scripts/             # Helper scripts
│   └── setup.sh        # Setup script
└── README.md           # This file
```

## Quick Start

### 1. Setup Kubernetes Cluster with kind

```bash
# Create a kind cluster
kind create cluster --name universal-cluster

# Verify it's running
kubectl cluster-info
kubectl get nodes
```

### 2. Setup Python Environment

```bash
cd api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Test API Locally (Optional)

```bash
cd api
python app.py
# API will be available at http://localhost:8000
# Visit http://localhost:8000/docs for interactive API docs
```

### 4. Build Docker Image and Load into kind

```bash
# Build the image
docker build -t universal:latest ./api

# Load image into kind cluster
kind load docker-image universal:latest --name universal-cluster
```

### 5. Deploy to Kubernetes

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods
kubectl get services

# Port forward to access the API
kubectl port-forward service/universal-service 8000:80

# Now access API at http://localhost:8000
```

### 6. Verify Deployment

```bash
# Check pods
kubectl get pods -l app=universal

# Check services
kubectl get services

# View logs
kubectl logs -l app=universal

# Describe service
kubectl describe service universal-service
```

## API Endpoints

Once deployed, the API exposes the following endpoints:

- `GET /` - Health check
- `GET /health` - Health check endpoint
- `GET /api/items` - List all items
- `GET /api/items/{id}` - Get item by ID
- `POST /api/items` - Create new item
- `PUT /api/items/{id}` - Update item
- `DELETE /api/items/{id}` - Delete item
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)

## Useful Commands

```bash
# View all resources
kubectl get all

# Delete deployment
kubectl delete -f k8s/

# Scale deployment
kubectl scale deployment universal-deployment --replicas=3

# Update image
kubectl set image deployment/universal-deployment universal=universal:v2

# View pod logs
kubectl logs -f <pod-name>

# Exec into pod
kubectl exec -it <pod-name> -- /bin/sh

# Describe resource
kubectl describe pod <pod-name>
```

## Troubleshooting

1. **Kubernetes cluster not running**
   - Check Docker Desktop is running: `docker ps`
   - Check if kind cluster exists: `kind get clusters`
   - Create cluster: `kind create cluster --name universal-cluster`

2. **Pods not starting / ImagePullBackOff**
   - Most common: Image not loaded into kind. Rebuild and reload:
     ```bash
     docker build -t universal:latest ./api
     kind load docker-image universal:latest --name universal-cluster
     ```
   - Check logs: `kubectl logs <pod-name>`
   - Describe pod: `kubectl describe pod <pod-name>`

3. **Service not accessible**
   - Ensure port-forward is running: `kubectl port-forward service/universal-service 8000:80`
   - Check service: `kubectl get svc universal-service`
   - Verify pods are ready: `kubectl get pods -l app=universal`

## Learning Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)

