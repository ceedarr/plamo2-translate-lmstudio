# plamo2-translate-lmstudio-py

LM Studio の OpenAI 互換 API を利用して `plamo-2-translate` モデル（GGUF）で英⇔日翻訳を行う Python モジュールです。


## 1. 事前準備

| 項目 | 手順 | 備考 |
| ---- | ---- | ---- |
| LM Studio | **Developer → Local Server** を **ON**（既定: `http://localhost:1234/v1`） | `arch: plamo2` が表示される最新バージョンを推奨 |
| モデル | **My Models → Add model** で `mmnga/plamo-2-translate-gguf` を追加。Prompt Template を空にする | 現状Q4_K_Sで実行確認済み、他plamo系モデルでも使えるかは未確認 |
| Stop Sequence | 任意で `<\|plamo:op\|>` を UI 側にも登録 | [Hugging face plamo モデルカード](https://huggingface.co/pfnet/plamo-2-translate) `Usage` 準拠。本ライブラリは API リクエスト時に自動指定 |
| llama.cpp ランタイム | **LM Studio を最新化**。Windows で **Vulkan llama.cpp**を更新 | **`reserved` 連発時に Vulkan 版を更新して改善**を確認（手元検証）。 |

### インストール・使用方法

(Windows)
```bash
git clone https://github.com/ceedarr/plamo2-translate-lmstudio.git
cd plamo2-translate-lmstudio
python -m venv .venv
.venv/Scripts/activate.bat
pip install -e .
```

`plamo2-translate-lmstudio` フォルダにJupyter Notebookを新規作成してご利用ください。  
サンプルを同梱の `example.ipynb` に示しています。



## 2. 翻訳 API のエントリーポイント

モジュールが提供するトップレベル関数は4つです。いずれも `plamo2_translate_lmstudio` 名前空間から import できます。

| 関数 | 役割 | 既定の言語方向 |
| ---- | ---- | ---- |
| `translate(text, src_lang="English", tgt_lang="Japanese", ...)` | 任意ペアの翻訳 | 指定可（他言語も利用可能） |
| `translate_ja_en(text_lang, text, ...)` | 日本語/英語の双方向判定つき翻訳 | `text_lang` が `ja/jp` なら日→英、`en` なら英→日 |
| `en2ja(text, ...)` | 英→日のショートカット | 英→日 |
| `ja2en(text, ...)` | 日→英のショートカット | 日→英 |

内部では `PlamoTranslator` クラスが実際の HTTP 呼び出しを担っています。トップレベル関数は**ラッパー**であり、以下の3つの利用シナリオをサポートします。



## 3. 利用シナリオ別ガイド

### 3.1 シナリオ1: 「規定のまま使う」（カスタマイズなし）

最も簡単な利用法です。ライブラリ既定の `base_url` や `model` がそのまま使われ、生成パラメータ（temperature など）も初期値を採用します。  
※`model` には、規定の `mmnga/plamo-2-translate-gguf` が用いられます。

```python
from plamo2_translate_lmstudio import translate, translate_ja_en, en2ja, ja2en

print(translate("Where are you from?"))
print(translate_ja_en("ja", "週末までに翻訳メモリを更新してください。"))
print(en2ja("Please share the draft agenda."))
print(ja2en("明日の会議には参加可能です。"))
```

> **特徴**: パラメータ指定が不要。LM Studio 側の設定のみで動作。

### 3.2 シナリオ2: 「`PlamoTranslator` をカスタマイズして使う」

使用モデルを変更したいときなどに使います。  

1. 任意の初期化パラメータ（`base_url`, `model`, `timeout_sec` など）を渡して `PlamoTranslator` をインスタンス化。
2. そのインスタンスのメソッド（`translate`, `translate_ja_en`, `en2ja`, `ja2en`）を変数に代入。

```python
from plamo2_translate_lmstudio import PlamoTranslator

translator = PlamoTranslator(
    base_url="http://localhost:1234/v1",  # エンドポイント変更時
    model="mmnga/plamo-2-translate-gguf", # ここでモデルを指定する
    timeout_sec=45,
)

translate = translator.translate
translate_ja_en = translator.translate_ja_en

print(translate("Deployment steps are documented.", src_lang="English", tgt_lang="Japanese", temperature=0.1))
print(translate_ja_en("jp", "リリースチェックリストの最新版を共有しましたか？", top_p=0.9))
```

> **特徴**: 初期化パラメータを 1 度だけ設定すれば、その後は自由な組み合わせで生成パラメータを指定可能。長期運用中のセッション再利用にも向く。

### 3.3 シナリオ3: 「カスタマイズされた `translator` を毎回引数へ渡す」

トップレベル関数の `translator` 引数に `PlamoTranslator` を渡す方式です。毎回明示的にインスタンスを指定したい場合に利用します。

```python
from plamo2_translate_lmstudio import translate, PlamoTranslator

custom_translator = PlamoTranslator(model="mmnga/plamo-2-translate-gguf", timeout_sec=90)

result = translate(
    "Could you prepare the metrics dashboard?",
    translator=custom_translator,
    temperature=0.2,
)
print(result)
```

> **特徴**: 関数呼び出しごとに異なる翻訳器設定を差し替えたい場面に便利。`translator` を渡した場合、`translator_kwargs` は同時指定できません。



## 4. パラメータの分類と入力先

### 4.1 初期化パラメータ（`base_url`, `model`, `timeout_sec`）

- **シナリオ1**: トップレベル関数に `translator_kwargs={"model": ..., ...}` の形式で渡すと、内部で新しい `PlamoTranslator` が生成されます。渡さなければライブラリ既定値が使われます。
- **シナリオ2**: `PlamoTranslator(...)` のコンストラクタ引数として 1 度設定し、以降はそのインスタンスを使い回します。トップレベル関数に `translator_kwargs` を渡す必要はありません。
- **シナリオ3**: 呼び出しごとに `translator=PlamoTranslator(...)` を明示する形で指定します。既存インスタンスを渡す場合は `translator_kwargs` を併用できません。

### 4.2 生成パラメータ（`temperature`, `top_p`, `top_k`, `max_tokens`, `stop` ...）

- **シナリオ1**: `translate(..., temperature=0.1, top_p=0.9, ...)` のようにトップレベル関数へ直接渡せます。
- **シナリオ2**: インスタンスメソッドを呼ぶ際にキーワードとして渡します（例: `translate(..., top_k=40)`）。
- **シナリオ3**: トップレベル関数に渡しつつ `translator=` でインスタンスを指定します。

> 代表的な生成パラメータの意味 (作者はこれについて詳しくありません。詳しくは、[LM Studio のドキュメント](https://lmstudio.ai/docs/app/api/endpoints/openai)を参照してください。):
>
> - `temperature`: 0.0 に近いと確定的、値を大きくすると多様性が増す。
> - `top_p`: nucleus sampling の確率質量（0〜1）。
> - `top_k`: 候補トークン数の上限（0 で無効）。
> - `max_tokens`: 応答で生成する最大トークン数。
> - `stop`: 追加のストップシーケンス。 [参照：Hugging face plamo モデルカード](https://huggingface.co/pfnet/plamo-2-translate)

### 4.3 `translator` / `translator_kwargs` の使い分け

- `translator` 引数には、既に作成済みの `PlamoTranslator` インスタンスを渡します。シナリオ3で毎回差し替える場合や、シナリオ2の派生としてメソッドを直接呼びたい場合に利用します。
- `translator_kwargs` 引数には、`PlamoTranslator` を内部生成してほしいときの初期化キーワード（`base_url` など）を辞書で渡します。トップレベル関数をそのまま使いながら、必要に応じて初期設定だけを一時的に上書きしたい場合に利用します。
- 上記 2 つを同時に指定することはできません。既存インスタンスを渡す場合は `translator_kwargs` を省略し、新規生成させる場合は `translator` を省略してください。



## 5. サンプルレシピ

### 5.1 翻訳品質が悪いときの再試行設定

```python
from plamo2_translate_lmstudio import translate

result = translate(
    "Reserved tokens keep appearing...",
    temperature=0.2,
    top_p=0.95,
    top_k=50,
    max_tokens=256,
)
print(result)
```

### 5.2 サーバ設定を都度切り替える（シナリオ3）

```python
from plamo2_translate_lmstudio import translate, PlamoTranslator

primary = PlamoTranslator(base_url="http://localhost:1234/v1")
backup = PlamoTranslator(base_url="http://localhost:2345/v1")

print(translate("Primary server test", translator=primary))
print(translate("Backup server test", translator=backup))
```

### 5.3 アプリケーション内で共有する（シナリオ2）

```python
from plamo2_translate_lmstudio import PlamoTranslator

shared_translator = PlamoTranslator(model="mmnga/plamo-2-translate-gguf", timeout_sec=120)

def translate_notice(text: str) -> str:
    return shared_translator.translate_ja_en("ja", text, temperature=0.05)

def translate_summary(text: str) -> str:
    return shared_translator.translate(text, src_lang="English", tgt_lang="Japanese", top_p=0.92)
```


## 6. 参考情報とライセンス

- 本リポジトリは **当方が作成したPythonコードのみ**を提供します。**モデル資産（重み・語彙・トークナイザ等）は同梱しません。**
- コードのライセンスは **MIT License** です。**現状有姿（AS IS）** で提供し、商品性・特定目的適合性・非侵害など**一切の保証を行いません**。本コードの利用により生じたいかなる損害についても、**作者は責任を負いません**。
- 本プロジェクトは **Preferred Networks, Inc.／LM Studio／llama.cpp の非公式**ラッパーです。いかなる提携・後援・保証関係もありません。**PLaMo／LM Studio** 等は各権利者の商標または登録商標です。
- `plamo-2-translate` モデルの取得・利用・生成物の取り扱いには、**PFNの PLaMo コミュニティライセンス等の条件**が適用されます。**商用利用時の事前登録や表記義務**を含め、**利用者の責任で原文を確認・遵守**してください。
- 本記載は **法的助言ではありません**。適用法令や契約・ライセンスの解釈は、必要に応じて専門家へご相談ください。
