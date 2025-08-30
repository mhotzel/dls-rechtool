
from pathlib import Path
from pypdf import PdfReader
from domain.fakturx_invoice import FakturXInvoice


class InvalidInvoiceException(Exception):

    def __init__(self, *args):
        super().__init__(*args)


class ZugferdInvoiceDocument:
    """Ein PDF-Dokument mit einer ZUGFeRD-Rechnung"""

    def __init__(self, pdf_file: Path):
        self.pdf_file = pdf_file
        reader = PdfReader(self.pdf_file)

        if len(reader.attachments) != 1:
            raise InvalidInvoiceException(
                f"file '{self.pdf_file}' is not a valid ZUGFeRD-Invoice: not attachement")

        try:
            invoice_data = str(
                reader.attachments['factur-x.xml'][0], encoding='utf8')
        except:
            raise InvalidInvoiceException(
                "file '{self.pdf_file}' is not a valid ZUGFeRD-Invoice: not attachement named 'factur-x.xml'")

        self.invoice = FakturXInvoice(invoice_data)
