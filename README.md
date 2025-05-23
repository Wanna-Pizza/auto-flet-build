# Flet Custom Build

A tool for automating the custom build process of Flet components. The script builds a Flutter application for Windows and then copies all necessary components into one or multiple structured output directories.

## Features

- 🚀 Automatic Flutter build for Windows
- 🔍 Verification of all required component paths
- 🧹 Cleaning of specific component directories before copying
- 📁 Copying of components:
  - Flet core
  - Flet CLI
  - Flet Desktop
  - Flet Web
  - Built Flutter application
- 📦 Automatic installation of msgpack package in site-packages directories
- 🔀 Support for multiple output directories in a single run
- 🔒 Support for file exclusions (default: `*.pyc`, `*.pdb`, `*.log`)
- 🎨 Beautiful console output formatting using Rich

## Requirements

- Python 3.8+
- Windows
- Flutter SDK in PATH
- Rich (`pip install rich`)

## Usage

1. Configure paths in `custom_build.py`:

```python
source_path = r"PATH_TO_FLET_SOURCE"  # Default is "H:\Flutter\flet-v1"

# Multiple output directories
output_dirs = [
    r"PATH_TO_FIRST_OUTPUT_DIRECTORY",  # e.g., "G:\Project\venv\Lib\site-packages"
    # Add more output directories here as needed
    # r"PATH_TO_SECOND_OUTPUT_DIRECTORY",
]

exclusions = ["*.pyc", "*.pdb", "*.log"]  # File exclusion patterns
```

2. Run the script:

```powershell
python custom_build.py
```

3. Monitor the process in the console, which will display:
   - Flutter build status
   - Component path verification
   - File copying progress for each output directory
   - Automatic msgpack installation for site-packages directories
   - Final statistics for all output directories

## Project Structure

For each output directory, the script will create the following structure:

```
output_directory/
├── flet/
├── flet_cli/
├── flet_desktop/
│   └── app/
│       └── flet/
└── flet_web/
```

## Implementation Details

- Automatic detection of Flutter path using `where flutter`
- Display of Flutter build progress with current status
- Selective cleaning of component directories only
- Parallel processing of multiple output directories after a single build
- Automatic installation of msgpack package in site-packages directories using pip
- Detailed logging of all operations
- Error handling at each build stage
- Final statistics of copied files for each output directory

## License

MIT
