import pandas as pd
import json
import io 

class SpreadsheetService:
    def __init__(self):
        pass

    def json_to_excel_buffer(
        self,
        llm_json: str
    ) -> io.BytesIO:
        data = json.loads(llm_json)

        df = pd.DataFrame(data)

        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)

        return excel_buffer