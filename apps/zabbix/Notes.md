## Zabbix

### Associating the Zabbix Agent with the Zabbix Server Host
- Access Zabbix Frontend
- Locate Your Zabbix Server Host: Head to “Monitoring” > “Hosts” and find your Zabbix server in the host list.
- Edit Zabbix Server Host Settings: Click on the name of your Zabbix server host to access its settings.

#### Configure Agent Details:
- If an agent interface for the Zabbix server is already present, check that the IP address or DNS name correctly points to the Zabbix agent’s location (running as a Docker container).
- If no agent interface is listed, click “Add” to create one. Choose “Agent” as the type, and input the IP address or DNS name of the Zabbix agent, ensuring the port aligns with your Zabbix agent configuration, in this case port 10050.
- Apply Changes: Confirm the agent interface details are correct, then click “Update” to save your modifications.
- Verify Connectivity: To confirm successful monitoring of the Zabbix server by the agent, go to “Monitoring” > “Latest data” and Filter by your Zabbix server host to see collected data, indicating the agent’s proper association and functionality. There might be a delay before all items start populating with data.
- Additionally, you can verify the status of the Zabbix agent by navigating to “Monitoring” > “Data collection” and selecting “Hosts” from the dropdown menu. Here, look for the agent availability status next to your Zabbix server host. Initially, this might be indicated by a red icon, signifying no communication. Once the Zabbix agent is successfully connected and communicating with the Zabbix server, this icon will change to green.
Following these steps ensures the Zabbix server is effectively monitored by the Zabbix agent, offering a comprehensive view of the server’s performance and health.