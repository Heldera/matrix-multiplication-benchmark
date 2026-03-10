import datetime
import gspread
from google.auth import default

class SheetExporter:
    def __init__(self,  isu_id):
        # The key is hardcoded/passed by the user
        self.sheet_key = "1uXRYgdSWIgnK1nr4XuNbHjspbxeYC3NeTmZAy9t69wI"
        self.isu_id = isu_id
        
    def authenticate_and_append(self, benchmark_results):
        """Authenticates via Colab and appends results to the sheet."""
        try:
            from google.colab import auth
            from google.auth import default
        except ImportError:
            raise ImportError("This feature requires the 'google.colab' environment.")

        if not benchmark_results or not len(benchmark_results):
            raise ValueError(f"Provided benchmark results are empty. {benchmark_results=}")
            
        print("Authenticating with Google Colab...")
        auth.authenticate_user()
        creds, _ = default()
        gc = gspread.authorize(creds)
        
        sheet = gc.open_by_key(self.sheet_key).sheet1
        
        # Prepare rows to append
        row = [datetime.datetime.now(datetime.timezone.utc).isoformat(), self.isu_id, benchmark_results[0]["Method"], benchmark_results[0]["Comment"]]
        for res_id in range(len(benchmark_results)):
            row.append(benchmark_results[res_id]["Test Type"])
            row.append(benchmark_results[res_id]["Best Time (s)"])
            row.append(benchmark_results[res_id]["Avg Time (s)"])
            row.append(benchmark_results[res_id]["Peak Memory (MB)"])
            
        # Append all rows in a single API call
        sheet.append_row(row)
        print(f"The row was successfully appended to Google Sheets.")