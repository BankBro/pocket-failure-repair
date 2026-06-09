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

## 关联记录

- raw manifest: `manifests/raw/binding_moad_zenodo13375913_raw_manifest_v1.json`.
- entries manifest: `manifests/entries/binding_moad_zenodo13375913_entries_manifest_v1.json`.
- md5: `manifests/downloaded_files.md5`.
- sha256: `manifests/downloaded_files.sha256`.
- download log: `logs/wget_resume_20260609T145306Z.log`.
