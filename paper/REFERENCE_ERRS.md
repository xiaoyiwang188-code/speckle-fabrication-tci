# 文献核验勘误清单（CrossRef 逐条复核，2026-09-30）

**方法**：`paper/verify_all_refs.py` 对 `references.bib` 全部 12 条做 CrossRef REST 逐条比对（作者数/前两位姓氏、年份、标题前 40 字、venue），DOI 逐条实际解析。
**结果**：10/12 clean，1 处为 HTML 实体转义造成的**假阳性**，1 条为无 DOI 的教科书（正常）。

## 逐条结论

| Key | 结论 | 说明 |
|---|---|---|
| li2018deep | ✅ OK | Optica 2018, DOI 10.1364/OPTICA.5.001181 |
| zhang2026physical | ✅ OK | Nat Commun 2026, DOI 10.1038/s41467-026-72304-z，8 位作者全对 |
| long2026universal | ✅ OK | Photonics Research 2026, DOI 10.1364/PRJ.586505，4 位作者全对，标题含 "deep learning for" |
| liu2024learning | ⚠️ 假阳性 | venue 差异仅为 CrossRef 返回 `&amp;`（HTML 实体）与 bib 的 `\&`（LaTeX 转义），**实为同一刊物**，无需修改 |
| zhang2024memoryless | ✅ OK | Sci Adv 2024, DOI 10.1126/sciadv.adn2205，标题为 "convolutional optical neural networks"（已修正过一次） |
| tivnan2024hallucination | ✅ OK | LNCS 2024, DOI 10.1007/978-3-031-72117-5_42，6 位作者全对 |
| li2025cascade | ✅ OK | Opt Commun 2025, DOI 10.1016/j.optcom.2025.131743，第一作者 Liao, Fu（已修正过一次） |
| popoff2010image | ✅ OK | Nat Commun 2010, DOI 10.1038/ncomms1078 |
| freund1988memory | ✅ OK | PRL 1988, DOI 10.1103/PhysRevLett.61.2328 |
| katz2014noninvasive | ✅ OK | Nat Photonics 2014, DOI 10.1038/nphoton.2014.189 |
| wiener1949extrapolation | ✅ 无 DOI（正常） | 1949 MIT Press 教科书，不分配 DOI |
| barbastathis2019use | ✅ OK | Optica 2019, DOI 10.1364/OPTICA.6.000921 |

## 引文语境（第二轮外部复审已确认）

- `popoff2010image` 的语境归因问题已在第一轮修正：原文"brittle to speckle decorrelation"现挂在 `li2018deep` 名下，popoff 只承担其真实贡献（确定性传输矩阵反演）。
- 12 条引用（18 处使用）全部语境适当，无 wrong-context，无 REPLACE/REMOVE。

## 结论

**references.bib 无需任何修改。** 项 1（4 条补全）与项 2（其余 8 条复核）均已完成：4 条 given names/标题/DOI/venue 全部齐全（无残留 note），8 条 DOI 全部实际解析且元数据一致。
