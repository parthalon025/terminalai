#!/usr/bin/env python3
"""
TerminalAI CLI Entry Point
===========================
Enables running the package as: python -m vhs_upscaler

Usage:
    python -m vhs_upscaler          # Launch GUI (default)
    python -m vhs_upscaler --help   # Show help
    python -m vhs_upscaler --info   # Show system information
    python -m vhs_upscaler --cli    # Launch CLI upscaler
"""

import sys
import argparse


def main():
    """Main entry point for python -m vhs_upscaler."""
    parser = argparse.ArgumentParser(
        description="TerminalAI - VHS Video Upscaling Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show system information and available features",
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Launch CLI upscaler instead of GUI",
    )
    parser.add_argument(
        "--check-deps",
        action="store_true",
        help="Check available dependencies",
    )

    args, unknown = parser.parse_known_args()

    # System information
    if args.info:
        from vhs_upscaler import print_system_info
        print_system_info()
        return 0

    # Dependency check
    if args.check_deps:
        from vhs_upscaler import check_dependencies
        check_dependencies(verbose=True)
        return 0

    # CLI upscaler
    if args.cli:
        from vhs_upscaler.vhs_upscale import main as cli_main
        return cli_main()

    # Default: Launch GUI
    from vhs_upscaler.gui import main as gui_main
    # Pass remaining arguments to GUI
    sys.argv = [sys.argv[0]] + unknown
    return gui_main()


if __name__ == "__main__":
    sys.exit(main())
