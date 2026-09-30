# Final Proposal — 散斑 DL 泛化的统计 vs 物理归因：定律、拐点与协议

**Run**: `scattering-speckle-20260929` | **Date**: 2026-09-30 | **Status**: 评审通过（conditional proceed）
**评审链**: triage（deepseek-v4-flash, 19 候选排序）→ novelty 裁决（A: PROCEED / B: PROCEED WITH CAUTION / C: PROCEED）→ external review（IEEE TCI 7/10、Photonics Research 6/10，完成 E1-E3 后升至 8/10）。Trace: `.aris/traces/idea-discovery/2026-09-30_*.md`

## Problem Anchor（冻结，防范围漂移）

**锚定问题**：深学到散斑成像领域的核心泛化主张——"同类散射体上训练、同类泛化"（自 Optica 2018 DSC 起）——从未被给出可操作统计定义；"幻觉"报告依赖隐含参考带宽选择；"记忆效应边界"语言未与训练统计解耦。本 program 在单一仿真套件内建立：距离→损失的定量定律（A）、无参考幻觉端点协议（B）、以及统计匹配后的剩余泛化边界是否物理（C）。

**一句话论点**：A 定义"匹配统计"的操作含义，B 定义可信的幻觉度量，C 用前者匹配、后者度量，检验剩余泛化拐点是否物理——三者构成一条因果链而非三个拼盘。

## 核心主张与最低置信证据（minimum convincing evidence）

| Claim | 最低证据 | 失败即发表的形态 |
|---|---|---|
| A: 距离→迁移损失存在（或不存在）紧凑标度律 | 3 种统计距离（Wasserstein/谱 KL/MMD）× monotone vs segmented 模型比较（BIC/CV-LL）× 置换零假设校准 changepoint 假阳性率；held-out diffuser 族 + 第二相位屏生成器验证 | "同类"被证明是任意标签——领域须改报告统计距离 |
| B: 训练目标带宽因果性影响测量幻觉 | fine-tune 长度 sweep（预注册）× 计算量匹配基线 × no-reference 主端点（null-space 能量、物理支持外谱能量、前向一致性）× Wiener/截断伪逆基线 | 幻觉是病态本质而非 GT 伪影——给物理机理研究一个受控消融 |
| C: 匹配统计后泛化拐点是否随 ME 角移动 | 固定对象集、仅变 ME 角（0.5×/1×/2×）重训 → changepoint 位置随动=物理，不动=统计；后验概率 >0.95 | 平滑衰减=文献中"记忆效应"语言是装饰性的 |

## 评审三大 objection 的防御（已内置）

1. **距离定律可能是度量伪影** → 距离候选族预注册、segmented 拟合必须胜过 monotone null（惩罚项比较）、changepoint 置换零假设。
2. **幻觉定义依赖不可见参考** → 主端点一律 no-reference 物理约束量；参考带宽作为因子而非默认。
3. **C 的拐点与对象复杂度混淆** → 对象集固定、仅变 ME 角；diversity 绑定到 A 的可测距离。

## Venue 主张

IEEE TCI（7/10 起，方法感知的预注册设计契合）；Photonics Research 需强化 ME 分量的物理生成性（6/10 起）。

## 与占位山头的差异化（novelty 裁决书原文要点）

- vs Zhang Nat Commun 2026（机理解释）：本 program 给**可操作定律与协议**（它解释 why，我们给 how-to-measure）。
- vs Long PR 2026（通用评估框架）：我们的距离律是**可证伪标度律**而非评估框架；B 的因果消融是它没有的。
- vs Tivnan 2024 Hallucination Index：通用 IQM vs **散斑算子信息带校准 + 因果 GT 带宽设计**。

---

## 复审修订（2026-09-30，E1-E3 结果发回 DeepSeek 复审后）

**Trace**: `.aris/traces/idea-discovery/2026-09-30_re-review_after_E1-E3.md`

1. **角色重排**：**B（GT 带宽因果消融）为唯一 lead**；A（距离连续预测）降为支撑/motivation 章节——E1 的"平滑多因子"故事来自 12 族/144 相关对的 post hoc 重定义，只可作 caution 不可作 headline law；C 维持延后。
2. **语言降级**："causally controls"改为受控设计下的因果缩减主张；"full-band references are artifacts"过强不写；4.5× Wiener 锚定**不作 headline**（headline = matched/control 因果缩减），它需过 Wiener 正则/支持敏感性 sweep + 第二线性基线后才是次级定量锚。
3. **标题约束**：完成真实散射数据或空间变化 PSF check 之前，标题不得使用 "speckle"（审稿人会指仿真无 ME 物理）；备选 "band-limited inverse problem"。
4. **可投稿最低 scale-up 配置**（评审原文）：
   - A（支撑）：≥36 diffuser 族、3 seeds、显式 held-out 族、代理迁移损失回归在 held-out 对上验证
   - B（lead）：2 架构 × 3 seeds × 3 目标带宽 × {baseline, raw-cont, matched-ft} + Wiener 超参/支持敏感性 sweep
   - 若保留 speckle 标题：至少一项真实散射数据或空间变化 PSF check
   - **估算 ≈ 60-135 A100 GPU·h**（0.5-1 GPU·h/run，~120-135 full runs；5-seed/3-arch 加强版 ≈250 GPU·h）
5. **Bottom line: proceed to scale-up of reshaped A+B exactly as conditioned。**

---

## 最终就绪评估（2026-09-30，scale-up 后 DeepSeek Round 4）

**Trace**: `.aris/traces/idea-discovery/2026-09-30_final-readiness_after-scaleup.md`

- **就绪判定**：**IEEE TCI 7/10 — 可直接投稿**（真实数据标记 preliminary）；Photonics Research 6/10 — 需先做 scale-registration 补救（~2-3 天、<10 Colab 小时），非新一轮实验。**模拟核心 0 个阻塞项**。
- **论点（评审原文）**："Matched target-bandwidth fine-tuning suppresses out-of-band spectral fabrication in learned speckle imaging without degrading relative forward-model error, while raw fabrication grows with network capacity and Wiener reconstructions cannot match DL's forward-fidelity operating point."
- **图清单（5 张）**：①现象/度量（MTF 支持外的带外能量定义）；②主对照（配对 fine-tune vs control，6/6，含无参考残差 inset）；③容量效应（base16/32）；④Wiener trade-off（oob vs 相对前向误差）；⑤鲁棒性（空间变化 PSF 存活 + DSC 配对信号 + 配准 limitation）。
- **标题候选**（"speckle" 允许用于 "learned speckle imaging"，不可用于 "experimental speckle reconstruction"）：
  1. *Matched fine-tuning controls spectral fabrication in learned speckle imaging*
  2. *Spectral fabrication in learned speckle imaging: capacity effects and a compute-matched fine-tuning remedy*
- **摘要强制 hedge（5 条）**：simulated protocols 限定；out-of-band energy 是 fabrication proxy 非语义/感知指标；真实数据 preliminary + 配准限制；结论限于已测架构/预算/带宽；matched fine-tuning 未增加无参考前向误差（+0.026）。
- **Bottom line: 先投 TCI**；要 PR 的实验散斑主张则先做 2-3 天配准补救。

### 配准补救实验结果（2026-09-30）—— 假设证伪，路线修正

三方尝试全部失败（详见 TRACKER RG 行）：互谱 OTF（线性模型对散斑无效）、径向过零（系统 ME 支持主导，径向平均丢失非各向同性对象结构）、2D autocorr NCC（尺度解混沌，CV=1.02）。

**根因（可写进论文 limitation，比原表述更精确）**：公开散斑数据集（DSC）是为"端到端 DL 学习不可解析映射"设计的（其原论文贡献即在此）；对这类数据，GT 带宽协议的定量落地需要一个**解析或学习式前向标定阶段**，而非简单尺度配准。最小协议下尺度解存在系统性混沌。

**修正后的路线**：
1. **IEEE TCI 直投（主线不变）**：真实数据段落表述为"系统参数实测（grain FWHM 1.93px / 支持 52% Nyquist / ME 191px）+ 配对信号统计 + 协议落地前置条件"，limitation 用上面的根因表述——这比"scale mismatch"诚实且更有科学增量。
2. **1区（PR）**：需要专门的真实数据工作（自采集含标定的散斑数据，或寻找前向模型干净的公开数据），规模超出 2-3 天补救；建议列为后续工作/第二篇。
