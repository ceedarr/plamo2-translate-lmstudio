"""plamo2-translate-lmstudio パッケージの公開 API.

`PlamoTranslator` クラスと `translate` ヘルパー関数を提供する。
"""

from __future__ import annotations

from typing import Optional

from .plamo_2_translate import PLAMO_STOP, PlamoTranslator

__all__ = ["PlamoTranslator", "PLAMO_STOP", "translate"]


def translate(
	text: str,
	src_lang: str = "English",
	tgt_lang: str = "Japanese",
	*,
	translator: Optional[PlamoTranslator] = None,
	**translator_kwargs,
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
		既存の :class:`PlamoTranslator` インスタンス。
		未指定の場合は ``translator_kwargs`` を使って新しく生成する。
	**translator_kwargs:
		`PlamoTranslator` コンストラクタに渡す追加パラメータ。
		``translator`` を明示した場合は無視される。

	Returns
	-------
	str
		翻訳結果の文字列。
	"""

	if translator is None:
		translator = PlamoTranslator(**translator_kwargs)

	return translator.translate(
		text=text,
		src_lang=src_lang,
		tgt_lang=tgt_lang,
	)
