# Compatibility Wrapper (legacy `templates/project-config/doc-naming.md`)

> **Deprecated**: 本文件仅作 v1.1 兼容层,保留是为了让既有的 `init-project-config.sh --legacy`
> 脚本与历史示例(`examples/01-wms-warehouse/`)继续工作。
>
> **新项目请使用 canonical 入口**:`<skill-root>/paths/doc-naming-path.md`
>
> 注意 canonical 文件名多了 `-path` 后缀 (`doc-naming-path.md`),与本 legacy 文件名
> (`doc-naming.md`) 不一致 —— 这是 v1.1 命名修正。
>
> `init-project-config.sh`(默认模式)已经把模板写到 `<project>/paths/doc-naming-path.md`,
> 不再使用本文件。
>
> `setup-check.py` 仍然能识别本文件,会发 warning 提示迁移到 `paths/doc-naming-path.md`。

The canonical entry for this configuration is `paths/doc-naming-path.md`. When this
template is used (e.g. by `init-project-config.sh --legacy`), the generated file
should be moved (and renamed) into the project's `paths/` directory as soon as practical.
