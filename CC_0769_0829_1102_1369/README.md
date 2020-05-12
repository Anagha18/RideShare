The final project can be found at /project/final
Run the command sudo docker-compose up -d --scale master=2 to launch the initial 5 containers.

The Rides and Users instance is run on two separate instances, the code (including Dockerfile) for which can be found at /rides and /users

Commands to run Rides:
docker system prune -a
docker build -t users:latest .
sudo docker run   -p 80:5000 -ti users:latest

Commands to run Users:
docker system prune -a
docker build -t rides:latest .
sudo docker run  -p 80:5000 -ti rides:latest

The DNS of the Load Balancer is: my-load-840480578.us-east-1.elb.amazonaws.com
IP address of the orchestrator: 18.214.10.98
IP address of Rides VM: 3.216.234.82
IP address of Users VM: 52.205.146.248