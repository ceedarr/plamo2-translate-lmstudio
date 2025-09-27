"""plamo2-translate-lmstudio パッケージの公開 API.

`PlamoTranslator` クラスと翻訳ユーティリティ関数を提供する。
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .plamo_2_translate import PLAMO_STOP, PlamoTranslator

__all__ = ["PlamoTranslator", "PLAMO_STOP", "translate", "translate_ja_en", "en2ja", "ja2en"]

_TRANSLATOR_INIT_KEYS = {"base_url", "model", "timeout_sec"}


def _collect_translator_kwargs(
	gen_kwargs: Dict[str, Any],
	translator_kwargs: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
	merged: Dict[str, Any] = {}
	extra = gen_kwargs.pop("translator_kwargs", None)
	if extra:
		merged.update(extra)
	if translator_kwargs:
		merged.update(translator_kwargs)
	for key in list(gen_kwargs.keys()):
		if key in _TRANSLATOR_INIT_KEYS:
			merged.setdefault(key, gen_kwargs.pop(key))
	return merged


def _ensure_translator(
	translator: Optional[PlamoTranslator],
	translator_kwargs: Dict[str, Any],
) -> PlamoTranslator:
	if translator is None:
		return PlamoTranslator(**translator_kwargs)
	if translator_kwargs:
		raise ValueError(
			"translator instance and translator initialization kwargs were both provided. "
			"Provide generation parameters only when passing an existing translator."
		)
	return translator


def translate(
	text: str,
	src_lang: str = "English",
	tgt_lang: str = "Japanese",
	*,
	translator: Optional[PlamoTranslator] = None,
	translator_kwargs: Optional[Dict[str, Any]] = None,
	**gen_kwargs,
) -> str:
	"""テキストを単発で翻訳するための薄いユーティリティ。

	Parameters
	----------
	text:
		翻訳したい文字列。
	src_lang, tgt_lang:
		元の言語と対象の言語。plamo-2-translate でサポートされる
		任意の言語ラベルを指定可能。
	translator:
		既存の :class:`PlamoTranslator` インスタンス。未指定なら内部で生成する。
	translator_kwargs:
		新たにインスタンス化する際に :class:`PlamoTranslator` に渡すパラメータ。
		``translator`` 指定時は無視される。
	**gen_kwargs:
		翻訳生成パラメータ。代表例は以下の通り。

		- ``temperature``: 0.0〜1.0 程度の値。0 に近いほど決定的。
		- ``top_p``: nucleus sampling の確率質量（0〜1）。
		- ``top_k``: 候補トークン数の上限（0 で無効）。
		- ``max_tokens``: 応答側で生成するトークン数の上限。
		- ``stop``: 追加のストップシーケンスを指定するリスト。

		ここに挙げた以外のキーワードも、`plamo2_translate_lmstudio.plamo_2_translate`
		モジュール内の :meth:`PlamoTranslator.translate` がサポートするパラメータ名であれば
		そのまま委譲される。詳細は当該メソッドの docstring や LM Studio の
		``/v1/completions`` エンドポイント仕様を参照。

	Returns
	-------
	str
		翻訳結果の文字列。
	"""

	collected = _collect_translator_kwargs(gen_kwargs, translator_kwargs)
	resolved = _ensure_translator(translator, collected)
	return resolved.translate(
		text=text,
		src_lang=src_lang,
		tgt_lang=tgt_lang,
		**gen_kwargs,
	)


def translate_ja_en(
	text_lang: str,
	text: str,
	*,
	translator: Optional[PlamoTranslator] = None,
	translator_kwargs: Optional[Dict[str, Any]] = None,
	**gen_kwargs,
) -> str:
	"""日本語と英語の双方向翻訳に特化したラッパー関数。"""

	collected = _collect_translator_kwargs(gen_kwargs, translator_kwargs)
	resolved = _ensure_translator(translator, collected)
	return resolved.translate_ja_en(text_lang, text, **gen_kwargs)


def en2ja(
	text: str,
	*,
	translator: Optional[PlamoTranslator] = None,
	translator_kwargs: Optional[Dict[str, Any]] = None,
	**gen_kwargs,
) -> str:
	"""英語から日本語へ翻訳するためのライトウェイトヘルパー。"""

	collected = _collect_translator_kwargs(gen_kwargs, translator_kwargs)
	resolved = _ensure_translator(translator, collected)
	return resolved.en2ja(text, **gen_kwargs)


def ja2en(
	text: str,
	*,
	translator: Optional[PlamoTranslator] = None,
	translator_kwargs: Optional[Dict[str, Any]] = None,
	**gen_kwargs,
) -> str:
	"""日本語から英語へ翻訳するためのライトウェイトヘルパー。"""

	collected = _collect_translator_kwargs(gen_kwargs, translator_kwargs)
	resolved = _ensure_translator(translator, collected)
	return resolved.ja2en(text, **gen_kwargs)

