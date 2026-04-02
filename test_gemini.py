import os


def main() -> None:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key in {"your_gemini_api_key_here", "your_actual_key", "your_actual_key_here"}:
        raise SystemExit(
            "GEMINI_API_KEY is not set. Set it in your environment (or a local .env) to run this script."
        )

    try:
        import google.generativeai as genai
    except Exception as e:
        raise SystemExit(
            "google-generativeai is not installed. Install it to run this script: pip install google-generativeai"
        ) from e

    print(f"Testing Gemini API key: {api_key[:8]}...")

    try:
        genai.configure(api_key=api_key)

        print("\nTrying model: gemini-2.0-flash")
        model = genai.GenerativeModel("gemini-2.0-flash")

        prompt = """Generate Python pandas code to answer this SPECIFIC question about a dataset:

Question: list products with order value greater than 1000

Dataset Information:
- Columns: order_id, customer_name, product_name, order_value, order_date
- Data types: {'order_id': 'int64', 'customer_name': 'object', 'product_name': 'object', 'order_value': 'int64', 'order_date': 'object'}

CRITICAL Requirements:
1. The dataframe is already loaded as variable 'df'
2. Answer the EXACT question asked - don't generate generic analysis
3. Filter df[df['order_value'] > 1000]
4. Save the FILTERED results to /tmp/result.csv (NOT the entire dataset)
5. DO NOT create any visualizations (user disabled visualization)
6. Print clear summary of what was found

Return ONLY the Python code, no explanations.
"""

        response = model.generate_content(prompt)
        print("✅ SUCCESS with gemini-2.0-flash\n")
        print(f"Generated code:\n{response.text}\n")

    except Exception as e:
        print(f"❌ API Test Failed: {e}")


if __name__ == "__main__":
    main()
