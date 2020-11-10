# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|  
  config.vm.box = "hashicorp/bionic64"  
  config.vm.network "forwarded_port", guest: 5000, host: 5000  
  config.vm.provision "shell", privileged: false, inline: <<-SHELL
     sudo apt-get update       
     sudo apt-get install -y make libssl-dev zlib1g-dev \
     libreadline-dev wget curl llvm libncurses5-dev libncursesw5-dev \
     xz-utils tk-dev libffi-dev liblzma-dev python-openssl git
     sudo apt-get install bzip2 libreadline6 libreadline6-dev openssl
     sudo apt install libssl1.0-dev
     sudo apt-get install -y build-essential
     sudo apt-get install -y libbz2-dev     
     sudo apt-get install -y libsqlite3-dev
             
     if [ ! -d ~/.pyenv ]; then
     git clone https://github.com/pyenv/pyenv.git ~/.pyenv     
     echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.profile
     echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.profile
     echo 'if command -v pyenv 1>/dev/null 2>&1; then' >> ~/.profile
     echo ' eval "$(pyenv init -)"' >> ~/.profile     
     echo 'fi' >> ~/.profile     
     source ~/.profile
     fi      
     pyenv install 3.8.5
     pyenv global 3.8.5
      
     curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
     export PATH="$HOME/.poetry/bin:$PATH"
     cd /vagrant
     poetry install      
  SHELL
  
  config.trigger.after :up do |trigger|
    trigger.name = "Launching App"
    trigger.info = "Running the TODO app setup script"    
    trigger.run_remote = {privileged: false, inline: "    
    cd /vagrant      
    poetry run flask run --host 0.0.0.0
    "}  
  end
 
end
