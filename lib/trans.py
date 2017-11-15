import subprocess

# require: translate-shell
# https://github.com/soimort/translate-shell

class Trans:
  def trans_ja2en(self, sentence):
    res = subprocess.run(["trans", "-b", "{ja=en}", sentence], stdout=subprocess.PIPE)
    return res.stdout.decode('utf-8')

  def trans_en2ja(self, sentence):
    res = subprocess.run(["trans", "-b", "{en=ja}", sentence], stdout=subprocess.PIPE)
    return res.stdout.decode('utf-8')

if __name__ == "__main__":
  trn = Trans()
  res = trn.trans_ja2en("優しさ")
  print(res)

  res = trn.trans_en2ja(res)
  print(res)
