from flask import Flask, render_template, send_from_directory
from CustomerSegmentationModel import report
from Customer_Review_Analysis.Intelligent_Customer_Review_Analysis import sentiment_counts
import nbformat
from nbconvert import HTMLExporter
import os

app = Flask(__name__)

def convert_notebook_to_html(notebook_path):
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook_content = nbformat.read(f, as_version=4)
    html_exporter = HTMLExporter()
    html_exporter.exclude_input = True  # Exclude code cells if desired
    body, _ = html_exporter.from_notebook_node(notebook_content)
    return body

@app.route('/')
def home():
    demand_notebook = convert_notebook_to_html("inventory_management/Demand_Forecasting_Model.ipynb")
    notebook_html = convert_notebook_to_html("Customer_Review_Analysis/NLP_Customer_reviews.ipynb")
    return render_template("index.html", report = report, demand_notebook=demand_notebook, notebook_html = notebook_html, sentiment_counts = sentiment_counts)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)