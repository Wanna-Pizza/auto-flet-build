# Flet Custom Build

A tool for automating the custom build process of Flet components. The script builds a Flutter application for Windows and then copies all necessary components into a structured output directory.

## Features

- 🚀 Automatic Flutter build for Windows
- 🔍 Verification of all required component paths
- 🧹 Cleaning of the target directory before building
- 📁 Copying of components:
  - Flet core
  - Flet CLI
  - Flet Desktop
  - Flet Web
  - Built Flutter application
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
output_dir = r"OUTPUT_DIRECTORY_PATH"  # Default is "G:\Auto Install Flet_Custom_build\build"
exclusions = ["*.pyc", "*.pdb", "*.log"]  # File exclusion patterns
```

2. Run the script:

```powershell
python custom_build.py
```

3. Monitor the process in the console, which will display:
   - Flutter build status
   - Component path verification
   - File copying progress
   - Final statistics

## Project Structure

The script will create the following structure:

```
build/
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
- Detailed logging of all operations
- Error handling at each build stage
- Final statistics of copied files

## License

MIT
