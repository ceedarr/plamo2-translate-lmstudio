# plamo2-translate-lmstudio

LM Studio の OpenAI 互換 API を利用して `plamo-2-translate` モデルで英⇔日翻訳を行う Python ライブラリです。

## 前提条件

1. **LM Studio** をインストールし、起動する。
2. `Developer (開発者) > Local Server` を **ON** にし、既定の `http://localhost:1234/v1` でアクセスできることを確認。
3. 翻訳モデルをロードし、LM Studio側でPrompt Template を空にする（会話テンプレート無効化）。
   本ライブラリは`mmnga/plamo-2-translate-gguf`の使用を想定しています。

## インストール

```bash
git clone https://github.com/ceedarr/plamo2-translate-lmstudio.git
cd plamo2-translate-lmstudio
pip install -e .
```

`requirements.txt` は特に用意していませんが、HTTP 通信に `requests` を利用しています。未インストールの場合は `pip install requests` を実行してください。

## 使い方

### 1. 汎用関数を使った翻訳
メインの利用想定は英→日、日→英ですが
引数`src_lang`および`tgt_lang`の設定を変えれば他言語への翻訳も一応可能です。翻訳精度は未知数ですが。

```python
from plamo2_translate_lmstudio import translate

result = translate("Where are you from?", src_lang="english", tgt_lang="japanese")
print(result)  # -> どこの出身ですか？ など
```

### 2. 英⇔日翻訳を前提とした言語指定の省略

```python
from plamo2_translate_lmstudio import translate_ja_en

print(translate_ja_en("jp", "お元気ですか？"))  # -> How are you?
print(translate_ja_en("en", "Nice to meet you"))  # -> お会いできてうれしいです
```

第一引数 `text_lang` は `"Japanese"`, `"ja"`, `"jp"`, `"English"`, `"en"` を受け付けます。

### 3. 細かな設定を行いたい場合 (開発者向け)

```python
from plamo2_translate_lmstudio import PlamoTranslator

translator = PlamoTranslator(
	base_url="http://localhost:1234/v1",
	model="mmnga/plamo-2-translate-gguf",
	timeout_sec=60,
)

result = translator.translate(
	"It was a close game.",
	src_lang="English",
	tgt_lang="Japanese",
	temperature=0.1,
	max_tokens=128,
)
print(result)
```

### 4. `translate` / `translate_ja_en` で追加パラメータを調整 (開発者向け)

どちらのヘルパー関数でも、生成パラメータや `PlamoTranslator` の初期化キーワードを直接指定できます。

```python
from plamo2_translate_lmstudio import translate

result = translate(
	"Reserved words keep appearing...",
	top_p=0.95,
	top_k=50,
	timeout_sec=45,  # PlamoTranslator(base_url=..., timeout_sec=45)
)
print(result)
```

`translate_ja_en` でも同様に `timeout_sec`, `model`, `base_url` などを引数として渡せます。

<!-- 自分が理解してないので隠しておく
## トラブルシューティング

- **`requests.exceptions.ConnectionError`**: LM Studio の Local Server が停止していないか確認してください。
- **翻訳結果が空 or `reserved` が多い**: デフォルトで 1 度だけパラメータを緩めてリトライします。改善しない場合は温度や `top_p`/`top_k` の調整を試してください。
- **応答が遅い**: `timeout_sec` を長めに設定するか、LM Studio でモデルを一度 warm-up してから再実行してください。 -->

## ライセンス

MIT License
