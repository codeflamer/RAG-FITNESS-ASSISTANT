
import ingest
from mistralai import Mistral
import time
from dotenv import load_dotenv
import os
import json

load_dotenv()


model = "mistral-medium-latest"

api_key = os.getenv('MISTRAL_KEY',"Your_mistral_apikey")

mistral_client = Mistral(api_key=api_key)

index = ingest.ingest_data()

def minsearch_improved(query):
    boost = {
        'exercise_name': 2.11,
        'type_of_activity': 1.46,
        'type_of_equipment': 0.65,
        'body_part': 2.65,
        'type': 1.31,
        'muscle_groups_activated': 2.54,
        'instructions': 0.74
    }

    results = index.search(
        query=query,
        filter_dict={},
        boost_dict=boost,
        num_results=10
    )

    return results

prompt_template = """
You're a fitness instructor. Answer the QUESTION based on the CONTEXT from our exercises database.
Use only the facts from the CONTEXT when answering the QUESTION.

QUESTION: {question}

CONTEXT: 
{context}
""".strip()

entry_template = """
exercise_name: {exercise_name}
type_of_activity: {type_of_activity}
type_of_equipment: {type_of_equipment}
body_part: {body_part}
type: {type}
muscle_groups_activated: {muscle_groups_activated}
instructions: {instructions}
""".strip()

def build_prompts(query, search_results):    
    context = ""
    
    for doc in search_results:
        context += entry_template.format(**doc) + "\n\n"
    
    prompt = prompt_template.format(question=query, context=context).strip()

    return prompt


def llm(prompt):
    response = mistral_client.chat.complete(
        model=model,
        messages=[
                {
                    "role":"user",
                    "content":prompt
                }
            ]
    )

    answer = response.choices[0].message.content
    tokens = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_token": response.usage.total_tokens
    }

    return answer,tokens


evaluation_prompt_template = """
You are an expert evaluator for a RAG system.
Your task is to analyze the relevance of the generated answer to the given question.
Based on the relevance of the generated answer, you will classify it
as "NON_RELEVANT", "PARTLY_RELEVANT", or "RELEVANT".

Here is the data for evaluation:

Question: {question}
Generated Answer: {answer}

Please analyze the content and context of the generated answer in relation to the question
and provide your evaluation in parsable JSON without using code blocks:
- remember no json syntax
- just return responses that are parsable

{{
  "Relevance": "NON_RELEVANT" | "PARTLY_RELEVANT" | "RELEVANT",
  "Explanation": "[Provide a brief explanation for your evaluation]"
}}
""".strip()

def evaluate_relevance(question, answer):
    prompt = evaluation_prompt_template.format(question=question, answer=answer)
    evaluation, tokens = llm(prompt)

    try:
        json_eval = json.loads(evaluation)
        return json_eval, tokens
    except json.JSONDecodeError:
        result = {"Relevance": "UNKNOWN", "Explanation": "Failed to parse evaluation"}
        return result, tokens


def rag(query):   
    t0 = time.time()
    results = minsearch_improved(query)
    prompt = build_prompts(query, results)
    answer, tokens = llm(prompt)
    t1 = time.time()
    took = t1-t0

    relevance, rel_token_stats = evaluate_relevance(query, answer)


    answer_data = {
        "answer":answer,
        "model_used":"mistral-medium-latest",
        "response_time":took,
        "relevance":relevance.get("Relevance","UNKNOWN"),
        "relevance_explanation":relevance.get("Explanation", "Failed to parse evaluation"),
        "prompt_tokens":tokens["prompt_tokens"],
        "completion_tokens": tokens["completion_tokens"],
        "total_tokens": tokens["total_token"],
        "eval_prompt_tokens":rel_token_stats["prompt_tokens"],
        "eval_completion_tokens":rel_token_stats["completion_tokens"],
        "eval_total_tokens":rel_token_stats["total_token"],
        "mistralai_cost":0,
    }

    return answer_data