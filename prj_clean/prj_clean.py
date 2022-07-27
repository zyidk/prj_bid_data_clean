import pandas as pd
import re
import numpy as np


# 出现20XX年第X季度，统计方式为XX月。

# 标题精简


# 招中标分类
def zhaob_zhongb_classify(df0):
    zhaoblist = ['公告', '变更', '预告', '招标公告', '招标变更', '招标预告', '国土']
    df0.loc[:, '招中标类型'] = ''
    df0.loc[df0['类型'].apply(lambda x:x in ['结果', '招标结果']), '招中标类型'] = '中标'
    df0.loc[df0['类型'].apply(lambda x:x in zhaoblist), '招中标类型'] = '招标'

    # df0.loc[df0['类型'] == '其他','招中标类型'] = '其他'

    # iszhongb = (df0['类型'] == '其他')&((~df0['中标企业'].isna())|
    #                                  (~df0['中标金额'].isna()))
    # df0.loc[iszhongb,'招中标类型'] = '中标'

    # iszhaob = (df0['类型'] == '其他')&(df0['标题'].apply(lambda x: '单一来源' in x))
    # df0.loc[iszhaob,'招中标类型'] = '招标'

    return df0

# 判断是否包含某些词


def isword_in_str(wordlist, string0):
    for word in wordlist:
        if word in string0:
            return word
    return False


# 有某词但没有另一词
def isword_in_notin_str(wordin, wordnotin, string0):
    index = string0.rfind(wordnotin)
    if index == -1:
        string1 = string0
    else:
        string1 = string0[1-index:]
    if wordin in string1:
        return wordin
    else:
        return False

# 同时存在两组词中的某两个


def isword_in_str_2list(str0, list0, list1):
    word0 = isword_in_str(list0, str0)
    word1 = isword_in_str(list1, str0)
    if word0 and word1:
        return f'{word1}{word0}'
    else:
        return False


# 应删除，判断单个标题
def istodel(title):
    wordlist0 = ['采购', '购置', '购买']
    wordlist0x = ['车辆', '轿车', '设备', '设施', '物资', '用品', '材料', '物料', '工具', '系统', '垃圾桶',
                  '电动车', '果皮箱', '工作服', '器材', '井盖', '药品', '家具']
    wordlist1 = ['安装', '维护', '保养', '维修', '清洗']
    wordlist1x = ['设备', '设施', '系统', '车辆', '器材']
    wordlist2 = ['汽保', '座椅', '铁丝', '装订机', '清洁剂',
                 '体检服务', '安装', '澄清', '答疑', '物业公开招租']
    wordlist3 = ['保证金（退还）', '保证金(退还)', '报废', '复印纸', '投诉', '废物箱', '门窗', '环卫服',
                 '市场调研', '家具采购', '低值易耗品',
                 '出租', '打印机', '雨衣', '垃圾袋', '服装采购', '除臭剂',
                 '环卫车', '工程设计', '招租', '桶装水', '改造', '工程结算', '冲洗车', '扫洗车', '责任险', '标识符', '电动手术床',
                 '生活用纸', '大米', '过滤器', '押钞车', '保洁物品', '垃圾分类桶', '吸污车', '无效', '招标代理']
    # 设计  太宽泛，不适合加进去
    isDel = isword_in_str_2list(title, wordlist0, wordlist0x)
    if isDel:
        return isDel
    isDel = isword_in_str_2list(title, wordlist1, wordlist1x)
    if isDel:
        return isDel

    if isword_in_notin_str('保险', '保险公司', title):
        return '保险'
    elif isword_in_notin_str('租赁', '租赁公司', title):
        # if '招租' not in title:
        return '租赁'
    elif isword_in_notin_str('燃油', '燃油公司', title):
        return '燃油'
    elif isword_in_str(wordlist2, title):
        return isword_in_str(wordlist2, title)
    elif isword_in_str(wordlist3, title):
        return isword_in_str(wordlist3, title)
    elif '房' in title and '改造' in title:
        return '房屋改造'

    elif '车辆' in title and '物业管理服务' not in title:
        return '车辆'
    else:

        return False

    return False

# 第二轮清洗 针对中标数据


def istodel_zb0(title):
    wordlist0 = ['终止', '中止', '停止', '暂停', '废标', '流标',
                 '作废', '异常', '撤销', '失败', '单据', '收据', '凭证']
    return isword_in_str(wordlist0, title)


# 第一轮清洗
# 补遗、调整、延期、暂停：类型 如果为“结果”则删除；如果为“变更”、“公告”则保留。但，需要把类型统一改为“变更”
def todel_df(dfin):
    wordlist0 = ['补遗', '调整', '延期', '暂停']
    dfin = dfin.set_index('iAutoID')
    df_drop_empty = pd.DataFrame({'iAutoID': [], 'DeleteReason': []})
    # 标题清洗
    seri_del0 = dfin['标题'].apply(istodel)
    dfx = dfin[seri_del0 == False]
    dfdel0 = dfin[seri_del0 != False]
    if dfdel0.empty:
        dfdel0 = df_drop_empty
    else:
        dfdel0.loc[:, 'DeleteReason'] = seri_del0
        dfdel0 = dfdel0.reset_index()[['iAutoID', 'DeleteReason']]

    # 标题清洗2 中标数据
    seri_del1 = dfx['标题'].apply(istodel_zb0)
    dfdel1 = dfx[seri_del1 != False]
    dfx = dfx[seri_del1 == False]
    if dfdel1.empty:
        dfdel1 = df_drop_empty
    else:
        dfdel1.loc[:, 'DeleteReason'] = seri_del1
        dfdel1 = dfdel1.reset_index()[['iAutoID', 'DeleteReason']]

    # 变更
    seri_del2 = dfx['标题'].apply(lambda x: isword_in_str(wordlist0, x))
    index0 = seri_del2 != False
    index1 = (dfx['类型'] == '变更') | (dfx['类型'] == '公告')
    index2 = dfx['类型'] == '结果'

    dfx.loc[index0 & index1, '类型'] = '变更'

    dfdel2 = dfx[index0 & index2]
    dfx = dfx[~(index0 & index2)]

    if dfdel2.empty:
        dfdel2 = df_drop_empty
    else:
        dfdel2.loc[:, 'DeleteReason'] = seri_del2
        dfdel2 = dfdel2.reset_index()[['iAutoID', 'DeleteReason']]

    dfx = dfx.reset_index()
    dfdel = pd.concat([dfdel0, dfdel1, dfdel2])
    dfdel.iAutoID = dfdel.iAutoID.astype(int)
    return dfx, dfdel


# 招标方式分类 单一来源采购其他条件另外处理
def bid_mode_classify(title):
    output = '其他'
    if isword_in_str(['竞谈', '谈判', '竞争性谈判'], title):
        output = '竞争性谈判'
#     elif isword_in_str(['公开','公开招标','竞争性谈判'],title):
#         output = '竞争性谈判'
    elif '公开招标' in title:
        output = '公开招标'
    elif '单一来源' in title:
        output = '单一来源采购'
    elif '询价' in title:
        output = '询价'
    elif '竞争性磋商' in title:
        output = '竞争性磋商'
    elif '框架协议' in title:
        output = '框架协议采购'
    elif '电子采购' in title:
        output = '电子采购'
    if isword_in_str(['比价', '比选'], title):
        output = '比价'
    elif '邀请' in title:
        output = '邀请招标'
    elif '磋商' in title:
        output = '竞争性磋商'
    elif '公开' in title:
        output = '公开招标'
    return output

# 招标方式分类
# 没用
# 若招标类型为公告、招标公告、预告、招标预告，且中标企业非空，且报名截止时间大于当前日期 --- 单一来源采购；


def bid_mode_classify_df(dfin):

    dfx = dfin.copy()
    dfx.loc[:, '招标方式'] = ''
    dfx.loc[dfx['招中标类型'] == '招标', '招标方式'] = dfx.loc[dfx['招中标类型']
                                                    == '招标', '标题'].apply(bid_mode_classify)


# 合同期限
def fetch_month0(title):

    month0 = -1
    pattern0 = re.compile(r'202\d年?[-至]?20\d{2}')
    pattern0x = re.compile(r'20\d{2}')

    pattern1 = re.compile(r'\D202\d[^\d至.-]')
    pattern1x = re.compile(r'\D202\d[年-]?\d{1,2}月')

    pattern2 = re.compile(r'202\d年\d{1,2}月至\d{1,2}月')
    pattern2x = re.compile(r'\d{1,2}月')

    pattern3 = re.compile(r'202\d年\d{1,2}月至20\d{2}年\d{1,2}月')
    pattern3x = re.compile(r'20\d{2}年')
    pattern3y = re.compile(r'\d{1,2}月')

    x = pattern1.findall(title)
    if len(x) > 0:
        month0 = 12
        xx = pattern1x.findall(title)
        if len(xx) == len(x):
            month0 = -1

    x = pattern0.findall(title)
    if len(x) > 0:
        xx = pattern0x.findall(x[0])
        month0 = (int(xx[1]) - int(xx[0])) * 12
        if month0 < 1:
            month0 = 12

    x = pattern2.findall(title)
    if len(x) > 0:
        xx = pattern2x.findall(x[0])
        month0 = (int(xx[1][:-1]) - int(xx[0][:-1])) + 1
        if month0 <= 1:
            month0 = -1

    x = pattern3.findall(title)
    if len(x) > 0:
        xx = pattern3x.findall(x[0])
        yy = pattern3y.findall(x[0])
        month0 = (int(xx[1][:-1]) - int(xx[0][:-1])) * \
            12 + int(yy[1][:-1]) - int(yy[0][:-1])
        if month0 < 1:
            month0 = 1

    return month0


# 业态分类
def ind_classify(titlein):

    办公0 = ['公司', '服务', '管理', '集团', '中心', '局', '机关',
           '支队', '政府', '办公', '大厦', '大楼', '厅', '办事']

    城市服务 = ['街道保洁', '环卫', '道路清扫', '垃圾转运', '公厕保洁', '公厕清扫', '道路清洗', '街道保安', '街道安保', '公厕管护', '卫生保洁',
            '河道清理', '河道保洁', '山林保洁', '保洁服务', '清扫保洁', '环卫作业', '环卫保洁', '环境保洁', '道路清洁', '场镇清扫']

    城市服务 = ['街道保洁', '环境保洁', '山林保洁', '公厕保洁', '河道保洁',
            '环卫', '道路清洗', '道路清扫', '街道安保', '垃圾转运',
            '公厕清扫', '公厕管护', '街道保安', '河道清理', '道路清洁', '场镇清扫',
            '街面秩序', '大道']

    城市服务1 = ['清扫', '保洁', '环卫', '清洁', '打扫']

    城市服务1x = ['镇', '河渠', '片区', '道路']

    # 一期二期三期物业管理服务   馆 新城 嘉苑 园 湾 湖 院 府 号 山 岛 庄 墅 里 品   写了 XX期  一般都是住宅
    住宅 = ['小区', '安置房', '前期物业', '公寓', '公租房', '拆迁房', '城中村',
          '宿舍', '住宅', '花园', '住房', '销售案场', '家园', '廉租房', '棚户区']

    办公1 = ['市民中心', '研究院', '研发中心', '红十字会', '公安局', '公安厅', '综合行政', '法院',
           '检察院', '营业网点', '分行', '电视台', '委员会', '银行', '红十字会', '办事处'

           ]

    公建 = [

        '文化中心', '文体中心', '文广中心', '文化馆',
        '机场', '休息室', '南站', '北站', '西站', '东站',
        '市民广场',
        '博物馆', '图书馆', '图书室', '档案馆', '展览馆', '会展中心',
        '科技馆', '科学技术馆',
        '体育中心', '健身中心',  '体育场', '体育馆', '运动管理中心', '奥体中心',
        '烈士陵园', '烈士墓',
        '国道', '轻轨', '轨道交通', '公路', '车站', '服务区', '地铁',
        '文化馆', '少年宫', '文化宫', '美术馆', '艺术中心', '校外活动中心',  '艺术馆',  '青少年活动中心',
        '纪念馆', '剧院',
        '救助管理站', '客运枢纽站',
        '地下通道', '天桥', '隧道'


    ]

    商业 = ['购物广场', '商厦', '百货大楼', '农贸市场', '购物中心', '酒店', '菜市场', '商业街', '美食街',
          '养老院', '敬老院', '老人院', '批发市场', '商铺', '电影院', '通讯城']

    产业园 = ['产业园', '孵化园', '大数据应用中心', '工业园', '软件园',
           '创新创业园', '物流园', '生态园', '科技园', '园区', '物流港', '创业园']

    景区 = ['景区', '湿地公园', '森林公园', '故居', '公园', '动物园', '度假区']

    其他 = ['公墓', '殡仪馆', '堤坊', '排涝站', '食堂', '大院', '厂区', '酒店', '福利院', '水库', '工厂', '电厂', '电站', '营区', '监狱', '家属院',
          '地块服务', '戒毒所', '环卫设施', '停车场', '仓库', '口岸', '杂技团', '车间', '基地', '看守所', '炼油厂', '厂区']
    # 外小  9中
    学校 = ['幼儿园', '小学', '中学', '大学', '校园', '学院', '党校', '学校', '校区', '美术院']

    医院 = ['卫生服务中心', '医院', '卫生院', '病防治院', '精神病院', '疾病预防控制中心', '妇幼保健', '计划生育服务中心',
          '卫生救治中心', '疾控', '社区卫生', '健康局', '保健服务中心', '保健中心', '康复中心']

    output = '未知'

    title = titlein.replace('政府采购', '')

    if '商业' in title:
        output = '商业'

    if isword_in_str(办公0, title):
        output = '办公'

    if isword_in_str(办公1, title):
        output = '办公'

    if isword_in_str(住宅, title):
        output = '住宅'

    if isword_in_str(城市服务, title):
        output = '城市服务'

    if isword_in_str(城市服务1, title) and isword_in_str(城市服务1x, title):
        output = '城市服务'

    if isword_in_str(公建, title):
        output = '公建'

    if isword_in_str(商业, title):
        output = '商业'

    if ('超市' in title) and ('网上超市' not in title):
        output = '商业'

    if ('电影' in title) and ('公司' not in title):
        output = '商业'

    if isword_in_str(产业园, title):
        output = '产业园'

    if isword_in_str(城市服务, title) and isword_in_str(['城区', '全域'], title):
        output = '城市服务'

    if isword_in_str(景区, title):
        output = '景区'

    if isword_in_str(其他, title):
        output = '其他'

    if isword_in_str(学校, title):
        output = '学校'

    if isword_in_str(医院, title):
        output = '医院'

    if isword_in_str(['附中', '附小'], title):
        output = '学校'

    if isword_in_str(['附院'], title):
        output = '医院'

    if '厂' in title:
        output = '未知'
    return output


# 业态分类依据招标公司
def ind_classify_offer(bid_offer):

    产业园 = ['产业园', '孵化园', '大数据应用中心', '工业园', '软件园', '创新创业园', '物流园', '生态园', '创业园']

    景区 = ['景区', '湿地公园', '森林公园', '故居', '公园', '动物园']

    其他 = ['公墓', '殡仪馆', '堤坊', '排涝站', '食堂', '大院', '厂区', '酒店', '福利院', '水库', '工厂', '电厂', '电站', '营区', '监狱', '家属院',
          '地块服务', '戒毒所', '环卫设施', '停车场']
    # 外小  9中
    学校 = ['幼儿园', '小学', '中学', '大学', '校园', '学院', '党校', '学校', '校区']

    医院 = ['卫生服务中心', '医院', '卫生院', '病防治院', '精神病院', '疾病预防控制中心',
          '妇幼保健', '计划生育服务中心', '卫生救治中心', '疾控', '社区卫生', '健康局']

    output = ''
    if type(bid_offer) != str:
        return output
    if len(bid_offer) < 2:
        return output

    if isword_in_str(产业园, bid_offer):
        output = '产业园'

    if isword_in_str(景区, bid_offer):
        output = '景区'

    if isword_in_str(其他, bid_offer):
        output = '其他'

    if isword_in_str(学校, bid_offer):
        output = '学校'

    if isword_in_str(医院, bid_offer):
        output = '医院'

    if isword_in_str(['附中', '附小'], bid_offer):
        output = '学校'

    if isword_in_str(['附院'], bid_offer):
        output = '医院'

    return output

# 删除句尾某词


def delifend(wordy, word0):
    len0 = len(word0)
    if wordy[-len0:] == word0:
        return wordy[:-len0]
    else:
        return wordy

# 删除句首某词


def delifhead(wordy, word0):
    len0 = len(word0)
    if word0 == wordy[:len0]:
        return wordy[len0:]
    else:
        return wordy

# 依据原标题标题精简


def title_clean_simple(title):
    pattern0 = re.compile('.+(?=采购项目)')
    pattern1 = re.compile('.+(?=项目)')

    pattern2 = re.compile('(?<=本级]).*')

    # pattern3 = re.compile('(?<=[：:]).*')

    pattern4 = re.compile('(?<=关于).*(?=[的,项目])')

    pattern5 = re.compile(r'.+(?=20\d{2}年)')

    pattern6 = re.compile('.+(?=竞争性谈判)')

    pattern7 = re.compile('（..编号.*）')

    pattern8 = re.compile('(?<=关于).*')

    pattern9 = re.compile('.*(?=单一来源采购)')

    delwordslist = ['采购竞争性磋商公告', '竞争性磋商公告', '公开招标中标公示', '谈判成交公告', '中标候选人公示',
                    '合同成交公告', '协议定点结果公告', '招投标评标结果公示', '竞价成交公告', '采购需求公开',
                    '邀请公告', '采购-公开', '（不见面开标）', '电子化公开招标采购变更公告', '公开招标',
                    '招标开标信息', '成交结果公告', '中标结果公告', '中标公示', '批次成交结果公示',
                    '招标公告', '询价公告', '需求公示', '采购公告', '合同公告', '成交公告', '中标公告', '询价书',
                    '-', '竞争性比选（询比）', '采购合同', '公开招租',
                    '合同', '竞价', '定点', '托管', '劳务', '招标', '政府', '公告', '结果', '方案',
                    '的网上超市', '答疑补遗文件',
                    '采购', '公开',
                    '的']
    del_head_words = ['招标公告：', '采购文件-']

    wordlist0 = ['重新招标', '变更', '更改', '更正', '补充', '增补', '补充通知', '恢复',
                 '预中标', '续签', '候选', '入围']

    wordlist0change = ['延期', '补遗', '调整', '暂停']

    title0 = title

    if len(title) < 2:
        return title

    x0 = pattern7.findall(title0)
    if len(x0) > 0:
        title0 = title0.replace(x0[0], '')

    title0 = title0.replace(' ', '')

    for word_head in del_head_words:
        title0 = delifhead(title0, word_head)

    x0 = pattern4.findall(title0)
    if len(x0) > 0:
        title0 = x0[0]
        if title0[-1] == '项':
            title0 = title0[:-1]

    x0 = pattern9.findall(title0)
    if len(x0) > 0:
        title0 = x0[0]
        x0 = pattern9.findall(title0)
        if len(x0) > 0:
            title0 = x0[0]

    x0 = pattern0.findall(title0)
    if len(x0) > 0:
        title0 = x0[0]

    if '项目部' not in title0:
        x0 = pattern1.findall(title0)
        if len(x0) > 0:
            title0 = x0[0]

    x0 = pattern2.findall(title0)
    if len(x0) > 0:
        title0 = x0[0]

    x0 = pattern8.findall(title0)
    if len(x0) > 0:
        title0 = x0[0]

#     x0 = pattern3.findall(title0)
#     if len(x0) > 0:
#         title0 = x0[0]

    if '政府采购意向' in title0:
        x0 = pattern5.findall(title0)
        if len(x0) > 0:
            title0 = x0[0]

    if '竞争性谈判' in title0:
        x0 = pattern6.findall(title0)
        if len(x0) > 0:
            title0 = x0[0]

    if len(title0) < 1:
        return title

    if title0[0] == '【':
        index0 = title0.find('】')
        title0 = title0[index0+1:]

    if len(title0) < 1:
        return title

    if title0[0] == '[':
        index0 = title0.find(']')
        title0 = title0[index0+1:]

    title0 = title0.replace('【', '')
    title0 = title0.replace('】', '')
    title0 = title0.replace('()', '')

    for word0 in delwordslist:
        #         title0 = title0.replace(word0,'')
        title0 = delifend(title0, word0)

    for word0 in delwordslist:
        #         title0 = title0.replace(word0,'')
        title0 = delifend(title0, word0)

    for word0 in wordlist0:
        if word0 in title:
            if word0 not in title0:
                title0 = title0 + word0
            break
    if '变更' not in title0:
        for word0 in wordlist0change:
            if word0 in title:
                title0 = title0 + '变更'
            break

    return title0


# 【2】
    # '[磋商]','【公告中】','【服务类】',
# 标题精简第一步
def title_clean_pre(df0):

    output = df0['原标题'].replace('\t', '')
    try:
        zb_code = str(df0['招标编号']).replace('\t', '')

        dellist = ['[线下]', '【国泰测试】', '[材料设备]', '[施工]', '[政府采购限额以下]', '[政采云]', '﹒', '【电子标】',
                   '[公开]', ]
        for word0 in dellist:
            output = output.replace(word0, '')

        output = delifhead(output, f'[{zb_code}]')
        output = delifhead(output, zb_code)
        output = delifhead(output, '：')
        output = delifhead(output, ':')

        output = output.replace(f'项目编号：{zb_code}', '')
        output = output.replace(zb_code, '')
    except Exception:
        pass

    # 中括号内XX市xx级的文字删除，文字小于4，删除
    pattern0 = re.compile(r'[\[【].*[\]】]')
    wordendlist = ['市', '区', '县', '镇', '村', '号', '级']
    x0 = pattern0.findall(output)
    for wordx in x0:
        if wordx[-2] in wordendlist:
            output = output.replace(wordx, '')
        elif len(wordx) < 6:
            output = output.replace(wordx, '')

    # XX咨询XX公司 关于 XX项目
    pattern1 = re.compile(
        r'.*(?:咨询|项目管理|置业|代理|招标|工程监理|工程管理|公共资源交易中心|政府采购中心|集中采购中心|服务中心).*关于')
    x0 = pattern1.findall(output)
    for wordx in x0:
        output = output.replace(wordx, '').replace('的', '')

    if '关于' in output:
        output = output.replace('关于', '').replace('的网上超市', '').replace('的', '')

    wordlist = ['【初始合同】', '【延续合同】',
                '【交易公告】', '[交易公告]', '【招标公告】', '【采购公告】', '[招标公告]', '【中标公告】', '【采购合同公告】'
                '[物业招标公告]', '[物业变更公告]', '【变更公告】',
                '【物业管理项目招投标中标结果公示表】', '[竞争性谈判]', '[竞争性磋商]',
                '[定点服务]', '[公开招标]', '[公开招标需求公示]',
                '【采购意向】',
                '服务类项目采购通告：']
    for word0 in wordlist:
        output = delifhead(output, word0)

    output = output.replace('()', '').replace(
        '（）', '').replace('(项目编号:)', '').replace('(采购编号：)', '')

    index0 = output.find('）') + 1
    if index0 > 0:
        if output[:index0] == output[index0:index0*2]:
            output = output[index0:]

    return output


# 批次号处理
# 第x批、批次x、标段x、x标段、第x次，
def get_batch_num(dfin, columnname='标题清洗'):
    pattern1 = re.compile(r'第[一二三四五六七八九十\d]{1,3}[次批]')
    pattern2 = re.compile(r'批次[一二三四五六七八九十\d]{1,3}')
    pattern3 = re.compile(r'标段[一二三四五六七八九十\d]{1,3}')
    pattern4 = re.compile(r'[一二三四五六七八九十\d]{1,3}标段')

    title0 = dfin['原标题']
    output = dfin[columnname]

    if (('变更' in title0) and ('变更' not in output)) or (('更正' in title0) and ('更正' not in output)):
        output += '变更'

    x0 = pattern1.findall(title0)
    if len(x0) > 0:
        if x0[0] not in output:
            output += f'({x0[0]})'

    x0 = pattern2.findall(title0)
    if len(x0) > 0:
        if x0[0] not in output:
            output += f'({x0[0]})'

    x0 = pattern3.findall(title0)
    if len(x0) > 0:
        if x0[0] not in output:
            output += f'({x0[0]})'

    x0 = pattern4.findall(title0)
    if len(x0) > 0:
        if x0[0] not in output:
            output += f'({x0[0]})'

    return output


# 标题精简最后一步
def title_clean_simple2(df0, columnname='标题清洗'):
    output = df0[columnname]
    entname = df0['招标企业']
    title0 = df0['原标题'].replace('前期物业介入服务', '前期物业服务')

    if df0['省份'] == '湖南省':
        if output[-2:] == '月至':
            output = output[:-9]
#     elif df0['省份'] == '云南省':

    if '前期物业服务' in title0 and output[-4:] != '物业服务':
        output = output + '项目前期物业服务'
        output = output.replace('前期物业介入服务', '')

    if type(entname) != str:
        return output
    else:
        if entname[-2:] == '本级':
            entname = entname[:-2]
        entlen = len(entname)

    if (entname in df0['原标题']) and (entname not in output):
        output = f'{entname}{output}'
        output = output.replace(' ', '')

    if f'{entname}：' == output[:entlen+1]:
        output = output[entlen+1:]


#     if len(output) > entlen + 18:
#         if entname == output[:entlen]:
#             output = output[entlen:]

    dic0 = {'原标题': title0, columnname: output}
    output = get_batch_num(dic0, columnname)

    if len(output) < 8:
        output = entname + output

    if (len(output) < 18) and ('物业管理服务' in output):
        output = entname + output

    if f'{entname}{entname}' == output[:entlen*2]:
        output = output[entlen:]

    if f'{entname}{entname}' == output[:entlen*2]:
        output = output[entlen:]

    return output


# 依据原标题标题精简，第二版
def title_clean_med(title):

    pattern2 = re.compile('(?<=本级]).*')

    pattern7 = re.compile('（..编号.*）')

    delwordslist = ['采购竞争性磋商公告', '竞争性磋商公告', '公开招标中标公示', '谈判成交公告', '中标候选人公示',
                    '合同成交公告', '协议定点结果公告', '招投标评标结果公示', '竞价成交公告', '采购需求公开',
                    '邀请公告', '采购-公开', '（不见面开标）', '电子化公开招标采购变更公告', '公开招标',
                    '招标开标信息', '成交结果公告', '中标结果公告', '中标公示', '批次成交结果公示',
                    '招标公告', '询价公告', '需求公示', '采购公告', '合同公告', '成交公告', '中标公告', '询价书',
                    '-', '竞争性比选（询比）', '采购合同', '公开招租',
                    '合同', '竞价', '定点', '托管', '劳务', '招标', '政府', '公告', '结果', '方案',
                    '的网上超市', '答疑补遗文件',
                    '采购', '公开',
                    '的']
    del_head_words = ['招标公告：', '采购文件-']

    delwordslist = []

    wordlist0 = ['重新招标', '变更', '更改', '更正', '补充', '增补', '补充通知', '恢复',
                 '预中标', '续签', '候选', '入围']

    # wordlist0change = ['延期', '补遗', '调整', '暂停']

    title0 = title

    if len(title) < 2:
        return title

    # 编号xxx删除
    x0 = pattern7.findall(title0)
    if len(x0) > 0:
        title0 = title0.replace(x0[0], '')

    title0 = title0.replace(' ', '')

    # 起始词条删除
    for word_head in del_head_words:
        title0 = delifhead(title0, word_head)

    # 删除关于
    title0 = title0.replace('关于', '')

    # X本级删除
    x0 = pattern2.findall(title0)
    if len(x0) > 0:
        title0 = x0[0]


#     x0 = pattern3.findall(title0)
#     if len(x0) > 0:
#         title0 = x0[0]

    if len(title0) < 1:
        return title
    if title0[0] == '【':
        title0 = title0.replace('【', '').replace('】', '')

    if len(title0) < 1:
        return title
    if title0[0] == '[':
        title0 = title0.replace('[', '').replace(']', '')

    title0 = title0.replace('【', '')
    title0 = title0.replace('】', '')
    title0 = title0.replace('()', '')

    for word0 in delwordslist:
        #         title0 = title0.replace(word0,'')
        title0 = delifend(title0, word0)

    for word0 in wordlist0:
        if word0 in title:
            if word0 not in title0:
                title0 = title0 + word0
            break

    # if '变更' not in title0:
    #     for word0 in wordlist0change:
    #         if word0 in title:
    #             title0 = title0 + '变更'
    #         break

    return title0

# 清洗
# title0 = 0 一般简化，=1最精简


def clean_df(df0, titleclean=0):
    df0 = df0.loc[df0['标题'].apply(lambda x: type(x) == str), :]

    # 第一次删除
    df1, dfdel = todel_df(df0)

    # 合同期限
    df2 = df1.copy()
    df2.loc[:, '合同期限'] = df2['标题'].apply(fetch_month0)
    df2.drop_duplicates(inplace=True)

    # 项目业态
    df2.loc[:, '项目业态'] = df2['标题'].apply(ind_classify)

    df_ind = df2['招标企业'].fillna('').apply(ind_classify_offer)
    df2.loc[df_ind != '', '项目业态'] = df_ind[df_ind != '']

    if titleclean == 0:
        # 标题精简
        df2 = df2.rename(columns={'标题': '原标题'})
        df2.loc[:, '标题清洗'] = df2.apply(title_clean_pre, axis=1)
        # df2.loc[~df2['招标编号'].isna(),'标题清洗'] = df2.loc[~df2['招标编号'].isna(),:].apply(title_clean_pre,axis = 1)
        df2.loc[:, '标题清洗'] = df2['标题清洗'].apply(title_clean_med)
        df2.loc[:, '标题清洗'] = df2.apply(title_clean_simple2, axis=1)
    else:
        # 标题精简
        df2 = df2.rename(columns={'标题': '原标题'})
        df2.loc[:, '标题清洗'] = df2.apply(title_clean_pre, axis=1)
        # df2.loc[~df2['招标编号'].isna(),'标题清洗'] = df2.loc[~df2['招标编号'].isna(),:].apply(title_clean_pre,axis = 1)
        df2.loc[:, '标题清洗'] = df2['标题清洗'].apply(title_clean_simple)
        df2.loc[:, '标题清洗'] = df2.apply(title_clean_simple2, axis=1)

    # 去重
    df2 = df2[df2['标题清洗'].apply(lambda x:len(x) > 4)]
    df2 = df2.sort_values(by=['标题清洗', '招标编号', '中标金额'],
                          ascending=[True, False, False])
    # df3 = df2.drop_duplicates(['招标编号'])

    del0 = df2.loc[~df2['招标编号'].isna() & df2['招标编号'].duplicated(), '招标编号']
    df3 = df2.drop(index=del0.index)
    df4 = df3.drop_duplicates(['标题清洗', '招标编号']).sort_index()

    # 输出
    newcolumns = ['iAutoID', '省份', '城市', '标题清洗',  '合同期限',
                  '项目业态',  '千里马分类', '类型', '发布时间', '项目类型(信息中心)',
                  '招标企业', '招标编号', '招标估价', '招标联系人', '招标联系电话', '代理联系人', '代理联系电话', '报名截止时间',
                  '投标截止时间', '中标企业', '中标金额', '中标单位联系人', '中标单位联系电话', '招标代理机构', '链接地址',
                  '中标单位关键词', '关键词中标物企', '天眼查中标物企', '附件下载（直接下载）', '原标题']
    # newcolumns =['省份', '城市','标题清洗',  '合同期限',
    #        '项目业态',  '千里马分类', '类型', '发布时间', '项目类型(信息中心)',
    #        '招标企业', '招标编号', '招标估价', '招标联系人', '招标联系电话', '代理联系人', '代理联系电话', '报名截止时间',
    #        '投标截止时间', '中标企业', '中标金额', '中标单位联系人', '中标单位联系电话', '招标代理机构', '链接地址',
    #        '中标单位关键词', '关键词中标物企', '天眼查中标物企', '附件下载（直接下载）', '原标题']
    dfout1 = df4.copy()[newcolumns]

    dfout2 = dfout1[['iAutoID', '省份', '城市', '标题清洗', '原标题', '合同期限',
                     '项目业态', '类型', '千里马分类', '项目类型(信息中心)', '招标企业', '招标编号',
                     '报名截止时间', '投标截止时间']]
    # dfout2 = dfout1[['省份','城市','标题清洗','原标题','合同期限',
    #                 '项目业态','类型','千里马分类','项目类型(信息中心)','招标企业', '招标编号',
    #                 '报名截止时间','投标截止时间']]

    dfdel0 = df0.loc[list(set(df0.index) - set(df1.index)), :]
    dfdel0.loc[:, '清除原因'] = '第一轮清洗'
    dfdel0 = dfdel0.rename(columns={'标题': '原标题'})
    dfdel1 = df2.loc[list(set(df2.index) - set(df4.index)), :]
    dfdel1.loc[:, '清除原因'] = '去重'

    dfout3 = pd.concat([dfdel0, dfdel1])
    return dfout1, dfout2, dfout3


def clean_jsondata(df0):
    # df00 = pd.DataFrame(datajson)

    renamedic = {'sProvinceName': '省份', 'sCityName': '城市', 'sTitle': '标题', 'sTenderType': '类型',
                 'sPubTime': '发布时间', 'sTenderCompany': '招标企业', 'sTenderNumber': '招标编号',
                 'sTenderMoney': '招标估价', 'sTenderContact': '招标联系人', 'sTenderContactPhone': '招标联系电话',
                 'sProxyContact': '代理联系人', 'sProxyContactPhone': '代理联系电话', 'sApplyEndTime': '报名截止时间',
                 'sEndTime': '投标截止时间', 'sWinCompany': '中标企业', 'sWinMoney': '中标金额', 'sWinContact': '中标单位联系人',
                 'sWinContactPhone': '中标单位联系电话', 'sProxyCompany': '招标代理机构'}
    df0.rename(columns=renamedic, inplace=True)

    df0 = df0.loc[df0['标题'].apply(lambda x: type(x) == str), :]

    # 第一次删除
    df1, dfdel = todel_df(df0)
    # 合同期限
    df2 = df1.copy()
    df2.loc[:, 'ContractPeriod'] = df2['标题'].apply(fetch_month0)
    df2.drop_duplicates(inplace=True)

    # 项目业态
    df2.loc[:, 'ProjectType'] = df2['标题'].apply(ind_classify)

    df_ind = df2['招标企业'].fillna('').apply(ind_classify_offer)
    df2.loc[df_ind != '', 'ProjectType'] = df_ind[df_ind != '']

    # 标题精简
    df2 = df2.rename(columns={'标题': '原标题'})
    df2.loc[:, 'NewTitle'] = df2.apply(title_clean_pre, axis=1)
    # df2.loc[~df2['招标编号'].isna(),'标题清洗'] = df2.loc[~df2['招标编号'].isna(),:].apply(title_clean_pre,axis = 1)
    df2.loc[:, 'NewTitle'] = df2['NewTitle'].apply(title_clean_med)
    df2.loc[:, 'NewTitle'] = df2.apply(
        lambda x: title_clean_simple2(x, columnname='NewTitle'), axis=1)
    # 标题最简化
    df2.loc[~df2['招标编号'].isna(), '原标题'] = df2.loc[~df2['招标编号'].isna(),
                                                  :].apply(title_clean_pre, axis=1)
    df2.loc[:, 'ShortTitle'] = df2['原标题'].apply(title_clean_simple)
    df2.loc[:, 'ShortTitle'] = df2.apply(
        lambda x: title_clean_simple2(x, columnname='ShortTitle'), axis=1)

    # 去重
    df2 = df2[df2['NewTitle'].apply(lambda x:len(x) > 4)]
    df2 = df2.sort_values(by=['NewTitle', '招标编号', '中标金额', '招标估价', '代理联系人', '投标截止时间'], ascending=[
                          True, False, False, False, False, False])
    # df3 = df2.drop_duplicates(['招标编号'])
    df2.loc[:, 'DeleteReason'] = df2['iAutoID']
    df2.loc[df2.duplicated(['招标编号']), 'DeleteReason'] = np.nan
    df2['DeleteReason'].fillna(method='ffill', inplace=True)
    del0 = df2.loc[~df2['招标编号'].isna() & df2['招标编号'].duplicated(), '招标编号']
    df3 = df2.drop(index=del0.index)
    dfdup0 = df2.loc[del0.index, ['iAutoID', 'DeleteReason']]

    df3.loc[df3.duplicated(['NewTitle', '招标编号']), 'DeleteReason'] = np.nan
    df3['DeleteReason'].fillna(method='ffill', inplace=True)
    df4 = df3.drop_duplicates(['NewTitle', '招标编号']).sort_index()
    dfdup1 = df3.loc[df3.drop(df4.index).index, ['iAutoID', 'DeleteReason']]

    df4.loc[df4.duplicated('NewTitle'), 'DeleteReason'] = np.nan
    df4['DeleteReason'].fillna(method='ffill', inplace=True)
    df5 = df4.drop_duplicates('NewTitle')
    dfdup2 = df4.loc[df4.drop(df5.index).index, ['iAutoID', 'DeleteReason']]

    dfdup = pd.concat([dfdup0, dfdup1, dfdup2])
    dfdup.DeleteReason = dfdup.DeleteReason.astype(int).astype(str)
    dfdup.DeleteReason = '去重：' + dfdup.DeleteReason
    df5 = df5.drop(columns='DeleteReason')

    # 输出
    # 有效数据
    # outputcolumns = ['iAutoID', 'IsDelete', 'DeleteReason', 'ContractPeriod', 'ProjectType',
    #                  'NewTitle', 'ShortTitle']
    outputcolumns1 = ['iAutoID', 'ContractPeriod',
                      'ProjectType', 'NewTitle', 'ShortTitle']
    dfout1 = df5.copy()[outputcolumns1]
    dfout1.loc[:, 'IsDelete'] = 0
    dfout1.loc[:, 'DeleteReason'] = ''

    # 无效数据
    # dfdel0 = df0.loc[list(set(df0.index) - set(df1.index)),:]
    # dfdel0.loc[:,'DeleteReason'] = '第一轮清洗'
    # dfdel0 = dfdel0.rename(columns={'标题':'原标题'})
    # dfdel1 = df2.loc[list(set(df2.index) - set(df4.index)),:]
    # dfdel1.loc[:,'DeleteReason'] = '去重'
    # dfout3 = pd.concat([dfdel0,dfdel1])

    dfout2 = pd.concat([dfdel, dfdup])
    dfout2.loc[:, 'IsDelete'] = 1
    dfout2.loc[:, 'ContractPeriod'] = -1
    dfout2.loc[:, 'ProjectType'] = ''
    dfout2.loc[:, 'NewTitle'] = ''
    dfout2.loc[:, 'ShortTitle'] = ''

    # # 包装输出格式
    # dfout3 = dfout3[['iAutoID','DeleteReason', 'ContractPeriod','ProjectType','NewTitle','ShortTitle']]
    # dfout3.ContractPeriod.fillna(-1,inplace=True)
    # dfout3.fillna('',inplace=True)
    # dfout3.loc[:,'IsDelete'] = 1

    dfout = pd.concat([dfout1, dfout2])
    dfout.iAutoID = dfout.iAutoID.astype(int)
    dfout.ContractPeriod = dfout.ContractPeriod.astype(int).astype(object)
    dfout.loc[dfout.ContractPeriod == -1, 'ContractPeriod'] = np.nan

    # dataout = json.loads(dfout.to_json(orient='records'))

    return dfout


def clean_file(filename, titletype=0):
    ol = '../data/raw/'
    # filename = '6.17-6.19招中标数据.xlsx'
    if filename[-4:] == '.csv':
        df0 = pd.read_csv(f'{ol}{filename}', encoding='gbk')
    elif filename[-4:] == 'xlsx':
        df0 = pd.read_excel(f'{ol}{filename}')

    dfout1, dfout2, dfout3 = clean_df(df0, titletype)

    if titletype == 0:
        name0 = '测试1'
    else:
        name0 = '精简1'

    with pd.ExcelWriter(f'../data/output/{name0}_{filename[:-4]}.xlsx') as file:
        dfout1.to_excel(file, sheet_name='清洗后数据', index=False)
        dfout2.to_excel(file, sheet_name='关键列', index=False)
        dfout3.to_excel(file, sheet_name='清除行', index=False)
        df0.to_excel(file, sheet_name='原数据', index=False)


def main():
    # ol = 'D:/工作/partjob/物业招中标数据清洗/data/raw/'
    filename = '5.11千里马招中标数据（清洗后）.xlsx'
    clean_file(filename)
