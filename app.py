# DataChat Pro - AI SQL Assistant with analytics
# Imports for core functionality, UI, database handling, and AI agents
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sqlite3
import tempfile
import os
import time
import json
import re

# LangChain imports for SQL agent
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain_groq import ChatGroq
from sqlalchemy import create_engine, text, inspect

# Page configuration with custom theme
st.set_page_config(
    page_title="DataChat Pro - AI SQL Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .status-connected {
        background: linear-gradient(90deg, #56ab2f 0%, #a8e6cf 100%);
        color: white;
        padding: 0.8rem;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .status-error {
        background: linear-gradient(90deg, #ff416c 0%, #ff4b2b 100%);
        color: white;
        padding: 0.8rem;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .query-suggestion {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 0.8rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .query-suggestion:hover {
        background: #e9ecef;
        border-color: #667eea;
    }
    
    .sql-output {
        background: #2d3748;
        color: #e2e8f0;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-family: 'Courier New', monospace;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state with all necessary variables
def init_session_state():
    if 'messages' not in st.session_state:
        st.session_state.messages = [{
            'role': 'assistant',
            'content': 'Welcome to DataChat Pro! I can help you explore your database using natural language queries. Connect to your database and start asking questions!',
            'timestamp': datetime.now()
        }]
    
    if 'db_engine' not in st.session_state:
        st.session_state.db_engine = None
    
    if 'db_instance' not in st.session_state:
        st.session_state.db_instance = None
        
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []
        
    if 'analytics' not in st.session_state:
        st.session_state.analytics = {
            'total_queries': 0,
            'successful_queries': 0,
            'total_response_time': 0
        }
    
    if 'current_view' not in st.session_state:
        st.session_state.current_view = 'chat'

init_session_state()

# Setup database connection from file path
def setup_database(db_path):
    try:
        engine = create_engine(f"sqlite:///{db_path}")
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db = SQLDatabase(engine)
        return engine, db, None
    except Exception as e:
        return None, None, str(e)

# Get comprehensive database information (tables, columns, row counts)
def get_database_info(engine):
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        schema_info = {}
        total_records = 0
        
        for table in tables:
            try:
                with engine.connect() as conn:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM [{table}]"))
                    row_count = result.scalar()
                    total_records += row_count
                    
                columns = inspector.get_columns(table)
                schema_info[table] = {
                    'columns': [{'name': col['name'], 'type': str(col['type'])} for col in columns],
                    'row_count': row_count
                }
            except Exception:
                schema_info[table] = {'columns': [], 'row_count': 0}
        
        return schema_info, total_records, None
        
    except Exception as e:
        return {}, 0, str(e)

# Get sample data from a table for preview
def get_sample_data(engine, table_name, limit=5):
    try:
        df = pd.read_sql_query(f"SELECT * FROM [{table_name}] LIMIT {limit}", engine)
        return df
    except Exception:
        return pd.DataFrame()

# Execute SQL query and return results with timing
def execute_sql_query(engine, query):
    try:
        start_time = time.time()
        df = pd.read_sql_query(query, engine)
        execution_time = time.time() - start_time
        return df, execution_time, None
    except Exception as e:
        return None, 0, str(e)

# Check if user input is asking for data/query results
def is_data_query(user_input):
    query_indicators = [
        'show me', 'list', 'find', 'get', 'select', 'count', 'sum', 'average', 'max', 'min',
        'who', 'what are', 'how many', 'which', 'top', 'bottom', 'first', 'last',
        'students who', 'data where', 'records', 'rows', 'table', 'give me', 'name of'
    ]
    
    user_lower = user_input.lower()
    return any(indicator in user_lower for indicator in query_indicators)

# Setup LangChain SQL agent
@st.cache_resource
def setup_ai_agent(_db, api_key):
    if not api_key:
        return None, "No API key provided"
    
    try:
        llm = ChatGroq(
            groq_api_key=api_key,
            model_name="gemma2-9b-it",
            temperature=0
        )
        
        agent = create_sql_agent(
            llm=llm,
            db=_db,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True,
            # max_iterations=3  # Limit iterations to reduce token usage
        )
        
        return agent, None
        
    except Exception as e:
        return None, str(e)

# Extract SQL query from AI response using regex patterns
def extract_sql_query(response_text):
    sql_patterns = [
        r'```sql\s*(.*?)\s*```',
        r'```\s*(SELECT.*?)\s*```',
        r'(SELECT\s+.*?(?:;|\n|$))',
        r'(INSERT\s+.*?(?:;|\n|$))',
        r'(UPDATE\s+.*?(?:;|\n|$))',
        r'(DELETE\s+.*?(?:;|\n|$))'
    ]
    
    for pattern in sql_patterns:
        matches = re.findall(pattern, response_text, re.IGNORECASE | re.DOTALL)
        if matches:
            sql_query = matches[0].strip()
            if sql_query.endswith(';'):
                sql_query = sql_query[:-1]
            return sql_query
    
    return None

# Generate quick insights about the database
def generate_database_insights(engine, schema_info):
    insights = []
    
    try:
        if schema_info:
            max_records = max(info['row_count'] for info in schema_info.values())
            largest_table = [name for name, info in schema_info.items() if info['row_count'] == max_records][0]
            insights.append(f"Largest table: {largest_table} ({max_records:,} records)")
            
            total_records = sum(info['row_count'] for info in schema_info.values())
            insights.append(f"Total records: {total_records:,}")
            
            avg_columns = sum(len(info['columns']) for info in schema_info.values()) / len(schema_info)
            insights.append(f"Average columns per table: {avg_columns:.1f}")
        
        return insights
    except Exception:
        return ["Unable to generate insights"]

# Create a chart showing record counts per table
def create_data_overview_chart(schema_info):
    if not schema_info:
        return None
    
    table_names = list(schema_info.keys())
    record_counts = [info['row_count'] for info in schema_info.values()]
    
    fig = px.bar(
        x=table_names,
        y=record_counts,
        title="Records per Table",
        labels={'x': 'Tables', 'y': 'Record Count'}
    )
    fig.update_layout(showlegend=False)
    return fig

# Process user query with database connection
def process_user_query(user_input, api_key):
    if not api_key:
        st.error("🔑 Please provide your Groq API key in the sidebar")
        return
    
    if not st.session_state.db_engine or not st.session_state.db_instance:
        st.error("📄 Please connect to a database first")
        return
    
    # Add user message only once - FIX for duplicate message issue
    if not st.session_state.messages or st.session_state.messages[-1]['content'] != user_input or st.session_state.messages[-1]['role'] != 'user':
        st.session_state.messages.append({
            'role': 'user',
            'content': user_input,
            'timestamp': datetime.now()
        })
    
    with st.chat_message("user"):
        st.write(user_input)
    
    # Process with AI
    with st.chat_message("assistant"):
        with st.spinner("🧠 Processing your query..."):
            try:
                start_time = time.time()
                
                agent, agent_error = setup_ai_agent(st.session_state.db_instance, api_key)
                
                if agent_error:
                    st.error(f"AI Agent Error: {agent_error}")
                    return
                
                # Enhanced prompt to ensure SQL query is returned
                enhanced_query = f"{user_input}. Please also show the SQL query you used to get this result."
                
                # Optimize query for token usage
                if "what tables" in user_input.lower() or "tables do we have" in user_input.lower():
                    enhanced_query = "list all table names and show the SQL query"  # More efficient prompt
                
                callback_handler = StreamlitCallbackHandler(st.container())
                response = agent.run(enhanced_query, callbacks=[callback_handler])
                
                execution_time = time.time() - start_time
                
                show_sql = is_data_query(user_input)
                
                st.write(response)
                
                st.session_state.analytics['total_queries'] += 1
                st.session_state.analytics['total_response_time'] += execution_time
                st.session_state.analytics['successful_queries'] += 1
                
                sql_query = None
                dataframe_result = None
                
                # Always try to extract and show SQL query
                try:
                    sql_query = extract_sql_query(response)
                    
                    if sql_query:
                        st.markdown("**🔍 Generated SQL Query:**")
                        st.code(sql_query, language='sql')
                        
                        # Execute the SQL query to show results
                        df, exec_time, error = execute_sql_query(st.session_state.db_engine, sql_query)
                        if error is None and df is not None and not df.empty:
                            dataframe_result = df
                            
                            st.subheader("📊 Query Results")
                            st.dataframe(df, use_container_width=True)
                            
                            csv = df.to_csv(index=False)
                            st.download_button(
                                "📥 Download Results",
                                csv,
                                f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                "text/csv"
                            )
                            
                            numeric_cols = df.select_dtypes(include=['number']).columns
                            if len(numeric_cols) > 0 and len(df) > 1 and len(df) <= 50:
                                st.subheader("📈 Quick Visualization")
                                
                                if len(numeric_cols) >= 2:
                                    fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1])
                                    st.plotly_chart(fig, use_container_width=True)
                                else:
                                    fig = px.bar(df.head(10), y=numeric_cols[0])
                                    st.plotly_chart(fig, use_container_width=True)
                        elif error:
                            st.warning(f"Could not execute extracted SQL query: {error}")
                
                except Exception as e:
                    st.info("Could not extract or execute SQL query automatically")
                
                message_data = {
                    'role': 'assistant',
                    'content': response,
                    'timestamp': datetime.now(),
                    'execution_time': execution_time,
                    'sql_query': sql_query,
                    'dataframe': dataframe_result
                }
                
                st.session_state.messages.append(message_data)
                
                st.session_state.query_history.append({
                    'query': user_input,
                    'response': response,
                    'timestamp': datetime.now(),
                    'execution_time': execution_time,
                    'sql_query': sql_query
                })
                
                if len(st.session_state.query_history) > 100:
                    st.session_state.query_history = st.session_state.query_history[-50:]
                
                st.caption(f"⚡ Processed in {execution_time:.3f} seconds")
                
            except Exception as e:
                error_msg = f"Error processing query: {str(e)}"
                st.error(error_msg)
                
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': error_msg,
                    'timestamp': datetime.now(),
                    'error': True
                })
        
    st.rerun()

# Main application entry point
def main():
    # Header section with gradient background
    st.markdown("""
    <div class="main-header">
        <h1>🧠 DataChat Pro - AI SQL Assistant</h1>
        <p style="margin:0;">Transform natural language into SQL queries with AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar configuration panel
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input for Groq
        api_key = st.text_input(
            "Groq API Key",
            type="password",
            help="Get your free API key from https://console.groq.com/keys"
        )
        
        if api_key:
            st.success("✅ API Key provided")
        else:
            st.warning("⚠️ Please enter your Groq API key")
        
        st.markdown("---")
        
        # Database selection options
        st.subheader("📁 Database Selection")
        
        db_option = st.radio(
            "Choose database source:",
            ["Use sample student.db", "Upload SQLite file"]
        )
        
        db_path = None
        
        if db_option == "Use sample student.db":
            if os.path.exists("student.db"):
                db_path = "student.db"
                st.success("✅ student.db found")
            else:
                st.error("❌ student.db not found")
                st.info("Please ensure student.db is in the app directory")
        
        else:  # Upload SQLite file option
            uploaded_file = st.file_uploader(
                "Upload SQLite Database",
                type=['db', 'sqlite', 'sqlite3']
            )
            
            if uploaded_file is not None:
                temp_dir = tempfile.gettempdir()
                db_path = os.path.join(temp_dir, f"uploaded_{uploaded_file.name}")
                
                with open(db_path, 'wb') as f:
                    f.write(uploaded_file.getvalue())
                
                st.success(f"✅ {uploaded_file.name} uploaded")
                st.info(f"Database path: {db_path}")
        
        # Setup database connection with refresh on path change
        if db_path:
            if st.session_state.get('current_db_path') != db_path:
                setup_ai_agent.clear()
                
                with st.spinner("Connecting to database..."):
                    engine, db, error = setup_database(db_path)
                    
                    if error:
                        st.error(f"❌ Connection failed: {error}")
                        st.session_state.db_engine = None
                        st.session_state.db_instance = None
                        st.session_state.current_db_path = None
                    else:
                        st.session_state.db_engine = engine
                        st.session_state.db_instance = db
                        st.session_state.current_db_path = db_path
                        st.success("✅ Database connected!")
        
        # Database statistics display
        if st.session_state.db_engine:
            st.markdown("---")
            st.subheader("📊 Database Stats")
            
            schema_info, total_records, error = get_database_info(st.session_state.db_engine)
            
            if not error:
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Tables", len(schema_info))
                    st.metric("Queries", st.session_state.analytics['total_queries'])
                
                with col_b:
                    st.metric("Records", f"{total_records:,}")
                    success_rate = (st.session_state.analytics['successful_queries'] / 
                                  max(st.session_state.analytics['total_queries'], 1) * 100)
                    st.metric("Success Rate", f"{success_rate:.1f}%")
        
        # Quick action buttons
        st.markdown("---")
        st.subheader("⚡ Quick Actions")
        
        chat_button_style = "🟢" if st.session_state.current_view == 'chat' else "⚪"
        if st.button(f"{chat_button_style} Chat with Your Data", use_container_width=True):
            st.session_state.current_view = 'chat'
            st.rerun()
        
        if st.button("📋 Show Database Schema", use_container_width=True):
            st.session_state.current_view = 'schema'
            st.rerun()
        
        if st.button("💡 Generate Insights", use_container_width=True):
            st.session_state.current_view = 'insights'
            st.rerun()
        
        if st.button("📈 Create Data Overview", use_container_width=True):
            st.session_state.current_view = 'overview'
            st.rerun()
        
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = st.session_state.messages[:1]
            st.session_state.current_view = 'chat'
            st.rerun()
        
        # Export functionality for query history
        if st.session_state.query_history:
            st.markdown("---")
            st.subheader("📥 Export")
            
            history_df = pd.DataFrame([
                {
                    'Query': h['query'],
                    'Response': h['response'][:100] + '...' if len(h['response']) > 100 else h['response'],
                    'SQL Query': h.get('sql_query', 'N/A'),
                    'Execution Time (s)': h.get('execution_time', 'N/A'),
                    'Timestamp': h['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                }
                for h in st.session_state.query_history
            ])
            
            csv = history_df.to_csv(index=False)
            st.download_button(
                "📋 Download Query History",
                csv,
                "datachat_history.csv",
                "text/csv",
                use_container_width=True
            )

    # Main content area with different views
    if st.session_state.current_view == 'schema':
        # Database schema view
        st.subheader("📋 Complete Database Schema")
        
        if st.session_state.db_engine:
            schema_info, total_records, error = get_database_info(st.session_state.db_engine)
            
            if not error:
                for table_name, table_info in schema_info.items():
                    st.write(f"**Table: {table_name}** ({table_info['row_count']:,} rows)")
                    
                    if table_info['columns']:
                        cols_df = pd.DataFrame(table_info['columns'])
                        st.dataframe(cols_df, use_container_width=True)
                    
                    sample_df = get_sample_data(st.session_state.db_engine, table_name, 5)
                    if not sample_df.empty:
                        with st.expander(f"Sample data from {table_name}"):
                            st.dataframe(sample_df, use_container_width=True)
                    
                    st.markdown("---")
    
    elif st.session_state.current_view == 'insights':
        # Database insights view
        st.subheader("💡 Database Insights")
        
        if st.session_state.db_engine:
            schema_info, total_records, error = get_database_info(st.session_state.db_engine)
            
            if not error:
                insights = generate_database_insights(st.session_state.db_engine, schema_info)
                
                for insight in insights:
                    st.info(insight)
                
                if schema_info:
                    st.write("**Table Sizes:**")
                    table_data = [
                        {'Table': name, 'Records': info['row_count'], 'Columns': len(info['columns'])}
                        for name, info in schema_info.items()
                    ]
                    table_df = pd.DataFrame(table_data).sort_values('Records', ascending=False)
                    st.dataframe(table_df, use_container_width=True)
    
    elif st.session_state.current_view == 'overview':
        # Data overview with visualization
        st.subheader("📈 Data Overview")
        
        if st.session_state.db_engine:
            schema_info, total_records, error = get_database_info(st.session_state.db_engine)
            
            if not error and schema_info:
                fig = create_data_overview_chart(schema_info)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                
                st.write("**Data Distribution:**")
                for table_name, table_info in schema_info.items():
                    percentage = (table_info['row_count'] / total_records * 100) if total_records > 0 else 0
                    st.write(f"• {table_name}: {table_info['row_count']:,} records ({percentage:.1f}%)")
    
    else:  # Default chat view
        # Main chat interface
        st.subheader("💬 Chat with Your Database")
        
        # Query suggestions with optimized prompts
        if st.session_state.db_engine:
            st.write("**💡 Try these queries:**")
            
            schema_info, _, _ = get_database_info(st.session_state.db_engine)
            table_names = list(schema_info.keys()) if schema_info else []
            
            # Optimized suggestions for lower token usage
            i = "give me the "
            if table_names:
                suggestions = [
                    f"Show all {table_names[0]} data",  # Simplified
                    "List table names",  # More efficient than "What tables do we have"
                    f"Count {table_names[0]} records" if table_names else "Count all records",
                    f"{i} Summary of database"  # Simplified
                ]
            else:
                suggestions = [
                    "List all tables",
                    "Summarise the database",
                    "Show database structure",
                    "Count total records"
                ]
            
            # Create clickable suggestion buttons
            cols = st.columns(2)
            for i, suggestion in enumerate(suggestions[:4]):
                with cols[i % 2]:
                    if st.button(f"💭 {suggestion}", key=f"suggestion_{i}", use_container_width=True):
                        # FIX: Prevent duplicate by checking if already processing
                        if 'process_query' not in st.session_state:
                            st.session_state['process_query'] = suggestion
                            st.rerun()
            
            st.markdown("---")
        
        # Display chat messages with proper formatting
        for message in st.session_state.messages:
            with st.chat_message(message['role']):
                st.write(message['content'])
                
                if message.get('sql_query'):
                    st.markdown("**🔍 Generated SQL Query:**")
                    st.code(message['sql_query'], language='sql')
                
                if message.get('dataframe') is not None:
                    st.subheader("📊 Query Results")
                    df = message['dataframe']
                    st.dataframe(df, use_container_width=True)
                    

                    numeric_cols = df.select_dtypes(include=['number']).columns
                    if len(numeric_cols) > 0 and len(df) > 1 and len(df) <= 50:
                        st.subheader("📈 Quick Visualization")
                        
                        if len(numeric_cols) >= 2:
                            fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1])
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            fig = px.bar(df.head(10), y=numeric_cols[0])
                            st.plotly_chart(fig, use_container_width=True)
                
                if message.get('execution_time'):
                    st.caption(f"⚡ Executed in {message['execution_time']:.3f} seconds")
        
        # Process queued query from suggestions - FIX to prevent duplicate
        if 'process_query' in st.session_state:
            user_input = st.session_state['process_query']
            del st.session_state['process_query']
            process_user_query(user_input, api_key)
        
        # Chat input for user queries
        user_input = st.chat_input("Ask me anything about your database...")
        
        if user_input:
            process_user_query(user_input, api_key)
    
    # Footer with performance analytics
    if st.session_state.analytics['total_queries'] > 0:
        st.markdown("---")
        st.subheader("📈 Session Analytics")
        
        analytics = st.session_state.analytics
        avg_response_time = analytics['total_response_time'] / analytics['total_queries']
        success_rate = (analytics['successful_queries'] / analytics['total_queries']) * 100
        
        metric_cols = st.columns(4)
        with metric_cols[0]:
            st.metric("Total Queries", analytics['total_queries'])
        with metric_cols[1]:
            st.metric("Successful Queries", analytics['successful_queries'])
        with metric_cols[2]:
            st.metric("Success Rate", f"{success_rate:.1f}%")
        with metric_cols[3]:
            st.metric("Avg Response Time", f"{avg_response_time:.2f}s")

if __name__ == "__main__":
    main()
