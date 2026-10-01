# DevSecOps CI/CD Pipeline

## 1. Overview

This document specifies an enterprise-grade CI/CD pipeline architecture integrating automated static code analysis, software supply-chain security, cryptographic artifact signing, runtime policy enforcement, and GitOps-driven deployment. Continuous Integration (CI) is decoupled from Continuous Deployment (CD): GitHub Actions orchestrates source security, quality gates, image builds, vulnerability analysis, artifact signing, and deployment manifest updates. Continuous Deployment is managed via Argo CD, which continuously reconciles the target state defined in a dedicated GitOps repository with the Red Hat OpenShift environment.

## 2. Pipeline Architecture


<img width="1588" height="572" alt="Screenshot 2026-10-01 141914" src="https://github.com/user-attachments/assets/35f54a5c-cfbb-4a43-a75b-180452e3f6d9" />



The delivery pipeline operates sequentially through static validation, artifact compilation, container security, cryptographic attestation, and GitOps promotion. Every phase functions as an explicit fail-closed promotion gate; failure at any point terminates the pipeline before artifact promotion.

## 3. Security, Quality, and Supply-Chain Tooling

The pipeline consolidates static, dynamic, and supply-chain controls into a unified toolchain:

| Tool | Category | Purpose / Function | Pipeline Stage | Gate Effect |
| --- | --- | --- | --- | --- |
| **Trivy FS** | SAST / SCA | Scans source filesystem for dependency vulnerabilities | Source Security | Fails pipeline on threshold breach |
| **Gitleaks** | Secret Detection | Identifies hardcoded keys, tokens, and credentials | Source Security | Fails pipeline on detected secrets |
| **pytest** | Dynamic Testing | Executes automated unit test suite | Unit Testing | Fails pipeline on test failure |
| **pytest-cov** | Quality Metric | Measures source code test execution coverage | Code Coverage | Generates coverage metrics |
| **Ruff** | Linter | Validates python code quality and syntax standards | Linting | Fails pipeline on linting errors |
| **SonarQube** | Static Analysis | Analyzes code quality, debt, and security flaws | Static Analysis | Fails pipeline on Quality Gate breach |
| **Trivy Image** | Container Security | Scans OS packages and image layer dependencies | Image Scan | Fails pipeline on High/Critical CVEs |
| **Syft / Trivy** | Supply Chain | Generates standardized SPDX Software Bill of Materials | SBOM | Pipeline halts if generation fails |
| **Cosign** | Cryptography | Signs image digests and attaches SBOM attestations | Signing & Attestation | Fails pipeline on signing failure |
| **RHACS (`roxctl`)** | Policy Engine | Evaluates image compliance against cluster policies | RHACS Image Validation | Fails pipeline on policy violation |



## 4. RHACS Runtime & Build-Time Policy Enforcement

RHACS operates at both the CI/CD build phase and the OpenShift cluster admission phase to enforce corporate governance.

| Policy Name | Enforcement Point | Severity / Condition | Pipeline Effect | Purpose |
| --- | --- | --- | --- | --- |
| **Require Cosign Signature** | Cluster Admission / Deploy | Unsigned or invalid image signature | Blocks deployment in OpenShift | Guarantees only cryptographically verified images execute in the cluster |
| **Block Images with Important or Critical Vulnerabilities** | Build-Time Gate (`roxctl`) | CVE Severity $\ge$ **Important** or **Critical** | Fails CI pipeline prior to promotion | Prevents vulnerable artifacts from reaching the deployment repository |

This multi-layered approach provides defense-in-depth: Trivy and Cosign perform local image scanning and key generation within the CI pipeline, while RHACS independently verifies these artifacts against cluster-wide policies at build time and blocks unauthorized deployment attempts at runtime via OpenShift Admission Controllers.

## 5. GitOps Delivery Model

Application deployment follows a strictly pull-based GitOps pattern:

1. **GitOps Repository:** Houses pure deployment manifests (Helm/Kustomize). GitHub Actions updates the container image reference using its strict SHA256 digest.
2. **Argo CD Reconciliation:** Argo CD monitors the GitOps repository for state drift. Upon detecting an updated digest commit, it reconciles the OpenShift environment.
3. **OpenShift Rollout:** OpenShift fetches the signed image digest from the registry, evaluates admission via RHACS policies, and updates the running pods.


## 6. Pipeline Security Gates

| Control | Mechanism | Promotion Effect |
| --- | --- | --- |
| **Source Security Scan** | Trivy FS dependency check | Blocks pipeline on vulnerable source libraries |
| **Secret Detection** | Gitleaks pattern matching | Blocks pipeline on exposed credentials |
| **Unit Testing** | pytest assertion checks | Blocks pipeline on code regression |
| **Code Linting** | Ruff rule enforcement | Blocks pipeline on code standard violations |
| **Static Code Analysis** | SonarQube Quality Gate API | Blocks pipeline on quality or security debt |
| **Container Scan** | Trivy Image severity parser | Blocks pipeline on High/Critical container CVEs |
| **RHACS Policy Validation** | `roxctl image check` CLI | Blocks pipeline on policy non-compliance |
| **Signature Verification** | Cosign public key verification | Blocks promotion on missing signature |

## 7. Generated Reports & Pipeline Artifacts

| Stage | Generated Artifact | Purpose |
| --- | --- | --- |
| **Unit Testing** | Test Report | Detailed test execution metrics |
| **Unit Testing** | Coverage Report | Code execution percentage files |
| **Linting** | Structured & HTML Lint Reports | Machine and human-readable lint output |
| **Container Scanning** | Structured & HTML Vulnerability Reports | Detailed CVE inventory and severity breakdown |
| **SBOM** | SPDX SBOM (`.json`) | Machine-readable software component inventory |
| **RHACS** | Structured & HTML Policy Reports | Build-stage security policy audit logs |


## 8. Auditability & Separation of Responsibilities

### 8.1. Platform Traceability Matrix

| Platform | Auditability Role | Primary Data Captured |
| --- | --- | --- |
| **GitHub Actions** | Execution Auditing | Pipeline step logs, build metadata, test run artifacts |
| **Cosign** | Supply Chain Trust | Public key signatures, signed in-toto attestation payloads |
| **RHACS** | Compliance & Policy | Build-time validation logs, admission policy decisions |
| **Argo CD** | Continuous Deployment | Sync state history, deployment revisions, cluster drift |
| **OpenShift** | Runtime Platform | Pod logs, container event streams, deployment rollouts |

### 8.2. Component Separation of Responsibilities

| System | Core Responsibility | Boundary Constraints |
| --- | --- | --- |
| **GitHub Actions** | CI Automation & Signing | No direct cluster deployment privileges |
| **Container Registry** | Artifact Storage | Stores immutable images, signatures, and attestations |
| **RHACS** | Security Governance | Enforces runtime and build-time compliance policies |
| **GitOps Repo** | Single Source of Truth | Houses environment configuration states only |
| **Argo CD** | State Reconciliation | Unidirectional pull-based sync into OpenShift |
| **OpenShift** | Container Orchestration | Executes workloads according to desired Git state |

## 9. Conclusion

This enterprise DevSecOps pipeline establishes an automated, policy-driven software supply chain linking initial source commit to OpenShift deployment. By integrating cryptographic image signing, SBOM attestations, build-time security gates, and pull-based GitOps synchronization, the delivery framework guarantees that only thoroughly audited, authentic, and compliant artifacts reach production environments.
