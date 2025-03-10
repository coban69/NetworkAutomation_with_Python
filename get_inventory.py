import sys
from netmiko import ConnectHandler
from paramiko.ssh_exception import SSHException
from netmiko.exceptions import NetMikoAuthenticationException
from netmiko.exceptions import NetMikoTimeoutException
import logging
import threading
import time
from getpass import getpass

script_start = time.time()   #to calculate script's execution time...

try:
    userName = input("username: ")
    passWord = getpass("password: ")
except KeyboardInterrupt:
    sys.exit()

logging.basicConfig(filename='getting_inventory.log', level=logging.DEBUG, datefmt="%d-%b-%y %H:%M:%S")
logger = logging.getLogger('netmiko')

def getinventory(device):

    status = 0
    counter = 0

    while status == 0 and counter < 3:
        try:
            test_conn = ConnectHandler(**device)
            time.sleep(2)
            test_conn.disconnect()
            status = 1
            time.sleep(1)
        except (NetMikoTimeoutException, SSHException, NetMikoAuthenticationException, ConnectionResetError, TimeoutError):
            time.sleep(5)
        counter += 1

    if status == 0:
        logging.error("SSH connection to device {} failed".format(device))

    if status == 1:

        filename = "inventory.txt"  # file to be created and put all PIDs
        pid_serial = list()

        connection = ConnectHandler(**device)
        prompt = connection.find_prompt()
        hostname = prompt[0:-1]
        print("Getting the inventory of {}".format(hostname))
        print("**********************************************")
        inventory = connection.send_command("show inventory").splitlines()

        for x in inventory:
            if 'PID' in x:
                pid_serial.append(x)
        # module_list = []
        for s in pid_serial:

            pid = s.split(',')[0].strip('PID:').strip()
            sn = s.split(',')[-1].strip(' SN:').strip()
            module = hostname + ', ' + pid + ", " + sn
            with open(filename, 'a+') as file_obj:
                file_obj.seek(0)
                # data = file_obj.read(100000)
                # if len(data) > 0:
                file_obj.write('\n')
                file_obj.write(module)

        print(f"Getting the inventory of {hostname} is completed.")
        print("*" * 55)

        connection.disconnect()

with open("devices.txt") as file:  # IP add of device in each line

    devices = file.read().splitlines()

threads = list()

device_to_be_connected = []

for device in devices:
    device_to_be_connected.append({'ip': device, "device_type": "cisco_ios", 'username': userName,
                                   'password': passWord, 'port': '22'})


if __name__ == "__main__":
    
    for line in device_to_be_connected:
        th = threading.Thread(target=getinventory, args=(line,))
        threads.append(th)

    for th in threads:
        th.start()
    for th in threads:
        th.join()

script_stop = time.time()
print("****** Script execution time is {} seconds **********".format(script_stop-script_start))

