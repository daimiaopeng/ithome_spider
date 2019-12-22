import requests
from bs4 import BeautifulSoup

url = 'https://dyn.ithome.com/ithome/getajaxdata.aspx'  # IT之家评论信息请求地址
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
}

session = requests.session()
def get_news_hash(news_id):  # 得到文章的hash值
    '''hash值不是js计算得出的而是在评论页面源代码最后几行，它被设置成隐藏属性'''
    news_id = str(news_id)
    l = len(news_id) // 2
    url_page = 'https://www.ithome.com/0/' + news_id[0:l]+'/'+news_id[l:]+'.htm'
    html_home = session.get(url=url_page,headers = headers)
    '''理网页源代码信息，筛选出hash1'''
    tree = BeautifulSoup(html_home.text, 'html.parser')
    hash_1 = tree.find('iframe', attrs={"id":"ifcomment"})['data']

    '''筛选出hash2'''
    url_com = 'https://dyn.ithome.com/comment/'+hash_1
    html_home = session.get(url=url_com, headers=headers).text
    first = html_home.find('var pagetype = ')
    news_hash = html_home[first + 16:first + 32]
    return news_hash

def getpage_commentinfo(news_id):  # 输入文章url，输出用户列表
    print("正在爬新闻id：%s" %(news_id))
    news_id = str(news_id)
    to_braak = False
    all_comment = []
    for i in range(1, 6666):  # 调整页面
        data_page = {  # 发送的数据包
            'newsID': news_id,
            'hash': get_news_hash(news_id),
            'type': 'commentpage',
            'page': str(i),
            'order': 'false'
        }
        '''读出一页中所有用户信息'''
        page = session.post(url=url, data=data_page).text
        html = BeautifulSoup(page, 'html.parser')
        user_allmember = html.find_all('li', attrs={'class': 'entry'})  # 筛选网页信息，得到用户对象列表，列表里对应用户所有信息源码
        '''循环读取每一个用户对象的信息加载到字典中，再把字典加载到列表里去'''
        for x in range(0, 6666):
            long = len(user_allmember)  # 计算用户对象个数
            if long == 0:
                to_braak = True
                break
            user_infor = user_allmember[x]  # 取一个用户对象
            '''id 等级 姓名 评论 赞同数  反对数 设备信息 楼层 地址 时间 app版本 新闻id'''
            user_allinfo = {}
            user_allinfo['user_id'] = user_infor.div.a['title'].replace('软媒通行证数字ID：', '')
            user_allinfo['user_level'] = user_infor.div.find('div', attrs={'class': 'level'}).span.string.replace('Lv.',
                                                                                                                  '')
            user_allinfo['user_name'] = str(user_infor.find('span', attrs={'class': 'nick'}).string)
            try:
                user_allinfo['user_comment'] = user_infor.find('div', attrs={'class': 'comm'}).p.get_text()
            except:
                user_allinfo['user_comment'] = 'None'
            user_allinfo['user_comment_praise'] = user_infor.find('a', attrs={'class': 's'}).string.replace('支持(',
                                                                                                            '').replace(
                ')', '')
            user_allinfo['user_comment_oppose'] = user_infor.find('a', attrs={'class': 'a'}).string.replace('反对(',
                                                                                                            '').replace(
                ')', '')
            try:
                user_allinfo['user_dev'] = user_infor.find('a',
                                                           attrs={'href': '//m.ithome.com/ithome/download/'}).string
            except:
                user_allinfo['user_dev'] = 'None'
            user_allinfo['user_floor'] = user_infor.find('strong', attrs={'class': 'p_floor'}).string.replace('楼', '')
            try:
                temp = user_infor.find('div', attrs={'class': 'nmp'}).find('span', attrs={'class': 'posandtime'}) \
                    .string.replace('\xa0', ' ').replace('IT之家', '').replace('网友', '')
                temp = temp.split(' ')
                user_allinfo['user_address'] = None
                user_allinfo['user_time'] = temp[0] + ' ' + temp[1]
            except:
                user_allinfo['user_address'] = 'None'
            try:
                user_allinfo['user_app'] = user_infor.find('span', attrs={'class': 'mobile android'}).a[
                    'title'].replace('App版本：v', '')
            except:
                user_allinfo['user_app'] = 'None'
            user_allinfo['user_news_id'] = news_id
            all_comment.append(user_allinfo)
            # all_user =
            # print('已抓取'+str(user_allinfo['user_floor'])+'楼')
            if x == long - 1:  # 自动连接每一页
                break
        if to_braak == True:
            break
        if int(user_allinfo['user_floor']) == 1:
            break
    return all_comment

if __name__ == '__main__':
    i = 464435
    while True:
        try:
            newid = i
            data_list = getpage_commentinfo(newid)
            print(data_list)
        except Exception as e:
            print(e)
        finally:
            i = i -1
