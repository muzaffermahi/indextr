"""
Turkish Language Detection Module
Because sometimes you need to know what language you're dealing with instead of guessing like a digital caveman

This module exists to solve the eternal question: "Is this text Turkish or are we all just living in linguistic chaos?"

Usage:
    from turkish_detector import detect_and_prioritize_turkish
    
    result = detect_and_prioritize_turkish("English text here", "Turkish text burada")
    # Returns the Turkish text if detected as Turkish, otherwise falls back to English
"""

def detect_and_prioritize_turkish(english_text: str, turkish_text: str) -> str:
    """
    Language detection using ACTUAL langdetect instead of elaborate philosophical bullshit
    
    This function embodies the beautiful principle of:
    "Use real language detection libraries instead of reinventing computational linguistics"
    
    Args:
        english_text: Text from the "English" position (might actually be Turkish because bureaucracy)
        turkish_text: Text from the "Turkish" position (probably Turkish but who knows)
        
    Returns:
        str: The Turkish text if detected as Turkish, otherwise English text, otherwise "Unknown Title"
        
    Example:
        english = "Machine learning algorithms in healthcare"
        turkish = "Sağlık alanında makine öğrenmesi algoritmaları"
        
        result = detect_and_prioritize_turkish(english, turkish)
        # Returns: "Sağlık alanında makine öğrenmesi algoritmaları"
    """
    try:
        from langdetect import detect, DetectorFactory
        # Set seed for consistent results because chaos is the enemy of reproducible science
        DetectorFactory.seed = 0
    except ImportError:
        print("   ⚠️  langdetect not installed. Install with: pip install langdetect")
        print("   📦 Quick fix: pip install langdetect")
        # Fallback to simple priority logic when the library gods abandon us
        return _fallback_turkish_detection(english_text, turkish_text)
    
    # Clean the texts first because input sanitization is not optional
    turkish_clean = turkish_text.strip() if turkish_text else ""
    english_clean = english_text.strip() if english_text else ""
    
    def _detect_language_safely(text: str) -> str:
        """
        Detect language with error handling because langdetect can be moody like a temperamental artist
        
        Args:
            text: Text to analyze
            
        Returns:
            str: Detected language code ('tr', 'en', etc.) or 'unknown' if detection fails
        """
        if not text or len(text.strip()) < 15:  # Need minimum text for reliable detection
            return 'unknown'
        
        try:
            detected = detect(text)
            return detected
        except Exception as e:
            # Language detection failed - could be mixed languages, too short, or just chaos
            return 'unknown'
    
    # Actually USE langdetect like responsible developers
    turkish_detected_lang = _detect_language_safely(turkish_clean)
    english_detected_lang = _detect_language_safely(english_clean)
    
    # Turkish-first priority logic using ACTUAL detection results
    if turkish_clean and turkish_detected_lang == 'tr':
        # Turkish text detected as Turkish - this is the dream scenario
        return turkish_clean
    elif english_clean and english_detected_lang == 'tr':
        # "English" text is actually Turkish (bureaucratic mislabeling strikes again)
        return english_clean
    elif turkish_clean and turkish_detected_lang != 'unknown':
        # Turkish position exists and has some detected language (might not be Turkish but still prefer it)
        return turkish_clean
    elif english_clean and english_detected_lang != 'unknown':
        # English position exists and has some detected language
        return english_clean
    elif turkish_clean:
        # Turkish position exists but detection failed - still prefer Turkish position
        return turkish_clean
    elif english_clean:
        # Only English available - better than nothing
        return english_clean
    else:
        # The linguistic void stares back
        return "Unknown Title"


def _fallback_turkish_detection(english_text: str, turkish_text: str) -> str:
    """
    Fallback method when langdetect is not available
    
    Uses simple priority logic because sometimes we must embrace digital minimalism
    
    Args:
        english_text: Text from English position
        turkish_text: Text from Turkish position
        
    Returns:
        str: Turkish text if available, otherwise English text, otherwise "Unknown Title"
    """
    turkish_clean = turkish_text.strip() if turkish_text else ""
    english_clean = english_text.strip() if english_text else ""
    
    # Simple fallback: prefer Turkish position, then English, then despair
    if turkish_clean:
        return turkish_clean
    elif english_clean:
        return english_clean
    else:
        return "Unknown Title"


def test_turkish_detection():
    """
    Test function to make sure our language detection isn't completely broken
    
    Run this to verify everything works before integrating into your search engine
    """
    print("🧪 Testing Turkish Language Detection...")
    
    test_cases = [
        # (english_text, turkish_text, expected_behavior)
        ("Machine learning algorithms", "Makine öğrenmesi algoritmaları", "Should prefer Turkish"),
        ("", "Türkçe metin burada", "Should use Turkish when English is empty"),
        ("English text here", "", "Should use English when Turkish is empty"),
        ("", "", "Should return Unknown Title"),
        ("This is English", "Bu Türkçe bir metindir ve çok güzel", "Should detect and prefer Turkish"),
    ]
    
    for i, (eng, tur, expected) in enumerate(test_cases, 1):
        result = detect_and_prioritize_turkish(eng, tur)
        print(f"   Test {i}: {expected}")
        print(f"   Result: '{result}'")
        print()
    
    print("✅ Turkish detection testing complete!")


if __name__ == "__main__":
    # Run tests when this file is executed directly
    test_turkish_detection()