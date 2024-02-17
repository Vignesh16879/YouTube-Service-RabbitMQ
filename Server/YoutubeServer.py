import pika
import time
import sys
import json


class RabbitMQ:
    def __init__(self, host = 'localhost', port = 5672, queue_name = 'DragonEyeX-Youtube'):
        self.host = host
        self.port = port
        self.queue_name = queue_name
        self.connection = None
        self.channel = None
        self.youtubers = {}
    
    
    def start(self):
        connection_url = f'amqp://{self.host}:{self.port}/'
        print(f"Connecting to RabbitMQ using URL: {connection_url}")
        
        try:
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.host, self.port))
        except pika.exceptions.AMQPConnectionError as e:

            print(f"Error connecting to RabbitMQ: {e}")

            sys.exit(1)

        time.sleep(5)
        print("Server Started.")
        
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue = self.queue_name)
        self.channel.queue_declare(queue = "DragonEyeX-Youtuber")
        self.channel.queue_declare(queue = "DragonEyeX-User")
        self.channel.basic_consume(queue = self.queue_name, on_message_callback = self.handle_request, auto_ack = True)

        self.channel.start_consuming()
    
    
    def stop(self):
        self.connection.close()
    
    
    def handle_request(self, channel, method, properties, body):
        request = body.decode()
        
        request=json.loads(request)
        if "user_type" in request:
            usertype=request['user_type']
            username=request["username"]
            
            response = self.process_request(request)
            response = json.dumps(response)
            if request["user_type"] == "User":
                queuename=f"DragonEyeX-User-{username}"
                self.channel.queue_declare(queue = queuename)
    
                channel.basic_publish(exchange='', routing_key=queuename, body=response)

            elif request["user_type"] == "Youtuber":
                queuename=f"DragonEyeX-Youtuber-{username}"
                self.channel.queue_declare(queue = queuename)
                channel.basic_publish(exchange='', routing_key=queuename, body=response)
            else:
                channel.basic_publish(exchange='', routing_key=self.queue_name, body=response)
    

    def handle_youtuber_request(self, username, video):
        if username not in self.youtubers:
            try:
                self.youtubers[username] = {
                    "videos" : [],
                    "users" : []
                }
            except:
                return {"status" : "FAILED", "error" : "An unexpected error occured. Please try again later."}
        
        try:
            self.youtubers[username]["videos"].append(video)
        except:
            return {"status" : "FAILED", "error" : "An unexpected error occured. Please try again later."}
        
        self.send_user_notification(username, video)

        return {"status" : "SUCCESS"}


    def send_user_notification(self, username, video):
        for user in self.youtubers[username]['users']:
            self.notify_user(user, username, video)


    def notify_user(self, user, youtuber, video):
        response = {
            "youtuber" : youtuber,
            "video" : video
        }
        queuename=f"DragonEyeX-User-{user}"
        self.channel.queue_declare(queue = queuename)
        self.channel.basic_publish(exchange='', routing_key=queuename, body=json.dumps(response))


    def handle_user_request(self, user):
        username = user["username"]
        subscribe = user["subscribe"]
        youtuber = user["youtuber"]

        if youtuber not in self.youtubers:
            return {"status": "FAILED", "error": "The specified youtuber does not exist."}

        if subscribe:
            if username not in self.youtubers[youtuber]["users"]:
                try:
                    self.youtubers[youtuber]["users"].append(username)
                    print(f"{username} has subscribed to {youtuber}.")
                except Exception as e:
                    return {"status": "FAILED", "error": "An error occurred while subscribing."}
        else:
            try:
                self.youtubers[youtuber]["users"].remove(username)
                print(f"{username} has unsubscribed to {youtuber}.")
            except Exception as e:
                return {"status": "FAILED", "error": "An error occurred while unsubscribing."}

        return {"status": "SUCCESS"}

    def process_request(self, request):


        try:
            user_type = request["user_type"]
        except:
            return {"status" : "FAILED",  "error":"Unknown error occured."}

        if request["user_type"] == "User":
            response = self.handle_user_request(request)

            return response
        elif request["user_type"] == "Youtuber":
            username = request["username"]
            video = request["video"]
            print(f"{username} uploaded {video}.")
            response = self.handle_youtuber_request(username, video)

            return response
        else:
            return  {"status" : "FAILED", "error":"Invalid Request."}


def server():
    SERVER = RabbitMQ()
    print("Starting Server.")
    
    try:
        SERVER.start()
    except KeyboardInterrupt:
        print("Stopping server...")
        SERVER.stop()


def main():
    while True:
        try:
            server()
            print("Waiting 60 seconds.")
            time.sleep(60)
            print("Starting Server again.")
        except KeyboardInterrupt:
            print("\nServer stopped")
            try:
                ans = input("Do you wish to start the server again (Yes/No): ")
            except:
                return
            
            if not ans.lower().startswith('y'):
                break


if __name__ == '__main__':
    main()
