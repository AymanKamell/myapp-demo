# Kubernetes 3-Tier Application — RHACS Security Demo

A small **3-tier application deployed on Kubernetes** and used as a hands-on lab for learning **Red Hat Advanced Cluster Security for Kubernetes (RHACS)**, Kubernetes security controls, networking, RBAC, resource management, and container security.

The application consists of a frontend, backend API, and PostgreSQL database. The deployment also includes Kubernetes NetworkPolicies, ResourceQuota, ServiceAccounts, RBAC, persistent storage, and an Ingress.

---

## 1. Architecture

The application follows this architecture:

```text
                         Browser
                            |
                            | HTTP
                            v
                  NodePort :32279
                            |
                            v
               NGINX Ingress Controller
                            |
                            v
                    Frontend Service
                            |
                            v
                    Frontend Pod
                     NGINX container
                            |
                     /api/* proxy
                            |
                            v
                    Backend Service
                            |
                            v
                    Backend Pod
                     Flask application
                            |
                         TCP 5432
                            |
                            v
                   PostgreSQL Service
                            |
                            v
                    PostgreSQL Pod
                            |
                            v
                    PersistentVolume
```

The Kubernetes traffic flow is:

```text
Browser
  -> Ingress NodePort
  -> NGINX Ingress Controller
  -> frontend Service
  -> frontend Pod
  -> backend Service
  -> backend Pod
  -> postgres Service
  -> PostgreSQL Pod
  -> PVC
```

---

## 2. Components

| Component               | Technology                | Kubernetes Resource               |
| ----------------------- | ------------------------- | --------------------------------- |
| Frontend                | NGINX                     | Deployment                        |
| Backend                 | Python / Flask            | Deployment                        |
| Database                | PostgreSQL 16             | StatefulSet                       |
| External access         | NGINX Ingress Controller  | Ingress                           |
| Database storage        | local-path                | PersistentVolumeClaim             |
| Application isolation   | Kubernetes NetworkPolicy  | NetworkPolicy                     |
| Resource control        | Kubernetes ResourceQuota  | ResourceQuota                     |
| Application identity    | Kubernetes ServiceAccount | ServiceAccount                    |
| Application permissions | Kubernetes RBAC           | Role / RoleBinding                |
| Security platform       | RHACS                     | Red Hat Advanced Cluster Security |

---

# 3. Repository Structure

```text
myapp/
├── backend/
│   ├── backend-application/
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── backend-service.yaml
│   ├── backend-serviceaccount.yaml
│   ├── backend.yaml
│   ├── role-app.yaml
│   └── rolebinding-app.yaml
│
├── database/
│   ├── db-pvc.yaml
│   ├── db-service.yaml
│   ├── db.yaml
│   └── db-secret.yaml
│
├── frontend/
│   ├── frontend-application/
│   │   ├── index.html
│   │   ├── nginx.conf
│   │   └── Dockerfile
│   ├── frontend-ingress.yaml
│   ├── frontend-service.yaml
│   └── frontend.yaml
│
├── networkPolicy.yml
├── resource-quotas.yaml
└── README.md
```

> `database/db-secret.yaml` contains database credentials and is intentionally excluded from Git using `.gitignore`.

---

# 4. Prerequisites

The lab requires:

* Kubernetes cluster
* `kubectl`
* Docker
* Access to a container registry
* NGINX Ingress Controller
* RHACS installed in the cluster
* `roxctl` for RHACS CLI operations

Verify the Kubernetes cluster:

```bash
kubectl get nodes
```

Verify the Ingress Controller:

```bash
kubectl get pods -n ingress-nginx
```

Verify RHACS:

```bash
kubectl get pods -n stackrox
```

---

# 5. Create the Application Namespace

Create the namespace:

```bash
kubectl create namespace myapp
```

Verify:

```bash
kubectl get namespace myapp
```

---

# 6. Build the Backend Image

The backend is a Flask application exposing the following endpoints:

```text
/health
/api/message
/api/db
```

Build the image:

```bash
cd backend/backend-application

docker build -t docker.io/aymankamell/myapp-backend:1.0 .
```

Push the image:

```bash
docker push docker.io/aymankamell/myapp-backend:1.0
```

---

# 7. Build the Frontend Image

The frontend uses NGINX to serve the web application and proxy API requests to the backend.

Build the image:

```bash
cd frontend/frontend-application

docker build -t docker.io/aymankamell/myapp-frontend:1.2 .
```

Push the image:

```bash
docker push docker.io/aymankamell/myapp-frontend:1.2
```

---

# 8. Deploy PostgreSQL

The database consists of:

* PostgreSQL StatefulSet
* PostgreSQL Service
* PersistentVolumeClaim
* Kubernetes Secret

Apply the database resources:

```bash
kubectl apply -f database/db-pvc.yaml
kubectl apply -f database/db-service.yaml
kubectl apply -f database/db.yaml
```

Create the database Secret separately:

```bash
kubectl apply -f database/db-secret.yaml
```

Verify:

```bash
kubectl get pods -n myapp
kubectl get svc -n myapp
kubectl get pvc -n myapp
```

The PostgreSQL pod should become:

```text
postgres-0    Running
```

Verify the StatefulSet:

```bash
kubectl get statefulset -n myapp
```

---

# 9. Deploy the Backend

Create the backend ServiceAccount:

```bash
kubectl apply -f backend/backend-serviceaccount.yaml
```

Apply the RBAC resources:

```bash
kubectl apply -f backend/role-app.yaml
kubectl apply -f backend/rolebinding-app.yaml
```

Deploy the backend:

```bash
kubectl apply -f backend/backend.yaml
kubectl apply -f backend/backend-service.yaml
```

Verify:

```bash
kubectl get pods -n myapp -l app=backend
kubectl get svc -n myapp backend
```

Check the backend logs:

```bash
kubectl logs -n myapp deploy/backend
```

Test the health endpoint from inside the Pod:

```bash
kubectl exec -n myapp deploy/backend -- \
  python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8080/health').read().decode())"
```

Expected response:

```json
{"status":"healthy"}
```

---

# 10. Test Backend-to-Database Connectivity

The backend exposes an endpoint that verifies PostgreSQL connectivity:

```text
/api/db
```

Run:

```bash
kubectl exec -n myapp deploy/backend -- \
  python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8080/api/db').read().decode())"
```

Expected response:

```json
{
  "database": "appdb",
  "status": "connected",
  "user": "appuser"
}
```

A direct TCP test can also be performed:

```bash
kubectl exec -n myapp deploy/backend -- \
  python -c "import socket; s=socket.create_connection(('postgres',5432),5); print('TCP connection to postgres:5432 successful'); s.close()"
```

Expected:

```text
TCP connection to postgres:5432 successful
```

---

# 11. Deploy the Frontend

Apply the frontend Deployment:

```bash
kubectl apply -f frontend/frontend.yaml
```

Create the Service:

```bash
kubectl apply -f frontend/frontend-service.yaml
```

Create the Ingress:

```bash
kubectl apply -f frontend/frontend-ingress.yaml
```

Verify:

```bash
kubectl get pods -n myapp -l app=frontend
kubectl get svc -n myapp frontend
kubectl get ingress -n myapp
```

---

# 12. Access the Application

For a bare-metal NGINX Ingress Controller deployment, determine the NodePort:

```bash
kubectl get svc -n ingress-nginx
```

Example:

```text
ingress-nginx-controller
HTTP NodePort: 32279
```

The application can then be accessed through:

```text
http://<NODE-IP>:32279
```

For example:

```text
http://192.168.153.128:32279
```

---

# 13. Apply the ResourceQuota

The application namespace has a ResourceQuota to control the total resources consumed by the workload.

Apply it:

```bash
kubectl apply -f resource-quotas.yaml
```

Verify:

```bash
kubectl get resourcequota -n myapp
```

Inspect usage:

```bash
kubectl describe resourcequota -n myapp
```

The quota limits:

```text
CPU requests
Memory requests
CPU limits
Memory limits
Number of Pods
```

---

# 14. Apply NetworkPolicies

The application uses NetworkPolicies to restrict communication between tiers.

Apply:

```bash
kubectl apply -f networkPolicy.yml
```

Verify:

```bash
kubectl get networkpolicy -n myapp
```

The intended traffic flow is:

```text
ingress-nginx
      |
      | TCP/80
      v
frontend
      |
      | TCP/8080
      v
backend
      |
      | TCP/5432
      v
postgres
```

The policies restrict ingress to the individual application tiers.

---

# 15. Verify the Complete Application

Check all application resources:

```bash
kubectl get all -n myapp
```

Check NetworkPolicies:

```bash
kubectl get networkpolicy -n myapp
```

Check storage:

```bash
kubectl get pvc -n myapp
```

Check quota:

```bash
kubectl get resourcequota -n myapp
```

Check the application endpoint:

```bash
curl http://<NODE-IP>:32279
```

---

# 16. RHACS Integration

RHACS is used to inspect and secure the application from multiple security perspectives.

The main RHACS areas exercised by this demo are:

* Image scanning
* Vulnerability management
* Network graph
* Network policy generation
* Kubernetes RBAC
* ServiceAccounts
* Resource management
* Security policies
* Deployment analysis

Verify RHACS:

```bash
kubectl get pods -n stackrox
```

---

# 17. Access RHACS with `roxctl`

Expose RHACS Central locally:

```bash
kubectl -n stackrox port-forward svc/central 18443:443
```

Configure the RHACS endpoint:

```bash
export ROX_ENDPOINT='localhost:18443'
export ROX_API_TOKEN='<RHACS_API_TOKEN>'
```

Because the lab uses a local port-forward:

```bash
roxctl central whoami --insecure-skip-tls-verify
```

This verifies that `roxctl` can authenticate against Central.

---

# 18. Scan the Backend Image

The backend image can be scanned using `roxctl`:

```bash
roxctl image scan \
  --image docker.io/aymankamell/myapp-backend:1.0 \
  --insecure-skip-tls-verify
```

This allows RHACS to analyze the image and identify known vulnerabilities and image metadata.

The image scan depends on RHACS Central being able to communicate with the configured container registry.

---

# 19. RHACS Network Graph

The RHACS Network Graph can be used to observe the actual communication paths between workloads.

Expected application communication:

```text
ingress-nginx
      |
      v
frontend
      |
      v
backend
      |
      v
postgres
```

For example, the backend should communicate with PostgreSQL over:

```text
TCP/5432
```

The backend can be used to generate database traffic:

```bash
kubectl exec -n myapp deploy/backend -- \
  python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8080/api/db').read().decode())"
```

After generating traffic, the corresponding flow can be observed in RHACS Network Graph.

---

# 20. Security Design

The application intentionally uses several Kubernetes security controls.

## ServiceAccount

The backend uses a dedicated ServiceAccount:

```text
myapp-backend
```

The ServiceAccount does not automatically mount a Kubernetes API token:

```yaml
automountServiceAccountToken: false
```

This follows the principle of minimizing unnecessary credentials inside application containers.

## RBAC

The backend has a dedicated Role and RoleBinding.

The Role provides only the permissions required by the application:

```text
get
list
watch
```

against ConfigMaps in the `myapp` namespace.

## Network Segmentation

NetworkPolicies restrict communication between application tiers.

The intended model is:

```text
Ingress Controller
        |
        v
    Frontend
        |
        v
     Backend
        |
        v
    PostgreSQL
```

## Resource Management

Resource requests and limits are defined for application containers.

A ResourceQuota limits the total resource consumption of the namespace.

## Persistent Storage

PostgreSQL uses a PersistentVolumeClaim rather than storing database data only inside the container filesystem.

---

# 21. Useful Troubleshooting Commands

Check all resources:

```bash
kubectl get all -n myapp
```

Check Pod status:

```bash
kubectl get pods -n myapp -o wide
```

Describe a Pod:

```bash
kubectl describe pod -n myapp <POD_NAME>
```

View logs:

```bash
kubectl logs -n myapp <POD_NAME>
```

Follow logs:

```bash
kubectl logs -n myapp -f <POD_NAME>
```

Check Services:

```bash
kubectl get svc -n myapp
```

Check Endpoints:

```bash
kubectl get endpoints -n myapp
```

Check NetworkPolicies:

```bash
kubectl get networkpolicy -n myapp
```

Describe a NetworkPolicy:

```bash
kubectl describe networkpolicy -n myapp <POLICY_NAME>
```

Check quota:

```bash
kubectl describe resourcequota -n myapp
```

---

# 22. Cleanup

To remove the application:

```bash
kubectl delete namespace myapp
```

This removes the application namespace and its namespaced resources.

If you want to keep the namespace and delete individual resources instead:

```bash
kubectl delete -f frontend/
kubectl delete -f backend/
kubectl delete -f database/
kubectl delete -f networkPolicy.yml
kubectl delete -f resource-quotas.yaml
```

---

# 23. Learning Objectives

This project is intended as a practical Kubernetes and RHACS security lab.

The main objectives are to practice:

```text
Kubernetes Deployments
Kubernetes StatefulSets
Kubernetes Services
Kubernetes Ingress
Kubernetes PersistentVolumeClaims
Kubernetes Secrets
Kubernetes ServiceAccounts
Kubernetes RBAC
Kubernetes NetworkPolicies
Kubernetes ResourceQuota
Container image building
Container image registries
RHACS image scanning
RHACS Network Graph
RHACS network policy generation
RHACS security policies
roxctl
Kubernetes troubleshooting
```
