import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import os
import json
from urllib.parse import urljoin, urlparse
import re
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompanyEnricher:
    def __init__(self, gemini_api_key: str = None, openai_api_key: str = None):  # FIXED: was _init
        """
        Initialize the Company Enricher with API keys
        
        Args:
            gemini_api_key: Google Gemini API key (free tier available)
            openai_api_key: OpenAI API key (optional)
        """
        self.gemini_api_key = gemini_api_key
        self.openai_api_key = openai_api_key
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def find_company_website(self, company_name: str) -> Optional[str]:
        """
        Find company website using Google search (simplified approach)
        """
        try:
            # Clean company name for search
            clean_name = re.sub(r'[^\w\s]', '', company_name)
            
            # Try common domain patterns first - FASTER approach
            domain_patterns = [
                f"{clean_name.lower().replace(' ', '')}.com",
                f"{clean_name.lower().replace(' ', '')}.co",
                f"{clean_name.lower().replace(' ', '')}.io",
                f"www.{clean_name.lower().replace(' ', '')}.com"
            ]
            
            # Quick check - don't wait too long
            for pattern in domain_patterns:
                test_url = f"https://{pattern}" if not pattern.startswith('www') else f"https://{pattern}"
                if self.is_website_accessible(test_url):
                    return test_url
            
            # Fallback: return best guess without validation for speed
            return f"https://www.{clean_name.lower().replace(' ', '')}.com"
                
        except Exception as e:
            logger.warning(f"Error finding website for {company_name}: {e}")
            return f"https://www.{company_name.lower().replace(' ', '')}.com"
    
    def is_website_accessible(self, url: str) -> bool:
        """Check if a website is accessible - FASTER with shorter timeout"""
        try:
            response = self.session.head(url, timeout=2)  # Reduced timeout
            return response.status_code == 200
        except:
            return False
    
    def scrape_website_content(self, url: str) -> str:
        """
        Scrape website content for analysis - OPTIMIZED for speed
        """
        try:
            response = self.session.get(url, timeout=5)  # Reduced timeout
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Limit text length for API efficiency - SMALLER for faster processing
            return text[:2000] if len(text) > 2000 else text
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return ""
    
    def analyze_with_gemini(self, company_name: str, website_content: str) -> Dict[str, str]:
        """
        Use Google Gemini API to analyze company and generate insights - OPTIMIZED for speed
        """
        if not self.gemini_api_key:
            return self.fallback_analysis(company_name, website_content)
        
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.gemini_api_key}"
            
            # SHORTER prompt for faster processing
            prompt = f"""
            Company: {company_name}
            Content: {website_content[:1500]}
            
            Provide JSON only:
            {{
                "summary": "Brief 1-sentence summary",
                "target_customer": "Main target market", 
                "industry": "Industry category",
                "company_size": "startup/small/medium/large",
                "automation_pitch": "Quick AI automation idea"
            }}
            """
            
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.3,  # Lower for faster, more consistent responses
                    "maxOutputTokens": 300  # Reduced for speed
                }
            }
            
            response = requests.post(url, json=payload, timeout=10)  # Reduced timeout
            response.raise_for_status()
            
            result = response.json()
            content = result['candidates'][0]['content']['parts'][0]['text']
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
                return analysis
            else:
                return self.fallback_analysis(company_name, website_content)
                
        except Exception as e:
            logger.error(f"Error with Gemini API: {e}")
            return self.fallback_analysis(company_name, website_content)
    
    def analyze_with_openai(self, company_name: str, website_content: str) -> Dict[str, str]:
        """
        Use OpenAI API to analyze company and generate insights - OPTIMIZED for speed
        """
        if not self.openai_api_key:
            return self.fallback_analysis(company_name, website_content)
        
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            # SHORTER prompt for faster processing
            prompt = f"""
            Company: {company_name}
            Content: {website_content[:1500]}
            
            JSON response only:
            {{
                "summary": "Brief summary",
                "target_customer": "Main target",
                "industry": "Industry",
                "company_size": "startup/small/medium/large", 
                "automation_pitch": "AI automation idea"
            }}
            """
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,  # Lower for speed
                "max_tokens": 300  # Reduced for speed
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
                return analysis
            else:
                return self.fallback_analysis(company_name, website_content)
                
        except Exception as e:
            logger.error(f"Error with OpenAI API: {e}")
            return self.fallback_analysis(company_name, website_content)
    
    def fallback_analysis(self, company_name: str, website_content: str) -> Dict[str, str]:
        """
        Fallback analysis when APIs are not available - FAST basic analysis
        """
        # Simple keyword-based analysis
        content_lower = website_content.lower()
        
        # Simplified industry detection
        if any(keyword in content_lower for keyword in ['software', 'tech', 'ai', 'saas', 'app']):
            industry = 'Technology'
        elif any(keyword in content_lower for keyword in ['financial', 'banking', 'fintech']):
            industry = 'Finance'
        elif any(keyword in content_lower for keyword in ['health', 'medical', 'healthcare']):
            industry = 'Healthcare'
        elif any(keyword in content_lower for keyword in ['retail', 'ecommerce', 'shopping']):
            industry = 'Retail'
        else:
            industry = 'Business Services'
        
        # Quick size estimation
        if len(website_content) > 2000:
            company_size = 'large'
        elif len(website_content) > 1000:
            company_size = 'medium'
        else:
            company_size = 'small'
        
        return {
            "summary": f"{company_name} is a {industry.lower()} company.",
            "target_customer": "Businesses and consumers",
            "industry": industry,
            "company_size": company_size,
            "automation_pitch": f"AI chatbot and process automation for {company_name}"
        }
    
    def enrich_company(self, company_name: str) -> Dict[str, str]:
        """
        Main method to enrich a single company - OPTIMIZED for speed
        """
        logger.info(f"Enriching data for: {company_name}")
        
        result = {
            'company_name': company_name,
            'website': '',
            'industry': '',
            'company_size': '',
            'summary_from_llm': '',
            'target_customer': '',
            'automation_pitch_from_llm': ''
        }
        
        try:
            # Step 1: Find website (quick)
            website = self.find_company_website(company_name)
            if website:
                result['website'] = website
                logger.info(f"Found website: {website}")
                
                # Step 2: Scrape website content (with timeout)
                content = self.scrape_website_content(website)
                if content:
                    logger.info(f"Scraped {len(content)} characters of content")
                    
                    # Step 3: Analyze with LLM (fastest available)
                    if self.gemini_api_key:
                        analysis = self.analyze_with_gemini(company_name, content)
                    elif self.openai_api_key:
                        analysis = self.analyze_with_openai(company_name, content)
                    else:
                        analysis = self.fallback_analysis(company_name, content)
                    
                    # Update result with analysis
                    result.update({
                        'industry': analysis.get('industry', 'Unknown'),
                        'company_size': analysis.get('company_size', 'Unknown'),
                        'summary_from_llm': analysis.get('summary', 'No summary available'),
                        'target_customer': analysis.get('target_customer', 'Unknown'),
                        'automation_pitch_from_llm': analysis.get('automation_pitch', 'Custom AI solution available')
                    })
                else:
                    # If no content scraped, use company name only
                    analysis = self.fallback_analysis(company_name, company_name)
                    result.update({
                        'industry': analysis.get('industry', 'Unknown'),
                        'company_size': analysis.get('company_size', 'Unknown'),
                        'summary_from_llm': analysis.get('summary', 'No summary available'),
                        'target_customer': analysis.get('target_customer', 'Unknown'),
                        'automation_pitch_from_llm': analysis.get('automation_pitch', 'Custom AI solution available')
                    })
            else:
                # If no website found, use basic analysis
                analysis = self.fallback_analysis(company_name, company_name)
                result.update({
                    'industry': analysis.get('industry', 'Unknown'),
                    'company_size': analysis.get('company_size', 'Unknown'), 
                    'summary_from_llm': analysis.get('summary', 'No summary available'),
                    'target_customer': analysis.get('target_customer', 'Unknown'),
                    'automation_pitch_from_llm': analysis.get('automation_pitch', 'Custom AI solution available')
                })
            
        except Exception as e:
            logger.error(f"Error processing {company_name}: {e}")
            # Return basic result on error
            result.update({
                'industry': 'Unknown',
                'company_size': 'Unknown',
                'summary_from_llm': f'Error processing {company_name}',
                'target_customer': 'Unknown',
                'automation_pitch_from_llm': 'Please contact us for custom solution'
            })
        
        # Reduced delay for faster processing
        time.sleep(0.5)  # Reduced from 2 seconds
        return result
    
    def process_csv(self, input_file: str, output_file: str = None) -> pd.DataFrame:
        """
        Process entire CSV file
        """
        if output_file is None:
            output_file = input_file.replace('.csv', '_enriched.csv')
        
        # Read input CSV
        try:
            df = pd.read_csv(input_file)
        except FileNotFoundError:
            logger.error(f"Input file {input_file} not found!")
            return None
        
        if 'company_name' not in df.columns:
            raise ValueError("CSV must contain 'company_name' column")
        
        # Process each company
        enriched_data = []
        total_companies = len(df)
        
        for idx, row in df.iterrows():
            company_name = row['company_name']
            logger.info(f"Processing {idx + 1}/{total_companies}: {company_name}")
            
            try:
                enriched_company = self.enrich_company(company_name)
                enriched_data.append(enriched_company)
            except Exception as e:
                logger.error(f"Error processing {company_name}: {e}")
                # Add a basic record even if processing fails
                enriched_data.append({
                    'company_name': company_name,
                    'website': 'Unknown',
                    'industry': 'Unknown',
                    'company_size': 'Unknown',
                    'summary_from_llm': 'Error processing company',
                    'target_customer': 'Unknown',
                    'automation_pitch_from_llm': 'Please contact us for custom solution'
                })
        
        # Create output DataFrame
        result_df = pd.DataFrame(enriched_data)
        
        # Save to CSV
        try:
            result_df.to_csv(output_file, index=False)
            logger.info(f"Results saved to: {output_file}")
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")
            # Save with a different name if there's an issue
            backup_file = f"enriched_companies_backup_{int(time.time())}.csv"
            result_df.to_csv(backup_file, index=False)
            logger.info(f"Results saved to backup file: {backup_file}")
        
        return result_df

def main():
    """
    Main function to run the enrichment process
    """
    # Configuration - FIXED the API key issue
    GEMINI_API_KEY = 'AIzaSyAcxl712jcHvAmhBOmyIModsOftgNoCE'  # Your API key directly
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # Optional
    
    if not GEMINI_API_KEY and not OPENAI_API_KEY:
        print("Warning: No API keys found. Using fallback analysis only.")
    
    # Initialize enricher
    enricher = CompanyEnricher(
        gemini_api_key=GEMINI_API_KEY,
        openai_api_key=OPENAI_API_KEY
    )
    
    # Process CSV
    input_file = 'companies.csv'  # Change this to your input file
    
    if not os.path.exists(input_file):
        # Create sample CSV if it doesn't exist
        sample_companies = pd.DataFrame({
            'company_name': ['Microsoft', 'Google', 'Amazon', 'Apple', 'Tesla', 'Netflix']
        })
        sample_companies.to_csv(input_file, index=False)
        print(f"Created sample file: {input_file}")
    
    try:
        enriched_df = enricher.process_csv(input_file)
        if enriched_df is not None:
            print(f"\nSuccessfully enriched {len(enriched_df)} companies!")
            print(f"Output file: {input_file.replace('.csv', '_enriched.csv')}")
            
            # Display sample results
            print("\nSample results:")
            print(enriched_df[['company_name', 'website', 'industry', 'company_size']].head())
            
            # Show full details for first company
            if len(enriched_df) > 0:
                print(f"\nDetailed results for {enriched_df.iloc[0]['company_name']}:")
                for col, val in enriched_df.iloc[0].items():
                    print(f"  {col}: {val}")
        else:
            print("Failed to process CSV file.")
        
    except Exception as e:
        logger.error(f"Error processing CSV: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":  # FIXED: was "_main"
    main()