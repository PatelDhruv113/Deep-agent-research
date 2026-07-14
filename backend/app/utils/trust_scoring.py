from typing import Dict

def calculate_trust_score(finding: Dict) -> int:
    """Calculate 0-100 trust score for a claim"""
    score = 60

    source = finding.get("source", {})

    url = source.get("url", "")
    if any(domain in url for domain in ["gov", ".edu", ".org"]):
        score += 25
    if "wikipedia" in url:
        score += 10
    
    if finding.get("score", 0) > 0.8:
        score += 15
    
    return min(max(score, 0), 100)