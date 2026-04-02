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
    import re

    columns = dataset_info.get("columns", [])
    dtypes = dataset_info.get("dtypes", {})
    question_lower = (question or "").lower().strip()

    def _norm(s: str) -> str:
        return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()

    norm_cols = {col: _norm(col) for col in columns}

    numeric_name_keywords = [
        "sales",
        "revenue",
        "amount",
        "value",
        "total",
        "price",
        "cost",
        "profit",
        "order_value",
        "quantity",
        "qty",
    ]

    def _is_numeric_like(col: str) -> bool:
        dt = str(dtypes.get(col, "")).lower()
        if any(k in dt for k in ["int", "float", "double", "number", "decimal"]):
            return True
        cl = col.lower()
        return any(kw in cl for kw in numeric_name_keywords)

    def _find_col_in_question() -> str | None:
        q = " " + _norm(question_lower) + " "
        for col, ncol in norm_cols.items():
            if not ncol:
                continue
            if f" {ncol} " in q:
                return col
        return None

    def _pick_numeric_col() -> str | None:
        numeric = []
        numeric_like = []
        for col in columns:
            dt = str(dtypes.get(col, "")).lower()
            if any(k in dt for k in ["int", "float", "double", "number", "decimal"]):
                numeric.append(col)
            elif any(kw in col.lower() for kw in numeric_name_keywords):
                numeric_like.append(col)
        # Heuristic: prefer common value columns
        preferred_keywords = ["sales", "revenue", "amount", "value", "total", "price", "cost", "profit", "order_value"]
        for kw in preferred_keywords:
            for col in numeric:
                if kw in col.lower():
                    return col
            for col in numeric_like:
                if kw in col.lower():
                    return col
        return numeric[0] if numeric else (numeric_like[0] if numeric_like else None)

    def _pick_group_col() -> str | None:
        # Look for "by <col>" / "per <col>" patterns
        q = _norm(question_lower)
        m = re.search(r"\b(by|per)\b\s+([a-z0-9_ ]+)", q)
        if m:
            tail = m.group(2)
            for col, ncol in norm_cols.items():
                if ncol and ncol in tail:
                    # If the "by" column is numeric-like, it's probably a metric (e.g., "top products by sales")
                    if _is_numeric_like(col):
                        break
                    return col
        # Prefer common categorical columns
        preferred_keywords = ["product", "category", "customer", "name", "type", "region", "city", "state"]
        for kw in preferred_keywords:
            for col in columns:
                if kw in col.lower():
                    return col
        # Fallback: first non-numeric
        non_numeric = []
        non_numeric_non_metric = []
        for col in columns:
            dt = str(dtypes.get(col, "")).lower()
            if not any(k in dt for k in ["int", "float", "double", "number", "decimal"]):
                non_numeric.append(col)
                if not _is_numeric_like(col):
                    non_numeric_non_metric.append(col)
        if non_numeric_non_metric:
            return non_numeric_non_metric[0]
        if non_numeric:
            return non_numeric[0]
        return None

    def _pick_date_col() -> str | None:
        preferred = ["date", "time", "timestamp", "created", "order_date"]
        for kw in preferred:
            for col in columns:
                if kw in col.lower():
                    return col
        return None

    def _parse_top_n() -> int:
        m = re.search(r"\btop\s+(\d+)\b", question_lower)
        if m:
            try:
                n = int(m.group(1))
                return max(1, min(n, 50))
            except Exception:
                pass
        return 5

    def _parse_comparison() -> tuple[str, str, float] | None:
        # Very simple parser: "<col> > 1000" / "greater than 1000" etc.
        q = question_lower.replace(",", "")
        op_map = {
            "greater than": ">",
            "more than": ">",
            "less than": "<",
            "below": "<",
            "under": "<",
            "at least": ">=",
            "at most": "<=",
        }
        for phrase, op in op_map.items():
            if phrase in q:
                m = re.search(rf"{re.escape(phrase)}\s+(-?\d+(?:\.\d+)?)", q)
                if m:
                    val = float(m.group(1))
                    col = _find_col_in_question() or _pick_numeric_col()
                    if col:
                        return col, op, val
        m = re.search(r"\b([a-zA-Z0-9_]+)\s*(<=|>=|<|>)\s*(-?\d+(?:\.\d+)?)", q)
        if m:
            token = _norm(m.group(1))
            op = m.group(2)
            val = float(m.group(3))
            col = None
            for c, ncol in norm_cols.items():
                if ncol == token:
                    col = c
                    break
            col = col or _pick_numeric_col()
            if col:
                return col, op, val
        return None

    value_col = _pick_numeric_col()
    group_col = _pick_group_col()
    date_col = _pick_date_col()
    comparison = _parse_comparison()

    wants_trend = any(w in question_lower for w in ["trend", "over time", "monthly", "daily", "by date", "time series"])
    wants_top = any(w in question_lower for w in ["top", "highest", "most", "best"])
    wants_sum = any(w in question_lower for w in ["total", "sum"])
    wants_avg = any(w in question_lower for w in ["average", "avg", "mean"])
    wants_count = any(w in question_lower for w in ["count", "how many", "number of"])

    # Interpret "top ... by <metric>" as top by sum/avg of that metric when possible
    if wants_top and not (wants_sum or wants_avg):
        qn = _norm(question_lower)
        m = re.search(r"\btop\b\s+\d+\b.*\bby\b\s+([a-z0-9_ ]+)", qn)
        if m:
            tail = m.group(1)
            metric_col = None
            for col, ncol in norm_cols.items():
                if ncol and ncol in tail:
                    metric_col = col
                    break
            if metric_col and _is_numeric_like(metric_col):
                value_col = metric_col
                wants_sum = True

    if not columns:
        return """import pandas as pd

print('No columns detected in dataset inspection.')
df.head(10).to_csv('/tmp/result.csv', index=False)
print('Saved first 10 rows to /tmp/result.csv')
"""

    # Build filter clause if requested
    filter_lines = ""
    df_name = "df"
    if comparison and value_col:
        c, op, val = comparison
        df_name = "df_filtered"
        filter_lines = f"""\n# Filter rows based on the question\ndf_filtered = df.copy()\ndf_filtered['{c}'] = pd.to_numeric(df_filtered['{c}'].astype(str).str.replace(',', ''), errors='coerce')\ndf_filtered = df_filtered[df_filtered['{c}'] {op} {val}]\n"""

    # Trend over time
    if wants_trend and date_col:
        agg_expr = ".size()"
        agg_name = "count"
        if value_col and (wants_sum or wants_avg):
            agg_expr = f"['{value_col}'].sum()" if wants_sum else f"['{value_col}'].mean()"
            agg_name = "total" if wants_sum else "average"

        value_convert_lines = ""
        if value_col and (wants_sum or wants_avg):
            value_convert_lines = (
                f"_df['{value_col}'] = pd.to_numeric(_df['{value_col}'].astype(str).str.replace(',', ''), errors='coerce')\n"
            )

        plot_block = ""
        if enable_visualization:
            plot_block = f"""\nimport matplotlib.pyplot as plt\n\nplt.figure(figsize=(12, 6))\nplt.plot(result_df['period'].astype(str), result_df['{agg_name}'], marker='o')\nplt.xticks(rotation=45, ha='right')\nplt.title('Trend over time')\nplt.tight_layout()\nplt.savefig('/tmp/plot1.png', dpi=150, bbox_inches='tight')\nprint('Saved plot to /tmp/plot1.png')\n"""

        return f"""import pandas as pd
{plot_block if False else ''}
{filter_lines}
# Parse date column and aggregate by month
_df = {df_name}
{value_convert_lines}
_df['{date_col}'] = pd.to_datetime(_df['{date_col}'], errors='coerce')
_df = _df.dropna(subset=['{date_col}'])
_df['period'] = _df['{date_col}'].dt.to_period('M')

result = _df.groupby('period'){agg_expr}
result_df = result.reset_index(name='{agg_name}')
result_df['period'] = result_df['period'].astype(str)

result_df.to_csv('/tmp/result.csv', index=False)
print('Saved results to /tmp/result.csv')
print(result_df)
""" + (plot_block if enable_visualization else "")

    # Top N
    if wants_top and group_col:
        n = _parse_top_n()
        metric = "count"
        value_convert_lines = ""
        if value_col and (wants_sum or wants_avg):
            value_convert_lines = (
                f"_df['{value_col}'] = pd.to_numeric(_df['{value_col}'].astype(str).str.replace(',', ''), errors='coerce')\n"
            )

        if value_col and wants_sum:
            metric = "total"
            result_series_expr = (
                f"_df.groupby('{group_col}', dropna=False)['{value_col}'].sum().sort_values(ascending=False)"
            )
        elif value_col and wants_avg:
            metric = "average"
            result_series_expr = (
                f"_df.groupby('{group_col}', dropna=False)['{value_col}'].mean().sort_values(ascending=False)"
            )
        else:
            result_series_expr = f"_df['{group_col}'].value_counts(dropna=False)"

        plot_block = ""
        if enable_visualization:
            plot_block = f"""\nimport matplotlib.pyplot as plt\n\nplt.figure(figsize=(10, 6))\nplt.bar(result_df['{group_col}'].astype(str), result_df['{metric}'])\nplt.xticks(rotation=45, ha='right')\nplt.title('Top {n} by {metric}')\nplt.tight_layout()\nplt.savefig('/tmp/plot1.png', dpi=150, bbox_inches='tight')\nprint('Saved plot to /tmp/plot1.png')\n"""

        return f"""import pandas as pd
{filter_lines}

_df = {df_name}
{value_convert_lines}result_series = {result_series_expr}.head({n})

result_df = result_series.reset_index()
result_df.columns = ['{group_col}', '{metric}']

result_df.to_csv('/tmp/result.csv', index=False)
print('Saved results to /tmp/result.csv')
print(result_df)
""" + (plot_block if enable_visualization else "")

    # Aggregate / answer
    if group_col and value_col and (wants_sum or wants_avg):
        agg_func = "sum" if wants_sum else "mean"
        metric = "total" if wants_sum else "average"
        return f"""import pandas as pd
{filter_lines}

_df = {df_name}
_df['{value_col}'] = pd.to_numeric(_df['{value_col}'].astype(str).str.replace(',', ''), errors='coerce')
result_df = _df.groupby('{group_col}', dropna=False)['{value_col}'].{agg_func}().reset_index(name='{metric}')
result_df = result_df.sort_values('{metric}', ascending=False)

result_df.to_csv('/tmp/result.csv', index=False)
print('Saved results to /tmp/result.csv')
print(result_df)
"""

    if value_col and wants_sum:
        return f"""import pandas as pd
{filter_lines}

_df = {df_name}
_df['{value_col}'] = pd.to_numeric(_df['{value_col}'].astype(str).str.replace(',', ''), errors='coerce')
total_val = _df['{value_col}'].sum()
result_df = pd.DataFrame([{{'{value_col}_sum': total_val}}])
result_df.to_csv('/tmp/result.csv', index=False)
print('Saved results to /tmp/result.csv')
print(result_df)
"""

    if wants_count:
        return f"""import pandas as pd
{filter_lines}

_df = {df_name}
result_df = pd.DataFrame([{{'count': int(len(_df))}}])
result_df.to_csv('/tmp/result.csv', index=False)
print('Saved results to /tmp/result.csv')
print(result_df)
"""

    # Fallback: return the first 20 rows (still question-aware: filtered if requested)
    preview_cols = columns[: min(6, len(columns))]
    return f"""import pandas as pd
{filter_lines}

_df = {df_name}
result_df = _df[{preview_cols!r}].head(20)
result_df.to_csv('/tmp/result.csv', index=False)
print('Saved results to /tmp/result.csv')
print(result_df)
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
