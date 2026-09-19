#define AppName "Jelon"
#define AppVersion "0.1.0"
#define AppPublisher "Jelon"
#define AppExeName "Jelon.Desktop.exe"

[Setup]
AppId={{8B0D4A3B-2F36-4A5B-9C4E-JELON00000001}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\Jelon
DefaultGroupName=Jelon
OutputDir=..\..\dist\installer
OutputBaseFilename=Jelon-Setup
ArchitecturesInstallIn64BitMode=x64
ArchitecturesAllowed=x64
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Files]
Source: "..\..\dist\desktop\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion
Source: "..\..\dist\core\*"; DestDir: "{app}\core"; Flags: recursesubdirs ignoreversion
Source: "..\..\models\*"; DestDir: "{app}\models"; Flags: recursesubdirs ignoreversion skipifsourcedoesntexist
Source: "..\..\skills\*"; DestDir: "{app}\skills"; Flags: recursesubdirs ignoreversion skipifsourcedoesntexist

[Dirs]
Name: "{localappdata}\Jelon\data"
Name: "{localappdata}\Jelon\config"

[Icons]
Name: "{autoprograms}\Jelon"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\Jelon"; Filename: "{app}\{#AppExeName}"

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Launch Jelon"; Flags: nowait postinstall skipifsilent
