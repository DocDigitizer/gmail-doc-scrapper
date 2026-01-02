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
            self.nlp = spacy.load(model_name)
            console.print("[green]✓ spaCy NLP model loaded[/green]")
        except Exception:
            # Dependencies checked at startup, silently fall back to pattern/keyword matching
            pass

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

            console.print("[green]✓ ML model initialized[/green]")
        except ImportError:
            # Dependencies checked at startup, silently fall back to rule-based classification
            pass

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
            console.print(f"[yellow]  ✗ Insufficient text: {len(text_content) if text_content else 0} chars (min: {self.min_text_length})[/yellow]")
            return None

        console.print(f"[cyan]→ Classifying document ({len(text_content)} chars)[/cyan]")

        # Try multiple classification methods
        results = []

        # 1. Pattern-based classification
        pattern_result = self._classify_by_patterns(text_content)
        if pattern_result:
            console.print(f"[dim]  Pattern: {pattern_result.document_type} ({pattern_result.confidence:.0%})[/dim]")
            results.append(pattern_result)
        else:
            console.print(f"[dim]  Pattern: No match[/dim]")

        # 2. NLP-based classification
        if self.nlp:
            nlp_result = self._classify_by_nlp(text_content)
            if nlp_result:
                console.print(f"[dim]  NLP: {nlp_result.document_type} ({nlp_result.confidence:.0%})[/dim]")
                results.append(nlp_result)
            else:
                console.print(f"[dim]  NLP: No match[/dim]")
        else:
            console.print(f"[dim]  NLP: Disabled[/dim]")

        # 3. Keyword-based classification (fallback)
        keyword_result = self._classify_by_keywords(text_content)
        if keyword_result:
            console.print(f"[dim]  Keyword: {keyword_result.document_type} ({keyword_result.confidence:.0%})[/dim]")
            results.append(keyword_result)
        else:
            console.print(f"[dim]  Keyword: No match[/dim]")

        # Select best result
        if not results:
            console.print(f"[red]  ✗ No classification match found[/red]")
            return None

        # Sort by confidence and return best match
        results.sort(key=lambda x: x.confidence, reverse=True)
        best_result = results[0]

        if best_result.confidence >= self.confidence_threshold:
            console.print(f"[green]  ✓ {best_result.display_name}: {best_result.confidence:.0%} (threshold: {self.confidence_threshold:.0%})[/green]")
            return best_result
        else:
            console.print(f"[yellow]  ✗ Best match '{best_result.display_name}' below threshold: {best_result.confidence:.0%} < {self.confidence_threshold:.0%}[/yellow]")
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

        console.print(f"[cyan]→ Extracting text from: {path.name}[/cyan]")

        # Check file size (skip files over max_file_size_mb)
        try:
            max_size = self.config['processing'].get('max_file_size_mb', 50) * 1024 * 1024
            file_size = path.stat().st_size

            if file_size > max_size:
                console.print(f"[yellow]  ✗ File too large: {file_size / 1024 / 1024:.1f}MB[/yellow]")
                return ""
        except Exception:
            pass  # If we can't check size, proceed anyway

        try:
            if extension == '.pdf':
                text = self._extract_pdf_text(file_path)
                if text.strip():
                    console.print(f"[green]  ✓ Extracted {len(text)} chars[/green]")
                    console.print(f"[dim]  Preview: {text[:100]}...[/dim]")
                else:
                    console.print(f"[yellow]  ✗ No text extracted from PDF[/yellow]")
                return text
            else:
                console.print(f"[yellow]  ✗ Unsupported extension: {extension}[/yellow]")
                return ""
        except Exception as e:
            console.print(f"[red]  ✗ Extraction error: {e}[/red]")
            return ""

    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF file with Windows-compatible timeout.

        Args:
            file_path: Path to PDF file

        Returns:
            Extracted text
        """
        text = ""
        max_pages = 10  # Reduced to 10 for speed - most invoices are 1-2 pages
        timeout_seconds = 5  # 5 second timeout for entire extraction

        # Use concurrent.futures for Windows-compatible timeout
        from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

        def extract_with_pdfplumber():
            """Extract text using pdfplumber."""
            extracted = ""
            try:
                with pdfplumber.open(file_path) as pdf:
                    total_pages = len(pdf.pages)
                    pages_to_process = min(total_pages, max_pages)

                    for page in pdf.pages[:pages_to_process]:
                        try:
                            page_text = page.extract_text(x_tolerance=3, y_tolerance=3)
                            if page_text:
                                extracted += page_text + "\n"
                        except Exception:
                            continue
            except Exception:
                pass
            return extracted

        # Try pdfplumber with timeout
        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(extract_with_pdfplumber)
                text = future.result(timeout=timeout_seconds)

            if text.strip():
                return text
        except FuturesTimeoutError:
            console.print(f"[yellow]  ⚠ PDF timeout ({timeout_seconds}s) - trying fallback[/yellow]")
        except Exception:
            pass

        # Fast fallback to PyPDF2 with same timeout
        def extract_with_pypdf2():
            """Extract text using PyPDF2."""
            extracted = ""
            try:
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    total_pages = len(pdf_reader.pages)
                    pages_to_process = min(total_pages, max_pages)

                    for i in range(pages_to_process):
                        try:
                            page_text = pdf_reader.pages[i].extract_text()
                            if page_text:
                                extracted += page_text + "\n"
                        except Exception:
                            continue
            except Exception:
                pass
            return extracted

        # Try PyPDF2 with timeout
        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(extract_with_pypdf2)
                text = future.result(timeout=timeout_seconds)
        except FuturesTimeoutError:
            console.print(f"[yellow]  ⚠ PyPDF2 timeout - skipping PDF[/yellow]")
        except Exception:
            pass

        # Return whatever we extracted (may be empty)
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
            console.print(f"[green]Extracted text from DOCX[/green]")
            return text
        except Exception as e:
            console.print(f"[red]DOCX extraction failed: {e}[/red]")
            return ""

    def _ocr_pdf(self, file_path: str) -> str:
        """OCR is disabled for this application.

        This method is not used but kept for potential future use.
        """
        return ""
