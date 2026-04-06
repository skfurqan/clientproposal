#!/usr/bin/env python3
"""CLI tool to generate branded PDF client proposals."""

from __future__ import annotations

import argparse
import os
import textwrap
from datetime import date
from decimal import Decimal, InvalidOperation

DEFAULT_TERMS = textwrap.dedent(
    """
    1) 50% deposit required to begin work. Remaining 50% due on final delivery.
    2) Scope changes outside the agreed project scope may require a change order.
    3) Client-provided feedback windows: 5 business days per review cycle.
    4) Deliverables are licensed to the client upon full payment.
    5) This proposal is valid for 30 days from the issue date.
    """
).strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a branded PDF proposal for a client project."
    )
    parser.add_argument("client_name", help="Client or company name")
    parser.add_argument("project_scope", help="Project scope summary text")
    parser.add_argument("price", help="Proposal price, e.g. 7500.00")
    parser.add_argument(
        "--brand-name",
        default="Your Company",
        help="Your brand/company name for the proposal header",
    )
    parser.add_argument(
        "--logo",
        default=None,
        help="Path to a PNG/JPG logo to place in the proposal header",
    )
    parser.add_argument(
        "--terms-file",
        default=None,
        help="Path to a text file containing terms and conditions",
    )
    parser.add_argument(
        "--payment-link",
        required=True,
        help="URL clients can use to pay the proposal invoice",
    )
    parser.add_argument(
        "--currency",
        default="USD",
        help="Currency label for the price (default: USD)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output PDF filename (default: proposal_<client>.pdf)",
    )
    return parser.parse_args()


def parse_price(price: str) -> Decimal:
    try:
        value = Decimal(price)
    except InvalidOperation as exc:
        raise ValueError(f"Invalid price '{price}'.") from exc

    if value <= 0:
        raise ValueError("Price must be greater than zero.")
    return value.quantize(Decimal("0.01"))


def read_terms(path: str | None) -> str:
    if not path:
        return DEFAULT_TERMS
    with open(path, "r", encoding="utf-8") as handle:
        content = handle.read().strip()
    return content or DEFAULT_TERMS


def draw_wrapped_text(
    pdf,
    text: str,
    x: int,
    y: int,
    width_chars: int = 92,
    line_height: int = 14,
) -> int:
    current_y = y
    for paragraph in text.splitlines() or [text]:
        paragraph = paragraph.strip()
        if not paragraph:
            current_y -= line_height
            continue
        lines = textwrap.wrap(paragraph, width=width_chars)
        for line in lines:
            pdf.drawString(x, current_y, line)
            current_y -= line_height
    return current_y


def generate_proposal(
    *,
    client_name: str,
    project_scope: str,
    price: Decimal,
    currency: str,
    brand_name: str,
    logo_path: str | None,
    terms: str,
    payment_link: str,
    output_file: str,
) -> None:
    try:
        from reportlab.lib.pagesizes import LETTER
        from reportlab.lib.utils import ImageReader
        from reportlab.pdfgen import canvas
    except ImportError as exc:  # pragma: no cover - runtime dependency check
        raise SystemExit(
            "Missing dependency: reportlab. Install with `pip install reportlab`."
        ) from exc

    pdf = canvas.Canvas(output_file, pagesize=LETTER)
    width, height = LETTER

    y = height - 60

    if logo_path and os.path.exists(logo_path):
        logo = ImageReader(logo_path)
        pdf.drawImage(logo, 40, y - 20, width=120, height=50, preserveAspectRatio=True)
        pdf.setFont("Helvetica-Bold", 20)
        pdf.drawString(180, y + 5, brand_name)
    else:
        pdf.setFont("Helvetica-Bold", 24)
        pdf.drawString(40, y, brand_name)

    y -= 65
    pdf.setFont("Helvetica", 11)
    pdf.drawString(40, y, f"Issue Date: {date.today().isoformat()}")
    y -= 18
    pdf.drawString(40, y, f"Prepared For: {client_name}")

    y -= 36
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(40, y, "Project Scope")
    y -= 20
    pdf.setFont("Helvetica", 11)
    y = draw_wrapped_text(pdf, project_scope, 40, y)

    y -= 18
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(40, y, "Investment")
    y -= 20
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(40, y, f"Total Project Fee: {currency} {price:,.2f}")

    y -= 35
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(40, y, "Terms & Conditions")
    y -= 20
    pdf.setFont("Helvetica", 10)
    y = draw_wrapped_text(pdf, terms, 40, y, width_chars=100, line_height=12)

    y -= 26
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(40, y, "Payment Link")
    y -= 20
    pdf.setFillColorRGB(0.0, 0.2, 0.7)
    pdf.setFont("Helvetica", 11)
    pdf.drawString(40, y, payment_link)
    pdf.linkURL(payment_link, (40, y - 2, width - 40, y + 12), relative=0)

    y -= 40
    pdf.setFillColorRGB(0, 0, 0)
    pdf.setFont("Helvetica-Oblique", 10)
    pdf.drawString(40, y, "Thank you for the opportunity. We look forward to working with you.")

    pdf.save()


def main() -> None:
    args = parse_args()
    try:
        price = parse_price(args.price)
    except ValueError as err:
        raise SystemExit(str(err)) from err

    terms = read_terms(args.terms_file)
    output_file = args.output
    if not output_file:
        safe_name = "_".join(args.client_name.lower().split())
        output_file = f"proposal_{safe_name}.pdf"

    generate_proposal(
        client_name=args.client_name,
        project_scope=args.project_scope,
        price=price,
        currency=args.currency,
        brand_name=args.brand_name,
        logo_path=args.logo,
        terms=terms,
        payment_link=args.payment_link,
        output_file=output_file,
    )

    print(f"Proposal generated: {output_file}")


if __name__ == "__main__":
    main()
