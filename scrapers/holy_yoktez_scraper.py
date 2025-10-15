import asyncio
import time
import re
import csv
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from playwright.async_api import async_playwright, BrowserContext
from bs4 import BeautifulSoup


class YokTezUnifiedScraper:
    """
    The holy grail of YÖK Tez scrapers
    Handles everything: small unis, big unis, year filtering, PDF extraction
    """
    
    def __init__(self):
        self.base_url = "https://tez.yok.gov.tr/UlusalTezMerkezi"
        self.search_url = f"{self.base_url}/tarama.jsp"
        self.year_range = range(1980, 2026)
        
        # AGGRESSIVE MODE: Reduced waits for maximum speed
        self.short_wait = 0.5  # Down from 1-2 seconds
        self.medium_wait = 1   # Down from 2 seconds  
        self.long_wait = 2     # Down from 5 seconds
    
    async def scrape_all_universities(self, 
                                     count_csv_path: str,
                                     extract_pdf_urls: bool = False,
                                     pdf_batch_size: int = 50,  # AGGRESSIVE: Up from 20
                                     year_batch_size: int = 30,  # AGGRESSIVE: Up from 5
                                     uni_parallel: int = 10 ,  # NEW: Process multiple unis at once
                                     output_filename: str = None):
        """
        The one scraper to rule them all
        
        Args:
            count_csv_path: CSV with university counts (university, thesis_count, capped columns)
            extract_pdf_urls: Extract PDF URLs (slower but gives you download links)
            pdf_batch_size: PDF extraction concurrency (higher = faster, 20-50 recommended)
            year_batch_size: Year query concurrency for capped unis (5-10 recommended)
            output_filename: Output CSV path
        """
        start_time = time.time()
        
        print(f"YÖK TEZ UNIFIED SCRAPER - THE FINAL FORM")
        print("="*70)
        print(f"PDF extraction: {'ENABLED' if extract_pdf_urls else 'DISABLED'}")
        if extract_pdf_urls:
            print(f"PDF concurrency: {pdf_batch_size}")
        print("="*70)
        
        # Load university data
        try:
            df = pd.read_csv(count_csv_path)
            print(f"\nLoaded {len(df)} universities from CSV")
            
            small_unis = df[df['capped'] == 'NO'].copy()
            large_unis = df[df['capped'] == 'YES'].copy()
            
            print(f"  Small (<2K): {len(small_unis)} universities")
            print(f"  Large (>2K): {len(large_unis)} universities (will use year filtering)")
            
        except Exception as e:
            print(f"Failed to load CSV: {e}")
            return
        
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"yoktez_complete_{timestamp}.csv"
            print(f"Output filename: {output_filename}")
        
        all_theses = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
            )
            
            try:
                # Phase 1: Large universities (year filtering)
                if len(large_unis) > 0:
                    print(f"\n{'='*70}")
                    print(f"PHASE 2: LARGE UNIVERSITIES ({len(large_unis)} total)")
                    print(f"Using year filtering with batch size {year_batch_size}")
                    print(f"{'='*70}")
                    
                    for idx, uni_row in large_unis.iterrows():
                        uni_name = uni_row['university']
                        uni_index = idx
                        expected_count = uni_row['thesis_count']
                        
                        print(f"\n[{idx}] {uni_name} (expected: {expected_count:,})")
                        
                        theses = await self._scrape_university_by_year(
                            browser, uni_index, uni_name, year_batch_size, 
                            extract_pdf_urls, pdf_batch_size
                        )
                        
                        if theses:
                            for t in theses:
                                t['university'] = uni_name
                            all_theses.extend(theses)
                            print(f"  ✓ {len(theses)} theses extracted")
                        
                        # Save incrementally
                        if all_theses:
                            self._save_csv(all_theses, output_filename, extract_pdf_urls)

                # Phase 2: Small universities (straightforward scraping)
                if len(small_unis) > 0:
                    print(f"\n{'='*70}")
                    print(f"PHASE 1: SMALL UNIVERSITIES ({len(small_unis)} total)")
                    print(f"{'='*70}")
                    
                    for idx, uni_row in small_unis.iterrows():
                        uni_name = uni_row['university']
                        uni_index = idx
                        
                        print(f"\n[{idx}] {uni_name}")
                        
                        context = await browser.new_context(
                            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                            viewport={'width': 1920, 'height': 1080}
                        )
                        
                        theses = await self._scrape_university_simple(
                            context, uni_index, uni_name, extract_pdf_urls, pdf_batch_size
                        )
                        
                        await context.close()
                        
                        if theses:
                            for t in theses:
                                t['university'] = uni_name
                            all_theses.extend(theses)
                            print(f"  ✓ {len(theses)} theses")
                        
                        # Save incrementally
                        if all_theses:
                            self._save_csv(all_theses, output_filename, extract_pdf_urls)
                
                
                
                # Final summary
                end_time = time.time()
                total_time = end_time - start_time
                minutes = int(total_time // 60)
                seconds = total_time % 60
                
                print(f"\n{'='*70}")
                print(f"COMPLETE YOKTEZ SCRAPE FINISHED")
                print(f"{'='*70}")
                
                print(f"\nResults:")
                print(f"  Total universities: {len(df)}")
                print(f"  Total theses: {len(all_theses):,}")
                
                print(f"\nTiming:")
                print(f"  Total: {minutes}m {seconds:.2f}s")
                print(f"  Theses/second: {len(all_theses)/total_time:.2f}")
                
                print(f"\nOutput: {output_filename}")
                
                return all_theses
                
            finally:
                await browser.close()
    
    async def _scrape_university_simple(self, context: BrowserContext, uni_index: int,
                                       uni_name: str, extract_pdfs: bool, 
                                       pdf_batch: int) -> List[Dict]:
        """Simple scrape for universities with <2000 theses"""
        page = await context.new_page()
        
        try:
            await page.goto(self.search_url, timeout=30000)  # AGGRESSIVE: No networkidle wait
            await asyncio.sleep(self.medium_wait)
            
            # Open popup
            uni_field = page.locator('input[name="uniad"][size="45"][onclick="uniEkle();"]')
            async with context.expect_page() as popup_info:
                await uni_field.click()
            
            popup = await popup_info.value
            await popup.wait_for_load_state('domcontentloaded', timeout=15000)  # AGGRESSIVE: domcontentloaded instead of networkidle
            await popup.wait_for_selector('table.filterable tbody', timeout=15000)
            await asyncio.sleep(self.medium_wait)
            
            # Select university
            links = await popup.locator('a[href*="eklecikar"]').all()
            if uni_index >= len(links):
                return []
            
            await links[uni_index].click()
            await asyncio.sleep(self.medium_wait)
            
            # Submit
            await page.locator('input[type="submit"]').first.click()
            await asyncio.sleep(self.long_wait)
            
            try:
                await page.wait_for_load_state('domcontentloaded', timeout=20000)  # AGGRESSIVE
            except:
                pass
            
            # Extract
            content = await page.content()
            theses = self._extract_theses_from_page(content)
            
            # PDF extraction if requested
            if extract_pdfs and theses:
                theses = await self._extract_pdf_urls_concurrent(context, theses, pdf_batch)
            
            return theses
            
        finally:
            await page.close()
    
    async def _scrape_university_by_year(self, browser, uni_index: int, uni_name: str,
                                        year_batch: int, extract_pdfs: bool,
                                        pdf_batch: int) -> List[Dict]:
        """Year-filtered scrape for universities with >2000 theses"""
        all_theses = []
        years = list(self.year_range)
        
        for batch_start in range(0, len(years), year_batch):
            batch_years = years[batch_start:batch_start + year_batch]
            
            contexts = []
            for _ in batch_years:
                ctx = await browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    viewport={'width': 1920, 'height': 1080}
                )
                contexts.append(ctx)
            
            try:
                tasks = [
                    self._scrape_single_year(contexts[i], uni_index, batch_years[i])
                    for i in range(len(batch_years))
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for year, result in zip(batch_years, results):
                    if isinstance(result, Exception):
                        continue
                    if result:
                        all_theses.extend(result)
                        if len(result) > 0:
                            print(f"    {year}: {len(result)} theses")
                
            finally:
                for ctx in contexts:
                    await ctx.close()
            
            await asyncio.sleep(1)
        
        # PDF extraction after collecting all years
        if extract_pdfs and all_theses:
            print(f"  Extracting PDF URLs...")
            # Use first context for PDF extraction
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            all_theses = await self._extract_pdf_urls_concurrent(context, all_theses, pdf_batch)
            await context.close()
        
        return all_theses
    
    async def _scrape_single_year(self, context: BrowserContext, uni_index: int,
                                  year: int) -> List[Dict]:
        """Scrape one year for one university - AGGRESSIVE MODE"""
        page = await context.new_page()
        
        try:
            await page.goto(self.search_url, timeout=30000)  # No networkidle
            await asyncio.sleep(self.medium_wait)
            
            # Popup
            uni_field = page.locator('input[name="uniad"][size="45"][onclick="uniEkle();"]')
            async with context.expect_page() as popup_info:
                await uni_field.click()
            
            popup = await popup_info.value
            await popup.wait_for_load_state('domcontentloaded', timeout=15000)  # Faster load state
            await popup.wait_for_selector('table.filterable tbody', timeout=15000)
            await asyncio.sleep(self.short_wait)  # Minimal wait
            
            links = await popup.locator('a[href*="eklecikar"]').all()
            if uni_index >= len(links):
                return []
            
            await links[uni_index].click()
            await asyncio.sleep(self.short_wait)  # Minimal wait
            
            # Select year
            await page.locator('select[name="yil1"]').first.select_option(value=str(year))
            await asyncio.sleep(self.short_wait)  # Minimal wait
            
            # Submit
            await page.locator('input[type="submit"]').first.click()
            await asyncio.sleep(self.long_wait)
            
            try:
                await page.wait_for_load_state('domcontentloaded', timeout=20000)
            except:
                pass
            
            content = await page.content()
            return self._extract_theses_from_page(content)
            
        except Exception as e:
            return []
        finally:
            await page.close()
    
    async def _extract_pdf_urls_concurrent(self, context: BrowserContext,
                                          theses: List[Dict], batch_size: int) -> List[Dict]:
        """Fast concurrent PDF URL extraction - AGGRESSIVE MODE"""
        
        async def extract_single(thesis: Dict) -> Dict:
            if 'detail_url' not in thesis or not thesis['detail_url']:
                thesis['pdf_url'] = ''
                return thesis
            
            page = await context.new_page()
            try:
                await page.goto(thesis['detail_url'], timeout=30000)  # No networkidle
                await asyncio.sleep(self.short_wait)  # Minimal wait
                
                content = await page.content()
                pdf_match = re.search(r'<a\s+href="TezGoster\?key=([^"]+)"', content)
                
                if pdf_match:
                    thesis['pdf_url'] = f"{self.base_url}/TezGoster?key={pdf_match.group(1)}"
                else:
                    thesis['pdf_url'] = ''
                
                return thesis
            except:
                thesis['pdf_url'] = ''
                return thesis
            finally:
                await page.close()
        
        results = []
        for i in range(0, len(theses), batch_size):
            batch = theses[i:i + batch_size]
            batch_results = await asyncio.gather(*[extract_single(t) for t in batch])
            results.extend(batch_results)
            if i + batch_size < len(theses):
                await asyncio.sleep(self.short_wait)  # Minimal pause
        
        return results
    
    def _extract_theses_from_page(self, html: str) -> List[Dict]:
        """Extract thesis metadata from page"""
        soup = BeautifulSoup(html, 'html.parser')
        scripts = soup.find_all('script')
        
        theses = []
        pattern = re.compile(r'var doc\s*=\s*(\{.*?\})\s*;\s*rows\.push\(doc\);', re.DOTALL)
        
        for script in scripts:
            if script.string and 'var doc' in script.string:
                matches = pattern.findall(script.string)
                for match in matches:
                    thesis = self._extract_thesis_info(f"var doc = {match};")
                    if thesis:
                        theses.append(thesis)
        
        return theses
    
    def _extract_thesis_info(self, var_doc: str) -> Optional[Dict]:
        """Extract thesis metadata from var doc string"""
        # Title
        title_match = re.search(r'weight:\s*"(.*?)"', var_doc, re.DOTALL)
        if not title_match:
            return None
        
        title_raw = title_match.group(1)
        if '<br>' in title_raw and 'font-style: italic' in title_raw:
            tr_match = re.search(r'^([^<]+)(?=<br>)', title_raw)
            title = tr_match.group(1).strip() if tr_match else ""
        else:
            soup = BeautifulSoup(title_raw, 'html.parser')
            title = soup.get_text(separator=' ').strip()
        
        # ID and detail URL
        onclick = re.search(r"onclick=tezDetay\('([^']+)','([^']+)'\)>(\d+)", var_doc)
        if onclick:
            article_id = onclick.group(3)
            detail_url = f"{self.base_url}/tezDetay.jsp?id={onclick.group(1)}&no={onclick.group(2)}"
        else:
            id_match = re.search(r"userId:\s*\"<span[^>]*?>(\d+)<\/span>\",", var_doc)
            article_id = id_match.group(1) if id_match else None
            detail_url = ''
        
        if not article_id:
            return None
        
        # Author
        author_match = re.search(r'name:\s*"(.*?)"\s*,', var_doc)
        author = ''
        if author_match:
            author = re.sub(r'<[^>]+>', '', author_match.group(1)).strip()
            author = ' '.join(author.replace('\\n', ' ').replace('\\t', ' ').split())
        
        # Date
        date_match = re.search(r'age:\s*"(.*?)"\s*,', var_doc)
        date = ''
        if date_match:
            date = re.sub(r'<[^>]+>', '', date_match.group(1)).strip()
            date = ' '.join(date.replace('\\n', ' ').replace('\\t', ' ').split())
        
        return {
            'title': title,
            'article_id': article_id,
            'author': author,
            'publication_date': date,
            'detail_url': detail_url
        }
    
    def _save_csv(self, theses: List[Dict], filename: str, has_pdfs: bool):
        """Save to CSV"""
        if not theses:
            return
        
        headers = ['article_id', 'title', 'author', 'publication_date', 'university', 'detail_url']
        if has_pdfs:
            headers.append('pdf_url')
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                
                for t in theses:
                    row = {k: t.get(k, '') for k in headers}
                    writer.writerow(row)
        except Exception as e:
            print(f"CSV save failed: {e}")


async def main():
    scraper = YokTezUnifiedScraper()
    
    await scraper.scrape_all_universities(
        count_csv_path='yoktez_university_counts_20251001_195443.csv',
        extract_pdf_urls=True,  # Set True if you want PDF URLs (slower)
        pdf_batch_size=50,
        year_batch_size=30
    )


if __name__ == "__main__":
    asyncio.run(main())
