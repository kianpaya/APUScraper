import subprocess

# Define the wget command
wget_command = [
    "wget",
    "--mirror",
    "--convert-links",
    "--adjust-extension",
    "--page-requisites",
    "--no-parent",
    "--wait=2",
    "--random-wait",
    "-e", "robots=off",
    "--directory-prefix=wget/data/html",
    "https://web.archive.org/web/20241112194819/https://apueducation.us/"
]

# Run the wget command from Python
subprocess.run(wget_command)
