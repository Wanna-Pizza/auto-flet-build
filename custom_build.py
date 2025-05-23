import os
import shutil
import fnmatch
import subprocess
import time
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich import print as rprint

class FileOperations:
    def __init__(self, source_path=None, output_path=None):
        self.source_path = Path(source_path) if source_path else None
        self.output_path = Path(output_path) if output_path else None
        self.last_operation_count = 0
        self.console = Console()

    def copy_files_with_exclusions(self, source_dir, dest_dir, exclusions=None):
        exclusions = exclusions or []
        
        source_path = Path(source_dir)
        dest_path = Path(dest_dir)
        
        if not source_path.exists() or not source_path.is_dir():
            raise ValueError(f"Source directory {source_dir} does not exist")
        
        os.makedirs(dest_path, exist_ok=True)
        copied_count = 0
        
        for root, dirs, files in os.walk(source_path):
            rel_path = os.path.relpath(root, source_path)
            dest_root = dest_path / rel_path if rel_path != '.' else dest_path
            os.makedirs(dest_root, exist_ok=True)
            
            for file in files:
                if any(fnmatch.fnmatch(file, pattern) for pattern in exclusions):
                    continue
                
                source_file = Path(root) / file
                dest_file = dest_root / file
                shutil.copy2(source_file, dest_file)
                copied_count += 1
        
        return copied_count

    def copy_folder(self, source_dir, dest_dir, exclude_patterns=None):
        exclude_patterns = exclude_patterns or []
        
        source_path = Path(source_dir)
        dest_path = Path(dest_dir)
        
        if not source_path.exists() or not source_path.is_dir():
            self.console.print(f"[red]Error: Source directory {source_dir} does not exist[/red]")
            return 0
        
        # Create destination directory if it doesn't exist
        try:
            os.makedirs(dest_path, exist_ok=True)
        except Exception as e:
            self.console.print(f"[red]Error creating destination directory {dest_path}: {e}[/red]")
            return 0
        
        # Extract the folder name from source path
        folder_name = source_path.name
        target_dir = dest_path / folder_name
        
        # Create target directory
        os.makedirs(target_dir, exist_ok=True)
        
        # Track statistics
        copied_count = 0
        skipped_count = 0
        
        # Process all files and subdirectories
        for root, dirs, files in os.walk(source_path):
            rel_path = os.path.relpath(root, source_path)
            target_path = target_dir / rel_path if rel_path != '.' else target_dir
            
            os.makedirs(target_path, exist_ok=True)
            
            # Process files in current directory
            for file in files:
                # Check exclusion patterns
                if any(fnmatch.fnmatch(file, pattern) for pattern in exclude_patterns):
                    skipped_count += 1
                    continue
                
                source_file = Path(root) / file
                dest_file = target_path / file
                
                try:
                    shutil.copy2(source_file, dest_file)
                    copied_count += 1
                except Exception as e:
                    self.console.print(f"[yellow]Warning: Failed to copy {source_file}: {e}[/yellow]")
        
        self.console.print(f"[green]✓ {folder_name}[/green] [dim]({copied_count} files)[/dim]")
            
        return copied_count

    def clear_directory(self, directory_path):
        dir_path = Path(directory_path)
        
        if not dir_path.exists():
            self.console.print(f"[yellow]Warning: Directory {directory_path} does not exist[/yellow]")
            return 0
            
        if not dir_path.is_dir():
            self.console.print(f"[red]Error: {directory_path} is not a directory[/red]")
            return 0
            
        removed_count = 0
        item_count = sum(1 for _ in dir_path.glob('**/*'))
        
        if item_count == 0:
            return 0
        
        self.console.print(f"[blue]Clearing directory...[/blue]", end="")
        
        has_errors = False
        for item in dir_path.iterdir():
            try:
                if item.is_file() or item.is_symlink():
                    item.unlink()
                    removed_count += 1
                elif item.is_dir():
                    shutil.rmtree(item)
                    removed_count += 1
            except Exception as e:
                has_errors = True
                self.console.print("")  # New line before error
                self.console.print(f"[red]Error removing {item}: {e}[/red]")
        
        if not has_errors:
            self.console.print(f"\r[green]✓ Cleared {directory_path} [dim]({removed_count} items)[/dim]")
                
        return removed_count

    def run_flutter_build(self, source_path, flutter_path=None):
        """Run Flutter build windows command in the client directory"""
        client_path = os.path.join(source_path, "client")
        
        if not os.path.exists(client_path):
            self.console.print(f"[red]Error: Client directory not found at {client_path}[/red]")
            return False
            
        self.console.print(f"\n[bold blue]Starting Flutter build in {client_path}[/bold blue]")
        
        try:
            flutter_result = subprocess.run(['where', 'flutter'], 
                                           capture_output=True, 
                                           text=True, 
                                           check=False)
            
            if flutter_result.returncode != 0:
                self.console.print("[red]Error: Flutter not found in PATH. Please install Flutter or add it to PATH.[/red]")
                return False
                
            flutter_paths = flutter_result.stdout.strip().split('\n')
            flutter_exe = None
            
            for path in flutter_paths:
                if path.endswith('.bat'):
                    flutter_exe = path
                    break
            
            if not flutter_exe:
                # If no .bat file found but flutter exists, use the first path
                flutter_exe = flutter_paths[0]
                
            self.console.print(f"[green]Found Flutter: {flutter_exe}[/green]")
            
        except Exception as e:
            self.console.print(f"[red]Error detecting Flutter: {str(e)}[/red]")
            return False
            
        command = [flutter_exe, "build", "windows"]
        self.console.print(f"[cyan]Running command: {' '.join(command)}[/cyan]")
        
        # Setup rich progress display
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("[bold cyan]{task.fields[status]}"),
            TimeElapsedColumn(),
            console=self.console
        ) as progress:
            build_task = progress.add_task("[bold]Building Flutter application...", total=None, status="Starting")
            
            try:
                # Run the process and capture output
                process = subprocess.Popen(
                    command,
                    cwd=client_path,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                
                # Update progress with output
                for line in iter(process.stdout.readline, ''):
                    # Update status with latest output
                    progress.update(build_task, status=line.strip())
                
                # Wait for process to complete
                exit_code = process.wait()
                
                if exit_code == 0:
                    progress.update(build_task, status="Completed successfully")
                    progress.stop()
                    
                    self.console.print("\n")
                    self.console.print(Panel.fit(
                        "[bold green]Flutter build completed successfully![/bold green]",
                        title="BUILD SUCCESS",
                        border_style="green",
                        padding=(1, 2)
                    ))
                    return True
                else:
                    progress.update(build_task, status=f"Failed with exit code {exit_code}")
                    self.console.print(f"\n[bold red]Flutter build failed with exit code {exit_code}[/bold red]")
                    return False
                    
            except Exception as e:
                progress.update(build_task, status=f"Error: {str(e)}")
                self.console.print(f"\n[bold red]Error running Flutter build: {str(e)}[/bold red]")
                return False

def initialize_paths(base_path):
    path_components = {
        "packages": ["sdk", "python", "packages"],
        "flet": ["flet", "src", "flet"],
        "flet_cli": ["flet-cli", "src", "flet_cli"],
        "flet_desktop": ["flet-desktop", "src", "flet_desktop"],
        "flet_web": ["flet-web", "src", "flet_web"],
        "desktop_app": ["client", "build", "windows", "x64", "runner", "Release"]
    }
    
    paths = {}
    paths["flet"] = os.path.join(base_path, *path_components["packages"], *path_components["flet"])
    paths["flet_cli"] = os.path.join(base_path, *path_components["packages"], *path_components["flet_cli"])
    paths["flet_desktop"] = os.path.join(base_path, *path_components["packages"], *path_components["flet_desktop"])
    paths["flet_web"] = os.path.join(base_path, *path_components["packages"], *path_components["flet_web"])
    paths["desktop_app"] = os.path.join(base_path, *path_components["desktop_app"])
    
    return paths

def display_paths(paths):
    console = Console()
    
    table = Table(title="Flet Project Paths", show_header=True)
    table.add_column("Component", style="cyan")
    table.add_column("Path", style="green")
    
    for name, path in paths.items():
        table.add_row(name.replace("_", " ").title(), path)
    
    console.print(table)
    return console

def verify_paths(paths):
    console = Console()
    console.print("\n[bold]Path Verification[/bold]")
    
    all_paths_exist = True
    for name, path in paths.items():
        if os.path.exists(path):
            console.print(f"✅ [green]{name}: {path}[/green]")
        else:
            console.print(f"❌ [red]{name}: {path} does not exist[/red]")
            all_paths_exist = False
    
    if not all_paths_exist:
        console.print("\n[bold red]Error:[/bold red] Some paths do not exist.")
    else:
        console.print("\n[bold green]All paths exist. Ready to proceed.[/bold green]")
        
    return all_paths_exist, console

def copy_flet_components(file_ops, source_paths, output_dir, exclusions=None):
    console = Console()
    console.print("\n[bold cyan]━━━ Copying Flet Components ━━━[/bold cyan]")
    
    exclusions = exclusions or ["*.pyc", "*.pdb", "*.log"]
    copied_counts = {}
    
    # Only clear specific component directories
    for name in ["flet", "flet_cli", "flet_desktop", "flet_web"]:
        component_dir = os.path.join(output_dir, name)
        if os.path.exists(component_dir):
            console.print(f"[blue]Clearing {name} directory...[/blue]")
            file_ops.clear_directory(component_dir)
    
    # Copy components (excluding desktop app)
    for name, path in source_paths.items():
        if name != "desktop_app":
            copied_counts[name] = file_ops.copy_folder(path, output_dir, exclusions)
    
    total_copied = sum(copied_counts.values())
    console.print(f"[dim]Total: {total_copied} files[/dim]")
    
    return copied_counts, console

def copy_desktop_app(file_ops, desktop_app_path, output_dir, exclusions=None):
    console = Console()
    console.print("\n[bold cyan]━━━ Copying Desktop Application ━━━[/bold cyan]")
    
    exclusions = exclusions or ["*.pyc", "*.pdb", "*.log"]
    app_target_path = os.path.join(output_dir, "flet_desktop", "app", "flet")
    
    # Create target directory
    os.makedirs(app_target_path, exist_ok=True)
    
    # Copy files
    copied = file_ops.copy_files_with_exclusions(desktop_app_path, app_target_path, exclusions)
    console.print(f"[green]✓ Desktop app[/green] [dim]({copied} files)[/dim]")
    
    return copied, console

def install_msgpack(output_dir):
    """Install msgpack using pip if target directory is a site-packages directory"""
    console = Console()
    
    # Check if target directory is a site-packages directory
    if "site-packages" in output_dir:
        console.print("\n[bold cyan]━━━ Installing msgpack Package ━━━[/bold cyan]")
        
        # Prepare pip command with target directory
        target_dir = output_dir
        pip_cmd = ["pip", "install", "msgpack", "-t", target_dir, "--upgrade", "--no-dependencies"]
        
        console.print(f"[cyan]Running command: {' '.join(pip_cmd)}[/cyan]")
        
        # Setup rich progress display
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("[bold cyan]{task.fields[status]}"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            install_task = progress.add_task("[bold]Installing msgpack...", total=None, status="Starting")
            
            try:
                # Run the pip process
                process = subprocess.Popen(
                    pip_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                
                # Update progress with output
                for line in iter(process.stdout.readline, ''):
                    progress.update(install_task, status=line.strip())
                
                # Wait for process to complete
                exit_code = process.wait()
                
                if exit_code == 0:
                    progress.update(install_task, status="Completed successfully")
                    progress.stop()
                    
                    console.print(f"[green]✓ msgpack installed to {target_dir}[/green]")
                    return 1  # Count as 1 operation
                else:
                    progress.update(install_task, status=f"Failed with exit code {exit_code}")
                    console.print(f"[red]Failed to install msgpack with exit code {exit_code}[/red]")
                    return 0
                    
            except Exception as e:
                progress.update(install_task, status=f"Error: {str(e)}")
                console.print(f"[red]Error installing msgpack: {str(e)}[/red]")
                return 0
    
    return 0

def run_build(source_path, output_dirs, exclusions):
        if not isinstance(output_dirs, list):
            output_dirs = [output_dirs]  # Convert single path to list

        file_ops = FileOperations(source_path)
        console = Console()
        
        console.print(Panel.fit(
            "[bold]Flet Custom Build[/bold]",
            border_style="cyan",
            padding=(1, 10)
        ))
        
        # Run Flutter build before copying files (only once)
        build_successful = file_ops.run_flutter_build(source_path)
        
        if not build_successful:
            console.print("[bold red]Flutter build failed. Exiting...[/bold red]")
            return 1
        
        # Process paths (only once)
        paths = initialize_paths(source_path)
        paths_valid, _ = verify_paths(paths)
        
        if not paths_valid:
            console.print("[bold red]Exiting due to missing paths.[/bold red]")
            return 1
        
        # Copy files to each output directory
        total_results = []
        for output_dir in output_dirs:
            console.print(f"\n[bold blue]Processing output directory: {output_dir}[/bold blue]")
              # Execute file operations for this output directory
            copy_results, _ = copy_flet_components(file_ops, paths, output_dir, exclusions)
            desktop_app_copied, _ = copy_desktop_app(file_ops, paths["desktop_app"], output_dir, exclusions)
            
            # Install msgpack if output is a site-packages directory
            msgpack_installed = install_msgpack(output_dir)
            
            # Add results to totals
            total_files = sum(copy_results.values()) + desktop_app_copied + msgpack_installed
            total_results.append({
                "dir": output_dir,
                "files": total_files
            })
        
        # Summary of all operations
        console.print("\n")
        success_panel = f"[bold green]Build completed successfully![/bold green]\n\n"
        
        # Add details for each output directory
        for result in total_results:
            success_panel += f"[white]{result['dir']}: {result['files']} files[/white]\n"
        
        console.print(Panel.fit(
            success_panel,
            title="SUCCESS",
            border_style="green",
            padding=(1, 10)
        ))
        
        return 0

def main():
    source_path = r"H:\Flutter\flet-v1"
    
    # Multiple output directories
    output_dirs = [
        r"G:\Folder\venv\Lib\site-packages",
        # Add more output directories here as needed
        # r"C:\Another\Output\Directory",
    ]
    
    exclusions = ["*.pyc", "*.pdb", "*.log"]

    run_build(source_path, output_dirs, exclusions)


if __name__ == "__main__":
    exit(main())
