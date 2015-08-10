import mpre.base
import mpre.network
import mpre.utilities
shell = mpre.utilities.shell

def tune_tcp_performance(minimum_size=10240, initial_size=87830,
                         maximum_size=1258912, window_scaling=1,
                         use_timestamps=1, use_selective_ack=1,
                         packet_backlog=0, metrics_cache_disabled=0):
    set_buffer_sizes(minimum_size, initial_size, maximum_size)
    set_window_scaling(window_scaling)
    set_timestamp_use(use_timestamps)
    
    use_selective_acknowledgement(use_selective_ack)
    if packet_backlog:
        set_packet_backlog(packet_backlog)
    disable_metrics_cache(metrics_cache_disabled)  
    
def set_buffer_sizes(minimum_size, initial_size, maximum_size):
    # set maximum read/write buffer sizes
    shell("echo 'net.core.wmem_max={}' >> /etc/sysctl.conf".format(maximum_size))
    shell("echo 'net.core.rmem_max={}' >> /etc/sysctl.conf".format(maximum_size))
    
    sizes = (initial_size, minimum_size, maximum_size)
    shell("echo 'net.ipv4.tcp_rmem= {} {} {}' >> /etc/sysctl.conf".format(*sizes))
    shell("echo 'net.ipv4.tcp_wmem= {} {} {}' >> /etc/sysctl.conf".format(*sizes))
        
def set_window_scaling(flag=1):    
    """Possible side effects per wikipedia:

       Because some routers and firewalls do not properly implement TCP Window Scaling, it can cause a user's Internet connection to malfunction intermittently for a few minutes, then appear to start working again for no reason. There is also an issue if a firewall doesn't support the TCP extensions.""" 
    shell("echo 'net.ipv4.tcp_window_scaling = {}' >> /etc/sysctl.conf".format(flag))
    
def set_timestamp_use(flag=1):    
    shell("echo 'net.ipv4.tcp_timestamps = {}' >> /etc/sysctl.conf".format(flag))
    
def use_selective_acknowledgement(flag=1):    
    shell("echo 'net.ipv4.tcp_sack = {}' >> /etc/sysctl.conf".format(flag))
        
def disable_metrics_cache(state=0):
    shell("echo 'net.ipv4.tcp_no_metrics_save = {}' >> /etc/sysctl.conf".format(state))
        
def set_packet_backlog(backlog=5000):
    shell("echo 'net.core.netdev_max_backlog = {}' >> /etc/sysctl.conf".format(backlog))
        
def reload_with_changes():
    shell("sysctl -p")    
    
def set_file_handle_limit(limit):
    shell("sysctl -w fs.file-max={}".format(limit))
    
def set_connection_backlog(backlog):
    shell("sysctl -w net.core.netdev_max_backlog = {}".format(backlog))
    
def set_max_connection(limit):    
    shell("sysctl -w net.core.somaxconn = {}".format(limit))
    
    
class RTT_Test(mpre.network.Tcp_Client):
    
    def on_connect(self):
        super(RTT_Test, self).on_connect()
        self.alert("Connection took: {}".format(self.latency.last_measurement), level=0)
        self.delete()