"""Dicionários de termos sintéticos (slop), clichês de LLM e padrões de pontuação."""

# Expressões em Português comuns em saídas sintéticas de IA
SLOP_PATTERNS_PT = [
    # Clichês de abertura e transição
    r"\bé importante (ressaltar|destacar|notar|lembrar|salientar)\b",
    r"\bno cenário atual\b",
    r"\bno mundo de hoje\b",
    r"\bno mundo contemporâneo\b",
    r"\bvale a pena (notar|ressaltar|destacar)\b",
    r"\bem suma\b",
    r"\bem conclusão\b",
    r"\bpor fim, mas não menos importante\b",
    r"\bcomo mencionado anteriormente\b",
    r"\bum divisor de águas\b",
    r"\bdesempenha um papel (fundamental|crucial|vital|central)\b",
    r"\buma ampla gama de\b",
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
}
