# WatchTowerAI – Log Analyzer and Runbook Generator

WatchTowerAI is an AI-powered log analysis and incident response assistant built using a fine-tuned FLAN-T5 model. It classifies log messages by severity and generates corresponding runbooks to support site reliability engineering (SRE) and DevOps workflows. Critical incidents automatically trigger Slack alerts with a link to the recommended remediation steps hosted on AWS S3.

## Features

- Real-time log message classification (INFO, WARNING, ERROR, CRITICAL, SECURITY)
- Fine-tuned FLAN-T5 model for classification and response generation
- Step-by-step markdown runbook generation for critical/severe logs
- Automatic Slack notifications with incident summaries
- Secure AWS S3 integration to store and access runbooks
- Streamlit web application for user-friendly log ingestion and results display

## Technologies Used

- Python
- Hugging Face Transformers (FLAN-T5)
- Streamlit (UI)
- AWS S3 (Cloud Storage)
- Slack Webhooks (Alerting)
- PyTorch
- boto3 (AWS SDK for Python)

## Model Details

The model used is a fine-tuned version of FLAN-T5 on a custom dataset of log messages and severity labels. It is hosted at:

- [Tuathe/codementor-flan-watchtower](https://huggingface.co/Tuathe/codementor-flan-watchtower)

Training details:
- Base Model: `google/flan-t5-base`
- Training Epochs: 25
- Dataset: Synthetic + real-world log messages with severity labels
- Output: Text classification + markdown-style runbook generation

## Application Flow

1. User enters or uploads log messages via the Streamlit interface.
2. The FLAN-T5 model classifies each message by severity.
3. If the severity is **CRITICAL** or **SECURITY**:
   - A markdown runbook is generated with possible causes, troubleshooting steps, and escalation info.
   - The runbook is uploaded to AWS S3.
   - A Slack alert is triggered with the log and a link to the runbook.
4. All results are shown in the web UI for review.

## Folder Structure

watchtowerai/
├── streamlit_app.py # Streamlit frontend + main logic
├── notify_slack.py # Slack integration
├── upload_to_s3.py # AWS S3 uploader
├── requirements.txt # Python dependencies
├── .gitignore # Ignore virtual env, secrets, etc.
└── README.md # Project documentation

bash
Copy
Edit

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/chetan10510/watchtowerai-log-analyzer.git
cd watchtowerai-log-analyzer
2. Create a Virtual Environment and Install Dependencies
bash
Copy
Edit
python -m venv .venv
source .venv/bin/activate    # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
3. Set Environment Secrets (Streamlit)
In secrets.toml or via Hugging Face Secrets:

toml
Copy
Edit
AWS_ACCESS_KEY_ID = "your_aws_key"
AWS_SECRET_ACCESS_KEY = "your_aws_secret"
AWS_REGION = "ap-south-1"
S3_BUCKET_NAME = "your-bucket"
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/..."
4. Run the App
bash
Copy
Edit
streamlit run streamlit_app.py
Deployment
This project can be deployed on:

Hugging Face Spaces (Streamlit + Transformers)

AWS EC2 (via Docker or manual Python setup)

Any public-facing server with Python + internet access

Example Use Case
Log Input:

bash
Copy
Edit
Service not responding for 300 seconds – connection timeout
Output:

Classification: CRITICAL

Runbook generated and uploaded to S3

Slack alert sent with runbook link

Future Enhancements
Log batch processing from S3 or log streams

Integration with Datadog, Prometheus, or Elastic Stack

Support for multilingual logs

Embedding-based similarity search for historical incidents

License
This project is licensed under the Apache 2.0 License.

Author
Created by Chetan K. as part of an AI/MLOps learning initiative. For academic, internship, and demonstration purposes.

yaml
Copy
Edit

---

Let me know if you'd like:
- A **shorter version** for GitHub previews
- A **PDF version** for resume/portfolio attachment
- A **streamlined version** for Hugging Face `README.md`

This version positions you professionally as a student or junior MLOps engineer with hands-on full-stack AI experience.







Ask ChatGPT
