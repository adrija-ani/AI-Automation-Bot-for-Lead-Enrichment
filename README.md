# 🤖 AI Lead Enrichment Bot

An AI-powered automation tool that enriches company data using web scraping and LLM analysis. Built for QF Innovate's internship assessment task.

## 🎯 Project Overview

This bot takes a simple CSV with company names and enriches it with:
- Company websites
- Industry classification
- Business summaries
- Target customer analysis
- Custom AI automation pitches

## 🚀 Demo Video

[![AI Lead Enrichment Bot Demo]https://youtu.be/HWAcL8LcP_E?si=8HfjPYL5fUnzSaAM

## ✨ Features

### Core Functionality
- 🌐 **Website Discovery**: Automatically finds company websites using DuckDuckGo API
- 🔍 **Content Scraping**: Extracts and cleans website content using BeautifulSoup
- 🤖 **AI Analysis**: Uses Google Gemini API (free tier) or OpenAI for intelligent insights
- 📊 **Data Enrichment**: Generates comprehensive company profiles
- 💾 **CSV Export**: Outputs enriched data in structured format

### Web Interface
- 📤 **File Upload**: Drag-and-drop CSV upload
- ⚡ **Real-time Processing**: Live progress tracking
- 🎛️ **Configurable Settings**: Batch size, delays, API selection
- 📥 **Instant Download**: One-click CSV export
- 📱 **Responsive Design**: Works on desktop and mobile

## 🛠️ Technology Stack

- **Python 3.8+**: Core programming language
- **Pandas**: Data manipulation and analysis
- **Requests + BeautifulSoup**: Web scraping
- **Google Gemini API**: AI analysis (free tier available)
- **Streamlit**: Web interface
- **DuckDuckGo API**: Website discovery (free)

## 📦 Installation & Setup

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/ai-lead-enrichment-bot.git
cd ai-lead-enrichment-bot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Get API Keys

#### Google Gemini API (Recommended - Free)
1. Visit [Google AI Studio](https://makersuite.google.com/)
2. Create account and generate API key
3. Copy your API key

#### OpenAI API (Optional)
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create account and add billing
3. Generate API key

### 4. Set Environment Variables
```bash
# Option 1: Create .env file
echo "GEMINI_API_KEY=your_gemini_key_here" > .env
echo "OPENAI_API_KEY=your_openai_key_here" >> .env

# Option 2: Export directly
export GEMINI_API_KEY="your_gemini_key_here"
export OPENAI_API_KEY="your_openai_key_here"  # Optional
```

## 🚀 Usage

### Method 1: Streamlit Web App (Recommended)
```bash
streamlit run streamlit_app.py
```
Then open http://localhost:8501 in your browser.

### Method 2: Command Line
```bash
python lead_enrichment_bot.py
```

### Method 3: Python Script
```python
from lead_enrichment_bot import CompanyEnricher

# Initialize enricher
enricher = CompanyEnricher(gemini_api_key="your_key_here")

# Process CSV
enriched_df = enricher.process_csv('companies.csv')
print(enriched_df.head())
```

## 📄 Input/Output Format

### Input CSV Format
```csv
company_name
OpenAI
DeepMind
Zoho
Freshworks
Slack
Notion
```

### Output CSV Format
```csv
company_name,website,industry,company_size,summary_from_llm,target_customer,automation_pitch_from_llm
OpenAI,https://openai.com,Technology,Large,"OpenAI is an AI research company that develops advanced artificial intelligence systems and models.","Developers, businesses, researchers","QF Innovate could help OpenAI implement automated customer onboarding and API usage optimization systems."
```

## 🎛️ Configuration Options

### API Settings
- **Gemini API**: Free tier with 60 requests/minute
- **OpenAI API**: Paid service, more accurate results
- **Fallback Mode**: Basic analysis without APIs

### Processing Settings
- **Batch Size**: 1-10 companies per run (start small for testing)
- **Delay**: 1-5 seconds between requests (be respectful to websites)
- **Timeout**: 15 seconds per website scrape

## 🧠 AI Prompts Used

### Company Analysis Prompt
```
Analyze the following company based on their website content:

Company Name: {company_name}
Website Content: {website_content}

Please provide:
1. A brief summary of what this company does (2-3 sentences)
2. Their target customer/market
3. Their industry category
4. Company size estimate (startup/small/medium/large/enterprise)
5. A specific AI automation idea that QF Innovate could pitch to them

Format your response as JSON:
{
    "summary": "Company summary here",
    "target_customer": "Target customer description",
    "industry": "Industry category", 
    "company_size": "Size estimate",
    "automation_pitch": "Specific AI automation pitch"
}
```

## 📊 Sample Results

### Input
```csv
company_name
Slack
Zoom
Shopify
```

### Output
```csv
company_name,website,industry,company_size,summary_from_llm,target_customer,automation_pitch_from_llm
Slack,https://slack.com,Technology,Large,"Slack is a business communication platform that organizes team conversations in channels, integrates with work tools, and enables remote collaboration.","Businesses of all sizes, remote teams, enterprise organizations","QF Innovate could develop AI-powered meeting summarization and automated workflow triggers for Slack channels."
Zoom,https://zoom.us,Technology,Large,"Zoom is a video communications platform providing video meetings, webinars, and cloud phone services for businesses and individuals.","Remote workers, businesses, educational institutions","QF Innovate could create AI meeting transcription with action item extraction and automated follow-up email generation."
Shopify,https://shopify.com,E-commerce,Large,"Shopify is an e-commerce platform that enables individuals and businesses to create and customize online stores with integrated payment processing.","Small to medium businesses, entrepreneurs, online retailers","QF Innovate could build AI-powered product description generation and customer behavior analysis for Shopify stores."
```

## 🔧 Architecture

```
Input CSV
    ↓
Website Discovery (DuckDuckGo API)
    ↓
Content Scraping (BeautifulSoup)
    ↓
AI Analysis (Gemini/OpenAI)
    ↓
Data Enrichment
    ↓
Output CSV
```

### Key Components

1. **CompanyEnricher Class**: Main processing engine
2. **Website Discovery**: Uses DuckDuckGo Instant Answer API
3. **Content Scraper**: BeautifulSoup with smart content extraction
4. **LLM Analyzer**: Gemini/OpenAI integration with fallback
5. **Streamlit Interface**: User-friendly web application

## 🎯 AI Automation Ideas Generated

The bot generates specific, actionable AI automation pitches based on company analysis:

- **SaaS Companies**: Customer onboarding automation, usage analytics
- **E-commerce**: Product recommendation engines, inventory optimization  
- **Healthcare**: Patient data analysis, appointment scheduling
- **Finance**: Risk assessment automation, fraud detection
- **Education**: Personalized learning paths, automated grading
- **Manufacturing**: Predictive maintenance, quality control

## 🚀 Performance & Limitations

### Performance
- **Processing Speed**: ~2-3 companies per minute (with delays)
- **Accuracy**: 85-90% website discovery rate
- **API Usage**: ~1000 tokens per company analysis

### Limitations
- Rate limited by website politeness delays
- Dependent on website content quality
- API quotas may limit batch processing
- Some websites block automated scraping

## 🛡️ Error Handling

- **Network Timeouts**: Automatic retry with exponential backoff
- **API Failures**: Graceful fallback to basic analysis
- **Invalid Websites**: Continues processing with error logging
- **Malformed Content**: Robust text cleaning and parsing

## 🔒 Best Practices

### Ethical Web Scraping
- Respectful delays between requests
- User-Agent headers for transparency
- Timeout limits to avoid hanging
- Robots.txt compliance (where possible)

### API Usage
- Environment variable for API keys
- Error handling for rate limits
- Efficient prompt design
- Token usage optimization

## 📈 Future Enhancements

- [ ] **Social media integration** (LinkedIn, Twitter APIs)
- [ ] **Contact information extraction** (emails, phone numbers)
- [ ] **Competitor analysis** using search APIs
- [ ] **Financial data integration** (funding, revenue estimates)
- [ ] **Bulk processing optimization** (async/parallel processing)
- [ ] **Advanced filtering** (company size, industry, location)
- [ ] **Export formats** (Excel, JSON, Google Sheets integration)

## 🐛 Troubleshooting

### Common Issues

**1. No websites found**
- Check internet connection
- Try with well-known companies first
- Verify company names are spelled correctly

**2. API errors**
- Verify API keys are set correctly
- Check API quotas and billing
- Test with individual companies first

**3. Streamlit issues**
- Ensure all dependencies are installed
- Check Python version compatibility
- Try running with `--server.port 8502` if port conflicts

**4. Scraping failures**
- Some websites block automated access
- Try with different companies
- Check firewall/proxy settings

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📞 Support

For questions or issues:
- Email: hey@qfinnovate.com
- Create GitHub issue
- Check troubleshooting section above

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **QF Innovate** for the internship opportunity
- **Google AI Studio** for free Gemini API access
- **DuckDuckGo** for free search API
- **Streamlit** for amazing web framework
- **Open source community** for excellent libraries

---

**Built with ❤️ for QF Innovate Internship Assessment**

*Last updated: May 2025*
