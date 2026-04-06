# Client Proposal PDF CLI

This repository includes a command-line tool that generates branded client proposal PDFs.

## Features
- Accepts client name, project scope, and price from CLI arguments.
- Supports brand name and optional logo image.
- Adds terms and conditions (from a file or default terms).
- Embeds a clickable payment link in the PDF.
- Writes a proposal PDF file ready to send to clients.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python proposal_cli.py \
  "Acme Corp" \
  "Design and build a responsive marketing website with CMS integration." \
  12500 \
  --brand-name "Bluepeak Studio" \
  --logo ./assets/logo.png \
  --payment-link "https://pay.example.com/invoice/1234" \
  --terms-file ./terms.txt \
  --currency USD \
  --output acme_proposal.pdf
```

### Minimum required arguments

```bash
python proposal_cli.py "Acme Corp" "Website redesign" 3500 --payment-link "https://pay.example.com/abc"
```

The command generates a PDF (default filename: `proposal_<client_name>.pdf`).
