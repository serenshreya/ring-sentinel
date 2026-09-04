import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_explanation(cluster: dict, orders_in_cluster: list[dict]) -> str:
    if not GROQ_API_KEY:
        return "Explanation unavailable: GROQ_API_KEY not configured."
        
    client = Groq(api_key=GROQ_API_KEY)
    
    members = cluster.get('member_customer_ids', [])
    devices = set(o.get('device_id') for o in orders_in_cluster if o.get('device_id'))
    ips = set(o.get('ip_address') for o in orders_in_cluster if o.get('ip_address'))
    refunds = set(o.get('refund_bank_account') for o in orders_in_cluster if o.get('refund_bank_account'))
    addresses = set(o.get('delivery_address') for o in orders_in_cluster if o.get('delivery_address'))
    amounts = [float(o.get('amount', 0)) for o in orders_in_cluster]
    avg_amount = sum(amounts) / len(amounts) if amounts else 0
    
    user_prompt = (
        f"Cluster size: {len(members)} accounts\n"
        f"Shared device count: {len(devices)}\n"
        f"Shared IP count: {len(ips)}\n"
        f"Shared refund accounts count: {len(refunds)}\n"
        f"Shared delivery address count: {len(addresses)}\n"
        f"Total orders placed: {len(orders_in_cluster)}\n"
        f"Average order amount: ${avg_amount:.2f}\n"
    )
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a fraud analyst assistant for an advisory risk system. "
                        "Generate exactly ONE concise plain-English sentence summarizing the observed signal patterns "
                        "(shared devices, shared IPs, refund bank accounts, or physical address overlap). "
                        "CRITICAL GUARDRAILS:\n"
                        "- Do NOT recommend any action (do NOT say 'block', 'hold', 'flag', 'freeze', or 'approve').\n"
                        "- Do NOT generate or invent numerical risk scores, probabilities, or percentages.\n"
                        "- Your role is strictly descriptive explainability of the provided signals."
                    )
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            model="qwen/qwen3.8-27b",
            temperature=0.2,
            max_tokens=90,
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating explanation: {str(e)}"
