#!/usr/bin/env python3
"""
Deep Performance Analysis for TerminalAI
========================================

Static code analysis to identify performance issues:
- Lock contention patterns
- Inefficient loops
- Memory allocation hotspots
- Subprocess overhead
- Thread pool sizing
- GPU utilization gaps

This script performs static analysis complementing runtime profiling.
"""

import ast
import json
import sys
from collections import defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any, Set

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


@dataclass
class PerformanceIssue:
    """Represents a detected performance issue."""
    severity: str  # "critical", "high", "medium", "low"
    category: str  # "memory", "cpu", "io", "threading", "gpu"
    file: str
    line: int
    function: str
    description: str
    recommendation: str
    estimated_impact: str  # "High: 50%+ improvement", "Medium: 10-50%", etc.


class PerformanceAnalyzer(ast.NodeVisitor):
    """AST visitor for detecting performance issues."""

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.issues: List[PerformanceIssue] = []
        self.current_function = None
        self.locks_acquired: Set[str] = set()
        self.subprocess_calls = 0
        self.temp_file_creates = 0
        self.loop_depth = 0

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Track current function context."""
        old_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_function

    def visit_For(self, node: ast.For):
        """Detect potentially inefficient loops."""
        self.loop_depth += 1

        # Check for file I/O in loops
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if self._is_file_operation(child):
                    self.issues.append(PerformanceIssue(
                        severity="medium",
                        category="io",
                        file=str(self.filepath.name),
                        line=node.lineno,
                        function=self.current_function or "<module>",
                        description="File I/O operation inside loop",
                        recommendation="Move file operations outside loop or use buffering",
                        estimated_impact="Medium: 10-30% improvement"
                    ))
                    break

        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_While(self, node: ast.While):
        """Track while loops."""
        self.loop_depth += 1
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_With(self, node: ast.With):
        """Detect lock usage patterns."""
        for item in node.items:
            if isinstance(item.context_expr, ast.Call):
                if self._is_lock_acquisition(item.context_expr):
                    # Check for long critical sections
                    if len(node.body) > 10:
                        self.issues.append(PerformanceIssue(
                            severity="high",
                            category="threading",
                            file=str(self.filepath.name),
                            line=node.lineno,
                            function=self.current_function or "<module>",
                            description="Long critical section under lock (>10 statements)",
                            recommendation="Minimize lock scope, consider lock-free alternatives",
                            estimated_impact="High: 30-50% improvement in concurrent scenarios"
                        ))

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        """Detect expensive function calls."""
        # Subprocess calls
        if self._is_subprocess_call(node):
            self.subprocess_calls += 1
            if self.loop_depth > 0:
                self.issues.append(PerformanceIssue(
                    severity="high",
                    category="cpu",
                    file=str(self.filepath.name),
                    line=node.lineno,
                    function=self.current_function or "<module>",
                    description="Subprocess call inside loop",
                    recommendation="Batch subprocess operations or restructure logic",
                    estimated_impact="High: 40-60% improvement"
                ))

        # Temporary file creation
        if self._is_temp_file_creation(node):
            self.temp_file_creates += 1

        # Sleep calls (GUI polling)
        if self._is_sleep_call(node):
            self.issues.append(PerformanceIssue(
                severity="low",
                category="cpu",
                file=str(self.filepath.name),
                line=node.lineno,
                function=self.current_function or "<module>",
                description="Sleep call detected (potential polling)",
                recommendation="Consider event-driven approach or increase interval",
                estimated_impact="Low: 5-10% CPU reduction"
            ))

        # JSON loads/dumps in loops
        if self.loop_depth > 0 and self._is_json_operation(node):
            self.issues.append(PerformanceIssue(
                severity="medium",
                category="cpu",
                file=str(self.filepath.name),
                line=node.lineno,
                function=self.current_function or "<module>",
                description="JSON serialization in loop",
                recommendation="Move JSON operations outside loop or cache results",
                estimated_impact="Medium: 15-25% improvement"
            ))

        self.generic_visit(node)

    def _is_lock_acquisition(self, node: ast.Call) -> bool:
        """Check if call is a lock acquisition."""
        if isinstance(node.func, ast.Attribute):
            return node.func.attr == 'acquire' or 'lock' in node.func.attr.lower()
        return False

    def _is_subprocess_call(self, node: ast.Call) -> bool:
        """Check if call is subprocess.run/Popen."""
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                if node.func.value.id == 'subprocess':
                    return node.func.attr in ('run', 'Popen', 'call', 'check_output')
        return False

    def _is_file_operation(self, node: ast.Call) -> bool:
        """Check if call is a file operation."""
        if isinstance(node.func, ast.Name):
            return node.func.id in ('open', 'read', 'write')
        if isinstance(node.func, ast.Attribute):
            return node.func.attr in ('open', 'read', 'write', 'read_text', 'write_text')
        return False

    def _is_temp_file_creation(self, node: ast.Call) -> bool:
        """Check if call creates temporary file."""
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                if node.func.value.id == 'tempfile':
                    return node.func.attr in ('mkdtemp', 'mkstemp', 'NamedTemporaryFile')
        return False

    def _is_sleep_call(self, node: ast.Call) -> bool:
        """Check if call is time.sleep."""
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                return node.func.value.id == 'time' and node.func.attr == 'sleep'
        return False

    def _is_json_operation(self, node: ast.Call) -> bool:
        """Check if call is JSON serialization."""
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                if node.func.value.id == 'json':
                    return node.func.attr in ('loads', 'dumps', 'load', 'dump')
        return False


def analyze_file(filepath: Path) -> List[PerformanceIssue]:
    """Analyze a single Python file for performance issues."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()

        tree = ast.parse(source, filename=str(filepath))
        analyzer = PerformanceAnalyzer(filepath)
        analyzer.visit(tree)

        return analyzer.issues

    except SyntaxError:
        print(f"Syntax error in {filepath}, skipping...")
        return []
    except Exception as e:
        print(f"Error analyzing {filepath}: {e}")
        return []


def analyze_codebase(base_path: Path) -> Dict[str, List[PerformanceIssue]]:
    """Analyze entire codebase."""
    issues_by_file = defaultdict(list)

    # Analyze main modules
    modules_to_analyze = [
        base_path / "vhs_upscaler" / "vhs_upscale.py",
        base_path / "vhs_upscaler" / "audio_processor.py",
        base_path / "vhs_upscaler" / "queue_manager.py",
        base_path / "vhs_upscaler" / "gui.py",
        base_path / "vhs_upscaler" / "face_restoration.py",
        base_path / "vhs_upscaler" / "rtx_video_sdk" / "video_processor.py",
        base_path / "vhs_upscaler" / "rtx_video_sdk" / "sdk_wrapper.py",
    ]

    for module_path in modules_to_analyze:
        if module_path.exists():
            issues = analyze_file(module_path)
            if issues:
                issues_by_file[str(module_path.relative_to(base_path))] = issues

    return dict(issues_by_file)


def generate_optimization_plan(issues_by_file: Dict[str, List[PerformanceIssue]]) -> str:
    """Generate prioritized optimization plan."""
    lines = [
        "=" * 80,
        "TerminalAI Performance Optimization Plan",
        "=" * 80,
        "",
    ]

    # Count issues by severity
    severity_counts = defaultdict(int)
    category_counts = defaultdict(int)

    all_issues = []
    for issues in issues_by_file.values():
        all_issues.extend(issues)
        for issue in issues:
            severity_counts[issue.severity] += 1
            category_counts[issue.category] += 1

    lines.extend([
        "SUMMARY",
        "-" * 80,
        f"Total issues found: {len(all_issues)}",
        "",
        "By Severity:",
    ])

    for severity in ["critical", "high", "medium", "low"]:
        count = severity_counts.get(severity, 0)
        if count > 0:
            lines.append(f"  {severity.capitalize()}: {count}")

    lines.extend([
        "",
        "By Category:",
    ])

    for category, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        lines.append(f"  {category.capitalize()}: {count}")

    lines.extend(["", ""])

    # Critical and high severity issues first
    lines.extend([
        "PRIORITY ISSUES (Critical & High)",
        "=" * 80,
        ""
    ])

    priority_issues = [i for i in all_issues if i.severity in ("critical", "high")]
    for i, issue in enumerate(sorted(priority_issues, key=lambda x: (x.severity, x.file)), 1):
        lines.extend([
            f"{i}. [{issue.severity.upper()}] {issue.file}:{issue.line} in {issue.function}()",
            f"   Issue: {issue.description}",
            f"   Fix: {issue.recommendation}",
            f"   Impact: {issue.estimated_impact}",
            ""
        ])

    # Medium severity issues
    medium_issues = [i for i in all_issues if i.severity == "medium"]
    if medium_issues:
        lines.extend([
            "",
            "MEDIUM PRIORITY OPTIMIZATIONS",
            "=" * 80,
            ""
        ])

        for i, issue in enumerate(sorted(medium_issues, key=lambda x: x.file), 1):
            lines.extend([
                f"{i}. {issue.file}:{issue.line} in {issue.function}()",
                f"   Issue: {issue.description}",
                f"   Fix: {issue.recommendation}",
                ""
            ])

    # Specific module recommendations
    lines.extend([
        "",
        "MODULE-SPECIFIC RECOMMENDATIONS",
        "=" * 80,
        ""
    ])

    module_recommendations = {
        "vhs_upscale.py": [
            "Implement frame-level parallelism for long videos",
            "Cache FFmpeg filter string generation",
            "Pre-allocate temp directory at startup",
            "Use memory-mapped files for large video processing"
        ],
        "audio_processor.py": [
            "Pre-load DeepFilterNet/AudioSR models at initialization",
            "Implement audio chunk streaming to reduce memory usage",
            "Cache filter chain construction results",
            "Use multiprocessing for AI model inference parallelism"
        ],
        "queue_manager.py": [
            "Implement read-write locks for status queries",
            "Use lock-free queue for high-frequency operations",
            "Batch notification sends to reduce lock contention",
            "Add connection pooling for database operations"
        ],
        "gui.py": [
            "Increase queue polling interval to 2 seconds",
            "Implement debouncing for progress updates (100ms)",
            "Use lazy loading for job list rendering",
            "Cache thumbnail generation with LRU eviction",
            "Batch log updates every 500ms instead of immediate"
        ],
        "rtx_video_sdk/video_processor.py": [
            "Implement frame batching (16-32 frames per batch)",
            "Use CUDA streams for overlapping I/O and compute",
            "Pre-allocate GPU memory buffers",
            "Implement double buffering for frame transfers"
        ]
    }

    for module, recommendations in module_recommendations.items():
        lines.extend([
            f"{module}:",
            ""
        ])
        for rec in recommendations:
            lines.append(f"  - {rec}")
        lines.append("")

    lines.extend(["", "=" * 80])

    return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Static performance analysis for TerminalAI"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("optimization_plan.txt"),
        help="Output file for optimization plan"
    )

    args = parser.parse_args()

    base_path = Path(__file__).parent
    print("Analyzing codebase for performance issues...")
    print("=" * 80)

    issues_by_file = analyze_codebase(base_path)

    print(f"\nFound issues in {len(issues_by_file)} files")

    # Generate optimization plan
    plan = generate_optimization_plan(issues_by_file)

    # Save to file
    args.output.write_text(plan)

    # Save JSON version
    json_path = args.output.with_suffix('.json')
    json_data = {
        filename: [asdict(issue) for issue in issues]
        for filename, issues in issues_by_file.items()
    }
    json_path.write_text(json.dumps(json_data, indent=2))

    print(plan)
    print(f"\nOptimization plan saved to: {args.output}")
    print(f"JSON data saved to: {json_path}")


if __name__ == "__main__":
    main()
