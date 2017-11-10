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


## dataset

- set symbolic link in `./dataset`

```
ln -s /**/data ./dataset
```