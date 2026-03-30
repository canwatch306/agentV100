---
name: git-fetch-extract
description: 从远端 Git 仓库的指定分支下载代码，并将仓库中 /drv 目录下的 a.tar.gz 解压到指定目标目录。当需要从 Git 获取代码并解压特定压缩包时使用。
---

# Git 代码下载与解压

从远端 Git 仓库克隆指定分支的代码，然后自动定位仓库内的 `/drv/a.tar.gz` 文件并将其解压到用户指定的目录（默认为 `d/save/`）。该技能封装了 Git 操作和解压逻辑，避免代理手动执行复杂命令。

## 工作流程（检查清单）

- [ ] **步骤 1：确认参数** – 用户需提供 Git 仓库 URL 和分支名（可选，默认 `main`）。可指定目标解压目录（默认 `d/save/`）。
- [ ] **步骤 2：执行脚本** – 运行 `python scripts/fetch_and_extract.py <repo_url> [--branch <branch>] [--target <target_dir>]`。
- [ ] **步骤 3：监控输出** – 脚本会打印克隆进度和解压状态，若出错会输出错误信息并退出。
- [ ] **步骤 4：验证结果** – 检查目标目录下是否生成了 `a.tar.gz` 的解压内容。

## 注意事项（Gotchas）

- **Git 依赖**：系统必须安装 Git，且 `git` 命令在 PATH 中可用。
- **磁盘空间**：克隆仓库会占用额外空间，解压后原仓库可手动删除，但脚本不会自动清理。
- **分支名**：若分支名包含特殊字符（如 `/`），需确保正确转义。脚本使用 `git clone --branch <branch>`，支持普通分支名。
- **文件存在性**：脚本会检查仓库中是否存在 `drv/a.tar.gz`，若不存在则报错。
- **跨平台解压**：脚本使用 Python 的 `tarfile` 模块，支持 `.tar.gz` 格式，在 Windows/Linux 下均可工作。

## 脚本使用

### `fetch_and_extract.py`

从 Git 仓库下载代码并解压指定文件。

**用法**：
```bash
python scripts/fetch_and_extract.py <repo_url> [--branch <branch>] [--target <target_dir>]

**参数**：
repo_url：Git 仓库 URL（必需）

--branch：分支名（可选，默认 main）

--target：解压目标目录（可选，默认 d/save/）

**示例**：
python scripts/fetch_and_extract.py https://github.com/example/project.git --branch develop --target ./output

**输出示例**：
Cloning repository https://github.com/example/project.git (branch: develop)...
Clone completed.
Found 2 archive(s) in drv/:
  - a.tar.gz -> extracting to ./output...
  - b.zip -> extracting to ./output...
Extraction completed.

**若找不到压缩文件，会输出**
No archive files found in drv/.