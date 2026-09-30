# Experiment Tracker

| # | 实验 | 状态 | 产物 | 结论 | 日期 |
|---|------|------|------|------|------|
| P0 | GT 带宽 pilot | ✅ 完成 | `idea-stage/pilot_results.json` | MIXED 偏 POSITIVE（3.1×，参考依赖子发现） | 2026-09-29 |
| E1 | 迁移损失矩阵 × 多距离重分析 | ✅ 完成 | `results/e1_stdout.txt` | **MONOTONE_OR_ARTIFACT**（三距离一致，置换 p=0.14/0.92/0.33）：无 changepoint 边界；单距离不完备 | 2026-09-30 |
| E2 | fine-tune sweep × 无参考端点 | ✅ 完成 | `results/e2_stdout.txt` | **CAUSAL_EFFECT**：matched/control 带外能量比 0.52/0.49/0.50 随长度稳定；排除训练非平稳性解释；Wiener 基线锚定 DL 超额带外 ~4.5× | 2026-09-30 |
| E3 | ME 角控制 | ⚠️ 完成-设计受限 | `results/e3_stdout.txt` | **INCONCLUSIVE_LOW_POWER**：t* 全部=训练 extent（0.6），grain 无效应；卷积仿真 ME 严格无限→物理边界不可测，需空间变化 PSF 或真实散射数据 | 2026-09-30 |
| S1-S5 | 第二波 scale-up | ⬜ 待设计修订 | — | C 组件需重设计；A/B 按 E1/E2 证据推进 | — |

**偏离记录**：
1. E2 原计划"复用 pilot checkpoints"——pilot 未存 checkpoint，实际重训 raw 基线（seed/协议一致）。
2. E3 判定规则不变（t* 随 grain 移动=物理），但卷积仿真下 ME 无限，物理杠杆失效——设计局限如实记录，组件 C 降级。

**对 program 的影响（按 FINAL_PROPOSAL 预声明判定）**：
- 组件 B（GT 带宽因果消融）：MIXED → **因果确认**，升为主导贡献候选；评审 CAUTION 条件全部满足（sweep 完成、无参考主端点、计算量匹配对照、Wiener 基线）。
- 组件 A（统计距离律）：拿到"统计虚构"分支的干净负结果数据 + 单距离不完备新线索 → 主张改为"损失由多因子距离连续预测，类别标签是任意切分"。
- 组件 C（ME 拐点）：当前设计不可判 → 需空间变化 PSF 仿真或实验数据，降级为第二篇/扩展，不拖累 A+B 主线。

| RR | E1-E3 结果复审（DeepSeek） | ✅ 完成 | `.aris/traces/idea-discovery/2026-09-30_re-review_after_E1-E3.md` | 重塑批准：B 唯一 lead、A 支撑、C 延后；scale-up 最低 60-135 GPU·h；标题暂禁 "speckle" | 2026-09-30 |

| RD | 真实散射数据 check（DSC Zenodo 15361263） | ✅ 部分达成 | `artifacts/dsc_data/`（240 张抽样） | 配对信号存在（same 0.10-0.18 > mismatch 0.05-0.11）；但最小协议下前向模型配不准（对象尺度/放大率失配，OTF 估计失效）→ 记为协议 limitation，前向模型配准是 scale-up 的真实数据模块前置工作 | 2026-09-30 |
| E4 | 空间变化 PSF check（复审二选一的另一臂） | ✅ 完成 | `results/e4_stdout.txt` | **EFFECT_SURVIVES_SPATIAL_VARIATION**：matched/control 带外比 0.52/0.60/0.54——协议不依赖平移不变理想化；同时回应 E3 的 ME 局限（位置依赖=有限 ME 代理） | 2026-09-30 |

| SU | Colab T4 scale-up（复审最低配置） | ✅ 完成 | `results/scaleup_results.json` + `results/scaleup_units/`（6 单元） | **B 组件主导效应全配置复现**：配对统计 finetune-vs-control 带外能量比 matched **0.34±0.11**、half **0.20±0.08**，**6/6 单元全部降低**（2 架构×3 seeds）。新发现：容量越大发明越多（base32 raw oob 0.026 > base16 0.015；效应也更强 0.23 vs 0.44）。Baseline 单调：raw 0.021 > matched 0.0066 > half 0.0036。Colab 会话已关停（spk3 not found，用量 ~45min ≈ 0.8 CU） | 2026-09-30 |

| FR | Scale-up 后最终就绪评估（DeepSeek R4） | ✅ 完成 | `.aris/traces/idea-discovery/2026-09-30_final-readiness_after-scaleup.md` | **TCI 7/10 可直投，0 阻塞项**；PR 需 2-3 天配准补救；论点/图清单/标题/hedge 全部就位 | 2026-09-30 |

| RG | 配准补救实验（三方法迭代） | ❌ **证伪** | `results/registration_fix{,2,3}.txt` | 三种方法全败：①互谱 OTF（模型错误：散斑不满足线性卷积）；②径向过零法（L_spk 恒定 191±1.3px = 系统 ME/视场支持，与对象无关，径向平均丢对象结构）；③2D autocorr NCC（alpha 混沌：0.4~2.5 撞界，CV=1.02，判据需 <0.15）。**根因：DSC 数据集本质是"端到端 DL 学不可解析映射"设计（原论文贡献即在此），最小协议的尺度配准不是工程问题而是前向建模问题**。修正："2-3 天配准→PR"假设证伪 | 2026-09-30 |
| RG+ | 配准实验的可用正面素材 | ✅ 提取 | 同上 | ①系统实测带宽：grain FWHM 1.93px → 信息支持 ~133px 半径（52% Nyquist）；②ME/视场相关长度 ~191px；③配对统计（20 对：0.10-0.18 vs 0.05-0.11）——真实数据段落从 "pairing signal" 升级为"系统参数实测 + 配对统计 + 协议落地前置条件清单" | 2026-09-30 |
