Introduction to YouTube Service

*Readme.md*

*In this part of the assignment we have to Build a simplified version of Youtube using RabbitMQ* **Running of the code**

- *YoutubeServer*

![](Aspose.Words.40378f6e-3c4d-4dd8-8ca1-ca72c3101262.001.png)

- *Youtuber*

![](Aspose.Words.40378f6e-3c4d-4dd8-8ca1-ca72c3101262.002.png)

- *User1*

![](Aspose.Words.40378f6e-3c4d-4dd8-8ca1-ca72c3101262.003.png)

- *User2*

![](Aspose.Words.40378f6e-3c4d-4dd8-8ca1-ca72c3101262.004.png)

**Explanation**

YoutubeServer.py

- RabbitMQ Class:
- The RabbitMQ class is responsible for initializing the RabbitMQ connection, handling requests from users and YouTubers, and managing subscriptions and notifications.
  - It has methods like start() to start the server, stop() to stop the server, handle\_request() to handle incoming requests, handle\_youtuber\_request() to handle requests from YouTubers, handle\_user\_request() to handle requests from users and process\_request() to process incoming requests.
- Server Functionality:
  - The server() function initializes an instance of the RabbitMQ class and starts the server. It catches KeyboardInterrupt exceptions to stop the server gracefully if the user interrupts the process.
- Main Function:
  - The main() function acts as the entry point.
  - It continuously starts the server and waits for a certain time interval (60 seconds) before restarting it.
  - It catches KeyboardInterrupt exceptions to provide an option to restart the server or exit the program.
- Handling Requests:
  - Requests are received in JSON format.
  - If the request is from a user, it subscribes or unsubscribes the user to/from a YouTuber's channel based on the request.
  - If the request is from a YouTuber, it handles the uploaded video by adding it to the YouTuber's video list and notifyingTT subscribed users about the new video.
- Messaging Queues:
  - Different queues are used for handling different types of requests (DragonEyeX-Youtube, DragonEyeX-Youtuber, DragonEyeX-User) to organize and manage the flow of messages.

Youtuber.py

- Youtuber Class:
- The Youtuber class represents a YouTuber entity.
- Its constructor initializes a connection to the RabbitMQ server, creates a channel, and declares two queues: one for general communication (DragonEyeX-Youtube) and another specific to this YouTuber instance (DragonEyeX-Youtuber-<username>).
- It also sets up a consumer to listen to messages on the YouTuber-specific queue (DragonEyeX-Youtuber-<username>).
- The publish\_video() method publishes a video to the RabbitMQ server. It constructs a JSON message containing the YouTuber's username and the video name, then sends it to the general communication queue (DragonEyeX-Youtube).
- handle\_response() Method:
  - This method is a callback function invoked when a response is received on the YouTuber-specific queue.
  - It decodes the response JSON and prints the status.
  - Finally, it closes the connection to the RabbitMQ server.
- connect\_to\_server() Function:
  - This function creates an instance of the Youtuber class and publishes a video by invoking the publish\_video() method.
  - It then starts consuming messages from the YouTuber-specific queue to listen for responses.
- main() Function:
  - This function serves as the entry point of the script.
  - It takes two command-line arguments: YoutuberName (the username of the YouTuber) and VideoName (the name of the video to publish).
  - It calls the connect\_to\_server() function with the provided arguments.
- Command Line Execution:
  - If the script is executed directly (not imported as a module), it checks if the correct number of command-line arguments (3) are provided.
  - If not, it prints a usage message and exits with a non-zero status.
  - Otherwise, it calls the main() function with the provided command-line arguments.

User.py

- User Class:
- The User class represents a user entity. Its constructor initializes a connection to the RabbitMQ server, creates a channel, and declares two queues: one for general communication (DragonEyeX-Youtube) and another specific to this user instance (DragonEyeX-User-<username>).
- The update\_subscription() method updates the user's subscription status to a specified YouTuber. It constructs a JSON message containing the user's username, the YouTuber's username, and whether to subscribe or unsubscribe (True or False). It then publishes this message to the general communication queue (DragonEyeX-Youtube).
- The receive\_notifications\_in\_queue() method receives notifications from the user-specific queue (DragonEyeX-User-<username>) using the basic\_get() method. It then handles the response accordingly.
- The receive\_notifications() method sets up a consumer to listen for notifications on the user-specific queue (DragonEyeX-User-<username>) using the basic\_consume() method. It then starts consuming messages using the start\_consuming() method.
- The handle\_response() method is a callback function invoked when a notification or response is received. It decodes the response JSON and prints the status or the notification details.
- Command Line Execution:
- If the script is executed directly (not imported as a module), it checks if the correct number of command-line arguments (2 or 4) are provided.
- If not, it prints a usage message and exits with a non-zero status. Otherwise, it creates an instance of the User class with the provided username.
- It then calls receive\_notifications\_in\_queue() to check for any existing notifications.
- If additional command-line arguments are provided (indicating a subscription update), it extracts the action ('s' for subscribe or 'u' for unsubscribe) and the YouTuber's name. It then calls update\_subscription() to update the subscription status.
- Finally, it starts consuming notifications by calling receive\_notifications().
