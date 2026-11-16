# 可比性归因与认可证书（运行说明）

本目录补充的是「同一基准、不同语言包 / 指标尺度」复测时的**可比性归因**，
以及**证书可追溯、不静默漂移**的约束。原有验收流程不变：

```
python3 -m benchmark_federation run --fixture fixtures/acceptance.json \
    --database /tmp/benchmark_federation.sqlite3 \
    --output /tmp/benchmark_federation-output
python3 -m benchmark_federation verify --database /tmp/benchmark_federation.sqlite3 \
    --output /tmp/benchmark_federation-output
```

带可比性评审的样例：

```
python3 -m benchmark_federation run --fixture fixtures/comparability.json \
    --database /tmp/comparability.sqlite3 --output /tmp/comparability-output
python3 -m benchmark_federation verify --database /tmp/comparability.sqlite3 \
    --output /tmp/comparability-output
```

评审定义也可以单独放在 JSON 文件里，通过 `--review path.json` 传入；
fixture 内嵌 `comparability` 字段时会被自动读取。

## 1. 评审面（review surface）

`fixtures/comparability.json` 的 `comparability` 块固定了四件事：

| 组成 | 作用 |
| --- | --- |
| `baseline` | 基准家族、版本，以及**基准声明的指标目录**（阈值、方向、权重、目标尺度、值域）。这是分母的唯一定义来源。 |
| `mappings` | 语言包 → 别名表 + 允许的尺度换算 + 语义映射置信度下限。每个语言包只认自己那条映射。 |
| `policy` | 通过阈值、最低可比比例、硬下限、豁免占比上限等认可规则。 |
| `observations` | 每个参赛者的**原始复测证据**：原始值、源尺度、证据引用与摘要、可选的豁免。 |

## 2. 指标缺失、豁免、尺度映射如何改变分母

每个基准指标都会得到一条归因（`comparability.json` 的 `metrics`），
状态只有四种：

* `comparable`：有对应原始证据、证据摘要、基准版本一致、映射置信度达线、
  尺度换算在映射允许范围内且结果落在值域内。**只有这一种进入分母。**
* `missing`：基准声明了该指标，但没有复测观测值或没有证据引用。
* `waived`：有在评审时刻仍有效、范围匹配、审批人明确的豁免。
* `incomparable`：指标存在但不可比，例如基准版本不一致、语义映射低于下限、
  尺度换算未被该映射版本批准、源指标名无法映射、归一化后越界、豁免已过期/越权。

关键规则：

1. **分母 = 可比指标权重之和**（`denominator.comparable_weight`）。
   `missing`、`waived`、`incomparable` 既不当作失败，也不填 0；
   它们只出现在 `missing/waived/incomparable` 列表和 `excluded_share` 里。
   `overall_pass_rate` 是「通过的可比权重 / 可比权重」，不是「通过数 / 基准指标数」。
2. **尺度映射只改变数值，不改变分母**。例如 83（percent）→ 0.83（fraction），
   0.11（seconds）→ 110 ms，`scale_factor` 会一并留痕。没有被当前映射版本批准的
   换算一律记为 `incomparable`，而不是就近猜测。
3. **可比比例决定结论是否可下**。可比比例低于 `hard_comparability_floor` /
   `minimum_comparability` 时结论是 `insufficient_evidence`：证据太薄，
   既不能判通过、也不能把被排除指标当作失败。
4. **可比失败仍然失败**。当可比比例达标且可比指标未达阈值，结论是
   `not_recognized`，原因写 `observed_pass_rate_below_threshold`，
   并注明哪些指标被排除、未计入。
5. **豁免不是免费通行证**。豁免必须带 `waiver_id`、`reason`、`approved_by`、
   覆盖该指标的 `scope`，以及带时区的 `expires_at`；评审使用 `reviewed_at`
   判断是否过期。过期、越权、必选指标不允许豁免时一律 `incomparable`。
   豁免占比超过 `max_waiver_share` 时结论降为 `insufficient_evidence`，
   不判失败。
6. **未声明的观测值**（基准目录里没有的指标）只记录在
   `denominator.undeclared_observations`，绝不进入分母。
7. **敏感性只是说明**。被排除指标带有 `sensitivity.if_counted_as_pass` /
   `if_counted_as_failure`，用于说明「如果强行计入会怎样」，
   但报告的分母与结论不会因此改变。

`summarize()` 的汇总也只纳入可比比例达标、分母可用的记录；
`records_excluded_from_aggregate` / `excluded_records` 明确列出未纳入者。
`mean_recorded_pass_rate`（参赛者自报的 `retest_pass_rate`）与
`mean_effective_pass_rate`（按可比分母重算）并列展示，两者差异就是这次
评审要解释的可比性归因。

## 3. 认可结论与既有决策的关系

可比性归因从不改写规则评分；它只对**正向结论**设下限：

* `recognized` → 维持 `approve`
* `conditional` → `approve` 降为 `review`
* `not_recognized` → `approve` 降为 `reject`
* `insufficient_evidence` → `approve` 降为 `review`

原本就是 `review` / `reject` / `hold` 的决策不受影响——不可比指标不能
制造失败，也不能把已有失败洗成通过。

## 4. 证书可追溯与不漂移

每次评审都会生成 `certificates.json`，并为每个参赛者写一张不可变证书：

* `certificate_id` 是证书正文（baseline、mapping、policy、分母、逐指标归因、
  结论、证据摘要）的哈希，**不含时间戳**，因此同一评审面重复执行得到同一张证书。
* `body.mapping` 记录当时实际使用的 `mapping_id` / `mapping_version` /
  `mapping_digest` / 语言包；语言包没有钉住映射时，
  `mapping_id` 为空且 `resolved=false`，原因写入 `unresolved_reason`，
  **不会偷偷套用默认映射**。
* 证书发布时，数据库同时归档 `baseline_snapshots`、`mapping_snapshots`、
  `review_snapshots`、`evidence_ledger`。后续重测或映射升级只追加新快照，
  旧快照按内容寻址保存，证书始终能回到当时的映射和原始证据。
* `review-archive.json` 与证书一起导出，离线也能核对 baseline / mapping / 证据。
* 后续评审若 baseline、mapping、policy 或证据任何一项发生变化，可以产生新证书；
  旧证书被标记为 `superseded`（保留正文、`superseded_by`、变更原因事件），
  **不会被覆盖或删除**。
* 若四者都没变却想改结论，`publish_certificate` 会直接拒绝（silent drift），
  必须走新的评审面。
* `verify` 现在额外检查：证书正文哈希、基线/映射引用、结论一致性、
  快照与证据是否齐全、每个记录至多一张 `verified` 证书，以及导出包中
  证书与归因面是否互相一致。

## 5. 模块边界

| 文件 | 职责 |
| --- | --- |
| `benchmark_federation/comparability/model.py` | Baseline / MappingProfile / ReviewPolicy / Waiver / MetricObservation / ReviewDefinition |
| `benchmark_federation/comparability/engine.py` | 逐指标归因、分母计算、结论、汇总 |
| `benchmark_federation/certificates/certificate.py` | 证书正文与编号、静默漂移检查 |
| `benchmark_federation/recognition/certificate_ledger.py` | 证书表、评审面快照、证据台账、证书校验 |
| `benchmark_federation/certificates/recognition_pack.py` | 导出包、证书交叉核对、分母完整性校验 |

原有 `benchmarks/contract.py`、`retest/execution.py`、`translation/*`、
`reuse/cost_model.py` 的评分与规则行为未改动。
