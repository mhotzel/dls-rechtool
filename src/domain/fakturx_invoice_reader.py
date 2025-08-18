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

    def __init__(self, xmlpath: str, optional: bool = False):
        self.xmlpath = xmlpath
        self.optional = optional

    def getElement(self, element: Element) -> Element | None:
        """Extrahiert ein Element """
        result = element.find(self.xmlpath, namespaces=self.namespaces)
        if result is None and self.optional == False:
            raise ValueError(
                f"element not found on path '{self.xmlpath}'"
            )

        return result

    def getAllElements(self, element: Element) -> list[Element] | None:
        """Extrahiert alle Elemente"""
        result = element.findall(self.xmlpath, namespaces=self.namespaces)
        if result is None and self.optional == False:
            raise ValueError(
                f"element not found on path '{self.xmlpath}'"
            )

        return result


POSITION_MAPPING = {
    'pos_nr': KeyMapping('.//ram:AssociatedDocumentLineDocument/ram:LineID'),
    'gtin':  KeyMapping('.//ram:SpecifiedTradeProduct/ram:GlobalID', optional=True),
    'suppl_prod_id': KeyMapping('.//ram:SpecifiedTradeProduct/ram:SellerAssignedID'),
    'prod_name': KeyMapping('.//ram:SpecifiedTradeProduct/ram:Name'),
    'order_id': KeyMapping('.//ram:SpecifiedLineTradeAgreement/ram:BuyerOrderReferencedDocument/ram:LineID', optional=True)
}


class FakturXInvoiceReader():
    """Liest eine Faktur-X-Datei ein"""

    namespaces = {
        'rsm': 'urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100',
        'ram': 'urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100',
        'udt': 'urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100'
    }

    def __init__(self, invoiceData: str):
        self.root = ET.fromstring(invoiceData)

    def isValidEN16931(self):
        """Prueft, ob sich das Dokument selbst als konform zur Spezifikation
        urn:cen.eu:en16931:2017 betrachtet."""

        mapping = KeyMapping(
            './/rsm:ExchangedDocumentContext/ram:GuidelineSpecifiedDocumentContextParameter/ram:ID')
        try:
            res = mapping.getElement(self.root)
            if res.text == 'urn:cen.eu:en16931:2017':
                return True
        except ValueError as ve:
            return False

    def getSellerTradeId(self) -> str:
        """Liefert die eindeutige ID des Lieferanten"""
        elem = KeyMapping(
            './/rsm:SupplyChainTradeTransaction/ram:ApplicableHeaderTradeAgreement/ram:SellerTradeParty/ram:ID').getElement(self.root)
        return elem.text

    def getSellerTradeName(self) -> str:
        """Liefert den Namen des Lieferanten"""
        elem = KeyMapping(
            './/rsm:SupplyChainTradeTransaction/ram:ApplicableHeaderTradeAgreement/ram:SellerTradeParty/ram:Name').getElement(self.root)
        return elem.text

    def getSellerTaxRegistration(self) -> str:
        """Steuer-ID des Lieferanten"""
        taxId = KeyMapping(
            './/rsm:SupplyChainTradeTransaction/ram:ApplicableHeaderTradeAgreement/ram:SellerTradeParty/ram:SpecifiedTaxRegistration/ram:ID').getElement(self.root)
        return taxId.text

    def getSellerTaxRegistrationType(self) -> str:
        """Steuer-ID des Lieferanten. 'VA' = UStID, 'FC' = Steuernummer"""
        taxId = KeyMapping(
            './/rsm:SupplyChainTradeTransaction/ram:ApplicableHeaderTradeAgreement/ram:SellerTradeParty/ram:SpecifiedTaxRegistration/ram:ID').getElement(self.root)
        taxType = taxId.get('schemeID', '')
        return taxType

    def getCustomerId(self) -> str:
        """Kundennummer bei Lieferanten"""
        customerId = KeyMapping(
            './/rsm:SupplyChainTradeTransaction/ram:ApplicableHeaderTradeAgreement/ram:BuyerTradeParty/ram:ID').getElement(self.root)
        return customerId.text

    def getInvoiceId(self) -> str:
        """Ermittelt die Rechnungsnummer"""

        mapping = KeyMapping('.//rsm:ExchangedDocument/ram:ID')
        return mapping.getElement(self.root).text

    def getTypeCode(self):
        """Ermittelt den Typ des Dokuments. Siehe auch die Uebersicht gemaess
        Dictionary 'DOCUMENTYPECODES'"""

        mapping = KeyMapping('.//rsm:ExchangedDocument/ram:TypeCode')
        return mapping.getElement(self.root).text

    def getInvoiceDate(self) -> datetime.date:
        """Ermittelt das Rechnungsdatum"""
        return datetime.strptime(
            KeyMapping('.//rsm:ExchangedDocument/ram:IssueDateTime/udt:DateTimeString').getElement(self.root).text, "%Y%m%d").date().isoformat()

    def getInvoiceCurrencyCode(self) -> str:
        """Rechnungswährung"""
        currencyCode = KeyMapping(
            './/rsm:SupplyChainTradeTransaction/ram:ApplicableHeaderTradeSettlement/ram:InvoiceCurrencyCode').getElement(self.root)
        return currencyCode.text

    def getTradeTax(self) -> list[dict]:
        """Steuerbeträge"""
        taxes = KeyMapping(
            './/rsm:SupplyChainTradeTransaction/ram:ApplicableHeaderTradeSettlement/ram:ApplicableTradeTax').getAllElements(self.root)
        taxResult = []
        for tax in taxes:
            result = {}
            res = KeyMapping('.//ram:CalculatedAmount').getElement(tax)
            result['tax-amount'] = float(res.text)

            res = KeyMapping('.//ram:TypeCode').getElement(tax)
            result['tax-type-code'] = res.text

            res = KeyMapping('.//ram:BasisAmount').getElement(tax)
            result['tax-basis-amount'] = float(res.text)

            res = KeyMapping('.//ram:CategoryCode').getElement(tax)
            result['tax-cat-code'] = res.text

            res = KeyMapping('.//ram:RateApplicablePercent').getElement(tax)
            result['tax-percent'] = float(res.text)

            taxResult.append(result)

        return taxResult

    def getBillingPeriod(self) -> dict:
        """Rechnungsperiode"""
        billingDateStart = KeyMapping(
            './/rsm:SupplyChainTradeTransaction/ram:ApplicableHeaderTradeSettlement/ram:BillingSpecifiedPeriod/ram:StartDateTime/udt:DateTimeString').getElement(self.root)
        billingDateEnd = KeyMapping(
            './/rsm:SupplyChainTradeTransaction/ram:ApplicableHeaderTradeSettlement/ram:BillingSpecifiedPeriod/ram:EndDateTime/udt:DateTimeString').getElement(self.root)

        return {
            'billing-period-start': datetime.strptime(billingDateStart.text, '%Y%m%d').date().isoformat(),
            'billing-period-end': datetime.strptime(billingDateEnd.text, '%Y%m%d').date().isoformat()
        }

    def getInvoiceSummary(self) -> dict:
        """Endebetraege der Rechnung"""
        lineTotalAmount = float(KeyMapping(
            './/rsm:SupplyChainTradeTransaction/ram:ApplicableHeaderTradeSettlement/ram:SpecifiedTradeSettlementHeaderMonetarySummation/ram:LineTotalAmount').getElement(self.root).text)
        taxBasisTotalAmount = float(KeyMapping(
            './/rsm:SupplyChainTradeTransaction/ram:ApplicableHeaderTradeSettlement/ram:SpecifiedTradeSettlementHeaderMonetarySummation/ram:TaxBasisTotalAmount').getElement(self.root).text)
        taxTotalAmount = KeyMapping(
            './/rsm:SupplyChainTradeTransaction/ram:ApplicableHeaderTradeSettlement/ram:SpecifiedTradeSettlementHeaderMonetarySummation/ram:TaxTotalAmount').getElement(self.root)
        currency = taxTotalAmount.get('currencyID', '')
        roundingAmount = float(KeyMapping(
            './/rsm:SupplyChainTradeTransaction/ram:ApplicableHeaderTradeSettlement/ram:SpecifiedTradeSettlementHeaderMonetarySummation/ram:RoundingAmount').getElement(self.root).text)
        # Gesamtbetrag einschl. Steuern
        grandTotalAmount = float(KeyMapping(
            './/rsm:SupplyChainTradeTransaction/ram:ApplicableHeaderTradeSettlement/ram:SpecifiedTradeSettlementHeaderMonetarySummation/ram:GrandTotalAmount').getElement(self.root).text)
        # Vorauszahlungen
        totalPrepaidAmount = float(KeyMapping(
            './/rsm:SupplyChainTradeTransaction/ram:ApplicableHeaderTradeSettlement/ram:SpecifiedTradeSettlementHeaderMonetarySummation/ram:TotalPrepaidAmount').getElement(self.root).text)
        # Restbetrag
        duePayableAmount = float(KeyMapping(
            './/rsm:SupplyChainTradeTransaction/ram:ApplicableHeaderTradeSettlement/ram:SpecifiedTradeSettlementHeaderMonetarySummation/ram:DuePayableAmount').getElement(self.root).text)

        return {
            'line-total-amount': lineTotalAmount,
            'tax-basis-total-amount': taxBasisTotalAmount,
            'tax-total-amount': float(taxTotalAmount.text),
            'currency': currency,
            'rounding-amount': roundingAmount,
            'grand-total-amount': grandTotalAmount,
            'total-prepaid-amount': totalPrepaidAmount,
            'due-payable-amount': duePayableAmount
        }

    def getPositions(self) -> list[dict]:
        """Ermittelt die Positionen"""

        positions = []
        transaction_mapping = KeyMapping('.//rsm:SupplyChainTradeTransaction')
        transaction = transaction_mapping.getElement(self.root)
        allPositions = KeyMapping(
            './/ram:IncludedSupplyChainTradeLineItem').getAllElements(transaction)

        for idx, pos in enumerate(allPositions, start=1):
            result = {}
            pos_nr = KeyMapping(
                './/ram:AssociatedDocumentLineDocument/ram:LineID').getElement(pos)
            result['line-nr'] = int(pos_nr.text)

            gtin = KeyMapping(
                './/ram:SpecifiedTradeProduct/ram:GlobalID', optional=True).getElement(pos)
            if gtin is not None:
                result['gtin'] = gtin.text

            suppl_prod_id = KeyMapping(
                './/ram:SpecifiedTradeProduct/ram:SellerAssignedID').getElement(pos)
            if suppl_prod_id is not None:
                result['suppl-prod-id'] = suppl_prod_id.text

            prod_name = KeyMapping(
                './/ram:SpecifiedTradeProduct/ram:Name').getElement(pos)
            if prod_name is not None:
                result['prod-name'] = prod_name.text

            order_id = KeyMapping(
                './/ram:SpecifiedLineTradeAgreement/ram:BuyerOrderReferencedDocument/ram:LineID', optional=True).getElement(pos)
            if order_id is not None:
                result['order-id'] = order_id.text

            # Informativer Listenpreis als Einzelpreis.
            grossPrice = KeyMapping(
                './/ram:SpecifiedLineTradeAgreement/ram:GrossPriceProductTradePrice/ram:ChargeAmount').getElement(pos)
            result['gross-price'] = float(grossPrice.text)

            # BasisQuantity“ BT-149-0 sollte als Preiseinheit für den Listenpreis verstanden werden
            basisQuantity = KeyMapping(
                './/ram:SpecifiedLineTradeAgreement/ram:GrossPriceProductTradePrice/ram:BasisQuantity').getElement(pos)
            result['basis-quantity'] = float(basisQuantity.text)

            # Unit Codes pro Rechnungszeile wie 'XCT':
            # https://easyfirma.net/e-rechnung/xrechnung/codes#elementor-toc__heading-anchor-17
            quantityUnitCode = KeyMapping(
                './/ram:SpecifiedLineTradeAgreement/ram:GrossPriceProductTradePrice/ram:BasisQuantity').getElement(pos)
            result['basis-quantity-unit-code'] = quantityUnitCode.get(
                'unitCode', '')

            # Normaler Nettopreis. Das Element „BasisQuantity“ BT-149-0 sollte als Preiseinheit für den Nettopreis verstanden werden
            netPrice = KeyMapping(
                './/ram:SpecifiedLineTradeAgreement/ram:NetPriceProductTradePrice/ram:ChargeAmount').getElement(pos)
            result['net-price'] = float(netPrice.text)

            # Liefermenge
            billedQuantity = KeyMapping(
                './/ram:SpecifiedLineTradeDelivery/ram:BilledQuantity').getElement(pos)
            result['billed-quantity'] = float(billedQuantity.text)
            result['billed-quantity-unit-code'] = billedQuantity.get(
                'unitCode', '')

            # Steuer
            # VAT = Umsatzsteuer
            steuertyp = KeyMapping(
                './/ram:SpecifiedLineTradeSettlement/ram:ApplicableTradeTax/ram:TypeCode').getElement(pos)
            result['tax-type'] = steuertyp.text

            # 'S' = Regel-Umsatzsteuersatz
            steuerkategorie = KeyMapping(
                './/ram:SpecifiedLineTradeSettlement/ram:ApplicableTradeTax/ram:CategoryCode').getElement(pos)
            result['tax-cat'] = steuerkategorie.text

            # 'S' = Regel-Umsatzsteuersatz
            steuersatz = KeyMapping(
                './/ram:SpecifiedLineTradeSettlement/ram:ApplicableTradeTax/ram:RateApplicablePercent').getElement(pos)
            result['tax-rate'] = float(steuersatz.text)

            rechnungsperiode_start = KeyMapping(
                './/ram:SpecifiedLineTradeSettlement/ram:BillingSpecifiedPeriod/ram:StartDateTime/udt:DateTimeString', optional=True).getElement(pos)
            if rechnungsperiode_start is not None:
                result['billing-period-start'] = datetime.strptime(
                    rechnungsperiode_start.text, "%Y%m%d").date().isoformat()

            rechnungsperiode_ende = KeyMapping(
                './/ram:SpecifiedLineTradeSettlement/ram:BillingSpecifiedPeriod/ram:EndDateTime/udt:DateTimeString', optional=True).getElement(pos)
            if rechnungsperiode_ende is not None:
                result['billing-period-end'] = datetime.strptime(
                    rechnungsperiode_ende.text, '%Y%m%d').date().isoformat()

            zeilensumme = KeyMapping(
                './/ram:SpecifiedLineTradeSettlement/ram:SpecifiedTradeSettlementLineMonetarySummation/ram:LineTotalAmount').getElement(pos)
            result['line-total-amount'] = float(zeilensumme.text)

            issuer_prod_id = KeyMapping(
                './/ram:SpecifiedLineTradeSettlement/ram:AdditionalReferencedDocument/ram:IssuerAssignedID', optional=True).getElement(pos)
            if issuer_prod_id is not None:
                result['issuer-prod-id'] = issuer_prod_id.text

            issuer_prod_type_code = KeyMapping(
                './/ram:SpecifiedLineTradeSettlement/ram:AdditionalReferencedDocument/ram:TypeCode', optional=True).getElement(pos)
            if issuer_prod_type_code is not None:
                result['issuer-prod-type-code'] = issuer_prod_type_code.text

            positions.append(result)

        return positions

    def to_dict(self):
        """Erzeugt aus dem Rechnungsobjekt in Dictionary, welches z.B. dann in ein JSON-Objekt verpackt werden kann"""

        return {
            'invoice-head': {
                'customer-id': self.getCustomerId(),
                'invoice-id': self.getInvoiceId(),
                'invoice-type-code': self.getTypeCode(),
                'invoice-date': self.getInvoiceDate(),
                'seller-trade-id': self.getSellerTradeId(),
                'seller-trade-name': self.getSellerTradeName(),
                'billing-period': self.getBillingPeriod(),
                'seller-tax-registration': self.getSellerTaxRegistration(),
                'seller-tax-registration-type': self.getSellerTaxRegistrationType()
            },
            'invoice-positions': self.getPositions(),
            'tax': self.getTradeTax(),
            'invoice-summary': self.getInvoiceSummary()
        }
