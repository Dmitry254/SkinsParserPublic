import webbrowser
import re
import time
import codecs


def open_links(file_name):
    file = codecs.open(f"items_list_{file_name}.txt", mode='r', encoding='utf-8')
    for line in file.readlines():
        url = re.findall(r'https?://\S+', line)
        if url:
            webbrowser.open(url[0], new=2, autoraise=True)
            time.sleep(0.5)
    file.close()


if __name__ == "__main__":
    open_links("cs")
