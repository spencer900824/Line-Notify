# LineNotify

# Init (only do this if using AWS ec2)
1. Create a AWS EC2 - "Amazon Linux2 AMI" instance
2. copy "init_on_ec2.sh" to the instance created in step 1
3. input cmd:  ". ./init_on_ec2.sh"

# Run server
1. git clone https://github.com/spencer900824/Line-Notify.git (if run on EC2, skip this step)
2. input cmd: ". Line-Notify/run.sh"

# Check alive
1. http://[instance_public_ip]:5001

# dev
1. py3 -m flask -A flask_app/main run -p 5001
