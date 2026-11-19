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

核对日期为 2026-11-18。题源是公开快照以及上游两个舍入修复。复核使用仓库名 `django-oscar/django-oscar` 和 PR 编号 4448、4455 作为复合键。数据集如使用镜像名或合成实例 ID，同时检索 `repo` 和 `instance_id` 的 Oscar 写法。仅凭“Django”“税”或相同数字不能认定是同一道题。[上游 PR #4448](https://github.com/django-oscar/django-oscar/pull/4448) · [上游 PR #4455](https://github.com/django-oscar/django-oscar/pull/4455)

| 数据集固定快照 | 实际检查范围 | 目标仓库及 PR |
|---|---|---|
| [SWE-bench](https://huggingface.co/datasets/princeton-nlp/SWE-bench/tree/e48e2bd1e9fecd5bbd641e9414ac59da9f2e69f6/data) | train 19,008、dev 225、test 2,294 行 | 三个 split 均无该仓库 |
| [SWE-bench Verified](https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified/tree/c104f840cc67f8b6eec6f759ebc8b2693d585d4a/data) · [Lite](https://huggingface.co/datasets/princeton-nlp/SWE-bench_Lite/tree/6ec7bb89b9342f664a54a6e0a6ea6501d3437cc2/data) | 两个评测集的 test，各 500、300 行 | 均无该仓库 |
| [Nebius SWE-bench-extra](https://huggingface.co/datasets/nebius/SWE-bench-extra/tree/11dcbfb30e19552df2a2f8030bd764adc95c92a5/data) | 单个 train 分片，6,376 行、1,974 个仓库 | 无该仓库 |
| [Nebius SWE-rebench](https://huggingface.co/datasets/nebius/SWE-rebench/tree/89cdfbab4ab1bd8f5a658bb212d1b63624f4f881/data) | test 21,336 行，filtered 6,542 行，两者分别检查 | 均无该仓库 |
| [Nebius SWE-rebench-leaderboard](https://huggingface.co/datasets/nebius/SWE-rebench-leaderboard/tree/34d5a58864acf91613740a09ec5d205228dcfa39/data) | test 和 2025_01 至 2026_03 月度分片共 1,720 行，去重后 860 个实例 | 无该仓库 |
| [Nebius SWE-rebench-V2](https://huggingface.co/datasets/nebius/SWE-rebench-V2/tree/d7608f017a29ab256400ad4b73d5248d97204966/data) | train 32,079 行 | 无该仓库 |
| [Nebius SWE-rebench-V2-PRs](https://huggingface.co/datasets/nebius/SWE-rebench-V2-PRs/tree/fbf0ecf50f268d5344149e2f0097db6bede83737/data) | train 三个分片共 126,300 行 | 无该仓库 |
| [SWE-smith](https://huggingface.co/datasets/SWE-bench/SWE-smith/tree/ea6d7173829c7ec8fa16c22055699ff2e9188091/data) · [SWE-smith-py](https://huggingface.co/datasets/SWE-bench/SWE-smith-py/tree/77cab9055d42ab4a5c25c89a8f937096db13558e/data) | train 分别 59,136、50,908 行，对应 222、131 个镜像仓库名 | 均无含 Oscar 的仓库名 |
| [SWE-Gym](https://huggingface.co/datasets/SWE-Gym/SWE-Gym/tree/bb94ed9e39bbeb96a7fcbfb533b80f25a7fd59cb/data) | train 2,438 行 | 无该仓库 |
| [SWE-Gym Raw](https://huggingface.co/datasets/SWE-Gym/SWE-Gym-Raw/tree/47e98187b31fd5a83deb62d5c48b94619648f2db/data) | train 六个分片共 64,689 行 | **同仓库 104 行**，PR 范围 #341–#4105，两个目标 PR 均为 0 行 |
| [apotterri/django-oscar](https://huggingface.co/datasets/apotterri/django-oscar/tree/4a08c39dcb9410785c5ffb4930f9f8184de9a7fa/data) | 检查 train 全部 23 行 | **同仓库 23 行**，PR 范围 #3019–#4017，两个目标 PR 均为 0 行 |

**复核方法。** 可对表内各版本的 Parquet 分片投影仓库列，按仓库统计行数。有单独 `pull_number` 字段的同仓库记录，再逐条核对两个 PR 编号。SWE-bench 和 SWE-smith 的仓库分布使用 Dataset Viewer 的 `/statistics` 接口，并验证响应头 `X-Revision` 一致、`partial=false`、仓库频数之和等于整个 split 行数。这里的行数用于标明各自检查范围，相关数据集之间可能重复。

**相似内容与范围。** 同仓库的公开题目覆盖过价格和促销业务。在 SWE-Gym Raw 的 104 条同仓库问题描述中，大小写无关检索 `rounding`、`quantiz`、`precision` 均为 0，但其中 #2404 已涉及购物车行零税额，#3019 涉及库存价格字段的含义。个人数据集也收录了 #3019 和有关购物车冻结的 #3393。本题要求修改固定税率舍入，并使显示、搜索、订单行与分批结算使用一致金额。使用上游 4.2.2 对此题反例做的七项观测均有差异，其中包含分批结算和不变价告警。以上核查确认了所列表内仓库和 PR 身份的重合情况，不能排除其他数据集、不同项目的语义近似题或模型训练时读过公开修复。[#2404](https://github.com/django-oscar/django-oscar/pull/2404) · [#3019](https://github.com/django-oscar/django-oscar/pull/3019) · [#3393](https://github.com/django-oscar/django-oscar/pull/3393) · [上游版本的反例运行记录](../CS-XX-001/solution/counterexamples/ce2_upstream_4.2.2_local.log)

## 盲测可见范围

本仓库公开提供作者材料，其中包含参考补丁、样例答卷、判分程序和包外说明。正式运行需要导出 `instruction.md` 和 `environment/workspace/repo/` 作为作答输入，阻断模型对公开答案仓库及作者文件的访问。模型完成作答并退出后，在独立环境中挂载验证器。初始镜像隔离证据及当前复验见[自检记录](../CS-XX-001/tests/assets/selfcheck.md)。

上游快照早于两次修复提交。公开的上游修复、题包和历史答案可能进入模型知识，因此对未来模型的训练集重合情况仍有不确定性。
