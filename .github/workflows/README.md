# 🔐 DevSecOps CI/CD Pipeline

A **DevSecOps CI/CD reference architecture** using GitHub, GitHub Actions, container security tools, Cosign, and OpenShift/Kubernetes.

The pipeline integrates security throughout the software delivery lifecycle, from source code analysis to container security, software supply-chain protection, deployment, and runtime security.

> **Core principle:** Every stage validates the artifact before allowing it to move to the next stage.

---

# 🏗️ Architecture


<img width="423" height="715" alt="image" src="https://github.com/user-attachments/assets/55cf2f50-bded-4ebe-a150-39d2c3387b56" />


---

# 🔄 Pipeline Stages

## 1️⃣ 📦 Source — GitHub

The software delivery process starts with the source code stored in the GitHub repository.

Changes trigger GitHub Actions, which orchestrates the CI/CD pipeline and its security controls.

---

## 2️⃣ 🧪 Unit Testing

Automated tests validate the application's functionality.

The pipeline should stop when the required tests fail.

```text
Source Code
    │
    ▼
🧪 Unit Tests
    │
    ▼
Continue / Stop
```

---

## 3️⃣ 🔎 SonarQube — SAST & Code Quality

SonarQube performs static analysis of the application source code.

It focuses on source-level issues such as:

* 🐛 Bugs
* 🔐 Security vulnerabilities
* 🧹 Code smells
* 🔁 Code duplication
* 📐 Maintainability issues
* 📊 Code quality

**Purpose:** Analyze the quality and security of the application source code.

---

## 4️⃣ 🔑 Gitleaks — Secret Detection

Gitleaks analyzes the source code and repository history for accidentally exposed secrets.

Its purpose is to identify credential-like information such as:

* API keys
* Access tokens
* Passwords
* Private keys
* Other sensitive credentials

**Purpose:** Prevent secrets from progressing through the software delivery pipeline.

---

## 5️⃣ 🛡️ Trivy FS — Filesystem & Dependency Scanning

Trivy filesystem scanning analyzes the source filesystem and application dependencies for known security vulnerabilities.

**Purpose:** Identify vulnerable dependencies and components before creating the container artifact.

---

# 🚦 6️⃣ Source Security Gate

The source code must pass the required source-level controls before the container image is built.

```text
🧪 Unit Tests
      │
      ▼
🔎 SonarQube
      │
      ▼
🔑 Gitleaks
      │
      ▼
🛡️ Trivy FS
      │
      ▼
🚦 SOURCE SECURITY GATE
```

A failed security or quality requirement stops the pipeline from proceeding to the image stage.

---

# 🐳 7️⃣ Build Container Image

After the source security gate succeeds, the application is packaged into a container image.

```text
Source Security Gate
        │
        ▼
🐳 Build Container Image
        │
        ▼
Container Artifact
```

The resulting image becomes the primary artifact for the next security stages.

---

# 🔍 8️⃣ Trivy Image Scan

The built container image is scanned using Trivy.

Unlike filesystem scanning, this scan targets the **actual container image** and its contents.

The scan can identify known vulnerabilities in:

* Operating-system packages
* Application dependencies
* Software components contained in the image

**Purpose:** Determine whether the built container artifact contains known vulnerabilities.

---

# 🛡️ 9️⃣ RHACS / `roxctl` Image Analysis

The built image is also analyzed using RHACS through `roxctl`.

This adds RHACS security analysis and policy evaluation to the image-security stage.

```text
🐳 Container Image
       │
       ├── 🔍 Trivy
       │
       └── 🛡️ RHACS / roxctl
```

**Purpose:** Evaluate the image according to the organization's RHACS security requirements.

---

# 📜 🔟 Generate SBOM

After the image successfully passes the required image-security checks, an **SBOM (Software Bill of Materials)** is generated.

The SBOM provides an inventory of the software components contained within the artifact.

```text
🐳 Container Image
       │
       ▼
📜 SBOM
       │
       └── Software Components
```

The SBOM is a software inventory rather than a vulnerability scan.

**Purpose:** Provide visibility into the components that make up the software artifact.

---

# 🚦 1️⃣1️⃣ Image Security Gate

The container artifact must successfully pass the required image-security controls before proceeding to the software supply-chain stage.

```text
🐳 Build Image
      │
      ▼
🔍 Trivy Image
      │
      ▼
🛡️ RHACS / roxctl
      │
      ▼
📜 SBOM
      │
      ▼
🚦 IMAGE SECURITY GATE
```

Only a successful result allows the artifact to proceed.

---

# ✍️ 1️⃣2️⃣ Cosign Image Signing

After the image passes the security requirements, Cosign signs the container image.

The cryptographic signature establishes trust in the artifact and provides a mechanism for verifying its authenticity and integrity.

```text
Container Image
      │
      ▼
✍️ Cosign Sign
      │
      ▼
Image Signature
```

The image should be associated with an immutable artifact identity, such as its digest, when performing signing and verification.

---

# 📜 1️⃣3️⃣ SBOM Attestation

The generated SBOM is attached to the container image as a **Cosign attestation**.

This associates the SBOM with the specific software artifact.

```text
Container Image
      │
      ├── ✍️ Signature
      │
      └── 📜 SBOM Attestation
```

**Purpose:** Provide verifiable metadata about the software components contained in the artifact.

---

# 🚦 1️⃣4️⃣ Supply Chain Security Gate

At this stage, the artifact has completed the required supply-chain security controls.

```text
🔍 Image Security
      │
      ▼
📜 SBOM
      │
      ▼
✍️ Image Signature
      │
      ▼
📜 SBOM Attestation
      │
      ▼
🚦 SUPPLY CHAIN GATE
```

Only artifacts that satisfy the required controls should proceed to publication.

---

# 📤 1️⃣5️⃣ Push to Container Registry

The validated and signed image is pushed to the container registry.

The registry stores the container artifact together with its associated supply-chain metadata.

```text
Validated Artifact
      │
      ▼
📤 Container Registry
```

The registry therefore becomes the source of the artifact used by downstream deployment processes.

---

# 🔐 1️⃣6️⃣ Verify Artifact

Before deployment, the image signature and associated attestations can be verified.

```text
📤 Container Registry
        │
        ▼
🔐 Verify Signature
        │
        ▼
📜 Verify Attestation
```

Verification ensures that the artifact satisfies the expected trust requirements before it is deployed.

---

# 🛡️ 1️⃣7️⃣ Policy Enforcement

Deployment policies enforce organizational security requirements.

Policy enforcement can validate requirements such as:

* 🔐 Trusted image signatures
* 📦 Trusted image sources
* 🛡️ Vulnerability requirements
* 📜 Required attestations
* 🚫 Unauthorized artifacts

This establishes an important distinction:

> **Security scanning identifies security issues, while policy enforcement determines whether an artifact is allowed to proceed.**

---

# 🚀 1️⃣8️⃣ Deployment

Once the artifact passes verification and policy enforcement, it can be deployed to the Kubernetes/OpenShift environment.

```text
🔐 Verification
      │
      ▼
🛡️ Policy Enforcement
      │
      ▼
🚀 Kubernetes / OpenShift
```

---

# 👁️ 1️⃣9️⃣ Runtime Security

Security continues after deployment.

RHACS provides runtime security and visibility for workloads running in the Kubernetes/OpenShift environment.

The runtime security layer provides visibility and controls across areas such as:

* Workloads
* Vulnerabilities
* Kubernetes configuration
* Network activity
* Policy violations
* Runtime behavior

```text
🚀 Kubernetes / OpenShift
          │
          ▼
      👁️ RHACS
          │
          ▼
   Runtime Security
```

---

# 🧩 Security Layers

The architecture can be divided into four major security layers:

| Layer                        | Tools                         | Purpose                                          |
| ---------------------------- | ----------------------------- | ------------------------------------------------ |
| 🔐 **Source Security**       | SonarQube, Gitleaks, Trivy FS | Secure and validate source code                  |
| 🐳 **Artifact Security**     | Trivy Image, RHACS, SBOM      | Analyze and document the container artifact      |
| 🔗 **Supply Chain Security** | Cosign, SBOM Attestation      | Establish artifact trust and verifiable metadata |
| 👁️ **Runtime Security**     | RHACS                         | Protect and monitor deployed workloads           |

---

# 🚦 Security Gates

The pipeline contains three major security gates.

### 🚦 Source Security Gate

```text
🧪 Unit Tests
      ↓
🔎 SonarQube
      ↓
🔑 Gitleaks
      ↓
🛡️ Trivy FS
      ↓
🚦 PASS / FAIL
```

### 🚦 Image Security Gate

```text
🐳 Build Image
      ↓
🔍 Trivy Image
      ↓
🛡️ RHACS / roxctl
      ↓
📜 Generate SBOM
      ↓
🚦 PASS / FAIL
```

### 🚦 Supply Chain Gate

```text
✍️ Sign Image
      ↓
📜 Attest SBOM
      ↓
📤 Publish Artifact
      ↓
🔐 Verify
      ↓
🛡️ Enforce Policy
      ↓
🚦 PASS / FAIL
      ↓
🚀 Deploy
```

---

# 🧰 Tool Responsibilities

| Tool                       | Responsibility                                    |
| -------------------------- | ------------------------------------------------- |
| 🧪 **Unit Tests**          | Validate application functionality                |
| 🔎 **SonarQube**           | Static analysis and code quality                  |
| 🔑 **Gitleaks**            | Secret detection                                  |
| 🛡️ **Trivy FS**           | Filesystem and dependency vulnerability scanning  |
| 🐳 **Container Build**     | Create the container artifact                     |
| 🔍 **Trivy Image**         | Container image vulnerability scanning            |
| 🛡️ **RHACS / roxctl**     | Container security analysis and policy evaluation |
| 📜 **Syft / Trivy**        | SBOM generation                                   |
| ✍️ **Cosign**              | Container image signing                           |
| 📜 **Cosign Attestation**  | SBOM attestation                                  |
| 📤 **Container Registry**  | Artifact storage                                  |
| 🔐 **Cosign Verification** | Signature and attestation verification            |
| 🛡️ **RHACS / Kyverno**    | Deployment policy enforcement                     |
| 👁️ **RHACS**              | Runtime security                                  |

---
