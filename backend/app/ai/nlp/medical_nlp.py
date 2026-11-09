import re
from typing import List, Dict, Any, Optional, Tuple

class MedicalNLPEngine:
    """
    Biomedical Natural Language Processing & Named Entity Recognition Engine.
    Extracts laboratory test names, values, units, reference ranges, diseases,
    symptoms, medications, anatomy, and dates from medical reports.
    Preserves exact numerical values without alteration.
    """

    # Verified standard laboratory clinical reference intervals (MedlinePlus / NIH)
    KNOWN_LAB_TESTS = {
        "hemoglobin": {"canonical": "Hemoglobin", "unit": "g/dL", "low": 12.0, "high": 17.5, "category": "Hematology"},
        "hgb": {"canonical": "Hemoglobin", "unit": "g/dL", "low": 12.0, "high": 17.5, "category": "Hematology"},
        "hb": {"canonical": "Hemoglobin", "unit": "g/dL", "low": 12.0, "high": 17.5, "category": "Hematology"},
        "wbc": {"canonical": "White Blood Cell Count", "unit": "x10^3/uL", "low": 4.5, "high": 11.0, "category": "Hematology"},
        "white blood cells": {"canonical": "White Blood Cell Count", "unit": "x10^3/uL", "low": 4.5, "high": 11.0, "category": "Hematology"},
        "leukocytes": {"canonical": "White Blood Cell Count", "unit": "x10^3/uL", "low": 4.5, "high": 11.0, "category": "Hematology"},
        "platelets": {"canonical": "Platelet Count", "unit": "x10^3/uL", "low": 150.0, "high": 450.0, "category": "Hematology"},
        "platelet count": {"canonical": "Platelet Count", "unit": "x10^3/uL", "low": 150.0, "high": 450.0, "category": "Hematology"},
        "plt": {"canonical": "Platelet Count", "unit": "x10^3/uL", "low": 150.0, "high": 450.0, "category": "Hematology"},
        "rbc": {"canonical": "Red Blood Cell Count", "unit": "x10^6/uL", "low": 4.2, "high": 5.9, "category": "Hematology"},
        "hematocrit": {"canonical": "Hematocrit", "unit": "%", "low": 36.0, "high": 50.0, "category": "Hematology"},
        "hct": {"canonical": "Hematocrit", "unit": "%", "low": 36.0, "high": 50.0, "category": "Hematology"},
        "mcv": {"canonical": "Mean Corpuscular Volume (MCV)", "unit": "fL", "low": 80.0, "high": 100.0, "category": "Hematology"},
        "mch": {"canonical": "Mean Corpuscular Hemoglobin (MCH)", "unit": "pg", "low": 27.0, "high": 33.0, "category": "Hematology"},
        "mchc": {"canonical": "MCHC", "unit": "g/dL", "low": 32.0, "high": 36.0, "category": "Hematology"},
        
        # Metabolic & Glucose
        "glucose": {"canonical": "Fasting Blood Glucose", "unit": "mg/dL", "low": 70.0, "high": 99.0, "category": "Endocrinology"},
        "fasting blood sugar": {"canonical": "Fasting Blood Glucose", "unit": "mg/dL", "low": 70.0, "high": 99.0, "category": "Endocrinology"},
        "fbs": {"canonical": "Fasting Blood Glucose", "unit": "mg/dL", "low": 70.0, "high": 99.0, "category": "Endocrinology"},
        "hba1c": {"canonical": "Hemoglobin A1c (HbA1c)", "unit": "%", "low": 4.0, "high": 5.6, "category": "Endocrinology"},
        "glycated hemoglobin": {"canonical": "Hemoglobin A1c (HbA1c)", "unit": "%", "low": 4.0, "high": 5.6, "category": "Endocrinology"},
        
        # Renal Panel
        "creatinine": {"canonical": "Serum Creatinine", "unit": "mg/dL", "low": 0.6, "high": 1.3, "category": "Nephrology"},
        "serum creatinine": {"canonical": "Serum Creatinine", "unit": "mg/dL", "low": 0.6, "high": 1.3, "category": "Nephrology"},
        "bun": {"canonical": "Blood Urea Nitrogen (BUN)", "unit": "mg/dL", "low": 7.0, "high": 20.0, "category": "Nephrology"},
        "blood urea nitrogen": {"canonical": "Blood Urea Nitrogen (BUN)", "unit": "mg/dL", "low": 7.0, "high": 20.0, "category": "Nephrology"},
        "egfr": {"canonical": "Estimated GFR (eGFR)", "unit": "mL/min/1.73m2", "low": 90.0, "high": 150.0, "category": "Nephrology"},
        
        # Lipid Panel
        "cholesterol": {"canonical": "Total Cholesterol", "unit": "mg/dL", "low": 100.0, "high": 199.0, "category": "Cardiology"},
        "total cholesterol": {"canonical": "Total Cholesterol", "unit": "mg/dL", "low": 100.0, "high": 199.0, "category": "Cardiology"},
        "triglycerides": {"canonical": "Triglycerides", "unit": "mg/dL", "low": 40.0, "high": 149.0, "category": "Cardiology"},
        "hdl": {"canonical": "HDL Cholesterol", "unit": "mg/dL", "low": 40.0, "high": 90.0, "category": "Cardiology"},
        "hdl cholesterol": {"canonical": "HDL Cholesterol", "unit": "mg/dL", "low": 40.0, "high": 90.0, "category": "Cardiology"},
        "ldl": {"canonical": "LDL Cholesterol", "unit": "mg/dL", "low": 50.0, "high": 99.0, "category": "Cardiology"},
        "ldl cholesterol": {"canonical": "LDL Cholesterol", "unit": "mg/dL", "low": 50.0, "high": 99.0, "category": "Cardiology"},
        
        # Liver Function
        "alt": {"canonical": "Alanine Aminotransferase (ALT)", "unit": "U/L", "low": 7.0, "high": 56.0, "category": "Gastroenterology"},
        "sgpt": {"canonical": "Alanine Aminotransferase (ALT)", "unit": "U/L", "low": 7.0, "high": 56.0, "category": "Gastroenterology"},
        "ast": {"canonical": "Aspartate Aminotransferase (AST)", "unit": "U/L", "low": 8.0, "high": 48.0, "category": "Gastroenterology"},
        "sgot": {"canonical": "Aspartate Aminotransferase (AST)", "unit": "U/L", "low": 8.0, "high": 48.0, "category": "Gastroenterology"},
        "bilirubin": {"canonical": "Total Bilirubin", "unit": "mg/dL", "low": 0.2, "high": 1.2, "category": "Gastroenterology"},
        "total bilirubin": {"canonical": "Total Bilirubin", "unit": "mg/dL", "low": 0.2, "high": 1.2, "category": "Gastroenterology"},
        "albumin": {"canonical": "Albumin", "unit": "g/dL", "low": 3.4, "high": 5.4, "category": "Gastroenterology"},
        "alkaline phosphatase": {"canonical": "Alkaline Phosphatase (ALP)", "unit": "U/L", "low": 44.0, "high": 147.0, "category": "Gastroenterology"},
        "alp": {"canonical": "Alkaline Phosphatase (ALP)", "unit": "U/L", "low": 44.0, "high": 147.0, "category": "Gastroenterology"},

        # Thyroid & Electrolytes
        "tsh": {"canonical": "Thyroid Stimulating Hormone (TSH)", "unit": "uIU/mL", "low": 0.4, "high": 4.0, "category": "Endocrinology"},
        "potassium": {"canonical": "Potassium (K+)", "unit": "mmol/L", "low": 3.5, "high": 5.1, "category": "Nephrology"},
        "sodium": {"canonical": "Sodium (Na+)", "unit": "mmol/L", "low": 135.0, "high": 145.0, "category": "Nephrology"},
        "calcium": {"canonical": "Total Calcium", "unit": "mg/dL", "low": 8.5, "high": 10.5, "category": "Endocrinology"}
    }

    # Clinical entity dictionaries for Named Entity Recognition
    DISEASE_KEYWORDS = [
        "anemia", "diabetes mellitus", "diabetes", "prediabetes", "hypertension", "dyslipidemia",
        "hypercholesterolemia", "chronic kidney disease", "acute kidney injury", "fatty liver",
        "hepatitis", "leukocytosis", "leukopenia", "thrombocytopenia", "thrombocytosis",
        "cardiomegaly", "pneumonia", "pleural effusion", "atelectasis", "pneumothorax",
        "infection", "inflammation", "hypokalemia", "hyperkalemia", "hypothyroidism"
    ]

    SYMPTOM_KEYWORDS = [
        "fatigue", "fever", "chest pain", "shortness of breath", "dyspnea", "cough", "weakness",
        "dizziness", "palpitations", "headache", "nausea", "swelling", "edema", "chills"
    ]

    MEDICATION_KEYWORDS = [
        "metformin", "atorvastatin", "amlodipine", "lisinopril", "losartan", "aspirin",
        "levothyroxine", "omeprazole", "amoxicillin", "azithromycin", "furosemide", "insulin"
    ]

    ANATOMY_KEYWORDS = [
        "lung", "lungs", "heart", "cardiac", "kidney", "kidneys", "renal", "liver", "hepatic",
        "blood", "pleura", "thorax", "mediastinum", "diaphragm", "bone", "vessel"
    ]

    def extract_entities(self, text: str, page_number: int = 1) -> List[Dict[str, Any]]:
        """
        Extract all medical entities from text with exact numerical preservation.
        """
        entities = []
        
        # 1. Extract Lab Tests and Numerical Values
        lab_entities = self._extract_lab_results(text, page_number)
        entities.extend(lab_entities)

        # 2. Extract Diseases & Conditions
        disease_entities = self._extract_keyword_entities(
            text, self.DISEASE_KEYWORDS, "disease", page_number
        )
        entities.extend(disease_entities)

        # 3. Extract Symptoms
        symptom_entities = self._extract_keyword_entities(
            text, self.SYMPTOM_KEYWORDS, "symptom", page_number
        )
        entities.extend(symptom_entities)

        # 4. Extract Medications
        med_entities = self._extract_keyword_entities(
            text, self.MEDICATION_KEYWORDS, "medication", page_number
        )
        entities.extend(med_entities)

        # 5. Extract Anatomical structures
        anatomy_entities = self._extract_keyword_entities(
            text, self.ANATOMY_KEYWORDS, "anatomy", page_number
        )
        entities.extend(anatomy_entities)

        # 6. Extract Dates
        date_entities = self._extract_dates(text, page_number)
        entities.extend(date_entities)

        return entities

    def _extract_lab_results(self, text: str, page_number: int) -> List[Dict[str, Any]]:
        results = []
        lines = text.split("\n")

        # Pattern: TestName ... Number ... (optional unit) ... (optional range: low-high)
        # e.g., "Hemoglobin  11.2  g/dL  13.8 - 17.2"
        # e.g., "Fasting Glucose: 118 mg/dL (70-99)"
        for line in lines:
            line_clean = line.strip()
            if not line_clean:
                continue

            for test_key, meta in self.KNOWN_LAB_TESTS.items():
                pattern = rf"(?i)\b{re.escape(test_key)}\b[\s:\-—=]+([<>]?\s*\d+(?:\.\d+)?)\s*([a-zA-Z/%^0-9\-\*]+)?(?:\s*\(?([\d\.]+\s*[-–—to]+\s*[\d\.]+)\)?)?"
                match = re.search(pattern, line_clean)
                if match:
                    raw_val_str = match.group(1).strip()
                    extracted_unit = match.group(2).strip() if match.group(2) else meta["unit"]
                    extracted_ref = match.group(3).strip() if match.group(3) else f"{meta['low']} - {meta['high']}"
                    
                    # Parse numerical value cleanly without alteration
                    try:
                        clean_num_str = re.sub(r"[^\d\.]", "", raw_val_str)
                        val_float = float(clean_num_str)
                        
                        # Evaluate reference range
                        is_out_of_range = False
                        flag = "NORMAL"
                        if val_float < meta["low"]:
                            is_out_of_range = True
                            flag = "LOW"
                        elif val_float > meta["high"]:
                            is_out_of_range = True
                            flag = "HIGH"
                    except ValueError:
                        is_out_of_range = None
                        flag = None

                    # Deduplicate in current results
                    if not any(r["text"] == meta["canonical"] for r in results):
                        results.append({
                            "entity_type": "lab_test",
                            "text": meta["canonical"],
                            "normalized_value": raw_val_str,
                            "unit": extracted_unit,
                            "reference_range": extracted_ref,
                            "is_out_of_range": is_out_of_range,
                            "flag": flag,
                            "source_page": page_number,
                            "confidence_score": 0.96
                        })

        return results

    def _extract_keyword_entities(self, text: str, keywords: List[str], entity_type: str, page_number: int) -> List[Dict[str, Any]]:
        results = []
        seen = set()
        for kw in keywords:
            pattern = rf"(?i)\b{re.escape(kw)}\b"
            if re.search(pattern, text):
                canonical = kw.capitalize()
                if canonical.lower() not in seen:
                    seen.add(canonical.lower())
                    results.append({
                        "entity_type": entity_type,
                        "text": canonical,
                        "normalized_value": None,
                        "unit": None,
                        "reference_range": None,
                        "is_out_of_range": None,
                        "flag": None,
                        "source_page": page_number,
                        "confidence_score": 0.92
                    })
        return results

    def _extract_dates(self, text: str, page_number: int) -> List[Dict[str, Any]]:
        results = []
        # Match dates like 2026-03-15, 15/03/2026, 15-Mar-2026, March 15, 2026
        date_pattern = r"\b(?:\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4})\b"
        matches = re.findall(date_pattern, text, re.IGNORECASE)
        for date_str in matches[:3]:  # Top 3 dates
            results.append({
                "entity_type": "date",
                "text": date_str,
                "normalized_value": date_str,
                "unit": None,
                "reference_range": None,
                "is_out_of_range": None,
                "flag": None,
                "source_page": page_number,
                "confidence_score": 0.98
            })
        return results

