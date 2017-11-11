## install

### mecab

- ref: https://github.com/taku910/mecab
```
git clone https://github.com/taku910/mecab.git
cd mecab/mecab
./configure  --enable-utf8-only
make
make check
sudo make install
```
- check following
```
/usr/local/etc/mecabrc
/usr/local/bin/mecab
/usr/local/bin/mecab-config
```

### ipa-dic

- dic for mecab
```
cd ../mecab-ipadic
./configure --with-charset=utf8
make
sudo make install
```

- check
```
$ mecab
MeCab はフリーソフトウェアです
```

### mecab for python

- use pip install
```
pip install mecab-python3
```

- in tha case that  error occurred when you use form python.
```
ImportError: libmecab.so.2: cannot open shared object file: No such file or directory
```
- check libraly path and fix it.
```
ldconfig -p | grep 'mecab'

echo '/usr/local/lib' >> ./mylib.conf
sudo cp  mylib.conf /etc/ld.so.conf.d/
sudo ldconfig

ldconfig -p | grep 'mecab'
```

- usage: https://github.com/SamuraiT/mecab-python3/blob/master/bindings.html

## NEologd 

- https://github.com/neologd/mecab-ipadic-neologd

## Cabocha

- CRF++
```
 wget "https://drive.google.com/uc?export=download&id=0B4y35FiV1wh7QVR6VXJ5dWExSTQ" -O CRF++-0.58.tar.gz
 $ tar zxfv CRF++-0.58.tar.gz
 $ cd CRF++-0.58
 $ ./configure
 $ make
 $ sudo make install

```
- Cabocha
```
$ wget "https://googledrive.com/host/0B4y35FiV1wh7cGRCUUJHVTNJRnM/cabocha-0.69.tar.bz2" -O cabocha-0.69.tar.bz2
$ tar jxvf cabocha-0.69.tar.bz2
$ cd cabocha-0.69
$ ./configure --with-charset=utf8
$ make
$ sudo make install
```

## dataset

- set symbolic link in `./dataset`

```
ln -s /**/data ./dataset
```