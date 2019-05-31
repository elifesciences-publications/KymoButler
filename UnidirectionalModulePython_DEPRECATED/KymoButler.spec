# -*- mode: python -*-

block_cipher = None

added_files = [
         ( 'net.json', '.' ),
         ( 'net.params', '.' ),
         ( 'auxparam.txt', '.' ),
         ( 'accum.py', '.' )
         ]

a = Analysis(['KymoButler.py'],
             pathex=['/Users/ad865/Dropbox (Personal)/KymoSoftware'],
             binaries=[('/Users/ad865/anaconda3/envs/kymo35/lib/python3.5/site-packages/mxnet/libmxnet.so', 'mxnet')],
             datas=added_files,
             hiddenimports=['pywt._extensions._cwt'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='KymoButler',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False )
app = BUNDLE(exe,
             name='KymoButler.app',
             icon=None,
             bundle_identifier=None)
