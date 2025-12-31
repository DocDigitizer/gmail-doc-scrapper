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
        """Create test classification rules."""
        return {
            "faturas": {
                "display_name": "Faturas",
                "keywords": ["fatura", "invoice", "NIF"],
                "patterns": [r"Fatura\s+N[ºo.]?\s*\d+"],
                "entities": ["MONEY", "ORG"],
                "confidence_boost": 0.1
            },
            "contratos": {
                "display_name": "Contratos",
                "keywords": ["contrato", "acordo"],
                "patterns": [r"Contrato\s+de"],
                "entities": ["PERSON", "ORG"],
                "confidence_boost": 0.15
            }
        }

    @pytest.fixture
    def classifier(self, config, rules):
        """Create DocumentClassifier instance."""
        return DocumentClassifier(config, rules)

    def test_classify_by_patterns(self, classifier):
        """Test pattern-based classification."""
        text = """
        FATURA N.º 2024/001
        NIF: 123456789
        Total: 150.00 EUR
        """

        result = classifier._classify_by_patterns(text)

        assert result is not None
        assert result.document_type == "faturas"
        assert result.confidence > 0.0
        assert len(result.matched_patterns) > 0

    def test_classify_by_keywords(self, classifier):
        """Test keyword-based classification."""
        text = """
        Este documento é uma fatura oficial.
        Inclui o NIF do cliente e total a pagar.
        """

        result = classifier._classify_by_keywords(text)

        assert result is not None
        assert result.document_type == "faturas"
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


if __name__ == '__main__':
    pytest.main([__file__])
