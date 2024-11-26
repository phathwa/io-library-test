#!/bin/bash

#!/bin/bash
echo "************************************************"
echo -e "\npreparing environment....."

# Install Python, pip, git, and AWS CLI (CLI to make sure)
yum install -y python3 python3-pip git aws-cli jq

# Clone Flask app from GitHub
cd /home/ec2-user
git clone https://github.com/phathwa/io-library-test.git
cd io-library-test

# Install Flask and required dependencies
python3 -m venv .venv
source .venv/bin/activate 
pip3 install -r requirements.txt

# # Retrieve secret from AWS Secrets Manager
# REGION="${var.region}"
# SECRET=$(aws secretsmanager get-secret-value --region $REGION --secret-id "${var.secret_name}" --query SecretString --output text)

# if [ $? -ne 0 ]; then
#     echo "Failed to retrieve secret"
#     exit 1
# fi

# # Extract API key from the secret
# API_KEY=$(echo $SECRET | jq -r '.["x-api-key"]')
# if [ -z "$API_KEY" ]; then
#     echo "API_KEY not found in secret"
#     exit 1
# fi

# echo "export API_KEY=$API_KEY" >> /etc/profile

# # Extract Database URI from the secret
# DATABASE_URI=$(echo $SECRET | jq -r '.["database-uri"]')
# if [ -z "$DATABASE_URI" ]; then
#     echo "DATABASE_URI not found in secret"
#     exit 1
# fi

# echo "export DATABASE_URI=$DATABASE_URI" >> /etc/profile

# Set Flask environment variable
echo "export FLASK_ENV=development" >> /etc/profile

# Apply the environment variables
source /etc/profile

# Start application
echo "starting application........"
nohup python3 main.py > /var/log/io-library-app.log 2>&1 &





# Install necessary dependencies
# yum update -y
# yum install -y python3 python3-pip git

# # Download the code from S3 to the /home/ec2-user directory
# aws s3 cp s3://io-library-code/io-books-test /home/ec2-user/io-books-test --recursive

# # Navigate to the project folder
# cd /home/ec2-user/io-books-test
# ls 
# # Install project dependencies
# pip3 install -r requirements.txt

# # Run the Flask application
# python3 main.py
