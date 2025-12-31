"""Intelligent document classifier using NLP and ML."""

import re
import PyPDF2
import pdfplumber
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from rich.console import Console

console = Console()


@dataclass
class ClassificationResult:
    """Result of document classification."""
    document_type: str
    confidence: float
    display_name: str
    matched_patterns: List[str]
    matched_keywords: List[str]
    method: str  # 'ml', 'pattern', 'keyword', or 'hybrid'


class DocumentClassifier:
    """Intelligent classifier for document type detection."""

    def __init__(self, config: Dict[str, Any], rules: Dict[str, Any]):
        """Initialize document classifier.

        Args:
            config: Configuration dictionary
            rules: Classification rules dictionary
        """
        self.config = config
        self.rules = rules
        self.confidence_threshold = config['classification']['confidence_threshold']
        self.min_text_length = config['classification']['min_text_length']

        # Try to load spaCy model (optional)
        self.nlp = None
        self._load_nlp_model()

        # Initialize TF-IDF vectorizer for ML classification
        self.vectorizer = None
        self.tfidf_model = None
        self._initialize_ml_model()

    def _load_nlp_model(self):
        """Load spaCy NLP model if available."""
        try:
            import spacy
            model_name = "pt_core_news_lg"
            console.print(f"[cyan]Loading spaCy model: {model_name}...[/cyan]")
            self.nlp = spacy.load(model_name)
            console.print("[green]✓ spaCy model loaded successfully[/green]")
        except Exception as e:
            console.print(f"[yellow]⚠ spaCy model not available: {e}[/yellow]")
            console.print("[yellow]Run: python -m spacy download pt_core_news_lg[/yellow]")
            console.print("[yellow]Falling back to pattern/keyword matching[/yellow]")

    def _initialize_ml_model(self):
        """Initialize ML model for text classification."""
        if not self.config['classification'].get('use_ml_model', False):
            return

        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.naive_bayes import MultinomialNB
            from sklearn.pipeline import Pipeline

            self.vectorizer = TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 3),
                min_df=1,
                stop_words=self._get_stop_words()
            )

            console.print("[cyan]ML model initialized for document classification[/cyan]")
        except ImportError:
            console.print("[yellow]⚠ scikit-learn not available, using rule-based classification[/yellow]")

    def _get_stop_words(self) -> List[str]:
        """Get Portuguese stop words.

        Returns:
            List of stop words
        """
        return [
            'a', 'o', 'de', 'da', 'do', 'e', 'em', 'para', 'com', 'por',
            'um', 'uma', 'os', 'as', 'dos', 'das', 'no', 'na', 'ao', 'à'
        ]

    def classify_document(self, file_path: str, text_content: Optional[str] = None) -> Optional[ClassificationResult]:
        """Classify a document by analyzing its content.

        Args:
            file_path: Path to the document file
            text_content: Pre-extracted text content (optional)

        Returns:
            ClassificationResult or None if classification failed
        """
        # Extract text if not provided
        if text_content is None:
            text_content = self.extract_text(file_path)

        if not text_content or len(text_content) < self.min_text_length:
            console.print(f"[yellow]⚠ Insufficient text content for classification[/yellow]")
            return None

        # Try multiple classification methods
        results = []

        # 1. Pattern-based classification
        pattern_result = self._classify_by_patterns(text_content)
        if pattern_result:
            results.append(pattern_result)

        # 2. NLP-based classification
        if self.nlp:
            nlp_result = self._classify_by_nlp(text_content)
            if nlp_result:
                results.append(nlp_result)

        # 3. Keyword-based classification (fallback)
        keyword_result = self._classify_by_keywords(text_content)
        if keyword_result:
            results.append(keyword_result)

        # Select best result
        if not results:
            return None

        # Sort by confidence and return best match
        results.sort(key=lambda x: x.confidence, reverse=True)
        best_result = results[0]

        if best_result.confidence >= self.confidence_threshold:
            console.print(
                f"[green]✓ Classified as '{best_result.display_name}' "
                f"(confidence: {best_result.confidence:.2%}, method: {best_result.method})[/green]"
            )
            return best_result
        else:
            console.print(
                f"[yellow]⚠ Low confidence classification: {best_result.confidence:.2%} "
                f"(threshold: {self.confidence_threshold:.2%})[/yellow]"
            )
            return None

    def _classify_by_patterns(self, text: str) -> Optional[ClassificationResult]:
        """Classify document using regex patterns.

        Args:
            text: Document text content

        Returns:
            ClassificationResult or None
        """
        best_match = None
        best_score = 0.0
        matched_patterns = []

        for doc_type, rules in self.rules.items():
            patterns = rules.get('patterns', [])
            if not patterns:
                continue

            matches = 0
            matched = []

            for pattern in patterns:
                try:
                    if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
                        matches += 1
                        matched.append(pattern)
                except re.error:
                    continue

            if matches > 0:
                # Calculate confidence based on number of pattern matches
                confidence = min(0.95, (matches / len(patterns)) * 0.8 + 0.2)

                # Apply confidence boost from rules
                confidence += rules.get('confidence_boost', 0)
                confidence = min(1.0, confidence)

                if confidence > best_score:
                    best_score = confidence
                    best_match = doc_type
                    matched_patterns = matched

        if best_match:
            return ClassificationResult(
                document_type=best_match,
                confidence=best_score,
                display_name=self.rules[best_match]['display_name'],
                matched_patterns=matched_patterns,
                matched_keywords=[],
                method='pattern'
            )

        return None

    def _classify_by_nlp(self, text: str) -> Optional[ClassificationResult]:
        """Classify document using NLP entity recognition.

        Args:
            text: Document text content

        Returns:
            ClassificationResult or None
        """
        if not self.nlp:
            return None

        try:
            # Process text with spaCy (limit to first 100k chars for performance)
            doc = self.nlp(text[:100000])

            # Extract named entities
            entities = {}
            for ent in doc.ents:
                entities[ent.label_] = entities.get(ent.label_, 0) + 1

            # Match against rule entities
            best_match = None
            best_score = 0.0

            for doc_type, rules in self.rules.items():
                required_entities = rules.get('entities', [])
                if not required_entities:
                    continue

                # Calculate entity match score
                matched = sum(1 for ent in required_entities if ent in entities)
                if matched > 0:
                    score = (matched / len(required_entities)) * 0.7 + 0.2

                    # Apply confidence boost
                    score += rules.get('confidence_boost', 0)
                    score = min(1.0, score)

                    if score > best_score:
                        best_score = score
                        best_match = doc_type

            if best_match:
                return ClassificationResult(
                    document_type=best_match,
                    confidence=best_score,
                    display_name=self.rules[best_match]['display_name'],
                    matched_patterns=[],
                    matched_keywords=[],
                    method='nlp'
                )

        except Exception as e:
            console.print(f"[yellow]NLP classification failed: {e}[/yellow]")

        return None

    def _classify_by_keywords(self, text: str) -> Optional[ClassificationResult]:
        """Classify document using keyword matching.

        Args:
            text: Document text content

        Returns:
            ClassificationResult or None
        """
        text_lower = text.lower()
        best_match = None
        best_score = 0.0
        matched_keywords = []

        for doc_type, rules in self.rules.items():
            keywords = rules.get('keywords', [])
            if not keywords:
                continue

            matches = 0
            matched = []

            for keyword in keywords:
                if keyword.lower() in text_lower:
                    matches += 1
                    matched.append(keyword)

            if matches > 0:
                # Calculate confidence based on keyword density
                confidence = min(0.85, (matches / len(keywords)) * 0.6 + 0.15)

                if confidence > best_score:
                    best_score = confidence
                    best_match = doc_type
                    matched_keywords = matched

        if best_match:
            return ClassificationResult(
                document_type=best_match,
                confidence=best_score,
                display_name=self.rules[best_match]['display_name'],
                matched_patterns=[],
                matched_keywords=matched_keywords,
                method='keyword'
            )

        return None

    def extract_text(self, file_path: str) -> str:
        """Extract text from document file.

        Args:
            file_path: Path to document

        Returns:
            Extracted text content
        """
        path = Path(file_path)
        extension = path.suffix.lower()

        try:
            if extension == '.pdf':
                return self._extract_pdf_text(file_path)
            elif extension == '.docx':
                return self._extract_docx_text(file_path)
            elif extension == '.txt':
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            else:
                console.print(f"[yellow]Unsupported file type: {extension}[/yellow]")
                return ""
        except Exception as e:
            console.print(f"[red]Text extraction failed for {path.name}: {e}[/red]")
            return ""

    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF file.

        Args:
            file_path: Path to PDF file

        Returns:
            Extracted text
        """
        text = ""

        # Try pdfplumber first (better for complex PDFs)
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

            if text.strip():
                console.print(f"[green]✓ Extracted text from PDF using pdfplumber[/green]")
                return text
        except Exception as e:
            console.print(f"[yellow]pdfplumber failed: {e}[/yellow]")

        # Fallback to PyPDF2
        try:
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"

            if text.strip():
                console.print(f"[green]✓ Extracted text from PDF using PyPDF2[/green]")
                return text
        except Exception as e:
            console.print(f"[yellow]PyPDF2 failed: {e}[/yellow]")

        # Try OCR if enabled and text extraction failed
        if self.config['processing'].get('enable_ocr', False):
            console.print("[cyan]Attempting OCR...[/cyan]")
            text = self._ocr_pdf(file_path)

        return text

    def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX file.

        Args:
            file_path: Path to DOCX file

        Returns:
            Extracted text
        """
        try:
            from docx import Document
            doc = Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            console.print(f"[green]✓ Extracted text from DOCX[/green]")
            return text
        except Exception as e:
            console.print(f"[red]DOCX extraction failed: {e}[/red]")
            return ""

    def _ocr_pdf(self, file_path: str) -> str:
        """Perform OCR on PDF file.

        Args:
            file_path: Path to PDF file

        Returns:
            OCR extracted text
        """
        try:
            import pytesseract
            from pdf2image import convert_from_path
            from PIL import Image

            # Convert PDF to images
            images = convert_from_path(file_path, dpi=300)

            text = ""
            languages = "+".join(self.config['processing'].get('ocr_languages', ['por']))

            for i, image in enumerate(images):
                console.print(f"[cyan]OCR processing page {i+1}/{len(images)}...[/cyan]")
                page_text = pytesseract.image_to_string(image, lang=languages)
                text += page_text + "\n"

            if text.strip():
                console.print(f"[green]✓ OCR completed successfully[/green]")

            return text
        except ImportError:
            console.print("[yellow]⚠ OCR dependencies not installed (pytesseract, pdf2image)[/yellow]")
            return ""
        except Exception as e:
            console.print(f"[red]OCR failed: {e}[/red]")
            return ""
