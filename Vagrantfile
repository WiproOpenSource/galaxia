# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # All Vagrant configuration is done here. The most common configuration
  # options are documented and commented below. For a complete reference,
  # please see the online documentation at vagrantup.com.

  # Every Vagrant virtual environment requires a box to build off of.
  config.vm.box = "ubuntu/trusty64"
  if ENV['GALAXIA']
    config.vm.synced_folder ENV['GALAXIA'], "/opt/galaxia"
  end
  config.vm.define :galaxia do |galaxia|
    galaxia.vm.hostname = 'galaxiainsta'
    galaxia.vm.network :private_network, ip: '192.168.76.20'

    galaxia.vm.provider "virtualbox" do |v|
      v.customize ["modifyvm", :id, "--memory", 4000]
      v.customize ["modifyvm", :id, "--cpus", 1]
      v.customize ["modifyvm", :id, "--nicpromisc3", "allow-all"]
    end
    end

end
