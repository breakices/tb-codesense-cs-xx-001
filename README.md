# CS-XX-001 — Tax-inclusive money precision

Version **1.1.2** is a Code Sense task built on a BSD-licensed django-oscar snapshot. It asks an engineer to reconcile prices across a basket, checkout and order settlement after changing the precision of unit tax.

This public repository is the **author package**. For a blind evaluation, supply the instructions and starter repository in a separate workspace. Keep the verifier, solutions, past answers and this public repository outside the agent’s filesystem and network reach. Mount the tests after the agent exits. [Instructions](CS-XX-001/instruction.md) · [Starter repository](CS-XX-001/environment/workspace/repo/) · [Verifier entry point](CS-XX-001/tests/test.sh)

The revised verifier checks the unit tax before further rounding, protects against overcharging within a series of payments, and covers the customer-visible price-change rule for old baskets. The UK offer base continues to follow the existing strategy.
On Linux/amd64, three independent verifier runs per control gave 41/41 for the reference, full-score, equivalent and two variant patches. The unmodified starter passed 23/41, the defective patch 31/41 and the draft-only patch 21/41. Each of those three earned reward 0. [Per-run evidence](CS-XX-001/tests/assets/selfcheck/linux-amd64-1.1.2/SUMMARY.json)

Model calibration is **incomplete**. Versions 1.1.1 and 1.1.2 have no formal rollouts. Historical runs for earlier versions, including the retrospective rescore of previously seen answers, are listed in the [baseline report](CS-XX-001-external/06_baseline.md).
