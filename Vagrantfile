# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure(2) do |config|

  config.vm.define "web" do |web|
    web.vm.box = "ubuntu/xenial64"
    web.vm.network "forwarded_port", guest: 8182, host: 8185
    web.vm.synced_folder ".", "/vagrant"
    web.vm.provider "virtualbox" do |v|
      v.customize ["modifyvm", :id, "--hwvirtex", "off"]
      v.customize ["modifyvm", :id, "--vtxvpid", "off"]
      v.customize ["guestproperty", "set", :id, "--timesync-threshold", 10000]
      v.customize ["guestproperty", "set", :id, "/VirtualBox/GuestAdd/VBoxService/--timesync-set-threshold", 1000]
      v.memory = 8192
      v.cpus = 4
    end
  end
end
