# 来源、许可证、脱敏与相似度自查

## 来源

- 仓库：django-oscar，https://github.com/django-oscar/django-oscar
- 快照提交：4dc248a6382cbc26d95644925467e143fa6debcf，2025-02-19
- 取得方式：对该提交执行 `git archive`，文件未做任何改写。
- 有效代码文件数：Python 文件 808 个；去掉迁移文件和空文件后 551 个，其中 `src/oscar` 下 314 个。

## 许可证

BSD 3-Clause，版权方 Tangent Communications PLC 及贡献者，许可证全文在快照的 `LICENSE`。task.toml 的 `code_license` 为 `BSD-3-Clause`。

## 脱敏

代码是公开仓库的原样快照，不含内部代码，不需要脱敏。题包内没有真实凭证、令牌和内部主机名。
题包自带的 Dockerfile 默认使用公共的软件源和包索引，镜像地址通过构建参数传入。

## 与公开基准的相似度

- django-oscar 不在 SWE-bench 的 12 个仓库之内。
- 题面、草稿、隐藏单测、参考修复都是为本题新写的。隐藏单测没有复制上游的测试，并且要求了上游至今没有处理的环节，例如分批结算和价格变动提示。
- 参考修复不是上游补丁的复制：上游修复后的最新版在反例程序的七项观测里七项都有缺陷，见 `solution/counterexamples/ce2_upstream_4.2.2_local.log`。
- SWE-Gym Raw 收录了 django-oscar/django-oscar 的 104 条记录（数据集说明页的仓库频次表）。这个数据集的记录大多没有可执行环境，也没有经过 SWE-bench 式的验证。SWE-Gym 的论文发表于 2024 年 12 月，本题依据的两次上游修复在 2025 年 3 月和 4 月，按时间不会在其中；这是推断，没有逐条核对。
- Hugging Face 上有一个个人上传的数据集 apotterri/django-oscar，23 条，SWE-bench 的字段格式，PR 编号从 3019 到 4017，不含 #4448 和 #4455，可见内容里没有税额舍入相关的题。
- 没有查成的：SWE-rebench、SWE-bench-extra、SWE-smith。2026-11-19 查询时 Hugging Face 的数据集检索接口返回错误，网页检索也没有找到这三个数据集的仓库清单。SWE-rebench 持续收录新 PR，有可能包含 2025 年的提交，交付前需要补查这三个。
- 即使某个数据集收录了 #4448 或 #4455，它们的题目是让模型复现上游补丁。本题的隐藏单测要求的是上游没有处理的环节，只做上游补丁在本题得 0 分。

## 重复与泄漏

- 模型可见的只有 `instruction.md` 和 `environment/workspace/repo/`。
- 镜像内不含 `solution/` 与 `tests/`，检查输出见 `tests/assets/selfcheck.md` 第 11 项。
- 快照早于上游的两次修复，仓库内没有修复后的代码。
