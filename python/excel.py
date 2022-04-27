import os
import pandas as pd
from utils import get_datetime
from logger import logger


class Excel:
    sheet_name = 'Sheet1'
    engine = None
    tmp_excel_name = 'Result.xlsx'

    @staticmethod
    def _path_from_name(name):
        folder_path = os.path.join(os.getcwd(), 'files')
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        return os.path.join(folder_path, name)

    @staticmethod
    def _generate_filename():
        return f'{get_datetime()}.xlsx'

    @classmethod
    def get_tmp_excel_path(cls):
        return cls._path_from_name(cls.tmp_excel_name)

    @classmethod
    def get_excel_path(cls):
        return cls._path_from_name(cls._generate_filename())

    @staticmethod
    def _refactor_data(data):
        columns = list(data[0].keys())
        excel_data = [[] for _ in columns]
        for product in data:
            for (key, value), row in zip(product.items(), excel_data):
                row.append(value)
        return columns, excel_data

    @classmethod
    def load_as_dataframe(cls, path):
        df = pd.DataFrame(pd.read_excel(path, sheet_name=cls.sheet_name, engine=cls.engine))
        return df.reindex(sorted(df.columns), axis=1)

    @classmethod
    def load_as_dicts(cls, path):
        data = cls.load_as_dataframe(path)
        labels = list(data.columns.values)
        labels.sort()
        return [{key: row[key] for key in labels} for row in logger.range(data.iloc, desc=f'Excel loading {path}')]

    @classmethod
    def save_dataframe(cls, df: pd.DataFrame, path):
        with pd.ExcelWriter(path) as writer:
            df.to_excel(writer, sheet_name=cls.sheet_name, index=False)

    @classmethod
    def save_dicts(cls, data: list[dict], path):
        if len(data) == 0:
            logger.warning(f'Data lenght is 0, nothing saved')
            return
        # Refactor data
        columns, data = cls._refactor_data(data)
        df = pd.DataFrame(dict(zip(columns, data)), index=None)
        # Write or append
        df_source = None
        if os.path.exists(path):
            df_source = pd.DataFrame(pd.read_excel(path, sheet_name=cls.sheet_name, engine=cls.engine))
        if df_source is not None:
            df = pd.concat([df_source, df], ignore_index=True)
            _log = f'Excel updated succesfull {path}'
        else:
            _log = f'Excel created succesfull {path}'
        cls.save_dataframe(df, path)
        logger.info(_log, start='\n')

