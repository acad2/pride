#   mpf.send_file - sends a file via udp to the specified address

from base import Instruction

Instruction("System", "create", "networklibrary2.File_Service", exit_when_finished=True).execute()
Instruction("File_Service", "send_file", parse_args=True).execute()
