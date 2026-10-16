import zipfile
import os

pyz_path = r"F:\招新赛的WP\安全部招新赛WP\Reverse\Boxer\Boxer.exe_extracted\PYZ.pyz"
out_dir = r"F:\招新赛的WP\安全部招新赛WP\Reverse\Boxer\PYZ_extracted"

os.makedirs(out_dir, exist_ok=True)

# PYZ 本质是 zlib 压缩的归档，不是标准 zip，用 PyInstaller 的 archive 读取
from PyInstaller.archive.readers import ZlibArchiveReader

archive = ZlibArchiveReader(pyz_path)
for name in archive.toc:
    print(name)
    data = archive.extract(name)
    # data 是 code object，可以 marshal 出来
    import marshal
    with open(os.path.join(out_dir, name + ".pyc"), "wb") as f:
        f.write(marshal.dumps(data))