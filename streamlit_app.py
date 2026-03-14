import streamlit as st
import boto3
import pandas as pd
from datetime import datetime

# Configure Streamlit
st.set_page_config(page_title="Legal Case Dashboard", layout="wide")

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('legal-document-summaries')

st.title("⚖️ Legal Case Management Dashboard")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("Search")
    search_type = st.radio("Search by:", ["Job ID", "Client Name", "Case Number"])
    search_query = st.text_input("Enter search term:")

# Main content
if search_query:
    try:
        if search_type == "Job ID":
            response = table.get_item(Key={'jobId': search_query})
            cases = [response['Item']] if 'Item' in response else []
        
        elif search_type == "Client Name":
            response = table.query(
                IndexName='ClientIndex',
                KeyConditionExpression='client_last_name = :cln',
                ExpressionAttributeValues={':cln': search_query}
            )
            cases = response.get('Items', [])
        
        else:  # Case Number
            response = table.scan(
                FilterExpression='case_number = :cn',
                ExpressionAttributeValues={':cn': search_query}
            )
            cases = response.get('Items', [])
        
        if cases:
            for case in cases:
                with st.container():
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Client Information")
                        st.write(f"**Name:** {case.get('client_first_name', 'N/A')} {case.get('client_last_name', 'N/A')}")
                        st.write(f"**Job ID:** {case.get('jobId', 'N/A')}")
                    
                    with col2:
                        st.subheader("Case Details")
                        st.write(f"**Opposing Party:** {case.get('opposing_party', 'N/A')}")
                        st.write(f"**Accident Date:** {case.get('accident_date', 'N/A')}")
                        st.write(f"**SOL Date:** {case.get('sol_date', 'N/A')}")
                    
                    st.write(f"**Location:** {case.get('location', 'N/A')}")
                    st.write(f"**Document Type:** {case.get('document_type', 'N/A')}")
                    
                    st.subheader("Summary")
                    st.write(case.get('summary', 'No summary available'))
                    
                    if case.get('vehicle_info'):
                        st.subheader("Vehicle Information")
                        for vehicle in case.get('vehicle_info', []):
                            st.write(f"**License Plate:** {vehicle.get('license_plate', 'N/A')}")
                    
                    st.markdown("---")
        else:
            st.warning("No cases found matching your search.")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")

else:
    st.info("👈 Use the sidebar to search for cases")

# Footer
st.markdown("---")
st.markdown("Built with Streamlit | Legal Case Management System")