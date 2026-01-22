import os
import argparse
from crewai import Agent, Task, Crew, LLM
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import hierarchical workflow components
from src.workflows import (
    HierarchicalWorkflow,
    HierarchicalWorkflowConfig,
    execute_hierarchical_workflow,
)


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

def run_hierarchical_workflow(
    user_requirement: str,
    manager_llm_provider: str = "google",
    manager_llm_model: str = "gemini/gemini-3-pro-preview",
    num_auditors: int = 1,
    verbose: bool = True,
    memory: bool = True,
):
    """
    Run hierarchical workflow with Manager Agent coordinating workers.

    Args:
        user_requirement: Feature description from user
        manager_llm_provider: LLM provider for Manager agent (default: "google")
        manager_llm_model: Model name for Manager agent
        num_auditors: Number of auditor agents to create (default: 1)
        verbose: Enable verbose logging (default: True)
        memory: Enable agent memory (default: True)

    Returns:
        Dict containing execution results
    """
    print("\n" + "="*60)
    print("HIERARCHICAL WORKFLOW MODE")
    print("="*60)
    print(f"User Requirement: {user_requirement}")
    print(f"Manager LLM: {manager_llm_provider} ({manager_llm_model})")
    print(f"Number of Auditors: {num_auditors}")
    print("="*60 + "\n")

    # Create configuration
    config = HierarchicalWorkflowConfig(
        manager_llm_provider=manager_llm_provider,
        manager_llm_model=manager_llm_model,
        verbose=verbose,
        memory=memory,
    )

    # Execute workflow
    result = execute_hierarchical_workflow(
        user_requirement=user_requirement,
        config=config,
        num_auditors=num_auditors,
    )

    # Print results
    print("\n" + "="*60)
    print("WORKFLOW EXECUTION COMPLETE")
    print("="*60)
    print(f"Tasks executed: {result.get('num_tasks', 'N/A')}")
    print(f"Auditors used: {result.get('num_auditors', 'N/A')}")
    print("="*60 + "\n")

    return result


def main():
    """
    Main entry point with CLI argument parsing.

    Supports two modes:
    - sequential: Original sequential workflow (backward compatible)
    - hierarchical: New hierarchical workflow with Manager Agent
    """
    parser = argparse.ArgumentParser(
        description="Deep-Spec AI: Multi-agent technical design system"
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["sequential", "hierarchical"],
        default="hierarchical",
        help="Workflow mode: 'sequential' (original) or 'hierarchical' (Manager-coordinated)",
    )
    parser.add_argument(
        "requirement",
        nargs="?",
        help="User requirement / feature description",
    )
    parser.add_argument(
        "--manager-llm",
        type=str,
        default="google",
        help="Manager LLM provider (default: google)",
    )
    parser.add_argument(
        "--manager-model",
        type=str,
        default="gemini/gemini-3-pro-preview",
        help="Manager LLM model (default: gemini/gemini-3-pro-preview)",
    )
    parser.add_argument(
        "--num-auditors",
        type=int,
        default=1,
        help="Number of auditor agents for hierarchical mode (default: 1)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=True,
        help="Enable verbose logging (default: True)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Disable verbose logging",
    )

    args = parser.parse_args()

    # Handle verbosity
    verbose = args.verbose and not args.quiet

    # Default requirement if not provided
    if args.requirement is None:
        args.requirement = "User authentication with email and password"

    try:
        if args.mode == "hierarchical":
            # Run hierarchical workflow
            result = run_hierarchical_workflow(
                user_requirement=args.requirement,
                manager_llm_provider=args.manager_llm,
                manager_llm_model=args.manager_model,
                num_auditors=args.num_auditors,
                verbose=verbose,
            )
        else:
            # Run sequential workflow (original behavior)
            run_original_sequential(args.requirement, verbose)

    except Exception as e:
        print(f"Error during execution: {e}")
        raise


def run_original_sequential(requirement: str, verbose: bool = True):
    """Original sequential workflow (for backward compatibility)."""
    print("\n" + "="*60)
    print("SEQUENTIAL WORKFLOW MODE (Original)")
    print("="*60)
    print(f"User Requirement: {requirement}")
    print("="*60 + "\n")

    print("Initializing Agents with different providers...")

    # 1. Define LLMs
    llm_openai = get_llm("zai")
    llm_google = get_llm("google")

    # 2. Define Agents
    agent_a = Agent(
        role='OpenAI Representative',
        goal='Introduce yourself and your underlying model',
        backstory='You are an AI assistant powered by OpenAI.',
        verbose=verbose,
        memory=False,
        llm=llm_openai
    )

    agent_b = Agent(
        role='Google Gemini Representative',
        goal='Introduce yourself and your underlying model',
        backstory='You are an AI assistant powered by Google Gemini.',
        verbose=verbose,
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


if __name__ == "__main__":
    main()
