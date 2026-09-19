# Jelon Windows packaging

The release target is Windows 10/11 x64.

## Local build

1. Install .NET 8 SDK, Python 3.11+, PyInstaller, and Inno Setup on the build machine.
2. Publish the desktop shell:

```powershell
dotnet publish desktop/Jelon.Desktop/Jelon.Desktop.csproj -c Release -p:PublishProfile=win-x64
```

3. Package the Python core:

```powershell
powershell -ExecutionPolicy Bypass -File packaging/python/build_core.ps1
```

4. Build the installer with Inno Setup using `packaging/installer/Jelon.iss`.

The resulting installer is `dist/installer/Jelon-Setup.exe`.

## Model policy

The installer does not fabricate or train a model. A compatible local model may be placed in the `models` directory and selected with `JELON_MODEL_PATH`. Large model files should normally be distributed as a separate model pack/release artifact rather than committed to Git.

## Release boundary

The CI package is a Windows x64 release pipeline. Optional AI/voice dependencies remain optional until their native assets are explicitly bundled and tested. This keeps the base installer honest and reproducible.
