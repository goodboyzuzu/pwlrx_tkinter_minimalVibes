import os

def get_matching_directories(logs_directory, search_lines):
    """
    Get directories in the logs directory that match any of the search lines.
    """
    dirs = [entry.name for entry in os.scandir(logs_directory) if entry.is_dir()]
    return [d for line in search_lines for d in dirs if d.startswith(line)]

def process_log_files(files):
    """
    Process log files to find the SELECTED_BLK_COUNT value.
    """
    end_marker = "(.)"
    max_iterations = 5
    for i, fp in enumerate(files):
        if i >= max_iterations:
            return "exceed max limit. find cycle value manually"
        try:
            file_size = os.path.getsize(fp)
            if file_size > 40000 or file_size < 880:  # Skip files >40KB or <1KB
                continue

            with open(fp, "rb") as fh:
                end_marker_found = False
                buffer_size = 1024
                buffer = b""
                fh.seek(0, os.SEEK_END)
                position = fh.tell()

                while position > 0:
                    read_size = min(buffer_size, position)
                    position -= read_size
                    fh.seek(position)
                    chunk = fh.read(read_size)
                    buffer = chunk + buffer

                    lines = buffer.splitlines()
                    buffer = lines.pop(0) if position > 0 and lines else b""

                    for line in reversed(lines):
                        line = line.decode(errors="ignore").strip()
                        if not line:
                            continue

                        if not end_marker_found and end_marker in line:
                            end_marker_found = True
                            continue

                        if end_marker_found and "SELECTED_BLK_COUNT" in line:
                            print("Found in file")
                            return line

                    # If end_marker is found but no "SELECTED_BLK_COUNT", return immediately
                    if end_marker_found:
                        return "No cycle in log"
        except Exception:
            continue
    return "-"
