# -*- coding: utf-8 -*
import pickle
import pandas as pd
import re
import globals
from utils import mapping_same_word

def clean_supplier_name(text):
    text = str(text)
    text = text.replace(u'\u3000', u' ').replace(u'\xa0', u' ').replace(r'\r\n','')
    text = text.lower()
    pos = text.find('(')
    if pos != -1:
        text = text[:pos]
    text = mapping_same_word(text)
    return text

def get_train_data():
    train_data = []
    with open('./train_data/train_data.pkl', 'rb') as f:
        train_data = pickle.load(f)
    return train_data



def get_train_data_base_on_file():
    try:
        train_data = get_train_data()
        return train_data
    except Exception as e:
        print(e)
        train_data = []
        base_path = './train_data/'
        for filename in globals.train_data_filenames:
            data_path = base_path + filename
            with open(data_path,'r',encoding='utf-8') as f:
                product_name_with_isbn = f.readline()
                product_token_result = f.readline()
                token_label = f.readline()
                while product_name_with_isbn and product_token_result and  token_label :
                    product_name_with_isbn = product_name_with_isbn.replace('\n','')
                    product_token_result = product_token_result.replace('\n','')
                    token_label = token_label.replace('\n','')

                    if token_label.replace(' ','') == '' or product_token_result.replace(' ','') == ''  or product_name_with_isbn.replace(' ','') == '':
                        continue
                    
                    try:
                        isbn , product_name = product_name_with_isbn.split('\t') 
                    except:
                        print(product_name_with_isbn.split('\t'))
                        print('get error')
                        continue
                        
                    tokens = product_token_result.split()
                    token_labels = token_label.split()    
                    for i in range(len(tokens)):
                        token = tokens[i]
                        token = mapping_same_word(token)
                        try:
                            label = token_labels[i]
                        except:
                            label = 0
                            
                        train_data.append((product_name,token,label))

                    product_name_with_isbn = f.readline()
                    product_token_result = f.readline()
                    token_label = f.readline()
                
        print(len(train_data))
        with open('./train_data/train_data.pkl', 'wb') as f:
            pickle.dump(train_data, f, pickle.HIGHEST_PROTOCOL)
        return train_data
    


# here is update ckip dict base on file

def get_ckip_dict_base_on_file():
    try:
        with open('./train_data/ckip_word_dict.pkl', 'rb') as f:
            ckip_word_dict = pickle.load(f)
        return ckip_word_dict
    except Exception as e:
        print(e)
        ckip_word_dict = {}
        supplier_df = pd.read_excel('./train_data/關鍵字和供應商.xlsx',sheet_name = '品名和廠商')
        supplier_words = supplier_df['廠商'].apply(clean_supplier_name).tolist()
        ckip_word_dict = {}
        for word in supplier_words:
            if len(word) > 5:
                continue
            word = mapping_same_word(word)
            if word in ckip_word_dict:
                ckip_word_dict[word] += 1
            else:
                ckip_word_dict[word] = 1

        train_data = get_train_data()
        for data in train_data:
            product_name , token , label = data
            if token == '' or len(token)>4 or re.match("^[A-Za-z0-9]*$", token) or len(token) <2 or token.isnumeric() :
                continue
            token = mapping_same_word(token)
            if token in ckip_word_dict:
                ckip_word_dict[token] += 1
            else:
                ckip_word_dict[token] = 1

                
        with open('./train_data/ckip_word_dict.pkl', 'wb') as f:
            pickle.dump(ckip_word_dict, f, pickle.HIGHEST_PROTOCOL)

        return ckip_word_dict





def save_product_tokens(product_name,tokens):
    # update train_data
    try:
        train_data = get_train_data()
        
        # update ckip wrod dict
        ckip_word_dict = {}
        with open('./train_data/ckip_word_dict.pkl', 'rb') as f:
            ckip_word_dict = pickle.load(f)


        for key, value in tokens.items():
            # update ckip word dict
            if not (key == '' or len(key)>4 or re.match("^[A-Za-z0-9]*$", key) or len(key) <2 or key.isnumeric()) :
                key = mapping_same_word(key)
                if key in ckip_word_dict:
                    ckip_word_dict[key] += 1
                else:
                    ckip_word_dict[key] = 1
            # update train_data
            train_data.append((product_name, key, int(value)))
            print((product_name, key, int(value)))
            
        from ckiptagger import construct_dictionary
        globals.dictionary = construct_dictionary(ckip_word_dict)
        # save to local
        with open('./train_data/train_data.pkl', 'wb') as f:
            pickle.dump(train_data, f, pickle.HIGHEST_PROTOCOL)
        with open('./train_data/ckip_word_dict.pkl', 'wb') as f:
            pickle.dump(ckip_word_dict, f, pickle.HIGHEST_PROTOCOL)
        
        return True
    except Exception as e:
        print(e)
        return False
        
    

def add_product(isbn, product_name, keywords, category):
    try:
        # update product csv
        df = pd.read_csv('./train_data/e7Line商品.csv')
        df.loc[df.index[-1]+1] = [str(isbn),str(product_name),str(keywords),str(category)]
        df.to_csv('./train_data/e7Line商品.csv', index=False)
        return True
    except Exception as e:
        print(e)
        return False
        
def add_bad_token(tokens):
    try:
        bad_token_list = []
        with open('./train_data/bad_token_list.pkl', 'rb') as f:
            bad_token_list = pickle.load(f)

        for token in tokens:
            token = str(token)
            token = token.replace(' ','')
            if token not in bad_token_list and token != '':
                bad_token_list.append(token)

        with open('./train_data/bad_token_list.pkl', 'wb') as f:
            pickle.dump(bad_token_list, f, pickle.HIGHEST_PROTOCOL)
        return bad_token_list

    except Exception as e:
        print(e)
        return bad_token_list


def add_bad_pos(_pos):
    try:
        bad_pos_list = []
        with open('./train_data/bad_pos_list.pkl', 'rb') as f:
            bad_pos_list = pickle.load(f)

        for _p in _pos:
            _p = str(_p)
            _p = _p.replace(' ','')
            if _p not in bad_pos_list and _p != '':
                bad_pos_list.append(_pos)

        with open('./train_data/bad_pos_list.pkl', 'wb') as f:
            pickle.dump(bad_pos_list, f, pickle.HIGHEST_PROTOCOL)
        return bad_pos_list

    except Exception as e:
        print(e)
        return bad_pos_list

def add_word_in_same_word_dict(word, keyword):
    try:
        word = word.lower()
        keyword = keyword.lower()
        if word in globals.same_word_dict:
            return True
        globals.same_word_dict[word] = keyword
        return True
    except Exception as e:
        print(e)
        return False
    