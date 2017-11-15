# -*- coding: utf-8 -*-
import os, sys, logging, time, re

app_home = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

LOG_LEVEL = 'DEBUG'
logging.basicConfig(
  level=getattr(logging, LOG_LEVEL),
  format='%(asctime)s [%(levelname)s] %(module)s | %(message)s',
  datefmt='%Y/%m/%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

def get_label(detail):
  label = 'x'
  if re.match(r'ポジ', detail):
    label = 'p'
  elif re.match(r'ネガ', detail):
    label = 'n'
  else:
    logger.error('label |'+detail+'|')
  return label

def conv_dic(input_file):
  """
  input:
  ネガ（経験） あがく
  oytput:
  あがく  n  ネガ（経験）
  """
  logger.info(input_file)
  with open(input_file ) as filedata:
    lines = filedata.readlines()
    for line in lines:
      try:
        text = line.strip()
        # text = filedata.read()
        line_ary  = text.split("\t")
        # logger.info(  line_ary)
        label = get_label(line_ary[0])
        print( "\t".join([line_ary[1], label, line_ary[0]]) )
      except:
        logger.error('line>>'+line+'<<')
        continue

if __name__ == "__main__":
  start = time.time()
  input_file  = app_home + '/dataset/posneg_dic/src_wago.121808.pn'
  conv_dic(input_file)

  elapsed_time = time.time() - start
  logger.info("elapsed_time:{0}".format(elapsed_time) + "[sec]")
