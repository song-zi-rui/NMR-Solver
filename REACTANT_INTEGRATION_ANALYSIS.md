# 反应物集成功能分析 / Reactant Integration Feature Analysis

## 概述 / Overview

本文档详细分析了 NMR-Solver 中实现"引入反应物来提高预测准确率"功能的代码部分。

This document provides a detailed analysis of the code sections that implement the "introducing reactants to improve prediction accuracy" feature in NMR-Solver.

---

## 核心功能描述 / Core Feature Description

**中文描述：**
通过场景适配模块将反应物结构纳入候选结构池，NMR-Solver 能够利用那些可能在反应中保留、并在 NMR 波谱中有所体现的子结构信息。这使得分子优化过程能够有效地向包含这些受波谱支持、且在化学上合理的片段的候选分子倾斜。

**English Description:**
Through the scene adaptation module, reactant structures are incorporated into the candidate structure pool. NMR-Solver can leverage substructure information that may be preserved during reactions and reflected in NMR spectra. This enables the molecular optimization process to effectively bias towards candidate molecules containing these spectrally-supported and chemically reasonable fragments.

---

## 关键代码组件 / Key Code Components

### 1. 候选分子参数 / Candidates Parameter

**文件位置 / File Location:** `src/core/solver.py`

**代码段 / Code Section (Lines 173, 200-210, 217, 237-241):**

```python
def run_solver(
    config: Dict, 
    H_split: Optional[List] = None, 
    H_shifts: Optional[np.ndarray] = None, 
    C_shifts: Optional[np.ndarray] = None, 
    allowed_elements: Optional[List[str]] = None, 
    constraints: Optional[Dict] = None, 
    candidates: Optional[List[str]] = None,  # ← 反应物/候选分子参数
    logger: Optional[logging.Logger] = Logger().get_logger(),
) -> Tuple[NMRMolPool, Dict[str, Dict]]:
```

**功能说明 / Functionality:**
- `candidates` 参数接收反应物的 SMILES 列表
- The `candidates` parameter accepts a list of reactant SMILES strings

**验证和处理 / Validation and Processing (Lines 200-210):**

```python
candidates_mol = []
if candidates is not None:
    for smi in candidates:
        try:
            mol = Chem.MolFromSmiles(smi)
        except:
            logger.warning('Invalid Candidate SMILES: %s', smi)
            continue
        if check_validity(mol):
            candidates_mol.append(mol)
candidates = [get_canonical_smiles_from_mol(mol) for mol in candidates_mol]
logger.info('candidates: %s', candidates)
```

**功能说明 / Functionality:**
- 验证候选分子的有效性
- 转换为标准化的 SMILES 格式
- Validates the validity of candidate molecules
- Converts to canonical SMILES format

### 2. 场景适配模块：候选分子池集成 / Scene Adaptation Module: Candidate Pool Integration

**文件位置 / File Location:** `src/core/solver.py`

**代码段 / Code Section (Lines 237-241):**

```python
if candidates:
    result = predict_nmr_from_mol(candidates, raw=True)
    nmr_mol_candidate = NMRMolPool(result)
    logger.info('num_candidate: %d', len(nmr_mol_candidate))
    nmr_mol_pool.add_pool(nmr_mol_candidate)
```

**功能说明 / Functionality:**
这是**场景适配模块的核心实现**：

1. **NMR 预测 / NMR Prediction:**
   - 为每个候选分子（反应物）预测其 NMR 化学位移
   - Predicts NMR chemical shifts for each candidate molecule (reactant)

2. **创建候选池 / Create Candidate Pool:**
   - 将候选分子转换为 `NMRMolPool` 对象
   - Converts candidate molecules to `NMRMolPool` object

3. **集成到主池 / Integration into Main Pool:**
   - 使用 `add_pool()` 方法将候选分子池添加到主分子池
   - 这确保了反应物结构被纳入候选结构池
   - Uses `add_pool()` method to add candidate pool to the main molecule pool
   - This ensures reactant structures are incorporated into the candidate structure pool

### 3. 分子池管理 / Molecule Pool Management

**文件位置 / File Location:** `src/core/pool.py`

**关键方法 / Key Method (Lines 122-136):**

```python
def add_pool(self, pool: "NMRMolPool") -> None:
    """
    Add molecules from another NMRMolPool to this pool.
    """
    assert self.is_scored == pool.is_scored, "Both pools must have the same scoring status."
    self.mol_list.extend(pool.mol_list)
    self.smiles_list.extend(pool.smiles_list)
    self.atoms_shift_list.extend(pool.atoms_shift_list)
    self.atoms_element_list.extend(pool.atoms_element_list)
    self.atoms_equi_class_list.extend(pool.atoms_equi_class_list)
    if self.is_scored:
        self.H_score_list.extend(pool.H_score_list)
        self.C_score_list.extend(pool.C_score_list)
        self.score_list.extend(pool.score_list)
        self.rerank_by_score()
```

**功能说明 / Functionality:**
- 合并两个分子池
- 保持所有 NMR 数据的完整性
- Merges two molecule pools
- Maintains integrity of all NMR data

### 4. 片段优化过程 / Fragment Optimization Process

**文件位置 / File Location:** `src/core/solver.py` 和 `src/core/solver_utils.py`

**交叉操作 / Crossover Operation (Lines 278-286 in solver.py):**

```python
logger.info('-'*20 + ' crossover ' + '-'*20)
nmr_mol_crossover = crossover(p, logger, config, H_split, H_shifts, C_shifts, 
                                allowed_elements, nmr_mol_pool)

logger.info('-'*20 + ' merge & filter & rerank ' + '-'*20)
if n_iter == 1 and allowed_elements:
    filtered_ids = p.map(partial(satisfy_constraints, constraints=constraints), 
                         nmr_mol_pool.mol_list)
    filtered_ids = [i for i, valid in enumerate(filtered_ids) if valid]
    nmr_mol_pool.filter_pool(filtered_ids)
nmr_mol_pool.add_pool(nmr_mol_crossover)
```

**片段切割 / Fragment Cutting (Lines 48-144 in solver_utils.py):**

```python
def cut_mols_into_frags(
    p: multiprocessing.pool.Pool, 
    logger: logging.Logger, 
    config: Dict, 
    nmr_mol_pool: NMRMolPool,  # ← 包含反应物的分子池
    allowed_elements: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Cut molecules into fragments.
    """
    # 将分子（包括反应物）切割成片段
    fragment_list_non_ring = [frag for fragments in p.map(cut_non_ring, 
                              nmr_mol_pool.mol_list) for frag in fragments]
    fragment_list_ring = [frag for fragments in p.map(cut_ring, 
                          nmr_mol_pool.mol_list) for frag in fragments]
    # ...
```

**功能说明 / Functionality:**
- 将所有候选分子（包括反应物）切割成片段
- 这些片段在交叉操作中被重新组合
- 保留了可能在反应中保留的子结构信息
- Cuts all candidate molecules (including reactants) into fragments
- These fragments are recombined in crossover operations
- Preserves substructure information that may be retained during reactions

### 5. 配置和数据输入 / Configuration and Data Input

**配置文件 / Configuration File:** `config/demo.yaml`

```yaml
use_candidates: False  # ← 启用/禁用候选分子功能
```

**运行脚本 / Run Script:** `run.py` (Line 58)

```python
candidates = input_data.get("candidates", []) if config['use_candidates'] else []
```

**数据格式 / Data Format:** `data_process.py` (Lines 26, 33)

```python
candidates = item0.split(', ') if len(item.split('\n')) == 4 else []
# ...
'candidates': candidates,
```

**数据文件格式示例 / Data File Format Example:**

在 `data/demo/test.txt` 中，如果第一行包含反应物列表：
```
Cc1ccccc1CC#CC(O)c1ccccc1C, c1ccccc1  # ← 反应物SMILES列表（可选）
Cc1ccccc1CC#CC(O)c1ccccc1C            # ← 目标分子
1H NMR (400 MHz, ...) δ ...           # ← 1H NMR数据
13C NMR (101 MHz, ...) δ ...          # ← 13C NMR数据
```

---

## 工作流程 / Workflow

```
1. 输入反应物SMILES列表
   Input reactant SMILES list
   ↓
2. 验证和标准化反应物结构
   Validate and canonicalize reactant structures
   ↓
3. 预测反应物的NMR化学位移
   Predict NMR chemical shifts for reactants
   ↓
4. 创建候选分子池 (场景适配)
   Create candidate molecule pool (scene adaptation)
   ↓
5. 集成到主分子池
   Integrate into main molecule pool
   ↓
6. 对所有分子（含反应物）评分
   Score all molecules (including reactants)
   ↓
7. 切割分子为片段
   Cut molecules into fragments
   ↓
8. 交叉操作：重组片段
   Crossover: recombine fragments
   ↓
9. 生成新的候选分子
   Generate new candidate molecules
   ↓
10. 根据NMR匹配分数优化
    Optimize based on NMR matching scores
```

---

## 关键优势 / Key Advantages

### 1. 子结构保留 / Substructure Preservation

通过将反应物纳入候选池，算法可以：
- 识别和保留在反应中可能保留的化学片段
- 利用这些片段的已知 NMR 特征

By incorporating reactants into the candidate pool, the algorithm can:
- Identify and preserve chemical fragments that may be retained during reactions
- Leverage known NMR characteristics of these fragments

### 2. 化学合理性 / Chemical Reasonability

- 生成的候选分子包含来自实际反应物的片段
- 提高了结构预测的化学合理性

Generated candidate molecules contain fragments from actual reactants:
- Improves chemical reasonability of structure predictions

### 3. 波谱支持 / Spectral Support

- 反应物的 NMR 数据提供了额外的约束
- 帮助算法向正确的结构方向优化

NMR data from reactants provides additional constraints:
- Helps the algorithm optimize towards correct structures

---

## 使用示例 / Usage Example

### 启用候选分子功能 / Enable Candidates Feature

1. **修改配置文件 / Modify Configuration:**

```yaml
# config/demo.yaml
use_candidates: True  # 启用功能
```

2. **准备输入数据 / Prepare Input Data:**

在数据文件中添加反应物SMILES（第一行）：
```
c1ccccc1, CCO                          # 反应物
OC(C#CCc1ccc(Cl)cc1)c1ccc(Cl)cc1      # 目标分子
1H NMR (400 MHz, ...) δ ...
13C NMR (101 MHz, ...) δ ...
```

3. **运行程序 / Run Program:**

```bash
sh scripts/run.sh demo
```

---

## 技术实现总结 / Technical Implementation Summary

**场景适配模块的核心实现在 `src/core/solver.py` 的第 237-241 行：**

The core implementation of the scene adaptation module is in `src/core/solver.py`, lines 237-241:

```python
if candidates:
    result = predict_nmr_from_mol(candidates, raw=True)
    nmr_mol_candidate = NMRMolPool(result)
    logger.info('num_candidate: %d', len(nmr_mol_candidate))
    nmr_mol_pool.add_pool(nmr_mol_candidate)
```

这段代码实现了：
1. **反应物结构的纳入** - 将反应物添加到候选结构池
2. **NMR数据预测** - 为反应物预测化学位移
3. **场景适配** - 通过池合并实现结构集成
4. **片段保留** - 在后续的交叉操作中，这些反应物的片段会被利用

This code implements:
1. **Incorporation of reactant structures** - Adds reactants to the candidate structure pool
2. **NMR data prediction** - Predicts chemical shifts for reactants
3. **Scene adaptation** - Implements structure integration through pool merging
4. **Fragment preservation** - In subsequent crossover operations, fragments from these reactants are utilized

---

## 相关文件清单 / Related Files List

1. **核心求解器 / Core Solver:** `src/core/solver.py`
2. **分子池管理 / Pool Management:** `src/core/pool.py`
3. **求解器工具 / Solver Utils:** `src/core/solver_utils.py`
4. **片段操作 / Fragment Operations:** `src/core/operation.py`
5. **数据处理 / Data Processing:** `data_process.py`
6. **运行脚本 / Run Script:** `run.py`
7. **配置文件 / Configuration:** `config/demo.yaml`

---

## 参考文献 / References

**论文 / Paper:**
- Jin, Yongqi, et al. "NMR-Solver: Automated Structure Elucidation via Large-Scale Spectral Matching and Physics-Guided Fragment Optimization." arXiv preprint arXiv:2509.00640 (2025).
- [arXiv Link](https://arxiv.org/abs/2509.00640)

---

*本分析文档由 GitHub Copilot 生成 / This analysis document was generated by GitHub Copilot*
