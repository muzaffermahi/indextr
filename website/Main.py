"""
THE ULTIMATE ACADEMIC KNOWLEDGE DESTROYER v2.6 - LAZY LOADING EDITION
Now with SMART MEMORY MANAGEMENT that doesn't murder PythonAnywhere

The Problem We Solved:
- v2.5 loaded everything at startup
- Two uWSGI workers = loading everything TWICE
- PythonAnywhere's RAM: "lol nope" *dies*

The Solution:
- Lazy loading: Don't load shit until someone actually searches
- Workers start light, load on-demand
- Only ONE worker loads data per search
- RAM usage: Manageable instead of catastrophic

This is the "ship it tonight and actually have it work" version.
"""

import pandas as pd
import json
import time
from pathlib import Path
from typing import List, Dict, Any
import re
from datetime import datetime
from Language_detection import detect_and_prioritize_turkish

class UnifiedAcademicSearchEngine:
    """
    v2.6: The "I learned my lesson about eager loading" edition

    Now with lazy loading because why load 1.8M records at startup
    when most of them sit there doing nothing until someone searches?
    """

    def __init__(self,
                 dergipark_parquet_path: str = "articles_dergipark_UNIFIED.parquet",
                 trdizin_parquet_path: str = "trdizin_reduced.parquet",
                 yoktez_parquet_path: str = "Yoktez_son_compressed_brotli.parquet"):
        """
        Initialize paths, but DON'T LOAD THE DATA YET

        This is the key difference from v2.5:
        - v2.5: "Let me load 1.8M records right fucking now"
        - v2.6: "Let me remember where the data is and chill"
        """
        # Store paths only - NO LOADING
        self.dergipark_path = dergipark_parquet_path
        self.trdizin_path = trdizin_parquet_path
        self.yoktez_path = yoktez_parquet_path

        # Private cache attributes (None until first access)
        self._dergipark_cache = None
        self._trdizin_cache = None
        self._yoktez_cache = None

        print("🚀 Search engine initialized with lazy loading")
        print("   (Data loads on first search - workers stay light at startup)")
        print("   (This is how we survive PythonAnywhere's RAM limits)")

    @property
    def dergipark_cache(self):
        """
        Lazy load Dergipark cache only when someone actually searches

        Python @property magic: This looks like a normal attribute
        but actually runs a function when accessed.
        First access? Load the data.
        Subsequent accesses? Return cached data.
        """
        if self._dergipark_cache is None:
            print("📚 Loading Dergipark cache (first use)...")
            self._dergipark_cache = self.load_dergipark_cache(self.dergipark_path)
            if not self._dergipark_cache.empty:
                print(f"   ✅ Loaded {len(self._dergipark_cache):,} articles")
        return self._dergipark_cache

    @property
    def trdizin_cache(self):
        """Lazy load TRDizin - same deal"""
        if self._trdizin_cache is None:
            print("📖 Loading TRDizin cache (first use)...")
            self._trdizin_cache = self.load_trdizin_cache(self.trdizin_path)
            if not self._trdizin_cache.empty:
                print(f"   ✅ Loaded {len(self._trdizin_cache):,} articles")
        return self._trdizin_cache

    @property
    def yoktez_cache(self):
        """Lazy load YÖK Tez - this is the big one that was murdering RAM"""
        if self._yoktez_cache is None:
            print("🎓 Loading YÖK Tez cache (first use)...")
            self._yoktez_cache = self.load_yoktez_cache(self.yoktez_path)
            if not self._yoktez_cache.empty:
                print(f"   ✅ Loaded {len(self._yoktez_cache):,} theses")
        return self._yoktez_cache

    def load_dergipark_cache(self, parquet_path: str) -> pd.DataFrame:
        """Load Dergipark data from parquet"""
        try:
            parquet_file = Path(parquet_path)
            if parquet_file.exists():
                df = pd.read_parquet(parquet_file)
                print(f"   📊 Columns: {list(df.columns)}")
                return df
            else:
                print(f"   ⚠️  Cache not found at {parquet_path}")
                return pd.DataFrame()
        except Exception as e:
            print(f"   💥 Error loading: {e}")
            return pd.DataFrame()

    def load_trdizin_cache(self, parquet_path: str) -> pd.DataFrame:
        """Load TRDizin data from parquet"""
        try:
            if parquet_path is None:
                return pd.DataFrame()

            parquet_file = Path(parquet_path)
            if parquet_file.exists():
                df = pd.read_parquet(parquet_file)
                print(f"   📊 Columns: {list(df.columns)}")
                return df
            else:
                print(f"   ⚠️  Cache not found at {parquet_path}")
                return pd.DataFrame()
        except Exception as e:
            print(f"   💥 Error loading: {e}")
            return pd.DataFrame()

    def load_yoktez_cache(self, parquet_path: str) -> pd.DataFrame:
        """
        Load YÖK Tez data from parquet

        WITH PRODUCTION SAFETY: Auto-sample on PythonAnywhere if needed
        """
        try:
            if parquet_path is None:
                return pd.DataFrame()

            parquet_file = Path(parquet_path)
            if parquet_file.exists():
                df = pd.read_parquet(parquet_file)

                # PRODUCTION MEMORY OPTIMIZATION
                # Detect if we're on PythonAnywhere and sample if needed
                import socket
                hostname = socket.gethostname()

                if 'pythonanywhere' in hostname.lower() or 'liveweb' in hostname.lower():
                    # We're on PythonAnywhere - sample to survive
                    original_size = len(df)
                    sample_fraction = 0.35  # Keep 35% of theses
                    df = df.sample(frac=sample_fraction, random_state=42)
                    print(f"   ⚠️  PythonAnywhere detected")
                    print(f"   📉 Sampled to {len(df):,} theses (from {original_size:,})")
                    print(f"   💡 This prevents RAM exhaustion on production")

                print(f"   📊 Columns: {list(df.columns)}")
                return df
            else:
                print(f"   ⚠️  Cache not found at {parquet_path}")
                return pd.DataFrame()
        except Exception as e:
            print(f"   💥 Error loading: {e}")
            return pd.DataFrame()

    def search_dergipark_local(self, keyword: str, max_results: int = 20, relevance_threshold: str = 'medium') -> List[Dict[str, Any]]:
        """
        Search Dergipark with exact phrase matching

        The @property decorator means accessing self.dergipark_cache
        automatically loads it if needed. Beautiful.
        """
        if self.dergipark_cache.empty:
            return []

        print(f"   🧠 EXACT PHRASE search for: '{keyword}'")

        exact_phrase = keyword.lower()
        mask = (
            self.dergipark_cache['title'].str.lower().str.contains(exact_phrase, na=False, regex=False) |
            self.dergipark_cache['keywords'].str.lower().str.contains(exact_phrase, na=False, regex=False)
        )

        potential_matches = self.dergipark_cache[mask].copy()
        print(f"   📊 Found {len(potential_matches)} matches")

        if potential_matches.empty:
            return []

        if max_results == "all" or max_results == -1:
            final_matches = potential_matches
        else:
            final_matches = potential_matches.head(max_results)

        results = []
        for rank, (_, article) in enumerate(final_matches.iterrows(), 1):
            results.append({
                'source': 'Dergipark (Local)',
                'title': article.get('title', 'Unknown'),
                'authors': self.clean_author_commas(article.get('authors', 'Unknown')),
                'keywords': self.clean_keywords_metadata(article.get('keywords', 'N/A')),
                'url': article.get('url', ''),
                'journal_slug': article.get('journal_slug', ''),
                'publication_date': article.get('publication_date', 'Unknown'),
                'volume': article.get('volume', 'N/A'),
                'issue': article.get('issue', 'N/A'),
                'search_relevance': 'exact_phrase',
                'rank': rank
            })

        print(f"   ✅ Returning {len(results)} results")
        return results

    def search_trdizin_local(self, keyword: str, max_results: int = 20, relevance_threshold: str = 'medium') -> List[Dict[str, Any]]:
        """Search TRDizin (bilingual)"""
        if self.trdizin_cache.empty:
            return []

        print(f"🧠 TRDizin search for: '{keyword}'")

        exact_phrase = keyword.lower()
        mask = (
            self.trdizin_cache['title_turkish'].str.lower().str.contains(exact_phrase, na=False, regex=False) |
            self.trdizin_cache['title_english'].str.lower().str.contains(exact_phrase, na=False, regex=False)
        )

        potential_matches = self.trdizin_cache[mask].copy()
        print(f"📊 Found {len(potential_matches)} matches")

        if potential_matches.empty:
            return []

        if max_results == "all" or max_results == -1:
            final_matches = potential_matches
        else:
            final_matches = potential_matches.head(max_results)

        results = []
        for rank, (_, article) in enumerate(final_matches.iterrows(), 1):
            title_tr = article.get('title_turkish', '')
            title_en = article.get('title_english', '')
            display_title = title_tr if (title_tr and title_tr.strip()) else title_en

            results.append({
                'source': 'TRDizin (Local)',
                'title': display_title or 'Unknown',
                'title_turkish': title_tr,
                'title_english': title_en,
                'authors': self.clean_author_commas(article.get('authors', 'Unknown')),
                'keywords': 'N/A',
                'url': f"https://doi.org/{article.get('doi', '')}",
                'journal_slug': 'trdizin',
                'publication_date': 'Unknown',
                'volume': 'N/A',
                'issue': 'N/A',
                'doi': article.get('doi', ''),
                'article_id': article.get('article_id', ''),
                'search_relevance': 'exact_phrase',
                'rank': rank
            })

        print(f"✅ Returning {len(results)} results")
        return results

    def search_yoktez_local(self, keyword: str, max_results: int = 20, relevance_threshold: str = 'medium') -> List[Dict[str, Any]]:
        """Search YÖK Tez (theses)"""
        if self.yoktez_cache.empty:
            return []

        print(f"🧠 YÖK Tez search for: '{keyword}'")

        exact_phrase = keyword.lower()
        title_col = 'title' if 'title' in self.yoktez_cache.columns else 'thesis_title'
        author_col = 'author' if 'author' in self.yoktez_cache.columns else 'authors'

        mask = (
            self.yoktez_cache[title_col].str.lower().str.contains(exact_phrase, na=False, regex=False) |
            self.yoktez_cache[author_col].str.lower().str.contains(exact_phrase, na=False, regex=False)
        )

        potential_matches = self.yoktez_cache[mask].copy()
        print(f"📊 Found {len(potential_matches)} matches")

        if potential_matches.empty:
            return []

        if max_results == "all" or max_results == -1:
            final_matches = potential_matches
        else:
            final_matches = potential_matches.head(max_results)

        results = []
        for rank, (_, thesis) in enumerate(final_matches.iterrows(), 1):
            thesis_id = thesis.get('article_id', thesis.get('thesis_id', ''))

            results.append({
                'source': 'YÖK Tez (Local)',
                'title': self.clean_escaped_title(thesis.get(title_col, 'Unknown')),
                'authors': self.clean_author_commas(thesis.get(author_col, 'Unknown')),
                'keywords': thesis.get('keywords', 'N/A'),
                'url': f"https://tez.yok.gov.tr/UlusalTezMerkezi/tezDetay.jsp?id={thesis_id}",
                'journal_slug': 'yoktez',
                'publication_date': thesis.get('publication_date', 'Unknown'),
                'volume': 'N/A',
                'issue': 'N/A',
                'thesis_id': thesis_id,
                'search_relevance': 'exact_phrase',
                'rank': rank
            })

        print(f"✅ Returning {len(results)} results")
        return results

    def search_everything(self, keyword: str, max_results_per_source: int = 15, relevance_threshold: str = 'medium'):
        """
        Search all three sources

        Lazy loading happens automatically when we access the cache properties.
        First search? Data loads. Subsequent searches? Uses cached data.
        """
        print(f"\n🔥 UNIFIED SEARCH FOR: '{keyword}' 🔥")

        search_start = time.time()

        print(f"\n📚 Phase 1: Dergipark...")
        dergipark_results = self.search_dergipark_local(keyword, max_results_per_source, relevance_threshold)

        print(f"\n📖 Phase 2: TRDizin...")
        trdizin_results = self.search_trdizin_local(keyword, max_results_per_source, relevance_threshold)

        print(f"\n🎓 Phase 3: YÖK Tez...")
        yoktez_results = self.search_yoktez_local(keyword, max_results_per_source, relevance_threshold)

        search_time = time.time() - search_start

        combined_results = {
            'keyword': keyword,
            'search_timestamp': datetime.now().isoformat(),
            'total_search_time_seconds': round(search_time, 2),
            'version': '2.6_LAZY_LOADING',
            'sources': {
                'dergipark': {
                    'total_results': len(dergipark_results),
                    'source_type': 'local_cache_lazy',
                    'results': dergipark_results
                },
                'trdizin': {
                    'total_results': len(trdizin_results),
                    'source_type': 'local_cache_lazy',
                    'results': trdizin_results
                },
                'yoktez': {
                    'total_results': len(yoktez_results),
                    'source_type': 'local_cache_lazy',
                    'results': yoktez_results
                }
            },
            'summary': {
                'total_articles_found': len(dergipark_results) + len(trdizin_results) + len(yoktez_results),
                'dergipark_count': len(dergipark_results),
                'trdizin_count': len(trdizin_results),
                'yoktez_count': len(yoktez_results)
            }
        }

        print(f"\n🎉 SEARCH COMPLETE IN {search_time:.2f}s")
        print(f"   Total: {combined_results['summary']['total_articles_found']} results")

        return combined_results

    # Helper methods (unchanged from v2.5)

    def clean_escaped_title(self, raw_title: str) -> str:
        if not raw_title:
            return raw_title
        cleaned = raw_title.replace("\\'", "'").replace('\\"', '"').replace('\\\\', '\\')
        cleaned = cleaned.replace('\\n', ' ').replace('\\t', ' ').replace('\\r', '')
        cleaned = ' '.join(cleaned.split())
        return cleaned.strip()

    def clean_author_commas(self, author_string: str) -> str:
        if not author_string:
            return author_string
        cleaned = re.sub(r',\s*,+', ',', author_string)
        cleaned = re.sub(r'^,\s*', '', cleaned)
        cleaned = re.sub(r'\s*,$', '', cleaned)
        cleaned = re.sub(r'\s*,\s*', ', ', cleaned)
        cleaned = re.sub(r',,+', ',', cleaned)
        if re.fullmatch(r'[^,]+,', cleaned.strip()):
            cleaned = cleaned.strip().rstrip(',')
        return cleaned.strip()

    def clean_keywords_metadata(self, raw_keywords: str) -> str:
        if not raw_keywords or raw_keywords in ['N/A', 'No keywords', '']:
            return 'N/A'
        keywords_text = str(raw_keywords).strip()
        pollution_patterns = [
            r'keywords?\s*:?\s*',
            r'anahtar\s*kelime(ler)?\s*:?\s*',
            r'key\s*words?\s*:?\s*',
            r'tags?\s*:?\s*',
            r'subject\s*(terms?)?\s*:?\s*',
        ]
        cleaned = keywords_text
        for pattern in pollution_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\([^)]*keywords?[^)]*\)', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\([^)]*anahtar[^)]*\)', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'^[,\s;]+', '', cleaned)
        cleaned = re.sub(r'[,\s;]+$', '', cleaned)
        cleaned = re.sub(r'[,;]\s*[,;]+', ',', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned)
        if not cleaned.strip() or len(cleaned.strip()) < 3:
            return 'N/A'
        return cleaned.strip()

    def save_search_results(self, results: Dict[str, Any], filename: str = None) -> str:
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            keyword_clean = re.sub(r'[^\w\-_\.]', '_', results['keyword'])
            filename = f"search_{keyword_clean}_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"   💾 Saved: {filename}")
        return filename


# Flask API
def create_unified_search_api():
    """
    Flask API with lazy loading

    The search_engine gets initialized once per worker.
    Data loads on first search, not at startup.
    """
    from flask import Flask, jsonify, request

    app = Flask(__name__)

    # This initialization is LIGHT - no data loaded yet
    search_engine = UnifiedAcademicSearchEngine()

    @app.route('/api/search')
    def api_search():
        keyword = request.args.get('keyword', '')
        max_results_param = request.args.get('max_results', '15')
        relevance_threshold = request.args.get('relevance_threshold', 'medium')

        if max_results_param == 'all':
            max_results = -1
        else:
            max_results = int(max_results_param)

        if len(keyword) < 3:
            return jsonify({'error': 'Keyword must be at least 3 characters'})

        try:
            results = search_engine.search_everything(keyword, max_results, relevance_threshold)
            return jsonify(results)
        except Exception as e:
            import traceback
            return jsonify({
                'error': str(e),
                'traceback': traceback.format_exc()
            }), 500

    @app.route('/api/dergipark')
    def api_dergipark_only():
        keyword = request.args.get('keyword', '')
        max_results_param = request.args.get('max_results', '20')
        relevance_threshold = request.args.get('relevance_threshold', 'medium')

        if max_results_param == 'all':
            max_results = -1
        else:
            max_results = int(max_results_param)

        if len(keyword) < 3:
            return jsonify({'error': 'Keyword must be at least 3 characters'})

        results = search_engine.search_dergipark_local(keyword, max_results, relevance_threshold)

        return jsonify({
            'keyword': keyword,
            'source': 'dergipark_local',
            'total_results': len(results),
            'results': results
        })

    @app.route('/api/trdizin')
    def api_trdizin_only():
        keyword = request.args.get('keyword', '')
        max_results_param = request.args.get('max_results', '20')
        relevance_threshold = request.args.get('relevance_threshold', 'medium')

        if max_results_param == 'all':
            max_results = -1
        else:
            max_results = int(max_results_param)

        if len(keyword) < 3:
            return jsonify({'error': 'Keyword must be at least 3 characters'})

        results = search_engine.search_trdizin_local(keyword, max_results, relevance_threshold)

        return jsonify({
            'keyword': keyword,
            'source': 'trdizin_local',
            'total_results': len(results),
            'results': results
        })

    @app.route('/api/yoktez')
    def api_yoktez_only():
        keyword = request.args.get('keyword', '')
        max_results_param = request.args.get('max_results', '20')

        if max_results_param == 'all':
            max_results = -1
        else:
            max_results = int(max_results_param)

        if len(keyword) < 3:
            return jsonify({'error': 'Keyword must be at least 3 characters'})

        results = search_engine.search_yoktez_local(keyword, max_results)
        return jsonify({
            'keyword': keyword,
            'source': 'yoktez_local',
            'total_results': len(results),
            'results': results
        })

    return app


def main():
    """
    Demo the unified search engine in all its LOCAL CACHE GLORY
    v2.5: Experience the raw speed of NOT launching browsers!
    """
    print("🚀 INITIALIZING THE ULTIMATE ACADEMIC KNOWLEDGE DESTROYER v2.5 🚀")
    print("   (Now with TRIPLE LOCAL CACHE SUPREMACY)")
    print("   (Zero browsers will be launched today, and that's a promise!)")

    # Initialize the search engine
    search_engine = UnifiedAcademicSearchEngine()

    # Let the human decide what they're curious about
    print(f"\n🤔 What academic mysteries shall we unravel today?")
    print("   (Enter your search term - minimum 3 characters)")
    print("   (v2.5: Everything is INSTANT now!)")

    while True:
        keyword = input("\n🔍 Enter your search keyword (or 'quit' to escape): ").strip()

        if keyword.lower() in ['quit', 'exit', 'bye', 'escape']:
            print("👋 Thanks for using the Academic Knowledge Destroyer v2.5!")
            print("   We launched exactly ZERO browsers during your session!")
            print("   May your research be fruitful and your citations properly formatted!")
            break

        if len(keyword) < 3:
            print("❌ Come on, give me at least 3 characters to work with!")
            print("   I'm powerful, but I'm not a mind reader (yet)")
            continue

        # Let the user choose their adventure
        print(f"\n🎯 How shall we hunt for '{keyword}'?")
        print("   1. 🔥 EVERYTHING (All 3 sources) - TRIPLE LOCAL CACHE POWER")
        print("   2. ⚡ Dergipark only (Local cache)")
        print("   3. 📖 TRDizin only (Local cache)")
        print("   4. 🎓 YÖK Tez only (Local cache - NO MORE BROWSERS!)")
        choice = input("\nChoose your weapon (1/2/3/4): ").strip()

        print(f"\n📊 How many results do you want?")
        print("   1. 20 Results (Quick & Focused)")
        print("   2. 50 Results (Comprehensive)")
        print("   3. 100 Results (Deep Dive)")
        print("   4. ALL Results (Academic Apocalypse)")

        limit_choice = input("\nChoose your result limit (1/2/3/4): ").strip()

        limit_map = {
            '1': 20,
            '2': 50,
            '3': 100,
            '4': -1  # Special code for "GIVE ME EVERYTHING"
        }

        max_results = limit_map.get(limit_choice, 20)  # Default to 20 if they can't follow instructions

        # THE CRITICAL ADDITION: Ask about relevance philosophy
        print(f"\n🎚️ What's your tolerance for academic bullshit?")
        print("   (AKA: How strict should we be about relevance?)")
        print("   1. 🎯 Çok Alakalı - I'm a perfectionist, show me only the intellectual elite")
        print("   2. ⚖️ Alakalı - Balanced approach, quality but not psychotic about it")
        print("   3. 🌊 Az Alakalı - Cast a wide net, I'll sort through the chaos myself")

        relevance_choice = input("\nChoose your relevance philosophy (1/2/3): ").strip()

        # Convert user choice to actual threshold values
        relevance_map = {
            '1': 'high',    # The academic perfectionists
            '2': 'medium',  # The reasonable humans
            '3': 'low'      # The chaos embracers
        }

        relevance_threshold = relevance_map.get(relevance_choice, 'medium')  # Default to sanity

        if max_results == -1:
            print(f"   🔥 UNLEASHING ALL AVAILABLE RESULTS (You asked for it!)")
        else:
            print(f"   📋 Limiting to {max_results} results (as per your sovereign choice)")

        if choice == "1":
            print(f"\n🔥 LAUNCHING FULL SPECTRUM SEARCH FOR: '{keyword}'")
            print("   (v2.5: All from local cache - this will be INSTANT!)")
            results = search_engine.search_everything(keyword, max_results, relevance_threshold)

            # Save results
            filename = search_engine.save_search_results(results)

            # Show sample results
            if results['sources']['dergipark']['results']:
                print(f"\n📚 Sample Dergipark Results:")
                for i, article in enumerate(results['sources']['dergipark']['results'][:3]):
                    print(f"   {i+1}. {article['title'][:60]}...")
                    print(f"      Authors: {article['authors'][:50]}...")

            if results['sources']['trdizin']['results']:
                print(f"\n📖 Sample TRDizin Results:")
                for i, article in enumerate(results['sources']['trdizin']['results'][:3]):
                    print(f"   {i+1}. {article['title'][:60]}...")
                    print(f"      DOI: {article['doi']}")

            if results['sources']['yoktez']['results']:
                print(f"\n🎓 Sample YÖK Tez Results (FROM LOCAL CACHE!):")
                for i, thesis in enumerate(results['sources']['yoktez']['results'][:3]):
                    print(f"   {i+1}. {thesis['title'][:60]}...")
                    print(f"      ID: {thesis['thesis_id']}")

            print(f"\n💾 Full results saved to: {filename}")
            print(f"⚡ Search completed in {results['total_search_time_seconds']} seconds!")

        elif choice == "2":
            print(f"\n⚡ LIGHTNING FAST LOCAL SEARCH FOR: '{keyword}'")
            results = search_engine.search_dergipark_local(keyword, max_results, relevance_threshold)

            if results:
                display_count = min(5, len(results))
                print(f"\n📚 Found {len(results)} Dergipark articles (showing first {display_count}):")
                for i, article in enumerate(results[:display_count]):
                    print(f"   {i+1}. {article['title'][:60]}...")
                    print(f"      Authors: {article['authors'][:50]}...")

                if len(results) > 5:
                    print(f"   ... and {len(results) - 5} more results")
            else:
                print("   😔 No matches found in local Dergipark cache")

        elif choice == "3":
            print(f"\n📖 BILINGUAL LOCAL SEARCH FOR: '{keyword}'")
            results = search_engine.search_trdizin_local(keyword, max_results, relevance_threshold)

            if results:
                display_count = min(5, len(results))
                print(f"\n📖 Found {len(results)} TRDizin articles (showing first {display_count}):")
                for i, article in enumerate(results[:display_count]):
                    print(f"   {i+1}. {article['title'][:60]}...")
                    print(f"      DOI: {article['doi']}")

                if len(results) > 5:
                    print(f"   ... and {len(results) - 5} more results")
            else:
                print("   😔 No matches found in local TRDizin cache")

        elif choice == "4":
            print(f"\n🎓 LOCAL YÖK TEZ SEARCH FOR: '{keyword}'")
            print("   (v2.5: FROM COMPRESSED PARQUET - NO BROWSERS!)")
            results = search_engine.search_yoktez_local(keyword, max_results, relevance_threshold)

            if results:
                display_count = min(5, len(results))
                print(f"\n🎓 Found {len(results)} YÖK Tez theses (showing first {display_count}):")
                for i, thesis in enumerate(results[:display_count]):
                    print(f"   {i+1}. {thesis['title'][:60]}...")
                    print(f"      ID: {thesis['thesis_id']}")

                if len(results) > 5:
                    print(f"   ... and {len(results) - 5} more results")
            else:
                print("   😔 No theses found in local YÖK Tez cache")
        else:
            print("   🤷 Invalid choice! Pick 1, 2, 3, or 4 (or learn to follow simple instructions)")
            continue

        print(f"\n" + "="*60)
        print("🎉 Search mission accomplished! Want to search for something else?")
        print("   (All searches powered by LOCAL CACHE - Zero browsers harmed!)")

if __name__ == "__main__":
    main()
