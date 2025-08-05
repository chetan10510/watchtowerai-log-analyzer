from notify_slack import send_slack_alert
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from upload_to_s3 import upload_file_to_s3  # upload function
import torch
import os

# Load fine-tuned Flan-T5 model
model_path = "D:/ACADEMICS/AI-ML/codementor-flan"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSeq2SeqLM.from_pretrained(model_path)

# S3 config
bucket_name = "watchtowerai-artifacts"
region = "ap-south-1"


# Rule-based fallback classifier

def fallback_label(log):
    log_lower = log.lower()
    if "login" in log_lower and "failed" in log_lower:
        return "SECURITY"
    elif "error" in log_lower or "failed" in log_lower:
        return "ERROR"
    elif "timeout" in log_lower or "not responding" in log_lower:
        return "CRITICAL"
    elif "cpu" in log_lower or "memory" in log_lower:
        return "WARNING"
    else:
        return "INFO"


# Hybrid classifier

def classify_log(log):
    prompt = f"""Classify this log message as one of: INFO, WARNING, ERROR, CRITICAL, SECURITY.

Log: {log}

Label:"""

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True)
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=3)

    prediction = tokenizer.decode(outputs[0], skip_special_tokens=True).strip().upper()
    valid_labels = {"INFO", "WARNING", "ERROR", "CRITICAL", "SECURITY"}
    return prediction if prediction in valid_labels else fallback_label(log)


# Runbook generator

def generate_runbook(log_text, label):
    prompt = f"""
You are an expert SRE. Create a step-by-step runbook in markdown format for the following {label} log.

Log message: "{log_text}"

Include:
1. Summary
2. Possible causes
3. Troubleshooting steps
4. Mitigation actions
5. Responsible team or escalation

Only output valid markdown text.
"""
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True)
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=300)

    runbook_text = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

    safe_filename = log_text.lower().replace(" ", "_").replace(":", "").replace('"', '').replace(".", "")
    runbook_path = f"runbooks/runbook_{safe_filename}.md"
    os.makedirs("runbooks", exist_ok=True)

    with open(runbook_path, "w", encoding="utf-8") as f:
        f.write(runbook_text)

    print(f" Runbook generated: {runbook_path}")
    return runbook_path


# MAIN

if __name__ == "__main__":
    logs = [
        "User login successful from IP 192.168.1.10",
        "Payment gateway not responding",
        "CPU usage exceeded 95%",
        "Failed SSH login from unknown IP",
        "Database connection timed out",
        "Out of memory error in service A",
        "Heartbeat signal lost from server B"
    ]

    print("\n--- Hybrid Log Classification Output ---\n")
    for log in logs:
        label = classify_log(log)
        print(f"[{label}] {log}")

        if label in {"CRITICAL", "SECURITY"}:
            runbook_path = generate_runbook(log, label)

            # S3 Key
            s3_key = os.path.basename(runbook_path)
            success = upload_file_to_s3(runbook_path, bucket_name, f"runbooks/{s3_key}")

            if success:
                s3_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/runbooks/{s3_key}"
                send_slack_alert(log, s3_url)
                print(" Slack alert sent with S3 link.\n")
            else:
                print(" Failed to upload to S3, skipping Slack alert.\n")
