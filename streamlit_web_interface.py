import streamlit as st
import pandas as pd
import io
import os
from datetime import datetime
import time
import sys
import traceback

st.set_page_config(
    page_title="AI Lead Enrichment Bot",
    page_icon="🤖",
    layout="wide"
)

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

CompanyEnricher = None
import_error = None

try:
    from lead_enrichment_bot import CompanyEnricher
    st.success("CompanyEnricher imported successfully")
except ImportError as e:
    import_error = f"Import Error: {e}"
    st.error(import_error)
    st.error("Please ensure 'lead_enrichment_bot.py' is in the same directory.")
    st.error(f"Current directory: {current_dir}")

class FallbackCompanyEnricher:
    def __init__(self, gemini_api_key=None, openai_api_key=None):
        self.gemini_api_key = gemini_api_key
        self.openai_api_key = openai_api_key
        st.warning("Using fallback enricher - limited functionality available")
    
    def enrich_company(self, company_name):
        time.sleep(0.5)
        
        name_lower = company_name.lower()
        if any(word in name_lower for word in ['tech', 'software', 'ai', 'digital']):
            industry = 'Technology'
        elif any(word in name_lower for word in ['bank', 'financial', 'capital']):
            industry = 'Finance'
        elif any(word in name_lower for word in ['health', 'medical', 'pharma']):
            industry = 'Healthcare'
        else:
            industry = 'Business Services'
        
        return {
            'company_name': company_name,
            'website': f'https://www.{company_name.lower().replace(" ", "").replace(".", "")}.com',
            'industry': industry,
            'company_size': 'Medium',
            'summary_from_llm': f'{company_name} is a {industry.lower()} company that provides services to businesses and consumers.',
            'target_customer': 'Small to medium businesses',
            'automation_pitch_from_llm': f'QF Innovate can help {company_name} implement AI chatbots, automated customer service, and process optimization to increase efficiency by 30-50%.'
        }

def create_enricher_instance(gemini_key, openai_key):
    if CompanyEnricher is None:
        st.warning("Using fallback enricher due to import issues")
        return FallbackCompanyEnricher(gemini_key, openai_key)
    
    try:
        enricher = CompanyEnricher(
            gemini_api_key=gemini_key if gemini_key else None,
            openai_api_key=openai_key if openai_key else None
        )
        st.success("CompanyEnricher initialized successfully")
        return enricher
        
    except Exception as e:
        st.error(f"Failed to initialize CompanyEnricher: {e}")
        st.warning("Using fallback enricher")
        return FallbackCompanyEnricher(gemini_key, openai_key)

def add_sidebar_info():
    st.sidebar.markdown("---")
    st.sidebar.subheader("How to Use")
    st.sidebar.markdown("""
    1. Get API Key from [Google AI Studio](https://makersuite.google.com/)
    2. Upload CSV with 'company_name' column
    3. Configure batch size and delays
    4. Click 'Start Enrichment'
    5. Download enriched data
    """)
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Features")
    st.sidebar.markdown("""
    - Website discovery
    - Industry classification
    - AI-powered summaries
    - Custom automation pitches
    - Real-time progress tracking
    - CSV export
    """)

def process_companies(df, enricher, batch_size, show_progress, delay):
    companies_to_process = df.head(batch_size)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    results_container = st.container()
    
    enriched_results = []
    total_companies = len(companies_to_process)
    
    for idx, row in companies_to_process.iterrows():
        company_name = row['company_name']
        
        progress = (idx + 1) / total_companies
        progress_bar.progress(progress)
        status_text.text(f"Processing {idx + 1}/{total_companies}: {company_name}")
        
        try:
            result = enricher.enrich_company(company_name)
            enriched_results.append(result)
            
            if show_progress:
                with results_container:
                    st.subheader(f"{company_name}")
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.write(f"**Website:** {result.get('website', 'Not found')}")
                        st.write(f"**Industry:** {result.get('industry', 'Unknown')}")
                        st.write(f"**Size:** {result.get('company_size', 'Unknown')}")
                    
                    with col2:
                        summary = result.get('summary_from_llm', 'No summary available')
                        if len(summary) > 150:
                            summary = summary[:150] + "..."
                        st.write(f"**Summary:** {summary}")
                    
                    pitch = result.get('automation_pitch_from_llm', 'No pitch available')
                    if len(pitch) > 200:
                        pitch = pitch[:200] + "..."
                    st.write(f"**Automation Pitch:** {pitch}")
                    st.divider()
            
            if delay > 0:
                time.sleep(delay)
            
        except Exception as e:
            error_msg = str(e)
            st.error(f"Error processing {company_name}: {error_msg}")
            
            enriched_results.append({
                'company_name': company_name,
                'website': 'Error',
                'industry': 'Unknown',
                'company_size': 'Unknown',
                'summary_from_llm': f'Error: {error_msg}',
                'target_customer': 'Unknown',
                'automation_pitch_from_llm': 'Contact us for custom solution'
            })
    
    progress_bar.progress(1.0)
    status_text.text("Processing complete")
    
    results_df = pd.DataFrame(enriched_results)
    
    st.header("Results")
    st.dataframe(results_df, use_container_width=True)
    
    st.header("Download Results")
    
    csv_buffer = io.StringIO()
    results_df.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"enriched_companies_{timestamp}.csv"
    
    st.download_button(
        label="Download Enriched Data (CSV)",
        data=csv_data,
        file_name=filename,
        mime="text/csv"
    )
    
    st.subheader("Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Companies Processed", len(results_df))
    
    with col2:
        websites_found = sum(1 for _, row in results_df.iterrows() 
                           if row.get('website') and row.get('website') != '' and row.get('website') != 'Error')
        st.metric("Websites Found", websites_found)
    
    with col3:
        industries_identified = sum(1 for _, row in results_df.iterrows() 
                                  if row.get('industry') and row.get('industry') != 'Unknown')
        st.metric("Industries Identified", industries_identified)
    
    with col4:
        pitches_generated = sum(1 for _, row in results_df.iterrows() 
                              if row.get('automation_pitch_from_llm') and 
                              'Error' not in str(row.get('automation_pitch_from_llm', '')))
        st.metric("Pitches Generated", pitches_generated)

def main():
    st.title("AI Lead Enrichment Bot")
    st.markdown("Enrich your company leads with AI-powered insights")
    
    if import_error:
        st.error(f"Import Issue: {import_error}")
        st.info("The app will work with limited functionality using the fallback enricher.")
    
    st.sidebar.header("Configuration")
    
    st.sidebar.subheader("API Keys")
    gemini_key = st.sidebar.text_input(
        "Google Gemini API Key",
        type="password",
        help="Get free API key from Google AI Studio"
    )
    
    openai_key = st.sidebar.text_input(
        "OpenAI API Key (Optional)",
        type="password",
        help="Optional OpenAI API key for GPT analysis"
    )
    
    if not gemini_key and not openai_key:
        st.sidebar.warning("No API keys provided. Will use basic analysis only.")
    
    st.sidebar.subheader("Processing Settings")
    batch_size = st.sidebar.slider(
        "Batch Size",
        min_value=1,
        max_value=50,
        value=5,
        help="Number of companies to process"
    )
    
    delay = st.sidebar.slider(
        "Delay between requests (seconds)",
        min_value=0.0,
        max_value=5.0,
        value=1.0,
        step=0.5,
        help="Delay to avoid rate limiting"
    )
    
    show_progress = st.sidebar.checkbox(
        "Show live progress",
        value=True,
        help="Display results as they're processed"
    )
    
    add_sidebar_info()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("Upload Data")
        
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type="csv",
            help="Upload a CSV file with a 'company_name' column"
        )
        
        if st.button("Create Sample Data", type="secondary"):
            sample_data = pd.DataFrame({
                'company_name': [
                    'OpenAI', 'Microsoft', 'Google', 'Amazon', 
                    'Slack', 'Notion', 'Stripe', 'Airbnb'
                ]
            })
            st.success("Sample data created")
            st.dataframe(sample_data, use_container_width=True)
            
            csv_buffer = io.StringIO()
            sample_data.to_csv(csv_buffer, index=False)
            st.download_button(
                label="Download Sample CSV",
                data=csv_buffer.getvalue(),
                file_name="sample_companies.csv",
                mime="text/csv"
            )
    
    with col2:
        st.header("Preview Data")
        
        df = None
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                
                if 'company_name' not in df.columns:
                    st.error("CSV must contain a 'company_name' column")
                    st.info("Available columns: " + ", ".join(df.columns.tolist()))
                else:
                    st.success(f"Found {len(df)} companies to process")
                    st.dataframe(df.head(10), use_container_width=True)
                    
                    if len(df) > 10:
                        st.info(f"Showing first 10 rows. Total: {len(df)} companies")
                        
            except Exception as e:
                st.error(f"Error reading CSV: {e}")
                df = None
    
    if df is not None and 'company_name' in df.columns:
        st.header("Start Processing")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            st.metric("Total Companies", len(df))
        with col2:
            st.metric("Will Process", min(batch_size, len(df)))
        with col3:
            estimated_time = min(batch_size, len(df)) * (delay + 2)
            st.metric("Est. Time", f"{estimated_time:.0f}s")
        
        if st.button("Start Enrichment", type="primary", use_container_width=True):
            enricher = create_enricher_instance(gemini_key, openai_key)
            
            with st.spinner("Processing companies..."):
                process_companies(df, enricher, batch_size, show_progress, delay)
    
    elif uploaded_file is not None:
        st.warning("Please upload a valid CSV file with a 'company_name' column to continue.")
    
    else:
        st.header("Welcome")
        st.markdown("""
        This AI Lead Enrichment Bot helps you gather valuable insights about your company leads.
        
        **What it does:**
        - Finds company websites automatically
        - Identifies industry and company size
        - Generates AI-powered company summaries
        - Creates custom automation pitches
        - Exports enriched data as CSV
        
        **To get started:**
        1. Add your Gemini API key in the sidebar
        2. Upload a CSV file with company names
        3. Click "Start Enrichment"
        """)
        
        st.subheader("Sample Output Preview")
        sample_result = pd.DataFrame([
            {
                'company_name': 'OpenAI',
                'website': 'https://openai.com',
                'industry': 'Technology',
                'company_size': 'Large',
                'summary_from_llm': 'OpenAI is an AI research company developing safe artificial intelligence.',
                'target_customer': 'Developers and enterprises',
                'automation_pitch_from_llm': 'QF Innovate can help implement GPT-powered chatbots and automate content generation workflows.'
            }
        ])
        st.dataframe(sample_result, use_container_width=True)

if __name__ == "__main__":
    main()