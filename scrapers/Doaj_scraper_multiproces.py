import requests
import json
import time
import csv
import pandas as pd
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
import logging
from datetime import datetime
import asyncio
import aiohttp
import math
from multiprocessing import Pool, cpu_count
from functools import partial
from trdizin_time_calculator import SimpleTRDizinTracker, SimpleFileManager
from dataclasses import asdict

@dataclass
class Article:
    """
    A structured container for academic paper data.
    Because chaos needs organization, even in the digital realm.
    """
    article_id: str
    titles: List[Dict[str, str]]  # [{"language": "ENG", "title": "..."}]
    abstracts: List[Dict[str, Any]]  # Full abstract objects with keywords
    authors: List[Dict[str, Any]]  # Author objects with all metadata
    publication_year: Optional[int] = None
    journal_info: Optional[Dict[str, Any]] = None
    doi: Optional[str] = None

class TRDizinMultiprocessingDestroyer:
    """
    The unholy fusion of your TRDizin scraper with multiprocessing violence.
    
    This class represents the philosophical rejection of sequential suffering
    in favor of parallel processing supremacy for Turkish academic databases.
    """
    
    def __init__(self, max_concurrent=50, num_processes=None, request_timeout=30):
        """Initialize the academic liberation machine with parallel processing consciousness"""
        self.base_url = "https://search.trdizin.gov.tr"
        self.api_endpoint = f"{self.base_url}/api/defaultSearch/publication/"
        
        self.max_concurrent = max_concurrent
        self.num_processes = num_processes or cpu_count()
        self.timeout = request_timeout
        
        # Professional browser cosplay headers (because APIs judge you)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9,tr;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://search.trdizin.gov.tr/tr/yayin/ara',
            'Connection': 'keep-alive',
        }
        
        # Setup logging because debugging is life
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        self.logger.info(f"🚀 Initializing TRDizin Academic Annihilator")
        self.logger.info(f"   CPU cores enlisted: {self.num_processes}")
        self.logger.info(f"   Concurrent connections per core: {max_concurrent}")
        self.logger.info(f"   Total destruction capacity: {self.num_processes * max_concurrent}")

    def get_articles_page(self, page: int = 1, limit: int = 100, order: str = "publicationYear-DESC", 
                         query: str = "", year_filter: str = None) -> Optional[Dict]:
        """
        Fetch a single page of article data from the API.
        Returns raw JSON response or None when shit hits the fan.
        """
        params = {
            'q': query,
            'order': order,
            'page': page,
            'limit': limit
        }
        
        # Add year filter if specified
        if year_filter:
            params['year'] = year_filter
        
        try:
            session = requests.Session()
            session.headers.update(self.headers)
            
            self.logger.debug(f"🔍 Fetching articles page {page} (limit: {limit})...")
            response = session.get(self.api_endpoint, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            session.close()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"💥 Request failed for page {page}: {e}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"💥 JSON parsing failed for page {page}: {e}")
            return None


    def parse_article_from_source(self, source_data: Dict) -> Article:
        """
        Extract and structure article data from the _source container.
        Now with bulletproof defenses against API fuckery.
        """
        try:
            # Extract basic identifiers with paranoid safety checks
            article_id = source_data.get('id', 'unknown')
            
            # Extract titles from abstracts with extreme prejudice against None values
            titles = []
            abstracts = source_data.get('abstracts', [])
            
            # Paranoid None checking because APIs are chaotic bastards
            if abstracts is not None and isinstance(abstracts, list):
                for abstract_obj in abstracts:
                    if (abstract_obj is not None and isinstance(abstract_obj, dict) and 
                        'title' in abstract_obj and 'language' in abstract_obj):
                        titles.append({
                            'language': abstract_obj['language'],
                            'title': abstract_obj['title']
                        })
            else:
                # Fallback: maybe titles are somewhere else in this digital chaos
                if 'title' in source_data:
                    titles.append({
                        'language': source_data.get('language', 'UNK'),
                        'title': source_data['title']
                    })
            
            # Extract authors with maximum paranoia
            authors = source_data.get('authors', [])
            if authors is None:
                authors = []
            elif not isinstance(authors, list):
                # Sometimes APIs return a single author object instead of a list
                if isinstance(authors, dict):
                    authors = [authors]
                else:
                    authors = []
            
            # Extract publication year with error handling for academic chaos
            pub_year = source_data.get('publicationYear')
            if isinstance(pub_year, str):
                try:
                    pub_year = int(pub_year)
                except (ValueError, TypeError):
                    pub_year = None
            elif not isinstance(pub_year, int):
                pub_year = None
            
            # Extract journal information (if it exists in this digital hellscape)
            journal_info = source_data.get('journal', {})
            if journal_info is None:
                journal_info = {}
            
            # Extract DOI (Digital Object Identifier or Digital Object Insanity?)
            doi = source_data.get('doi')
            if doi is not None and not isinstance(doi, str):
                doi = str(doi) if doi else None
            
            # Ensure abstracts is always a list (because consistency is dead)
            if abstracts is None:
                abstracts = []
            elif not isinstance(abstracts, list):
                abstracts = [abstracts] if isinstance(abstracts, dict) else []
            
            return Article(
                article_id=str(article_id),
                titles=titles,
                abstracts=abstracts,
                authors=authors,
                publication_year=pub_year,
                journal_info=journal_info,
                doi=doi,
            )
            
        except Exception as e:
            # Log the specific data that caused the clusterfuck
            self.logger.error(f"💀 Article parsing apocalypse: {e}")
            
            # Return a minimal article object to prevent total system collapse
            return Article(
                article_id=str(source_data.get('id', 'error_article')),
                titles=[],
                abstracts=[],
                authors=[],
                publication_year=None,
                journal_info={},
                doi=None,
            )

    
    def scrape_all_articles_SIMPLE(self, max_pages: int = None, delay: float = 0.5, 
                              query: str = "", year_filter: str = None) -> List[Article]:
        """
        Multiprocessing academic annihilation without the existential crisis commentary
        """
        self.logger.info("🎯 STARTING TRDIZIN MULTIPROCESSING SCRAPER")
        
        # Simple tracking - no philosophical bullshit
        from trdizin_time_calculator import SimpleTRDizinTracker, SimpleFileManager
        
        if max_pages is None:
            max_pages = self.discover_total_pages(query=query, year_filter=year_filter)
            max_pages = min(max_pages, 6524)  # Don't murder their servers
        
        tracker = SimpleTRDizinTracker(total_pages=max_pages)
        file_manager = SimpleFileManager("trdizin_articles.parquet")
        
        tracker.start_session()
        
        # Generate page chunks for multiprocessing
        page_numbers = list(range(1, max_pages + 1))
        chunk_size = math.ceil(len(page_numbers) / self.num_processes)
        
        process_args = []
        for i in range(0, len(page_numbers), chunk_size):
            chunk = page_numbers[i:i + chunk_size]
            if chunk:
                process_args.append((
                    chunk, query, year_filter, self.headers, 
                    self.api_endpoint, self.timeout, delay
                ))
        
        self.logger.info(f"🚀 Launching {len(process_args)} processes...")
        
        # Execute multiprocessing
        with Pool(processes=self.num_processes) as pool:
            chunk_results = pool.map(process_page_chunk_simple, process_args)
            
            # Process results
            for chunk_articles, pages_done, batch_time in chunk_results:
                # Update progress tracking
                tracker.update_progress(pages_done, batch_time)
                
                # Save batch
                if chunk_articles:
                    file_manager.save_batch([asdict(article) for article in chunk_articles])
        
        # Final stats
        final_stats = file_manager.get_stats()
        self.logger.info(f"🎉 SCRAPING COMPLETE!")
        self.logger.info(f"   Articles: {final_stats['total_articles']:,}")
        self.logger.info(f"   File: {final_stats['file_path']}")
        self.logger.info(f"   Size: {final_stats['file_size_mb']:.1f}MB")
        
        return []
    # Original save methods (unchanged but with some optimization)
    def save_to_parquet(self, articles: List[Article], filename: str = "trdizin_articles.parquet"):
        """
        Save articles to Parquet format with brutal efficiency.
        Strips abstract text bloat while preserving essential metadata.
        """
        try:
            parquet_data = []
            
            for article in articles:
                # Create base row with scalar values
                row = {
                    'article_id': article.article_id,
                    'publication_year': article.publication_year,
                    'doi': article.doi,
                }
                
                # Handle titles
                title_dict = {}
                keyword_dict = {}
                
                for title_obj in article.titles:
                    if title_obj and isinstance(title_obj, dict):
                        lang = str(title_obj.get('language')).lower()
                        title_dict[f'title_{lang}'] = title_obj.get('title', '')
                
                # Process abstracts ONLY for keywords and metadata
                for abstract_obj in article.abstracts:
                    if abstract_obj and isinstance(abstract_obj, dict):
                        lang = str(abstract_obj.get('language')).lower()
                        
                        # Extract keywords
                        keywords = abstract_obj.get('keywords', [])
                        if keywords and isinstance(keywords, list):
                            keyword_dict[f'keywords_{lang}'] = '|'.join([str(k) for k in keywords if k])
                        else:
                            keyword_dict[f'keywords_{lang}'] = ''
                
                # Ensure consistent columns
                for lang in ['tur', 'eng']:
                    if f'title_{lang}' not in title_dict:
                        title_dict[f'title_{lang}'] = ''
                    if f'keywords_{lang}' not in keyword_dict:
                        keyword_dict[f'keywords_{lang}'] = ''
                        
                row.update(title_dict)
                row.update(keyword_dict)
                
                # Handle authors
                author_names = []
                for author in article.authors:
                    if author and isinstance(author, dict):
                        name = author.get('name', '')
                        if name:
                            author_names.append(str(name))
                    elif author and isinstance(author, str):
                        author_names.append(str(author))
                
                row['authors'] = '|'.join(author_names) if author_names else ''
                
                # Handle journal information
                if article.journal_info and isinstance(article.journal_info, dict):
                    row.update({
                        'journal_name': str(article.journal_info.get('name', '')),
                        'journal_issn': str(article.journal_info.get('issn', '')),
                        'journal_eissn': str(article.journal_info.get('eissn', '')),
                        'journal_id': str(article.journal_info.get('id', ''))
                    })
                else:
                    row.update({
                        'journal_name': '',
                        'journal_issn': '',
                        'journal_eissn': '',
                        'journal_id': ''
                    })
                
                parquet_data.append(row)
            
            # Convert to DataFrame with optimized dtypes
            df = pd.DataFrame(parquet_data)
            
            if 'publication_year' in df.columns:
                df['publication_year'] = pd.to_numeric(df['publication_year'], errors='coerce').astype('Int64')
            
            # Save to Parquet with maximum compression
            df.to_parquet(
                filename,
                engine='pyarrow',
                compression='snappy',
                index=False,
                use_deprecated_int96_timestamps=False
            )
            
            self.logger.info(f"💾 Saved {len(articles)} articles to optimized Parquet: {filename}")
            self.logger.info(f"📊 Schema: {len(df.columns)} columns, {len(df)} rows")
            
            return True
            
        except ImportError:
            self.logger.error("💥 Parquet export requires pyarrow: pip install pyarrow")
            return False
        except Exception as e:
            self.logger.error(f"💥 Failed to save Parquet: {e}")
            return False

# --- STANDALONE FUNCTIONS FOR PICKLE-SAFE MULTIPROCESSING ---
# These exist outside the class to avoid Python's pickle anxiety disorder

def get_articles_page_standalone(page, query, year_filter, headers, api_endpoint, timeout):
    """
    Standalone page fetcher for multiprocessing
    Because Python multiprocessing has commitment issues with class methods
    """
    params = {
        'q': query,
        'order': "publicationYear-DESC",
        'page': page,
        'limit': 100
    }
    
    if year_filter:
        params['year'] = year_filter
    
    try:
        session = requests.Session()
        session.headers.update(headers)
        
        response = session.get(api_endpoint, params=params, timeout=timeout)
        response.raise_for_status()
        
        session.close()
        return response.json()
        
    except Exception as e:
        logging.error(f"💥 Page {page} failed: {e}")
        return None

def extract_articles_from_response_standalone(response_data):
    """Standalone article extraction for multiprocessing"""
    articles = []
    
    if not response_data:
        return articles
    
    # Handle Elasticsearch hits structure
    if 'hits' in response_data and isinstance(response_data['hits'], dict):
        hits = response_data['hits'].get('hits', [])
    elif isinstance(response_data, list):
        hits = response_data
    else:
        hits = []
        for key, value in response_data.items():
            if isinstance(value, list) and len(value) > 0:
                if isinstance(value[0], dict) and '_source' in value[0]:
                    hits = value
                    break
    
    for hit in hits:
        try:
            if isinstance(hit, dict) and '_source' in hit:
                source_data = hit['_source']
                article = parse_article_from_source_standalone(source_data)
                articles.append(article)
        except Exception as e:
            logging.error(f"💥 Failed to parse article: {e}")
            continue
    
    return articles

def parse_article_from_source_standalone(source_data):
    """Standalone article parser for multiprocessing"""
    try:
        # Extract basic identifiers
        article_id = source_data.get('id', 'unknown')
        
        # Extract titles
        titles = []
        abstracts = source_data.get('abstracts', [])
        
        if abstracts is not None and isinstance(abstracts, list):
            for abstract_obj in abstracts:
                if (abstract_obj is not None and isinstance(abstract_obj, dict) and 
                    'title' in abstract_obj and 'language' in abstract_obj):
                    titles.append({
                        'language': abstract_obj['language'],
                        'title': abstract_obj['title']
                    })
        else:
            if 'title' in source_data:
                titles.append({
                    'language': source_data.get('language', 'UNK'),
                    'title': source_data['title']
                })
        
        # Extract authors
        authors = source_data.get('authors', [])
        if authors is None:
            authors = []
        elif not isinstance(authors, list):
            if isinstance(authors, dict):
                authors = [authors]
            else:
                authors = []
        
        # Extract publication year
        pub_year = source_data.get('publicationYear')
        if isinstance(pub_year, str):
            try:
                pub_year = int(pub_year)
            except (ValueError, TypeError):
                pub_year = None
        elif not isinstance(pub_year, int):
            pub_year = None
        
        # Extract journal info
        journal_info = source_data.get('journal', {})
        if journal_info is None:
            journal_info = {}
        
        # Extract DOI
        doi = source_data.get('doi')
        if doi is not None and not isinstance(doi, str):
            doi = str(doi) if doi else None
        
        # Ensure abstracts is always a list
        if abstracts is None:
            abstracts = []
        elif not isinstance(abstracts, list):
            abstracts = [abstracts] if isinstance(abstracts, dict) else []
        
        return Article(
            article_id=str(article_id),
            titles=titles,
            abstracts=abstracts,
            authors=authors,
            publication_year=pub_year,
            journal_info=journal_info,
            doi=doi,
        )
        
    except Exception as e:
        logging.error(f"💀 Article parsing failed: {e}")
        return Article(
            article_id=str(source_data.get('id', 'error_article')),
            titles=[],
            abstracts=[],
            authors=[],
            publication_year=None,
            journal_info={},
            doi=None,
        )
def process_page_chunk_simple(chunk_data):
    """
    Process page chunk without temporal philosophy degree requirements
    """
    page_numbers, query, year_filter, headers, api_endpoint, timeout, delay = chunk_data
    
    start_time = time.time()
    all_articles = []
    
    for page_num in page_numbers:
        try:
            response_data = get_articles_page_standalone(
                page_num, query, year_filter, headers, api_endpoint, timeout
            )
            
            if response_data:
                page_articles = extract_articles_from_response_standalone(response_data)
                all_articles.extend(page_articles)
            
            if delay > 0:
                time.sleep(delay)
                
        except Exception as e:
            logging.error(f"💥 Page {page_num} failed: {e}")
    
    batch_time = time.time() - start_time
    return (all_articles, len(page_numbers), batch_time)
def process_page_chunk_with_oracle_standalone(chunk_data):
    """
    The pickle-safe bridge for processing page chunks WITH TEMPORAL AWARENESS
    
    This function processes multiple pages in a single process while tracking
    performance metrics for the time oracle's prophecy calculations.
    """
    page_numbers, query, year_filter, headers, api_endpoint, timeout, delay, process_id = chunk_data
    
    logging.info(f"🔥 Process-{process_id} starting work on {len(page_numbers)} pages...")
    
    all_articles = []
    pages_successfully_processed = 0
    
    for page_num in page_numbers:
        try:
            # Get page data
            response_data = get_articles_page_standalone(
                page_num, query, year_filter, headers, api_endpoint, timeout
            )
            
            if response_data:
                # Extract articles from this page
                page_articles = extract_articles_from_response_standalone(response_data)
                all_articles.extend(page_articles)
                pages_successfully_processed += 1
                
                logging.info(f"✅ Process-{process_id} Page {page_num}: {len(page_articles)} articles")
            else:
                logging.warning(f"💀 Process-{process_id} Page {page_num}: No data returned")
            
            # Be nice to the servers
            if delay > 0:
                time.sleep(delay)
                
        except Exception as e:
            logging.error(f"💥 Process-{process_id} Page {page_num} failed: {e}")
            continue
    
    logging.info(f"🎉 Process-{process_id} complete: {len(all_articles)} articles from {pages_successfully_processed} pages")
    
    # Return tuple: (articles, pages_processed, process_id)
    return (all_articles, pages_successfully_processed, process_id)

def main():
    """
    The main event - multiprocessing academic liberation in action!
    """
    print("🚀 TRDIZIN MULTIPROCESSING DESTROYER: Academic Liberation Front 2.0")
    print("="*70)
    
    scraper = TRDizinMultiprocessingDestroyer(
        max_concurrent=20,  # Conservative for API politeness
    )
    
    # Configuration options
    config = {
        'max_pages': 4,  # Increase for full-scale academic annihilation
        'delay': 0,     # Be nice to their servers
        'query': '',      # Empty = all articles
        'year_filter': None  # e.g., '2024' for specific year
    }
    
    print(f"🎯 Configuration:")
    print(f"   Max pages: {config['max_pages']}")
    print(f"   Processes: {scraper.num_processes}")
    print(f"   Query: '{config['query']}'")
    print(f"   Year filter: {config['year_filter']}")
    print(f"   Delay: {config['delay']}s between requests")
    
    print("\n🔥 Starting multiprocessing academic annihilation...")
    
    # Unleash the multiprocessing beast
    articles = scraper.scrape_all_articles_SIMPLE(
        max_pages=config['max_pages'],
        delay=config['delay'],
        query=config['query'],
        year_filter=config['year_filter']
    )
    
    if articles:
        print(f"\n✅ Successfully annihilated {len(articles)} articles!")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        parquet_filename = f"trdizin_multiprocessing_{timestamp}.parquet"
        
        scraper.save_to_parquet(articles, parquet_filename)
        
        print(f"\n🎉 MULTIPROCESSING MISSION ACCOMPLISHED!")
        print(f"📁 File generated: {parquet_filename}")
        
        # Show performance insights
        if len(articles) > 0:
            sample = articles[0]
            print(f"\n📋 Sample article:")
            print(f"   ID: {sample.article_id}")
            print(f"   Titles: {len(sample.titles)} languages")
            print(f"   Authors: {len(sample.authors)}")
            print(f"   Year: {sample.publication_year}")
        
    else:
        print("💀 Multiprocessing annihilation failed. Check API availability.")

if __name__ == "__main__":
    main()