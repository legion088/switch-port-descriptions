"""
Программа реализована только для сетевых коммутаторов D-Link
"""
from telnetlib import Telnet
import json


class Switch(object):
    def __init__(self, host: str, username: str,
                 password: str, count_ports: int):
        self.host = host
        self.username = username
        self.password = password
        self.count_ports = count_ports

    def connect(self) -> object:
        tn = Telnet(self.host)
        tn.read_until("UserName:".encode("ascii"), timeout=2)
        tn.write(f"{self.username}\n".encode("ascii"))
        tn.read_until("PassWord:".encode("ascii"), timeout=2)
        tn.write(f"{self.password}\n".encode("ascii"))
        return tn

    def extract_descriptions(self) -> dict:
        tn = self.connect()
        port_descriptions = {
            self.host: {}
        }
        for port in enumerate(range(0, self.count_ports), start=1):
            tn.write(f"show ports {port[0]} description\n".encode("ascii"))
            tn.write("q".encode("ascii"))
            tn.read_until("Description: ".encode("ascii"), timeout=2)
            desc = tn.read_very_eager().decode("utf-8")
            port_descriptions.get(self.host).setdefault(port[0], desc.splitlines()[0].strip())
        tn.close()
        return port_descriptions


def read_data() -> dict:
    with open("switch_conf.json", "r") as file:
        return json.load(file)


def main():
    switch_conf = read_data()
    all_ports_descriptions = dict()
    for host, conf in switch_conf.items():
        obj = Switch(host,
                     conf.get('username'),
                     conf.get('password'),
                     conf.get('ports'))
        all_ports_descriptions.update(obj.extract_descriptions())
    ports_descriptions = json.dumps(all_ports_descriptions, indent=4, ensure_ascii=False)
    with open("data.json", "w", encoding="utf-8") as file:
        file.write(ports_descriptions)


if __name__ == '__main__':
    main()