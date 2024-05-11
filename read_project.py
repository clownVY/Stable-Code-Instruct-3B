# 给一个项目路径，读取该路径下所有的代码文件，返回一个字符串，字符串中包含所有代码文件的文件名和内容。
def read_code(path):
    import os
    code = ""
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".java") or file.endswith(".py"):
                with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                    code += f"│   │   │   │   ├── {file}\n"
                    code += f"{f.read()}\n"
    return code


# if __name__ == '__main__':
#     path = "/Users/clown/Desktop/aip-llm-proxy-master"
#     # print(read_code(path))
#     # 将结果保存为一个txt文件
#     with open("code_python.txt", "w", encoding="utf-8") as f:
#         f.write(read_code(path))

if __name__ == '__main__':
    with open("code_python.txt", "w", encoding="utf-8") as f:
        code = ""
        with open("/Users/clown/Documents/python/SDXLapi/SDXLall-api/src/app.py", "r", encoding="utf-8") as f1:
            code += f"{f1.read()}\n"
        f.write(code)
