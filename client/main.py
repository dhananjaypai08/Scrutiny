# FastAPI imports
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

# Model imports
from model import Customer, CustomerCreate, SessionLocal, ResponseCustomer

# redis import
import redis

# other imports
from typing import List, Optional
import uvicorn
import stripe
# from dotenv import load_dotenv
import os
import json
import logging
import socket
from datetime import datetime

# Configure the logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
severity = {"INFO": 1, "DEBUG": 2, "WARNING": 3, "ERROR": 4, "CRITICAL": 5}

# # Create a TCP socket connection
# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock.connect(('localhost', 5000)) 
# # Send logs to your logging service
# handler = logging.handlers.SocketHandler(sock, port=5000)
handler = logging.FileHandler("./logfile.log")
logger.addHandler(handler)

# Create a StreamHandler connected to the socket
# handler = logging.StreamHandler(sock)
# logger.addHandler(handler)

# load_dotenv()
app = FastAPI()

# Redis Connection
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Cache setup
redis_cache = redis.StrictRedis(host='localhost', port=6379, db=0)

# @app.on_event("shutdown")
# async def shutdown():
#     global sock
#     sock.close()

def getDate():
    # Get the current date and time object
    now = datetime.now()

    # Format the date and time according to your desired format
    formatted_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
    return str(formatted_datetime)

def getIP():
    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server (replace with desired host and port)
    sock.connect(("www.example.com", 80))

    # Get the connected peer's address (source IP and port)
    source_ip, source_port = sock.getsockname()

    # Get the remote peer's address (destination IP and port)
    dest_ip, dest_port = sock.getpeername()

    # Close the socket
    sock.close()
    return source_ip, dest_ip

# Handle Incoming requests from Stripe
@app.post("/stripe/webhook")
async def stripe_webhook(request: Request, event_id: Optional[str] = None):
    """ This endpoint is a webhook that detects modifications from stripe account and updates to our Local DB using Redis Queue"""
    payload = await request.body()
    # sign_headers = request.headers.get("stripe-signature")
    
    try:
        # event = stripe.Webhook.construct_event(
        #     payload, sign_headers, webhook_secret
        # )
        source, destination = getIP()
        logger.info({"logmessage": "INFO", "logdescription": "Event detected from stripe webhook", "severity": severity["INFO"], "timestamp": getDate(), "source_ips": source, "destination_ips": destination})
        event = json.loads(payload)
        # logger.info({})
    except Exception as e:
        source, destination = getIP()
        logger.error({"logmessage": "ERROR", "logdescription": "Caught error while processing stripe webhook", "severity": severity["ERROR"], "timestamp": getDate(), "source_ips": source, "destination_ips": destination})
    
    # Handle the specific events
    # if event.type == "customer.created":
    #     customer = event.data.object
    #     # Serialize the task, including parameters, to JSON
    #     # customer['key'] = 'customer_created'
    #     # task = json.dumps(customer)
    #     # Add the task to the queue
    #     redis_client.lpush("inward", "yoyo")
    #     source, destination = getIP()
    #     print("Customer Creation request from stripe was sent to Redis Queue")
    #     logger.info("Customer creation request from stripe was sent to Redis Queue")
        
    
    # if event.type == "customer.updated":
    #     # customer = event.data.object
    #     # customer['key'] = 'customer_updated'
    #     # task = json.dumps(customer)
    #     # Add the task to the queue
    #     redis_client.lpush("inward", "yoyo")
    #     print("Customer Updation request sent to Redis")
    #     logger.info("Customer updation request sent to Redis")
        
    # if event.type == "customer.deleted":
    #     # customer = event.data.object
    #     # customer = {"id": customer['id']}
    #     # customer['key'] = 'customer_deleted'
    #     # task = json.dumps(customer)
    #     # Add the task to the queue
    #     redis_client.lpush("inward", "yoyo")
    #     print("Customer deletion request sent to Redis")
    #     logger.info("Customer deletion request sent to Redis")

# API routes
@app.post("/stripe/customers", response_model=dict)
async def create_customer(customer: CustomerCreate):
    """Create a new customer on Local + stripe

    Args:
        customer (CustomerCreate): model details of customer

    Returns:
        dict: Status of the tasks added to the queue
    """
    # Serialize the task, including parameters, to JSON
    # new_customer = customer.dict()
    # new_customer['key'] = 'customer_created'
    # task = json.dumps(new_customer)
    # Add the task to the queue
    redis_client.lpush("outward", "yoyo")
    source, destination = getIP()
    logger.info({"logmessage": "INFO", "logdescription": "Customer creation request sent to Redis Queue", "severity": severity["INFO"], "timestamp": getDate(), "source_ips": source, "destination_ips": destination})
    return {"message": "Customer Creation request sent to Redis Queue"}

@app.get("/stripe/customers", response_model=List[ResponseCustomer])
async def get_customer():
    """Get all the customers

    Returns:
        List[ResponseCustomer]: list details of the retrieved customer
    """
    # Attempt to retrieve the resource from the cache
    cached_resource = redis_cache.get("resource")
    if cached_resource: 
        source, destination = getIP()
        logger.debug({"logmessage": "DEBUG", "logdescription": "The data has been fetched from cache", "severity": severity["DEBUG"], "timestamp": getDate(), "source_ips": source, "destination_ips": destination})
        return json.loads(cached_resource)
    
    db = SessionLocal()
    customers = db.query(Customer).all()
    db.close()
    resources = [{"id": customer.id, "name": customer.name, "email": customer.email} for customer in customers]
    # Cache the resource with a short expiration time (e.g., 60 seconds)
    redis_cache.setex("resource", 30, json.dumps(resources))
    source, destination = getIP()
    logger.info({"logmessage": "INFO", "logdescription": "All the customers have been fetched", "severity": severity["INFO"], "timestamp": getDate(), "source_ips": source, "destination_ips": destination})
    return customers

@app.get("/stripe/customers/get", response_model=str)
async def get_specific_customer():
    """ Get a specific customer

    Args:
        id (str): Customer ID

    Returns:
        ResponseCustomer: details of the retrieved customer
    """
    try:
        # Attempt to retrieve the resource from the cache
        cached_resource = redis_cache.get(f"resource_{id}")
        if cached_resource: 
            logger.debug({"logmessage": "DEBUG", "logdescription": "data has been fetched", "severity": severity["DEBUG"], "timestamp": getDate(), "source_ips": source, "destination_ips": destination})
            return json.loads(cached_resource)
        
        # db = SessionLocal()
        # customer = db.query(Customer).filter_by(id=id).first()
        # db.close()
        # Cache the resource with a short expiration time (e.g., 60 seconds)
        redis_cache.setex(f"resource_{id}", 30, "yoyo")
        logger.debug({"logmessage": "DEBUG", "logdescription": "data has been fetched from db", "severity": severity["DEBUG"], "timestamp": getDate(), "source_ips": source, "destination_ips": destination})
    except Exception as e:
        source, destination = getIP()
        logger.critical({"logmessage": "CRITICAL", "logdescription": "Something went wrong while fetching the specific customer data", "severity": severity["CRITICAL"], "timestamp": getDate(), "source_ips": source, "destination_ips": destination})
    return "Customer data fetched"

@app.put("/stripe/customers", response_model=dict)
async def update_customer():
    """ Updating a customer in strip + local

    Args:
        id (str): customer ID
        data (CustomerCreate): Customer model Details

    Returns:
        dict: Status of the tasks added to the queue
    """
    # customer = data.dict()
    # customer['id'] = id
    # customer['key'] = 'customer_updated'
    # task = json.dumps(customer)
    # Add the task to the queue
    redis_client.lpush("outward", "yoyo")
    source, destination = getIP()
    logger.info({"logmessage": "INFO", "logdescription": "data has been cache", "severity": severity["INFO"], "timestamp": getDate(), "source_ips": source, "destination_ips": destination})
    return {"message": "Customer Updation request sent to Redis"}

@app.delete("/stripe/customers", response_model=dict)
async def delete_customer():
    """ Deleting customer from local + stripe

    Args:
        id (str): customer_id

    Returns:
        str: success message
    """
    # customer = {"id": id}
    # customer['key'] = 'customer_deleted'
    # task = json.dumps(customer)
    # Add the task to the queue
    redis_client.lpush("outward", "yoyo")
    source, destination = getIP()
    logger.warning({"logmessage": "WARNING", "logdescription": "Customer deletion request sent to Redis", "severity": severity["WARNING"], "timestamp": getDate(), "source_ips": source, "destination_ips": destination})
    return {"message": "Customer deletion request sent to Redis"}

@app.get("/getLogs", response_model=list)
async def getLogs():
    data = []
    with open("./logfile.log", "r") as file:
        for i, line in enumerate(file):
            try:
                line = eval(line)
                line["uids"] = i
                data.append(line)
            except:
                pass
            
        file.close()
    print(data)
    # return data
    def generate_csv():
        file_name = "logs.csv"
        yield ','.join(data[0].keys()) + '\n'
        for item in data:
            yield ','.join(str(item[key]) for key in data[0].keys()) + '\n'
    return StreamingResponse(generate_csv(), media_type="text/csv")

if __name__ == "__main__":
    uvicorn.run("main:app",host='localhost', port=8000, reload=True)