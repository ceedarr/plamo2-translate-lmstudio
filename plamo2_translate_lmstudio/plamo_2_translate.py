from __future__ import annotations
import requests
from typing import Optional

PLAMO_STOP = "<|plamo:op|>"

class PlamoTranslator:
    """
    LM Studio (OpenAI互換) の /v1/completions を使って
    plamo-2-translate(GGUF) で翻訳を行うための小さなクライアント。

    前提:
      - LM Studio > Developer > Local Server を ON（既定: http://localhost:1234/v1）
      - 対象モデル: "mmnga/plamo-2-translate-gguf" 等をロード済み
      - My Models の Prompt Template は「空」（= 会話化なし）
    """

    def __init__(
        self,
        base_url: str = "http://localhost:1234/v1",
        model: str = "mmnga/plamo-2-translate-gguf",
        timeout_sec: int = 30,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout_sec
        self.session = requests.Session()

    @staticmethod
    def build_prompt(
        text: str,
        src_lang: str = "English",
        tgt_lang: str = "Japanese",
        blank_line_after_header: bool = True,
    ) -> str:
        """
        PLaMo公式の書式に沿ってプロンプト文字列を組み立てる。
        """
        lines = [
            f"{PLAMO_STOP}dataset",
            "translation",
        ]
        if blank_line_after_header:
            lines.append("")  # ← "translation" の直後に空行を入れると安定しやすい
        lines += [
            f"{PLAMO_STOP}input lang={src_lang}",
            text,
            f"{PLAMO_STOP}output lang={tgt_lang}",
            "",  # 末尾改行を1つ
        ]
        return "\n".join(lines)

    def _call_completions(
        self,
        prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 256,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        stop_token: str = PLAMO_STOP,
    ) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stop": [stop_token],
        }
        if top_p is not None:
            payload["top_p"] = float(top_p)
        if top_k is not None:
            payload["top_k"] = int(top_k)

        url = f"{self.base_url}/completions"
        resp = self.session.post(url, json=payload, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()
        text = data["choices"][0]["text"]
        return text

    def translate(
        self,
        text: str,
        src_lang: str = "English",
        tgt_lang: str = "Japanese",
        temperature: float = 0.0,
        max_tokens: int = 256,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
    ) -> str:
        """
        “生プロンプト + stop=<|plamo:op|>” で plamo-2-translate を叩く。
        必要に応じて 1 回だけパラメータを緩めてリトライ（reserved連発の簡易対策）。
        """
        prompt = self.build_prompt(text, src_lang, tgt_lang, blank_line_after_header=True)
        out = self._call_completions(
            prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            top_k=top_k,
        ).strip()

        # “reserved” が続く等の異常出力に対する軽いリトライ
        if "<|plamo:reserved" in out or not out:
            out = self._call_completions(
                prompt,
                temperature=max(0.2, temperature),
                max_tokens=max_tokens,
                top_p=top_p if top_p is not None else 0.95,
                top_k=top_k if top_k is not None else 50,
            ).strip()
        return out

    # 使い勝手用の薄いラッパ
    def en2ja(self, text: str, **gen_kw) -> str:
        return self.translate(text, "English", "Japanese", **gen_kw)

    def ja2en(self, text: str, **gen_kw) -> str:
        return self.translate(text, "Japanese", "English", **gen_kw)


if __name__ == "__main__":
    tr = PlamoTranslator(
        base_url="http://localhost:1234/v1",
        model="mmnga/plamo-2-translate-gguf",
    )
    print(tr.en2ja("where are you from?"))  # 例: 「どこ出身ですか？」
