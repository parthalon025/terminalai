# VHS Upscaler Test Suite

Comprehensive test suite for the VHS Upscaler new features including deinterlacing, preset comparison, dry-run mode, and parallel batch processing.

## Test Structure

```
tests/
├── conftest.py                      # Shared fixtures and configuration
├── test_deinterlace_integration.py  # Deinterlacing module tests
├── test_comparison.py               # Preset comparison tests
├── test_dry_run.py                  # Dry-run mode tests
├── test_batch_parallel.py           # Parallel batch processing tests
├── test_gui_helpers.py              # GUI helper tests (existing)
├── test_gui_integration.py          # GUI integration tests (existing)
└── test_queue_manager.py            # Queue manager tests (existing)
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_deinterlace_integration.py
pytest tests/test_comparison.py
pytest tests/test_dry_run.py
pytest tests/test_batch_parallel.py
```

### Run Specific Test Class

```bash
pytest tests/test_deinterlace_integration.py::TestDeinterlaceEngine
pytest tests/test_comparison.py::TestPresetComparator
```

### Run Specific Test

```bash
pytest tests/test_deinterlace_integration.py::TestDeinterlaceEngine::test_engine_values
```

### Run with Coverage

```bash
pytest --cov=vhs_upscaler --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html`.

### Run with Verbose Output

```bash
pytest -v
```

### Run Only Fast Tests

```bash
pytest -m "not slow"
```

### Run Only Integration Tests

```bash
pytest -m integration
```

## Test Categories

### Unit Tests (Fast)
- **test_deinterlace_integration.py**:
  - Engine initialization
  - Configuration validation
  - FFmpeg filter generation
  - VapourSynth integration

- **test_comparison.py**:
  - ComparisonConfig validation
  - PresetComparator initialization
  - Output path generation
  - Report generation

- **test_dry_run.py**:
  - Pipeline visualization
  - Configuration validation
  - Warning detection
  - Command generation

- **test_batch_parallel.py**:
  - Video discovery
  - Path generation
  - Config loading
  - Job filtering

### Integration Tests (Slower)
- **test_deinterlace_integration.py**:
  - FFmpeg command execution (mocked)
  - QTGMC script generation
  - VHSUpscaler integration

- **test_comparison.py**:
  - Clip extraction workflow
  - Preset processing pipeline
  - Grid generation workflow

- **test_batch_parallel.py**:
  - Sequential processing
  - Parallel processing
  - Error handling

## Test Coverage

### test_deinterlace_integration.py (400+ lines)

**Coverage Areas:**
- DeinterlaceEngine enum (4 engines)
- DeinterlaceProcessor initialization
- FFmpeg-based deinterlacing (yadif, bwdif, w3fdif)
- QTGMC deinterlacing via VapourSynth
- Engine fallback behavior
- ProcessingConfig integration
- VHSUpscaler integration
- Error handling
- Field order detection

**Test Classes:**
- `TestDeinterlaceEngine` - Enum validation
- `TestDeinterlaceProcessorInit` - Initialization and fallback
- `TestFFmpegDeinterlacing` - FFmpeg filters
- `TestQTGMCDeinterlacing` - VapourSynth QTGMC
- `TestProcessingConfigIntegration` - Config integration
- `TestVHSUpscalerIntegration` - Upscaler integration
- `TestErrorHandling` - Error scenarios
- `TestFieldOrder` - Field order handling
- `TestQualityComparison` - Quality ranking

### test_comparison.py (500+ lines)

**Coverage Areas:**
- ComparisonConfig dataclass
- PresetComparator initialization
- Test clip extraction
- Video duration extraction
- Preset processing pipeline
- Grid generation (horizontal/vertical stacks)
- Comparison report generation
- FFmpeg command construction
- Error handling

**Test Classes:**
- `TestComparisonConfig` - Config validation
- `TestPresetComparatorInit` - Initialization
- `TestClipExtraction` - Clip extraction
- `TestPresetProcessing` - Preset processing
- `TestGridGeneration` - Grid creation
- `TestVideoInfo` - Video metadata
- `TestReportGeneration` - Report creation
- `TestComparisonSuite` - Full suite
- `TestConvenienceFunction` - Helper functions
- `TestEdgeCases` - Edge cases

### test_dry_run.py (550+ lines)

**Coverage Areas:**
- DryRunVisualizer initialization
- Pipeline visualization output
- I/O information display
- Video analysis display
- Preprocessing stage info
- Upscaling stage info
- Postprocessing stage info
- FFmpeg command generation
- Configuration validation
- Warning detection

**Test Classes:**
- `TestDryRunVisualizerInit` - Initialization
- `TestPipelineVisualization` - Output format
- `TestIOInfo` - Input/output display
- `TestVideoInfo` - Video analysis
- `TestPreprocessingStage` - Preprocessing info
- `TestUpscalingStage` - Upscaling info
- `TestPostprocessingStage` - Postprocessing info
- `TestFFmpegCommands` - Command generation
- `TestConfigurationValidation` - Config validation
- `TestGetVideoInfo` - Metadata extraction
- `TestConvenienceFunction` - Helper functions
- `TestEdgeCases` - Edge cases

### test_batch_parallel.py (600+ lines)

**Coverage Areas:**
- Video file discovery
- Output path generation
- Sequential batch processing
- Parallel batch processing
- Job filtering (skip existing, resume)
- Dry-run mode
- Max count limiting
- Config file loading
- Error handling
- Statistics tracking

**Test Classes:**
- `TestVideoDiscovery` - File discovery
- `TestOutputPathGeneration` - Path generation
- `TestSequentialProcessing` - Sequential mode
- `TestParallelProcessing` - Parallel mode
- `TestJobFiltering` - Filtering logic
- `TestDryRun` - Dry-run mode
- `TestMaxCount` - Count limiting
- `TestConfigLoading` - Config loading
- `TestErrorHandling` - Error scenarios
- `TestBatchStatistics` - Statistics
- `TestParserSetup` - Argument parsing
- `TestVideoExtensions` - Extension handling

## Shared Fixtures (conftest.py)

### Path Fixtures
- `temp_dir` - Temporary directory for test files
- `sample_video_path` - Mock video file path
- `sample_videos` - Multiple video files

### Mock Fixtures
- `mock_queue` - Mock VideoQueue instance
- `mock_app_state` - Mock GUI application state
- `processing_config` - ProcessingConfig instance
- `mock_subprocess_run` - Mock subprocess.run
- `mock_video_info` - Mock video metadata

### Job Fixtures
- `sample_job` - Sample pending job
- `completed_job` - Sample completed job

## Writing New Tests

### Test Structure Template

```python
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

class TestMyFeature:
    """Test my new feature."""

    def test_basic_functionality(self):
        """Test basic functionality works."""
        # Arrange
        expected = "result"

        # Act
        result = my_function()

        # Assert
        assert result == expected

    def test_error_handling(self):
        """Test error handling."""
        with pytest.raises(ValueError):
            my_function(invalid_input)

    @patch('module.external_dependency')
    def test_with_mock(self, mock_dep):
        """Test with mocked dependency."""
        mock_dep.return_value = "mocked"

        result = my_function()

        assert mock_dep.called
        assert result == "mocked"

    def test_with_fixture(self, temp_dir):
        """Test using shared fixture."""
        file_path = temp_dir / "test.txt"
        file_path.write_text("content")

        assert file_path.exists()
```

### Best Practices

1. **Use descriptive test names**: Test name should describe what is being tested
2. **One assertion per test**: Keep tests focused and simple
3. **Use fixtures**: Leverage shared fixtures from conftest.py
4. **Mock external dependencies**: Don't rely on FFmpeg, VapourSynth, etc.
5. **Test both success and failure**: Include error handling tests
6. **Use parametrize**: Test multiple scenarios with @pytest.mark.parametrize
7. **Add docstrings**: Explain what each test validates

### Example: Parametrized Test

```python
@pytest.mark.parametrize("engine,expected_filter", [
    ("yadif", "yadif=1"),
    ("bwdif", "bwdif=1"),
    ("w3fdif", "w3fdif"),
])
def test_deinterlace_filters(self, engine, expected_filter):
    """Test deinterlace filter generation for each engine."""
    processor = DeinterlaceProcessor(engine)
    filter_str = processor.get_filter()
    assert expected_filter in filter_str
```

## Continuous Integration

These tests are designed to run in CI/CD environments:

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11

    - name: Install dependencies
      run: |
        pip install -e .[dev]

    - name: Run tests
      run: |
        pytest --cov=vhs_upscaler --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

## Troubleshooting

### Tests Failing on Import

**Problem**: Import errors when running tests

**Solution**: Install package in development mode:
```bash
pip install -e .
```

### Mock Not Working

**Problem**: External dependencies being called

**Solution**: Ensure mocks are patched at the correct location:
```python
# Wrong: patches where it's defined
@patch('subprocess.run')

# Right: patches where it's used
@patch('vhs_upscaler.deinterlace.subprocess.run')
```

### Fixtures Not Found

**Problem**: pytest can't find fixtures

**Solution**: Ensure conftest.py is in tests/ directory and fixtures are properly defined

### Slow Tests

**Problem**: Tests taking too long

**Solution**: Use mocks for external processes, mark slow tests:
```python
@pytest.mark.slow
def test_slow_operation():
    pass
```

Then skip slow tests: `pytest -m "not slow"`

## Test Metrics

Current test suite statistics:
- **Total test files**: 7
- **Total test classes**: 40+
- **Total test functions**: 150+
- **Lines of test code**: 2500+
- **Expected coverage**: >80%
- **Execution time**: <30s (with mocks)

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure >80% code coverage
3. Include both success and failure cases
4. Mock external dependencies
5. Add docstrings to test functions
6. Update this README if adding new test files

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [Unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [Coverage.py](https://coverage.readthedocs.io/)
