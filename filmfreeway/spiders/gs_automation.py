import time

import gspread


class GoogleSheetAutomation:
    sheet_name = "--WORKFILE-- Film Festivals"

    scopes = [
        "https://spreadsheets.google.com/feeds",
        'https://www.googleapis.com/auth/spreadsheets',
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive",
    ]

    gs = gspread.service_account(filename='gs_credentials.json', scopes=scopes)
    sheet = gs.open(sheet_name).sheet1

    gs_input_records = sheet.get_all_records()
    sheet_headers = {h: i for i, h in enumerate(sheet.row_values(1), start=1)}
    row_count = len(gs_input_records)

    def __init__(self):
        print(f"Connected with {self.sheet_name} Google Spreadsheet")

    def update_gs_rows(self, scraped_records):
        for row_id, row in enumerate(self.gs_input_records, start=2):
            record = scraped_records.get(row['FilmFestivalID'])
            if not record:
                continue

            for col_name, val in record.items():
                if col_name not in self.sheet_headers:
                    continue

                retry = 0
                while retry < 3:
                    try:
                        self.sheet.update_cell(row_id, self.sheet_headers[col_name], val or ' ')
                        time.sleep(0.4)
                        break
                    except Exception as err:
                        print(err)
                        time.sleep(3)
                        retry += 1

        print(f"{len(scraped_records)} rows inserted into google spreadsheet.")
