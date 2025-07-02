import os
import json
import logging
import google.generativeai as genai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.environ.get("API_KEY")

if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY environment variable not set in Netlify.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

def handler(event, context):
    logger.info('Netlify Function "explainSkill" processed a request.')
    headers = {
        "Access-Control-Allow-Origin": "*", # IMPORTANT: Restrict this in production
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Content-Type": "application/json"
    }

    if event['httpMethod'] == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers}

    try:
        body = json.loads(event['body'])
        skill_name = body.get('skill')
    except (json.JSONDecodeError, TypeError):
        logger.error("Request body is not valid JSON or missing.")
        return {'statusCode': 400, 'headers': headers, 'body': json.dumps({"explanation": "Please pass a JSON object with 'skill' in the request body."})}

    if not skill_name:
        logger.warning("No 'skill' provided in the request body.")
        return {'statusCode': 400, 'headers': headers, 'body': json.dumps({"explanation": "Please pass a 'skill' in the request body."})}

    if not GEMINI_API_KEY:
        logger.error("Gemini API Key is missing. Cannot process request.")
        return {'statusCode': 500, 'headers': headers, 'body': json.dumps({"explanation": "Server configuration error: Gemini API key not found."})}

    prompt = f"Explain what {skill_name} is in the context of data engineering, its main purpose, and a common use case. Keep it concise, around 2-3 sentences. Do not include any introductory or concluding phrases like 'Here's an explanation:' or 'In summary,'."

    try:
        response = model.generate_content(prompt)
        explanation = response.text
        logger.info(f"Generated explanation for {skill_name}: {explanation}")

        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({"explanation": explanation})
        }

    except Exception as e:
        logger.error(f"Error calling Gemini API for skill '{skill_name}': {e}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({"explanation": f"An error occurred while fetching the explanation for {skill_name}. Please try again later."})
        }
