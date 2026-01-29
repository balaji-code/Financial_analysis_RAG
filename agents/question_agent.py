# This file implements a very simple AI "agent".
# An agent is a loop that:
# 1. Knows a goal (topic)
# 2. Remembers what it has learned (knowledge)
# 3. Decides what to do next (ask a question or stop)
# 4. Updates its memory based on the answer
# 5. Stops when it is done or reaches a safety limit

from openai import OpenAI
from dotenv import load_dotenv
import json
from pathlib import Path

load_dotenv()
client = OpenAI()

# Safety limit so the agent cannot run forever
MAX_STEPS = 5
step = 0

topic = "How companies manage risk"
knowledge = []
asked_questions = []

# Load long-term conceptual memory once (read → modify → write)
memory_path = Path("memory/conceptual_models.json")
if memory_path.exists():
    long_term_models = json.loads(memory_path.read_text())
else:
    long_term_models = []

# Check if a conceptual model already exists for this topic
existing_model = None
for entry in long_term_models:
    if entry["topic"].lower() == topic.lower():
        existing_model = entry["model"]
        break

# EARLY STOP CHECK:
# Ask whether the existing long-term model already fully answers the topic
should_stop_early = False

if existing_model:
    early_stop_prompt = f"""
    You are an analytical agent.

    Topic:
    {topic}

    Existing consolidated understanding:
    {existing_model}

    Does this model already provide a sufficient, end-to-end understanding
    of the topic for a knowledgeable user?

    Reply with only one word:
    YES or NO
    """

    decision = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": early_stop_prompt}],
        temperature=0
    ).choices[0].message.content.strip()

    if decision == "YES":
        should_stop_early = True

# Main agent loop: the agent thinks, acts, observes, and updates memory
if should_stop_early:
    print("\nEarly STOP: Existing long-term model already answers the topic.")
else:
    while step < MAX_STEPS:
        # The agent is explicitly shown any prior consolidated understanding
        # so it can avoid re-deriving what it already knows
        prompt = f"""
You are an analytical agent.

Topic: {topic}

Existing long-term understanding (if any):
{existing_model}

Short-term knowledge from this session:
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

        # SELF-CONSISTENCY CHECK:
        # Verify whether the extracted insight is internally coherent and well-formed
        consistency_prompt = f"""
You are an analytical agent reviewing a single insight.

Insight:
{insight}

Determine whether this insight is internally consistent, coherent,
and explains itself without contradiction or vague hand-waving.

Reply with only one word:
CONSISTENT or INCONSISTENT
"""

        consistency_decision = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": consistency_prompt}],
            temperature=0
        ).choices[0].message.content.strip()

        if consistency_decision == "INCONSISTENT":
            print("Insight rejected due to internal inconsistency.")
            asked_questions.append(content)
            step += 1
            continue

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

if should_stop_early:
    print("\nUsing existing consolidated mental model:")
    print(existing_model)
else:
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

    # Persist updated long-term memory exactly once at shutdown
    long_term_models.append({
        "topic": topic,
        "model": consolidated_model
    })

    memory_path.write_text(json.dumps(long_term_models, indent=2))