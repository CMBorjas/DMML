from sqlalchemy import Column, Integer, String, Text
from app import db

class CampaignLog(db.Model):
    __tablename__ = "campaign_logs"  # Explicit table name
    id = db.Column(db.Integer, primary_key=True)
    narrative = db.Column(db.Text)
    encounters = db.Column(db.Text)
    npc_details = db.Column(db.Text)

    def __repr__(self):
        return f"<CampaignLog id={self.id} narrative={self.narrative[:30]}>"

# Function to fetch campaign data
def get_campaign_data():
    # Query all campaign logs from the database
    campaign_logs = CampaignLog.query.all()
    
    # Log the retrieved campaign logs
    print(f"Fetched campaign logs: {campaign_logs}")
    
    # Concatenate relevant fields from all logs for LangChain processing
    campaign_data = []
    for log in campaign_logs:
        campaign_data.append(f"Narrative: {log.narrative}")
        campaign_data.append(f"Encounters: {log.encounters}")
        campaign_data.append(f"NPC Details: {log.npc_details}")
    
    print(f"Campaign data for LangChain: {campaign_data}")
    return campaign_data

