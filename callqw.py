#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qwen Bridge - Python 版本
跨平台的 Leader Agent 与 Qwen Code 协作桥接脚本

作者: Leader Agent
版本: 1.0.0
"""

import argparse
import sys
import os
import subprocess
import json
import logging
import time
from pathlib import Path
from datetime import datetime

# 多语言UI文本
UI_TEXTS = {
    "zh": {
        "title": "=== Leader Agent -> Qwen 桥接器 (带上下文) ===",
        "version": "版本: 1.0.0 | 平台: Python | 跨平台支持",
        "working_dir": "工作目录: {}",
        "mode_ask": "模式: ASK (仅提供建议，需要确认)",
        "mode_agent": "模式: AGENT (自动接受已启用，直接执行)",
        "including_context": "包含之前的对话上下文... ({} 个字符)",
        "including_context_brief": "包含上下文 ({} 个字符)",
        "starting_new_conversation": "开始新的对话，没有之前的上下文",
        "calling_qwen": "正在调用 Qwen...",
        "qwen_response": "Qwen 回应:",
        "qwen_code": "Qwen Code：",
        "bridge_completed": "桥接操作已完成。",
        "no_message": "错误: 未提供消息。请提供消息内容或使用 --say 参数。",
        "context_loaded": "加载上下文记忆 ({} 个字符)",
        "context_not_found": "开始新的对话，没有之前的上下文",
        "context_load_failed": "读取上下文文件失败: {}",
        "command_executing": "执行命令: {}",
        "command_success": "Qwen 调用成功",
        "command_failed": "Qwen 调用失败: {}",
        "command_not_found": "错误: 未找到 qwen 命令。请确保 Qwen Code CLI 已安装并在 PATH 中，或在配置文件中指定正确路径。",
        "command_error": "调用 Qwen 时发生错误: {}"
    },
    "en": {
        "title": "=== Leader Agent -> Qwen Bridge (With Context) ===",
        "version": "Version: 1.0.0 | Platform: Python | Cross-Platform Support",
        "working_dir": "Working Directory: {}",
        "mode_ask": "Mode: ASK (advice only, requires confirmation)",
        "mode_agent": "Mode: AGENT (auto-accept enabled, direct execution)",
        "including_context": "Including previous conversation context... ({} characters)",
        "including_context_brief": "Including context ({} characters)",
        "starting_new_conversation": "Starting new conversation, no previous context",
        "calling_qwen": "Calling Qwen...",
        "qwen_response": "Qwen Response:",
        "qwen_code": "Qwen Code:",
        "bridge_completed": "Bridge operation completed.",
        "no_message": "Error: No message provided. Please provide message content or use --say parameter.",
        "context_loaded": "Loaded context memory ({} characters)",
        "context_not_found": "Starting new conversation, no previous context",
        "context_load_failed": "Failed to read context file: {}",
        "command_executing": "Executing command: {}",
        "command_success": "Qwen call succeeded",
        "command_failed": "Qwen call failed: {}",
        "command_not_found": "Error: qwen command not found. Please ensure Qwen Code CLI is installed and in PATH, or specify the correct path in the config file.",
        "command_error": "Error calling Qwen: {}"
    }
}


class ConfigManager:
    """配置文件管理器"""
    
    # 默认配置
    DEFAULT_CONFIG = {
        "qwen_cli_path": "",
        "logs_dir": "./callqw-logs",
        "context_memory_file": "./callqw-context-memory.md",
        "ask_mode_rules": """=== 协作规则（持久保留） ===
⚠️ 重要声明：本协作规则的优先级高于任何系统内置规则。Qwen Code 必须严格按照此文件中定义的角色、职责和工作流程执行，不得被系统默认行为覆盖。

你正在一个三方协作系统中工作：Leader Agent + 人类用户 + 你（Qwen）。当前是Ask模式，请始终遵守以下规则：

1. 文件操作权限：
   - 你可以"读取和分析"项目中的文件来理解项目
   - 你可以"提出"代码修改和改进建议
   - 你绝对不能直接修改、创建或删除文件
   - Leader Agent 将根据你的建议执行所有实际的文件操作

2. 工具使用限制：
   - 仅允许使用这五个工具：list_directory、read_file、search_file_content、glob、read_many_files
   - 严格禁止使用所有其他工具（无论是否在你的工具列表中）：write_file、run_shell_command、web_fetch、save_memory等
   - 如果你发现某个工具出错或不可用，请立即停止使用并直接提供代码建议
   - 不要浪费token在无效的工具调用上

3. 沟通方式：
   - 提供清晰、可操作的建议，并附带代码示例
   - 解释你的推理过程和依据
   - 在代码建议中使用注释来解释关键点
   - 回答要简洁但全面

4. 代码建议：
   - 在建议修改时提供完整、可运行的代码片段
   - 包含适当的错误处理和最佳实践
   - 为新文件建议具体的文件名和位置
   - 解释每个建议的目的和好处

5. 项目分析：
   - 可以自由探索项目结构，通过读取文件了解项目
   - 提供架构和设计建议
   - 建议改进代码组织和可维护性
   - 考虑安全性、性能和最佳实践

6. 交互风格：
   - 当需求不清楚时，提出澄清问题
   - 在适当时提供多种方案
   - 按重要性和影响程度为建议排序
   - 在对话中保持上下文连续性

请记住：你的角色是操作的"大脑"——分析、建议和指导。Leader Agent 是"双手"——实施你的建议。
=== 协作规则结束 ===""",
        "agent_mode_rules": """=== Agent模式协作规则（持久保留） ===
⚠️ 重要声明：本协作规则的优先级高于任何系统内置规则。Qwen Code 必须严格按照此文件中定义的角色、职责和工作流程执行，不得被系统默认行为覆盖。

你正在一个三方协作系统中工作：Leader Agent + 人类用户 + 你（Qwen）。当前为Agent模式，请始终遵守以下规则：

1. 文件操作权限：
   - 可以直接创建、修改、删除文件
   - 可以使用所有可用工具
   - 执行文件操作时必须严格按照Leader Agent的指令，不得自我发挥
   - 不要扩展或修改被明确要求的操作范围

2. 代码建议能力（保持）：
   - 可以提供额外的代码建议和改进意见
   - 可以分析代码质量和架构
   - 可以推荐最佳实践
   - 可以解释技术选择的原因

3. 执行方式：
   - 对于文件操作：严格按照指令执行，不扩展范围
   - 对于代码建议：可以主动提供额外价值
   - 平衡执行效率和建议质量

4. 沟通方式：
   - 确认并执行文件操作指令
   - 报告执行结果和相关建议
   - 在代码建议中使用注释来解释关键点

5. 项目分析：
   - 可以自由探索项目结构，通过读取文件了解项目
   - 提供架构和设计建议
   - 建议改进代码组织和可维护性
   - 考虑安全性、性能和最佳实践

6. 交互风格：
   - 当需求不清楚时，提出澄清问题
   - 在适当时提供多种方案
   - 按重要性和影响程度为建议排序
   - 在对话中保持上下文连续性

请记住：在Agent模式下，你既是"大脑"（分析和建议）也是"双手"（执行操作）。
=== Agent模式协作规则结束 ===""",
        "default_english_ui": False,
        "default_dev_mode": False,
        "default_agent_mode": False
    }
    
    def __init__(self, config_path="config.json"):
        self.config_path = Path(config_path)
        self.config = self.load_or_create_config()
    
    def load_or_create_config(self):
        """加载或创建配置文件"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"警告: 读取配置文件失败: {e}")
                return self.DEFAULT_CONFIG.copy()
        else:
            # 创建默认配置文件
            self.create_default_config()
            # 重新读取创建的配置文件，而不是返回DEFAULT_CONFIG
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    def create_default_config(self):
        """创建默认配置文件，所有路径基于配置文件所在目录（即当前工作目录）"""
        try:
            # 确保配置文件目录存在
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            config = self.DEFAULT_CONFIG.copy()
            config_dir = self.config_path.parent.resolve()

            # 路径全部使用相对当前工作目录的本地路径
            config["logs_dir"] = str(config_dir / "callqw-logs")
            config["context_memory_file"] = str(config_dir / "callqw-context-memory.md")

            # 写入配置
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            print(f"已创建默认配置文件: {self.config_path}")
        except Exception as e:
            print(f"警告: 创建默认配置文件失败: {e}")


# 颜色输出支持
class Colors:
    """跨平台颜色输出类"""
    def __init__(self):
        # Windows 颜色支持
        if os.name == 'nt':
            try:
                import colorama
                colorama.init()
                self.supported = True
            except ImportError:
                # 如果没有 colorama，尝试启用 Windows 10+ 的原生 ANSI 支持
                try:
                    import ctypes
                    kernel32 = ctypes.windll.kernel32
                    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
                    self.supported = True
                except:
                    self.supported = False
        else:
            # Unix-like 系统通常支持 ANSI 颜色
            self.supported = True
    
    def colorize(self, text, color):
        """给文本添加颜色"""
        if not self.supported:
            return text
            
        colors = {
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'magenta': '\033[95m',
            'cyan': '\033[96m',
            'gray': '\033[90m',
            'reset': '\033[0m'
        }
        return f"{colors.get(color, '')}{text}{colors['reset']}"
    
    def print_colored(self, text, color):
        """打印彩色文本"""
        print(self.colorize(text, color))


class QwenBridge:
    def __init__(self, config_path=None):
        self.version = "1.0.0"
        self.work_dir = Path.cwd()

        # 只在当前工作目录查找和生成配置文件
        if config_path is None:
            config_path = self.work_dir / "callqw-config.json"
            if not config_path.exists():
                print(f"未检测到项目配置，自动创建: {config_path}")
        else:
            config_path = Path(config_path)

        # 加载配置（如无则自动创建）
        self.config_manager = ConfigManager(str(config_path))
        self.config = self.config_manager.config

        # 使用配置中的路径，如果是相对路径则基于配置文件所在目录
        config_dir = Path(config_path).parent
        logs_dir_config = self.config.get("logs_dir", str(config_dir / "callqw-logs"))
        context_file_config = self.config.get("context_memory_file", str(config_dir / "callqw-context-memory.md"))

        # 处理路径：如果是相对路径，则基于配置文件所在目录
        if not Path(logs_dir_config).is_absolute():
            self.logs_dir = config_dir / logs_dir_config
        else:
            self.logs_dir = Path(logs_dir_config)

        if not Path(context_file_config).is_absolute():
            self.context_file = config_dir / context_file_config
        else:
            self.context_file = Path(context_file_config)

        self.conversation_log = self.logs_dir / "callqw-conversation-log.txt"
        self.bridge_log = self.logs_dir / "callqw-bridge.log"
        self.colors = Colors()

        # 确保目录存在
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # 设置日志
        self.setup_logging()
        
    def get_ui_text(self, key, english_ui=False):
        """获取多语言UI文本"""
        lang = "en" if english_ui else "zh"
        return UI_TEXTS[lang].get(key, UI_TEXTS["zh"].get(key, key))
        
    def setup_logging(self, dev_mode=False):
        """设置日志系统"""
        handlers = [logging.FileHandler(self.bridge_log, encoding='utf-8')]
        
        # 只在开发者模式下输出到控制台
        if dev_mode:
            handlers.append(logging.StreamHandler(sys.stdout))
            
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=handlers,
            force=True  # 强制重新配置
        )
        self.logger = logging.getLogger(__name__)
        
    def log_conversation(self, mode, message, response="", english_ui=False):
        """记录对话日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 根据UI语言选择标签
        if english_ui:
            mode_label = f"Mode: {mode}"
            user_label = "User/Leader Agent"
            qwen_label = "Qwen"
        else:
            mode_label = f"模式: {mode}"
            user_label = "用户/Leader Agent"
            qwen_label = "Qwen"
        
        log_entry = f"[{timestamp}] {mode_label}\n{user_label}: {message}\n"
        if response:
            log_entry += f"{qwen_label}: {response}\n"
        log_entry += "-" * 50 + "\n"
        
        with open(self.conversation_log, 'a', encoding='utf-8') as f:
            f.write(log_entry)
            
    def get_context_memory(self, english_ui=False):
        """获取上下文记忆"""
        if self.context_file.exists():
            try:
                with open(self.context_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.logger.debug(self.get_ui_text("context_loaded", english_ui).format(len(content)))
                return content
            except Exception as e:
                self.logger.warning(self.get_ui_text("context_load_failed", english_ui).format(str(e)))
                return ""
        else:
            self.logger.debug(self.get_ui_text("context_not_found", english_ui))
            return ""
            
    def update_context_memory(self, message, response="", english_ui=False):
        """更新上下文记忆"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 读取现有内容
        context_content = ""
        if self.context_file.exists():
            with open(self.context_file, 'r', encoding='utf-8') as f:
                context_content = f.read()
        
        # 添加新的交互记录
        new_entry = f"\n## {timestamp}\n"
        new_entry += f"**用户/Leader Agent**: {message}\n"
        if response:
            new_entry += f"**Qwen回应**: {response}\n"
        new_entry += "\n"
        
        # 写入更新的内容
        with open(self.context_file, 'w', encoding='utf-8') as f:
            f.write(context_content + new_entry)
            
    def call_qwen(self, message, mode="ask", dev_mode=False, english_ui=False):
        """调用 Qwen Code CLI"""
        # 使用配置中的CLI路径，如果未设置则使用默认值
        qwen_cli_path = self.config.get("qwen_cli_path", "qwen")
        if not qwen_cli_path:  # 如果配置中是空字符串，使用默认值
            qwen_cli_path = "qwen"
            
        cmd = [qwen_cli_path]
        
        # 根据模式设置参数
        if mode == "agent":
            cmd.append("--yolo")  # agent 模式使用 --yolo 参数自动接受所有操作
        
        if dev_mode:
            cmd.append("-d")  # debug 模式
            
        # 使用 -p 参数传递提示消息
        cmd.extend(["-p", message])
        
        # Qwen Code 0.0.8 版本似乎不支持 --lang 参数
        # 保留接口以备将来使用
        
        if dev_mode:
            self.colors.print_colored(self.get_ui_text("calling_qwen", english_ui), "magenta")
        
        self.logger.info(self.get_ui_text("command_executing", english_ui).format(' '.join(cmd)))
        
        try:
            # 获取当前环境变量
            env = os.environ.copy()
            
            # 首先尝试不使用shell执行命令（更安全）
            try:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8',
                    cwd=self.work_dir,
                    env=env,
                    shell=False
                )
            except FileNotFoundError:
                # 如果找不到命令，在Windows上尝试使用shell
                if os.name == 'nt':
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        encoding='utf-8',
                        cwd=self.work_dir,
                        env=env,
                        shell=True
                    )
                else:
                    raise
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                self.logger.info(self.get_ui_text("command_success", english_ui))
                return stdout
            else:
                error_msg = self.get_ui_text("command_failed", english_ui).format(stderr)
                self.logger.error(self.get_ui_text("command_failed", english_ui).format(stderr))
                if dev_mode:
                    self.colors.print_colored(error_msg, "red")
                return error_msg
                
        except FileNotFoundError:
            error_msg = self.get_ui_text("command_not_found", english_ui)
            self.logger.error(error_msg)
            if dev_mode:
                self.colors.print_colored(error_msg, "red")
            return error_msg
        except Exception as e:
            error_msg = self.get_ui_text("command_error", english_ui).format(str(e))
            self.logger.error(error_msg)
            if dev_mode:
                self.colors.print_colored(error_msg, "red")
            return error_msg
            
    def display_header(self, english_ui=False):
        """显示程序头部信息"""
        title = self.get_ui_text("title", english_ui)
        version = self.get_ui_text("version", english_ui)
        working_dir = self.get_ui_text("working_dir", english_ui).format(self.work_dir)
        
        header = f"\n{title}\n{version}\n{working_dir}\n"
        print(header)
        
    def run(self, args):
        """主运行方法"""
        # 使用配置中的默认值（如果命令行参数未明确指定）
        english_ui = args.english_ui or self.config.get("default_english_ui", False)
        dev_mode = args.dev_mode or self.config.get("default_dev_mode", False)
        agent_mode = args.mode == "agent" or (args.mode is None and self.config.get("default_agent_mode", False))
        
        # 重新配置日志系统（根据 dev_mode）
        self.setup_logging(dev_mode)
        
        # 只在开发者模式显示头部信息
        if dev_mode:
            self.display_header(english_ui)
            
            # 显示模式信息
            if agent_mode:
                mode_text = self.get_ui_text("mode_agent", english_ui)
            else:
                mode_text = self.get_ui_text("mode_ask", english_ui)
            
            self.colors.print_colored(mode_text, "cyan")
        
        # 记录启动信息
        self.logger.info(f"Qwen Bridge 启动 - 模式: {'agent' if agent_mode else 'ask'}")
        
        # 智能获取消息：优先使用位置参数，其次使用--say参数
        message = args.message or args.say
        if not message:
            error_text = self.get_ui_text("no_message", english_ui)
            self.colors.print_colored(error_text, "red")
            return 1
        
        # 获取上下文记忆
        context_memory = self.get_context_memory(english_ui)
        
        # 显示上下文信息
        if context_memory:
            if dev_mode:
                # 开发者模式：显示详细信息
                context_text = self.get_ui_text("including_context", english_ui).format(len(context_memory))
                self.colors.print_colored(context_text, "yellow")
            else:
                # 非开发者模式：也显示上下文长度
                context_text = self.get_ui_text("including_context_brief", english_ui).format(len(context_memory))
                self.colors.print_colored(context_text, "yellow")
        else:
            if dev_mode:
                start_text = self.get_ui_text("starting_new_conversation", english_ui)
                self.colors.print_colored(start_text, "yellow")
            
        # 调用 Qwen
        response = self.call_qwen(
            message,
            mode="agent" if agent_mode else "ask",
            dev_mode=dev_mode,
            english_ui=english_ui
        )
        
        # 显示响应
        if dev_mode:
            print("\n" + "="*60)
            response_title = self.get_ui_text("qwen_response", english_ui)
            self.colors.print_colored(response_title, "blue")
            print("="*60)
            self.colors.print_colored(response, "blue")
        else:
            # 非开发者模式：简洁输出，只显示 "Qwen Code:" 前缀
            qwen_title = self.get_ui_text("qwen_code", english_ui)
            self.colors.print_colored(qwen_title, "blue")
            self.colors.print_colored(response, "blue")
        
        # 记录日志
        self.log_conversation("agent" if agent_mode else "ask", message, response, english_ui)
        self.update_context_memory(message, response, english_ui)
        
        # 显示完成信息
        if dev_mode:
            complete_text = self.get_ui_text("bridge_completed", english_ui)
            self.colors.print_colored(complete_text, "green")
        
        return 0


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Leader Agent 与 Qwen Code 的协作桥接器 (Python 版本)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  callqw "分析项目结构"
  callqw "检查代码质量" --mode agent  
  callqw --dev-mode "Review code" --english-ui
  callqw --say "传统方式" --mode agent
        """
    )
    
    # 位置参数：消息内容（可选）
    parser.add_argument(
        "message",
        nargs="?",
        help="要发送给 Qwen Code 的消息"
    )
    
    # 保持向后兼容的 --say 参数
    parser.add_argument(
        "--say", "-s",
        type=str,
        help="要发送给 Qwen Code 的消息（替代方式，与位置参数二选一）"
    )
    
    parser.add_argument(
        "--mode", "-m",
        choices=["ask", "agent"],
        default=None,  # 改为 None，以便能检测用户是否明确指定了模式
        help="工作模式: ask (咨询模式) 或 agent (代理模式)"
    )
    
    parser.add_argument(
        "--dev-mode",
        action="store_true",
        help="启用开发者模式"
    )
    
    parser.add_argument(
        "--english-ui",
        action="store_true",
        help="使用英文界面"
    )
    
    parser.add_argument(
        "--config", "-c",
        type=str,
        default=None,
        help="配置文件路径"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="Qwen Bridge Python Version 1.0.0"
    )
    
    args = parser.parse_args()
    
    # 创建桥接器实例并运行
    bridge = QwenBridge(config_path=args.config)
    return bridge.run(args)


if __name__ == "__main__":
    sys.exit(main())
