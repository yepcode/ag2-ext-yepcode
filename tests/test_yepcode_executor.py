"""Unit tests for YepCodeCodeExecutor."""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List

from autogen.coding import CodeBlock, MarkdownCodeExtractor

from ag2_ext_yepcode import YepCodeCodeExecutor, YepCodeCodeResult


class TestYepCodeCodeExecutor:
    """Test suite for YepCodeCodeExecutor."""

    def setup_method(self):
        """Setup method run before each test."""
        # Clear environment variables
        if "YEPCODE_API_TOKEN" in os.environ:
            del os.environ["YEPCODE_API_TOKEN"]

    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeRun")
    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeApiConfig")
    def test_init_with_api_token(self, mock_config, mock_runner):
        """Test initialization with API token provided."""
        mock_config.return_value = Mock()
        mock_runner.return_value = Mock()

        executor = YepCodeCodeExecutor(api_token="test_token")

        assert executor._api_token == "test_token"
        assert executor._timeout == 60
        assert executor._remove_on_done is False
        assert executor._sync_execution is True
        mock_config.assert_called_once_with(api_token="test_token")
        mock_runner.assert_called_once()

    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeRun")
    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeApiConfig")
    def test_init_with_environment_token(self, mock_config, mock_runner):
        """Test initialization with API token from environment."""
        os.environ["YEPCODE_API_TOKEN"] = "env_token"
        mock_config.return_value = Mock()
        mock_runner.return_value = Mock()

        executor = YepCodeCodeExecutor()

        assert executor._api_token == "env_token"
        mock_config.assert_called_once_with(api_token="env_token")

    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeRun")
    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeApiConfig")
    def test_init_with_custom_parameters(self, mock_config, mock_runner):
        """Test initialization with custom parameters."""
        mock_config.return_value = Mock()
        mock_runner.return_value = Mock()

        executor = YepCodeCodeExecutor(
            api_token="test_token",
            timeout=120,
            remove_on_done=True,
            sync_execution=False,
        )

        assert executor._api_token == "test_token"
        assert executor._timeout == 120
        assert executor._remove_on_done is True
        assert executor._sync_execution is False

    @patch("ag2_ext_yepcode._yepcode_executor.load_dotenv")
    def test_init_without_api_token(self, mock_load_dotenv):
        """Test initialization without API token raises ValueError."""
        # Ensure environment variable is not set
        if "YEPCODE_API_TOKEN" in os.environ:
            del os.environ["YEPCODE_API_TOKEN"]

        # Mock dotenv to not load any variables
        mock_load_dotenv.return_value = None

        # Also clear any cached environment that might be loaded by dotenv
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="YepCode API token is required"):
                YepCodeCodeExecutor()

    def test_init_with_invalid_timeout(self):
        """Test initialization with invalid timeout raises ValueError."""
        with pytest.raises(
            ValueError, match="Timeout must be greater than or equal to 1"
        ):
            YepCodeCodeExecutor(api_token="test_token", timeout=0)

    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeRun")
    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeApiConfig")
    def test_init_runner_failure(self, mock_config, mock_runner):
        """Test initialization when YepCodeRun fails."""
        mock_config.return_value = Mock()
        mock_runner.side_effect = Exception("API initialization failed")

        with pytest.raises(RuntimeError, match="Failed to initialize YepCode runner"):
            YepCodeCodeExecutor(api_token="test_token")

    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeRun")
    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeApiConfig")
    def test_code_extractor_property(self, mock_config, mock_runner):
        """Test code_extractor property returns MarkdownCodeExtractor."""
        mock_config.return_value = Mock()
        mock_runner.return_value = Mock()

        executor = YepCodeCodeExecutor(api_token="test_token")

        assert isinstance(executor.code_extractor, MarkdownCodeExtractor)

    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeRun")
    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeApiConfig")
    def test_timeout_property(self, mock_config, mock_runner):
        """Test timeout property."""
        mock_config.return_value = Mock()
        mock_runner.return_value = Mock()

        executor = YepCodeCodeExecutor(api_token="test_token", timeout=120)

        assert executor.timeout == 120

    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeRun")
    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeApiConfig")
    def test_normalize_language(self, mock_config, mock_runner):
        """Test _normalize_language method."""
        mock_config.return_value = Mock()
        mock_runner.return_value = Mock()

        executor = YepCodeCodeExecutor(api_token="test_token")

        assert executor._normalize_language("python") == "python"
        assert executor._normalize_language("py") == "python"
        assert executor._normalize_language("Python") == "python"
        assert executor._normalize_language("javascript") == "javascript"
        assert executor._normalize_language("js") == "javascript"
        assert executor._normalize_language("JavaScript") == "javascript"
        assert executor._normalize_language("java") == "java"  # unsupported

    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeRun")
    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeApiConfig")
    def test_execute_empty_code_blocks(self, mock_config, mock_runner):
        """Test execute_code_blocks with empty list."""
        mock_config.return_value = Mock()
        mock_runner.return_value = Mock()

        executor = YepCodeCodeExecutor(api_token="test_token")
        result = executor.execute_code_blocks([])

        assert result.exit_code == 0
        assert result.output == ""

    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeRun")
    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeApiConfig")
    def test_execute_unsupported_language(self, mock_config, mock_runner):
        """Test execute_code_blocks with unsupported language."""
        mock_config.return_value = Mock()
        mock_runner.return_value = Mock()

        executor = YepCodeCodeExecutor(api_token="test_token")
        code_blocks = [CodeBlock(language="java", code="System.out.println('Hello');")]
        result = executor.execute_code_blocks(code_blocks)

        assert result.exit_code == 1
        assert "Unsupported language: java" in result.output

    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeRun")
    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeApiConfig")
    def test_execute_successful_python_code(self, mock_config, mock_runner):
        """Test successful execution of Python code."""
        mock_config.return_value = Mock()
        mock_runner_instance = Mock()
        mock_runner.return_value = mock_runner_instance

        # Mock execution
        mock_execution = Mock()
        mock_execution.id = "exec_123"
        mock_execution.error = None
        mock_execution.return_value = "Hello, World!"
        mock_execution.logs = [
            Mock(
                timestamp="2023-01-01T00:00:00Z",
                level="INFO",
                message="Starting execution",
            )
        ]
        mock_runner_instance.run.return_value = mock_execution

        executor = YepCodeCodeExecutor(api_token="test_token")
        code_blocks = [CodeBlock(language="python", code="print('Hello, World!')")]
        result = executor.execute_code_blocks(code_blocks)

        assert result.exit_code == 0
        assert "Execution result:\nHello, World!" in result.output
        assert "Execution logs:" in result.output
        assert result.execution_id == "exec_123"

        mock_runner_instance.run.assert_called_once_with(
            "print('Hello, World!')",
            {
                "language": "python",
                "removeOnDone": False,
                "timeout": 60000,
            },
        )
        mock_execution.wait_for_done.assert_called_once()

    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeRun")
    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeApiConfig")
    def test_execute_successful_javascript_code(self, mock_config, mock_runner):
        """Test successful execution of JavaScript code."""
        mock_config.return_value = Mock()
        mock_runner_instance = Mock()
        mock_runner.return_value = mock_runner_instance

        # Mock execution
        mock_execution = Mock()
        mock_execution.id = "exec_456"
        mock_execution.error = None
        mock_execution.return_value = "42"
        mock_execution.logs = []
        mock_runner_instance.run.return_value = mock_execution

        executor = YepCodeCodeExecutor(api_token="test_token")
        code_blocks = [CodeBlock(language="javascript", code="console.log(42);")]
        result = executor.execute_code_blocks(code_blocks)

        assert result.exit_code == 0
        assert "Execution result:\n42" in result.output
        assert result.execution_id == "exec_456"

        mock_runner_instance.run.assert_called_once_with(
            "console.log(42);",
            {
                "language": "javascript",
                "removeOnDone": False,
                "timeout": 60000,
            },
        )

    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeRun")
    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeApiConfig")
    def test_execute_code_with_error(self, mock_config, mock_runner):
        """Test execution with error."""
        mock_config.return_value = Mock()
        mock_runner_instance = Mock()
        mock_runner.return_value = mock_runner_instance

        # Mock execution with error
        mock_execution = Mock()
        mock_execution.id = "exec_error"
        mock_execution.error = "NameError: name 'undefined_var' is not defined"
        mock_execution.logs = [
            Mock(
                timestamp="2023-01-01T00:00:00Z",
                level="ERROR",
                message="Execution failed",
            )
        ]
        mock_runner_instance.run.return_value = mock_execution

        executor = YepCodeCodeExecutor(api_token="test_token")
        code_blocks = [CodeBlock(language="python", code="print(undefined_var)")]
        result = executor.execute_code_blocks(code_blocks)

        assert result.exit_code == 1
        assert "Execution failed with error:" in result.output
        assert "NameError: name 'undefined_var' is not defined" in result.output
        assert result.execution_id == "exec_error"

    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeRun")
    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeApiConfig")
    def test_execute_multiple_code_blocks(self, mock_config, mock_runner):
        """Test execution of multiple code blocks."""
        mock_config.return_value = Mock()
        mock_runner_instance = Mock()
        mock_runner.return_value = mock_runner_instance

        # Mock two executions
        mock_execution1 = Mock()
        mock_execution1.id = "exec_1"
        mock_execution1.error = None
        mock_execution1.return_value = "First result"
        mock_execution1.logs = []

        mock_execution2 = Mock()
        mock_execution2.id = "exec_2"
        mock_execution2.error = None
        mock_execution2.return_value = "Second result"
        mock_execution2.logs = []

        mock_runner_instance.run.side_effect = [mock_execution1, mock_execution2]

        executor = YepCodeCodeExecutor(api_token="test_token")
        code_blocks = [
            CodeBlock(language="python", code="print('First')"),
            CodeBlock(language="javascript", code="console.log('Second')"),
        ]
        result = executor.execute_code_blocks(code_blocks)

        assert result.exit_code == 0
        assert "First result" in result.output
        assert "Second result" in result.output
        assert "===" in result.output  # Separator between outputs
        assert result.execution_id == "exec_2"  # Last execution ID

        assert mock_runner_instance.run.call_count == 2

    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeRun")
    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeApiConfig")
    def test_execute_async_execution(self, mock_config, mock_runner):
        """Test asynchronous execution."""
        mock_config.return_value = Mock()
        mock_runner_instance = Mock()
        mock_runner.return_value = mock_runner_instance

        # Mock execution
        mock_execution = Mock()
        mock_execution.id = "exec_async"
        mock_runner_instance.run.return_value = mock_execution

        executor = YepCodeCodeExecutor(api_token="test_token", sync_execution=False)
        code_blocks = [CodeBlock(language="python", code="print('Hello')")]
        result = executor.execute_code_blocks(code_blocks)

        assert result.exit_code == 0
        assert "Execution started with ID: exec_async" in result.output
        assert result.execution_id == "exec_async"

        # Should not call wait_for_done in async mode
        mock_execution.wait_for_done.assert_not_called()

    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeRun")
    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeApiConfig")
    def test_execute_runtime_exception(self, mock_config, mock_runner):
        """Test execution with runtime exception."""
        mock_config.return_value = Mock()
        mock_runner_instance = Mock()
        mock_runner.return_value = mock_runner_instance

        # Mock runtime exception
        mock_runner_instance.run.side_effect = Exception("Runtime error")

        executor = YepCodeCodeExecutor(api_token="test_token")
        code_blocks = [CodeBlock(language="python", code="print('Hello')")]
        result = executor.execute_code_blocks(code_blocks)

        assert result.exit_code == 1
        assert "Error executing code: Runtime error" in result.output

    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeRun")
    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeApiConfig")
    def test_execute_with_custom_timeout(self, mock_config, mock_runner):
        """Test execution with custom timeout."""
        mock_config.return_value = Mock()
        mock_runner_instance = Mock()
        mock_runner.return_value = mock_runner_instance

        # Mock execution
        mock_execution = Mock()
        mock_execution.id = "exec_timeout"
        mock_execution.error = None
        mock_execution.return_value = "Result"
        mock_execution.logs = []
        mock_runner_instance.run.return_value = mock_execution

        executor = YepCodeCodeExecutor(api_token="test_token", timeout=120)
        code_blocks = [CodeBlock(language="python", code="print('Hello')")]
        result = executor.execute_code_blocks(code_blocks)

        assert result.exit_code == 0

        # Check that timeout was converted to milliseconds
        mock_runner_instance.run.assert_called_once_with(
            "print('Hello')",
            {
                "language": "python",
                "removeOnDone": False,
                "timeout": 120000,  # 120 seconds * 1000
            },
        )

    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeRun")
    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeApiConfig")
    def test_execute_with_remove_on_done(self, mock_config, mock_runner):
        """Test execution with remove_on_done enabled."""
        mock_config.return_value = Mock()
        mock_runner_instance = Mock()
        mock_runner.return_value = mock_runner_instance

        # Mock execution
        mock_execution = Mock()
        mock_execution.id = "exec_remove"
        mock_execution.error = None
        mock_execution.return_value = "Result"
        mock_execution.logs = []
        mock_runner_instance.run.return_value = mock_execution

        executor = YepCodeCodeExecutor(api_token="test_token", remove_on_done=True)
        code_blocks = [CodeBlock(language="python", code="print('Hello')")]
        result = executor.execute_code_blocks(code_blocks)

        assert result.exit_code == 0

        # Check that removeOnDone was set to True
        mock_runner_instance.run.assert_called_once_with(
            "print('Hello')",
            {
                "language": "python",
                "removeOnDone": True,
                "timeout": 60000,
            },
        )

    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeRun")
    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeApiConfig")
    def test_restart_method(self, mock_config, mock_runner):
        """Test restart method (currently a no-op)."""
        mock_config.return_value = Mock()
        mock_runner.return_value = Mock()

        executor = YepCodeCodeExecutor(api_token="test_token")

        # Should not raise any exception
        executor.restart()

    @patch("ag2_ext_yepcode._yepcode_executor.load_dotenv")
    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeRun")
    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeApiConfig")
    def test_dotenv_loading(self, mock_config, mock_runner, mock_load_dotenv):
        """Test that dotenv is loaded when available."""
        mock_config.return_value = Mock()
        mock_runner.return_value = Mock()

        executor = YepCodeCodeExecutor(api_token="test_token")

        mock_load_dotenv.assert_called_once()

    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeRun")
    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeApiConfig")
    def test_execute_no_return_value(self, mock_config, mock_runner):
        """Test execution with no return value."""
        mock_config.return_value = Mock()
        mock_runner_instance = Mock()
        mock_runner.return_value = mock_runner_instance

        # Mock execution with no return value
        mock_execution = Mock()
        mock_execution.id = "exec_no_return"
        mock_execution.error = None
        mock_execution.return_value = None
        mock_execution.logs = []
        mock_runner_instance.run.return_value = mock_execution

        executor = YepCodeCodeExecutor(api_token="test_token")
        code_blocks = [CodeBlock(language="python", code="x = 1")]
        result = executor.execute_code_blocks(code_blocks)

        assert result.exit_code == 0
        assert result.output == ""  # No return value and no logs means empty output
        assert result.execution_id == "exec_no_return"

    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeRun")
    @patch("ag2_ext_yepcode._yepcode_executor.YepCodeApiConfig")
    def test_execute_no_return_value_with_logs(self, mock_config, mock_runner):
        """Test execution with no return value but with logs."""
        mock_config.return_value = Mock()
        mock_runner_instance = Mock()
        mock_runner.return_value = mock_runner_instance

        # Mock execution with no return value but with logs
        mock_execution = Mock()
        mock_execution.id = "exec_no_return_logs"
        mock_execution.error = None
        mock_execution.return_value = None
        mock_execution.logs = [
            Mock(
                timestamp="2023-01-01T00:00:00Z",
                level="INFO",
                message="Some log message",
            )
        ]
        mock_runner_instance.run.return_value = mock_execution

        executor = YepCodeCodeExecutor(api_token="test_token")
        code_blocks = [CodeBlock(language="python", code="x = 1")]
        result = executor.execute_code_blocks(code_blocks)

        assert result.exit_code == 0
        assert "Execution logs:" in result.output
        assert "Some log message" in result.output
        assert result.execution_id == "exec_no_return_logs"


class TestYepCodeCodeResult:
    """Test suite for YepCodeCodeResult."""

    def test_code_result_creation(self):
        """Test YepCodeCodeResult creation."""
        result = YepCodeCodeResult(
            exit_code=0, output="Test output", execution_id="exec_123"
        )

        assert result.exit_code == 0
        assert result.output == "Test output"
        assert result.execution_id == "exec_123"

    def test_code_result_without_execution_id(self):
        """Test YepCodeCodeResult creation without execution_id."""
        result = YepCodeCodeResult(exit_code=1, output="Error output")

        assert result.exit_code == 1
        assert result.output == "Error output"
        assert result.execution_id is None
