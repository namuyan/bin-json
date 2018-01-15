bin-json
===========
Pythonの特徴的なオブジェクト、int, str, bytes, tuple, set, dict, listを含んだデータを
バイナリ形式に変換します。

目的
----
Pythonのオブジェクトを他のプログラムに送信する場合、通常はJSON形式に変換して伝えます。
しかし、JSON形式は仕様上、bytes, set, tupleなどを伝える事ができません。
また、dictには順番という概念は本来存在せず、JSONコードをバイナリと仮定した場合、環境によっては
微妙に異なる為、署名の基に使用できません。

環境
----
Python3

インストール
-----------
```commandline
git clone https://github.com/namuyan/bin-json.git
cd bin-json
sudo python3 setup.py install
```

テスト
------
```python
import bjson
 
bjson.test()
```

使い方
-----
```python
import bjson
 
test = {"hello": 12345677, 'world': 567880}
bj = bjson.dumps(test)
print(bj)
oj = bjson.loads(bj)
print(oj)
```

注意点
------
set, dict に順番という概念は存在しません。
内部で自動的にソートされます。

ライセンス
---------
MIT