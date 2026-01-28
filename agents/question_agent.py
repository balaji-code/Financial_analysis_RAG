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

Decide the SINGLE best next action.

You can choose ONE of the following actions:
1. ASK: ask a new question
2. SEARCH: search existing knowledge using a tool
3. STOP: if understanding is sufficient
If you have not yet built any understanding, prefer ASK over SEARCH.
Format:
ACTION: <ASK | SEARCH | STOP>
CONTENT: <question or search query>
REASON: <why this action is chosen>
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

    action = output.split("ACTION:")[1].split("\n")[0].strip()
    content = output.split("CONTENT:")[1].split("\n")[0].strip()
    reason = output.split("REASON:")[1].strip()

    print(f"\nAgent action: {action}")
    print("Reason:", reason)

    # Ask the chosen question to the "environment" (here, another LLM call)
    if action == "ASK":
       answer = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": content}],
        temperature=0
    ).choices[0].message.content

    # The agent may choose SEARCH even in the first step if the prompt
    # suggests that searching existing knowledge is preferable to asking.
    # This is a rational choice made by the LLM, not a bug.
    elif action == "SEARCH":
     from .tools import search_risks
     results = search_risks(content)
     answer = f"Search results: {results}"

    else:
      break

    # Update the agent's memory with the new information
    # Ask the LLM to extract the key insight worth remembering
    # Compose an LLM prompt to extract a distilled insight from the answer
    insight_prompt = f"""
    You are an analytical agent.

    Original question:
    {content}

    Answer received:
    {answer}

    Extract the SINGLE most important insight that should be remembered.
    Be concise (1-2 sentences).
    """

    # Get the concise insight from the LLM
    insight = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": insight_prompt}],
        temperature=0
    ).choices[0].message.content.strip()

    # MEMORY EVALUATION STEP:
    # The agent checks whether a new insight adds value or is redundant
    # Decide whether this insight is genuinely new or already covered
    memory_check_prompt = f"""
    You are an analytical agent reviewing your own memory.

    Existing knowledge:
    {knowledge}

    New insight:
    {insight}

    Decide whether the new insight adds something genuinely NEW.
    Reply with only one word:
    NEW or REDUNDANT
    """

    memory_decision = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": memory_check_prompt}],
        temperature=0
    ).choices[0].message.content.strip()

    if memory_decision == "NEW":
        knowledge.append(insight)
    else:
        print("Insight ignored as redundant.")

    asked_questions.append(content)
  
    # Increment step counter to avoid infinite loops
    step += 1

# Print everything the agent has learned during the loop
print("\nRaw learned insights:")
for k in knowledge:
    print("-", k)

# This step compresses multiple related insights into a single abstract model,
# mirroring how human analysts move from details to frameworks.

# CONSOLIDATION STEP:
# Ask the agent to synthesize all stored insights into a higher-level model
consolidation_prompt = f"""
You are an expert analyst.

Below are several insights about a topic. These insights may describe
different parts of the same underlying system.

Insights:
{knowledge}

Synthesize these into a SINGLE coherent higher-level model or framework.
- Do NOT repeat the insights verbatim.
- Capture the core structure or loop they describe.
- Be concise (3–5 sentences).
"""

consolidated_model = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[{"role": "user", "content": consolidation_prompt}],
    temperature=0
).choices[0].message.content.strip()

print("\nConsolidated mental model:")
print(consolidated_model)