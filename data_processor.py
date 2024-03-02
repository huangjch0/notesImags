import re
import argparse
import os

class DataPreprocess:
    def __init__(self, file_list):
        self.file_list = file_list
        self.data = self.read_log_file(self.file_list)

    def read_log_file(self, file_list):
        result = ''
        for file_path in file_list:
            try:
                with open(file_path, 'r') as file:
                    result += file.read()
            except IOError as e:
                result += str(e)
        return result

    def split_data(self, delimiter):
        data_list = self.data.strip().split(delimiter)
        data_list = [item.strip() for item in data_list if item.strip()]
        return data_list

class DataCut(DataPreprocess):
    def __init__(self, config):
        self.config = config
        super().__init__(self.config.files)
        split_datas = self.split_data(self.config.delimiter)  # 数据分割（以后可能有用）
        self.remove_alpha_datas = self.remove_non_alpha_elements(split_datas)  # 移除HwTblID

    def remove_non_alpha_elements(self, data_list):
        filtered_list = []
        for data in data_list:
            match = re.search(rf'{self.config.table_nameP}{self.config.notion}\d+\((\w+)\)', data)  # 匹配 HwTblID 后的()内的内容
            if match:
                filtered_list.append(data)
                # tbl_id = match.group(1)
                # if any(c.isalpha() for c in tbl_id):
                #     filtered_list.append(data)
        return filtered_list    
    
    # def search_data(self, keyword, data):
    #     return [keyword in element for element in data]
    def search_data(self, keyword, data):
        pattern = re.compile(r'\b' + re.escape(keyword) + r'\b')
        return [bool(pattern.search(element)) for element in data]

    def filter_true_element(self, keyword, data):
        bool_list = self.search_data(keyword, data)
        return [string for bool_val, string in zip(bool_list, data) if bool_val]
    
    def filter_elements_by_keywords(self, keywords, data):
        for keyword in keywords:
            data = self.filter_true_element(keyword, data)
        return data

    def fretch_ai_response(self, query, str_list):
        results = []
        for str_item in str_list:
            notion = self.config.notion
            pattern = fr'{str_item}{notion}(\d+)'
            matches = re.search(pattern, query)
            if matches:
                results.append(int(matches.group(1)))
        return results

    def fretch_table_name(self, data_str):
        pattern = rf"{self.config.table_nameP}{self.config.notion}\d+\((\w+)\)"
        match = re.search(pattern, data_str)
        return match.group(1) if match else None
    
    def contruct_word(self, log_str):
        pattern = r"(\d+)<(.*?)>"
        matches = re.findall(pattern, log_str)
        result_adjusted = []
        
        for match in matches:
            if ',' in match[1]:
                # 如果有逗号，分割字符串并分别处理
                parts = match[1].split(',')
                for part in parts:
                    result_adjusted.append([part, int(match[0])])
            else:
                result_adjusted.append([match[1], int(match[0])])
        return result_adjusted
    
    def transform_list(self, input_list):
        return [[word, f'key{self.config.notion}{num}'] for word, num in input_list]
    
    def contruct_model(self, keywords, result_list=None, deep = 0):
        if result_list is None:
            result_list = []
        # init_table = self.filter_elements_by_keywords(keywords, self.split_datas)
        init_table = self.filter_elements_by_keywords(keywords, self.remove_alpha_datas)

        if len(init_table) == 0 or deep >7:  # 限制深度
            return result_list
        for i in init_table:
            if self.transform_list(self.contruct_word(i)) == []:
                result_list.append(i)  # 不找后面的日志
                return result_list
            if i in result_list:
                return result_list
            
            result_list.append(i)
            
            words = self.transform_list(self.contruct_word(i))
            for word in words:
                self.contruct_model(word, result_list, deep+1)
        return result_list
    
    def process_data_from_gui(self, files, initKeyword, sort, delimiter, table_nameP, notion):
        self.file_list = files.split(', ')  # GUI传入的文件路径列表，以逗号分隔
        self.config = argparse.Namespace(
            files=self.file_list,
            initKeyword=initKeyword.split(', '),  # 初始化关键词，以逗号分隔
            sort=sort.lower() in ('true', 'yes', '1'),  # 将字符串转换为布尔值
            delimiter=delimiter,
            table_nameP=table_nameP,
            notion=notion
        )
        self.data = self.read_log_file(self.file_list)  # 重新读取文件
        split_datas = self.split_data(self.config.delimiter)
        self.remove_alpha_datas = self.remove_non_alpha_elements(split_datas)
        
        result = self.contruct_model(self.config.initKeyword)
        if self.config.sort:
            result = sort_by_datetime(result)
        
        return result

def sort_by_datetime(s):
    '''
    功能：排版
    '''
    from datetime import datetime
    def extract_datetime(s):
        match = re.search(r'when:(\d{4}-\d{1,2}-\d{1,2}-\d{1,2}:\d{1,2}:\d{1,2}\.\d{1,2})', s)
        if match:
            datetime_str = match.group(1)
            datetime_str = datetime_str.replace('-', ' ')  # 替换日期中的'-'为' '
            return datetime.strptime(datetime_str, '%Y %m %d %H:%M:%S.%f')
        else:
            return None
    return sorted(s, key=extract_datetime)


def get_abs_filepaths(directory):
    filepaths = []
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.log'):
                filepath = os.path.abspath(os.path.join(root, filename))
                filepaths.append(filepath)
    return filepaths

def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--files', nargs='+', default=['./datalab/ldp.log'], help='文件列表')
    parser.add_argument('--initKeyword', nargs='+', default=['vpnnh', 'key:7'], help='初始化关键词')
    parser.add_argument("--sort", type=bool, default=False, help="排序方式：True为时间，False为广度优先排序")
    parser.add_argument("--delimiter", type=str, default="-----------------end------------------", help="日志分割符")
    parser.add_argument("--table_nameP", type=str, default="HwTblID", help="表名位置信息")
    parser.add_argument("--notion", type=str, default=":", help="标识符（如日志中的：key:7，':'即为其标识符）")
    return parser.parse_args()

def print_by_format(opt):
    '''
    打印结果
    '''
    # file_list = opt.files
    data_processor = DataCut(opt)
    result = data_processor.contruct_model(opt.initKeyword)
    
    remind = '深度优先搜索排序'
    if opt.sort:
        result = sort_by_datetime(result)
        remind = '时间排序'
        
    print(f'本算法共找到 {len(result)} 张表')
    print()
    print('*'*50, f'{remind}', '*'*50)
    print()
    
    for i in result:
        print(i)
        print()
        print(opt.delimiter)
        print()


def save_to_txt(opt, output_file):
    '''
    将结果保存到txt文件
    '''
    file_list = opt.files
    data_processor = DataCut(opt)
    result = data_processor.contruct_model(opt.initKeyword)
    
    remind = '深度优先搜索排序'
    if opt.sort:
        result = sort_by_datetime(result)
        remind = '时间排序'
        
    with open(output_file, 'w') as f:
        f.write(f'本算法共找到 {len(result)} 张表\n\n')
        f.write('*'*50 + f'{remind}' + '*'*50 + '\n\n')
        
        for i in result:
            f.write(i + '\n\n')
            f.write(opt.delimiter + '\n\n')

if __name__ == '__main__':
    opt = parse_opt()
    print_by_format(opt)