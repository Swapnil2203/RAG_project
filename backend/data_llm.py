from fastapi import FastAPI, HTTPException
import openai
import os
from dotenv import load_dotenv

load_dotenv()

class DataLLM:
    openai_client = openai.AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION")
    )

    @staticmethod
    def query_openai(question: str, context: str):
        try:
            response = DataLLM.openai_client.chat.completions.create(
                model="gpt-35-turbo",
                messages = [
                    {
                        "role": "system",
                        "content": (
                            "You are an AI assistant specialized in survey data analysis. "
                            "Use the provided context to derive insights, make comparisons, and summarize key findings. "
                            "Provide an informative and concise response, including numerical data where appropriate. "
                            "Avoid dataset IDs and instead focus on aggregated insights that help understand the overall trends."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"Use the following context to provide insights: {context}. Question: {question}"
                    }
                ],



                max_tokens=150,
                temperature=0.7,
                n=1
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"OpenAI error: {str(e)}")


# Example usage:
if __name__ == "__main__":
    data_llm = DataLLM()
    question = "What are the top festive brands during Christmas?"
    context = "The top festive brands in the supermarket are Coca Cola, Cadbury, and Lindt. People prefer buying these brands especially during holiday seasons."

    try:
        response = data_llm.query_openai(question, context)
        print("Response from OpenAI: {}".format(response))
    except HTTPException as http_exc:
        print("Error: {}".format(http_exc.detail))