# Jelon Desktop

Windows desktop shell for Jelon.

## Target

- Windows 10/11
- 64-bit recommended
- .NET 8 SDK
- Python runtime available during development

## Run from the repository root

```bash
dotnet run --project desktop/Jelon.Desktop/Jelon.Desktop.csproj
```

The desktop shell starts `python -m engine.desktop_server` and communicates with the Python core using JSON Lines over stdin/stdout.

The release installer will later replace this development Python dependency with a bundled Jelon runtime.
