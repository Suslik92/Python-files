import logging

logging.basicConfig(filename='Log.txt',filemode='a',
                    level=logging.info,format='%(asctime)s -- %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logging.info('Testlog')
