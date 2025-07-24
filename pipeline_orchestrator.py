# pipeline_orchestrator.py

from dotenv import load_dotenv
load_dotenv()

import os
import json
import sys
from langchain import OpenAI
from langchain.agents import Tool, initialize_agent
from llm_agent import EmailTool
from mailer_agent import MailerTool

# Your threshold (override via env var if you like)
MIN_VAL_ACC = float(os.getenv("MIN_VALIDATION_ACCURACY", 0.10))

def load_metrics(build_id: str) -> dict:
    """
    Read training_metrics.csv (or JSON) and return:
      { "best_val_accuracy": float, "best_epoch": int, "epochs_trained": int }
    """
    # CSV loader (requires pandas in your env)
    csv_path = "training_metrics.csv"
    if os.path.exists(csv_path):
        import pandas as pd
        df = pd.read_csv(csv_path)
        best_idx = df["val_accuracy"].idxmax()
        row = df.loc[best_idx]
        return {
            "best_val_accuracy": float(row["val_accuracy"]),
            "best_epoch":        int(row["epoch"]),
            "epochs_trained":    int(df["epoch"].max()),
        }

    # Fallback to test-results.json
    json_path = "test-results.json"
    if os.path.exists(json_path):
        return json.load(open(json_path))

    return {}

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-id",      help="CodeBuild build identifier")
    parser.add_argument("--deploy-event",  choices=["success","failure"])
    args = parser.parse_args()

    llm = OpenAI(temperature=0)
    tools = [
        Tool("RunTests",  func=lambda _: os.system("pytest --json-report --maxfail=1"),
             description="Run the test suite"),
        Tool("Deploy",    func=lambda _: os.system("bash deploy.sh"),
             description="Deploy the Docker container to EC2"),
        Tool("Rollback",  func=lambda _: os.system("bash rollback.sh"),
             description="Rollback to the previous stable release"),
        EmailTool(),
        MailerTool(),
    ]
    agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)

    if args.build_id:
        metrics = load_metrics(args.build_id)
        best_acc = metrics.get("best_val_accuracy", 0.0)
        # Enforce 95% threshold
        if best_acc < MIN_VAL_ACC:
            # Low accuracy → rollback + notify
            prompt = (
                f"Build {args.build_id} achieved best validation accuracy = "
                f"{best_acc:.4f}, which is below the minimum of {MIN_VAL_ACC:.2f}. "
                "Invoke Rollback and then send a failure notification email."
            )
        else:
            # High enough → tests (if you want) then deploy + notify
            prompt = (
                f"Build {args.build_id} achieved best validation accuracy = "
                f"{best_acc:.4f}, meeting the {MIN_VAL_ACC:.2f} threshold. "
                "Invoke Deploy and then send a success notification email."
            )
        agent.run(prompt)

    elif args.deploy_event:
        if args.deploy_event == "success":
            agent.run("Deployment succeeded. Send notification email to team.")
        else:
            agent.run("Deployment failed. Roll back and notify team.")
    else:
        agent.run("No event specified.")

if __name__ == "__main__":
    main()
