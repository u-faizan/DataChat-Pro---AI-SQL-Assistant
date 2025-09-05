# DataChat Pro - AI SQL Assistant 🧠

A powerful Streamlit application that transforms natural language queries into SQL commands using AI, making database exploration accessible to everyone.

## 🌟 Features

### Core Functionality
- **Natural Language to SQL**: Convert plain English questions into SQL queries using AI
- **Interactive Chat Interface**: Conversational approach to database exploration
- **Real-time Query Execution**: Execute generated SQL queries and display results instantly
- **Data Visualization**: Automatic chart generation for query results
- **Multiple Database Sources**: Support for sample databases and file uploads

### Advanced Features
- **Smart Query Suggestions**: Context-aware query recommendations
- **Database Schema Explorer**: Comprehensive view of tables, columns, and data types
- **Performance Analytics**: Track query success rates and response times
- **Export Capabilities**: Download query results and chat history
- **Sample Data Preview**: View sample records from each table
- **Database Insights**: Automated analysis of database structure and content

## 🛠️ Technology Stack

- **Frontend**: Streamlit with custom CSS styling
- **AI/ML**: LangChain with Groq API (Gemma2-9b-it model)
- **Database**: SQLite with SQLAlchemy
- **Visualization**: Plotly Express & Plotly Graph Objects
- **Data Processing**: Pandas
- **UI Components**: Modern gradient designs with responsive layout

## 📋 Prerequisites

- Python 3.8 or higher
- Groq API key (free at [console.groq.com](https://console.groq.com/keys))
- SQLite database file (or use the included sample database)

## 🚀 Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd datachat-pro
   ```

2. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🏃‍♂️ Quick Start

1. **Get your Groq API Key**:
   - Visit [Groq Console](https://console.groq.com/keys)
   - Create a free account
   - Generate an API key

2. **Prepare your database**:
   - Use the sample `student.db` file, or
   - Upload your own SQLite database file

3. **Run the application**:
   ```bash
   streamlit run app.py
   ```

4. **Open your browser** to `http://localhost:8501`

5. **Configure the app**:
   - Enter your Groq API key in the sidebar
   - Select your database source
   - Start chatting with your data!

## 💡 Usage Examples

### Sample Queries
Try these natural language queries:

**Basic Data Exploration**:
- "Show me all students"
- "How many records are in each table?"
- "What tables do we have?"

**Analytical Queries**:
- "Find students with grades above 85"
- "Show the average grade by subject"
- "List top 10 students by performance"

**Complex Questions**:
- "Which students are enrolled in both Math and Science?"
- "Show grade distribution across different departments"
- "Find students who haven't submitted assignments"

## 🎯 Key Components

### 1. Database Connection
- Automatic SQLite database detection
- Support for file uploads
- Connection validation and error handling

### 2. AI Query Processing
- LangChain SQL agent integration
- Natural language understanding
- SQL query generation and validation

### 3. Results Display
- Formatted data tables
- Automatic visualizations
- Export functionality

### 4. Multiple Views
- **Chat View**: Interactive conversation interface
- **Schema View**: Database structure explorer
- **Insights View**: Automated database analysis
- **Overview View**: Data distribution charts

## 📊 Database Schema Support

The application automatically detects and works with:
- Table structures and relationships
- Column names and data types
- Record counts and data distribution
- Sample data for context

## 🎨 User Interface

### Modern Design Features
- Gradient backgrounds and modern styling
- Responsive layout for different screen sizes
- Intuitive navigation with sidebar controls
- Real-time status indicators
- Interactive charts and visualizations

### Navigation Options
- **Quick Actions**: One-click access to common tasks
- **Query Suggestions**: Smart recommendations based on your data
- **Export Tools**: Download results and history
- **Performance Metrics**: Track usage and success rates

## 🔧 Configuration Options

### API Settings
- Groq API key configuration
- Model selection (currently using Gemma2-9b-it)
- Temperature and response settings

### Database Options
- Sample database usage
- Custom SQLite file upload
- Automatic schema detection

### Display Preferences
- Chat history management
- Visualization settings
- Export formats

## 📈 Performance Features

### Analytics Dashboard
- Total queries executed
- Success rate tracking
- Average response times
- Database statistics

### Optimization
- Query caching for repeated requests
- Efficient SQL generation
- Memory management for large datasets
- Token usage optimization

## 🛡️ Error Handling

The application includes comprehensive error handling for:
- Database connection issues
- Invalid SQL queries
- API rate limits
- File upload problems
- Parsing errors

## 🚀 Advanced Usage

### Custom Database Setup
1. Prepare your SQLite database
2. Ensure proper table structures
3. Upload through the interface
4. Verify connection status

### Query Optimization Tips
- Use specific table and column names
- Be clear about what data you want
- Ask follow-up questions for refinement
- Use the schema view for reference

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional database support (PostgreSQL, MySQL)
- Enhanced visualization options
- Query performance optimization
- UI/UX improvements
- Error handling enhancements

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🐛 Troubleshooting

### Common Issues

**"API Key Error"**:
- Verify your Groq API key is correct
- Check your API quota and usage limits

**"Database Connection Failed"**:
- Ensure the SQLite file is valid
- Check file permissions
- Verify the database isn't corrupted

**"Query Processing Error"**:
- Try rephrasing your question
- Check if the requested data exists
- Use simpler queries first

### Performance Tips
- Keep queries specific and focused
- Use the schema view to understand your data structure
- Break complex questions into smaller parts
- Clear chat history periodically

## 📞 Support

If you have any issues, questions, or suggestions:

- Check the **Troubleshooting** section.
- Review the error messages in the UI.
- Ensure all dependencies are installed correctly.
- Verify your API key and database setup.
- Reach out on [LinkedIn](https://www.linkedin.com/in/your-linkedin-u-faizan/)  
- Open an issue in the [GitHub repository](https://github.com/u-faizan/DataChat-Pro---AI-SQL-Assistant)


## 🔄 Updates and Maintenance

The application includes:
- Automatic dependency management
- Session state handling
- Memory cleanup for long sessions
- Error recovery mechanisms

---

**Made with ❤️ using Streamlit and AI**

Transform your database queries from complex SQL to simple conversations!
