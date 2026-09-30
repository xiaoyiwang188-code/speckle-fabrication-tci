# Experiment Plan — 因果链 A→B→C

**预注册原则**：主端点、模型比较标准、changepoint 检验方式在跑实验前冻结于本文件；偏离需在 EXPERIMENT_TRACKER 记录原因。

## 第一波：三个便宜判别实验（评审要求，全部 CPU 小时级，复用现有仿真套件）

### E1 — 迁移损失矩阵 × 多距离重分析（Component A）
- 复用已训 checkpoint，构建完整合成 diffuser 迁移损失矩阵
- 3 种统计距离：高度图 Wasserstein、散斑功率谱 KL/TV、强度 patch MMD
- monotone vs segmented（changepoint）拟合，BIC + CV 预测对数似然比较
- 类标签置换 × 100 估计 changepoint 假阳性率
- **判别**：定律度量稳健 vs 阈值伪影
- **预算**：小时级，无新训练

### E2 — fine-tune 长度 sweep × 无参考端点（Component B）
- 用 pilot checkpoints 计算随 fine-tune 长度变化的：null-space 能量、物理支持外谱能量、前向一致性 ‖H(x̂)−y‖/‖y‖（相对残差！）
- 带宽匹配 vs 无限带宽 GT，计算量匹配 schedule（固定 epoch 数，不用早停）
- 加 Wiener 滤波/截断伪逆基线
- **判别**：3.1× 效应是否为训练非平稳性/优化伪影
- **预算**：现有 checkpoint 前向为主，可能少量短重训

### E3 — 记忆效应角控制（Component C）
- 固定训练对象集，仅变 ME 角：0.5×、1×、2× 基线
- 同架构、同对象数、同 extent 分布重训（缩减网格）
- **判别**：changepoint 随 ME 角移动=物理必要；固定=统计
- **预算**：现有 CPU 模拟器小时级

## 第二波：scale-up（E1-E3 通过后）

1. 5 seeds × 3 diffuser classes × 2 架构容量（U-Net 小/大）
2. Held-out diffuser 族 + 第二相位屏生成器（防单模拟器过拟合）
3. 自然图像对象（Pascal 子集重采样）验证 digit 基准外推
4. 多谱段 grain（2-3px 与 20+px）复验 top 发现（评审 caveat）
5. B 的幻觉能量比在人造已知幻觉上做检测器验证

## 预注册端点与判定

- **主端点（no-reference）**：null-space 能量、物理支持外谱能量比、相对前向一致性
- **次端点**：band-limited PSNR（参考带宽为因子，不做单一参考）
- **changepoint**：后验概率 + 置换零假设 FPR 校准；segmented 须胜 monotone（BIC）
- **判定规则**：每实验的正/负/零结果各自的可发表结论已在 FINAL_PROPOSAL 表中预声明

## 资源

- 第一波：本机 CPU（已验证 ~2.5 min/3 模型量级）
- 第二波：vast.ai / Modal GPU（run-experiment），预算约 8-15 GPU·h，跑前确认费用
- 实验代码延续 `idea-stage/pilot_gt_bandwidth.py` 的仿真基建（孔径受限散斑模型 + 残差 U-Net）
