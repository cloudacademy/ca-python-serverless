# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/xenial64"

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  config.vm.network "forwarded_port", guest: 8080, host: 8080
  
  # For SAM Local
  config.vm.network "forwarded_port", guest: 3000, host: 3000

  
  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  # config.vm.network "private_network", ip: "192.168.33.10"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network "public_network"

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  config.vm.synced_folder ".", "/app_files"

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VirtualBox:
  #
  config.vm.provider "virtualbox" do |vb|
    # Display the VirtualBox GUI when booting the machine
    vb.gui = false
  
    # Customize the amount of memory on the VM:
    vb.memory = "2048"
  end
  #
  # View the documentation for the provider you are using for more
  # information on available options.

  # Define a Vagrant Push strategy for pushing to Atlas. Other push strategies
  # such as FTP and Heroku are also available. See the documentation at
  # https://docs.vagrantup.com/v2/push/atlas.html for more information.
  # config.push.define "atlas" do |push|
  #   push.app = "YOUR_ATLAS_USERNAME/YOUR_APPLICATION_NAME"
  # end

  # Enable provisioning with a shell script. Additional provisioners such as
  # Puppet, Chef, Ansible, Salt, and Docker are also available. Please see the
  # documentation for more information about their specific syntax and use.
  config.vm.provision "shell", inline: <<-SHELL
    add-apt-repository ppa:deadsnakes/ppa --yes
    apt-get update
    apt-get install -y python3.6 python3.6-dev libssl-dev 
    apt-get install -y python3-pip virtualenv zip
    

    # In case the dir isn't there already, which is unlikey since it's a bound dir.
    mkdir -p /app_files
    cd /app_files
    virtualenv -p /usr/bin/python3.6 venv
   
    source /app_files/venv/bin/activate
    
    pip install moto
    pip install moto[server]    
    pip install -r requirements.txt

    # New and untested
    source /app_files/venv/bin/activate
    pip install awscli
    # link the creds file to the VM
    mkdir -p /home/ubuntu/.aws
    ln -s /app_files/credentials /home/ubuntu/.aws/
    
    # activate the venv on login.
    # this will append for each provision, however it shouldn't be too problematic
    echo "source /app_files/venv/bin/activate" | sudo tee -a /etc/profile
    
    grep -q -F 'PYTHONPATH="/app_files:$PYTHONPATH"' /etc/environment || echo 'PYTHONPATH="/app_files:$PYTHONPATH"' | sudo tee -a /etc/environment
    
    # Install SAM local. 
    # Doing it manually since there's an issue with the NPM install as of Sept. 1, 2017
    cd ~
    # wget https://github.com/awslabs/aws-sam-local/releases/download/v0.2.0/sam_0.2.0_linux_amd64.deb
    # dpkg -i sam_0.2.0_linux_amd64.deb
    
    wget https://github.com/awslabs/aws-sam-local/releases/download/v0.2.2/sam_0.2.2_linux_amd64.deb
    dpkg -i sam_0.2.2_linux_amd64.deb
    
    apt-get -f install

    # SAM Local uses docker...so let's install it...
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
    apt-get update
    apt-cache policy docker-ce
    apt-get install -y docker-ce
    
  SHELL
end
