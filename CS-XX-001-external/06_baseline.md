# 模型试测记录

1.1.1 和 1.1.2 均无正式答卷。

## 历史 Opus 5.5 答卷

v5 的五份答卷由 Claude Code 2.1.318 在隔离镜像中生成，每次限时 2700 秒，权限模式为 `bypassPermissions`。最初的 38 项测试有三份全过。读取答卷后补入 U39，连同 U40 和 U41 重判原答卷，得到一份全过、四份未全过，单测合计 199/205。两份只在 U39 失败，两份在 U14、U39 失败。运行用时、轮数、失败签名和距离统计见[运行摘要](../CS-XX-001/tests/assets/baseline_runs/SUMMARY.json)、[逐项矩阵](../CS-XX-001/tests/assets/baseline_runs/matrix.csv)和[原始答卷](../CS-XX-001/tests/assets/baseline_runs/opus5.5/)。

1.1.0 在 41 项测试下另有四份独立有效答卷。`v6r-01`、`v6r-02`、`v6n-01` 全过，`v6m-01` 通过 39 项，失败项为 U14、U39。开发机另记录 `v6a-01` 配额错误和 `v6m-02` 空运行，两次均无可判分答卷。v6 原始运行记录存放于开发机。
