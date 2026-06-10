"""Brazilian Portuguese formatting utilities.

Common number and currency formatting functions used across report executors.
"""


def fmt_brl(value: float) -> str:
    """Format value as BRL currency with scale suffix.

    Examples:
        >>> fmt_brl(1_500_000_000)
        'R$ 1,50 bi'
        >>> fmt_brl(42_000_000)
        'R$ 42,00 mi'
        >>> fmt_brl(-300_000_000)
        '-R$ 300,00 mi'
    """
    abs_value = abs(value)
    sign = "-" if value < 0 else ""
    if abs_value >= 1_000_000_000:
        scaled, suffix = abs_value / 1_000_000_000, "bi"
    else:
        scaled, suffix = abs_value / 1_000_000, "mi"
    formatted = f"{scaled:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{sign}R$ {formatted} {suffix}"


def fmt_pct(value: float) -> str:
    """Format value as pt-BR percentage.

    Examples:
        >>> fmt_pct(19.99)
        '19,99%'
        >>> fmt_pct(-3.5)
        '-3,50%'
    """
    return f"{value:,.2f}%".replace(",", "X").replace(".", ",").replace("X", ".")
