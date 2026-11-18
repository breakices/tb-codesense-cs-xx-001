# 陷阱反例

两个程序都是确定性的，不依赖时间、随机数和网络。下面的日志是在任务镜像里运行得到的。

## ce1_default_rounding.py

只需要 Python 和 Django。它展示语言和框架的默认行为：`Decimal.quantize` 不传 `rounding` 时是银行家舍入；Django 把位数过多的值写进 `DecimalField` 时也这样量化。
五个取值都在五的进位点上，默认结果与四舍五入全部不同。

运行：`python ce1_default_rounding.py`

```
python 3.12.14 | Linux-5.15.152-amd64-x86_64-with-glibc2.36
default context rounding: ROUND_HALF_EVEN
unit tax 0.03 x 17.5%              exact 0.00525  quantize() 0.0052  ROUND_HALF_UP 0.0053  DIFFERENT
shipping net 5.00 x 3.75 / 6.00    exact 3.125    quantize() 3.12    ROUND_HALF_UP 3.13    DIFFERENT
shipping discount 2.50 x 25%       exact 0.625    quantize() 0.62    ROUND_HALF_UP 0.63    DIFFERENT
line net 20.00 - 11.25 / 1.2       exact 10.625   quantize() 10.62   ROUND_HALF_UP 10.63   DIFFERENT
gross 0.60 x 1.175                 exact 0.705    quantize() 0.70    ROUND_HALF_UP 0.71    DIFFERENT
django 5.1.15 format_number(0.7050, max_digits=12, decimal_places=2) -> 0.70
cases where the default differs from half up: 6
exit status: 0
```

## ce2_draft_consequences.py

对一个仓库做七项观测，统计其中出现缺陷的项数。有缺陷时退出码为 0。第七项是搜索索引里的商品价格与商品页显示的价格是否相同。

运行：`python ce2_draft_consequences.py --repo <仓库目录>`

在只做草稿两处改动的仓库上，即快照加 `tests/calibration/guessed.patch`：

```
python 3.12.14 | django 5.1.15 | Linux-5.15.152-amd64-x86_64-with-glibc2.36
repository: /workspace/repo
[DEFECT] warning on an unchanged price: "The price of 'Item 1' has decreased from £1.19 to £1.19 since you added it to your basket"
[DEFECT] order line / settled in two batches: 1.20 / 0.30 + 0.70 = 1.00
[DEFECT] lines shown / total shown: 0.04 + 0.04 / 0.07
[DEFECT] order lines / order total: 0.04 + 0.04 / 0.07
[DEFECT] unit tax of 0.03 at 17.5%: 0.0052
[DEFECT] 0.7050 in the basket / on the order / on the page: 0.71 / 0.70 / 0.70
[DEFECT] price of a 0.99 product in the search index / on its page: 1.1880 / 1.19
defects observed: 7 of 7
exit status: 0
```

在参考修复上：

```
python 3.12.14 | django 5.1.15 | Linux-5.15.152-amd64-x86_64-with-glibc2.36
repository: /workspace/repo
[ok] warning on an unchanged price: None
[ok] order line / settled in two batches: 1.20 / 0.50 + 0.70 = 1.20
[ok] lines shown / total shown: 0.04 + 0.04 / 0.08
[ok] order lines / order total: 0.04 + 0.04 / 0.08
[ok] unit tax of 0.03 at 17.5%: 0.0053
[ok] 0.7050 in the basket / on the order / on the page: 0.71 / 0.71 / 0.71
[ok] price of a 0.99 product in the search index / on its page: 1.19 / 1.19
defects observed: 0 of 7
exit status: 1
```

在上游项目 4.2.2 上。这一份是在本地 macOS 上跑的，仅作旁证，说明这些下游问题在真实项目里至今存在：

```
python 3.12.13 | django 5.1.15 | macOS-26.6.2-arm64-arm-64bit
repository: django-oscar a5ed3c9c17d4 (4.2.2), local checkout
[DEFECT] warning on an unchanged price: "The price of 'Item 1' has decreased from £1.19 to £1.19 since you added it to your basket"
[DEFECT] order line / settled in two batches: 1.20 / 0.30 + 0.70 = 1.00
[DEFECT] lines shown / total shown: 0.04 + 0.04 / 0.07
[DEFECT] order lines / order total: 0.04 + 0.04 / 0.07
[DEFECT] unit tax of 0.03 at 17.5%: 0.0052
[DEFECT] 0.7050 in the basket / on the order / on the page: 0.71 / 0.70 / 0.70
[DEFECT] price of a 0.99 product in the search index / on its page: 1.1880 / 1.19
defects observed: 7 of 7
exit status: 0
```

## 复现率

陷阱不是概率性的。每个程序在镜像里连跑 3 次，输出逐字相同，触发率 3/3。

## 能运行但语义错的写法

`tests/calibration/guessed.patch` 是一个能运行、语法正确、题面两个症状都消失的实现，但它不满足口径。上面第二段日志就是它的运行输出，七项观测全部出现缺陷。
不满足口径的原因见 `tests/calibration/guessed_result.md`。
