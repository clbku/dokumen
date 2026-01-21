import os
from crewai import Agent, Task, Crew, LLM
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_llm(provider):
    """
    Factory function to get an LLM instance based on the provider name.
    """
    provider = provider.lower()
    
    if provider == "zai":
        # Z.AI via OpenAI compatible interface
        api_key = os.getenv("OPENAI_API_KEY") # Z.AI uses the same key var usually, or specific one
        base_url = os.getenv("OPENAI_API_BASE")
        if not base_url:
             print("Warning: OPENAI_API_BASE not found for Z.AI.")
        return LLM(
            model="glm-4.7", # Replace with actual Z.AI model
            base_url=base_url,
            api_key=api_key
        )

    elif provider == "google":
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
             print("Warning: GOOGLE_API_KEY not found.")
        return LLM(
            model="gemini/gemini-3-flash-preview",
            api_key=api_key
        )
    
    else:
        raise ValueError(f"Unknown provider: {provider}")

def main():
    try:
        print("Initializing Agents with different providers...")
        
        # 1. Define LLMs
        # You can swap these providers based on your .env configuration
        llm_openai = get_llm("zai")
        llm_google = get_llm("google") 

        # 2. Define Agents
        # Agent A uses OpenAI
        agent_a = Agent(
            role='OpenAI Representative',
            goal='Introduce yourself and your underlying model',
            backstory='You are an AI assistant powered by OpenAI.',
            verbose=True,
            memory=False,
            llm=llm_openai
        )

        # Agent B uses Google Gemini
        agent_b = Agent(
            role='Google Gemini Representative',
            goal='Introduce yourself and your underlying model',
            backstory='You are an AI assistant powered by Google Gemini.',
            verbose=True,
            memory=False,
            llm=llm_google
        )

        # 3. Define Tasks
        task_a = Task(
            description='Say hello and state which model provider you are using.',
            expected_output='A greeting from the OpenAI agent.',
            agent=agent_a,
        )

        task_b = Task(
            description='Say hello and state which model provider you are using. Also compliment the other agent.',
            expected_output='A greeting from the Google agent.',
            agent=agent_b,
        )

        # 4. Define Crew
        crew = Crew(
            agents=[agent_a, agent_b],
            tasks=[task_a, task_b],
            process='sequential'
        )

        # 5. Kickoff
        result = crew.kickoff()
        print("\n########################\n")
        print("Crew Execution Result:")
        print(result)
        print("\n########################\n")

    except Exception as e:
        print(f"Error during execution: {e}")

if __name__ == "__main__":
    main()
