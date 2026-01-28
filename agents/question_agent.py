# This file implements a very simple AI "agent".
# An agent is a loop that:
# 1. Knows a goal (topic)
# 2. Remembers what it has learned (knowledge)
# 3. Decides what to do next (ask a question or stop)
# 4. Updates its memory based on the answer
# 5. Stops when it is done or reaches a safety limit

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

# Safety limit so the agent cannot run forever
MAX_STEPS = 5
step = 0

topic = "How companies manage risk"
knowledge = []
asked_questions = []

# Main agent loop: the agent thinks, acts, observes, and updates memory
while step < MAX_STEPS:
    prompt = f"""
You are an analytical agent.

Topic: {topic}

What you already know:
{knowledge}

Questions already asked:
{asked_questions}

Decide the SINGLE best next question to ask.
Also explain briefly WHY this question is important.
Format:
QUESTION: <question>
REASON: <reason>
If no more questions are needed, reply with: STOP
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    output = response.choices[0].message.content.strip()

    # If the agent decides it has learned enough, stop the loop
    if output == "STOP":
      break

    question = output.split("QUESTION:")[1].split("REASON:")[0].strip()
    reason = output.split("REASON:")[1].strip()  

   
    print("\nAgent asks:", question)
    print("Reason:", reason)

    # Ask the chosen question to the "environment" (here, another LLM call)
    answer = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": question}],
        temperature=0
    ).choices[0].message.content

    # Update the agent's memory with the new information
    knowledge.append(answer)
    asked_questions.append(question)

    # Increment step counter to avoid infinite loops
    step += 1

# Print everything the agent has learned during the loop
print("\nFinal understanding:")
for k in knowledge:
    print("-", k)