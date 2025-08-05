import streamlit as st
import os
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from upload_to_s3 import upload_file_to_s3
from notify_slack import send_slack_alert

# Load fine-tuned model
model_path = "Tuathe/codementor-flan-watchtower"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSeq2SeqLM.from_pretrained(model_path)

# Fallback rule-based classifier
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

# Hybrid classifier using Flan-T5 with fallback
def classify_log(log):
    prompt = f"""Classify this log message as one of: INFO, WARNING, ERROR, CRITICAL, SECURITY.

Log: {log}

Label:"""
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True)
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=3)
    prediction = tokenizer.decode(outputs[0], skip_special_tokens=True).strip().upper()

    valid_labels = {"INFO", "WARNING", "ERROR", "CRITICAL", "SECURITY"}
    if prediction in valid_labels:
        return prediction, "Model"
    else:
        return fallback_label(log), "Fallback"

# Runbook generator in markdown format
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

    return runbook_path, runbook_text

# Streamlit UI
st.set_page_config(page_title="WatchTowerAI", layout="centered")
st.title("WatchTowerAI - Log Classification and Runbook Generator")

# Input: text or file
log_input = st.text_input("Enter a log message")
uploaded_file = st.file_uploader("Or upload a .log file", type=["txt", "log"])

# Trigger button
if st.button("Classify and Generate Runbook"):
    logs = []

    if log_input:
        logs.append(log_input.strip())

    if uploaded_file:
        content = uploaded_file.read().decode("utf-8")
        logs.extend([line.strip() for line in content.splitlines() if line.strip()])

    if not logs:
        st.warning("Please enter a log message or upload a file.")
    else:
        for log in logs:
            with st.spinner(f"Processing: {log}"):
                label, source = classify_log(log)
                st.markdown(f"**Classification:** `{label}` ({source})")
                st.markdown(f"**Log:** {log}")

                if label in {"CRITICAL", "SECURITY"}:
                    runbook_path, runbook_md = generate_runbook(log, label)

                    s3_path = runbook_path.replace("\\", "/")
                    success = upload_file_to_s3(runbook_path, "watchtowerai-artifacts", s3_path)

                    if success:
                        s3_url = f"https://watchtowerai-artifacts.s3.ap-south-1.amazonaws.com/{s3_path}"
                        send_slack_alert(log, s3_url)
                        st.success("Slack alert sent with S3 link.")
                        st.markdown(f"[View Runbook on S3]({s3_url})")

                    st.download_button("Download Runbook", runbook_md, file_name=os.path.basename(runbook_path))
                else:
                    st.info("No runbook generated for this log.")
