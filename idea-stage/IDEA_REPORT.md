# Idea Discovery Report — Imaging Through Scattering Media

**Direction**: Deep learning for imaging through scattering media (speckle-based computational imaging), differentiated from the executor's prior FPM self-calibration + INR diagnostics paper. Target: SCI journals (Photonics Research / Optics Express / IEEE TCI).
**Date**: 2026-09-29
**Run ID**: `scattering-speckle-20260929`（run state: `.aris/runs/`，root `C:\zcode\SCI\论文项目`）
**Pipeline**: research-lit ✅ → idea-creator ✅（lens fan-out ✅；Codex brainstorm 配额耗尽未跑）→ novelty-check ✅ accepted（deepseek-v4-flash）→ research-review ✅ accepted（deepseek-v4-flash）→ research-refine ✅

> **状态更新（2026-09-30）**：跨模型评审已通过 **DeepSeek-v4-flash**（用户部署的 SenseNova 中转，与 GLM executor 跨族）完成：triage ✅ → novelty 裁决 ✅（A: PROCEED / B: PROCEED WITH CAUTION / C: PROCEED）→ external review ✅（IEEE TCI 7/10、PR 6/10，E1-E3 完成后 8/10；bottom line: **proceed conditionally**）。全部 verdict/trace 存于 `.aris/traces/idea-discovery/`。Codex MCP 全程未参与（配额耗尽），评审后端切换已记录。

## Literature Landscape

（Phase 1, research-lit, composed 模式折入；来源：arxiv helper + WebSearch；验证：verify_papers.py 三层校验）

| Paper | Venue | Method | Key Result | Relevance | Status |
|-------|-------|--------|------------|-----------|--------|
| Deep Speckle Correlation (Li, Xue, Tian) arXiv:1806.04139 | Optica 2018 | one-to-all 统计 DL | 跨同类 diffuser 泛化首证 | 范式基线 | ✅ arxiv |
| Zhang et al., DOI 10.1038/s41467-026-72304-z | Nat Commun 2026 | 泛化/幻觉物理机理 | 机理级解释 | **占位：机理山头** | ✅ crossref |
| Long et al., PRJ 14(4):1280 | Photonics Research 2026 | MIMO + 通用泛化评估 | 定量评估协议 | **占位：评估山头** | ⚠️ verify_pending |
| Liu et al., Learning-based real-time dynamic scattering | Light Sci Appl 2024 | 动态实时成像 | 实时 SOTA | 拥挤区 | ⚠️ verify_pending |
| Zhang et al., DOI 10.1126/sciadv.adn2205 | Sci Adv 2024 | memory-less 超快 CNN | 无记忆假设部署 | 拥挤区 | ✅ crossref |
| Disorder-invariant INR arXiv:2304.00837 | 2023 | 介质无序不变 INR | 表示不变性 | INR 已入场 | ✅ arxiv |
| Implicit Neural Speckle Denoising arXiv:2608.06574 | 2026-08 | INR 散斑去噪 | 表示参数化 | INR 已入场 | ✅ arxiv |
| Support-free speckle-correlation w/ INR | recent | INR 重建 | — | 需查新 | ⚠️ verify_pending |
| Universal sensitivity of SIC arXiv:1610.01671 | 2016 经典 | speckle 相关理论 | 波前变化敏感性 | 理论锚点 | ✅ arxiv |

**版图结论**：大方向活跃；"通用泛化+定量评估"（PR 2026）与"幻觉物理机理"（Nat Commun 2026）两个山头已被占；INR-as-such 不新；动态/实时高度内卷。差异化空间在**操作化工具**（推理时的可靠性判定、协议、判别实验），而非又一个评估框架或又一种表示。

## Ranked Ideas

（20 候选 → 19 去重合并；初版为 executor PROVISIONAL 排序，已被 deepseek-v4-flash 的 triage/novelty/review 三连评审取代，见下方 Novelty Verification 与 External Critical Review 章节）

### 🥇 Idea 1: DL 散斑重建的有效分辨率上限审计（two-point-resolution-ceiling）
- **Method（实际做什么）**：仿真平移不变散斑态 → 生成 5k 两点目标（间距 0.5–3×speckle 半径）→ 训练两种容量 U-Net（2-scale vs 6-scale）→ 用 20%-dip 判据测重建的分辨极限 → 对照 Tikhonov 线性逆与 speckle Rayleigh 极限；辅以 executor 擅长的输入-输出 Jacobian 诊断。
- **Hypothesis**：重建分辨率在 speckle 相关长度处饱和，与网络容量无关；高容量下的"亚散斑超分辨"是未通过两点判据的纹理幻觉。
- **Contribution**: diagnostic / **Risk**: LOW / **Effort**: weeks（pilot ≤2h）
- **Why**: 无论正负都可发表（可证伪能力上限 vs 量化超分辨及其 OOD 边界），给领域一个标准"分辨率证书"。最接近工作：DSC 2018（定性）+ MRI 的 DL-线性等价性——散斑版容量扫描未见。

### 🥈 Idea 2: GT 带宽失配是幻觉的隐性成因？（gt-bandwidth-mismatch-hallucination-ablation）— **PILOT RUNNING**
- **Method**：同一仿真管线训三个模型（GT 分别为无限带宽 / speckle-MTF 匹配带宽 / 半带宽），固定带限参考评估 → 幻觉指标（MTF 支持外高频能量 + 背景伪影）归因于 GT 预处理。
- **Hypothesis**：对带限外频率训练迫使网络发明高频结构；带宽匹配 GT 在带内保真不变的前提下大幅降低测量幻觉。
- **Contribution**: empirical / **Risk**: LOW / **Effort**: days（pilot ≤1h）
- **Pre-registered 判据**：matched/raw 幻觉能量比 <0.5 且带内 PSNR 损失 <0.5 dB → POSITIVE；>0.8 → NEGATIVE。
- **Pilot**: `idea-stage/pilot_gt_bandwidth.py`（CPU, 运行中）→ `pilot_results.json`

### 🥉 Idea 3: 前向一致性残差作为无标签幻觉标记（inverse-consistency-hallucination-decoupling）— **PILOT B RUNNING**
- **Method**：已知 H 时计算 ||H(x̂)−y||，在对象特征尺度跨越 speckle 尺度的分级测试集上画 SSIM-vs-残差解耦图。
- **Hypothesis**：信息带外 SSIM 与残差解耦（指标高估忠实度）；带内保持耦合 → 解耦点即幻觉起点，残差是可部署的无 GT 幻觉标记。
- **Contribution**: diagnostic / **Risk**: ~~LOW~~ **MEDIUM（查新降级）** / **Effort**: days
- **⚠️ 查新发现**：Tivnan et al. 2024 "Hallucination Index"（PMC11956116，52 引用）已是 no-reference 幻觉质量指标且讨论 forward process；Nature Biomed Eng 2025 有无 GT 幻觉评估框架。本 idea 的剩余差异化 = **散斑算子信息带校准 + SSIM-残差解耦相图**（比通用 IQM 更物理、可出 regime 图），但新颖性显著收窄，cross-model triage 时需重点裁决。

### Idea 4: "同类 diffuser"的统计定义与距离-损失标度律（diffuser-class-statistical-distance-law，由 2 候选合并）
- 因子正交归因（相关长度×高度分布×谱形）+ 统计距离→迁移损失的 changepoint-vs-monotone 判别。若 class 是"统计虚构"，领域必须报告距离而非标签；若真有边界，首个定量准入判据。Risk MED, weeks。

### Idea 5: 保形预测集大小作为散斑幻觉探针（conformal-sets-localize-speckle-hallucination）
- split-conformal 校准后集大小图与幻觉像素共定位 → 分布无关保证的失败分诊；若失败即形式化证据"后验 UQ 对散斑幻觉结构性盲"。Risk LOW, days。跨领域迁移新颖性高，需查新。

### Idea 6: ME-利用指数（memory-effect-vs-texture-attribution）
- 因子析因协议（联合平移/换 diffuser/统计微扰×对象保持）分解网络保真度的 ME-物理 vs 纹理先验 vs 内容先验贡献 → 可操作的"ME-利用指数"。Risk LOW, days。

### Idea 7-19（BACKUP，均通过客观预算门，详见 codex_triage 待补评）
7. conv-prior-breakdown-phase-diagram（FOV/ME 宽度相图：架构限制 vs 信息限制）LOW
8. photon-per-grain-speckle-crossover（光子/颗粒度 crossover 相变）LOW
9. metric-doping-certification-audit（指标"投毒"认证表）LOW
10. tm-determinism-vs-learned-prior-crossover（TM 反演 vs 学习先验的漂移 crossover）LOW
11. memory-effect-knee-vs-training-diversity（泛化拐点：物理 vs 多样性方差分解）LOW
12. digit-benchmark-statistics-portability-audit（统计匹配的跨族基准审计）MED
13. autocorrelation-consistency-test-time-adaptation（物理锚定 TTA）MED
14. dps-psf-decomposition-of-speckle-networks（先验 vs 前向知识分解）MED
15. shift-equivariance-symmetry-leakage-speckle（对称性泄漏）MED（与 Nat Commun 2026 潜在重叠，查新优先级最高）
16. integration-time-m-crossover（单曝光积分统计 M~1 相变）MED
17. temporal-memory-crossover-phase-diagram（动态散斑 temporal vs memory-less 相图 + 持久性幻觉）MED, weeks
18. thin-screen-vs-volumetric-substrate-transfer（基底保真度审计）MED
19. double-layer-speckle-regime-transition（激发+发射双层散射解码器族 crossover；与 executor 自校准强项衔接）MED, weeks

## Eliminated Ideas
| Idea | Reason |
|------|--------|
| INR 用于散斑重建（as-such） | 已被 arXiv:2304.00837 / 2608.06574 / support-free INR 占位 |
| 又一个"通用泛化评估框架" | PR 2026 14(4):1280 已占 |
| 实时动态散射新架构 | LSA 2024 / Sci Adv 2024 / PR 2026 高度内卷 |

## Pilot Experiment Results

**Pilot A/B 已完成**（`idea-stage/pilot_gt_bandwidth.py`，CPU ~2.5 min；设计：raw 基线 20ep 收敛 → 同一起点 fine-tune 至 matched/half 目标带宽 3ep，保证 target 带宽是唯一变量）：

| Idea | Device | Time | Key Metric | Signal |
|------|--------|------|------------|--------|
| Idea 2（GT 带宽） | CPU | 2.5 min | 幻觉能量比 matched/raw = **0.32**（<0.5 ✓）；带内 PSNR 掉 3.2 dB（>0.5 ✗） | **MIXED（偏 POSITIVE）** |
| Idea 3（一致性残差） | CPU | 同上 | 绝对残差未按 ‖y‖ 归一化，本轮不可判 | NEEDS LARGER PILOT |

**Idea 2 详细数字**（speckle grain 6px、MTF 支持 12px、400 测试图）：
- raw-GT：带内 31.46 dB，带外能量 0.0352，背景伪影 4.64e-4
- matched-GT：28.28 dB，带外 0.0113（**↓3.1×**），伪影 2.51e-4（↓1.8×）
- half-GT：35.52 dB，带外 0.0048（↓7.4×）
- **子发现（可发表）**：PSNR 排序随参考带宽翻转——"哪个模型更好"取决于拿哪个带宽的参考做 GT。幻觉审计不能脱离 GT 预处理协议 → 支撑 Idea 2 升级为"GT 带宽协议 + 参考依赖性"双主张。
- Stage B（一致性残差）：残差随对象模糊单调上升但未归一化，full 实验改相对残差 ‖H(x̂)−y‖/‖y‖。

**Scale-up 建议（full 实验）**：5 seeds × 3 带宽 × 2 架构容量；参考带宽 × 模型全因子矩阵；相对残差版一致性解耦；加自然图像对象验证 digit 外推（衔接 Idea 12 的基准审计）。

（GPU pilot 预算 MAX_TOTAL_GPU_HOURS=8 未动用：本机无 GPU；其余 ideas 标记 "needs pilot validation"。）

## Novelty Verification

（adjudicator: deepseek-v4-flash, trace `2026-09-30_novelty-check_run02.md`；执行者多源检索先行，跨模型裁决）

- **A. diffuser-class-statistical-distance-law: PROCEED**。最近工作：Zhang Nat Commun 2026（物理机理，非定律）、Research Square rs-7097373 预印本（数据集同质性，非距离律）。差异化主张：把"同类散射体"从训练配方变成**可证伪统计定律**。存活性条件：距离→损失律须预测 held-out diffuser 族；因子归因须因果（正交合成屏）；segmented 须胜 monotone null。
- **B. gt-bandwidth-mismatch-hallucination-ablation: PROCEED WITH CAUTION**。最近工作：Tivnan 2024 Hallucination Index（通用 IQM）。差异化：**训练目标带宽的因果问题**（它给度量，我们问成因）。CAUTION 条件：fine-tune 长度 sweep 预注册、计算量匹配基线、主端点改 no-reference 物理量——已纳入 EXPERIMENT_PLAN E2。
- **C. memory-effect-knee-vs-training-diversity: PROCEED**。最近工作：Fu 2026 / Mashiko 2023（超出 ME 的**方法**论文，非判别诊断）。检索未发现 kink-vs-diversity 方差分解先例。

3×3 重叠检查（Nat Commun 2026 / dataset-homogeneity 预印本是否已含）：距离→损失律 unknown→判读为未含；受控 GT 带宽幻觉消融：否；多样性-vs-ME-kink 方差分解：unknown→判读为未含。**无一 ABANDON。**

## External Critical Review

（reviewer: deepseek-v4-flash, trace `2026-09-30_research-review_run01.md`）

- **评分**：IEEE TCI 7/10、Photonics Research 6/10；完成三个便宜判别实验（E1-E3）后两者升至 8/10。
- **最强 objection**：①距离定律可能是度量伪影（阈值自选、粗离散化可造 changepoint）→ 防御：距离候选族预注册 + 置换零假设 + 惩罚项模型比较；②幻觉定义依赖不可见参考 → 防御：主端点改 no-reference 物理量（null-space 能量/支持外谱能量/相对前向一致性），参考带宽降为因子；③C 的拐点与对象复杂度混淆 → 防御：对象集固定仅变 ME 角，diversity 绑定 A 的可测距离。
- **组合 vs 拆分裁定**：若 A 定义 C 的匹配统计、B 的端点作为 C 的主因变量，三者构成因果链，**一篇 > 三篇**；若只是共享模拟器则拒绝合并。已按因果链结构写入 FINAL_PROPOSAL。
- **Bottom line: Proceed, conditionally**（三个 CPU 小时级实验 + 预注册分析计划，风险可控）。

## Next Steps
- [ ] 等 pilot 完成 → 按 pre-registered 判据记录 verdict
- [ ] Codex 恢复后：补 brainstorm seed + triage（复评 provisional 排序）+ novelty-check + research-review
- [ ] Top idea 进入 /research-refine-pipeline → FINAL_PROPOSAL + EXPERIMENT_PLAN
- [ ] 然后进入 /experiment-bridge → /run-experiment → /auto-review-loop

<!-- ARIS_IDEA_DISCOVERY_EVIDENCE_GATE:START -->
## Evidence Gate
**Status:** PASS

All required stage records, review receipts, artifacts, and report sections are present.
<!-- ARIS_IDEA_DISCOVERY_EVIDENCE_GATE:END -->
