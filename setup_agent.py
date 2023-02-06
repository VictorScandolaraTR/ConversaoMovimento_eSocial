from cx_Freeze import Executable, setup

name = 'Agente de comunicação'
version = '1.0'
author = 'Conversão'
url = 'http://thomsonreuters.com'
description = 'Agente de comunicação Conversor de movimento.'

# opções para build
build_exe_options = {
    'packages': ['os'],
    'excludes': [
        'PyQt5',
        'PyQt5-Qt5',
        'PyQt5-sip',
        'PySide6',
        'lxml',
        'numpy'
        'PIL',
        'psycopg2',
        'scipy',
        'test',
        ],
    'include_msvcr': True
}

setup(
    name=name,
    version=version,
    author=author,
    url=url,
    description=description,
    options={
        'build_exe': build_exe_options
    },
    executables=[
        Executable(
            '.\\src\\rpa\\agent.py',
            base='win32GUI',
            shortcut_name="Agente de comunicação",
            shortcut_dir='DesktopFolder'
        )],
)