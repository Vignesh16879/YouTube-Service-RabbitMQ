import pika
import json
import sys

class Youtuber:
    def __init__(self, username):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        self.queue_name = 'DragonEyeX-Youtube'
        self.youtuber_qeue_name=f"DragonEyeX-Youtuber-{username}"
        self.channel.queue_declare(queue=self.queue_name)
        self.channel.queue_declare(queue = self.youtuber_qeue_name)
        self.username = username
        self.channel.basic_consume(queue=self.youtuber_qeue_name, on_message_callback=self.handle_response, auto_ack=True)


    def publish_video(self, video_name):
        request = {
            'user_type': "Youtuber",
            'username': self.username,
            'video': video_name
        }
        self.channel.basic_publish(exchange='', routing_key=self.queue_name, body=json.dumps(request))


    def handle_response(self, channel, method, properties, body):
        response = json.loads(body.decode())

        if "status" in response:
            print(response["status"])
            self.connection.close()


def connect_to_server(username, video):
    youtuber = Youtuber(username)
    youtuber.publish_video(video)
    youtuber.channel.start_consuming()


def main(username, video):
    connect_to_server(username, video)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python Youtuber.py <YoutuberName> <VideoName>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])
