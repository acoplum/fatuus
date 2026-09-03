"""Dicionários de termos sintéticos (slop), clichês de LLM e padrões de pontuação."""

# Expressões em Português comuns em saídas sintéticas de IA
SLOP_PATTERNS_PT = [
    # Clichês de abertura e transição
    r"\bé importante (ressaltar|destacar|notar|lembrar|salientar)\b",
    r"\bno cenário atual\b",
    r"\bno mundo de hoje\b",
    r"\bno mundo contemporâneo\b",
    r"\bvale a pena (notar|ressaltar|destacar)\b",
    r"\bvale lembrar que\b",
    r"\bem suma\b",
    r"\bem conclusão\b",
    r"\bpor fim, mas não menos importante\b",
    r"\bcomo mencionado anteriormente\b",
    r"\bum divisor de águas\b",
    r"\bdesempenha um papel (fundamental|crucial|vital|central)\b",
    r"\buma ampla gama de\b",
    r"\buma vasta gama de\b",
    r"\bum vislumbre de\b",
    r"\bmergulhar (fundo|mais fundo) em\b",
    r"\bdesvendar os segredos\b",
    r"\bfarol de (esperança|inovação|luz)\b",
    r"\btapeçaria (vibrante|complexa|cultural)\b",
    r"\bum testemunho (de|do|da|vivo)\b",
    r"\bessencial para garantir\b",
    r"\bsempre em constante evolução\b",
    r"\bimpulsionar o crescimento\b",
    r"\bpodemos concluir que\b",
    r"\bé inegável que\b",
    r"\bcabe destacar que\b",
    r"\bnos dias de hoje\b",
    r"\bdiante desse cenário\b",
    r"\bcada vez mais presente\b",
    r"\buma verdadeira revolução\b",
    r"\bmudança de paradigma\b",
    r"\babordagem holística\b",
    r"\bembarcar em uma jornada\b",
    r"\belevar o (nível|patamar)\b",
    r"\bdesbloquear o potencial\b",
    r"\bé fundamental (compreender|entender|destacar)\b",
]

# Expressões em Inglês (Slop e AI markers)
SLOP_PATTERNS_EN = [
    r"\bdelve into\b",
    r"\ba testament to\b",
    r"\btapestry of\b",
    r"\bbeacon of\b",
    r"\bcrucial role\b",
    r"\bpivotal (moment|role|step)\b",
    r"\bgame-changer\b",
    r"\bit is important to (note|remember|highlight)\b",
    r"\bin today's (fast-paced|world|digital landscape)\b",
    r"\bnavigating the landscape\b",
    r"\bharnessing the power of\b",
    r"\bunleash(ing)? the potential\b",
    r"\ba myriad of\b",
    r"\ba plethora of\b",
    r"\bfostering a sense of\b",
    r"\bpoised to\b",
    r"\bunderscores the need\b",
    r"\bvibrant ecosystem\b",
    r"\bin conclusion\b",
    r"\blast but not least\b",
    r"\bever-evolving\b",
    r"\bever-changing\b",
    r"\bin the realm of\b",
    r"\bat the end of the day\b",
    r"\bwhen it comes to\b",
    r"\bit('| i)s worth noting\b",
    r"\bneedless to say\b",
    r"\bembark on a journey\b",
    r"\bdive (deep|deeper) into\b",
    r"\btreasure trove of\b",
    r"\bparadigm shift\b",
    r"\bholistic approach\b",
    r"\bseamlessly integrate(s|d)?\b",
    r"\belevate your\b",
    r"\bunlock the (full )?(power|potential|secrets)\b",
]

# Padrões estruturais do "Signs of AI writing" (WikiProject AI Cleanup):
# detectáveis por regex, mas sem substituição determinística segura —
# reescrevê-los é papel da Camada 1, não do sanitizador.
STRUCTURAL_PATTERNS_PT = [
    (
        "negação contrastiva (não é X, é Y)",
        r"\bnão é (?:apenas|só|somente) [^.!?\n]{1,60}[,;] (?:é|mas)\b",
    ),
    (
        "não apenas X, mas também Y",
        r"\bnão (?:apenas|só) [^.!?\n]{1,60},? mas também\b",
    ),
    (
        "não se trata de X, mas Y",
        r"\bnão se trata (?:apenas |só )?de [^.!?\n]{1,60}, mas\b",
    ),
]

STRUCTURAL_PATTERNS_EN = [
    (
        "not only X but (also) Y",
        r"\bnot only [^.!?\n]{1,60}\bbut(?: also)?\b",
    ),
    (
        "it's not about X, it's Y",
        r"\bit'?s not (?:just |only )?about [^.!?\n]{1,60}[,;\u2013\u2014-] (?:it'?s|but)\b",
    ),
    (
        "whether you're X or Y",
        r"\bwhether you'?re an? [^.!?\n]{1,60}\bor an? \w+",
    ),
]

# Caracteres invisíveis usados frequentemente em watermarks ou resquícios de copy-paste
ZERO_WIDTH_CHARS = {
    "\u200b": "Zero Width Space (ZWSP)",
    "\u200c": "Zero Width Non-Joiner (ZWNJ)",
    "\u200d": "Zero Width Joiner (ZWJ)",
    "\u200e": "Left-to-Right Mark (LRM)",
    "\u200f": "Right-to-Left Mark (RLM)",
    "\ufeff": "Zero Width No-Break Space (BOM)",
    "\u00ad": "Soft Hyphen",
    "\u2060": "Word Joiner (WJ)",
    "\u180e": "Mongolian Vowel Separator (MVS)",
    # Controles bidirecionais — embutimento, override e isolamento
    "\u202a": "Left-to-Right Embedding (LRE)",
    "\u202b": "Right-to-Left Embedding (RLE)",
    "\u202c": "Pop Directional Formatting (PDF)",
    "\u202d": "Left-to-Right Override (LRO)",
    "\u202e": "Right-to-Left Override (RLO)",
    "\u2066": "Left-to-Right Isolate (LRI)",
    "\u2067": "Right-to-Left Isolate (RLI)",
    "\u2068": "First Strong Isolate (FSI)",
    "\u2069": "Pop Directional Isolate (PDI)",
    # Operadores matemáticos invisíveis
    "\u2061": "Function Application",
    "\u2062": "Invisible Times",
    "\u2063": "Invisible Separator",
    "\u2064": "Invisible Plus",
}

# Seletores de variação (U+FE00–FE0F). Legítimos depois de uma base emoji
# (ex.: "✔" + VS16); em qualquer outra posição são canal clássico de
# watermark por steganografia.
VARIATION_SELECTORS = {chr(cp): f"Variation Selector-{cp - 0xFE00 + 1} (VS)" for cp in range(0xFE00, 0xFE10)}

# Espaços que se disfarçam de espaço comum — substituídos por " ", não removidos
SPACE_LOOKALIKE_CHARS = {
    "\u00a0": "No-Break Space (NBSP)",
    "\u202f": "Narrow No-Break Space (NNBSP)",
    "\u2000": "En Quad",
    "\u2001": "Em Quad",
    "\u2002": "En Space",
    "\u2003": "Em Space",
    "\u2004": "Three-Per-Em Space",
    "\u2005": "Four-Per-Em Space",
    "\u2006": "Six-Per-Em Space",
    "\u2007": "Figure Space",
    "\u2008": "Punctuation Space",
    "\u2009": "Thin Space",
    "\u200a": "Hair Space",
    "\u205f": "Medium Mathematical Space",
    "\u3000": "Ideographic Space",
}

# Separadores de linha Unicode — normalizados para "\n"
LINE_SEPARATOR_CHARS = {
    "\u2028": "Line Separator (LS)",
    "\u2029": "Paragraph Separator (PS)",
}

# Normalização tipográfica (aspas curvas e reticências → ASCII).
# Travessão fica de fora de propósito: em PT-BR ele é pontuação legítima
# (diálogo, aposto) — a densidade dele vira métrica no detector, não
# substituição cega no sanitizador.
TYPOGRAPHIC_REPLACEMENTS = {
    "\u2018": "'",  # left single quotation mark
    "\u2019": "'",  # right single quotation mark
    "\u201a": "'",  # single low-9 quotation mark
    "\u2032": "'",  # prime
    "\u201c": '"',  # left double quotation mark
    "\u201d": '"',  # right double quotation mark
    "\u201e": '"',  # double low-9 quotation mark
    "\u2033": '"',  # double prime
    "\u2026": "...",  # horizontal ellipsis
}

# Bases que tornam um seletor de variação legítimo: emoji, símbolos e os
# dígitos/`#`/`*` das sequências de keycap.
_EMOJI_BASE_RANGES = (
    (0x2190, 0x2BFF),  # setas, símbolos diversos, dingbats
    (0x1F000, 0x1FAFF),  # blocos de emoji
    (0x3030, 0x303D),
    (0x3297, 0x3299),
    (0x00A9, 0x00A9),  # ©
    (0x00AE, 0x00AE),  # ®
    (0x2122, 0x2122),  # ™
)
_KEYCAP_BASES = set("0123456789#*")


def is_emoji_base(char: str) -> bool:
    """True se `char` pode legitimamente preceder um seletor de variação."""
    if char in _KEYCAP_BASES:
        return True
    cp = ord(char)
    return any(lo <= cp <= hi for lo, hi in _EMOJI_BASE_RANGES)
