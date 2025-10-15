# THE ULTIMATE DERGIPARK ACADEMIC ANNIHILATION MACHINE
# Hybrid Async + Multiprocessing approach to systematically consume Turkish academic publishing
# at computational speeds that would make your old scraper commit digital suicide

import asyncio
import aiohttp
import pandas as pd
import time
import re
import requests
from multiprocessing import Pool, cpu_count
from functools import partial
from bs4 import BeautifulSoup
import math
from datetime import datetime
from urllib.parse import urljoin
import logging
from pathlib import Path
from scrape_time_calculator import AcademicScrapingTimeOracle, UnifiedParquetBatchManager
# Configure logging because we want to witness the beautiful chaos unfold
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Configuration for the Academic Apocalypse ---
BASE_URL = "https://dergipark.org.tr"
JOURNALS_EXPLORE_BASE_URL = "https://dergipark.org.tr/en/pub/explore/journals"
OUTPUT_FILENAME = "Parquet_dergipark_HYBRID"
MAX_JOURNALS_TO_PROCESS = 99  # Because why limit academic domination?
MAX_JOURNAL_EXPLORE_PAGES = 3


# HYBRID PERFORMANCE SETTINGS - Adjust these to unleash controlled violence
MAX_CONCURRENT_PER_PROCESS = 150  # How many simultaneous requests per CPU core
REQUEST_TIMEOUT = 15  # Don't wait forever for slow servers
BATCH_SAVE_SIZE = 1000  # Save results in batches to prevent memory overflow

class SequentialScrapingMasochist:
    """
    Your old approach - for benchmarking purposes only
    
    This class exists purely to demonstrate how much computational suffering
    you've been inflicting upon yourself like some kind of digital monk
    """
    
    def __init__(self):
        self.scraper = HybridDergiparkDestroyer()
    
    def scrape_articles_sequentially(self, article_urls, journal_slug):
        """Sequential suffering - one article at a time like a polite Victorian gentleman"""
        logger.info(f"😴 SEQUENTIAL MASOCHISTIC BENCHMARK STARTING")
        logger.info(f"   Articles to torture sequentially: {len(article_urls)}")
        
        start_time = time.time()
        successful_articles = []
        
        session = requests.Session()
        
        for i, url in enumerate(article_urls):
            try:
                logger.debug(f"🐌 Sequential crawl {i+1}/{len(article_urls)}")
                response = session.get(url, timeout=15)
                
                if response.status_code == 200:
                    article_data = self.scraper.extract_article_data_from_html(
                        response.text, url, journal_slug
                    )
                    if article_data:
                        successful_articles.append(article_data)
                
                
            except Exception as e:
                logger.error(f"💀 Sequential failure: {e}")
                continue
        
        elapsed = time.time() - start_time
        articles_per_second = len(successful_articles) / elapsed if elapsed > 0 else 0
        
        logger.info(f"😵 SEQUENTIAL BENCHMARK COMPLETE")
        logger.info(f"   Speed: {articles_per_second:.2f} articles/second")
        logger.info(f"   Computational dignity: OBLITERATED")
        
        session.close()
        return successful_articles, articles_per_second, elapsed

class HybridDergiparkDestroyer:
    """
    The philosophical embodiment of "Why scrape sequentially when you can 
    systematically consume Turkish academic databases through parallel processing violence?"
    
    This class represents humanity's rejection of waiting politely for web servers
    """
    
    def __init__(self, max_concurrent_per_process=MAX_CONCURRENT_PER_PROCESS, 
                 num_processes=None, request_timeout=REQUEST_TIMEOUT):
        """Initialize the academic knowledge devourer with parallel processing consciousness"""
        self.max_concurrent = max_concurrent_per_process
        self.num_processes = num_processes or cpu_count()
        self.timeout = request_timeout
        self.session_config = {
            'timeout': aiohttp.ClientTimeout(total=request_timeout),
            'connector': aiohttp.TCPConnector(
                limit=100, limit_per_host=30, enable_cleanup_closed=True
            )
        }
        
        logger.info(f"🚀 Initializing Dergipark Academic Annihilator")
        logger.info(f"   CPU cores enlisted: {self.num_processes}")
        logger.info(f"   Concurrent connections per core: {max_concurrent_per_process}")
        logger.info(f"   Total simultaneous destruction capacity: {self.num_processes * max_concurrent_per_process}")
    async def scrape_all_issues_parallel(self, issue_links, journal_slug):
            """
            The missing piece - parallel issue processing to eliminate the chokepoint
            
            This is where we apply parallel processing to EVERY FUCKING STEP
            instead of just the final article scraping phase
            """
            semaphore = asyncio.Semaphore(20)  # Control the chaos
            session_config = {
        'timeout': aiohttp.ClientTimeout(total=self.timeout),  # NOW it works!
        'connector': aiohttp.TCPConnector(
            limit=100, limit_per_host=30, enable_cleanup_closed=True
        )
    }
            async with aiohttp.ClientSession(**session_config) as session:
                tasks = [
                    self.scrape_single_issue_async(session, issue, journal_slug, semaphore)
                    for issue in issue_links
                ]
                
                logger.info(f"🚀 Parallel processing {len(tasks)} issues...")
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Flatten all article URLs from all issues
                all_article_urls = []
                for issue_articles in results:
                    if isinstance(issue_articles, list):
                        all_article_urls.extend(issue_articles)
                
                return all_article_urls
    def extract_articles_from_issue_html(self, html_content, issue_url, journal_slug):
        """
        Extract article URLs from issue HTML - the missing piece of your async puzzle
        
        This is basically your existing scrape_articles_from_issue_page logic
        but adapted for HTML content instead of making HTTP requests
        """
        articles_in_issue = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # Your existing article discovery logic
            articles_listing_div = soup.find('div', id='articles-listing')
            article_card_elements = []

            if articles_listing_div:
                article_card_elements = articles_listing_div.select('div.article-card-block')
            else:
                article_card_elements = soup.select('div.article-card-block')

            for card_element in article_card_elements:
                article_link_el = card_element.select_one('a.card-title.article-title[href*="/pub/"]')
                
                if article_link_el and 'href' in article_link_el.attrs:
                    article_rel_url = article_link_el['href']
                    article_full_url = urljoin(issue_url, article_rel_url)
                    article_title = article_link_el.get_text(strip=True)

                    # RETURN PROPER DICTIONARY OBJECTS
                    articles_in_issue.append({
                        'url': article_full_url,
                        'title': article_title,
                        'journal_slug': journal_slug
                    })
        except Exception as e:
            logger.error(f"Error extracting articles from issue HTML: {e}")

        return articles_in_issue
    async def scrape_single_issue_async(self, session, issue_data, journal_slug, semaphore):
            """
            Async issue scraper - because why process issues sequentially 
            when you can SIMULTANEOUSLY CONSUME ALL OF THEM?
            """
            async with semaphore:
                try:
                    async with session.get(issue_data['url']) as response:
                        if response.status == 200:
                            html = await response.text()
                            return self.extract_articles_from_issue_html(html, issue_data['url'], journal_slug)
                            
                except Exception as e:
                    logger.warning(f"💥 Issue scraping failed: {e}")
                    return []
    # --- Original Journal Discovery Functions (Unchanged) ---
    def get_journal_slugs_and_titles_by_scraping(self):
        """Your existing journal discovery logic - no changes needed here"""
        journal_data = []
        seen_slugs = set()
        page_num = 2

        while page_num <= MAX_JOURNAL_EXPLORE_PAGES:
            url = f"{JOURNALS_EXPLORE_BASE_URL}/{page_num}"
            logger.info(f"Scraping journal list page: {url}")
            
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')

                journal_elements = soup.select('h5 a[href*="/pub/"]')

                if not journal_elements:
                    logger.warning(f"No journal links found on page {page_num}")
                    break

                for link in journal_elements:
                    href = link['href']
                    title = link.get_text(strip=True)

                    match = re.search(r'/pub/([a-zA-Z0-9_-]+)$', href)
                    if match:
                        slug = match.group(1)
                        if slug not in seen_slugs:
                            journal_data.append({
                                'journal_slug': slug, 
                                'title': title, 
                                'explore_url': href
                            })
                            seen_slugs.add(slug)

                logger.info(f"  Found {len(seen_slugs)} unique journal slugs total")
                page_num += 1

            except Exception as e:
                logger.error(f"Error scraping journal list: {e}")
                break

        return journal_data

    def scrape_issue_links_from_archive(self, archive_url):
        """Your existing issue discovery logic"""
        issue_links = []
        logger.debug(f"Scraping issue links from: {archive_url}")
        
        try:
            response = requests.get(archive_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            issue_link_elements = soup.select('a[href*="/issue/"]:not([href*="/article/"])')
            
            for link in issue_link_elements:
                full_url = urljoin(archive_url, link['href'])
                if '/issue/' in full_url and 'article' not in full_url:
                    issue_links.append({
                        'url': full_url, 
                        'title': link.get_text(strip=True)
                    })
                    
        except Exception as e:
            logger.error(f"Error scraping archive page {archive_url}: {e}")
            
        return issue_links

    def scrape_articles_from_issue_page(self, issue_url, journal_slug):
        """Your existing article URL discovery logic"""
        articles_in_issue = []
        
        try:
            response = requests.get(issue_url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Try to find articles listing
            articles_listing_div = soup.find('div', id='articles-listing')
            article_card_elements = []

            if articles_listing_div:
                article_card_elements = articles_listing_div.select('div.article-card-block')
            else:
                article_card_elements = soup.select('div.article-card-block')

            for card_element in article_card_elements:
                article_link_el = card_element.select_one('a.card-title.article-title[href*="/pub/"]')
                
                if article_link_el and 'href' in article_link_el.attrs:
                    article_rel_url = article_link_el['href']
                    article_full_url = urljoin(issue_url, article_rel_url)
                    article_title = article_link_el.get_text(strip=True)

                    articles_in_issue.append({
                        'url': article_full_url,
                        'title': article_title,
                        'journal_slug': journal_slug
                    })

        except Exception as e:
            logger.error(f"Error processing issue {issue_url}: {e}")

        return articles_in_issue

    def collect_all_article_urls_for_journal(self, journal_slug):
    
        all_articles_for_journal = []
        
        archive_url = f"{BASE_URL}/en/pub/{journal_slug}/archive"
        logger.info(f"  Collecting articles for journal: {journal_slug}")

        issue_links = self.scrape_issue_links_from_archive(archive_url)
        
        if not issue_links:
            # Fallback logic (unchanged)
            main_journal_url = f"{BASE_URL}/en/pub/{journal_slug}"
            articles_from_main_page = self.scrape_articles_from_issue_page(main_journal_url, journal_slug)
            if articles_from_main_page:
                all_articles_for_journal.extend(articles_from_main_page)
            return all_articles_for_journal

        logger.info(f"  Found {len(issue_links)} issues for journal '{journal_slug}'")
        
        # THE ASYNC PORTAL ACTIVATION
        # Instead of sequential masochism, we use asyncio.run() to bridge realities
        all_articles_for_journal = asyncio.run(
            self.scrape_all_issues_parallel(issue_links, journal_slug)
        )

        return all_articles_for_journal
    def collect_all_dergipark_data_HYBRID(self):
        """
        The main event - where we systematically consume Turkish academic publishing
        at speeds that would make your old scraper commit digital suicide
        """
        logger.info("🎯 STARTING HYBRID DERGIPARK ANNIHILATION!")
        logger.info("   Extracting ALL the academic goodies at parallel processing speeds!")
        batch_manager = UnifiedParquetBatchManager("articles_dergipark_UNIFIED")
        oracle = AcademicScrapingTimeOracle(total_journals=2480)
        oracle.start_session()

        all_journals_data = []
        all_articles_data = []

        # Discover all journals (unchanged logic)
        journal_slugs_and_titles = self.get_journal_slugs_and_titles_by_scraping()
        logger.info(f"Found {len(journal_slugs_and_titles)} unique journals")

        seen_article_urls = set()
        
        for j_data in journal_slugs_and_titles:
            slug = j_data['journal_slug']
            j_title = j_data['title']

            logger.info(f"\n📖 Processing journal: '{j_title}' (Slug: {slug})")

            oracle.start_journal(j_title, slug)

            all_journals_data.append({
                'journal_slug': slug,
                'j_title': j_title,
                'explore_url': j_data['explore_url'],
                'last_scraped': time.strftime('%Y-%m-%d %H:%M:%S')
            })

            # Collect all article URLs for this journal
            articles_overview = self.collect_all_article_urls_for_journal(slug)
            
            # Filter out duplicates
            new_article_urls = []
            for article_data in articles_overview:
                if article_data['url'] not in seen_article_urls:
                    seen_article_urls.add(article_data['url'])
                    new_article_urls.append(article_data['url'])
            
            logger.info(f"  📋 Found {len(new_article_urls)} new articles to process")

            if new_article_urls:
                # UNLEASH THE HYBRID BEAST
                journal_articles = self.hybrid_scrape_articles(new_article_urls, slug)
                all_articles_data.extend(journal_articles)
                
                oracle.finish_journal(j_title, len(journal_articles))
        
                # Periodically save progress (every 10 journals)
                if oracle.processed_journals % 10 == 0:
                    oracle.save_progress_checkpoint()

                # Save periodically to prevent data loss
                # NEW UNIFIED SAVING:
                if len(all_articles_data) >= BATCH_SAVE_SIZE:
                    batch_manager.save_batch(all_articles_data, slug)
                    all_articles_data = []  # Clear memory
                    
                    # Optional: Create backup every 10 batches
                    if batch_manager.total_articles_saved % (BATCH_SAVE_SIZE * 10) == 0:
                        batch_manager.create_backup()

        logger.info(f"\n🎉 MISSION ACCOMPLISHED!")
        logger.info(f"   📊 Total articles collected: {len(all_articles_data)}")
        logger.info(f"   📚 Total journals processed: {len(all_journals_data)}")
        
        # NEW UNIFIED FINAL SAVE:
        if all_articles_data:  # Save any remaining articles
            batch_manager.save_batch(all_articles_data)

        # Still save journals separately (they're small)
        if all_journals_data:
            journals_df = pd.DataFrame(all_journals_data)
            journals_df.to_parquet(f'journals_{OUTPUT_FILENAME}.parquet')
            logger.info(f"📚 Saved {len(all_journals_data)} journals")

        # Final statistics
        final_stats = batch_manager.get_current_stats()
        logger.info(f"\n🎉 UNIFIED DATABASE CONSTRUCTION COMPLETE!")
        logger.info(f"   📊 Total articles: {final_stats['total_articles']}")
        logger.info(f"   📁 Database file: {final_stats['file_path']}")
        logger.info(f"   💽 Final file size: {final_stats['file_size_mb']:.1f} MB")        
        logger.info("\n🚀 Data collection finished! Turkish academic database dominated!")


    def extract_article_data_from_html(self, html_content, article_url, journal_slug):
        """
        Extract all academic goodness from HTML content
        
        This is your existing scraping logic, optimized for parallel processing
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Title extraction (your existing logic)
            title = 'N/A'
            title_css = soup.select_one('h3.article-title')
            if title_css:
                title = title_css.get_text(strip=True)
                title = re.sub(r'^\d+\.\s*', '', title).strip()
            
            # Authors extraction (your enhanced logic)
            authors = self.extract_authors(soup)
            
            # Publication date
            publication_date = self.extract_publication_date(soup)
            
            # Keywords extraction
            keywords = self.extract_keywords(soup)
            
            
            return {
                'journal_slug': journal_slug,
                'url': article_url,
                'title': title,
                'authors': authors,
                'publication_date': publication_date,
                'keywords': keywords,
                
                'last_scraped': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"💥 HTML parsing failed for {article_url}: {e}")
            return None

    def extract_authors(self, soup):
        """Extract author information - your existing logic"""
        authors = 'N/A'
        
        # Dergipark-specific structure
        author_container = soup.select_one('p.card-text.article-authors.font-weight-normal, p.article-authors')
        if author_container:
            author_elements = author_container.select('a, span')
            author_names = [elem.get_text(strip=True) for elem in author_elements if elem.get_text(strip=True)]
            if author_names:
                authors = ", ".join(author_names)
        
        # Fallback strategies
        if authors == 'N/A':
            authors_elements = soup.select('p.article-author span, p.article-author a, .article-author-name, .author-name')
            if authors_elements:
                authors = ", ".join([a.get_text(strip=True) for a in authors_elements if a.get_text(strip=True)])
        
        return authors if authors and authors.strip() else 'N/A'

    def extract_publication_date(self, soup):
        """Extract publication date - your existing logic"""
        date_meta = soup.find('meta', {'name': 'citation_publication_date'})
        if date_meta and 'content' in date_meta.attrs:
            return date_meta['content']
        
        date_element = soup.select_one('.article-detail-date, .publication-date, .date')
        if date_element:
            return date_element.get_text(strip=True)
        
        return 'N/A'

    def extract_keywords(self, soup):
        """Extract keywords - your existing logic"""
        keywords_element = soup.select_one('.keywords, .article-keywords, [class*="keyword"]')
        if keywords_element:
            keywords_text = keywords_element.get_text(strip=True)
            return keywords_text.replace("Keywords:", "").strip()
        
        keywords_meta = soup.find('meta', {'name': 'keywords'})
        if keywords_meta and 'content' in keywords_meta.attrs:
            return keywords_meta['content']
        
        return 'N/A'

    
    def extract_doi(self, soup):
        """Extract DOI - your existing logic"""
        doi_element = soup.select_one('.doi, [class*="doi"]')
        if doi_element:
            return doi_element.get_text(strip=True)
        
        doi_meta = soup.find('meta', {'name': 'citation_doi'})
        if doi_meta and 'content' in doi_meta.attrs:
            return doi_meta['content']
        
        return 'N/A'

    def extract_pages(self, soup):
        """Extract page range - your existing logic"""
        pages_element = soup.select_one('.pages, .page-range, [class*="page"]')
        if pages_element:
            return pages_element.get_text(strip=True)
        return 'N/A'

    async def process_article_chunk_async(self, article_urls, journal_slug):
        """
        Process a chunk of articles using async concurrency
        
        This is where the async magic happens - we're processing multiple articles
        simultaneously instead of waiting like digital peasants
        """
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async with aiohttp.ClientSession(**self.session_config) as session:
            tasks = [
                self.scrape_single_article_async(session, url, journal_slug, semaphore)
                for url in article_urls
            ]
            
            logger.info(f"🚀 Launching {len(tasks)} simultaneous attacks...")
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful_results = [
                result for result in results 
                if result is not None and not isinstance(result, Exception)
            ]
            
            logger.info(f"✅ Conquered {len(successful_results)}/{len(article_urls)} articles")
            return successful_results

    def hybrid_scrape_articles(self, all_article_urls, journal_slug):
        """
        The main event - hybrid async + multiprocessing academic annihilation
        BUT WITH PICKLE-PROOF ARCHITECTURE because Python multiprocessing is a diva
        
        This function embodies the principle of "Why choose between async and 
        multiprocessing when you can have BOTH simultaneously WITHOUT pickle nightmares?"
        """
        if not all_article_urls:
            return []
            
        logger.info(f"🎯 INITIATING HYBRID ACADEMIC ANNIHILATION")
        logger.info(f"   Target: {len(all_article_urls)} articles")
        logger.info(f"   Weapons: {self.num_processes} CPU cores + async concurrency")
        logger.info(f"   Pickle avoidance: MAXIMUM (because Python multiprocessing is sensitive)")
        
        start_time = time.time()
        
        # Calculate optimal chunk size per process
        chunk_size = math.ceil(len(all_article_urls) / self.num_processes)
        logger.info(f"   Each process handling ~{chunk_size} articles")
        
        # Split URLs into chunks for each process
        url_chunks = [
            all_article_urls[i:i + chunk_size]
            for i in range(0, len(all_article_urls), chunk_size)
        ]
        
        # Prepare SIMPLE data for multiprocessing (no class instances!)
        chunk_args = [
            (chunk, journal_slug, self.max_concurrent, self.timeout) 
            for chunk in url_chunks if chunk
        ]
        
        logger.info(f"🚀 Launching {len(chunk_args)} pickle-safe parallel processes...")
        
        # Execute multiprocessing with STANDALONE functions (pickle-safe!)
        all_results = []
        with Pool(processes=self.num_processes) as pool:
            chunk_results = pool.map(process_article_chunk_standalone, chunk_args)
            
            # Flatten results from all processes
            for chunk_result in chunk_results:
                all_results.extend(chunk_result)
        
        elapsed_time = time.time() - start_time
        articles_per_second = len(all_results) / elapsed_time if elapsed_time > 0 else 0
        
        logger.info(f"🎉 ACADEMIC ANNIHILATION COMPLETE!")
        logger.info(f"   Articles conquered: {len(all_results)}")
        logger.info(f"   Time elapsed: {elapsed_time:.2f} seconds")
        logger.info(f"   Speed: {articles_per_second:.2f} articles/second")
        
        return all_results

    def save_to_parquet(self, all_articles_data, journals_data, output_filename):
        """Save results to parquet - because parquet is basically the Tesla of data formats"""
        if all_articles_data:
            articles_df = pd.DataFrame(all_articles_data)
            articles_filename = f'articles_{output_filename}.parquet'
            articles_df.to_parquet(articles_filename)
            logger.info(f"🚀 Saved {len(all_articles_data)} articles to {articles_filename}")
        
        if journals_data:
            journals_df = pd.DataFrame(journals_data)
            journals_filename = f'journals_{output_filename}.parquet'
            journals_df.to_parquet(journals_filename)
            logger.info(f"📚 Saved {len(journals_data)} journals to {journals_filename}")

   

    
    def save_intermediate_batch(self, articles_data, journal_slug):
        """Save intermediate results to prevent data loss"""
        if not articles_data:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"articles_batch_{journal_slug}_{timestamp}.parquet"
        
        df = pd.DataFrame(articles_data)
        df.to_parquet(filename)
        logger.info(f"💾 Saved batch: {len(articles_data)} articles to {filename}")

# --- STANDALONE FUNCTIONS FOR PICKLE-SAFE MULTIPROCESSING ---
# These exist outside the class to avoid Python's pickle anxiety disorder

async def scrape_single_article_standalone(session, article_url, journal_slug, semaphore):
    """
    Standalone async article scraper that doesn't trigger Python's pickle phobias
    
    This function exists in the global namespace because Python multiprocessing
    has commitment issues with class methods and weak references
    """
    async with semaphore:
        try:
            async with session.get(article_url) as response:
                if response.status == 200:
                    html_content = await response.text()
                    
                    # Process HTML using standalone extraction functions
                    article_data = extract_article_data_standalone(
                        html_content, article_url, journal_slug
                    )
                    
                    if article_data:
                        return article_data
                    
            return None
                    
        except Exception as e:
            logger.warning(f"💥 Failed {article_url}: {e}")
            return None

def extract_article_data_standalone(html_content, article_url, journal_slug):
    """
    Standalone article data extraction - pickle-safe and anxiety-free
    
    This is your existing scraping logic but as a standalone function
    that doesn't make Python multiprocessing cry about object references
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Title extraction
        title = 'N/A'
        title_css = soup.select_one('h3.article-title')
        if title_css:
            title = title_css.get_text(strip=True)
            title = re.sub(r'^\d+\.\s*', '', title).strip()
        
        # Authors extraction
        authors = extract_authors_standalone(soup)
        
        # Publication date
        publication_date = extract_publication_date_standalone(soup)
        
        # Keywords
        keywords = extract_keywords_standalone(soup)
            
        return {
            'journal_slug': journal_slug,
            'url': article_url,
            'title': title,
            'authors': authors,
            'publication_date': publication_date,
            'keywords': keywords,
            
            'last_scraped': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"💥 HTML parsing failed for {article_url}: {e}")
        return None

def extract_authors_standalone(soup):
    """Standalone author extraction function"""
    authors = 'N/A'
    
    # Dergipark-specific structure
    author_container = soup.select_one('p.card-text.article-authors.font-weight-normal, p.article-authors')
    if author_container:
        author_elements = author_container.select('a, span')
        author_names = [elem.get_text(strip=True) for elem in author_elements if elem.get_text(strip=True)]
        if author_names:
            authors = ", ".join(author_names)
    
    # Fallback strategies
    if authors == 'N/A':
        authors_elements = soup.select('p.article-author span, p.article-author a, .article-author-name, .author-name')
        if authors_elements:
            authors = ", ".join([a.get_text(strip=True) for a in authors_elements if a.get_text(strip=True)])
    
    return authors if authors and authors.strip() else 'N/A'

def extract_publication_date_standalone(soup):
    """Standalone publication date extraction"""
    date_meta = soup.find('meta', {'name': 'citation_publication_date'})
    if date_meta and 'content' in date_meta.attrs:
        return date_meta['content']
    
    date_element = soup.select_one('.article-detail-date, .publication-date, .date')
    if date_element:
        return date_element.get_text(strip=True)
    
    return 'N/A'

def extract_keywords_standalone(soup):
    """Standalone keywords extraction"""
    keywords_element = soup.select_one('.keywords, .article-keywords, [class*="keyword"]')
    if keywords_element:
        keywords_text = keywords_element.get_text(strip=True)
        return keywords_text.replace("Keywords:", "").strip()
    
    keywords_meta = soup.find('meta', {'name': 'keywords'})
    if keywords_meta and 'content' in keywords_meta.attrs:
        return keywords_meta['content']
    
    return 'N/A'

def extract_pages_standalone(soup):
    """Standalone page range extraction"""
    pages_element = soup.select_one('.pages, .page-range, [class*="page"]')
    if pages_element:
        return pages_element.get_text(strip=True)
    return 'N/A'

async def process_article_chunk_async_standalone(article_urls, journal_slug, max_concurrent, timeout):
    """
    Standalone async chunk processor that doesn't make Python cry about pickling
    
    This is the async processing function liberated from class method prison
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    session_config = {
        'timeout': aiohttp.ClientTimeout(total=timeout),
        'connector': aiohttp.TCPConnector(
            limit=100, limit_per_host=30, enable_cleanup_closed=True
        )
    }
    
    async with aiohttp.ClientSession(**session_config) as session:
        tasks = [
            scrape_single_article_standalone(session, url, journal_slug, semaphore)
            for url in article_urls
        ]
        
        logger.info(f"🚀 Process launching {len(tasks)} simultaneous attacks...")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful_results = [
            result for result in results 
            if result is not None and not isinstance(result, Exception)
        ]
        
        logger.info(f"✅ Process conquered {len(successful_results)}/{len(article_urls)} articles")
        return successful_results

def process_article_chunk_standalone(chunk_data):
    """
    The pickle-safe bridge between multiprocessing and async
    
    This function exists as a standalone entity because Python multiprocessing
    is basically a digital drama queen that refuses to work with complex objects
    """
    article_urls, journal_slug, max_concurrent, timeout = chunk_data
    
    logger.info(f"🔥 Process starting async loop for {len(article_urls)} articles...")
    
    try:
        return asyncio.run(
            process_article_chunk_async_standalone(article_urls, journal_slug, max_concurrent, timeout)
        )
    except Exception as e:
        logger.error(f"💥 Process failed: {e}")
        return []

    
class PerformanceBattleArena:
    """
    The computational Thunderdome where scraping approaches battle for supremacy
    """
    
    def __init__(self):
        self.sequential_fighter = SequentialScrapingMasochist()
        self.hybrid_destroyer = HybridDergiparkDestroyer(
            max_concurrent_per_process=10,  # Conservative for testing
            num_processes=min(4, cpu_count())
        )
    
    def conduct_performance_massacre(self, test_urls=None, test_count=20):
        """
        Performance battle royale - watching approaches fight to computational death
        """
        if test_urls is None:
            # Generate test URLs (replace with real Dergipark URLs for actual testing)
            test_urls = [f"https://httpbin.org/delay/{i%2}" for i in range(test_count)]
        
        print("\n" + "="*80)
        print("🏟️  COMPUTATIONAL THUNDERDOME: SCRAPING PERFORMANCE BATTLE")
        print("="*80)
        print(f"📊 Testing with {len(test_urls)} articles")
        print(f"⚔️  Sequential Masochism vs Hybrid Supremacy")
        
        journal_slug = "benchmark_test"
        
        # ROUND 1: Sequential Suffering
        print("\n🥊 ROUND 1: SEQUENTIAL APPROACH")
        print("💀 Witnessing computational masochism...")
        seq_results, seq_speed, seq_time = self.sequential_fighter.scrape_articles_sequentially(
            test_urls, journal_slug
        )
        
        # ROUND 2: Hybrid Annihilation
        print("\n🥊 ROUND 2: HYBRID PARALLEL PROCESSING")
        print("🚀 Unleashing the parallel processing beast...")
        
        hybrid_start = time.time()
        hybrid_results = asyncio.run(
            self.hybrid_destroyer.process_article_chunk_async(test_urls, journal_slug)
        )
        hybrid_time = time.time() - hybrid_start
        hybrid_speed = len(hybrid_results) / hybrid_time if hybrid_time > 0 else 0
        
        # THE BRUTAL PERFORMANCE COMPARISON
        print("\n" + "="*80)
        print("📊 COMPUTATIONAL CARNAGE REPORT")
        print("="*80)
        
        speedup_factor = hybrid_speed / seq_speed if seq_speed > 0 else float('inf')
        
        print(f"🐌 SEQUENTIAL APPROACH:")
        print(f"   Speed: {seq_speed:.2f} articles/second")
        print(f"   Time: {seq_time:.2f} seconds")
        print(f"   Dignity: OBLITERATED")
        
        print(f"\n🚀 HYBRID APPROACH:")
        print(f"   Speed: {hybrid_speed:.2f} articles/second")
        print(f"   Time: {hybrid_time:.2f} seconds")
        print(f"   Supremacy: ABSOLUTE")
        
        print(f"\n💥 MASSACRE SUMMARY:")
        print(f"   Speedup: {speedup_factor:.1f}x faster")
        print(f"   Winner: HYBRID (by technological knockout)")
        
        # Extrapolate to 700k articles
        articles_total = 700000
        seq_total_hours = articles_total / seq_speed / 3600 if seq_speed > 0 else float('inf')
        hybrid_total_hours = articles_total / hybrid_speed / 3600 if hybrid_speed > 0 else float('inf')
        
        print(f"\n📈 700K ARTICLE EXTRAPOLATION:")
        print(f"   Sequential: {seq_total_hours:.1f} hours ({seq_total_hours/24:.1f} days)")
        print(f"   Hybrid: {hybrid_total_hours:.1f} hours ({hybrid_total_hours/24:.1f} days)")
        print(f"   Life saved: {(seq_total_hours - hybrid_total_hours)/24:.1f} days")
        
        print("="*80)
        print("🎉 COMPUTATIONAL ENLIGHTENMENT ACHIEVED!")
        print("🚀 Parallel processing supremacy mathematically proven!")
        print("="*80)

def main():
    """The main event - where computational evolution happens"""
    print("🎯 DERGIPARK HYBRID SCRAPER INITIALIZATION")
    print("⚔️  Choose your computational destiny:")
    print("   1. 🚀 RUN HYBRID SCRAPER (The enlightened path)")
    print("   2. ⚡ PERFORMANCE BENCHMARK (Watch the massacre)")
    print("   3. 📊 FULL PRODUCTION RUN (700k articles)")
    
    choice = input("\nEnter your choice (1/2/3): ").strip()
    
    if choice == "1":
        print("\n🚀 LAUNCHING HYBRID ACADEMIC ANNIHILATION...")
        scraper = HybridDergiparkDestroyer()
        scraper.collect_all_dergipark_data_HYBRID()
        
    elif choice == "2":
        print("\n⚡ INITIATING PERFORMANCE THUNDERDOME...")
        arena = PerformanceBattleArena()
        arena.conduct_performance_massacre()
        
    elif choice == "3":
        print("\n📊 FULL PRODUCTION ANNIHILATION MODE...")
        print("🔥 This will systematically consume ALL Turkish academic publishing...")
        confirm = input("Are you absolutely sure? (yes/no): ")
        if confirm.lower() == 'yes':
            scraper = HybridDergiparkDestroyer()
            scraper.collect_all_dergipark_data_HYBRID()
        else:
            print("💀 Computational cowardice detected. Maybe start with option 2?")
    else:
        print("🤷 Invalid choice. Learn to follow simple instructions!")

if __name__ == "__main__":
    main()