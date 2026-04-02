"""
LLM Client for code generation
Supports placeholder mode and real LLM integration (Gemini/OpenAI)
"""
import os
import logging
import pandas as pd
from typing import Optional

logger = logging.getLogger(__name__)


def generate_code_for_question(
    question: str,
    dataset_path: str,
    context: Optional[str] = None,
    enable_visualization: bool = True
) -> str:
    """
    Generate pandas code to answer a question about a dataset
    
    Args:
        question: Natural language question
        dataset_path: Path to CSV dataset
        context: Additional context or constraints
        enable_visualization: Whether to generate visualizations
    
    Returns:
        Python code string
    """
    # Check if real LLM API keys are available
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    # Inspect dataset for context
    dataset_info = _inspect_dataset(dataset_path)
    
    if gemini_key and gemini_key != "your_gemini_api_key_here":
        logger.info("Using Gemini API for code generation")
        return _generate_with_gemini(question, dataset_info, context, enable_visualization)
    elif openai_key and openai_key != "your_openai_api_key_here":
        logger.info("Using OpenAI API for code generation")
        return _generate_with_openai(question, dataset_info, context, enable_visualization)
    else:
        logger.info("Using placeholder LLM (no API key configured)")
        return _generate_placeholder_code(question, dataset_info, enable_visualization)


def _inspect_dataset(dataset_path: str) -> dict:
    """Inspect dataset and return schema information"""
    try:
        df = pd.read_csv(dataset_path, nrows=100)  # Sample for inspection
        return {
            "columns": df.columns.tolist(),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "shape": df.shape,
            "sample": df.head(3).to_dict(orient="records")
        }
    except Exception as e:
        logger.error(f"Failed to inspect dataset: {e}")
        return {
            "columns": [],
            "dtypes": {},
            "shape": (0, 0),
            "sample": []
        }


def _generate_placeholder_code(question: str, dataset_info: dict, enable_visualization: bool = True) -> str:
    """
    Generate safe placeholder code for testing
    Returns deterministic, safe pandas code
    """
    columns = dataset_info.get("columns", [])
    
    # Determine if question is about time series, aggregation, or general analysis
    question_lower = question.lower()
    
    # Time-based analysis
    if any(word in question_lower for word in ["trend", "time", "monthly", "daily", "over time"]):
        date_col = next((col for col in columns if "date" in col.lower() or "time" in col.lower()), None)
        
        if date_col:
            return f"""import pandas as pd
import matplotlib.pyplot as plt

# Convert date column to datetime
df['{date_col}'] = pd.to_datetime(df['{date_col}'], errors='coerce')

# Group by month and count records
df['month'] = df['{date_col}'].dt.to_period('M')
monthly_data = df.groupby('month').size().reset_index(name='count')
monthly_data['month'] = monthly_data['month'].astype(str)

# Save results
monthly_data.to_csv('/tmp/result.csv', index=False)

# Create visualization
plt.figure(figsize=(12, 6))
plt.plot(range(len(monthly_data)), monthly_data['count'], marker='o')
plt.xlabel('Month')
plt.ylabel('Count')
plt.title('Monthly Trend Analysis')
plt.xticks(range(len(monthly_data)), monthly_data['month'], rotation=45, ha='right')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('/tmp/plot1.png', dpi=150, bbox_inches='tight')

print(f'Trend analysis complete: {{len(monthly_data)}} months analyzed')
print('Results saved to /tmp/result.csv and /tmp/plot1.png')
"""
    
    # Top N analysis
    elif any(word in question_lower for word in ["top", "best", "highest", "most"]):
        # Find a likely value column (numeric)
        value_col = next((col for col in columns if any(kw in col.lower() for kw in ["amount", "sales", "revenue", "price", "value", "total"])), columns[0] if columns else "value")
        group_col = next((col for col in columns if any(kw in col.lower() for kw in ["product", "category", "name", "type", "customer"])), columns[0] if len(columns) > 1 else "category")
        
        return f"""import pandas as pd
import matplotlib.pyplot as plt

# Find top 5 by aggregation
if '{value_col}' in df.columns and pd.api.types.is_numeric_dtype(df['{value_col}']):
    result = df.groupby('{group_col}')['{value_col}'].sum().sort_values(ascending=False).head(5)
else:
    # Fallback: count occurrences
    result = df['{group_col}'].value_counts().head(5)

# Convert to dataframe
result_df = pd.DataFrame({{
    '{group_col}': result.index,
    'value': result.values
}})
result_df.to_csv('/tmp/result.csv', index=False)

# Create bar chart
plt.figure(figsize=(10, 6))
plt.bar(range(len(result)), result.values)
plt.xlabel('{group_col}')
plt.ylabel('Value')
plt.title('Top 5 Analysis')
plt.xticks(range(len(result)), result.index, rotation=45, ha='right')
plt.tight_layout()
plt.savefig('/tmp/plot1.png', dpi=150, bbox_inches='tight')

print(f'Top 5 analysis complete: {{len(result)}} items')
print('Results saved to /tmp/result.csv and /tmp/plot1.png')
"""
    
    # Default: summary statistics
    else:
        return f"""import pandas as pd
import matplotlib.pyplot as plt

# Generate summary statistics
summary = df.describe(include='all').T
summary.to_csv('/tmp/result.csv')

# Create a sample of the first 10 rows
sample = df.head(10)
sample.to_csv('/tmp/result.csv', index=False)

# Create basic visualization
numeric_cols = df.select_dtypes(include=['number']).columns[:5]
if len(numeric_cols) > 0:
    fig, axes = plt.subplots(1, len(numeric_cols), figsize=(4*len(numeric_cols), 4))
    if len(numeric_cols) == 1:
        axes = [axes]
    
    for ax, col in zip(axes, numeric_cols):
        df[col].hist(ax=ax, bins=20)
        ax.set_title(col)
        ax.set_xlabel('Value')
        ax.set_ylabel('Frequency')
    
    plt.tight_layout()
    plt.savefig('/tmp/plot1.png', dpi=150, bbox_inches='tight')

print(f'Dataset analysis complete: {{len(df)}} rows, {{len(df.columns)}} columns')
print('Results saved to /tmp/result.csv')
if len(numeric_cols) > 0:
    print('Visualizations saved to /tmp/plot1.png')
"""


def _generate_with_gemini(question: str, dataset_info: dict, context: Optional[str] = None, enable_visualization: bool = True) -> str:
    """
    Generate code using Google Gemini API
    
    TODO: Implement when Gemini API key is configured
    
    Example implementation:
    ```python
    import google.generativeai as genai
    
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = _build_prompt(question, dataset_info, context)
    response = model.generate_content(prompt)
    
    # Extract code from response
    code = _extract_code_from_response(response.text)
    return code
    ```
    """
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        # Use gemini-2.0-flash (latest stable model)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = _build_prompt(question, dataset_info, context, enable_visualization)
        response = model.generate_content(prompt)
        
        # Extract code from markdown code blocks
        code = _extract_code_from_response(response.text)
        return code
    
    except Exception as e:
        logger.error(f"Gemini API call failed: {e}")
        logger.info("Falling back to placeholder code")
        return _generate_placeholder_code(question, dataset_info, enable_visualization)


def _generate_with_openai(question: str, dataset_info: dict, context: Optional[str] = None, enable_visualization: bool = True) -> str:
    """
    Generate code using OpenAI API
    
    TODO: Implement when OpenAI API key is configured
    
    Example implementation:
    ```python
    from openai import OpenAI
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    prompt = _build_prompt(question, dataset_info, context)
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a pandas code generator..."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    
    code = _extract_code_from_response(response.choices[0].message.content)
    return code
    ```
    """
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        system_prompt = """You are an expert Python data analyst. Generate ONLY pandas/numpy/matplotlib code.
Rules:
1. Dataframe is already loaded as 'df'
2. Save results to /tmp/result.csv
3. Save plots to /tmp/plot1.png, /tmp/plot2.png, etc.
4. Use error handling
5. Add informative print statements
6. NO imports other than pandas, numpy, matplotlib
"""
        
        user_prompt = _build_prompt(question, dataset_info, context, enable_visualization)
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3
        )
        
        code = _extract_code_from_response(response.choices[0].message.content)
        return code
    
    except Exception as e:
        logger.error(f"OpenAI API call failed: {e}")
        logger.info("Falling back to placeholder code")
        return _generate_placeholder_code(question, dataset_info, enable_visualization)


def _build_prompt(question: str, dataset_info: dict, context: Optional[str] = None, enable_visualization: bool = True) -> str:
    """Build the prompt for LLM"""
    columns = dataset_info.get("columns", [])
    dtypes = dataset_info.get("dtypes", {})
    sample = dataset_info.get("sample", [])
    
    visualization_instruction = ""
    if enable_visualization:
        visualization_instruction = """
6. Create visualization ONLY if it makes sense for the question
7. Visualization should be relevant to the specific question (not generic histograms)
8. Save relevant visualization to /tmp/plot1.png (ONLY if visualization adds value)
"""
    else:
        visualization_instruction = """
6. DO NOT create any visualizations (user disabled visualization)
7. Skip matplotlib imports and plotting code
8. Focus only on data analysis and results
"""
    
    prompt = f"""Generate Python pandas code to answer this SPECIFIC question about a dataset:

Question: {question}

Dataset Information:
- Columns: {', '.join(columns)}
- Data types: {dtypes}
- Sample rows (first 2): {sample[:2]}

CRITICAL Requirements:
1. The dataframe is already loaded as variable 'df'
2. Answer the EXACT question asked - don't generate generic analysis
3. If question asks for filtering (e.g., "products with value > 1000"), filter the data
4. If question asks for specific columns, return only those columns
5. Save the FILTERED/PROCESSED results to /tmp/result.csv (NOT the entire dataset)
{visualization_instruction}
9. For numeric comparisons, ensure proper data type conversion if needed
10. Handle commas in numbers (e.g., "1,000" should be treated as 1000)
11. Print clear summary of what was found

Output Requirements:
- Save results to /tmp/result.csv
- Use ONLY: pandas (import pandas as pd){', matplotlib' if enable_visualization else ''}
- DO NOT import numpy unless absolutely necessary
- NO try-except blocks (code should be simple and direct)
- Print informative messages showing the results (use print statements)
- Print the final DataFrame/results so users can see the answer

{f'Additional context: {context}' if context else ''}

Examples of good responses:
- "list products with order_value > 1000" → Filter df[df['order_value'] > 1000], print results, save filtered data{', create bar chart' if enable_visualization else ''}
- "show trend over time" → Group by date, aggregate, print results{', create line plot' if enable_visualization else ''}
- "top 5 products" → Group, sum, sort, head(5), print results{', create bar chart' if enable_visualization else ''}

IMPORTANT: Always print the results/answer so the user can see them immediately!

Return ONLY the Python code that directly answers the question, no explanations.
"""
    return prompt


def _extract_code_from_response(response_text: str) -> str:
    """Extract Python code from LLM response (handles markdown code blocks)"""
    # Remove markdown code block markers
    code = response_text.strip()
    
    # Handle ```python ... ``` format
    if code.startswith("```python"):
        code = code[9:]
    elif code.startswith("```"):
        code = code[3:]
    
    if code.endswith("```"):
        code = code[:-3]
    
    return code.strip()
