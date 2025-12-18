"""
Unit and integration tests for collect_code.py

This module contains comprehensive tests for the code collection functionality,
including unit tests for the collect_files function and integration tests for
the CLI interface.
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import collect_code


class TestFileStructureFixture:
    """
    Reusable fixture for creating test directory structures.

    This class provides methods to create common test file structures,
    reducing code duplication across test cases.
    """

    @staticmethod
    def create_standard_structure(base_path: Path) -> dict:
        """
        Create a standard test directory structure with multiple language files.

        Test Case: Standard project structure with mixed file types
        Input:
            base_path: Root directory for test structure

        Creates:
            - test.py: Python file
            - Test.java: Java file
            - program.c: C file
            - program.cpp: C++ file
            - header.h: C header
            - header.hpp: C++ header
            - readme.txt: Text file
            - readme.md: Markdown file
            - subdir/sub.py: Python file in subdirectory
            - build/output.o: File in build directory

        Returns:
            Dictionary with paths to created files and directories
        """
        files = {}

        # Create main test files
        files["test.py"] = base_path / "test.py"
        files["test.py"].write_text("print('Python')")

        files["Test.java"] = base_path / "Test.java"
        files["Test.java"].write_text("class Test {}")

        files["program.c"] = base_path / "program.c"
        files["program.c"].write_text("int main() {}")

        files["program.cpp"] = base_path / "program.cpp"
        files["program.cpp"].write_text("int main() {}")

        files["header.h"] = base_path / "header.h"
        files["header.h"].write_text("#define TEST")

        files["header.hpp"] = base_path / "header.hpp"
        files["header.hpp"].write_text("#define TEST")

        files["readme.txt"] = base_path / "readme.txt"
        files["readme.txt"].write_text("readme")

        files["readme.md"] = base_path / "readme.md"
        files["readme.md"].write_text("# readme")

        # Create subdirectory with file
        subdir = base_path / "subdir"
        subdir.mkdir()
        files["sub.py"] = subdir / "sub.py"
        files["sub.py"].write_text("# subdir python")

        # Create build directory with file
        build_dir = base_path / "build"
        build_dir.mkdir()
        files["output.o"] = build_dir / "output.o"
        files["output.o"].write_text("binary")

        return files

    @staticmethod
    def create_project_structure(base_path: Path) -> dict:
        """
        Create a realistic project directory structure.

        Test Case: Multi-directory project structure
        Input:
            base_path: Root directory for project structure

        Creates:
            - src/main.py: Python main file
            - src/App.java: Java application
            - src/util.c: C utility
            - src/util.h: C header
            - tests/test_main.py: Python test file
            - build/output.o: Build artifact

        Returns:
            Dictionary with paths to created files and directories
        """
        files = {}

        # Create src directory
        src_dir = base_path / "src"
        src_dir.mkdir()
        files["main.py"] = src_dir / "main.py"
        files["main.py"].write_text("def main():\n    pass")

        files["App.java"] = src_dir / "App.java"
        files["App.java"].write_text("public class App {}")

        files["util.c"] = src_dir / "util.c"
        files["util.c"].write_text("int util() { return 0; }")

        files["util.h"] = src_dir / "util.h"
        files["util.h"].write_text("#ifndef UTIL_H\n#define UTIL_H\n#endif")

        # Create tests directory
        tests_dir = base_path / "tests"
        tests_dir.mkdir()
        files["test_main.py"] = tests_dir / "test_main.py"
        files["test_main.py"].write_text("def test():\n    pass")

        # Create build directory
        build_dir = base_path / "build"
        build_dir.mkdir()
        files["output.o"] = build_dir / "output.o"
        files["output.o"].write_text("binary")

        return files


class TestCollectFiles(unittest.TestCase):
    """Unit tests for the collect_files function"""

    def setUp(self):
        """Create a temporary directory structure for testing"""
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_path = Path(self.test_dir.name)
        self.files = TestFileStructureFixture.create_standard_structure(self.test_path)

    def tearDown(self):
        """Clean up temporary directory"""
        self.test_dir.cleanup()

    def test_collect_default_languages(self):
        """
        Test default language collection (Python, Java, C, C++).

        Test Case: Verify that only default supported languages are collected
        Input:
            - Directory with .py, .java, .c, .cpp, .h, .hpp, .txt, .md files
            - all_files=False
            - No exclusions

        Expected Output:
            - Result contains: .py, .java, .c, .cpp, .h, .hpp files
            - Result does NOT contain: .txt, .md files
        """
        result = collect_code.collect_files(
            self.test_path,
            exclude_files=set(),
            exclude_dirs=set(),
            all_files=False,
            include_extensions=collect_code.DEFAULT_EXTENSIONS,
            exclude_extensions=set(),
        )

        # Should include default languages
        self.assertIn("test.py", result)
        self.assertIn("Test.java", result)
        self.assertIn("program.c", result)
        self.assertIn("program.cpp", result)
        self.assertIn("header.h", result)
        self.assertIn("header.hpp", result)
        self.assertIn("sub.py", result)

        # Should not include non-default files
        self.assertNotIn("readme.txt", result)
        self.assertNotIn("readme.md", result)

    def test_collect_all_files(self):
        """
        Test all-files collection mode.

        Test Case: Verify all files are collected when all_files=True
        Input:
            - Directory with multiple file types
            - all_files=True
            - No exclusions

        Expected Output:
            - Result contains all file types including .txt and .md
        """
        result = collect_code.collect_files(
            self.test_path,
            exclude_files=set(),
            exclude_dirs=set(),
            all_files=True,
            include_extensions=collect_code.DEFAULT_EXTENSIONS,
            exclude_extensions=set(),
        )

        # Should include all file types
        self.assertIn("test.py", result)
        self.assertIn("readme.txt", result)
        self.assertIn("readme.md", result)

    def test_exclude_extensions(self):
        """
        Test extension-based exclusion.

        Test Case: Verify specific file extensions can be excluded
        Input:
            - Directory with .py, .java, .c, .cpp files
            - exclude_extensions={".py", ".java"}

        Expected Output:
            - Result does NOT contain .py and .java files
            - Result contains .c and .cpp files
        """
        exclude_ext = {".py", ".java"}
        result = collect_code.collect_files(
            self.test_path,
            exclude_files=set(),
            exclude_dirs=set(),
            all_files=False,
            include_extensions=collect_code.DEFAULT_EXTENSIONS,
            exclude_extensions=exclude_ext,
        )

        # Should not include Python or Java
        self.assertNotIn("test.py", result)
        self.assertNotIn("Test.java", result)
        self.assertNotIn("sub.py", result)

        # Should include C and C++
        self.assertIn("program.c", result)
        self.assertIn("program.cpp", result)

    def test_exclude_directories(self):
        """
        Test directory-based exclusion.

        Test Case: Verify specific directories can be excluded from traversal
        Input:
            - Directory structure with 'build' subdirectory
            - exclude_dirs={"build"}
            - all_files=True

        Expected Output:
            - Result does NOT contain files from 'build' directory
            - Result contains files from other directories
        """
        result = collect_code.collect_files(
            self.test_path,
            exclude_files=set(),
            exclude_dirs={"build"},
            all_files=True,
            include_extensions=collect_code.DEFAULT_EXTENSIONS,
            exclude_extensions=set(),
        )

        # Should not include files from build directory
        self.assertNotIn("output.o", result)

        # Should include files from other directories
        self.assertIn("test.py", result)

    def test_exclude_specific_files(self):
        """
        Test specific file path exclusion.

        Test Case: Verify individual files can be excluded by path
        Input:
            - Directory with test.py and sub.py
            - exclude_files={path_to_test.py}

        Expected Output:
            - Result does NOT contain test.py content
            - Result contains sub.py content
        """
        test_py_path = self.test_path / "test.py"
        result = collect_code.collect_files(
            self.test_path,
            exclude_files={test_py_path},
            exclude_dirs=set(),
            all_files=False,
            include_extensions=collect_code.DEFAULT_EXTENSIONS,
            exclude_extensions=set(),
        )

        # Should not include the excluded file
        self.assertNotIn("print('Python')", result)

        # Should include other Python files
        self.assertIn("sub.py", result)

    def test_exclude_extensions_precedence(self):
        """
        Test that extension exclusion takes precedence over all_files mode.

        Test Case: Verify exclude_extensions works even with all_files=True
        Input:
            - Directory with .py, .txt, .md files
            - all_files=True
            - exclude_extensions={".txt"}

        Expected Output:
            - Result does NOT contain .txt files
            - Result contains .py and .md files
        """
        exclude_ext = {".txt"}
        result = collect_code.collect_files(
            self.test_path,
            exclude_files=set(),
            exclude_dirs=set(),
            all_files=True,
            include_extensions=collect_code.DEFAULT_EXTENSIONS,
            exclude_extensions=exclude_ext,
        )

        # Should not include txt even with all_files=True
        self.assertNotIn("readme.txt", result)

        # Should include other files
        self.assertIn("test.py", result)
        self.assertIn("readme.md", result)

    def test_file_content_format(self):
        """
        Test output format with proper headers and content.

        Test Case: Verify collected output has correct formatting
        Input:
            - Directory with test.py containing "print('Python')"
            - exclude_dirs={"build", "subdir"}

        Expected Output:
            - Result contains "[dir_name/test.py]" header
            - Result contains "print('Python')" content
        """
        result = collect_code.collect_files(
            self.test_path,
            exclude_files=set(),
            exclude_dirs={"build", "subdir"},
            all_files=False,
            include_extensions=collect_code.DEFAULT_EXTENSIONS,
            exclude_extensions=set(),
        )

        # Check for proper formatting
        self.assertIn(f"[{self.test_path.name}/test.py]", result)
        self.assertIn("print('Python')", result)

    def test_case_insensitive_extensions(self):
        """
        Test case-insensitive file extension matching.

        Test Case: Verify extension matching works regardless of case
        Input:
            - Files with uppercase extensions: Test.PY, Test.JAVA
            - include_extensions (lowercase): {".py", ".java"}

        Expected Output:
            - Result contains content from Test.PY and Test.JAVA
        """
        # Create files with uppercase extensions
        (self.test_path / "Test.PY").write_text("uppercase py")
        (self.test_path / "Test.JAVA").write_text("uppercase java")

        result = collect_code.collect_files(
            self.test_path,
            exclude_files=set(),
            exclude_dirs=set(),
            all_files=False,
            include_extensions=collect_code.DEFAULT_EXTENSIONS,
            exclude_extensions=set(),
        )

        # Should handle case-insensitive matching
        self.assertIn("uppercase py", result)
        self.assertIn("uppercase java", result)


class TestArgumentParsing(unittest.TestCase):
    """Unit tests for CLI argument parsing"""

    def test_exclude_langs_parsing_without_dots(self):
        """
        Test parsing --exclude-langs with extensions without leading dots.

        Test Case: CLI parses extension list without dots correctly
        Input:
            - CLI args: ['collect_code.py', 'test', '--exclude-langs=py,java']

        Expected Output:
            - Parsed exclude_extensions={'.py', '.java'} (dots added)
        """
        with patch("sys.argv", ["collect_code.py", "test", "--exclude-langs=py,java"]):
            with patch("collect_code.Path.is_dir", return_value=True):
                with patch("collect_code.collect_files", return_value=""):
                    with patch("builtins.open", unittest.mock.mock_open()):
                        captured_args = {}

                        def capture_collect(
                            folder_path,
                            exclude_files,
                            exclude_dirs,
                            all_files,
                            include_extensions,
                            exclude_extensions,
                        ):
                            captured_args["exclude_extensions"] = exclude_extensions
                            return ""

                        with patch("collect_code.collect_files", side_effect=capture_collect):
                            collect_code.main()

                        self.assertEqual(captured_args["exclude_extensions"], {".py", ".java"})

    def test_exclude_langs_parsing_with_dots(self):
        """
        Test parsing --exclude-langs with extensions with leading dots.

        Test Case: CLI parses extension list with dots correctly
        Input:
            - CLI args: ['collect_code.py', 'test', '--exclude-langs=.cpp,.h']

        Expected Output:
            - Parsed exclude_extensions={'.cpp', '.h'} (dots preserved)
        """
        with patch("sys.argv", ["collect_code.py", "test", "--exclude-langs=.cpp,.h"]):
            with patch("collect_code.Path.is_dir", return_value=True):
                with patch("collect_code.collect_files", return_value=""):
                    with patch("builtins.open", unittest.mock.mock_open()):
                        captured_args = {}

                        def capture_collect(
                            folder_path,
                            exclude_files,
                            exclude_dirs,
                            all_files,
                            include_extensions,
                            exclude_extensions,
                        ):
                            captured_args["exclude_extensions"] = exclude_extensions
                            return ""

                        with patch("collect_code.collect_files", side_effect=capture_collect):
                            collect_code.main()

                        self.assertEqual(captured_args["exclude_extensions"], {".cpp", ".h"})

    def test_exclude_langs_with_whitespace(self):
        """
        Test whitespace handling in --exclude-langs parameter.

        Test Case: CLI filters out empty/whitespace entries from extension list
        Input:
            - CLI args: ['collect_code.py', 'test', '--exclude-langs=py,  , java  ']

        Expected Output:
            - Parsed exclude_extensions={'.py', '.java'} (whitespace-only entries removed)
        """
        with patch("sys.argv", ["collect_code.py", "test", "--exclude-langs=py,  , java  "]):
            with patch("collect_code.Path.is_dir", return_value=True):
                with patch("collect_code.collect_files", return_value=""):
                    with patch("builtins.open", unittest.mock.mock_open()):
                        captured_args = {}

                        def capture_collect(
                            folder_path,
                            exclude_files,
                            exclude_dirs,
                            all_files,
                            include_extensions,
                            exclude_extensions,
                        ):
                            captured_args["exclude_extensions"] = exclude_extensions
                            return ""

                        with patch("collect_code.collect_files", side_effect=capture_collect):
                            collect_code.main()

                        # Should filter out empty/whitespace entries
                        self.assertEqual(captured_args["exclude_extensions"], {".py", ".java"})


class TestIntegration(unittest.TestCase):
    """Integration tests for end-to-end CLI scenarios"""

    def setUp(self):
        """Create a temporary directory structure for integration testing"""
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_path = Path(self.test_dir.name)
        self.output_file = self.test_path / "collected_code.txt"
        self.files = TestFileStructureFixture.create_project_structure(self.test_path)

    def tearDown(self):
        """Clean up temporary directory"""
        self.test_dir.cleanup()

    def test_default_collection(self):
        """
        Test default collection behavior across multiple directories.

        Test Case: End-to-end collection from multiple directories
        Input:
            - CLI: collect-code src/ tests/
            - Directories contain .py, .java, .c, .h files

        Expected Output:
            - Output file created: collected_code.txt
            - Contains all default language files from both directories
        """
        src_dir = str(self.test_path / "src")
        tests_dir = str(self.test_path / "tests")

        with patch("sys.argv", ["collect_code.py", src_dir, tests_dir]):
            with patch("os.getcwd", return_value=str(self.test_path)):
                collect_code.main()

        # Check output file exists
        self.assertTrue(self.output_file.exists())

        # Check content
        content = self.output_file.read_text()
        self.assertIn("main.py", content)
        self.assertIn("App.java", content)
        self.assertIn("util.c", content)
        self.assertIn("util.h", content)
        self.assertIn("test_main.py", content)

    def test_exclude_langs_integration(self):
        """
        Test --exclude-langs flag in real scenario.

        Test Case: Exclude specific languages via CLI
        Input:
            - CLI: collect-code src/ --exclude-langs=java,h
            - Directory contains .py, .java, .c, .h files

        Expected Output:
            - Output contains .py and .c files
            - Output does NOT contain .java and .h files
        """
        src_dir = str(self.test_path / "src")

        with patch("sys.argv", ["collect_code.py", src_dir, "--exclude-langs=java,h"]):
            with patch("os.getcwd", return_value=str(self.test_path)):
                collect_code.main()

        content = self.output_file.read_text()
        self.assertIn("main.py", content)
        self.assertIn("util.c", content)
        self.assertNotIn("App.java", content)
        self.assertNotIn("util.h", content)

    def test_exclude_directory_integration(self):
        """
        Test --exclude flag for directory exclusion.

        Test Case: Exclude specific directories via CLI
        Input:
            - CLI: collect-code project/ --exclude build tests
            - Project contains src/, tests/, build/ directories

        Expected Output:
            - Output contains files from src/
            - Output does NOT contain files from tests/ or build/
        """
        with patch(
            "sys.argv", ["collect_code.py", str(self.test_path), "--exclude", "build", "tests"]
        ):
            with patch("os.getcwd", return_value=str(self.test_path)):
                collect_code.main()

        content = self.output_file.read_text()
        # Should include src files
        self.assertIn("main.py", content)
        # Should not include test or build files
        self.assertNotIn("test_main.py", content)
        self.assertNotIn("output.o", content)

    def test_combined_exclusions(self):
        """
        Test combining --exclude and --exclude-langs flags.

        Test Case: Use both directory and extension exclusions together
        Input:
            - CLI: collect-code project/ --exclude build --exclude-langs=py
            - Project contains .py, .java, .c files in multiple directories

        Expected Output:
            - Output contains .java and .c files
            - Output does NOT contain .py files or files from build/
        """
        with patch(
            "sys.argv",
            ["collect_code.py", str(self.test_path), "--exclude", "build", "--exclude-langs=py"],
        ):
            with patch("os.getcwd", return_value=str(self.test_path)):
                collect_code.main()

        content = self.output_file.read_text()
        # Should include Java and C
        self.assertIn("App.java", content)
        self.assertIn("util.c", content)
        # Should not include Python
        self.assertNotIn("main.py", content)
        self.assertNotIn("test_main.py", content)

    def test_all_files_with_exclusion(self):
        """
        Test --all-files flag with --exclude-langs.

        Test Case: Collect all files except specified extensions
        Input:
            - CLI: collect-code src/ --all-files --exclude-langs=java
            - Directory contains .py, .java, .c, .h, .md files

        Expected Output:
            - Output contains all file types except .java
            - Output includes .py, .c, .h, .md files
        """
        # Add a non-code file
        (self.test_path / "src" / "README.md").write_text("# README")

        with patch(
            "sys.argv",
            ["collect_code.py", str(self.test_path / "src"), "--all-files", "--exclude-langs=java"],
        ):
            with patch("os.getcwd", return_value=str(self.test_path)):
                collect_code.main()

        content = self.output_file.read_text()
        # Should include all files except Java
        self.assertIn("main.py", content)
        self.assertIn("util.c", content)
        self.assertIn("README.md", content)
        self.assertNotIn("App.java", content)


if __name__ == "__main__":
    unittest.main()
