# Compatibility Wrapper (legacy `templates/project-config/knowledge-path.md`)

> **Deprecated**: 本文件仅作 v1.1 兼容层,保留是为了让既有的 `init-project-config.sh --legacy`
> 脚本与历史示例(`examples/01-wms-warehouse/`)继续工作。
>
> **新项目请使用 canonical 入口**:`<skill-root>/paths/knowledge-path.md`
>
> `init-project-config.sh`(默认模式)已经把模板写到 `<project>/paths/knowledge-path.md`,
> 不再使用本文件。
>
> `setup-check.py` 仍然能识别本文件,会发 warning 提示迁移到 `paths/`。

The canonical entry for this configuration is `paths/knowledge-path.md`. When this
template is used (e.g. by `init-project-config.sh --legacy`), the generated file
should be moved into the project's `paths/` directory as soon as practical.
