# DevSecOps CI/CD Pipeline

## 1. Overview

This project implements an enterprise-oriented CI/CD pipeline that integrates software quality, security, supply-chain protection, container security, image signing, and GitOps-based deployment.

The pipeline is designed to provide security and quality controls throughout the software delivery lifecycle, from source-code changes through application deployment.

The architecture separates continuous integration from continuous deployment.

GitHub Actions is responsible for building, testing, scanning, validating, signing, and promoting application artifacts.

The GitOps repository represents the desired deployment state.

Argo CD continuously monitors the GitOps repository and reconciles the OpenShift environment with the desired state stored in Git.

Red Hat Advanced Cluster Security for Kubernetes provides additional container and runtime security controls.

---

# 2. Pipeline Architecture

The overall delivery process follows this sequence:

<img width="423" height="715" alt="image" src="https://github.com/user-attachments/assets/55cf2f50-bded-4ebe-a150-39d2c3387b56" />

---

# 3. Source Security

The source security stage performs security analysis against the application source before the application is built and promoted.

The stage includes vulnerability analysis of the source filesystem and dependency content.

It also performs secret detection to identify credentials, tokens, private keys, passwords, and other sensitive information that may have been accidentally committed to the repository.

The purpose of this stage is to identify security issues as early as possible in the development lifecycle.

A failed security control prevents the application from progressing through the pipeline.

---

# 4. Automated Unit Testing

The testing stage executes the application's automated unit tests.

Unit testing verifies that individual application components behave according to their expected functionality.

The test stage provides an automated validation mechanism that runs consistently for every applicable pipeline execution.

The test results are evaluated as part of the pipeline gate.

If the required tests fail, subsequent delivery stages are prevented from progressing.

---

# 5. Code Coverage

Code coverage measures the amount of application code exercised by the automated tests.

The coverage result provides visibility into how extensively the test suite exercises the application.

Coverage information is also made available to the static analysis platform so that code quality analysis can consider test coverage as part of the overall quality assessment.

Coverage reports are generated and retained as pipeline artifacts for later inspection.

---

# 6. Code Linting

The linting stage performs automated analysis of the source code according to the language and project coding standards.

Linting identifies issues such as:

* Syntax and formatting problems
* Unused code
* Code-quality violations
* Potential programming errors
* Violations of configured coding rules

The linting result is evaluated as a quality gate.

A failed linting gate prevents the pipeline from progressing.

A machine-readable report and a human-readable report are generated and retained as pipeline artifacts.

---

# 7. Static Code Analysis

The static analysis stage evaluates the source code without executing the application.

The analysis identifies potential code-quality and maintainability issues and provides additional software quality metrics.

The analysis platform also consumes the generated test coverage information.

A Quality Gate is used to determine whether the analyzed code meets the configured quality requirements.

The pipeline waits for the Quality Gate result before continuing.

A failed Quality Gate prevents the application from progressing to the subsequent build and security stages.

---

# 8. Application Build

After the source, test, and quality controls have passed, the application is built into its deployable form.

For containerized workloads, this stage produces the container image that will subsequently be scanned and promoted.

The image is associated with the source revision that produced it, providing traceability between the source code and the resulting artifact.

---

# 9. Container Image Vulnerability Scanning

The container image is scanned for known vulnerabilities before it is promoted for deployment.

The scan evaluates the operating system packages, application dependencies, and other components contained within the image.

The pipeline applies the configured severity policy to determine whether detected vulnerabilities are acceptable.

High and critical vulnerabilities are evaluated against the configured security gate.

The scan generates both structured and human-readable results.

The reports are retained as pipeline artifacts.

If the configured security gate fails, the image is not promoted to the subsequent supply-chain stages.

---

# 10. Software Bill of Materials

The pipeline generates a Software Bill of Materials for the container image.

The SBOM provides an inventory of the software components and dependencies contained within the image.

The SBOM improves software supply-chain visibility and provides information that can be used for vulnerability management, compliance, incident response, and component tracking.

The generated SBOM is retained as a pipeline artifact.

The SBOM is subsequently used as part of the image attestation process.

---

# 11. Container Image Registry

After the image passes the required container security controls, it is pushed to the configured container registry.

The registry stores the container image and provides an immutable digest that identifies the exact image content.

The deployment process uses the image digest rather than relying solely on a mutable image tag.

This ensures that the image deployed to the environment corresponds to the exact artifact that passed the pipeline controls.

---

# 12. Immutable Image Identification

The pipeline uses the image digest as the immutable identifier for deployment.

A container image tag can potentially be moved to different image content.

A digest, however, identifies a specific image manifest and its associated content.

Using the digest in the GitOps configuration provides deterministic deployment behavior.

The GitOps repository therefore records exactly which image artifact should be deployed.

---

# 13. RHACS Image Security Validation

Red Hat Advanced Cluster Security for Kubernetes is integrated into the CI/CD process to evaluate the container image against configured security policies.

The image is checked before it is promoted for deployment.

RHACS evaluates the image against the applicable build-stage policies and returns the policy evaluation result to the pipeline.

The pipeline uses the RHACS result as a security gate.

If the image violates a required RHACS policy, the pipeline fails and the deployment process does not proceed.

The RHACS policy results are generated in structured and human-readable formats and retained as pipeline artifacts.

---

# 14. Image Signing

After the image passes the required security controls, the image is cryptographically signed using Cosign.

Image signing establishes a verifiable relationship between the image artifact and the trusted signing identity.

The signature allows downstream systems to verify that the image was produced and signed by an authorized source.

The signing private key is protected using the CI/CD platform's secret-management mechanism and is not stored in the source repository.

The corresponding public key is used for signature verification.

---

# 15. SBOM Attestation

The generated SBOM is attached to the container image through a Cosign attestation.

The attestation provides a verifiable association between the image and the SBOM describing its contents.

The pipeline verifies the generated attestation after creation.

This provides an additional software supply-chain control by allowing downstream systems to verify that the image has an associated signed SBOM.

---

# 16. Signature Verification

After signing, the pipeline verifies the image signature using the configured public key.

The verification confirms that the image has a valid signature corresponding to the expected signing key.

Both signing and verification are performed as part of the pipeline.

This prevents the pipeline from promoting an artifact when the expected cryptographic verification cannot be completed successfully.

---

# 17. RHACS Cosign Signature Policy

RHACS contains a configured image security policy named:

**Require Cosign Signuture**

This policy requires applicable container images to satisfy the configured Cosign signature requirement.

The policy provides an additional security layer beyond the CI/CD pipeline.

The CI/CD pipeline signs and verifies the image before it is promoted.

RHACS subsequently evaluates the image against the configured signature policy when the image is used in the OpenShift environment.

This establishes a supply-chain trust model in which unsigned or improperly signed images can be prevented from being admitted according to the configured RHACS enforcement settings.

The policy also provides visibility into image-signature compliance through the RHACS console.

---

# 18. GitOps Deployment

The deployment stage follows a GitOps model.

Instead of directly modifying the OpenShift environment from the CI/CD pipeline, the pipeline updates the desired deployment state in the GitOps repository.

The update contains the immutable image digest associated with the validated container image.

The change is committed to Git, providing an auditable record of the deployment change.

Git therefore becomes the source of truth for the desired application state.

---

# 19. GitOps Repository

The GitOps repository contains the Kubernetes deployment configuration required to run the application.

It represents the desired state of the environment independently from the application source repository.

Application source changes are therefore separated from deployment configuration changes.

Every deployment change can be traced through Git history, including the image digest that was promoted.

---

# 20. Argo CD Automated Synchronization

Argo CD monitors the GitOps repository for changes.

When the desired state stored in Git changes, Argo CD detects the new Git revision.

Automated synchronization causes Argo CD to reconcile the OpenShift environment with the new desired state.

This removes the requirement for a manual deployment command after the GitOps repository has been updated.

Argo CD continuously maintains the relationship between the desired state in Git and the actual state running in OpenShift.

---

# 21. OpenShift Deployment

OpenShift is the runtime platform where the application workload is deployed.

Argo CD applies the desired state represented in the GitOps repository.

The deployment uses the immutable container image digest produced by the CI/CD process.

OpenShift performs the resulting workload rollout and maintains the application according to the declared Kubernetes resources.

---

# 22. Deployment Reconciliation

The deployment process is based on continuous reconciliation rather than a one-time deployment command.

The desired state is stored in Git.

Argo CD compares the desired state with the actual state of the OpenShift environment.

If a difference is detected, Argo CD can synchronize the environment according to the configured synchronization policy.

This provides continuous desired-state management.

---

# 23. Generated Reports and Artifacts

The pipeline generates reports throughout the software delivery lifecycle.

| Stage              | Generated Artifact              | Purpose                                         |
| ------------------ | ------------------------------- | ----------------------------------------------- |
| Unit Testing       | Test Report                     | Provides detailed automated test results        |
| Unit Testing       | Coverage Report                 | Provides code coverage information              |
| Linting            | Structured Lint Report          | Provides machine-readable linting results       |
| Linting            | HTML Lint Report                | Provides human-readable linting results         |
| Container Scanning | Structured Vulnerability Report | Provides machine-readable vulnerability results |
| Container Scanning | HTML Vulnerability Report       | Provides human-readable vulnerability results   |
| SBOM               | SPDX SBOM                       | Provides a software component inventory         |
| RHACS              | Structured Policy Report        | Provides machine-readable RHACS policy results  |
| RHACS              | HTML Policy Report              | Provides human-readable RHACS policy results    |

The generated artifacts are retained with the corresponding pipeline execution.

This provides traceability and allows security, quality, and testing results to be reviewed after the pipeline completes.

---

# 24. Pipeline Security Gates

The pipeline contains multiple security and quality gates.

| Control                      | Purpose                                                                        |
| ---------------------------- | ------------------------------------------------------------------------------ |
| Source Vulnerability Scan    | Identifies known vulnerabilities in source dependencies and filesystem content |
| Secret Detection             | Detects accidentally committed credentials and sensitive information           |
| Unit Testing                 | Validates application functionality                                            |
| Code Coverage                | Measures test execution coverage                                               |
| Linting                      | Validates source-code quality and coding standards                             |
| Static Analysis              | Identifies code-quality and maintainability issues                             |
| Quality Gate                 | Determines whether the source meets configured quality requirements            |
| Container Vulnerability Scan | Identifies vulnerabilities inside the container image                          |
| SBOM                         | Provides software component visibility                                         |
| RHACS Policy Validation      | Evaluates the image against container security policies                        |
| Image Signing                | Establishes cryptographic authenticity                                         |
| SBOM Attestation             | Provides verifiable software supply-chain metadata                             |
| Signature Verification       | Validates the image signature                                                  |
| RHACS Signature Policy       | Enforces the configured image-signature requirement                            |

These controls provide defense in depth across the software delivery lifecycle.

---

# 25. Failure and Promotion Model

Each security and quality stage can act as a promotion gate.

When a required control fails, the pipeline stops the affected delivery path.

Examples include:

* Source security findings exceeding the configured threshold
* Detected secrets
* Failed unit tests
* Linting violations
* Failed static analysis Quality Gate
* Container vulnerabilities exceeding the configured threshold
* RHACS policy violations
* Failed SBOM attestation
* Failed image signature verification
* Failed GitOps repository update

This prevents an artifact that has failed a required control from automatically progressing to deployment.

---

# 26. Auditability

The architecture provides traceability across the complete software delivery lifecycle.

GitHub Actions provides:

* Pipeline execution history
* Stage results
* Security results
* Test results
* Generated artifacts
* Build information

Git provides:

* Source-code history
* Deployment configuration history
* Image digest changes
* Deployment commits

Cosign provides:

* Image signatures
* SBOM attestations
* Cryptographic verification

RHACS provides:

* Image security policy results
* Signature policy results
* Security violations
* Runtime security visibility

Argo CD provides:

* Git revision tracking
* Synchronization status
* Application health
* Deployment history
* Desired-state reconciliation

OpenShift provides:

* Deployment status
* Workload status
* Rollout information
* Runtime state

---

# 27. Separation of Responsibilities

The architecture separates responsibilities between the major components.

## GitHub Actions

Responsible for continuous integration, security validation, artifact creation, image signing, and updating the desired deployment state.

## Container Registry

Responsible for storing and distributing validated container images.

## RHACS

Responsible for container security policy evaluation, image security controls, signature policy enforcement, and runtime security.

## GitOps Repository

Responsible for storing the desired deployment state and immutable image references.

## Argo CD

Responsible for monitoring the GitOps repository and reconciling the OpenShift environment with the desired state.

## OpenShift

Responsible for running and managing the application workload.

---


---

# 29. Design Principles

The implementation follows these principles:

1. Security is integrated throughout the software delivery lifecycle.
2. Quality and security controls are automated.
3. Failed security and quality gates prevent artifact promotion.
4. Container images are deployed using immutable digests.
5. Software components are documented through an SBOM.
6. Container images are cryptographically signed.
7. SBOMs are cryptographically attested.
8. Image signatures are independently verified.
9. RHACS provides additional image and runtime security controls.
10. The `Require Cosign Signuture` RHACS policy provides image-signature enforcement.
11. Git is the source of truth for the desired deployment state.
12. GitHub Actions does not directly deploy application workloads to OpenShift.
13. Argo CD performs automated synchronization and desired-state reconciliation.
14. Pipeline reports and artifacts provide evidence of testing and security validation.
15. Git history provides an auditable deployment trail.
16. CI and CD responsibilities are separated.
17. Application source and deployment configuration are maintained independently.

---
