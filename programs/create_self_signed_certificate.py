import mpre.base
import mpre.networkssl

class Self_Signed_Certificate(mpre.base.Base):
    
    defaults = mpre.base.Base.defaults.copy()
    defaults.update({"name" : "server"})
    
    def _get_key(self):
        return self.create("mpre.fileio.File", "{}.key".format(self.name), 'rb')
    key = property(_get_key)
    
    def _get_crt(self):
        return self.create("mpre.fileio.File", "{}.crt".format(self.name), 'rb')
    crt = property(_get_crt)
    
    def _get_csr(self):
        return self.create("mpre.fileio.File", "{}.csr".format(self.name), 'rb')
    csr = property(_get_csr)
    
    def __init__(self, **kwargs):
        super(Self_Signed_Certificate, self).__init__(**kwargs)
        mpre.networkssl.generate_self_signed_certificate(self.name)
        
if __name__ == "__main__":
    certificate = Self_Signed_Certificate(parse_args=True)    
    Instruction("Python", "exit").execute()