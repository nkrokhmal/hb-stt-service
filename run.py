import os

if os.path.exists('.env'):
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            print(var[0], var[1])
            os.environ[var[0]] = var[1]

from app import create_app
print(os.getenv('CONFIG_TYPE'))
client = create_app(os.getenv('CONFIG_TYPE') or 'debug')


if __name__ == '__main__':
    try:
        client.start_consuming()
    except Exception as e:
        raise Exception(e)