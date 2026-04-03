"""AI Task Planner for automated server operations"""

import json
from typing import List, Optional
from dataclasses import dataclass
from .base import BaseAIClient

@dataclass
class PlanStep:
    """A single step in the execution plan"""
    step_id: int
    description: str
    command: str
    status: str = "pending"  # pending, running, done, failed
    output: str = ""
    error: str = ""

@dataclass
class ExecutionPlan:
    """Complete execution plan"""
    goal: str
    steps: List[PlanStep]
    current_step: int = 0

PLANNER_SYSTEM_PROMPT = """
You are an automated server operation planner. 
Given the user's goal, create a step-by-step plan to accomplish it via SSH commands.

Follow these rules:
1. Response MUST be valid JSON format only
2. Each step should have:
   - description: Clear description of what this step does
   - command: The exact shell command to execute
3. Keep steps logical and in correct order
4. Use standard Linux/Unix commands that are commonly available
5. If installing packages, use the appropriate package manager for the system
7. Do not include any explanatory text outside the JSON

Output format example:
{
  "goal": "Deploy a web application",
  "steps": [
    {
      "description": "Update system packages",
      "command": "apt update && apt upgrade -y"
    },
    {
      "description": "Install Nginx",
      "command": "apt install -y nginx"
    }
  ]
}
"""

def generate_plan(ai_client: BaseAIClient, user_goal: str, system_info: str = "") -> Optional[ExecutionPlan]:
    """Generate an execution plan from user goal"""
    
    prompt = PLANNER_SYSTEM_PROMPT + f"\n\nUser goal: {user_goal}\n"
    if system_info:
        prompt += f"\nCurrent system information: {system_info}\n"
    prompt += "\nGenerate the execution plan in JSON format:\n"

    response = ai_client._complete(prompt)
    if not response:
        return None

    try:
        data = json.loads(response)
        steps = []
        for i, step_data in enumerate(data.get("steps", [])):
            step = PlanStep(
                step_id=i + 1,
                description=step_data.get("description", ""),
                command=step_data.get("command", "")
            )
            steps.append(step)
        
        return ExecutionPlan(
            goal=data.get("goal", user_goal),
            steps=steps
        )
    except json.JSONDecodeError as e:
        print(f"Failed to parse plan: {e}")
        print(f"Response was: {response}")
        return None

def get_next_step(plan: ExecutionPlan) -> Optional[PlanStep]:
    """Get the next pending step"""
    if plan.current_step >= len(plan.steps):
        return None
    return plan.steps[plan.current_step]

def mark_current_step_done(plan: ExecutionPlan, output: str) -> None:
    """Mark current step as completed"""
    if plan.current_step < len(plan.steps):
        plan.steps[plan.current_step].status = "done"
        plan.steps[plan.current_step].output = output
        plan.current_step += 1

def mark_current_step_failed(plan: ExecutionPlan, error: str) -> None:
    """Mark current step as failed"""
    if plan.current_step < len(plan.steps):
        plan.steps[plan.current_step].status = "failed"
        plan.steps[plan.current_step].error = error

def is_plan_complete(plan: ExecutionPlan) -> bool:
    """Check if plan is complete"""
    return plan.current_step >= len(plan.steps)

def get_plan_status(plan: ExecutionPlan) -> str:
    """Get human-readable plan status"""
    done = sum(1 for step in plan.steps if step.status == "done")
    total = len(plan.steps)
    current_desc = ""
    if plan.current_step < len(plan.steps):
        current_desc = plan.steps[plan.current_step].description
    
    return f"[{done}/{total}] {plan.goal}: {current_desc}"
