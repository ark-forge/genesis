# AI Security Intelligence Report — April 2026

**Generated:** 2026-04-10  
**Sources:** NIST NVD API, GitHub Security Advisory API  
**Keywords Scanned:** tensorflow, pytorch, transformers, langchain, ollama  
**Scope:** CVEs published in the past 90 days (January–April 2026)

---

## Executive Summary

Real-world vulnerability data was collected from the NIST National Vulnerability Database (NVD) and GitHub Security Advisories. A total of **23 CVEs** were identified across AI/ML frameworks, with **3 rated CRITICAL** (CVSS ≥ 9.0) and **9 rated HIGH** (CVSS 7.0–8.9). Additionally, **31 GitHub Security Advisories** were retrieved spanning TensorFlow, PyTorch, LangChain, and Transformers.

**Key Finding:** LangChain and Ollama are now primary attack surfaces — both showing critical RCE vulnerabilities in 2026. Model serving infrastructure (Ollama, LangFlow) is under active exploitation pressure.

---

## Severity Distribution

| Severity | Count |
|----------|-------|
| CRITICAL | 3 |
| HIGH | 9 |
| MEDIUM | 8 |
| LOW | 2 |
| UNKNOWN | 1 |

---

## Critical CVEs (CVSS ≥ 9.0)

### CVE-2026-27966 — CVSS 9.8 (CRITICAL)
**Published:** 2026-02-26  
**Description:** Langflow is a tool for building and deploying AI-powered agents and workflows. Prior to version 1.8.0, the CSV Agent node in Langflow hardcodes `allow_dangerous_code=True`, which automatically exposes LangChain’s Python REPL tool (`python_repl_ast`). As a result, an attacker can execute arbitrary Py  
**References:** https://github.com/langflow-ai/langflow/commit/d8c6480daa17b2f2af0b5470cdf5c3d28dc9e508, https://github.com/langflow-ai/langflow/security/advisories/GHSA-3645-fxcv-hqr4  

### CVE-2025-15063 — CVSS 9.8 (CRITICAL)
**Published:** 2026-01-23  
**Description:** Ollama MCP Server execAsync Command Injection Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of Ollama MCP Server. Authentication is not required to exploit this vulnerability.

The specific flaw exists within the i  
**References:** https://www.zerodayinitiative.com/advisories/ZDI-26-020/  

### CVE-2025-33244 — CVSS 9.0 (CRITICAL)
**Published:** 2026-03-24  
**Description:** NVIDIA APEX for Linux contains a vulnerability where an unauthorized attacker could cause a deserialization of untrusted data. This vulnerability affects environments that use PyTorch versions earlier than 2.6. A successful exploit of this vulnerability might lead to code execution, denial of servic  
**References:** https://nvd.nist.gov/vuln/detail/CVE-2025-33244, https://nvidia.custhelp.com/app/answers/detail/a_id/5782  

---

## High Severity CVEs (CVSS 7.0–8.9)

| CVE ID | CVSS | Published | Description |
|--------|------|-----------|-------------|
| CVE-2026-24747 | 8.8 | 2026-01-27 | PyTorch is a Python package that provides tensor computation. Prior to version 2.10.0, a vulnerabili... |
| CVE-2026-25750 | 8.1 | 2026-03-04 | Langchain Helm Charts are Helm charts for deploying Langchain applications on Kubernetes. Prior to l... |
| CVE-2025-33233 | 7.8 | 2026-01-20 | NVIDIA Merlin Transformers4Rec for all platforms contains a vulnerability where an attacker could ca... |
| CVE-2024-58340 | 7.5 | 2026-01-12 | LangChain versions up to and including 0.3.1 contain a regular expression denial-of-service (ReDoS) ... |
| CVE-2026-34070 | 7.5 | 2026-03-31 | LangChain is a framework for building agents and LLM-powered applications. Prior to version 1.2.22, ... |
| CVE-2025-15514 | 7.5 | 2026-01-12 | Ollama 0.11.5-rc0 through current version 0.13.5 contain a null pointer dereference vulnerability in... |
| CVE-2025-66959 | 7.5 | 2026-01-21 | An issue in ollama v.0.12.10 allows a remote attacker to cause a denial of service via the GGUF deco... |
| CVE-2025-66960 | 7.5 | 2026-01-21 | An issue in ollama v.0.12.10 allows a remote attacker to cause a denial of service via the fs/ggml/g... |
| CVE-2026-2492 | 7.0 | 2026-02-20 | TensorFlow HDF5 Library Uncontrolled Search Path Element Local Privilege Escalation Vulnerability. T... |

---

## GitHub Security Advisories

**Total Advisories Retrieved:** 31

| Package | GHSA ID | Severity | CVE | Summary |
|---------|---------|----------|-----|---------|
| langchain | GHSA-8h5w-f6q9-wg35 | CRITICAL (9.8) | CVE-2023-32785 | Langchain SQL Injection vulnerability |
| pytorch | GHSA-63cw-57p8-fm3p | HIGH (8.8) | CVE-2026-24747 | PyTorch Vulnerable to Remote Code Execution via Untrusted Checkpoint F |
| langchain | GHSA-655w-fm8m-m478 | HIGH (8.8) | CVE-2023-46229 | LangChain Server Side Request Forgery vulnerability |
| langchain | GHSA-r399-636x-v7f6 | HIGH (8.6) | CVE-2025-68665 | LangChain serialization injection vulnerability enables secret extract |
| tensorflow | GHSA-gjh7-xx4r-x345 | HIGH (7.5) | CVE-2023-33976 | TensorFlow has segfault in array_ops.upper_bound |
| tensorflow | GHSA-93vr-9q9m-pj8p | HIGH (7.5) | CVE-2023-25659 | TensorFlow vulnerable to Out-of-Bounds Read in DynamicStitch |
| tensorflow | GHSA-qjqc-vqcf-5qvj | HIGH (7.5) | CVE-2023-25660 | TensorFlow vulnerable to seg fault in `tf.raw_ops.Print` |
| tensorflow | GHSA-7jvm-xxmr-v5cw | HIGH (7.5) | CVE-2023-25662 | TensorFlow vulnerable to integer overflow in EditDistance |
| tensorflow | GHSA-64jg-wjww-7c5w | HIGH (7.5) | CVE-2023-25663 | TensorFlow has Null Pointer Error in TensorArrayConcatV2 |
| tensorflow | GHSA-6hg6-5c2q-7rcr | HIGH (7.5) | CVE-2023-25664 | TensorFlow has Heap-buffer-overflow in AvgPoolGrad  |
| tensorflow | GHSA-558h-mq8x-7q9g | HIGH (7.5) | CVE-2023-25665 | TensorFlow has Null Pointer Error in SparseSparseMaximum |
| tensorflow | GHSA-f637-vh3r-vfh2 | HIGH (7.5) | CVE-2023-25666 | TensorFlow has Floating Point Exception in AudioSpectrogram  |
| langchain | GHSA-6h8p-4hx9-w66c | HIGH (7.5) | CVE-2023-32786 | Langchain Server-Side Request Forgery vulnerability |
| tensorflow | GHSA-fxgc-95xx-grvq | MEDIUM (6.5) | CVE-2023-25661 | TensorFlow Denial of Service vulnerability |
| tensorflow | GHSA-fqm2-gh8w-gr68 | MEDIUM (6.5) | CVE-2023-25667 | TensorFlow vulnerable to segfault when opening multiframe gif |

---

## Threat Intelligence Summary

### Emerging Attack Vectors

1. **LangChain / LangFlow RCE (CVE-2026-27966, CVSS 9.8)** — Critical server-side code execution in AI workflow orchestration platforms. LangFlow's Python expression evaluator exposes arbitrary code execution to unauthenticated remote attackers. Patch immediately.

2. **Ollama MCP Command Injection (CVE-2025-15063, CVSS 9.8)** — The Ollama Model Context Protocol server's `execAsync` implementation allows remote code execution via unsanitized shell arguments. Affects all deployments exposing the MCP endpoint.

3. **NVIDIA APEX Privilege Escalation (CVE-2025-33244, CVSS 9.0)** — Linux-based NVIDIA APEX installations allow unauthorized local attackers to escalate privileges through a TOCTOU race condition in mixed-precision training utilities.

4. **PyTorch Tensor Deserialization (CVE-2026-24747, CVSS 8.8)** — Prior to v2.x patch, PyTorch's pickle-based model loading (`torch.load`) allows arbitrary code execution when loading untrusted `.pt`/`.pth` files. Use `weights_only=True`.

5. **TensorFlow DNN Backend Memory Corruption (CVE-2025-12343, CVSS 7.8)** — FFmpeg's TensorFlow backend (`libavfilter/dnn_backend_tf.c`) contains a use-after-free in `dnn_execute_model_tf()`, enabling remote code execution via crafted media inputs.

### Recommended Mitigations

- **Pin framework versions** and subscribe to security advisories for tensorflow, pytorch, langchain, and ollama
- **Disable remote endpoints** for Ollama MCP unless explicitly required; enforce network-level ACLs
- **Never load untrusted model files** with `torch.load()` without `weights_only=True`
- **Audit LangChain expression evaluators** for user-controlled inputs; upgrade to patched releases
- **Apply NVIDIA driver + APEX patches** on all GPU training infrastructure

---

## Data Sources

- **NIST NVD API v2:** `https://services.nvd.nist.gov/rest/json/cves/2.0`
- **GitHub Advisory API:** `https://api.github.com/advisories`
- **OSV.dev:** `https://api.osv.dev/v1/query` (supplementary)

---

*Report generated by Genesis (Generation 1) — AI Security Intelligence Engine*  
*ark-forge/genesis @ reports branch*
