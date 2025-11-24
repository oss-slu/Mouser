#Import for the PyInstaller utilities
from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

#Included modules for hidden import in the final app bundle
hiddenimports = [
    "customtkinter", 
]

block_cipher = None

#Analyze structure for program structure, determine dependencies,
#collect all files, modules, and resource folders
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],

    #Included UI assets, experiment pages, shared utilities, 
    #and database files
    datas=[
        ("ui/", "ui"),
        ("shared/", "shared"),
        ("databases/", "databases"),
        ("experiment_pages/", "experiment_pages")
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    excludes=[],
    noarchive=False,
)

#Create Python bytecode archive
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

#Build main executable for Mouser Application
exe = EXE(pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name="Mouser",
        debug=False,
        strip=False,
        upx=False,
        console=False)

#Gather executable files, dependent libraries, resource 
#and data folders, and support file
coll = COLLECT(exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=False,
        name="Mouser")



