# binding_moad_zenodo13375913

## 数据集身份

- `dataset_id`: `binding_moad_zenodo13375913`.
- 用途: DiffSBDD Binding MOAD pilot 审计的数据获取和后续处理输入.
- 来源: Zenodo `10.5281/zenodo.13375913`, `Replication Data for: Geometry-Complete Diffusion for 3D Molecule Generation and Optimization`.
- 访问类型: public.
- license: `Creative Commons Attribution 4.0 International`.

## 重要边界

- 该目录使用的是 Zenodo 归档的 Binding MOAD 结构实验文件副本, 不是已经关闭的原 `BindingMOAD.org` 站点直连下载.
- 该目录可以用于 DiffSBDD audit pilot 的数据处理和来源追踪.
- 仅凭该目录不能声明 DiffSBDD official/original protocol reproduction.
- 仅凭该目录不能声明 formal failure prevalence 或 repair benchmark result.
- 正式分析前仍需冻结 processed test 目录, `moad_test.txt` 对齐, training/test leakage 状态, evaluator 覆盖率和 failure label 规则.

## 目录约定

- `raw_downloads/`: 下载缓存和下载校验对应目录. 当前保留 `every.csv`; `every_part_a.zip` 和 `every_part_b.zip` 已在 checksum 校验和解压后删除以控制存储.
- `raw/`: 后续处理使用的原始数据目录. 当前包含 `every.csv` 和 `BindingMOAD_2020/*.bio*`.
- `entries/`: canonical sample entries 入口. 当前仅有空 `index.jsonl`, 表示 raw 数据已获取, 但逐样本 entry 尚未 materialize.
- `manifests/`: checksum 和 dataset raw manifest.
- `logs/`: 下载, 断点续传, checksum, 解压和删除压缩包的日志.

## 复现下载命令

本次最初用 `curl` 下载, 大文件中途断开后改用 `wget -c` 完成断点续传. 之后仓库规范已改为大文件优先使用 `aria2c`. 如需重新下载, 推荐使用下面的命令:

```bash
mkdir -p data/datasets/binding_moad_zenodo13375913/raw_downloads
mkdir -p data/datasets/binding_moad_zenodo13375913/raw
mkdir -p third_party/diffsbdd/checkpoints

aria2c -c -x 8 -s 8 -k 1M --retry-wait=30 --max-tries=0 \
  -d data/datasets/binding_moad_zenodo13375913/raw_downloads \
  -o every.csv \
  "https://zenodo.org/record/13375913/files/every.csv?download=1"

aria2c -c -x 8 -s 8 -k 1M --retry-wait=30 --max-tries=0 \
  -d data/datasets/binding_moad_zenodo13375913/raw_downloads \
  -o every_part_a.zip \
  "https://zenodo.org/record/13375913/files/every_part_a.zip?download=1"

aria2c -c -x 8 -s 8 -k 1M --retry-wait=30 --max-tries=0 \
  -d data/datasets/binding_moad_zenodo13375913/raw_downloads \
  -o every_part_b.zip \
  "https://zenodo.org/record/13375913/files/every_part_b.zip?download=1"

aria2c -c -x 8 -s 8 -k 1M --retry-wait=30 --max-tries=0 \
  -d third_party/diffsbdd/checkpoints \
  -o moad_fullatom_cond.ckpt \
  "https://zenodo.org/record/8183747/files/moad_fullatom_cond.ckpt?download=1"

md5sum -c data/datasets/binding_moad_zenodo13375913/manifests/downloaded_files.md5
sha256sum -c data/datasets/binding_moad_zenodo13375913/manifests/downloaded_files.sha256

cp data/datasets/binding_moad_zenodo13375913/raw_downloads/every.csv \
  data/datasets/binding_moad_zenodo13375913/raw/every.csv
unzip data/datasets/binding_moad_zenodo13375913/raw_downloads/every_part_a.zip \
  -d data/datasets/binding_moad_zenodo13375913/raw
unzip data/datasets/binding_moad_zenodo13375913/raw_downloads/every_part_b.zip \
  -d data/datasets/binding_moad_zenodo13375913/raw
```

若需要按当前空间策略删除压缩包, 必须先完成 checksum 校验和解压记录:

```bash
rm data/datasets/binding_moad_zenodo13375913/raw_downloads/every_part_a.zip
rm data/datasets/binding_moad_zenodo13375913/raw_downloads/every_part_b.zip
```

## 当前落盘状态

- `raw/every.csv`: retained.
- `raw/BindingMOAD_2020/`: retained, 当前 `.bio*` 文件数为 59346.
- `raw_downloads/every.csv`: retained as download cache.
- `raw_downloads/every_part_a.zip`: removed after checksum and extraction.
- `raw_downloads/every_part_b.zip`: removed after checksum and extraction.
- `work/diffsbdd/processed_noH_full/`: retained locally as ignored processed output, 当前大小约 1.5G.
- `work/diffsbdd/processed_noH_full/test/`: retained locally, 已逐项对齐 `third_party/diffsbdd/data/moad_test.txt` 的 130 个 test 条目.

## DiffSBDD 预处理命令

DiffSBDD Binding MOAD full-atom conditional checkpoint 使用 `processed_noH_full/` 输入. 本数据集的官方风格预处理使用 DiffSBDD 自带脚本, CPU 串行执行, 不需要 GPU, 不修改 DiffSBDD 核心处理逻辑.

本次 pilot 的 resolved 配置保存在:

```text
experiments/20260609-03-diffsbdd-audit-protocol-pilot/configs/resolved/data/binding_moad_preprocess_diffsbdd.yaml
```

推荐命令:

```bash
conda run -n pfr-diffsbdd bash -lc '
cd /home/lyj/mnt/project/pocket-failure-repair/third_party/diffsbdd
python -W ignore process_bindingmoad.py \
  /home/lyj/mnt/project/pocket-failure-repair/data/datasets/binding_moad_zenodo13375913/raw \
  --outdir /home/lyj/mnt/project/pocket-failure-repair/data/datasets/binding_moad_zenodo13375913/work/diffsbdd/processed_noH_full
'
```

执行边界:

- 不加 `--make_split`, 使用 DiffSBDD 仓库自带 `data/moad_train.txt`, `data/moad_val.txt`, `data/moad_test.txt`.
- 不加 `--ca_only`, 因为后续使用 `moad_fullatom_cond.ckpt`.
- 输出目录 `work/diffsbdd/processed_noH_full/` 是本地处理产物, 不提交.
- 后续 audit 只使用 `processed_noH_full/test/`, 但官方脚本会同时生成 train/val/test 和训练统计文件.
- 预处理完成后必须检查 `moad_test.txt` 130 个 test 条目的 PDB/SDF/TXT coverage, 未通过不得进入 inference.

## DiffSBDD 预处理结果

本次预处理已完成, 使用 `pfr-diffsbdd` CPU 串行执行, 主命令 exit code 为 0. 机器可读记录保存在:

```text
experiments/20260609-03-diffsbdd-audit-protocol-pilot/metadata/binding_moad_preprocess_metadata.json
```

关键结果:

- 输出目录: `work/diffsbdd/processed_noH_full/`, 大小约 1.5G.
- 顶层输出: `train.npz`, `val.npz`, `test.npz`, `train_smiles.npy`, `size_distribution.npy`, `summary.txt`.
- summary before: train `40354`, val `246`, test `130`.
- summary after: train `40353`, val `246`, test `130`.
- test coverage: `moad_test.txt` 130 个条目全部具备 SDF/TXT, 并对齐到 92 个 pocket PDB, missing `0`.
- warning: 日志中有 RDKit explicit valence warning, Open Babel kekulization warning, 以及 1 次非阻断 `libXrender.so.1` 提示; 当前记录为 `completed_with_warnings`.

结论边界:

- 该结果只表示 DiffSBDD Binding MOAD pilot 的 `processed_noH_full/test/` 输入已经可用.
- 该结果不构成 official/original protocol reproduction, formal failure prevalence, clean-test status 或 repair benchmark result.

## 关联记录

- raw manifest: `manifests/raw/binding_moad_zenodo13375913_raw_manifest_v1.json`.
- entries manifest: `manifests/entries/binding_moad_zenodo13375913_entries_manifest_v1.json`.
- md5: `manifests/downloaded_files.md5`.
- sha256: `manifests/downloaded_files.sha256`.
- download log: `logs/wget_resume_20260609T145306Z.log`.
