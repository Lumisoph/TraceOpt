"""只读检查轨迹和导出 IR 的命令行接口。"""

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from .dependency import analyze_trajectory
from .semantics import analyze_command
from .trajectory import load_trajectory


class _Parser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        kwargs["add_help"] = False
        super().__init__(*args, **kwargs)
        self.add_argument("-h", "--help", action="help", help="显示帮助信息")
        self._positionals.title = "位置参数"
        self._optionals.title = "选项"

    def format_usage(self):
        return super().format_usage().replace("usage: ", "用法：", 1)

    def format_help(self):
        return super().format_help().replace("usage: ", "用法：", 1)

    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(2, "错误：参数无效，请使用 --help 查看用法。\n")


def main(argv: list[str] | None = None) -> int:
    """输出 UTF-8 JSON；输入或输出错误返回 2。"""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = _Parser(prog="traceopt", description="只读检查工具调用轨迹并导出规范事件")
    subparsers = parser.add_subparsers(dest="action", required=True, title="子命令")
    for name, description in [("inspect", "输出轨迹摘要"), ("export", "输出完整规范事件"),
                              ("analyze", "分析显式工作目录下的读写依赖")]:
        child = subparsers.add_parser(name, help=description, description=description)
        child.add_argument("input", metavar="输入文件", type=Path, help="UTF-8 轨迹 JSON 文件")
        child.add_argument(
            "--output", metavar="输出文件", type=Path, help="创建新文件，不覆盖已有文件")
        if name == "analyze":
            child.add_argument("--cwd", required=True, metavar="POSIX目录",
                               help="显式断言所有调用使用此目录；不会从轨迹推断")
    args = parser.parse_args(argv)
    try:
        trajectory = load_trajectory(args.input)
        if args.action == "export":
            data = {"schema_version": 1, **asdict(trajectory)}
        elif args.action == "analyze":
            context = analyze_command("cat placeholder", cwd=args.cwd)
            if context.unknown:
                raise ValueError(context.reason)
            analysis = analyze_trajectory(trajectory, cwd_by_call={
                e.call_id: args.cwd for e in trajectory.events if e.kind == "tool_call"})
            data = {"schema_version": 1, "cwd_policy": "explicit_fixed", **asdict(analysis)}
        else:
            data = {
                "schema_version": 1,
                "source": trajectory.source,
                "source_sha256": trajectory.source_sha256,
                "trajectory_format": trajectory.trajectory_format,
                "instance_id": trajectory.instance_id,
                "message_count": len({e.message_index for e in trajectory.events}),
                "event_count": len(trajectory.events),
                "tool_call_count": sum(e.kind == "tool_call" for e in trajectory.events),
                "tool_result_count": sum(e.kind == "tool_result" for e in trajectory.events),
                "pending_call_ids": trajectory.pending_call_ids,
            }
        payload = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
        if args.output is None:
            sys.stdout.write(payload)
        else:
            with args.output.open("x", encoding="utf-8", newline="\n") as output:
                output.write(payload)
    except ValueError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2
    except FileExistsError:
        print("错误：输出文件已存在，不能覆盖。", file=sys.stderr)
        return 2
    except OSError:
        print("错误：无法写入输出，请检查路径、权限或输出管道。", file=sys.stderr)
        return 2
    return 0
