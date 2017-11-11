# -*- coding: utf-8 -*-
import os, sys, logging, time
import json

app_home = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.append(os.path.join(app_home, "lib"))
from jp_parser import JpParser

LOG_LEVEL = 'DEBUG'
logging.basicConfig(
  level=getattr(logging, LOG_LEVEL),
  format='%(asctime)s [%(levelname)s] %(module)s | %(message)s',
  datefmt='%Y/%m/%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

def parser():
  usage = 'Usage: python ** [--input] [--delimiter] [--help]'\
    .format(__file__)
  arguments = sys.argv
  data = dict()
  if len(arguments) == 1:
    logger.error(usage)
    return None
  arguments.pop(0)

  options = [option for option in arguments if option.startswith('-')]
  if '-h' in options or '--help' in options:
    logger.error(usage)
    return None
  if '-d' in options or '--delimiter' in options:
    position = arguments.index('-d') if '-d' in options else arguments.index('--delimiter')
    delimiter = arguments[position + 1]
    data['delimiter'] = delimiter
  if '-i' in options or '--input' in options:
    position = arguments.index('-i') if '-i' in options else arguments.index('--input')
    file_name = arguments[position + 1]
    data['input'] = file_name
  return data

# INPUT:
# 5,職場 義理 チョコ
def calc_stat(file_name, delimiter=','):
  logger.info(file_name)
  logger.info( 'delimiter=' + delimiter )

  stars = { 'X':0, '5':0, '4':0, '3':0, '2':0, '1':0 }
  # cat
  # prod
  with open(file_name ) as filedata:
    lines = filedata.readlines()
    for line in lines:
      text = line.strip()
      star = text.split(delimiter)[0]
      # logger.info(star )
      try:
        s = star[0]
        pass
      except:
        logger.error(text)
        continue
      if s in stars:
        stars[s] += 1
      else:
        stars['X'] += 1
        logger.error(star)
        logger.error(s)
        logger.error(s[0])
        logger.error( s[0] in stars)
  stat = { 'star': stars}
  return stat

def view_stat(stat):
  print( json.dumps( stat ) )


if __name__ == "__main__":
  start = time.time()
  param = parser()
  stat = calc_stat(param['input'], delimiter=param['delimiter'])
  view_stat( stat )
  # file_name  = app_home + '/dataset/rakuten/rakuten_reviews.txt'
  # target_dir = app_home + '/dataset/rakuten/'

  elapsed_time = time.time() - start
  logger.info("elapsed_time:{0}".format(elapsed_time) + "[sec]")