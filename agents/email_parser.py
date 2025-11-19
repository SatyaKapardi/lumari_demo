"""
Email Parser Agent - Extracts supply chain entities from unstructured emails
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime

# Load spaCy model for NER (optional)
nlp = None
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except (OSError, TypeError, ImportError, Exception):
    # Gracefully handle missing model or version conflicts
    # Demo works fine with regex-only parsing
    pass


class EmailParser:
    """Parses supplier emails and extracts supply chain entities"""
    
    def __init__(self):
        # Regex patterns for supply chain entities
        self.po_pattern = re.compile(r'\bPO[#\s]*:?\s*(\d{4,})\b', re.IGNORECASE)
        self.quantity_pattern = re.compile(r'\b(\d+(?:,\d+)?)\s*(?:units?|pcs?|pieces?|qty)\b', re.IGNORECASE)
        self.date_pattern = re.compile(r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\w+\s+\d{1,2},?\s+\d{4}|\d{4}-\d{2}-\d{2})\b')
        self.part_number_pattern = re.compile(r'\b(?:Part|Item|SKU)[#\s]*:?\s*([A-Z0-9-]+)\b', re.IGNORECASE)
        self.price_pattern = re.compile(r'\$?\s*(\d+(?:,\d+)?(?:\.\d{2})?)\b')
    
    def extract_entities(self, email_body: str, subject: str = "") -> Dict[str, Any]:
        """Extract supply chain entities from email"""
        full_text = f"{subject} {email_body}".strip()
        
        entities = {
            "po_number": None,
            "quantities": [],
            "dates": [],
            "part_numbers": [],
            "prices": [],
            "confidence": 0.0
        }
        
        # Extract PO numbers
        po_matches = self.po_pattern.findall(full_text)
        if po_matches:
            entities["po_number"] = po_matches[0]
            entities["confidence"] += 0.3
        
        # Extract quantities
        qty_matches = self.quantity_pattern.findall(full_text)
        entities["quantities"] = [q.replace(',', '') for q in qty_matches]
        if qty_matches:
            entities["confidence"] += 0.2
        
        # Extract dates (enhanced with spaCy if available)
        date_matches = self.date_pattern.findall(full_text)
        entities["dates"] = date_matches[:3]  # Limit to first 3 dates
        
        # Use spaCy for better date extraction if available
        if nlp:
            doc = nlp(full_text)
            for ent in doc.ents:
                if ent.label_ == "DATE":
                    if ent.text not in entities["dates"]:
                        entities["dates"].append(ent.text)
                elif ent.label_ == "MONEY" and not entities["prices"]:
                    entities["prices"].append(ent.text)
        
        # Extract part numbers
        part_matches = self.part_number_pattern.findall(full_text)
        entities["part_numbers"] = part_matches[:5]  # Limit to first 5
        
        # Extract prices
        if not entities["prices"]:
            price_matches = self.price_pattern.findall(full_text)
            entities["prices"] = price_matches[:3]
        
        # Normalize confidence score
        entities["confidence"] = min(entities["confidence"], 1.0)
        
        return entities
    
    def classify_intent(self, subject: str, body: str) -> Dict[str, Any]:
        """Classify email intent using keyword analysis"""
        text = f"{subject} {body}".lower()
        
        intent_keywords = {
            "delivery_delay": ["delay", "delayed", "late", "postpone", "reschedule", "behind schedule"],
            "price_change": ["price", "pricing", "cost", "quote", "increase", "decrease", "change"],
            "quantity_change": ["quantity", "qty", "units", "increase", "decrease", "revise"],
            "acknowledgement_request": ["acknowledge", "confirm", "receipt", "received", "please confirm"],
            "quality_issue": ["defect", "quality", "damage", "issue", "problem", "reject"],
            "general_inquiry": ["question", "inquiry", "ask", "help", "information"]
        }
        
        scores = {}
        for intent, keywords in intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            scores[intent] = score
        
        # Determine primary intent
        if max(scores.values()) == 0:
            primary_intent = "general_inquiry"
            confidence = 0.5
        else:
            primary_intent = max(scores, key=scores.get)
            confidence = min(scores[primary_intent] / len(intent_keywords[primary_intent]), 1.0)
        
        return {
            "intent": primary_intent,
            "confidence": confidence,
            "scores": scores
        }

