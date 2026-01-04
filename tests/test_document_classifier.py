"""Tests for document classifier."""

import pytest
from pathlib import Path
from src.document_classifier import DocumentClassifier, ClassificationResult


class TestDocumentClassifier:
    """Test cases for DocumentClassifier."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return {
            "classification": {
                "confidence_threshold": 0.7,
                "min_text_length": 100,
                "use_ml_model": False
            },
            "processing": {
                "enable_ocr": False,
                "ocr_languages": ["por", "eng"]
            }
        }

    @pytest.fixture
    def rules(self):
        """Create test classification rules (invoices and receipts only)."""
        return {
            "invoices": {
                "display_name": "Invoices",
                "keywords": ["fatura", "invoice", "factura", "NIF", "bill"],
                "patterns": [r"Fatura\s+N[ºo.]?\s*\d+", r"Invoice\s*#?\s*\d+"],
                "entities": ["MONEY", "ORG", "DATE"],
                "confidence_boost": 0.15
            },
            "receipts": {
                "display_name": "Receipts",
                "keywords": ["receipt", "recibo", "comprovante", "payment received"],
                "patterns": [r"Receipt\s*#?\s*\d+", r"Recibo\s+N[ºo.]?\s*\d+"],
                "entities": ["MONEY", "DATE"],
                "confidence_boost": 0.10
            }
        }

    @pytest.fixture
    def classifier(self, config, rules):
        """Create DocumentClassifier instance."""
        return DocumentClassifier(config, rules)

    def test_classify_by_patterns(self, classifier):
        """Test pattern-based classification for invoices."""
        text = """
        FATURA N.º 2024/001
        NIF: 123456789
        Total: 150.00 EUR
        """

        result = classifier._classify_by_patterns(text)

        assert result is not None
        assert result.document_type == "invoices"
        assert result.confidence > 0.0
        assert len(result.matched_patterns) > 0

    def test_classify_by_keywords(self, classifier):
        """Test keyword-based classification for invoices."""
        text = """
        Este documento é uma fatura oficial.
        Inclui o NIF do cliente e total a pagar.
        """

        result = classifier._classify_by_keywords(text)

        assert result is not None
        assert result.document_type == "invoices"
        assert len(result.matched_keywords) > 0

    def test_classify_by_patterns_receipt(self, classifier):
        """Test pattern-based classification for receipts."""
        text = """
        RECEIPT #2024-456
        Payment Received
        Amount Paid: $75.00
        """

        result = classifier._classify_by_patterns(text)

        assert result is not None
        assert result.document_type == "receipts"
        assert result.confidence > 0.0
        assert len(result.matched_patterns) > 0

    def test_classify_by_keywords_receipt(self, classifier):
        """Test keyword-based classification for receipts."""
        text = """
        Thank you for your payment.
        Receipt number: 12345
        Payment received with thanks.
        """

        result = classifier._classify_by_keywords(text)

        assert result is not None
        assert result.document_type == "receipts"
        assert len(result.matched_keywords) > 0

    def test_classify_insufficient_text(self, classifier):
        """Test classification with insufficient text."""
        text = "short"

        result = classifier.classify_document(
            file_path=None,
            text_content=text
        )

        assert result is None

    def test_extract_text_from_txt(self, classifier, tmp_path):
        """Test text extraction from plain text file."""
        test_file = tmp_path / "test.txt"
        test_content = "This is a test document"

        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)

        extracted = classifier.extract_text(str(test_file))

        assert extracted == test_content

    def test_classify_email_with_invoice_subject(self, classifier):
        """Test v2.0 email classification with invoice in subject."""
        subject = "Fatura N.º 2024/001 - Pagamento Pendente"
        body = "Prezado cliente, segue em anexo a fatura do mês."

        result = classifier.classify_email(subject, body)

        assert result is not None
        assert result.document_type == "invoices"
        assert result.confidence >= 0.5

    def test_classify_email_with_invoice_body(self, classifier):
        """Test v2.0 email classification with invoice keywords in body."""
        subject = "Documento importante"
        body = """
        Prezado cliente,

        Segue em anexo a fatura referente aos serviços prestados.
        NIF: 123456789
        Total: 150.00 EUR
        """

        result = classifier.classify_email(subject, body)

        assert result is not None
        assert result.document_type == "invoices"

    def test_classify_email_with_receipt_subject(self, classifier):
        """Test v2.0 email classification with receipt in subject."""
        subject = "Receipt #2024-456 - Payment Confirmed"
        body = "Thank you for your payment. Please find your receipt attached."

        result = classifier.classify_email(subject, body)

        assert result is not None
        assert result.document_type == "receipts"
        assert result.confidence >= 0.5

    def test_classify_email_with_receipt_body(self, classifier):
        """Test v2.0 email classification with receipt keywords in body."""
        subject = "Payment confirmation"
        body = """
        Dear customer,

        Your payment has been received successfully.
        Receipt number: 2024-789
        Amount paid: $150.00
        """

        result = classifier.classify_email(subject, body)

        assert result is not None
        assert result.document_type == "receipts"

    def test_classify_email_empty_content(self, classifier):
        """Test v2.0 email classification with empty content."""
        result = classifier.classify_email("", "")

        assert result is None

    def test_classify_email_no_match(self, classifier):
        """Test v2.0 email classification with no matching rules."""
        subject = "Hello, how are you?"
        body = "This is just a friendly email with no financial content."

        result = classifier.classify_email(subject, body)

        assert result is None


if __name__ == '__main__':
    pytest.main([__file__])
