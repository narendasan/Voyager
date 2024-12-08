import requests
from datetime import datetime
import re


def get_latest_version_before_date(package_name, cutoff_date):
    """
    Fetch the latest version of a package released before the cutoff date.

    :param package_name: Name of the package to query
    :param cutoff_date: The cutoff date (str) in "YYYY-MM-DD" format
    :return: The latest version before the cutoff date or None if no version is found
    """
    response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
    response.raise_for_status()
    data = response.json()
    cutoff_date = datetime.strptime(cutoff_date, "%Y-%m-%d")
    valid_versions = []

    for version, details in data["releases"].items():
        for file in details:
            upload_time = datetime.strptime(file["upload_time"], "%Y-%m-%dT%H:%M:%S")
            if upload_time <= cutoff_date:
                valid_versions.append((version, upload_time))
                break

    if not valid_versions:
        return None
    # Sort by release date descending and return the latest version
    return max(valid_versions, key=lambda x: x[1])[0]


def process_requirements_file(input_file, cutoff_date, output_file):
    """
    Process a requirements.in file and generate a constraints.txt with the latest versions limited by cutoff date.

    :param input_file: Path to the requirements.in file
    :param cutoff_date: The cutoff date (str) in "YYYY-MM-DD" format
    :param output_file: Path to the constraints.txt output file
    """
    with open(input_file, "r") as infile:
        lines = infile.readlines()

    constraints = []
    version_pattern = re.compile(r"([a-zA-Z0-9_\-]+)([<>=!~]*.*)?")

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            constraints.append(line + "\n")  # Preserve comments and empty lines
            continue

        match = version_pattern.match(line)
        if match:
            package_name = match.group(1)
            existing_constraint = match.group(2)

            if existing_constraint:
                print(f"Using existing constraint for {package_name}: {line}")
                constraints.append(line + "\n")
                continue  # Skip fetching new versions

            print(f"Processing {package_name} without constraints...")
            try:
                version = get_latest_version_before_date(package_name, cutoff_date)
                if version:
                    constraints.append(f"{package_name}<= {version}\n")
                else:
                    print(f"  No versions found for {package_name} before {cutoff_date}.")
            except Exception as e:
                print(f"  Error processing {package_name}: {e}")

    with open(output_file, "w") as outfile:
        outfile.writelines(constraints)
    print(f"Constraints file written to {output_file}.")


# Example Usage:
if __name__ == "__main__":
    # Set paths and date
    requirements_file = "requirements.in"  # Input file with package names
    constraints_file = "constraints.txt"  # Output constraints file
    cutoff_date = "2023-07-23"  # Replace with your desired cutoff date

    # Process the requirements file
    process_requirements_file(requirements_file, cutoff_date, constraints_file)
