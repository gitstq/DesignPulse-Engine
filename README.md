<p align="center">
  <a href="https://github.com/gitstq/DesignPulse-Engine">
    <img src="https://img.shields.io/badge/DesignPulse--Engine-v1.0-blue?style=flat-square" alt="DesignPulse-Engine">
  </a>
  <a href="https://www.python.org/downloads/">
    <img src="https://img.shields.io/badge/Python-3.6+-green?style=flat-square" alt="Python 3.6+">
  </a>
  <a href="https://github.com/gitstq/DesignPulse-Engine/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" alt="MIT License">
  </a>
  <a href="https://github.com/gitstq/DesignPulse-Engine">
    <img src="https://img.shields.io/badge/Dependencies-0-ff69b4?style=flat-square" alt="Zero Dependencies">
  </a>
</p>

<p align="center">
  <b>简体中文</b> | <a href="#繁體中文">繁體中文</a> | <a href="#english">English</a>
</p>

---

# 简体中文

## 🎉 项目介绍

**DesignPulse-Engine** 是一款轻量级、零依赖的终端设计质量检测与优化引擎。它专为前端开发者和 UI 设计师打造，能够在命令行中快速分析 HTML 文件的设计质量，涵盖配色和谐度、对比度合规性、排版规范性、布局一致性、响应式设计及代码质量六大维度，并给出量化评分与针对性优化建议。

无论你是在做设计评审、代码走查，还是日常开发中的快速自查，DesignPulse-Engine 都能帮你高效发现问题、提升设计品质。

> 核心理念：**零外部依赖，纯 Python 标准库实现，开箱即用，离线运行，隐私优先。**

---

## ✨ 核心特性

- **零外部依赖** — 完全基于 Python 标准库构建，无需 `pip install`，克隆即可运行
- **WCAG 2.1 对比度合规检测** — 内置 WCAG 2.1 AA/AAA 级别对比度检测，保障可访问性达标
- **六大维度量化评分** — 配色和谐度(25%)、对比度/可访问性(20%)、排版规范(20%)、布局一致性(15%)、响应式设计(10%)、代码质量(10%)
- **批量分析** — 一键扫描整个目录下的所有 HTML 文件，生成汇总报告
- **多格式报告导出** — 支持 JSON 和 Markdown 两种格式，方便集成到 CI/CD 或文档流程
- **离线运行，隐私优先** — 所有分析均在本地完成，不上传任何文件或数据
- **模块化架构** — 七个独立子命令，按需调用，灵活组合

---

## 🚀 快速开始

### 环境要求

- Python 3.6 或更高版本
- 无需安装任何第三方库

### 安装

```bash
# 克隆仓库
git clone https://github.com/gitstq/DesignPulse-Engine.git
cd DesignPulse-Engine
```

### 使用命令

```bash
# 查看帮助信息
python designpulse.py --help

# 全量分析一个 HTML 文件
python designpulse.py analyze index.html

# 快速评分
python designpulse.py score index.html
```

---

## 📖 详细使用指南

DesignPulse-Engine 提供七个子命令，覆盖从全量分析到专项检测的各类场景。

### 1. `analyze` — 全量设计质量分析

对单个 HTML 文件执行完整的六大维度分析，输出综合评分和各维度详情。

```bash
python designpulse.py analyze index.html
```

输出包含：总分、等级评定、各维度得分、具体问题列表及优化建议。

### 2. `batch` — 批量分析目录

扫描指定目录下所有 `.html` / `.htm` 文件，逐一分析后生成汇总报告。可通过 `-o` 参数将每份独立报告保存到指定目录。

```bash
# 基本用法
python designpulse.py batch ./src/pages

# 保存独立报告到指定目录
python designpulse.py batch ./src/pages -o ./reports
```

### 3. `score` — 快速评分

仅输出总分和等级，适合快速自查或集成到脚本中做阈值判断。

```bash
python designpulse.py score index.html
```

输出示例：`DesignPulse Score: 82 / 100 [B+] - index.html`

### 4. `report` — 生成报告文件

将分析结果导出为 JSON 或 Markdown 格式的报告文件，方便归档、分享或接入自动化流程。

```bash
# 导出 JSON 报告（默认）
python designpulse.py report index.html --format json

# 导出 Markdown 报告
python designpulse.py report index.html --format markdown

# 指定输出路径
python designpulse.py report index.html --format json -o ./output/report.json
```

### 5. `colors` — 配色方案分析

专注于配色维度的专项分析：独立颜色数量、配色和谐度评分、平均对比度、WCAG 合规情况及配色优化建议。

```bash
python designpulse.py colors index.html
```

### 6. `typography` — 排版分析

专注于排版维度的专项分析：字体族列表、字号范围、行高范围、排版规范评分及排版优化建议。

```bash
python designpulse.py typography index.html
```

### 7. `accessibility` — 可访问性分析

专注于可访问性维度的专项分析：可访问性评分、通过项列表、问题列表、对比度不达标的元素详情。

```bash
python designpulse.py accessibility index.html
```

---

## 💡 设计思路与迭代规划

### 设计思路

DesignPulse-Engine 的核心设计哲学是 **「轻量至上，标准先行」**：

1. **零依赖策略** — 拒绝引入任何第三方库，确保在任何 Python 环境下都能直接运行，降低使用门槛。
2. **标准驱动** — 以 WCAG 2.1 等国际标准为检测依据，让评分结果具有权威性和可参考性。
3. **模块解耦** — 分析引擎的每个维度（配色、排版、可访问性等）均为独立模块，可单独调用也可组合使用。
4. **终端优先** — 输出格式针对终端阅读优化，同时提供文件导出能力，兼顾人读和机读。

### 迭代规划

- **v1.0** — 核心功能：六大维度分析、七个子命令、JSON/Markdown 报告导出
- **v1.1（规划中）** — 支持 CSS 文件直接分析、增加自定义评分权重配置
- **v1.2（规划中）** — 支持 CI/CD 集成模式、增加趋势对比分析
- **v2.0（远期）** — 支持 Vue/React 组件分析、可视化 HTML 报告生成

---

## 📦 打包与部署指南

### 使用 PyInstaller 打包为可执行文件

```bash
# 安装 PyInstaller（仅打包时需要）
pip install pyinstaller

# 打包为单文件可执行程序
pyinstaller --onefile --name designpulse designpulse.py

# 打包完成后，可执行文件位于 dist/ 目录
./dist/designpulse analyze index.html
```

### 部署到服务器

```bash
# 克隆到目标服务器
git clone https://github.com/gitstq/DesignPulse-Engine.git /opt/designpulse
cd /opt/designpulse

# 创建软链接到系统 PATH（可选）
sudo ln -s /opt/designpulse/designpulse.py /usr/local/bin/designpulse

# 之后可直接使用
designpulse analyze /path/to/index.html
```

### Docker 部署（可选）

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
ENTRYPOINT ["python", "designpulse.py"]
```

```bash
docker build -t designpulse .
docker run --rm -v $(pwd):/data designpulse analyze /data/index.html
```

---

## 🤝 贡献指南

我们欢迎并感谢所有形式的贡献！无论是提交 Bug 报告、改进建议，还是直接提交代码，都是对项目的巨大支持。

### 贡献流程

1. **Fork** 本仓库
2. 创建特性分支：`git checkout -b feature/your-feature-name`
3. 提交改动：`git commit -m 'feat: add your feature description'`
4. 推送分支：`git push origin feature/your-feature-name`
5. 提交 **Pull Request**

### 代码规范

- 遵循 PEP 8 编码规范
- 新增功能请附带相应的测试用例
- 提交信息建议使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式

### 报告问题

如发现 Bug 或有功能建议，请通过 [GitHub Issues](https://github.com/gitstq/DesignPulse-Engine/issues) 提交，并尽量附上复现步骤和期望行为。

---

## 📄 开源协议

本项目基于 [MIT License](https://github.com/gitstq/DesignPulse-Engine/blob/main/LICENSE) 开源。

```
MIT License

Copyright (c) 2024 DesignPulse-Engine Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

# 繁體中文

## 🎉 專案介紹

**DesignPulse-Engine** 是一款輕量級、零依賴的終端設計品質檢測與最佳化引擎。它專為前端開發者與 UI 設計師打造，能在命令列中快速分析 HTML 檔案的設計品質，涵蓋配色和諧度、對比度合規性、排版規範性、佈局一致性、響應式設計及程式碼品質六大維度，並給出量化評分與針對性最佳化建議。

無論你是在做設計評審、程式碼審查，還是日常開發中的快速自查，DesignPulse-Engine 都能幫你高效發現問題、提升設計品質。

> 核心理念：**零外部依賴，純 Python 標準函式庫實現，開箱即用，離線運行，隱私優先。**

---

## ✨ 核心特性

- **零外部依賴** — 完全基於 Python 標準函式庫構建，無需 `pip install`，克隆即可運行
- **WCAG 2.1 對比度合規檢測** — 內建 WCAG 2.1 AA/AAA 級別對比度檢測，保障可訪問性達標
- **六大維度量化評分** — 配色和諧度(25%)、對比度/可訪問性(20%)、排版規範(20%)、佈局一致性(15%)、響應式設計(10%)、程式碼品質(10%)
- **批次分析** — 一鍵掃描整個目錄下的所有 HTML 檔案，生成彙總報告
- **多格式報告匯出** — 支援 JSON 與 Markdown 兩種格式，方便整合到 CI/CD 或文件流程
- **離線運行，隱私優先** — 所有分析均在本地完成，不上傳任何檔案或資料
- **模組化架構** — 七個獨立子命令，按需呼叫，靈活組合

---

## 🚀 快速開始

### 環境要求

- Python 3.6 或更高版本
- 無需安裝任何第三方函式庫

### 安裝

```bash
# 克隆倉庫
git clone https://github.com/gitstq/DesignPulse-Engine.git
cd DesignPulse-Engine
```

### 使用命令

```bash
# 查看幫助資訊
python designpulse.py --help

# 全量分析一個 HTML 檔案
python designpulse.py analyze index.html

# 快速評分
python designpulse.py score index.html
```

---

## 📖 詳細使用指南

DesignPulse-Engine 提供七個子命令，覆蓋從全量分析到專項檢測的各類場景。

### 1. `analyze` — 全量設計品質分析

對單個 HTML 檔案執行完整的六大維度分析，輸出綜合評分和各維度詳情。

```bash
python designpulse.py analyze index.html
```

輸出包含：總分、等級評定、各維度得分、具體問題列表及最佳化建議。

### 2. `batch` — 批次分析目錄

掃描指定目錄下所有 `.html` / `.htm` 檔案，逐一分析後生成彙總報告。可透過 `-o` 參數將每份獨立報告儲存到指定目錄。

```bash
# 基本用法
python designpulse.py batch ./src/pages

# 儲存獨立報告到指定目錄
python designpulse.py batch ./src/pages -o ./reports
```

### 3. `score` — 快速評分

僅輸出總分和等級，適合快速自查或整合到腳本中做閾值判斷。

```bash
python designpulse.py score index.html
```

輸出示例：`DesignPulse Score: 82 / 100 [B+] - index.html`

### 4. `report` — 生成報告檔案

將分析結果匯出為 JSON 或 Markdown 格式的報告檔案，方便歸檔、分享或接入自動化流程。

```bash
# 匯出 JSON 報告（預設）
python designpulse.py report index.html --format json

# 匯出 Markdown 報告
python designpulse.py report index.html --format markdown

# 指定輸出路徑
python designpulse.py report index.html --format json -o ./output/report.json
```

### 5. `colors` — 配色方案分析

專注於配色維度的專項分析：獨立顏色數量、配色和諧度評分、平均對比度、WCAG 合規情況及配色最佳化建議。

```bash
python designpulse.py colors index.html
```

### 6. `typography` — 排版分析

專注於排版維度的專項分析：字型族列表、字號範圍、行高範圍、排版規範評分及排版最佳化建議。

```bash
python designpulse.py typography index.html
```

### 7. `accessibility` — 可訪問性分析

專注於可訪問性維度的專項分析：可訪問性評分、通過項列表、問題列表、對比度不達標的元素詳情。

```bash
python designpulse.py accessibility index.html
```

---

## 💡 設計思路與迭代規劃

### 設計思路

DesignPulse-Engine 的核心設計哲學是 **「輕量至上，標準先行」**：

1. **零依賴策略** — 拒絕引入任何第三方函式庫，確保在任何 Python 環境下都能直接運行，降低使用門檻。
2. **標準驅動** — 以 WCAG 2.1 等國際標準為檢測依據，讓評分結果具有權威性和可參考性。
3. **模組解耦** — 分析引擎的每個維度（配色、排版、可訪問性等）均為獨立模組，可單獨呼叫也可組合使用。
4. **終端優先** — 輸出格式針對終端閱讀最佳化，同時提供檔案匯出能力，兼顧人讀和機讀。

### 迭代規劃

- **v1.0** — 核心功能：六大維度分析、七個子命令、JSON/Markdown 報告匯出
- **v1.1（規劃中）** — 支援 CSS 檔案直接分析、增加自訂評分權重配置
- **v1.2（規劃中）** — 支援 CI/CD 整合模式、增加趨勢對比分析
- **v2.0（遠期）** — 支援 Vue/React 元件分析、視覺化 HTML 報告生成

---

## 📦 打包與部署指南

### 使用 PyInstaller 打包為可執行檔

```bash
# 安裝 PyInstaller（僅打包時需要）
pip install pyinstaller

# 打包為單檔可執行程式
pyinstaller --onefile --name designpulse designpulse.py

# 打包完成後，可執行檔位於 dist/ 目錄
./dist/designpulse analyze index.html
```

### 部署到伺服器

```bash
# 克隆到目標伺服器
git clone https://github.com/gitstq/DesignPulse-Engine.git /opt/designpulse
cd /opt/designpulse

# 建立軟連結到系統 PATH（可選）
sudo ln -s /opt/designpulse/designpulse.py /usr/local/bin/designpulse

# 之後可直接使用
designpulse analyze /path/to/index.html
```

### Docker 部署（可選）

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
ENTRYPOINT ["python", "designpulse.py"]
```

```bash
docker build -t designpulse .
docker run --rm -v $(pwd):/data designpulse analyze /data/index.html
```

---

## 🤝 貢獻指南

我們歡迎並感謝所有形式的貢獻！無論是提交 Bug 回報、改進建議，還是直接提交程式碼，都是對專案的巨大支持。

### 貢獻流程

1. **Fork** 本倉庫
2. 建立特性分支：`git checkout -b feature/your-feature-name`
3. 提交變更：`git commit -m 'feat: add your feature description'`
4. 推送分支：`git push origin feature/your-feature-name`
5. 提交 **Pull Request**

### 程式碼規範

- 遵循 PEP 8 編碼規範
- 新增功能請附帶相應的測試用例
- 提交資訊建議使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式

### 回報問題

如發現 Bug 或有功能建議，請透過 [GitHub Issues](https://github.com/gitstq/DesignPulse-Engine/issues) 提交，並盡量附上重現步驟和期望行為。

---

## 📄 開源協議

本專案基於 [MIT License](https://github.com/gitstq/DesignPulse-Engine/blob/main/LICENSE) 開源。

```
MIT License

Copyright (c) 2024 DesignPulse-Engine Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

# English

## 🎉 Introduction

**DesignPulse-Engine** is a lightweight, zero-dependency terminal design quality detection and optimization engine. Built for front-end developers and UI designers, it rapidly analyzes the design quality of HTML files from the command line across six key dimensions: color harmony, contrast compliance, typography standards, layout consistency, responsive design, and code quality — delivering quantified scores and actionable optimization suggestions.

Whether you are conducting design reviews, code audits, or quick self-checks during daily development, DesignPulse-Engine helps you efficiently identify issues and elevate design quality.

> Core philosophy: **Zero external dependencies, built entirely on the Python standard library. Ready to run out of the box, works offline, privacy first.**

---

## ✨ Key Features

- **Zero External Dependencies** — Built entirely on the Python standard library. No `pip install` needed; just clone and run.
- **WCAG 2.1 Contrast Compliance** — Built-in WCAG 2.1 AA/AAA level contrast detection to ensure accessibility compliance.
- **Six-Dimension Quantified Scoring** — Color Harmony (25%), Contrast/Accessibility (20%), Typography (20%), Layout Consistency (15%), Responsive Design (10%), Code Quality (10%).
- **Batch Analysis** — Scan all HTML files in a directory with a single command and generate a consolidated summary report.
- **Multi-Format Report Export** — Export reports in JSON or Markdown format for seamless integration into CI/CD pipelines or documentation workflows.
- **Offline & Privacy-First** — All analysis runs locally. No files or data are ever uploaded.
- **Modular Architecture** — Seven independent subcommands that can be invoked individually or combined as needed.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.6 or later
- No third-party packages required

### Installation

```bash
# Clone the repository
git clone https://github.com/gitstq/DesignPulse-Engine.git
cd DesignPulse-Engine
```

### Basic Usage

```bash
# Show help information
python designpulse.py --help

# Run a full analysis on an HTML file
python designpulse.py analyze index.html

# Quick score check
python designpulse.py score index.html
```

---

## 📖 Detailed Usage Guide

DesignPulse-Engine provides seven subcommands covering everything from comprehensive analysis to targeted inspections.

### 1. `analyze` — Full Design Quality Analysis

Performs a complete six-dimension analysis on a single HTML file, outputting an overall score and detailed breakdowns.

```bash
python designpulse.py analyze index.html
```

Output includes: overall score, grade, per-dimension scores, issue list, and optimization suggestions.

### 2. `batch` — Batch Directory Analysis

Scans all `.html` / `.htm` files in the specified directory, analyzes each one, and generates a summary report. Use the `-o` flag to save individual reports to a target directory.

```bash
# Basic usage
python designpulse.py batch ./src/pages

# Save individual reports to a specified directory
python designpulse.py batch ./src/pages -o ./reports
```

### 3. `score` — Quick Scoring

Outputs only the overall score and grade. Ideal for quick checks or threshold validation in scripts.

```bash
python designpulse.py score index.html
```

Example output: `DesignPulse Score: 82 / 100 [B+] - index.html`

### 4. `report` — Generate Report File

Exports analysis results as a JSON or Markdown report file for archiving, sharing, or integration into automated workflows.

```bash
# Export as JSON report (default)
python designpulse.py report index.html --format json

# Export as Markdown report
python designpulse.py report index.html --format markdown

# Specify output path
python designpulse.py report index.html --format json -o ./output/report.json
```

### 5. `colors` — Color Scheme Analysis

Focused analysis on the color dimension: unique color count, harmony score, average contrast ratio, WCAG compliance status, and color optimization suggestions.

```bash
python designpulse.py colors index.html
```

### 6. `typography` — Typography Analysis

Focused analysis on the typography dimension: font family list, font size range, line height range, typography score, and typography optimization suggestions.

```bash
python designpulse.py typography index.html
```

### 7. `accessibility` — Accessibility Analysis

Focused analysis on the accessibility dimension: accessibility score, passed checks, issue list, and details of elements failing contrast requirements.

```bash
python designpulse.py accessibility index.html
```

---

## 💡 Design Philosophy & Roadmap

### Design Philosophy

The core design philosophy of DesignPulse-Engine is **"Lightweight First, Standards-Driven"**:

1. **Zero-Dependency Strategy** — No third-party libraries are introduced, ensuring the tool runs directly in any Python environment and minimizing the barrier to entry.
2. **Standards-Driven** — Detection is based on international standards such as WCAG 2.1, giving scoring results authority and reference value.
3. **Modular Decoupling** — Each analysis dimension (color, typography, accessibility, etc.) is an independent module that can be invoked separately or combined.
4. **Terminal-First** — Output is optimized for terminal readability while also offering file export for both human and machine consumption.

### Roadmap

- **v1.0** — Core features: six-dimension analysis, seven subcommands, JSON/Markdown report export
- **v1.1 (Planned)** — Direct CSS file analysis, custom scoring weight configuration
- **v1.2 (Planned)** — CI/CD integration mode, trend comparison analysis
- **v2.0 (Long-term)** — Vue/React component analysis, visual HTML report generation

---

## 📦 Packaging & Deployment Guide

### Package as a Standalone Executable with PyInstaller

```bash
# Install PyInstaller (only needed for packaging)
pip install pyinstaller

# Package as a single-file executable
pyinstaller --onefile --name designpulse designpulse.py

# After packaging, the executable is in the dist/ directory
./dist/designpulse analyze index.html
```

### Deploy to a Server

```bash
# Clone to the target server
git clone https://github.com/gitstq/DesignPulse-Engine.git /opt/designpulse
cd /opt/designpulse

# Create a symlink to system PATH (optional)
sudo ln -s /opt/designpulse/designpulse.py /usr/local/bin/designpulse

# Now you can use it directly
designpulse analyze /path/to/index.html
```

### Docker Deployment (Optional)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
ENTRYPOINT ["python", "designpulse.py"]
```

```bash
docker build -t designpulse .
docker run --rm -v $(pwd):/data designpulse analyze /data/index.html
```

---

## 🤝 Contributing

We welcome and appreciate contributions of all kinds! Whether it is a bug report, a feature suggestion, or a direct code submission, every contribution makes a difference.

### Contribution Workflow

1. **Fork** this repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m 'feat: add your feature description'`
4. Push the branch: `git push origin feature/your-feature-name`
5. Submit a **Pull Request**

### Code Standards

- Follow PEP 8 coding conventions
- Include corresponding test cases for new features
- Use [Conventional Commits](https://www.conventionalcommits.org/) format for commit messages

### Reporting Issues

If you find a bug or have a feature request, please submit it via [GitHub Issues](https://github.com/gitstq/DesignPulse-Engine/issues). Include reproduction steps and expected behavior whenever possible.

---

## 📄 License

This project is licensed under the [MIT License](https://github.com/gitstq/DesignPulse-Engine/blob/main/LICENSE).

```
MIT License

Copyright (c) 2024 DesignPulse-Engine Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
