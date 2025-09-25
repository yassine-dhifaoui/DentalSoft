; ————————————————
; DentalSoft.iss
; ————————————————

[Setup]
AppName=DentalSoft
AppVersion=1.0
; Installation dans Program Files (x86 sur 32-bit, Program Files sur 64-bit)
DefaultDirName={commonpf}\DentalSoft
DefaultGroupName=DentalSoft
AllowNoIcons=yes
OutputDir=.
OutputBaseFilename=DentalSoft_Installer
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Files]
; Exécutable généré par PyInstaller
Source: "dist\DentalSoft.exe"; DestDir: "{app}"; Flags: ignoreversion
; Tous vos assets (icônes, splash…) copiés sous {app}\assets
Source: "assets\*";               DestDir: "{app}\assets"; Flags: recursesubdirs createallsubdirs

[Icons]
; Raccourci sur le bureau
Name: "{commondesktop}\DentalSoft"; Filename: "{app}\DentalSoft.exe"; IconFilename: "{app}\assets\icons\Logo.ico"
; Raccourci dans le menu Démarrer
Name: "{group}\DentalSoft";         Filename: "{app}\DentalSoft.exe"; IconFilename: "{app}\assets\icons\Logo.ico"

[Run]
; Lancer l’application à la fin de l’installation
Filename: "{app}\DentalSoft.exe"; Description: "Lancer DentalSoft"; Flags: nowait postinstall skipifsilent