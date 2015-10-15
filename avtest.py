import struct

import mpre.network

class Clamd_Connection(mpre.network.Tcp_Client):
    
    defaults = {"ip" : "127.0.0.1", "port" : 3310, "max_chunk_size" : 1024}
    
    def __init__(self, **kwargs):
        self.file_results = {}
        super(Clamd_Connection, self).__init__(**kwargs)
        
    def scan_stream(self, _bytes):
        self.send("INSTREAM")
        max_size = self.max_chunk_size
        for chunk_number in range(1 + len(_bytes) / max_size):
            chunk = _bytes[chunk_number * max_size:(chunk_number + 1) * max_size]
            size = struct.pack("!L", len(chunk))
            self.send(size + chunk)
    
    def recv(self, byte_count):
        response = super(Clamd_Connection, self).recv(byte_count).strip()
        if response == "INSTREAM size limit exceeded. ERROR":
            raise ValueError("BuffersizeError")
            
        filename = response.split(": ")[0]
        left = response.split(": ")[1:]
        if isinstance(left, str):
            result = left
        else:
            result = ": ".join(left)
            
        if result != "OK":
            parts = result.split()
            reason = ' '.join(parts[:-1])
            status = parts[-1]
        else:
            reason, status = '', "OK"
            
        self.file_results[filename] = (status, reason)
        if status == "FOUND":
            self.alert("Found infected file: {}: {}: {}",
                       filename, status, reason, level='')