import pika
import json
import sys

class User:
    def __init__(self, user_name):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        self.queue_name = 'DragonEyeX-Youtube'
        self.user_queue_name=f"DragonEyeX-User-{user_name}"

        self.channel.queue_declare(queue=self.queue_name)
        self.channel.queue_declare(queue=self.user_queue_name)
        self.username = user_name


    def update_subscription(self, youtuber_name, subscribe):
        request = {
            'user_type' : "User",
            'username': self.username,
            'youtuber': youtuber_name,
            'subscribe': True if subscribe == 's' else False
        }

        self.channel.basic_publish(exchange='', routing_key=self.queue_name, body=json.dumps(request))


    def receive_notifications_in_queue(self):
        method_frame, header_frame, body = self.channel.basic_get(queue=self.user_queue_name, auto_ack=True)

        if method_frame:
            self.handle_response(method_frame, header_frame," ", body)
        else:
            return


    def receive_notifications(self):
        self.channel.basic_consume(queue=self.user_queue_name, on_message_callback=self.handle_response, auto_ack=True)
        self.channel.start_consuming()


    def handle_response(self, channel, method, properties, body):
        response = json.loads(body.decode())

        if "status" in response:
            print(response["status"])
        else:
            youtuber = response["youtuber"]
            video = response["video"]
            print(f"New Notification: { youtuber } uploaded { video }")


if __name__ == "__main__":
    if len(sys.argv) not in [2, 4]:
        print("Usage: python User.py <UserName> [s/u YoutuberName]")
        sys.exit(1)

    user_name = sys.argv[1]
    user = User(user_name)

    user.receive_notifications_in_queue()

    if len(sys.argv) == 4:
        action = sys.argv[2]
        youtuber_name = sys.argv[3]

        user.update_subscription(youtuber_name, action)

    user.receive_notifications()
