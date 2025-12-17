import os
import argparse
import logging
from pathlib import Path

# Configure logging with ISO 8601 datetime format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z"
)
logger = logging.getLogger(__name__)

DEFAULT_EXCLUDE_DIRS = {".idea", ".venv", "venv", "__pycache__", ".env"}


def collect_files(folder_path: Path, exclude_files: set, exclude_dirs: set, all_files: bool) -> str:
    """Collects content of files from a directory and its subdirectories.

    By default, only collects .py files. If `all_files` is True, collects all files.
    Skips files in `exclude_dirs` and files listed in `exclude_files`.
    Handles read errors gracefully by inserting an error message instead of crashing.

    Args:
        folder_path (Path): Root directory to start collecting files from.
        exclude_files (set): Set of Path objects representing files to exclude.
        exclude_dirs (set): Set of directory names to skip during traversal.
        all_files (bool): If True, include all files; if False, only .py files.

    Returns:
        str: Concatenated string with each file's content prefixed by its relative path
             in format: "[folder_name/relative/path/to/file.py]\n<content>\n\n"
    """
    output_parts = []
    for root, dirs, files in os.walk(folder_path):
        # Filter out excluded directories in-place
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            # Skip non-Python files unless all_files is True
            if not all_files and not file.endswith(".py"):
                continue

            file_path = Path(root) / file
            # Skip explicitly excluded files
            if file_path in exclude_files:
                continue

            # Compute relative path from the root folder
            rel_path = file_path.relative_to(folder_path)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                logger.warning(f"Failed to read file {file_path}: {e}")
                content = f"<<Error reading file: {e}>>"

            output_parts.append(f"[{folder_path.name}/{rel_path}]\n{content}\n\n")

    return "".join(output_parts)


def main():
    """Main entry point for the collect-code CLI tool.

    Parses command-line arguments and collects code from one or more directories.
    Outputs a single file 'collected_code.txt' in the current working directory.
    Excludes the script itself and common system directories by default.
    """
    parser = argparse.ArgumentParser(
        description="Collect code from multiple directories (.py by default, all files with --all-files)"
    )
    parser.add_argument(
        "folders",
        nargs="+",
        help="One or more directory paths to collect code from (space-separated)"
    )
    parser.add_argument(
        "--exclude",
        nargs="*",
        default=[],
        help="Additional directory names to exclude (beyond default: .idea, .venv, venv, __pycache__, .env)"
    )
    parser.add_argument(
        "--all-files",
        action="store_true",
        help="Include all files (not just .py files) in the output"
    )

    args = parser.parse_args()

    # Exclude the script itself and any output file that might exist
    current_script = Path(__file__).resolve()
    exclude_files = {current_script}

    # Combine default and user-provided excluded directories
    exclude_dirs = DEFAULT_EXCLUDE_DIRS.union(set(args.exclude))

    # Define output file path
    output_file = Path(os.getcwd()) / "collected_code.txt"
    output_content = []

    logger.info(f"Starting code collection from {len(args.folders)} directories...")
    logger.debug(f"Excluded directories: {exclude_dirs}")
    logger.debug(f"Excluded files: {exclude_files}")
    logger.debug(f"Collecting all files: {args.all_files}")

    # Process each provided folder
    for folder in args.folders:
        folder_path = Path(folder).resolve()
        if not folder_path.is_dir():
            logger.error(f"Error: {folder_path} is not a directory, skipping.")
            continue

        logger.info(f"Processing directory: {folder_path}")
        output_content.append(
            collect_files(folder_path, exclude_files, exclude_dirs, args.all_files)
        )

    # Write all collected content to output file
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("".join(output_content))
        logger.info(f"Successfully created output file: {output_file}")
    except Exception as e:
        logger.error(f"Failed to write output file {output_file}: {e}")
        raise


if __name__ == "__main__":
    main()
