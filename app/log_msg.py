def log_msg(self, msg: str, tag: str = "info"):
    self.log.insert("end", msg + "\n", tag)
    self.log.see("end")
    self.update_idletasks()