# plamo2-translate-lmstudio

LM Studio の OpenAI 互換 API を利用して `plamo-2-translate` モデルで英⇔日翻訳を行う Python ライブラリです。



## 前提条件（セットアップ）

### 1) LM Studio のローカルサーバを有効化
1. LM Studio を起動  
2. 左サイドバー **Developer（開発者）** → **Local Server** を **ON**  
3. 画面に **http://localhost:1234/v1** と表示されることを確認  
   - （任意）**Developer Logs** を開き、起動ログを見られるようにしておくと実行確認が容易

### 2) モデルを追加し、**My Models** から設定を変更
1. 左サイドバー **My Models** → **Add model**  
   - **Hugging Face** から検索して **`mmnga/plamo-2-translate-gguf`** を追加   
   - まずは **Q4_K_S**（軽量・動作確認向け）がおすすめ。安定重視なら **Q5_0 / Q5_K_S**
2. **My Models** で `plamo-2-translate`（追加したもの）を選択 → **⚙（歯車）** をクリック  
   - **Prompt Template**：**Custom（カスタム）を選び、内容を空にする**  
     - ＝ **会話テンプレートを無効化**（“User: … / Assistant: …”等を自動で挿入させない）  
   - （任意）**Stop sequences** に **`<|plamo:op|>`** を追加  
     - [Hugging face plamoページ](https://huggingface.co/pfnet/plamo-2-translate) `Usage` 準拠。
     - 本ライブラリは API 側で `stop=["<|plamo:op|>"]` を毎回付けますが、UIにも入れておくと手動試験が楽。  
     ※作者はこの設定なしでも正常に翻訳できました。

> **ポイント**：会話テンプレは **My Models でモデル単位**に設定します（Playground側のテンプレとは別）。  
> 念のため、**新規チャット**で試すのが安全です。

### 3) （推奨）llama.cpp のバージョンを新しめに
- LM Studio 同梱のエンジン（llama.cpp）が古いと **“`<|plamo:reserved:0x1E|>` が連発”** することがあります。  
- 起動ログ（Local Server のログ）で **`arch: plamo2`** と出ているか確認してください（出ない場合は LM Studio 更新を検討）。



## このライブラリがやること

- `plamo-2-translate` は**専用フォーマット**で動かす必要があります：
```

<|plamo:op|>dataset
translation
<|plamo:op|>input lang=English
(訳したい本文)
<|plamo:op|>output lang=Japanese

````

本ライブラリはこの書式を**自動で組み立てて送信**します。

---

## インストール

```bash
git clone https://github.com/ceedarr/plamo2-translate-lmstudio.git
cd plamo2-translate-lmstudio
pip install -e .
```


## 使い方

トップレベルのヘルパー関数（`translate` / `translate_ja_en` / `en2ja` / `ja2en`）は共通して次のキーワードを受け取ります。

- `translator`: 既存の `PlamoTranslator` インスタンスを使い回す場合に指定。
- `translator_kwargs`: 新しく `PlamoTranslator` を生成するときに渡す初期化パラメータ（`base_url` / `model` / `timeout_sec` など）。
- それ以外のキーワード（`temperature`, `top_p`, `top_k`, `max_tokens` 等）は翻訳生成パラメータとして `PlamoTranslator.translate` に引き継がれます。

> **NOTE**: 既存インスタンス（`translator` 引数）を渡した場合、同時に `translator_kwargs` を渡すことはできません。初期化済みの設定をそのまま使いたい、というケースでインスタンス引数を使ってください。

### 1. 汎用関数を使った翻訳

※規定モデル：`mmnga/plamo-2-translate-gguf`  
メインの利用想定は英→日、日→英ですが、`src_lang` と `tgt_lang` を変えれば他言語も翻訳可能（精度は未検証）。

```python
from plamo2_translate_lmstudio import translate

result = translate("Where are you from?", src_lang="English", tgt_lang="Japanese")
print(result)  # -> どこ出身ですか？ など
```

### 2. 英→日、日→英、英⇔日専用関数を使った翻訳

※規定モデル：`mmnga/plamo-2-translate-gguf`  
```python
from plamo2_translate_lmstudio import en2ja, ja2en, translate_ja_en

result_en2ja = en2ja("I would like to schedule a meeting with you next week.")
print(result_en2ja)  # -> 来週あなたと会議を予定したいのですが。

result_ja2en = ja2en("今日は一日どうでしたか？")
print(result_ja2en)  # -> How was your day today?

result_mix_ja = translate_ja_en("ja", "週末までに翻訳メモリを最新化してください。")
print(result_mix_ja)  # -> Please update the translation memory by the weekend.

result_mix_en = translate_ja_en("en", "Could you summarize the customer feedback in Japanese?")
print(result_mix_en)  # -> 顧客からのフィードバックを日本語で要約していただけますか？
```

### 3. ループを使った一括翻訳

※規定モデル：`mmnga/plamo-2-translate-gguf`  
```python
from plamo2_translate_lmstudio import translate, translate_ja_en

pairs = [
    ("English", "Japanese", "Could you prepare the architecture review slides?"),
    ("Japanese", "English", "新しいテストケースをリポジトリに追加しました。"),
]

for src_lang, tgt_lang, sentence in pairs:
    output = translate(sentence, src_lang=src_lang, tgt_lang=tgt_lang)
    print(f"{src_lang} -> {tgt_lang}")
    print(f"  Original   : {sentence}")
    print(f"  Translation: {output}\n")

ja_en_samples = [
    ("ja", "週次ミーティングの議事録を送付しました。"),
    ("en", "Please double-check the release plan for next week."),
    ("ja", "来週のリリース手順を確認してください。"),
    ("en", "The localization glossary has been updated."),
]

for src_lang, sentence in ja_en_samples:
    output = translate_ja_en(src_lang, sentence)
    tgt_lang = "English" if src_lang in ["Japanese", "ja", "jp"] else "Japanese"
    print(f"{src_lang} -> {tgt_lang}")
    print(f"  Original   : {sentence}")
    print(f"  Translation: {output}\n")
```

### 4. モデルなどを指定して翻訳する

```python
from plamo2_translate_lmstudio import PlamoTranslator

translator = PlamoTranslator(
	base_url="http://localhost:1234/v1",
	model="mmnga/plamo-2-translate-gguf", # ここでモデルを指定する
	timeout_sec=60,
)

translate = translator.translate
translate_ja_en = translator.translate_ja_en
en2ja = translator.en2ja
ja2en = translator.ja2en

sample_translate = translate("Please submit the quarterly report.", src_lang="English", tgt_lang="Japanese")
sample_translate_ja_en = translate_ja_en("ja", "最新の議事録を共有済みですか？")
sample_en2ja = en2ja("The deployment checklist is complete.")
sample_ja2en = ja2en("顧客への返信を今日中にお願いします。")

print("translate:", sample_translate)
print("translate_ja_en:", sample_translate_ja_en)
print("en2ja:", sample_en2ja)
print("ja2en:", sample_ja2en)
```

### 5. 細かな設定を行いたい場合

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
    temperature=0.0,     # 0: 毎回同じ回答になる
    max_tokens=128,
)
print(result)
```

### 6. `translate` / `translate_ja_en` で追加パラメータを調整
どちらのヘルパー関数でも、生成パラメータや `PlamoTranslator` の初期化キーワードを直接指定できます。

```python
from plamo2_translate_lmstudio import translate

result = translate(
	"Reserved words keep appearing...",
	top_p=0.95,
	top_k=50,
	timeout_sec=45,
)
print(result)
```

既存インスタンスを使い回す場合は、`translator` を渡しつつ生成パラメータのみ指定します。

```python
from plamo2_translate_lmstudio import translate, PlamoTranslator

shared_translator = PlamoTranslator(timeout_sec=90)

result = translate(
    "Could you review the release checklist?",
    translator=shared_translator,
    temperature=0.1,
)
print(result)
```

同じ要領で `en2ja` や `ja2en` も利用できます。

```python
from plamo2_translate_lmstudio import en2ja, ja2en

result_en = en2ja(
  "Please confirm the deployment window.",
  top_p=0.9,
  top_k=40,
  timeout_sec=50,
)
result_ja = ja2en(
  "最新のガイドラインに沿ってレビューを進めてください。",
  temperature=0.15,
)

print(result_en)
print(result_ja)
```



## **"reserved" が延々と出る**場合

   * 典型原因：古いエンジン or **会話テンプレ混入**
   * 手順で直す：

     * **My Models → （対象モデル）→ ⚙ → Prompt Template を空**（カスタムにして全削除）
     * **（任意）Stop sequences に `<|plamo:op|>` を追加**
     * **Developer → Local Server → /v1/completions** を使う（/v1/chat/completions ではない）
     * **Local Server の Show Logs** で **`arch: plamo2`** を確認（出なければ LM Studio 更新）
---

## クイック検証（cURL 例：/v1/completions を使う）

```bash
curl http://localhost:1234/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mmnga/plamo-2-translate-gguf",
    "prompt": "<|plamo:op|>dataset\ntranslation\n\n<|plamo:op|>input lang=English\nwhere are you from?\n<|plamo:op|>output lang=Japanese\n",
    "temperature": 0,
    "max_tokens": 128,
    "stop": ["<|plamo:op|>"]
  }'
# -> どこ出身ですか？（など）
```

出力例：
```
{
  "id": "(idが表示)",
  "object": "text_completion",
  "created": (UNIX時刻),
  "model": "plamo-2-translate",
  "choices": [
    {
      "index": 0,
      "text": "どこ出身ですか？\n",
      "logprobs": null,
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 22,
    "completion_tokens": 4,
    "total_tokens": 26
  },
  "stats": {}
}
```


<!-- 自分が理解してないので隠しておく

## トラブルシューティング

* **`requests.exceptions.ConnectionError`**

  * **Developer → Local Server** が **ON** か、`http://localhost:1234/v1` へ到達できるか確認
* **出力が空 or `reserved` 連発**

  * **My Models → ⚙ → Prompt Template を空**、**新規チャット**、**/v1/completions**、**Stop 指定**を確認
  * **Local Server → Show Logs** で **`arch: plamo2`** を確認。出ない場合は LM Studio 更新
  * ライブラリは自動で 1 回だけパラメータを緩めて再試行します（`temperature/top_p/top_k`）
* **応答が遅い**

  * `timeout_sec` を延長／モデルを一度ウォームアップ
  * 量子化を軽めに（Q4_K_S）-->

---

<!-- ## ライセンス / モデル利用上の注意

* 本ライブラリ：**MIT License**
* モデル `plamo-2-translate` のライセンス・利用条件は **PFN の配布条件**に従ってください（商用条件などに注意）。
  LM Studio および同梱コンポーネントのライセンスも各提供元の規約に従います。



## 免責事項（Disclaimer）

本リポジトリが提供するのは **当方作成のオリジナル Python コードのみ**であり、**現状有姿（AS IS）**で提供されます。  
明示黙示を問わず、**商品性・特定目的適合性・非侵害**を含むいかなる保証も行いません。

- **利用者責任**：本ソフトウェアの使用・不使用・設定・更新・第三者ソフト（LM Studio / llama.cpp など）の変更や不具合、ならびに本ソフトが生成・取得・加工に関与した**翻訳結果（生成物）**の正確性・完全性・有用性・適法性について、**最終的な責任は利用者にあります**。  
- **損害賠償の制限**：適用法で許される最大範囲において、当方は使用・使用不能・不具合・互換性問題・データ喪失・業務中断・利益喪失等から生じる**直接・間接・付随・特別・結果的損害**について**一切責任を負いません**。  
- **非公式性**：本リポジトリは Preferred Networks, Inc.、LM Studio、llama.cpp の**非公式**ラッパーであり、いかなる提携・後援・保証関係もありません。各名称は**各権利者の商標**または登録商標です。  
- **ライセンス遵守**：`plamo-2-translate` モデルの取得・実行・（必要に応じ）配布や、生成物の第三者提供・商用利用等には、**PLaMo コミュニティライセンス等の条件**が適用されます。**事前登録や表記義務などの遵守は利用者の責任**です。  
- **環境依存・互換性**：OS/ドライバ/llama.cpp・LM Studio のバージョン、モデル量子化（GGUF など）、ネットワーク/権限設定により挙動は変わります。**将来の互換性は保証しません**（API・挙動は予告なく変更され得ます）。  
- **輸出管理等**：輸出管理・制裁関連法令その他の適用法令の遵守は利用者の責任です。地域により使用が制限される場合があります。  
- **法的助言ではありません**：本READMEの記載は**法的助言（Legal Advice）ではありません**。適用ライセンス・契約・法令の解釈や適法性判断は、必要に応じて**専門家に相談**のうえ、利用者の責任で行ってください。 -->

## 免責・法的通知

- 本リポジトリは **当方が作成したPythonコードのみ**を提供します。**モデル資産（重み・語彙・トークナイザ等）は同梱しません。**
- コードのライセンスは **MIT License** です。**現状有姿（AS IS）** で提供し、商品性・特定目的適合性・非侵害など**一切の保証を行いません**。本コードの利用により生じたいかなる損害についても、**作者は責任を負いません**。
- 本プロジェクトは **Preferred Networks, Inc.／LM Studio／llama.cpp の非公式**ラッパーです。いかなる提携・後援・保証関係もありません。**PLaMo／LM Studio** 等は各権利者の商標または登録商標です。
- `plamo-2-translate` モデルの取得・利用・生成物の取り扱いには、**PFNの PLaMo コミュニティライセンス等の条件**が適用されます。**商用利用時の事前登録や表記義務**を含め、**利用者の責任で原文を確認・遵守**してください。
- 本記載は **法的助言ではありません**。適用法令や契約・ライセンスの解釈は、必要に応じて専門家へご相談ください。
