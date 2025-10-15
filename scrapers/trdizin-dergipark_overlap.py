import pandas as pd
import numpy as np
from typing import Set, List, Tuple
import re
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import matplotlib.pyplot as plt
import seaborn as sns

class JournalOverlapAnalyzer:
    """
    A digital weapon for dissecting journal overlap between datasets.
    Because academic data is messy as fuck and needs professional intervention.
    """
    
    def __init__(self):
        self.csv_journals = set()
        self.parquet_journals = set()
        self.csv_raw = []
        self.parquet_raw = []
        
    def load_csv_journals(self, csv_path: str, column_name: str = 'Journal Title') -> Set[str]:
        """
        Load journal names from your TR-Dizin CSV like a digital vampire.
        """
        try:
            print(f"🔍 Loading CSV journals from: {csv_path}")
            df = pd.read_csv(csv_path, encoding='utf-8')
            
            print(f"📊 CSV structure: {df.shape[0]} rows, {df.shape[1]} columns")
            print(f"🔑 Available columns: {list(df.columns)}")
            
            if column_name not in df.columns:
                print(f"💥 Column '{column_name}' not found! Available: {list(df.columns)}")
                # Try to find the right column automatically
                for col in df.columns:
                    if 'title' in col.lower() or 'journal' in col.lower() or 'name' in col.lower():
                        print(f"🎯 Auto-detected column: {col}")
                        column_name = col
                        break
            
            # Extract journal names and clean them
            journals = df[column_name].dropna().unique()
            self.csv_raw = list(journals)
            self.csv_journals = set(self.clean_journal_names(journals))
            
            print(f"✅ Loaded {len(self.csv_journals)} unique journals from CSV")
            print(f"📋 Sample journals:")
            for i, journal in enumerate(list(self.csv_journals)[:5], 1):
                print(f"  {i}. {journal}")
            
            return self.csv_journals
            
        except Exception as e:
            print(f"💀 CSV loading failed: {e}")
            return set()
    
    def load_parquet_journals(self, parquet_path: str, column_name: str = None) -> Set[str]:
        """
        Load journal names from parquet file like a data ninja.
        Auto-detects the journal column if you don't specify it.
        """
        try:
            print(f"🔍 Loading Parquet journals from: {parquet_path}")
            df = pd.read_parquet(parquet_path)
            
            print(f"📊 Parquet structure: {df.shape[0]} rows, {df.shape[1]} columns")
            print(f"🔑 Available columns: {list(df.columns)}")
            
            # Auto-detect journal column if not specified
            if column_name is None:
                potential_cols = []
                for col in df.columns:
                    col_lower = col.lower()
                    if any(keyword in col_lower for keyword in ['title', 'journal', 'name', 'publication']):
                        potential_cols.append(col)
                
                if potential_cols:
                    column_name = potential_cols[0]
                    print(f"🎯 Auto-detected journal column: {column_name}")
                else:
                    print("💥 Could not auto-detect journal column. Please specify manually.")
                    print(f"Available columns: {list(df.columns)}")
                    return set()
            
            # Extract and clean journal names
            journals = df[column_name].dropna().unique()
            self.parquet_raw = list(journals)
            self.parquet_journals = set(self.clean_journal_names(journals))
            
            print(f"✅ Loaded {len(self.parquet_journals)} unique journals from Parquet")
            print(f"📋 Sample journals:")
            for i, journal in enumerate(list(self.parquet_journals)[:5], 1):
                print(f"  {i}. {journal}")
            
            return self.parquet_journals
            
        except Exception as e:
            print(f"💀 Parquet loading failed: {e}")
            return set()
    
    def clean_journal_names(self, journals: List[str]) -> List[str]:
        """
        Clean journal names because academic data is messy as hell.
        Normalize the chaos into something comparable.
        """
        cleaned = []
        
        for journal in journals:
            if pd.isna(journal) or not isinstance(journal, str):
                continue
            
            # Basic cleaning operations
            clean_name = journal.strip()
            
            # Remove common prefixes/suffixes that cause mismatches
            # (adjust based on your data patterns)
            clean_name = re.sub(r'^(The\s+)', '', clean_name, flags=re.IGNORECASE)
            clean_name = re.sub(r'\s+', ' ', clean_name)  # Normalize whitespace
            
            # Convert to title case for consistency
            clean_name = clean_name.title()
            
            if clean_name:  # Only add non-empty strings
                cleaned.append(clean_name)
        
        return cleaned
    
    def calculate_exact_overlap(self) -> Tuple[Set[str], float, dict]:
        """
        Calculate exact string matches between datasets.
        Because sometimes life is simple and journals have identical names.
        """
        if not self.csv_journals or not self.parquet_journals:
            print("💀 No data loaded. Load both datasets first, you magnificent bastard!")
            return set(), 0.0, {}
        
        # Find exact matches
        exact_matches = self.csv_journals.intersection(self.parquet_journals)
        
        # Calculate percentages
        csv_total = len(self.csv_journals)
        parquet_total = len(self.parquet_journals)
        matches_count = len(exact_matches)
        
        csv_overlap_pct = (matches_count / csv_total) * 100 if csv_total > 0 else 0
        parquet_overlap_pct = (matches_count / parquet_total) * 100 if parquet_total > 0 else 0
        
        stats = {
            'csv_total': csv_total,
            'parquet_total': parquet_total,
            'exact_matches': matches_count,
            'csv_overlap_percentage': csv_overlap_pct,
            'parquet_overlap_percentage': parquet_overlap_pct,
            'union_size': len(self.csv_journals.union(self.parquet_journals)),
            'jaccard_similarity': matches_count / len(self.csv_journals.union(self.parquet_journals))
        }
        
        return exact_matches, csv_overlap_pct, stats
    
    def calculate_fuzzy_overlap(self, threshold: int = 85) -> Tuple[List[Tuple], float, dict]:
        """
        Find similar journal names using fuzzy matching.
        Because journal names are inconsistent academic nightmares.
        """
        print(f"🔍 Running fuzzy matching with threshold: {threshold}%")
        
        fuzzy_matches = []
        csv_matched = set()
        
        # For each CSV journal, find best match in parquet
        for csv_journal in self.csv_journals:
            best_match = process.extractOne(
                csv_journal, 
                list(self.parquet_journals),
                scorer=fuzz.ratio
            )
            
            if best_match and best_match[1] >= threshold:
                fuzzy_matches.append((csv_journal, best_match[0], best_match[1]))
                csv_matched.add(csv_journal)
        
        # Calculate stats
        matches_count = len(fuzzy_matches)
        csv_total = len(self.csv_journals)
        fuzzy_overlap_pct = (matches_count / csv_total) * 100 if csv_total > 0 else 0
        
        stats = {
            'csv_total': csv_total,
            'parquet_total': len(self.parquet_journals),
            'fuzzy_matches': matches_count,
            'fuzzy_overlap_percentage': fuzzy_overlap_pct,
            'threshold_used': threshold,
            'unmatched_csv': csv_total - matches_count
        }
        
        return fuzzy_matches, fuzzy_overlap_pct, stats
    
    def generate_overlap_report(self, save_path: str = None) -> str:
        """
        Generate a comprehensive overlap analysis report.
        Because data without insights is just digital hoarding.
        """
        if not self.csv_journals or not self.parquet_journals:
            return "💀 No data loaded. Run load_csv_journals() and load_parquet_journals() first!"
        
        # Calculate exact and fuzzy overlaps
        exact_matches, exact_pct, exact_stats = self.calculate_exact_overlap()
        fuzzy_matches, fuzzy_pct, fuzzy_stats = self.calculate_fuzzy_overlap()
        
        report = f"""
🎯 JOURNAL OVERLAP ANALYSIS REPORT
{'='*50}

📊 DATASET OVERVIEW:
   CSV Journals (TR-Dizin): {exact_stats['csv_total']:,}
   Parquet Journals: {exact_stats['parquet_total']:,}
   Total Unique Journals: {exact_stats['union_size']:,}

🔍 EXACT MATCH ANALYSIS:
   Identical Journals: {exact_stats['exact_matches']:,}
   CSV Overlap: {exact_stats['csv_overlap_percentage']:.2f}%
   Parquet Overlap: {exact_stats['parquet_overlap_percentage']:.2f}%
   Jaccard Similarity: {exact_stats['jaccard_similarity']:.4f}

🎭 FUZZY MATCH ANALYSIS (≥85% similarity):
   Similar Journals: {fuzzy_stats['fuzzy_matches']:,}
   CSV Fuzzy Overlap: {fuzzy_stats['fuzzy_overlap_percentage']:.2f}%
   Unmatched CSV Journals: {fuzzy_stats['unmatched_csv']:,}

🏆 KEY INSIGHTS:
   • Exact overlap indicates {exact_pct:.1f}% of your CSV journals exist in the parquet file
   • Including fuzzy matches raises this to {fuzzy_pct:.1f}%
   • {exact_stats['union_size'] - exact_stats['exact_matches']:,} unique journals across both datasets
   • Data quality: {'High' if exact_pct > 80 else 'Medium' if exact_pct > 50 else 'Low'} exact match rate

📋 SAMPLE EXACT MATCHES:
"""
        
        # Add sample exact matches
        for i, match in enumerate(list(exact_matches)[:10], 1):
            report += f"   {i:2d}. {match}\n"
        
        if len(exact_matches) > 10:
            report += f"   ... and {len(exact_matches) - 10} more\n"
        
        report += "\n📋 SAMPLE FUZZY MATCHES:\n"
        
        # Add sample fuzzy matches
        for i, (csv_name, parquet_name, score) in enumerate(fuzzy_matches[:10], 1):
            report += f"   {i:2d}. {csv_name} ≈ {parquet_name} ({score}%)\n"
        
        if len(fuzzy_matches) > 10:
            report += f"   ... and {len(fuzzy_matches) - 10} more\n"
        
        report += f"\n{'='*50}\n"
        
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"💾 Report saved to: {save_path}")
        
        return report
    
    def visualize_overlap(self, save_path: str = None):
        """
        Create visualizations because humans are visual creatures.
        """
        try:
            exact_matches, exact_pct, exact_stats = self.calculate_exact_overlap()
            
            # Create a figure with subplots
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Journal Overlap Analysis', fontsize=16, fontweight='bold')
            
            # 1. Venn-style bar chart
            categories = ['CSV Only', 'Both', 'Parquet Only']
            csv_only = exact_stats['csv_total'] - exact_stats['exact_matches']
            both = exact_stats['exact_matches']
            parquet_only = exact_stats['parquet_total'] - exact_stats['exact_matches']
            values = [csv_only, both, parquet_only]
            
            axes[0,0].bar(categories, values, color=['#ff7f0e', '#2ca02c', '#1f77b4'])
            axes[0,0].set_title('Journal Distribution')
            axes[0,0].set_ylabel('Number of Journals')
            
            # Add value labels on bars
            for i, v in enumerate(values):
                axes[0,0].text(i, v + max(values) * 0.01, str(v), ha='center', va='bottom')
            
            # 2. Overlap percentage pie chart
            overlap_data = [exact_stats['csv_overlap_percentage'], 100 - exact_stats['csv_overlap_percentage']]
            axes[0,1].pie(overlap_data, labels=['Overlap', 'Unique to CSV'], autopct='%1.1f%%', 
                         colors=['#2ca02c', '#ff7f0e'])
            axes[0,1].set_title('CSV Journal Overlap %')
            
            # 3. Dataset size comparison
            datasets = ['CSV\n(TR-Dizin)', 'Parquet']
            sizes = [exact_stats['csv_total'], exact_stats['parquet_total']]
            axes[1,0].bar(datasets, sizes, color=['#1f77b4', '#ff7f0e'])
            axes[1,0].set_title('Dataset Sizes')
            axes[1,0].set_ylabel('Number of Journals')
            
            # Add value labels
            for i, v in enumerate(sizes):
                axes[1,0].text(i, v + max(sizes) * 0.01, str(v), ha='center', va='bottom')
            
            # 4. Similarity metrics
            metrics = ['Exact\nMatches', 'Union\nSize', 'Jaccard\nSimilarity']
            metric_values = [
                exact_stats['exact_matches'],
                exact_stats['union_size'],
                exact_stats['jaccard_similarity'] * 1000  # Scale for visibility
            ]
            
            bars = axes[1,1].bar(metrics, metric_values, color=['#2ca02c', '#d62728', '#9467bd'])
            axes[1,1].set_title('Overlap Metrics')
            axes[1,1].set_ylabel('Count / Scaled Value')
            
            # Add value labels (special handling for Jaccard)
            for i, (bar, value) in enumerate(zip(bars, metric_values)):
                if i == 2:  # Jaccard similarity
                    label = f"{exact_stats['jaccard_similarity']:.3f}"
                else:
                    label = str(int(value))
                axes[1,1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(metric_values) * 0.01,
                              label, ha='center', va='bottom')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                print(f"📊 Visualization saved to: {save_path}")
            
            plt.show()
            
        except ImportError:
            print("📊 Visualization requires matplotlib and seaborn. Install with: pip install matplotlib seaborn")
        except Exception as e:
            print(f"💥 Visualization failed: {e}")


def main():
    """
    The main event - let's analyze some fucking journal overlap!
    """
    print("🚀 Journal Overlap Analysis: Academic Data Detective Work")
    print("="*60)
    
    analyzer = JournalOverlapAnalyzer()
    
    # Load your datasets (adjust paths as needed)
    csv_path = "trdizin_journals.csv"  # Your TR-Dizin scraping results
    parquet_path = "articles_dergipark_UNIFIED.parquet"  # Your other journal dataset
    
    print("📥 Loading datasets...")
    
    # Load CSV journals
    csv_journals = analyzer.load_csv_journals(csv_path)
    if not csv_journals:
        print("💀 Failed to load CSV. Check the file path and column names.")
        return
    
    # Load parquet journals  
    parquet_journals = analyzer.load_parquet_journals(parquet_path)
    if not parquet_journals:
        print("💀 Failed to load Parquet. Check the file path and column names.")
        return
    
    print("\n" + "="*60)
    print("🔥 RUNNING OVERLAP ANALYSIS...")
    
    # Generate comprehensive report
    report = analyzer.generate_overlap_report("journal_overlap_report.txt")
    print(report)
    
    # Create visualizations
    print("📊 Generating visualizations...")
    analyzer.visualize_overlap("journal_overlap_analysis.png")
    
    print("\n🎉 ANALYSIS COMPLETE!")
    print("📁 Files generated:")
    print("   • journal_overlap_report.txt")
    print("   • journal_overlap_analysis.png")


if __name__ == "__main__":
    main()