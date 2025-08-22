from dataclasses import dataclass
from typing import Sequence
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
from datetime import datetime

# Übersicht der Schema-IDs in './/ram:SpecifiedTradeProduct/ram:GlobalID'
# https://docs.peppol.eu/poacc/billing/3.0/codelist/ICD/
# schemaID="0160" it die GTIN

DOCUMENTYPECODES = {
    '71': 'Request for payment',
    '80': 'Debit note related to goods or services',
    '81': 'Credit note related to goods or services',
    '82': 'Metered services invoice',
    '83': 'Credit note related to financial adjustments',
    '84': 'Debit note related to financial adjustments',
    '102': 'Tax notification',
    '130': 'Rechnungsdatenblatt',
    '202': 'Verkürzte Baurechnung',
    '203': 'Vorläufige Baurechnung',
    '204': 'Baurechnung',
    '211': 'Zwischen-(abschlags-)rechnung',
    '218': 'Final payment request based on completion of work',
    '219': 'Payment request for completed units',
    '261': 'Self billed credit note',
    '262': 'Consolidated credit note - goods and services',
    '295': 'Price variation invoice',
    '296': 'Credit note for price variation',
    '308': 'Delcredere credit note',
    '325': 'Proformarechnung',
    '326': 'Teilrechnung',
    '331': 'Commercial invoice which includes a packing list',
    '380': 'Handelsrechnung',
    '381': 'Gutschriftanzeige',
    '382': 'Provisionsmitteilung',
    '383': 'Belastungsanzeige',
    '384': 'Rechnungskorrektur',
    '385': 'Konsolidierte Rechnung',
    '386': 'Vorauszahlungsrechnung',
    '387': 'Mietrechnung',
    '388': 'Steuerrechnung',
    '389': 'Selbst ausgestellte Rechnung (Gutschrift im Gutschriftsverfahren)',
    '390': 'Delkredere-Rechnung',
    '393': 'Inkasso-Rechnung',
    '394': 'Leasing-Rechnung',
    '395': 'Konsignationsrechnung',
    '396': 'Inkasso-Gutschrift',
    '420': 'Optical Character Reading (OCR) payment credit note',
    '456': 'Belastungsanzeige',
    '457': 'Storno einer Belastung.',
    '458': 'Storno einer Gutschrift',
    '527': 'Self billed debit note',
    '532': 'Gutschrift des Spediteurs',
    '553': 'Forwarders invoice discrepancy report',
    '575': 'Rechnung des Versicherers',
    '623': 'Speditionsrechnung',
    '633': 'Hafenkostenrechnung',
    '751': 'Invoice information for accounting purposes',
    '780': 'Frachtrechnung',
    '817': 'Claim notification',
    '870': 'Konsulatsfaktura',
    '875': 'Partial construction invoice',
    '876': 'Partial final construction invoice',
    '877': 'Final construction invoice',
    '935': 'Zollrechnung'
}


class KeyMapping:
    """Definiert Positionen in der Rechnung, deren DLS-internen Namen, den XML-Pfad sowie Dinge wie 'MUSS-Feld' usw. """

    namespaces = {
        'rsm': 'urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100',
        'ram': 'urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100',
        'udt': 'urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100'
    }

    def __init__(self, xmldoc: str, optional: bool = True):
        self.xmlpath = xmldoc
        self.optional = optional

    def getElementAsFloat(self, element: Element) -> float | None:
        """Extrahiert ein Element als float"""
        result = element.find(self.xmlpath, namespaces=self.namespaces)
        if result is None and self.optional == False:
            raise ValueError(
                f"element not found on path '{self.xmlpath}'"
            )

        return float(result.text) if result is not None else None

    def getElementAsInt(self, element: Element) -> int | None:
        """Extrahiert ein Element als int"""
        result = element.find(self.xmlpath, namespaces=self.namespaces)
        if result is None and self.optional == False:
            raise ValueError(
                f"element not found on path '{self.xmlpath}'"
            )

        return int(result.text) if result is not None else None

    def getElement(self, element: Element) -> str | None:
        """Extrahiert ein Element """
        result = element.find(self.xmlpath, namespaces=self.namespaces)
        if result is None and self.optional == False:
            raise ValueError(
                f"element not found on path '{self.xmlpath}'"
            )

        return result.text if result is not None else None

    def getAttribute(self, element: Element, attribute: str) -> str | None:
        """Extrahiert ein Attribut eines Elements"""
        result = element.find(self.xmlpath, namespaces=self.namespaces)
        if result is None and self.optional == False:
            raise ValueError(
                f"attribute '{attribute}' not found on path '{self.xmlpath}'"
            )
       
        return result.get(attribute) if result is not None else None

    def getAllElements(self, element: Element) -> list[Element] | None:
        """Extrahiert alle Elemente"""
        result = element.findall(self.xmlpath, namespaces=self.namespaces)
        if result is None and self.optional == False:
            raise ValueError(
                f"element not found on path '{self.xmlpath}'"
            )

        return result


@dataclass
class ApplicableTradeTax:
    typeCode: str
    categoryCode: str
    rateApplicablePercent: float | None = None


@dataclass
class ProductTradePrice:
    type: str
    chargeAmount: float | None = None
    basisQuantity: float | None = None
    unitCode: str | None = None

@dataclass
class FakturXInvoicePosition:
    idx: int
    lineId: str  # ram:AssociatedDocumentLineDocument/ram:LineID / MUSS
    # ram:SpecifiedTradeProduct/ram:GlobalID / und SchemaId / Kann
    globalproductId: tuple[str, str] | None = None
    # ram:SpecifiedTradeProduct/ram:SellerAssignedID / Optional
    sellerAssignedId: str | None = None
    # ram:SpecifiedTradeProduct/ram:BuyerAssignedID / Optional
    buyerAssignedId: str | None = None
    name: str | None = None  # ram:SpecifiedTradeProduct/ram:Name / MUSS

    # ram:SpecifiedLineTradeAgreement/ram:GrossPriceProductTradePrice
    grossPriceProductTradePrice: ProductTradePrice | None = None

    # ram:SpecifiedLineTradeAgreement/ram:NetPriceProductTradePrice
    netPriceProductTradePrice: ProductTradePrice | None = None

    billedQuantity: float | None = None
    # ram:SpecifiedLineTradeDelivery/ram:BilledQuantity/@unitCode / Optional
    billedQuantityUnitCode: str | None = None
    # ram:SpecifiedLineTradeSettlement/ram:ApplicableTradeTax / MUSS
    applicableTradeTax: str | None = None
    # ram:SpecifiedLineTradeSettlement/ram:SpecifiedTradeSettlementLineMonetarySummation/ram:LineTotalAmount / MUSS
    lineTotalAmount: float | None = None


class FakturXInvoice():
    """Liest eine Faktur-X-Datei ein"""

    namespaces = {
        'rsm': 'urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100',
        'ram': 'urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100',
        'udt': 'urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100'
    }

    def __init__(self, invoiceData: str):
        self.root = ET.fromstring(invoiceData)

        self.invoice = self.root.find(
            'rsm:ExchangedDocumentContext/ram:GuidelineSpecifiedDocumentContextParameter/ram:ID', self.namespaces)
        if self.root is None:
            raise ValueError("not a valid Faktur-X invoice")

    @property
    def invoiceNumber(self) -> str:
        """Liefert die Rechnungsnummer"""
        elem = self.root.find('rsm:ExchangedDocument/ram:ID', self.namespaces)
        return elem.text

    @property
    def invoiceType(self) -> str:
        """Liefert den Typ der Rechnung"""
        elem = self.root.find(
            'rsm:ExchangedDocument/ram:TypeCode', self.namespaces)
        return elem.text

    @property
    def invoiceDate(self) -> str:
        """Liefert das Rechnungsdatum"""
        elem = self.root.find(
            'rsm:ExchangedDocument/ram:IssueDateTime/udt:DateTimeString', self.namespaces)
        return datetime.strptime(elem.text, '%Y%m%d').date()

    @property
    def sellerName(self) -> str:
        """Liefert den Namen des Verkäufers. Muss laut Standard immer vorhanden sein.
        BT-27"""
        elem = self.root.find(
            'rsm:SupplyChainTradeTransaction/ram:ApplicableHeaderTradeAgreement/ram:SellerTradeParty/ram:Name', self.namespaces)
        if elem is None:
            raise ValueError("Seller name not found")
        return elem.text

    @property
    def sellerId(self) -> str:
        """Liefert die ID des Verkäufers. Muss laut Standard nicht vorhanden sein.
        Alternativ kann auch die GlobalID des Verkäufers verwendet werden, die aber auch nicht zwingend vorhanden sein muss.
        BT-29
        """
        elem = self.root.find(
            'rsm:SupplyChainTradeTransaction/ram:ApplicableHeaderTradeAgreement/ram:SellerTradeParty/ram:ID', self.namespaces)
        return elem.text if elem is not None else None

    @property
    def sellerGlobalId(self) -> tuple:
        """Liefert die GlobalID des Verkäufers und die dazugehörige SchemaID, welche die Herkunft der GlobalID beschreibt. Muss laut Standard nicht vorhanden sein.
        Alternativ kann auch die ID des Verkäufers verwendet werden, die aber auch nicht zwingend vorhanden sein muss.
        Ist die GlobalID vorhanden, ist sie eindeutig und kann auch für die Identifikation des Verkäufers verwendet werden.
        BT-29-0, BT-29-1
        """
        elem = self.root.find(
            'rsm:SupplyChainTradeTransaction/ram:ApplicableHeaderTradeAgreement/ram:SellerTradeParty/ram:GlobalID', self.namespaces)
        schemaId = elem.get('schemeID') if elem is not None else None
        if elem is not None:
            return (elem.text, schemaId)
        return (None, None)

    @property
    def invoicePositions(self) -> Sequence[FakturXInvoicePosition]:
        """Liefert die Positionen der Rechnung"""

        lineIdMapping = KeyMapping(
            'ram:AssociatedDocumentLineDocument/ram:LineID', optional=False)
        globalproductIdMapping = KeyMapping(
            'ram:SpecifiedTradeProduct/ram:GlobalID')
        sellerAssignedIdMapping = KeyMapping(
            'ram:SpecifiedTradeProduct/ram:SellerAssignedID')
        buyerAssignedIdMapping = KeyMapping(
            'ram:SpecifiedTradeProduct/ram:BuyerAssignedID')
        prodNameMapping = KeyMapping('ram:SpecifiedTradeProduct/ram:Name')
        grossPriceChargeAmountMapping = KeyMapping(
            'ram:SpecifiedLineTradeAgreement/ram:GrossPriceProductTradePrice/ram:ChargeAmount')
        grossPriceBasisQuantityMapping = KeyMapping(
            'ram:SpecifiedLineTradeAgreement/ram:GrossPriceProductTradePrice/ram:BasisQuantity')
        netPriceChargeAmountMapping = KeyMapping(
            'ram:SpecifiedLineTradeAgreement/ram:NetPriceProductTradePrice/ram:ChargeAmount', optional=False)
        netPriceBasisQuantityMapping = KeyMapping(
            'ram:SpecifiedLineTradeAgreement/ram:NetPriceProductTradePrice/ram:BasisQuantity')
        billedQuantityMapping = KeyMapping(
            'ram:SpecifiedLineTradeDelivery/ram:BilledQuantity', optional=True)

        applicableTradeTaxTypeCodeMapping = KeyMapping(
            'ram:SpecifiedLineTradeSettlement/ram:ApplicableTradeTax/ram:TypeCode', optional=False)

        applicableTradeTaxCategoryCodeMapping = KeyMapping(
            'ram:SpecifiedLineTradeSettlement/ram:ApplicableTradeTax/ram:CategoryCode', optional=False)

        applicableTradeTaxRateApplicablePercentMapping = KeyMapping(
            'ram:SpecifiedLineTradeSettlement/ram:ApplicableTradeTax/ram:RateApplicablePercent', optional=True)

        lineTotalAmountMapping = KeyMapping(
            'ram:SpecifiedLineTradeSettlement/ram:SpecifiedTradeSettlementLineMonetarySummation/ram:LineTotalAmount', optional=False)

        positions = []
        posList = self.root.findall(
            'rsm:SupplyChainTradeTransaction/ram:IncludedSupplyChainTradeLineItem', self.namespaces)
        for idx, pos in enumerate(posList):
            # Wichtig: Die Positionsnummer ist zumindest bei Fleischerei Kurz NICHT eindeutig,
            # obwohl das m.E. so Vorschrift ist! Deswegen ein separater Positionszähler
            positions.append(
                FakturXInvoicePosition(
                    idx=idx,
                    lineId=lineIdMapping.getElement(pos),
                    globalproductId=(globalproductIdMapping.getElement(
                        pos), globalproductIdMapping.getAttribute(pos, 'schemeID')),
                    sellerAssignedId=sellerAssignedIdMapping.getElement(pos),
                    buyerAssignedId=buyerAssignedIdMapping.getElement(pos),
                    name=prodNameMapping.getElement(pos),
                    grossPriceProductTradePrice=ProductTradePrice(
                        type='grossPrice',
                        chargeAmount=grossPriceChargeAmountMapping.getElementAsFloat(
                            pos),
                        basisQuantity=grossPriceBasisQuantityMapping.getElementAsFloat(
                            pos),
                        unitCode=grossPriceBasisQuantityMapping.getAttribute(
                            pos, 'unitCode')
                    ),
                    netPriceProductTradePrice=ProductTradePrice(
                        type='netPrice',
                        chargeAmount=netPriceChargeAmountMapping.getElementAsFloat(
                            pos),
                        basisQuantity=netPriceBasisQuantityMapping.getElementAsFloat(
                            pos),
                        unitCode=netPriceBasisQuantityMapping.getAttribute(
                            pos, 'unitCode')
                    ),
                    billedQuantity=billedQuantityMapping.getElementAsFloat(
                        pos),
                    billedQuantityUnitCode=billedQuantityMapping.getAttribute(
                        pos, 'unitCode'),
                    applicableTradeTax=ApplicableTradeTax(
                        typeCode=applicableTradeTaxTypeCodeMapping.getElement(
                            pos),
                        categoryCode=applicableTradeTaxCategoryCodeMapping.getElement(
                            pos),
                        rateApplicablePercent=applicableTradeTaxRateApplicablePercentMapping.getElement(
                            pos)
                    ),
                    lineTotalAmount=lineTotalAmountMapping.getElementAsFloat(
                        pos)
                )
            )
        return positions

    def __repr__(self):
        result = ""
        result += f"FakturXInvoice(invoiceType={self.invoiceType})"
        result += f", invoiceType={self.invoiceType})"
        result += f", invoiceNumber={self.invoiceNumber})"
        result += f", invoiceDate={repr(self.invoiceDate)})"
        result += f", sellerName={self.sellerName})"
        result += f", sellerId={self.sellerId})"
        result += f", sellerGlobalId={self.sellerGlobalId})"
        result += f", invoicePositions={self.invoicePositions}))"

        return result