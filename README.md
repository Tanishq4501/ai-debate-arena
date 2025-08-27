# AI Debate Arena

A sophisticated AI-powered debate platform where artificial intelligence agents engage in structured intellectual discourse on complex topics. Watch different AI personas argue, analyze, and compete using distinct reasoning styles and debate strategies.

## Live Demo

**[Try AI Debate Arena Live](https://ai-debate-arena-tantheta.streamlit.app/)** 

*Replace with your actual Streamlit deployment URL*

## Screenshots

### Main Interface
*[Screenshot coming soon.....]*

### Debate Setup
*[Screenshot coming soon.....]*

### Live Debate
*[Screenshot coming soon.....]*

### Results Dashboard
*[Screenshot coming soon.....]*

## Features

### AI Personas
Choose from 6 distinct AI debate personalities:
- **Formal Analyst**: Logical, evidence-based, methodical approach
- **Emotional Activist**: Passionate, persuasive, emotionally compelling
- **Sarcastic Rebel**: Witty, challenging, uses humor strategically  
- **Curious Thinker**: Questioning, exploratory, open-minded
- **Strategic Debater**: Tactical, calculated, focuses on winning
- **Evidence Expert**: Data-driven, factual, research-focused

### Structured Debate Format
- Opening statements
- Multiple rebuttal rounds
- Cross-examination sessions
- Strategic questioning
- Closing arguments
- Comprehensive scoring system

### Advanced Features
- Real-time debate progression
- Interactive timeline visualization
- Persistent session management
- Performance analytics
- Auto-debate mode
- Modern responsive UI

## Technology Stack

- **Frontend**: Streamlit with custom CSS/HTML
- **AI Engine**: Google Gemini API
- **Database**: SQLite with thread-safe operations
- **Styling**: Modern dark theme with glassmorphism
- **Deployment**: Streamlit Cloud

## Local Development

### Prerequisites
- Python 3.8+
- Google Gemini API key
- Git

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ai-debate-arena.git
   cd ai-debate-arena
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API key**
   ```bash
   # Create .streamlit/secrets.toml
   mkdir .streamlit
   echo 'GEMINI_API_KEY = "your_api_key_here"' > .streamlit/secrets.toml
   
   # Or set environment variable
   export GEMINI_API_KEY="your_api_key_here"
   ```

4. **Run the application**
   ```bash
   streamlit run debate_arena.py
   ```

5. **Access the app**
   Open http://localhost:8501 in your browser

## Deployment

### Streamlit Cloud Deployment

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Set main file: `debate_arena.py`
   - Add secrets: `GEMINI_API_KEY = "your_api_key"`
   - Deploy

3. **Configure Secrets**
   In Streamlit Cloud dashboard, add:
   ```toml
   GEMINI_API_KEY = "your_actual_gemini_api_key_here"
   ```

## Project Structure

```
ai-debate-arena/
├── agent_manager.py      # AI agent logic and debate strategies
├── debate_arena.py       # Main Streamlit application
├── memory_manager.py     # Database operations and session management
├── requirements.txt      # Python dependencies
└── README.md            # Project documentation
```

## Core Components

### Agent Manager (`agent_manager.py`)
- Manages AI agent personalities and behaviors
- Handles debate strategies and response generation
- Implements fallback mechanisms for API failures
- Tracks argument patterns and opponent analysis

### Debate Arena (`debate_arena.py`)
- Main Streamlit interface with modern UI
- Manages debate flow and user interactions
- Implements real-time updates and animations
- Handles session state and error management

### Memory Manager (`memory_manager.py`)
- SQLite database operations with thread safety
- Session persistence and history tracking
- Performance analytics and scoring
- Data cleanup and maintenance utilities

## Usage Guide

### Starting a Debate

1. **Choose a Topic**
   - Enter a clear, debatable statement
   - Examples: "AI should replace human teachers", "Social media does more harm than good"

2. **Select AI Personas**
   - Choose 2-4 different personas for diverse perspectives
   - Mix complementary styles (e.g., Formal Analyst vs Emotional Activist)

3. **Configure Settings**
   - Enable auto-debate for hands-off experience
   - Adjust debate speed for optimal viewing
   - Enable detailed scoring for comprehensive analysis

4. **Launch and Watch**
   - Debates progress through structured phases
   - Each agent maintains consistent personality
   - Real-time scoring and analysis

### Best Practices

**Topic Selection:**
- Use clear, controversial statements
- Avoid overly complex or niche subjects  
- Frame as "Should X..." or "Is Y better than Z?"

**Persona Combinations:**
- **Balanced**: Formal Analyst + Emotional Activist
- **Dynamic**: Sarcastic Rebel + Evidence Expert  
- **Thoughtful**: Curious Thinker + Strategic Debater
- **Complex**: Mix 3-4 personas for multi-sided debates

## API Usage and Limits

### Google Gemini API
- Requires valid API key with billing enabled
- Rate limits may apply based on your plan
- Monitor usage in Google Cloud Console

### Error Handling
- Automatic retries with exponential backoff
- Graceful degradation with fallback responses
- Comprehensive logging for debugging

## Contributing

We welcome contributions to improve AI Debate Arena:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Add tests if applicable**
5. **Submit a pull request**

### Development Guidelines
- Follow existing code style and structure
- Add comprehensive error handling
- Include docstrings for new functions
- Test with multiple AI personas and topics

## Known Issues

- Database resets on Streamlit Cloud app restart
- Long debates may timeout on free hosting tiers
- API rate limits may affect rapid-fire debates

## Future Enhancements

- Persistent cloud database integration
- Advanced scoring algorithms
- Multi-language support
- Custom persona creation
- Debate export and sharing
- Audience voting system

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues, questions, or contributions:
- Create an issue on GitHub
- Check existing documentation
- Review error logs in Streamlit Cloud dashboard

## Acknowledgments

- Google Gemini API for AI capabilities
- Streamlit for the excellent deployment platform
- Open source community for inspiration and tools

---

**Built with ❤️ and artificial intelligence**

*Last updated: August 2025*
