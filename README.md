# AI IDE - CLI 协作桥接器

**项目背景**：为了让各种AI IDE与CLI工具更好地联动协作，使用Github Copilot和Qwen Code开发了这个通用的桥接工具，并自动生成了所有开源所需文件，如果有错误或不妥处请谅解 。目前已针对免费的Qwen Code进行了适配，感兴趣的开发者可以基于此项目进行二次开发，扩展支持更多AI工具和CLI应用。

## 项目概述

本项目提供了一个Python脚本，在Leader Agent和Qwen Code之间建立桥梁，使AI IDE能够与Qwen Code进行通信，同时让所有交互对用户可见。该桥梁使用基于文件的通信方式确保透明度并支持实时协作。

## 核心功能

- **透明通信**：Leader Agent与Qwen之间的所有交互对人类用户可见
- **基于文件的通信**：使用临时文件或会话文件进行消息传递
- **实时协作**：支持三方实时对话
- **会话管理**：支持带有日志记录的持久会话

## 使用方法
使用项目前需要电脑已经安装Qwen Code命令行工具，原则上可以直接使用本项目，但是最好配合AI IDE使用。

### 默认聊天模式
直接启动脚本用say即可和Qwen Code对话，第一次使用时会自动创建配置文件，可以查看默认配置，支持手动DIY配置。
```bash
# 简洁的聊天界面，只显示Qwen的回答
python callqw.py --say "你好 Qwen"
```
在没有"-"符号开头引起歧义的情况下，也可以直接使用
```bash
# 简洁的聊天界面，只显示Qwen的回答
python callqw.py "你好 Qwen"
```
### 开发者模式
```bash
# 显示详细的调试信息和执行过程
python callqw.py --dev-mode --say "你好 Qwen"
```
### 英文界面模式
```bash
# 手动启用英文界面
python callqw.py --english-ui --say "Hello Qwen"
```
### 代理模式
```bash
# 启用代理模式，允许Qwen直接执行操作
python callqw.py --mode agent --say "生成一个测试txt文件，内容为测试agent模式成功"
```
可以在系统中安装本脚本，脚本优先使用当前目录的配置文件。
## 协作规则
本项目遵循Leader Agent角色协作规则：
- **Leader Agent**：担任Leader角色，负责规划、设计、指挥
- **Qwen Code**：担任执行角色，负责深度分析和代码实现
- **智能分工**：根据任务复杂度自动选择处理方式
规则详见`.github` 里的 `leader agent.chatmode.md`。

## 参数说明

### callqw.py 完整参数
```bash
python callqw.py [选项]

必需参数:
  --say, -s <string>          要发送给 Qwen Code 的消息

可选参数:
  --mode, -m {ask,agent}      工作模式: ask (咨询模式，默认) 或 agent (代理模式)
  --dev-mode                  启用开发者模式，显示详细的调试信息和执行过程
  --english-ui                使用英文界面
  --config, -c <path>         配置文件路径 (默认: config.json)
  --version, -v               显示版本信息并退出
  --help, -h                  显示帮助信息并退出

使用示例:
  python callqw.py --say "分析项目结构"
  python callqw.py --say "检查代码质量" --mode agent
  python callqw.py --say "Review code" --english-ui
  python callqw.py --say "你好" --dev-mode
  python callqw.py --config custom.json --say "测试"
```

## 贡献说明

本项目专为个人使用和AI协作工作流实验而设计。欢迎根据您的需求修改和扩展脚本。

## 许可证

本项目是开源项目，采用MIT许可证。
