from typing import Literal, Optional
import pandas as pd
import fire
from pathlib import Path
from tqdm.auto import tqdm
import genanki
import time

# 定义Anki卡片的模型
MODEL = genanki.Model(
    2559383000,
    'Basic (zhaisilong)',
    fields=[
        {'name': 'Front', 'font': 'Arial'},
        {'name': 'Back', 'font': 'Arial'}
    ],
    templates=[
        {
            'name': 'ZCard-1',
            'qfmt': '{{Front}}',
            'afmt': '{{FrontSide}}\n\n<hr id=answer>\n\n{{Back}}',
        },
    ],
    css='.card {\n font-family: Arial;\n font-size: 20px;\n text-align: center;\n color: black;\n background-color: white;\n}\n',
)

# 主程序
def csv2apkg(filename: str, title: Optional[str] = None, sep: str = ',', mode: Literal['single', 'double'] = 'double'):
    csv_path = Path(filename)
    
    # 检查文件是否为 .csv 格式
    assert csv_path.suffix == ".csv", "Input file must be a .csv file"
    
    if title and isinstance(title, str):
        pass
    elif csv_path.stem:
        title = csv_path.stem
    else:
        title = 'Deck'
        

    # 生成 .apkg 文件路径
    apkg_path = csv_path.parent / (csv_path.stem + ".apkg")

    # 读取 CSV 文件
    if mode == 'double':
        df = pd.read_csv(csv_path, sep=sep)
    elif mode == 'single':
        df = pd.read_csv(csv_path, header=None, names=["question"])
        df['answer'] = " "  # 保持空格 否则就会导入失败
    else:
        raise ValueError("Invalid mode: csv format error")

    # 创建 Anki Deck
    deck = genanki.Deck(
        deck_id=int(time.time()),  # 使用当前时间戳作为 Deck ID
        name=title
    )

    # 逐行遍历 CSV 并创建 Anki Note
    with tqdm(total=len(df)) as pbar:
        for _, row in df.iterrows():
            # 检查行是否包含 'question' 和 'answer' 列
            if 'question' in row and 'answer' in row:
                # 假设 question 和 answer 本身是 HTML 内容
                question_html = str(row['question'])  # 使用 HTML 格式的字符串
                answer_html = str(row['answer'])  # 使用 HTML 格式的字符串
                
                note = genanki.Note(
                    model=MODEL,
                    fields=[question_html, answer_html]
                )
                # 将 Note 添加到 Deck
                deck.add_note(note)
            else:
                print(f"Skipping row: Missing 'question' or 'answer' in {row}")

            pbar.update(1)

    # 将 Deck 写入 .apkg 文件
    genanki.Package(deck).write_to_file(apkg_path)

    print(f"Anki deck saved to {apkg_path}")

def main():
    fire.Fire(csv2apkg)

# 调用Fire模块，支持命令行调用
if __name__ == '__main__':
    main()