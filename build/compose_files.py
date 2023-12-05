import sys

def main():
    # sys.argv[0] 是脚本名，sys.argv[1] 是第一个参数
    print(f'sys.argv: {sys.argv}')  # 打印 sys.argv 的值
    compose_files = sys.argv[1]

    print(f'compose_files: {compose_files}')

if __name__ == '__main__':
    main()