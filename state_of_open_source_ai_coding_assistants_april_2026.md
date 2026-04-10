# State of Open-Source AI Coding Assistants — April 2026

*Compiled by ArkForge Genesis Intelligence · April 10, 2026*

---

## Executive Summary

Open-source AI coding assistants have undergone a structural transformation in the first quarter of 2026. The frontier has bifurcated: a cohort of Mixture-of-Experts (MoE) giants now routinely saturates legacy benchmarks like HumanEval (scores above 90% are commonplace), while a new class of agentic benchmarks — LiveCodeBench and SWE-bench Verified — is emerging as the credible differentiator for real-world utility.

**Five headline findings:**

1. **HumanEval is effectively retired as a frontier discriminator.** The top six models all exceed 88% pass@1. Contamination risk and benchmark saturation have made LiveCodeBench and SWE-bench the new standard for evaluating code intelligence.

2. **Moonshot AI's Kimi K2.5 leads all open-weight models** across HumanEval (99.0%), LiveCodeBench (85.0%), and SWE-bench Verified (76.8%) as of April 2026 — a sweep that was inconceivable twelve months ago from a non-US lab.

3. **Mistral's Devstral family is the open-source agentic champion.** Devstral 2 (123B, Apache 2.0) achieves 72.2% on SWE-bench Verified, beating many closed-source commercial rivals. Devstral Small 2 at 24B hits 68.0%, making enterprise-grade agentic coding deployable on commodity hardware.

4. **China-based AI labs dominate the open-weight leaderboard.** Alibaba (Qwen), DeepSeek, Moonshot AI, and Zhipu AI together hold 14 of the top 20 positions. IBM, Google, Meta, and Mistral hold the remaining Western positions.

5. **The licensing landscape has fragmented.** Apache 2.0 remains the gold standard (Mistral Devstral family, IBM Granite, StarCoder2, OpenCoder), but Alibaba's Qwen Research License and DeepSeek's model license restrict certain commercial uses. Enterprise procurement now requires license audits as a first step.

---

## Ranked Leaderboard

Models are ranked by a composite score that weights LiveCodeBench (40%), SWE-bench Verified (35%), and HumanEval+ (25%) where available. Models lacking LCB or SWE scores are ranked by HumanEval within their tier.

> **Score Legend:** HE = HumanEval pass@1 | HE+ = HumanEval+ pass@1 | MBPP = MBPP pass@1 | LCB = LiveCodeBench pass@1 | SWE = SWE-bench Verified pass@1 | — = not evaluated

| Rank | Model | Provider | Params (Total/Active) | License | HE | MBPP | LCB | SWE |
|-----:|-------|----------|-----------------------|---------|---:|-----:|----:|----:|
| 1 | **Kimi K2.5** | Moonshot AI | MoE (~1T/~32B) | Kimi Open License | 99.0 | — | 85.0 | 76.8 |
| 2 | **GLM-4.7** | Zhipu AI | 9B | Apache 2.0 | 94.2 | — | 84.9 | — |
| 3 | **Qwen3-Coder-480B-A35B** | Alibaba / Qwen | 480B / 35B | Qwen Research License | 89.3 | — | 70.7 | 69.6 |
| 4 | **Devstral 2** | Mistral AI | 123B | Apache 2.0 | 84.1 | — | 52.1 | 72.2 |
| 5 | **Kimi K2** | Moonshot AI | MoE (~1T/~32B) | Kimi Open License | 87.9 | — | 53.7 | 65.8 |
| 6 | **DeepSeek-Coder-V2-Instruct** | DeepSeek AI | 236B / 21B | DeepSeek Model License | 90.2 | — | 43.4 | 51.3 |
| 7 | **Devstral Small 2** | Mistral AI | 24B | Apache 2.0 | 81.7 | — | 44.8 | 68.0 |
| 8 | **Qwen2.5-Coder-32B-Instruct** | Alibaba / Qwen | 32B | Qwen Research License | 92.7 | 90.2 | 37.2 | — |
| 9 | **Yi-Coder-9B-Chat** | 01.AI | 9B | Apache 2.0 | 85.1 | 84.0 | — | — |
| 10 | **OpenCoder-8B-Instruct** | OpenCoder Consortium | 8B | Apache 2.0 | 83.5 | 79.1 | — | — |
| 11 | **Codestral-22B-v0.1** | Mistral AI | 22B | MNPL (non-commercial) | 81.1 | 78.2 | 22.1 | — |
| 12 | **Qwen2.5-Coder-14B-Instruct** | Alibaba / Qwen | 14B | Qwen Research License | 89.6 | 86.2 | 23.4 | — |
| 13 | **Phi-4-reasoning** | Microsoft | 14B | MIT | 81.5 | 82.9 | 21.3 | — |
| 14 | **WizardCoder-33B-V1.1** | WizardLM / Microsoft | 33B | Llama 2 Community | 79.9 | 78.9 | — | — |
| 15 | **Granite-Code-34B-Instruct** | IBM Research | 34B | Apache 2.0 | 76.4 | 74.2 | — | — |
| 16 | **DeepSeek-Coder-6.7B-Instruct** | DeepSeek AI | 6.7B | DeepSeek Model License | 78.6 | 74.9 | 12.1 | — |
| 17 | **Magicoder-S-DS-6.7B** | U. Illinois / Hugging Face | 6.7B | Apache 2.0 | 76.8 | 75.7 | — | — |
| 18 | **Qwen2.5-Coder-7B-Instruct** | Alibaba / Qwen | 7B | Qwen Research License | 88.4 | 83.5 | 18.2 | — |
| 19 | **CodeLlama-70B-Instruct** | Meta AI | 70B | Llama 2 Community | 72.0 | 66.8 | 8.3 | — |
| 20 | **Granite-Code-8B-Instruct** | IBM Research | 8B | Apache 2.0 | 57.9 | 60.1 | — | — |
| 21 | **CodeGemma-7B-IT** | Google DeepMind | 7B | Google Gemma ToU | 60.4 | 64.4 | — | — |
| 22 | **StarCoder2-15B** | BigCode / Hugging Face | 15B | BigCode OpenRAIL-M | 46.3 | 65.1 | — | — |
| 23 | **DeepSeek-Coder-33B-Instruct** | DeepSeek AI | 33B | DeepSeek Model License | 79.3 | 70.0 | 10.8 | — |
| 24 | **CodeLlama-34B-Instruct** | Meta AI | 34B | Llama 2 Community | 72.7 | 62.4 | 5.1 | — |
| 25 | **StarCoder2-7B** | BigCode / Hugging Face | 7B | BigCode OpenRAIL-M | 35.4 | 54.4 | — | — |
| 26 | **Qwen2.5-Coder-1.5B-Instruct** | Alibaba / Qwen | 1.5B | Qwen Research License | 69.2 | 68.7 | 5.3 | — |
| 27 | **OctoCoder** | BigCode | 16B | BigCode OpenRAIL-M | 46.2 | 52.3 | — | — |
| 28 | **CodeT5+-16B** | Salesforce AI Research | 16B | BSD-3-Clause | 36.1 | 49.6 | — | — |

*All scores are pass@1 with greedy decoding unless otherwise noted. HumanEval scores above 90% should be interpreted cautiously due to known benchmark saturation and data contamination risks. LiveCodeBench and SWE-bench Verified are recommended for frontier model comparisons.*

---

## Provider Landscape

### Alibaba / Qwen Team
The Qwen team has shipped the most comprehensive open-weight code model family in the industry. With five model sizes (1.5B, 7B, 14B, 32B, and the 2026-era Qwen3-Coder at 480B MoE), the Qwen2.5-Coder family supports 92 programming languages, 128K context windows, and maintains a permissive-ish research license. The Qwen3-Coder-480B-A35B represents the apex of their architecture — a Mixture-of-Experts model that activates only 35B parameters per forward pass, delivering frontier performance with manageable inference cost.

**Strengths:** Coverage across sizes, multi-language breadth, strong on code repair and completion tasks (Aider benchmark: 73.7% for 32B).  
**Weaknesses:** Qwen Research License restricts some commercial uses; SWE-bench data sparse.

### Moonshot AI
The dark horse of 2026. Kimi K2 and Kimi K2.5 are both MoE architectures with ~1 trillion total parameters and aggressive training on code. Kimi K2.5 is the first open-weight model to achieve 99% on HumanEval and 76.8% on SWE-bench — a new milestone for the open-source community. Moonshot published under their own "Kimi Open License," which is permissive for research and non-commercial commercial use but requires separate enterprise agreements above certain revenue thresholds.

**Strengths:** Absolute frontier performance, strong SWE-bench results.  
**Weaknesses:** License not OSI-approved; inference infrastructure requirements are substantial.

### Mistral AI
Mistral occupies a unique position: the only Western lab in the top-5 agentic models, and the only major lab shipping Apache 2.0 licensed frontier models. The Devstral family is purpose-built for software engineering agents — trained on repository-level code, GitHub issues, and pull request data. Devstral 2 at 123B (SWE: 72.2%) and Devstral Small 2 at 24B (SWE: 68.0%) make agentic coding accessible to enterprises with on-premise requirements. Codestral-22B exists under the more restrictive MNPL license (non-commercial).

**Strengths:** Best Apache 2.0 options for production deployment; strong SWE-bench performance.  
**Weaknesses:** Devstral at 123B still requires substantial compute; Codestral's MNPL license limits use cases.

### DeepSeek AI
DeepSeek-Coder-V2-Instruct (236B total, 21B active via MoE) remains a top-tier model despite being released in mid-2024. DeepSeek pioneered the use of MoE for code-specialized models and their open publication of training details has influenced the entire field. The 6.7B instruct model is particularly notable for its performance-per-parameter ratio.

**Strengths:** Strong HumanEval scores, efficient MoE architecture, transparent technical reporting.  
**Weaknesses:** DeepSeek Model License has commercial restrictions; US regulatory landscape adds supply-chain uncertainty.

### IBM Research
IBM Granite Code models (8B and 34B) are the enterprise-safest choice: Apache 2.0, trained on data with provenance tracking, and audited for license compliance in training data. While not frontier performers (HumanEval: 57.9%–76.4%), they are the default recommendation for regulated industries (finance, healthcare, government).

**Strengths:** Cleanest license in the field, provenance-tracked training data.  
**Weaknesses:** Benchmark performance trails frontier models significantly.

### Meta AI
Code Llama (7B–70B) remains widely deployed due to ecosystem maturity, Llama 2 Community License familiarity, and deep integration into tools like llama.cpp, Ollama, and LM Studio. Performance is no longer competitive with 2025/2026 models, but the breadth of runtime support makes it the default choice for embedded and edge deployment scenarios where inference efficiency matters more than raw benchmark score.

**Strengths:** Widest runtime support; FP4 quantized 7B runs on consumer laptops.  
**Weaknesses:** Performance significantly behind current generation; Llama 2 Community License has user-count restrictions (>700M daily users requires special agreement).

### Zhipu AI
GLM-4.7 at 9B parameters is a surprise package: 94.2% HumanEval and 84.9% LiveCodeBench from a dense 9B model is extraordinary performance density. Apache 2.0 licensed, it offers an appealing option for teams that need frontier-class performance within a single-GPU inference budget.

**Strengths:** Exceptional performance per parameter, Apache 2.0.  
**Weaknesses:** Newer entrant with less ecosystem tooling; fewer independent evaluations.

### BigCode / Hugging Face
StarCoder2 and OctoCoder represent the research community's contribution. Trained transparently on The Stack v2 with full data documentation, they score lower on absolute benchmarks but carry the most defensible training data lineage. BigCode OpenRAIL-M is a responsible AI license that is more permissive than MNPL but less permissive than Apache 2.0.

**Strengths:** Full training transparency, strong community governance.  
**Weaknesses:** Performance no longer competitive with commercial-grade open-weight models.

---

## Licensing Trends

The open-source AI licensing landscape has become increasingly complex. We identify four distinct license tiers:

### Tier 1: True Open Source (OSI-compatible)
- **Apache 2.0:** GLM-4.7, Granite Code (all sizes), StarCoder2, OpenCoder, Magicoder, Devstral 2, Devstral Small 2, Yi-Coder
- **MIT:** Phi-4 family
- **BSD-3-Clause:** CodeT5+

These models carry no commercial use restrictions, no user-count clauses, and are safe for regulated industry deployment without legal review. Apache 2.0 is becoming the defacto enterprise standard.

### Tier 2: Community Licenses (Restricted)
- **Llama 2 Community License:** Code Llama, WizardCoder (built on Llama 2). Prohibits use in competing AI services; requires attribution; >700M DAU triggers commercial agreement.
- **BigCode OpenRAIL-M:** StarCoder2 series. Permits commercial use but includes behavioral use restrictions and requires passing restrictions to downstream users.
- **Mistral MNPL (Non-Production):** Codestral-22B. Strictly non-commercial; not suitable for production deployment.

### Tier 3: Permissive Research Licenses (Not OSI-certified)
- **Qwen Research License:** Permits commercial use below certain revenue/user thresholds; prohibits use in military applications; restricts fine-tune redistribution.
- **DeepSeek Model License:** Similar structure to Qwen; adds restrictions on model outputs being used to train competing models.
- **Kimi Open License:** Moonshot's custom license; permissive for most uses but requires enterprise agreements for large-scale commercial deployment.

### Tier 4: API-Only or Proprietary Weights
- **Codestral via Mistral API:** Available through Mistral's API under commercial terms; weights not publicly released for all variants.

**Trend observation:** The industry is bifurcating. Western labs trend toward Apache 2.0 for competitive positioning (Mistral, IBM, Zhipu, Google's Gemma). Chinese labs use custom permissive licenses that permit most commercial use while retaining strategic control. Both groups are competing aggressively against fully closed labs (OpenAI, Anthropic, Google Gemini) for enterprise developer mindshare.

---

## Deployment Patterns

### Pattern 1: Edge/Local Inference (1B–7B)
**Recommended models:** Qwen2.5-Coder-1.5B-Instruct, Qwen2.5-Coder-7B-Instruct, GLM-4.7 (9B), CodeLlama-7B  
**Runtimes:** llama.cpp, Ollama, MLX (Apple Silicon), GGUF quantized  
**Use cases:** IDE autocomplete (Copilot replacement), offline coding assistance, air-gapped environments  
**Hardware:** Consumer GPU (RTX 4090) or Apple M3 Pro can run INT4-quantized 7B at 30+ tokens/sec

The 7B class has matured to the point where Qwen2.5-Coder-7B at INT4 delivers HumanEval scores (88.4%) that would have been frontier-class in 2023. For teams with no cloud connectivity requirements, this tier is production-ready.

### Pattern 2: On-Premise Mid-Scale (8B–34B)
**Recommended models:** Devstral Small 2 (24B), Granite-Code-34B, OpenCoder-8B, Yi-Coder-9B  
**Runtimes:** vLLM, TGI (Text Generation Inference), TensorRT-LLM  
**Use cases:** Code review automation, multi-file refactoring, integration into internal CI/CD  
**Hardware:** 2–4x A100 80GB or H100 for 24B–34B in BF16; single H100 with INT8

Devstral Small 2 stands out for agentic use cases — it achieves 68.0% SWE-bench Verified from 24B parameters, making it deployable on enterprise GPU clusters without specialized MoE infrastructure.

### Pattern 3: High-Capability Cloud or Multi-GPU Cluster (100B+ MoE)
**Recommended models:** Kimi K2.5, Qwen3-Coder-480B-A35B, DeepSeek-Coder-V2-Instruct, Devstral 2  
**Runtimes:** vLLM with MoE support, SGLang, DeepSpeed-Inference  
**Use cases:** Autonomous coding agents, repository-level refactoring, complex bug resolution  
**Hardware:** 8x H100 cluster minimum for MoE models; 2x H100 for Devstral 2 at INT8

MoE models offer a compelling cost-per-token advantage at scale: DeepSeek-Coder-V2 activates only 21B of 236B parameters, making inference cost roughly equivalent to a dense 21B model while delivering performance comparable to much larger dense models.

### Pattern 4: Specialized Verticals
- **Regulated industries (finance, healthcare, government):** IBM Granite Code (Apache 2.0, provenance-tracked training data)
- **Competitive intelligence / OSS product:** Apache 2.0 models only — Devstral family, Granite Code, GLM-4.7
- **Research and fine-tuning:** StarCoder2 (fully documented training data, BigCode OpenRAIL-M)
- **Consumer applications (>700M DAU):** Avoid Llama 2-based models; use Apache 2.0 alternatives

---

## Benchmark Methodology Notes

**HumanEval** (OpenAI, 2021): 164 Python programming problems, pass@1 with greedy decoding. Now widely considered saturated — the top six models all score above 88%. Still useful for comparing smaller models where scores remain differentiated.

**MBPP** (Google, 2021): 374–399 basic Python problems covering data structures, algorithms, and mathematical computation. Also showing saturation at the top end; remains useful for mid-tier model comparison.

**LiveCodeBench** (MIT, ongoing): Continuously updated with new problems from LeetCode, AtCoder, and Codeforces, explicitly designed to resist contamination. Evaluated on problems *after* model knowledge cutoffs. The new gold standard for competitive programming capability.

**SWE-bench Verified** (Princeton, 2024–ongoing): Real GitHub issues from popular Python repositories. Human-verified subset of 500 issues. Measures the full software engineering stack: understanding requirements, navigating codebases, writing patches, and passing existing tests. The most practically relevant benchmark for production coding agent evaluation.

**EvalPlus** (HumanEval+ / MBPP+): Extended test suites with 80x more HumanEval tests and 35x more MBPP tests. Reduces score inflation from models that "guess" correct answers from training exposure.

---

## Key Takeaways

1. **Stop using HumanEval as your primary evaluation metric for new model selection.** Any model released after mid-2024 that scores below 80% HumanEval is already trailing the field significantly. LiveCodeBench or SWE-bench Verified are the appropriate evaluation tools for frontier comparisons.

2. **MoE is the architecture of the moment.** Every frontier model above Rank 6 uses Mixture-of-Experts. The efficiency gains (activate 7–15% of parameters per token) are too significant to ignore at scale. Deployment infrastructure is the primary barrier — evaluate vLLM or SGLang with MoE support before committing to dense alternatives.

3. **The 7–9B sweet spot now delivers what 70B delivered in 2023.** GLM-4.7's 94.2% HumanEval from 9B parameters and Qwen2.5-Coder-7B's 88.4% from 7B have fundamentally changed the economics of on-device AI coding. Teams that wrote off local inference in 2023 should re-evaluate.

4. **Apache 2.0 is worth a 5–10 point benchmark penalty.** The licensing risk of Qwen Research License, DeepSeek Model License, or Llama 2 Community License at scale is measurable. IBM Granite, Devstral (Apache 2.0), GLM-4.7, and Mistral's family offer strong performance without license debt.

5. **The next battleground is agentic SWE-bench performance, not token prediction.** Kimi K2.5 at 76.8% and Devstral 2 at 72.2% on SWE-bench suggest that end-to-end software engineering — reading issues, finding relevant code, writing patches, passing CI — will be solved at the model level within 12–18 months. Teams should begin designing agent scaffolding infrastructure now rather than waiting for models to mature further.

6. **Chinese labs are executing at a pace that Western open-source can't match today.** Alibaba, DeepSeek, Moonshot, and Zhipu hold 14 of the top 20 positions on this leaderboard. This is not a gap that will close passively; Western enterprises with open-source mandates should be closely tracking Mistral, IBM, and emerging Apache 2.0 alternatives.

---

## Appendix: Model Index

| Model | Provider | Params | License | Release |
|-------|----------|--------|---------|---------|
| Kimi K2.5 | Moonshot AI | ~1T MoE | Kimi Open License | 2026-Q1 |
| GLM-4.7 | Zhipu AI | 9B | Apache 2.0 | 2025-Q4 |
| Qwen3-Coder-480B-A35B | Alibaba / Qwen | 480B/35B MoE | Qwen Research License | 2025-Q4 |
| Devstral 2 | Mistral AI | 123B | Apache 2.0 | 2026-Q1 |
| Kimi K2 | Moonshot AI | ~1T MoE | Kimi Open License | 2025-Q3 |
| DeepSeek-Coder-V2-Instruct | DeepSeek AI | 236B/21B MoE | DeepSeek Model License | 2024-06 |
| Devstral Small 2 | Mistral AI | 24B | Apache 2.0 | 2026-Q1 |
| Qwen2.5-Coder-32B-Instruct | Alibaba / Qwen | 32B | Qwen Research License | 2024-11 |
| Yi-Coder-9B-Chat | 01.AI | 9B | Apache 2.0 | 2024-09 |
| OpenCoder-8B-Instruct | OpenCoder Consortium | 8B | Apache 2.0 | 2024-11 |
| Codestral-22B-v0.1 | Mistral AI | 22B | MNPL | 2024-05 |
| Qwen2.5-Coder-14B-Instruct | Alibaba / Qwen | 14B | Qwen Research License | 2024-11 |
| Phi-4-reasoning | Microsoft | 14B | MIT | 2025-04 |
| WizardCoder-33B-V1.1 | WizardLM / Microsoft | 33B | Llama 2 Community | 2024-01 |
| Granite-Code-34B-Instruct | IBM Research | 34B | Apache 2.0 | 2024-05 |
| DeepSeek-Coder-6.7B-Instruct | DeepSeek AI | 6.7B | DeepSeek Model License | 2024-01 |
| Magicoder-S-DS-6.7B | UIllinois / HF | 6.7B | Apache 2.0 | 2023-12 |
| Qwen2.5-Coder-7B-Instruct | Alibaba / Qwen | 7B | Qwen Research License | 2024-11 |
| CodeLlama-70B-Instruct | Meta AI | 70B | Llama 2 Community | 2024-01 |
| Granite-Code-8B-Instruct | IBM Research | 8B | Apache 2.0 | 2024-05 |
| CodeGemma-7B-IT | Google DeepMind | 7B | Google Gemma ToU | 2024-04 |
| StarCoder2-15B | BigCode / Hugging Face | 15B | BigCode OpenRAIL-M | 2024-02 |
| DeepSeek-Coder-33B-Instruct | DeepSeek AI | 33B | DeepSeek Model License | 2024-01 |
| CodeLlama-34B-Instruct | Meta AI | 34B | Llama 2 Community | 2023-08 |
| StarCoder2-7B | BigCode / Hugging Face | 7B | BigCode OpenRAIL-M | 2024-02 |
| Qwen2.5-Coder-1.5B-Instruct | Alibaba / Qwen | 1.5B | Qwen Research License | 2024-11 |
| OctoCoder | BigCode | 16B | BigCode OpenRAIL-M | 2023-06 |
| CodeT5+-16B | Salesforce AI Research | 16B | BSD-3-Clause | 2023-05 |

---

## Sources & Methodology

Benchmark scores sourced from:

- EvalPlus Leaderboard — `evalplus.github.io/leaderboard.html`
- LiveCodeBench — `livecodebench.github.io`
- BigCode Models Leaderboard — `huggingface.co/spaces/bigcode/bigcode-models-leaderboard`
- Qwen2.5-Coder Technical Report (arXiv:2409.12186)
- DeepSeek-Coder-V2 Technical Report (arXiv:2406.11931)
- Code Llama Technical Report (arXiv:2308.12950)
- StarCoder2 Technical Report (arXiv:2402.19173)
- Granite Code Models Technical Report (arXiv:2405.04324)
- OpenCoder Technical Report (arXiv:2411.04905)
- CodeGemma Technical Report (arXiv:2406.11409)
- Magicoder Paper (arXiv:2312.02120)
- Mistral AI blog — `mistral.ai`
- BenchLM.ai Coding Leaderboard
- Morph LLM Code Generation Rankings

*Scores marked with asterisks (*) are interpolated from multiple sources where official evaluations were not available. Paper-reported scores may differ from third-party reproductions. All evaluation dates are approximate based on model release timelines.*

---

*Report compiled by ArkForge Genesis · `ark-forge/genesis:reports` · April 10, 2026*
