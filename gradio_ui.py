def upload_file(self, file, file_uploads_log, allowed_file_types=None):
        """
        Upload a file with size and disk space validation.
        """
        if file is None:
            return gr.Textbox("No file uploaded", visible=True), file_uploads_log

        if allowed_file_types is None:
            allowed_file_types = [".pdf", ".docx", ".txt"]

        file_ext = os.path.splitext(file.name)[1].lower()
        if file_ext not in allowed_file_types:
            return gr.Textbox("File type disallowed", visible=True), file_uploads_log

        #Start protection of DDOS

        # Read limits from environment variables, with default fallbacks
        # MAX_FILE_SIZE_MB will be an integer, default to 100 if not set or invalid
        max_file_size_mb = int(os.getenv("MAX_FILE_SIZE_MB", 100))
        # MIN_FREE_SPACE_MB will be an integer, default to 500 if not set or invalid
        min_free_space_mb = int(os.getenv("MIN_FREE_SPACE_MB", 500))

        #check size of file to limit DDOS on disk
        file_size_bytes = os.path.getsize(file.name)
        file_size_mb = file_size_bytes / (1024 * 1024)

        #check the size of file
        if file_size_mb > max_file_size_mb:
            return gr.Textbox(f"File too big (max {max_file_size_mb} MB)", visible=True), file_uploads_log

        #check the disk availablity
        try:
            free_space_mb = shutil.disk_usage(self.file_upload_folder).free / (1024 * 1024)
            if free_space_mb < min_free_space_mb + file_size_mb:
                return gr.Textbox("File too big is rejected", visible=True), file_uploads_log
        except Exception:
            return gr.Textbox("File too big is rejected", visible=True), file_uploads_log

        #end protection of DDOS
  
        sanitized_name = re.sub(r"[^\w\-.]", "_", os.path.basename(file.name))
        file_path = os.path.join(self.file_upload_folder, sanitized_name)

        try:
            shutil.copy(file.name, file_path)
            file_uploads_log.append({"name": sanitized_name, "path": file_path, "size_mb": round(file_size_mb, 2)})
            return gr.Textbox(f"'{sanitized_name}' uploaded", visible=True), file_uploads_log
        except Exception:
            return gr.Textbox("Upload failed", visible=True), file_uploads_log
