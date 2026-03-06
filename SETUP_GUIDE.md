# Setup Guide: Kubernetes + REST API

## Step-by-Step Setup Instructions

### Part 1: Setting Up Kubernetes on Mac with kind

kind (Kubernetes in Docker) is a lightweight tool for running local Kubernetes clusters.

#### Prerequisites Installation

1. **Install Docker**
   ```bash
   brew install --cask docker
   # Launch Docker Desktop and ensure it's running
   ```

2. **Install kind**
   ```bash
   brew install kind
   ```

3. **Install kubectl** (Kubernetes CLI)
   ```bash
   brew install kubectl
   ```

#### Create kind Cluster

1. **Create a single-node cluster** (easiest for development)
   ```bash
   kind create cluster --name universal-cluster
   ```

2. **Verify the cluster is running**
   ```bash
   kubectl cluster-info
   kubectl get nodes
   ```

3. **Check your current context**
   ```bash
   kubectl config current-context
   # Should show: kind-universal-cluster
   ```

#### Managing the kind Cluster

```bash
# List all kind clusters
kind get clusters

# Delete the cluster (when done testing)
kind delete cluster --name universal-cluster

# Recreate the cluster
kind create cluster --name universal-cluster
```

### Part 2: Understanding REST APIs

#### What is a REST API?

REST (Representational State Transfer) is an architectural style for designing web services. Key concepts:

- **Resources**: Everything is a resource (e.g., `/api/items`)
- **HTTP Methods**: 
  - `GET` - Retrieve data
  - `POST` - Create new data
  - `PUT` - Update existing data
  - `DELETE` - Delete data
- **Stateless**: Each request contains all information needed
- **JSON**: Common data format for APIs

#### Our REST API Structure

Our FastAPI application provides:

```
GET    /api/items       - List all items
GET    /api/items/{id}  - Get specific item
POST   /api/items       - Create new item
PUT    /api/items/{id}  - Update item
DELETE /api/items/{id}  - Delete item
GET    /health          - Health check
GET    /docs            - Interactive API docs (Swagger UI)
```

### Part 3: Building and Deploying

#### Step 1: Test API Locally (Optional)

```bash
# Navigate to API directory
cd api

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the API
python app.py

# API is now available at http://localhost:8000
# Visit http://localhost:8000/docs for interactive documentation
```

#### Step 2: Build Docker Image and Load into kind

```bash
# Build the Docker image locally
docker build -t universal:latest ./api

# Verify image was created
docker images | grep universal

# Load the image into kind cluster
kind load docker-image universal:latest --name universal-cluster
```

**Note:** kind runs Kubernetes in Docker containers, so we need to explicitly load the image into the cluster. This is simpler than using a registry for local development.

#### Step 3: Deploy to Kubernetes

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods
kubectl get services

# Wait for pods to be ready
kubectl wait --for=condition=available --timeout=60s deployment/universal-deployment
```

#### Step 4: Access the API

```bash
# Port forward the service to your local machine
kubectl port-forward service/universal-service 8000:80

# Now the API is accessible at http://localhost:8000
# Try visiting:
# - http://localhost:8000/docs (Interactive API docs)
# - http://localhost:8000/health (Health check)
```

### Part 4: Testing the API

#### Using curl:

```bash
# Health check
curl http://localhost:8000/health

# Get all items
curl http://localhost:8000/api/items

# Create a new item
curl -X POST http://localhost:8000/api/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Laptop", "description": "Gaming laptop", "price": 1299.99}'

# Get specific item
curl http://localhost:8000/api/items/1

# Update item
curl -X PUT http://localhost:8000/api/items/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "Gaming Laptop", "price": 1199.99}'

# Delete item
curl -X DELETE http://localhost:8000/api/items/1
```

#### Using the Interactive Docs:

1. Open http://localhost:8000/docs in your browser
2. Click on any endpoint
3. Click "Try it out"
4. Fill in the parameters
5. Click "Execute"

### Part 5: Understanding Kubernetes Resources

#### Deployment (`k8s/deployment.yaml`)
- Manages Pods (containers)
- Ensures desired number of replicas are running
- Handles rolling updates
- Defines container image, ports, resources, health checks

#### Service (`k8s/service.yaml`)
- Exposes Pods to network traffic
- Provides stable IP address
- Load balances across Pods
- Type: ClusterIP (internal access only)

#### Key Concepts:
- **Pod**: Smallest deployable unit (one or more containers)
- **Deployment**: Manages Pods and ensures they're running
- **Service**: Network access to Pods
- **Replica**: Copy of a Pod (for scaling)

### Part 6: Useful Commands

```bash
# View all resources
kubectl get all

# View pods
kubectl get pods

# View services
kubectl get services

# View deployments
kubectl get deployments

# View pod logs
kubectl logs -l app=universal

# View specific pod logs
kubectl logs <pod-name>

# Follow logs
kubectl logs -f <pod-name>

# Describe pod (debugging)
kubectl describe pod <pod-name>

# Exec into pod
kubectl exec -it <pod-name> -- /bin/sh

# Scale deployment
kubectl scale deployment universal-deployment --replicas=3

# Delete deployment
kubectl delete -f k8s/

# Check cluster info
kubectl cluster-info

# Check nodes
kubectl get nodes
```

### Troubleshooting

#### Issue: kind cluster not starting
- Make sure Docker Desktop is running: `docker ps`
- Check if cluster exists: `kind get clusters`
- Create cluster: `kind create cluster --name universal-cluster`

#### Issue: Pods not starting / ImagePullBackOff
- **Most common issue**: Image not loaded into kind
  ```bash
  # Rebuild and reload image
  docker build -t universal:latest ./api
  kind load docker-image universal:latest --name universal-cluster
  ```
- Check pod status and events:
  ```bash
  kubectl get pods
  kubectl describe pod <pod-name>
  kubectl logs <pod-name>
  ```

#### Issue: Service not accessible
- Make sure port-forward is running: `kubectl port-forward service/universal-service 8000:80`
- Check service is created: `kubectl get svc universal-service`
- Verify pods are running: `kubectl get pods -l app=universal`

### Quick Reference

**Full deployment workflow:**
```bash
# 1. Create kind cluster (first time only)
kind create cluster --name universal-cluster

# 2. Build and load Docker image
docker build -t universal:latest ./api
kind load docker-image universal:latest --name universal-cluster

# 3. Deploy to Kubernetes
kubectl apply -f k8s/

# 4. Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app=universal --timeout=60s

# 5. Port forward to access API
kubectl port-forward service/universal-service 8000:80
```

**Clean up:**
```bash
# Delete all resources
kubectl delete -f k8s/

# Delete the kind cluster
kind delete cluster --name universal-cluster
```

**Test API:**
- Interactive docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health
- List items: http://localhost:8000/api/items

