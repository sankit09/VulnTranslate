"""
CVE Term Preserver
Implements ITermPreserver interface for CVE-specific technical terms
"""

import re
from typing import List, Dict, Set
from core.interfaces import ITermPreserver
from core.models import CVETerms


class CVETermPreserver(ITermPreserver):
    """Preserves CVE-specific technical terms during translation"""
    
    def __init__(self):
        # Enhanced regex patterns for comprehensive term protection
        self.patterns = {
            'cve_ids': re.compile(r'CVE-\d{4}-\d{4,7}', re.IGNORECASE),
            'vmsa_ids': re.compile(r'VMSA-\d{4}-\d{4}', re.IGNORECASE),
            'cvss_scores': re.compile(r'CVSS[v]?\d+(\.\d+)?', re.IGNORECASE),
            'score_ranges': re.compile(r'\d+\.\d+[-–]\d+\.\d+', re.IGNORECASE),
            'version_numbers': re.compile(r'\b\d+\.\d+(?:\.\d+)*(?:\s*build\s*\d+)?\b', re.IGNORECASE),
            'build_numbers': re.compile(r'\bbuild\s+\d+\b', re.IGNORECASE),
            'company_names': re.compile(r'\b(VMware|Microsoft|Oracle|Adobe|Cisco|Apple|Google|Amazon|IBM|Dell|HP|Intel|AMD|NVIDIA|Broadcom)\b', re.IGNORECASE),
            'product_names': re.compile(r'\b(ESXi|vCenter\s+Server|Workstation|Fusion|Windows|Office|Exchange|SharePoint|Chrome|Firefox|Safari|Cloud\s+Foundation|Telco\s+Cloud)\b', re.IGNORECASE),
            'product_editions': re.compile(r'\b(Pro|Standard|Enterprise|Professional|Ultimate|Home)\b', re.IGNORECASE),
            'urls': re.compile(r'https?://[^\s]+', re.IGNORECASE),
            'emails': re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', re.IGNORECASE),
            'file_paths': re.compile(r'[a-zA-Z]:\\[^\s]+|/[^\s]+', re.IGNORECASE),
            'ip_addresses': re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', re.IGNORECASE),
            'mac_addresses': re.compile(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', re.IGNORECASE),
            'registry_keys': re.compile(r'HKEY_[A-Z_]+\\[^\s]+', re.IGNORECASE),
            'hash_values': re.compile(r'\b[a-fA-F0-9]{32,64}\b', re.IGNORECASE),
            'port_numbers': re.compile(r'\b(?:port\s+)?\d{1,5}\b', re.IGNORECASE),
            'file_extensions': re.compile(r'\.[a-zA-Z0-9]{2,5}\b', re.IGNORECASE)
        }
        
        # Additional known technical terms
        self.technical_keywords = {
            'authentication', 'authorization', 'vulnerability', 'exploit', 
            'payload', 'shellcode', 'buffer overflow', 'privilege escalation',
            'remote code execution', 'denial of service', 'cross-site scripting',
            'sql injection', 'malware', 'ransomware', 'backdoor', 'trojan',
            'phishing', 'social engineering', 'cryptography', 'encryption',
            'decryption', 'certificate', 'ssl', 'tls', 'https', 'api',
            'endpoint', 'firewall', 'intrusion detection', 'antivirus'
        }

    def extract_terms(self, text: str) -> List[str]:
        """Extract all technical terms that should be preserved"""
        if not text:
            return []
        
        preserved_terms = set()
        
        # Extract using regex patterns
        for pattern_name, pattern in self.patterns.items():
            matches = pattern.findall(text)
            if isinstance(matches[0], tuple) if matches else False:
                # Handle regex groups
                preserved_terms.update([match[0] if isinstance(match, tuple) else match for match in matches])
            else:
                preserved_terms.update(matches)
        
        return list(preserved_terms)

    def create_preservation_map(self, text: str) -> Dict[str, str]:
        """Create a mapping of terms to protection tokens"""
        terms = self.extract_terms(text)
        preservation_map = {}
        
        for i, term in enumerate(terms):
            # Create unique protection token
            token = f"[KEEP:{i:04d}]"
            preservation_map[token] = term
        
        return preservation_map

    def apply_protection_tokens(self, text: str, preservation_map: Dict[str, str]) -> str:
        """Replace technical terms with protection tokens"""
        protected_text = text
        
        # Sort by length (longest first) to avoid partial replacements
        sorted_terms = sorted(preservation_map.values(), key=len, reverse=True)
        
        for term in sorted_terms:
            # Find the corresponding token
            token = next(k for k, v in preservation_map.items() if v == term)
            # Replace term with token
            protected_text = protected_text.replace(term, token)
        
        return protected_text

    def restore_preservation_map(self, text: str, preservation_map: Dict[str, str]) -> str:
        """Restore protection tokens back to original terms"""
        restored_text = text
        
        for token, term in preservation_map.items():
            restored_text = restored_text.replace(token, term)
        
        return restored_text

    def verify_preservation(self, original: str, translated: str) -> bool:
        """Verify that technical terms are preserved in translation"""
        original_terms = set(self.extract_terms(original))
        translated_terms = set(self.extract_terms(translated))
        
        # Check if all original terms are preserved
        missing_terms = original_terms - translated_terms
        
        # Allow for minor variations in formatting
        return len(missing_terms) == 0

    def get_cve_terms(self, text: str) -> CVETerms:
        """Extract categorized CVE terms from text"""
        cve_terms = CVETerms()
        
        if not text:
            return cve_terms
        
        # Extract specific term categories
        cve_terms.cve_ids = self.patterns['cve_ids'].findall(text)
        cve_terms.cvss_scores = self.patterns['cvss_scores'].findall(text)
        cve_terms.company_names = self.patterns['company_names'].findall(text)
        cve_terms.product_names = self.patterns['product_names'].findall(text)
        cve_terms.urls = self.patterns['urls'].findall(text)
        
        # Extract technical identifiers (combination of various patterns)
        tech_identifiers = []
        tech_identifiers.extend(self.patterns['file_paths'].findall(text))
        tech_identifiers.extend(self.patterns['registry_keys'].findall(text))
        tech_identifiers.extend(self.patterns['hash_values'].findall(text))
        tech_identifiers.extend(self.patterns['ip_addresses'].findall(text))
        tech_identifiers.extend(self.patterns['mac_addresses'].findall(text))
        
        cve_terms.technical_identifiers = list(set(tech_identifiers))
        
        return cve_terms

    def create_preservation_map(self, text: str) -> Dict[str, str]:
        """Create a map of terms to preserve with their replacements"""
        preservation_map = {}
        terms = self.extract_terms(text)
        
        for i, term in enumerate(terms):
            placeholder = f"__PRESERVE_{i}__"
            preservation_map[term] = placeholder
        
        return preservation_map

    def apply_preservation_map(self, text: str, preservation_map: Dict[str, str]) -> str:
        """Apply preservation map to text (replace terms with placeholders)"""
        modified_text = text
        for term, placeholder in preservation_map.items():
            modified_text = modified_text.replace(term, placeholder)
        return modified_text

    def restore_preservation_map(self, text: str, preservation_map: Dict[str, str]) -> str:
        """Restore original terms from placeholders"""
        restored_text = text
        for term, placeholder in preservation_map.items():
            restored_text = restored_text.replace(placeholder, term)
        return restored_text

    def get_preservation_statistics(self, original: str, translated: str) -> Dict[str, any]:
        """Get detailed statistics about term preservation"""
        original_terms = self.extract_terms(original)
        translated_terms = self.extract_terms(translated)
        
        original_set = set(original_terms)
        translated_set = set(translated_terms)
        
        preserved = original_set.intersection(translated_set)
        missing = original_set - translated_set
        added = translated_set - original_set
        
        return {
            'total_original_terms': len(original_terms),
            'unique_original_terms': len(original_set),
            'preserved_terms': len(preserved),
            'missing_terms': len(missing),
            'added_terms': len(added),
            'preservation_rate': len(preserved) / len(original_set) if original_set else 1.0,
            'missing_term_list': list(missing),
            'added_term_list': list(added),
            'preserved_term_list': list(preserved)
        }

    def validate_term_integrity(self, text: str) -> Dict[str, bool]:
        """Validate integrity of different term categories"""
        validation_results = {}
        
        for pattern_name, pattern in self.patterns.items():
            matches = pattern.findall(text)
            # Check if terms are properly formatted
            validation_results[pattern_name] = all(
                self._validate_term_format(match, pattern_name) 
                for match in matches
            )
        
        return validation_results

    def _validate_term_format(self, term: str, term_type: str) -> bool:
        """Validate format of specific term types"""
        if term_type == 'cve_ids':
            return bool(re.match(r'^CVE-\d{4}-\d{4,7}$', term, re.IGNORECASE))
        elif term_type == 'cvss_scores':
            return bool(re.match(r'^CVSS[v]?\d+(\.\d+)?$', term, re.IGNORECASE))
        elif term_type == 'urls':
            return term.startswith(('http://', 'https://'))
        elif term_type == 'emails':
            return '@' in term and '.' in term.split('@')[1]
        else:
            return True  # Basic validation for other types