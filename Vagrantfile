Vagrant.configure(2) do |config|
  config.vm.hostname = 'netaddr-' + `whoami`.chomp.downcase
  config.vm.box = "ubuntu/trusty64"
  config.ssh.forward_agent = true

  config.vm.provider "virtualbox" do |v|
    v.memory = 1024
    v.cpus = 2
  end
end
