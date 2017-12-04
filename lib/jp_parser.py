# -*- coding: utf-8 -*-

# MeCab: Yet Another Part-of-Speech and Morphological Analyzer
# -------------------------------------------------------------
# - http://taku910.github.io/mecab/
# - https://github.com/taku910/mecab
# exec following command when you check pos dic
# $ cat ./venv/lib/mecab/lib/mecab/dic/ipadic/pos-id.def | nkf -w

# Cabocha: Yet Another Japanese Dependency Structure Analyzer
# -------------------------------------------------------------
# - https://taku910.github.io/cabocha/

import MeCab
import CaboCha
import mojimoji, os, sys
from collections import namedtuple

app_home = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, os.path.join(app_home, "pymongo"))
sys.path.append(os.path.join(app_home, "lib"))
from database import load_politly_dic

# import sys, argparse
# sys.path.insert(0, TOP_DIR)
# from aramaki.database import get_politely_score, get_stopwords, bulk_search_for_politely_dict

class JpParser:
    """
    return parsed data with Mecab/Cabocha

    japanese have tree types of structure in a sentence. 
    - sentence > chunk > token
    - token is a tagged word

    ex)  'デザインが気に入り購入しました。'
        chunk1: 'デザイン / が '
         -> head_token: デザイン
        chunk2:' 気に入り'
         -> head_token: 気に入り
        chunk3: '購入 / し / まし / た /。'
         -> head_token: し
    """
    # exec following command when you check pos dic
    # $ cat ./venv/lib/mecab/lib/mecab/dic/ipadic/pos-id.def | nkf -w
    POS_DIC = {
        'BOS/EOS': 'EOS', # end of sentense
        '形容詞' : 'ADJ',
        '連体詞' : 'JADJ', # Japanese-specific POS like a adjective
        '副詞'   : 'ADV',
        '名詞'   : 'NOUN',
        '動詞'   : 'VERB',
        '助動詞' : 'AUX',
        '助詞'   : 'PART',
        '感動詞' : 'INTJ',
        '接続詞' : 'CONJ',
        '記号'   : 'SYM', # symbol
        '*'      : 'X',
        'その他' : 'X',
        'フィラー': 'X',
        '接頭詞' : 'X',
    }
    POS_2ND_DIC = {
        '代名詞':'PRON',
    }

    # ex) sys_dic_path='/usr/local/cai_venv/lib/mecab/lib/mecab/dic/ipadic-neologd/'):
    # https://github.com/neologd/mecab-ipadic-neologd/
    def __init__(self, *, sys_dic_path='', load_politely_dict=False):
        opt_m = "-Ochasen"
        opt_c = '-f4'
        if sys_dic_path:
            opt_m += ' -d {0}'.format(sys_dic_path)
            opt_c += ' -d {0}'.format(sys_dic_path)
        tagger = MeCab.Tagger(opt_m)
        tagger.parse('') # for UnicodeDecodeError
        self._tagger = tagger
        self._parser = CaboCha.Parser(opt_c)
        # load when you use sentimentanalysis
        # dictionary size is big (20k)
        if load_politely_dict:
            self.pol_dic = load_politly_dic("politely_JP")

    def search_politely_dict(self, words):
        politely_dict = dict()
        default_score = 0  # return score when not found in plitely dict
        for w in words:
            res = self.pol_dic[self.pol_dic['headword']==w]
            if len(res.index) > 0:
                politely_dict.update({res['headword'].values[0]: res['score'].values[0]})
            else:
                politely_dict.update({w:default_score})
        return politely_dict

    def get_sentences(self, text):
        """ 
        input: text have many sentences
        output: ary of sentences ['sent1', 'sent2', ...]
        """
        EOS_DIC = ['。', '．', '！','？','!?', '!', '?' ]
        sentences = list()
        sent = ''
        # split in first when text include '\n'
        temp = text.split('\\n')
        for each_text in temp:
            if each_text == '':
                continue
            for token in self.tokenize(each_text):
                # print(token.pos_jp, token.pos, token.surface, sent)
                # TODO: this is simple way. ex)「今日は雨ね。」と母がいった
                sent += token.surface
                if token.surface in EOS_DIC and sent != '':
                    sentences.append(sent)
                    sent = ''
            if sent != '':
                sentences.append(sent)
        return sentences

    def normalize(self, src_text):
        # Zenkaku to Hankaku ( handling japaneze character )
        normalized = mojimoji.han_to_zen(src_text, digit=False, ascii=False)
        normalized = mojimoji.zen_to_han(normalized, kana=False)
        return normalized.lower()

    def tokenize(self, sent):
        node = self._tagger.parseToNode( sent )
        tokens = list()
        idx = 0
        while node:
            feature = node.feature.split(',')
            token = namedtuple('Token', 'idx, surface, pos, pos_detail1, pos_detail2, pos_detail3,\
                                infl_type, infl_form, base_form, reading, phonetic')
            token.idx         = idx
            token.surface     = node.surface  # 表層形
            token.pos_jp      = feature[0]    # 品詞
            token.pos_detail1 = feature[1]    # 品詞細分類1
            token.pos_detail2 = feature[2]    # 品詞細分類2
            token.pos_detail3 = feature[3]    # 品詞細分類3
            token.infl_type   = feature[4]    # 活用型
            token.infl_form   = feature[5]    # 活用形
            token.base_form   = feature[6] if feature[6]!='*' else node.surface # 原型 ex)MacMini's base_form=='*'
            token.pos         = self.POS_DIC.get( feature[0], 'X' )     # 品詞
            token.reading     = feature[7] if len(feature) > 7 else ''  # 読み
            token.phonetic    = feature[8] if len(feature) > 8 else ''  # 発音
            # for BOS/EOS
            if token.pos != 'EOS':
                tokens.append(token)
                idx += 1
            node = node.next
        return tokens

    def tokenize_filtered_by_pos(self, sent, pos=['NOUN',]):
        tokens = [token for token in self.tokenize(sent) if token.pos in pos]
        return tokens

    def extract_words(self, text, *, filter_pos=[]):
        if len(filter_pos)!=0:
            return [ w.surface for w in self.tokenize(text) if not w.pos in filter_pos]
        else:
            return [ w.surface for w in self.tokenize(text)]

    def get_chunk_data(self, sentence):
        tree = self._parser.parse(sentence)
        tokens = self.tokenize(sentence)
        chunk_data = list()
        for i in range(0, tree.chunk_size()):
            chunk = namedtuple('Chunk', 'tokens, head_token, chunk_idx, depend_idx, src_idx, head_idx, func_idx,\
                                token_size, token_idx, feature_size, score, additional_info')
            c = tree.chunk(i)
            c_tokens = list()
            for j in range(c.token_pos, c.token_pos+c.token_size):
                c_tokens.append(tokens[j])
            chunk.tokens       = c_tokens
            chunk.head_token   = c_tokens[c.head_pos] # 主辞のtoken
            chunk.chunk_idx    = i                    # chunk_index
            chunk.depend_idx   = c.link               # dependecy chunk index
            chunk.src_idx      = list()               # source chunk (recieve chunk) index
            chunk.head_idx     = c.head_pos           # 主辞のindex
            chunk.func_idx     = c.func_pos           # 機能語のindex
            chunk.token_size   = c.token_size
            chunk.token_idx    = c.token_pos          # chunk先頭tokenのindex
            chunk.feature_size = c.feature_list_size
            chunk.score        = c.score
            chunk.additional_info = c.additional_info
            chunk_data.append(chunk)
        for i in range(0, tree.chunk_size()):
            c = tree.chunk(i)
            if c.link != -1:
                chunk_data[c.link].src_idx.append(i)
        return chunk_data

    def get_child_tokens(self, chunks, chunk, token):
        child_tokens = list()
        # a non head_token have no child (return empty list)
        if token.idx == chunk.head_token.idx:
            child_tokens.extend([t for t in chunk.tokens if t.idx!=token.idx])
            if len(chunk.src_idx)!=0:
                child_tokens.extend([chunks[si].head_token for si in chunk.src_idx])
        return child_tokens

    # just call aramaki.databases
    def get_stopwords(self):
        return get_stopwords(suffix='_JP')

    def debug(self, sentence):
        tree = self._parser.parse(sentence)
        # 0: tree format
        print(tree.toString(0))
        # 4: CONLL format
        print(tree.toString(4))

    # return senti_word_list
    def senti_tokenize(self, sentence):
        senti_tokens = {'pos':[], 'nue':[], 'neg':[]}
        words = [s.base_form.lower()
                    for s in self.tokenize(sentence)
                    if s.base_form!='*' and s.pos!='SYM']
        politely_dict = self.search_politely_dict(words)
        for w,score in politely_dict.items():
            key = 'pos' if int(score) > 0 else 'nue' if int(score) == 0 else 'neg'
            senti_tokens[key].append(w)
        return senti_tokens

    def senti_analisys(self, sentence):
        """
        output: sentiment score (1:positive < score < -1:negative)
        """
        score = 0
        num_all_words = 0
        tokens = self.tokenize(sentence)
        words = list()
        words.extend([s.base_form.lower() for s in tokens])
        politely_dict = self.search_politely_dict(words)
        # politely_dict = bulk_search_for_politely_dict(words, suffix='_JP')
        scores = list()
        scores.extend([politely_dict[w] for w in words])
        for i in range(0, len(tokens)):
            s = tokens[i]
            scores = self.apply_muliwords_rule_for_senti_analisys(i, tokens, scores)
            scores = self.apply_politely_reverse_rule_for_senti_analisys(i, tokens, scores, sentence)
        # evaluate score
        # -------------------------------------------------------------------
        for sc in scores:
            score += sc
            num_all_words += 1
        return round(score/num_all_words, 2)

    def apply_politely_reverse_rule_for_senti_analisys(self, i, tokens, scores, sentence):
        # ref) http://must.c.u-tokyo.ac.jp/nlpann/pdf/nlp2013/C6-01.pdf
        reverse_multiwords = [
            # headword,N-gram,apply_type
            ['の で は ない',       3, 'own'],
            ['わけ で は ない',     3, 'own'],
            ['わけ に は いく ない',4, 'src'],
        ]
        reverse_words = [
            # headword,pos,apply_type
            ['ない', 'AUX', 'own'],
            ['ぬ',   'AUX', 'own'],
            ['ない', 'ADJ', 'own'],
        ]
        apply_type = ''
        # detect politely-reverse word ( like a 'not' )
        # -------------------------------------------------------------------
        for r in reverse_words:
            if tokens[i].base_form==r[0] and tokens[i].pos==r[1]:
                apply_type = r[2]
        for r in reverse_multiwords:
            if i >= r[1]:
                multi_words = [ x.base_form.lower() for x in tokens if i-r[1] <= x.idx <= i]
                if ' '.join(multi_words) == r[0]:
                    apply_type = r[2]
        # apply for score
        # -------------------------------------------------------------------
        if apply_type!='':
            chunk = self.get_chunk_data(sentence)
            for j in range(0,len(chunk)):
                c = chunk[j]
                if c.token_idx <= i <= c.token_idx+c.token_size-1:
                    if apply_type=='own':
                        start_idx, end_idx = c.token_idx, (c.token_idx+c.token_size)
                    elif apply_type=='src':
                        sc = chunk[c.src_idx[-1]]
                        start_idx, end_idx = sc.token_idx, (sc.token_idx+sc.token_size)
                    # elif apply_type=='depend':
                    max_score_of_reverse = max(scores[start_idx:end_idx])
                    # print('max:', max_score_of_reverse, scores[start_idx:end_idx] )
                    del scores[start_idx:end_idx]
                    scores.append(-1*int(max_score_of_reverse))
                    scores.extend([0 for i in range(end_idx-start_idx-1)])
                    break
        return scores

    def apply_muliwords_rule_for_senti_analisys(self, i, tokens, scores):
        bigram_score, trigram_score = 0,0
        if i >= 1:  # bigram
            headword = ' '.join([tokens[i-1].base_form.lower(), tokens[i].base_form.lower()])
            res = self.search_politely_dict([headword])
            bigram_score = res[headword]
        if i >= 2:  # triram
            headword = ' '.join([tokens[i-2].base_form.lower(), tokens[i-1].base_form.lower(), tokens[i].base_form.lower()])
            res = self.search_politely_dict([headword])
            trigram_score = res[headword]
        # apply for scores
        if trigram_score != 0:
            del scores[i-3:i]
            scores.extend([trigram_score, 0, 0])
        elif bigram_score != 0:
            del scores[i-2:i]
            scores.extend([bigram_score, 0])
        return scores


if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument("INPUT", help="Specify input sentences",type=str,
    #                     nargs='?',default='',const='')
    # args = parser.parse_args()
    inp =  input('input japanese text(default text="d")>>')

    if inp=='d':
        # Japanese famous poem written by Soseki natusme.
        input_sentences = '我輩は猫である。名前はまだ無い。どこで生れたかとんと見当けんとうがつかぬ。何でも薄暗いじめじめした所でニャーニャー泣いていた事だけは記憶している。吾輩はここで始めて人間というものを見た。'
        input_sentences = 'チョコが甘くて好きです。２種類で５袋となっていて、残念でした。好みが合わなかったものは無駄になってしまいます。こんなに壊れやすいチョコは買うわけにはいかない'
    else:
        input_sentences = inp
    
    jp = JpParser(load_politely_dict=True)

    # print('ｕｓｂｱｲｳ')
    # print('normalized_str:', jp.normalize('ｕｓｂｱｲｳ'))

    sentences = jp.get_sentences(input_sentences)
    # print(jp.get_jp_stopwords())
    # print(jp.POS_DIC)
    # print(sentences)

    for  sent in sentences:
        print('BEGIN: '+sent+': --------------------------------------------------------------------------------------')
        # print(jp.extract_words(sent))
        # print(jp.extract_words(sent, filter_pos=['SYM']))
        # token --------------------------------------
        # sent_data = jp.tokenize(sent)
        # for s in sent_data:
        #   print(s.surface, s.base_form, s.pos)

        # chunk --------------------------------------
        # jp.debug(sent)
        # chunk_data = jp.get_chunk_data(sent)
        # for c in chunk_data:
        #     print(c.depend_idx, len(c.tokens), 
        #             'dst='+chunk_data[c.depend_idx].head_token.surface, 
        #             'src='+c.tokens[0].surface )
        #
        #     # extract feature with dependence
        #     for t in c.tokens:
        #         if t.base_form == '我輩':
        #             feature = chunk_data[c.depend_idx].head_token.base_form
        #             print('我輩dep=' + feature)
        print('senti_tokenize: ', jp.senti_tokenize(sent))
        print('senti_score: ', jp.senti_analisys(sent))

