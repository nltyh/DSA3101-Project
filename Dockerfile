FROM python:3.9-slim

# Set the working directory
WORKDIR /DSA3101-Project

# Set PYTHONPATH so Python can find all packages
ENV PYTHONPATH "${PYTHONPATH}:/DSA3101-Project"

# Copy the folders
COPY ./customer_behaviour /DSA3101-Project/customer_behaviour
COPY ./Customer_Review_Analysis /DSA3101-Project/Customer_Review_Analysis
COPY ./inventory_management /DSA3101-Project/inventory_management

# Install dependencies
RUN pip install --no-cache-dir -r /DSA3101-Project/customer_behaviour/requirements.txt

# Expose the port Flask will run on
EXPOSE 5000

# Command to run the Flask app
CMD ["python", "customer_behaviour/app.py"]


