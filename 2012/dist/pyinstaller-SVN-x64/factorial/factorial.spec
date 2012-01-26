# -*- mode: python -*-
a = Analysis([os.path.join(HOMEPATH,'support/_mountzlib.py'), os.path.join(CONFIGDIR,'support/useUnicode.py'), '/Users/lwy08/Downloads/FYP/Pyrulan/2012/sample_src/factorial.py'],
             pathex=['/Users/lwy08/Downloads/pyinstaller-SVN-x64'],
             hookspath=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=1,
          name=os.path.join('build/pyi.darwin/factorial', 'factorial'),
          debug=False,
          strip=None,
          upx=True,
          console=True )
coll = COLLECT( exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name=os.path.join('dist', 'factorial'))
