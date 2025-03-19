import matplotlib.pyplot as plt
import pandas as pd
import json
from portal import Portal


VIEWSCOLOR='gold'#'lemonchiffon' #          '#FFD700'
VIEWSContCOLOR='red'
DOWNLOADSCOLOR='dodgerblue'   #' lightsteelblue'
DOWNLOADSContCOLOR='blue'
DATASETSCOLOR='lightgrey'

SMALL_SIZE = 14
MEDIUM_SIZE = 16
BIGGER_SIZE = 20




class Plotpar():

    def __init__(self, nrows, ncols, sharex, sharey, figsize, **kwargs):
        super(Plotpar, self).__init__()

        self.nrows = nrows
        self.ncols = ncols
        self.sharex = sharex
        self.sharey = sharey
        # self.constrained_layout = None
        self.figsize = figsize
        for key, value in kwargs.items():
            setattr(self, key, value)

#
#
#       Views and Downaload Distribuitons per portal with Bar blots into 5 classes/intervals (not-linear)
#
#
def plot_views_kist_log(portals, allPortalsDatasetsFile, plotpar, typep='views', ylog=False, query=False, geospdt=False, color='black'):

    import numpy as np

    fig, axes = plt.subplots(nrows=plotpar.nrows, ncols=plotpar.ncols, sharex=plotpar.sharex, sharey=plotpar.sharey,
                             figsize=plotpar.figsize)

    fig.subplots_adjust(left=0.150, right=0.9750, top=0.975, bottom=0.025)

    ax = plt.gca()

    from matplotlib.ticker import PercentFormatter
    # ax.yaxis.set_major_formatter(PercentFormatter(100, symbol='%'))

    import matplotlib.ticker as plticker
    loc = plticker.MultipleLocator(base=25)

    j = 0
    # intsv=pd.DataFrame()

    bar_width=0.25
    for p in portals:

            pcity=p[1]
            all_datasets = df_datasets_portals(allPortalsDatasetsFile)
            dfm=all_datasets[all_datasets['city'] == pcity]
            dfm.rename(columns={'viewCount': 'dviews', 'downloadCount': 'dother'}, inplace=True)

            totdatasets = dfm['dviews'].count()

            if typep=='views' or typep=='all':

                intsv1 = dfm['dviews'][dfm.dviews < 11].count()
                intsv2 = dfm['dviews'][(dfm.dviews > 10) & (dfm.dviews < 101)].count()
                intsv3 = dfm['dviews'][(dfm.dviews > 100) & (dfm.dviews < 1001)].count()
                intsv4 = dfm['dviews'][(dfm.dviews > 1000) & (dfm.dviews < 10001)].count()
                intsv5 = dfm['dviews'][dfm.dviews > 10000].count()

                pctV = (100 * intsv1 / totdatasets, 100 * intsv2 / totdatasets, 100 * intsv3 / totdatasets,
                       100 * intsv4 / totdatasets, 100 * intsv5 / totdatasets)

            if typep=='downl' or typep=='all':
                intsd1 = dfm['dother'][dfm.dother < 11].count()
                intsd2 = dfm['dother'][(dfm.dother > 10) & (dfm.dother < 101)].count()
                intsd3 = dfm['dother'][(dfm.dother > 100) & (dfm.dother < 1001)].count()
                intsd4 = dfm['dother'][(dfm.dother > 1000) & (dfm.dother < 10001)].count()
                intsd5 = dfm['dother'][dfm.dother > 10000].count()

                pctD = (100 * intsd1 / totdatasets, 100 * intsd2 / totdatasets, 100 * intsd3 / totdatasets,
                        100 * intsd4 / totdatasets, 100 * intsd5 / totdatasets)

            labels = ('0-10', '10-100', '100-1K', '1K-10K', '>10k')
            step = 1
            x_pos = np.arange(0, len(labels) * step, step=step)


            if typep=='all':
                axes.flatten()[j].bar(x_pos-bar_width/2, pctV, bar_width, align='center', color=VIEWSCOLOR,alpha=1, label='Views')  # ,width=(x_pos[1]-x_pos[0])*0.9
                axes.flatten()[j].bar(x_pos+bar_width/2, pctD, bar_width, align='center', color=DOWNLOADSCOLOR, alpha=1, label='Downloads')  # ,width=(x_pos[1]-x_pos[0])*0.9
            else:
                if typep=='views':
                    axes.flatten()[j].bar(x_pos, pctV, align='center', color=VIEWSCOLOR,alpha=1, label='Views')
                else:
                    axes.flatten()[j].bar(x_pos, pctD, align='center', color=DOWNLOADSCOLOR, alpha=1, label='Downloads')

            axes.flatten()[j].set_xticks(x_pos)
            axes.flatten()[j].set_xticklabels(labels)

            axes.flatten()[j].set_ylabel('% of datasets', fontsize=13)
            axes.flatten()[j].set_title(p[1], fontsize=15)
            axes.flatten()[j].tick_params(axis='both', which='major', labelsize=11)
            axes.flatten()[j].yaxis.set_major_formatter(PercentFormatter(100, symbol='%'))
            axes.flatten()[j].set_ylim(ymin=0, ymax=100)
            axes.flatten()[j].yaxis.set_major_locator(loc)

            axes.flatten()[j].legend(loc='upper right', bbox_to_anchor=(1, 1), markerscale=0.2, frameon=True,
                                     fontsize=11)

            j += 1

    fig.tight_layout()
    
    plt.show()
    
    plt.close()



def extract_theme(Portal, datasets_file,groupcat=True):

    if groupcat:
        ### Mod 13112023
        if (Portal.platform == 'SocrataNew' or Portal.platform == 'Socrata'):

            df=datasets_file[datasets_file['city'] == Portal.city].groupby(['category']).sum().astype(int).reset_index()
            df['count'] = \
            datasets_file[datasets_file['city'] == Portal.city].groupby(['category']).size().reset_index(name='count')[
                'count']
            df.rename(columns={'viewCount': 'views', 'downloadCount': 'downl'}, inplace=True)

        else:
            pass

    else:
        df=pd.DataFrame()
        df['id']=datasets_file[datasets_file['city'] == Portal.city]['id']
        df['city']=datasets_file[datasets_file['city'] == Portal.city]['city']
        df['category']=datasets_file[datasets_file['city'] == Portal.city]['category']
        df['views']=datasets_file[datasets_file['city'] == Portal.city]['viewCount']
        df['downl']=datasets_file[datasets_file['city'] == Portal.city]['downloadCount']

    return df


def df_datasets_portals(allPortalsDatasetsFile):

    file = open(allPortalsDatasetsFile, 'r', encoding="utf-8")
    with file as json_file:
        l_all_datasets=json.load(file)
    file.close()
    return pd.DataFrame(l_all_datasets)



def show_categories(portals, allPortalsDatasetsFile, plotpar, legendloc='upper right', unspecified=False,downindex=False, logstats=False,log=True,sortcount=False,sortdown=False,sortmean=False,sortmedian=False,HVDvalue=False):

    import numpy as np
    from matplotlib.ticker import PercentFormatter
    import seaborn as sns

    if plotpar.nrows==plotpar.ncols==1:
        fig, axes = plt.subplots(nrows=plotpar.nrows, ncols=2, sharex=plotpar.sharex, figsize=plotpar.figsize, gridspec_kw={'width_ratios': [20, 1]})
        axes.flatten()[1].set_visible(False)
    else:
        fig, axes = plt.subplots(nrows=plotpar.nrows, ncols=plotpar.ncols, sharex=plotpar.sharex, figsize=plotpar.figsize)
        fig.subplots_adjust(wspace=0.420)
        fig.subplots_adjust(left=0.150, right=0.9750, top=0.975, bottom=0.025)
    # Axes location
    #ax_left, ax_bottom, ax_width, ax_height = 0.1, 0.3, 0.8, 0.65

    listPortalsCategoryUsage = []
    j = 0

    all_datasets=df_datasets_portals(allPortalsDatasetsFile)
    for p in portals:
        portal = Portal()
        portal.city = p[1]
        portal.url = p[0]
        portal.platform = p[3]
        catl = extract_theme(portal, all_datasets)
        catl = catl.sort_values(by='category')
        catl = catl.reset_index(drop=True)
        tot = catl['count'].sum()
        totv = catl['views'].sum()
        totd = catl['downl'].sum()
        catl['pdat'] = (catl['count'] / tot) * 100.0
        catl['pviews'] = (catl['views'] / totv) * 100.0
        catl['pdownl'] = (catl['downl'] / totd) * 100.0
        catl1 = extract_theme(portal, all_datasets, groupcat=False)  ### Estrate tutti i datasets stats e category
        catl1.loc[catl1['downl'] < 1, 'downl'] = 1
        catl1.loc[catl1['views'] < 1, 'views'] = 1
        stat = pd.DataFrame()
        stat['category'] = catl['category']
        stat['count'] = pd.to_numeric(catl["count"], downcast="integer")  # datasets number per category
        stat['pcount'] = stat['count'] / len(catl1)  # len(catl1) ->  datasets number per portal
        stat['views'] = catl['views']
        stat['pviews'] = catl['pviews']
        stat['downl'] = catl['downl']
        stat['pdownl'] = catl['pdownl']
        stat['mean'] = catl1.groupby(['category'])['downl'].mean().reset_index()['downl']
        perc=0.95
        if portal.platform == 'SocrataNew' or portal.platform == 'Socrata':
            stat['median'] = catl1.groupby(['category'])['downl'].median().reset_index()['downl']
            stat['p9X'] = catl1.groupby(['category'])['downl'].quantile(perc).reset_index()['downl']
            ec = DOWNLOADSContCOLOR
            fc = DOWNLOADSCOLOR
            xax = 'downl'
            xlabel = "Downloads"
        else:  ## CKAN e altri portali (solo Views)
            stat['median'] = catl1.groupby(['category'])['views'].median().reset_index()['views']
            stat['p9X'] = catl1.groupby(['category'])['views'].quantile(perc).reset_index()['views']
            ec = VIEWSContCOLOR
            fc = VIEWSCOLOR
            xax = 'views'
            xlabel = "Views"
        ###  HVDvalue metric
        ###
        stat['HVDvalue'] = stat['median'] * stat['pcount']+stat['p9X']*(stat['pcount']*(1-perc))
        ###
        if sortcount:
            catl.sort_values(by=['count'],inplace=True, ascending=False)
        if sortdown:
            catl.sort_values(by=['pdownl'],inplace=True, ascending=False)
        if sortmean:
            catl['meand']=catl['pdownl']/catl['count']
            catl.sort_values(by=['meand'],inplace=True, ascending=False)
        if sortmedian:
            catl['median']=stat['median']
            catl.sort_values(by=['median'],inplace=True, ascending=False)
        if HVDvalue:
            catl['HVDvalue']=stat['HVDvalue']
            catl.sort_values(by=['HVDvalue'],inplace=True, ascending=False)
        orderedcat = catl['category']
        if not unspecified:
            catl=catl[catl.category!='Unspecified']
        ### for boxplots
        city =  str(p[1])
        index = np.arange(len(catl['pdat']))
        bar_width = 0.25
        opacity = 1
        yticks = index + bar_width
        ###
        fontsize = MEDIUM_SIZE
        titlefontsize = BIGGER_SIZE
        legendsize=SMALL_SIZE
        if (sortcount or sortdown or sortmean or sortmedian or HVDvalue):
        # create plot
            index = np.arange(len(catl['pdat']))
            bar_width = 0.25
            opacity = 1

            rects1 = axes.flatten()[j].barh(index, catl['pdat'], bar_width, color=DATASETSCOLOR, alpha=opacity, label='Datasets')
            if portal.platform == 'SocrataNew' or portal.platform == 'Socrata':
                rects2 = axes.flatten()[j].barh(index + bar_width, catl['pviews'], bar_width, color=VIEWSCOLOR,
                                                alpha=opacity, label='Views')
                rects3 = axes.flatten()[j].barh(index + bar_width + bar_width, catl['pdownl'], bar_width, color=DOWNLOADSCOLOR,
                                                alpha=opacity, label='Downloads')
                yticks = index + bar_width
            else:
                rects3 = axes.flatten()[j].barh(index + bar_width, catl['pviews'], bar_width, color=VIEWSCOLOR,
                                                alpha=opacity, label='Views')
                yticks = index + bar_width / 2
            axes.flatten()[j].set_title(city, fontsize=titlefontsize, fontweight='bold', pad=2)
            axes.flatten()[j].set_yticks(yticks)
            axes.flatten()[j].set_yticklabels(catl['category'].to_list(),
                                              multialignment='center')  #### NB  multialignment. per funzionare bisogna forzare un "\n" in mezzo alla label.....
            axes.flatten()[j].invert_yaxis()
            axes.flatten()[j].tick_params(axis='both', which='major', labelsize=fontsize)
            axes.flatten()[j].xaxis.set_major_formatter(PercentFormatter(100, symbol='%', decimals=0))
            axes.flatten()[j].legend(loc=legendloc,
                                     markerscale=0.2, frameon=True, fontsize=legendsize)
            if unspecified:
                indU=catl['category'].tolist().index('Unspecified')
                plt.setp(axes.flatten()[j].get_yticklabels()[indU], color='red')
        else:
            j=-1
        if downindex:
            if not unspecified:
                stat = stat[stat.category != 'Unspecified']
                catl= catl[catl.category != 'Unspecified']
                catl1= catl1[catl1.category != 'Unspecified']
                ###orderedcat= orderedcat[orderedcat.category != 'Unspecified']
                orderedcat=orderedcat.drop(orderedcat.tolist().index('Unspecified'))
            ax2 = axes.flatten()[j].twinx()
            ax2.set_yticks(())
            xs = index + bar_width  # np.arange(0, len(catl['pdownl']), 1)
            if HVDvalue:
                ys = sorted(stat['HVDvalue'], reverse=True)  # catl['pdownl'],
            else:
                ys = stat['HVDvalue']       ##### NB per altre metriche fare attenzione a ordine asse categorie!!!!
            ymax = max(max(catl['pdat']), max(catl['pdownl']), max(catl['pviews']))
            axes.flatten()[j].set_xlim(xmin=0, xmax=ymax + 5)
            for x, y in zip(xs, ys):
                label = "{:.0f}".format(y)
                axes.flatten()[j].annotate(label,                       # this is the text
                                           (ymax + 5, x),               # these are the coordinates to position the label
                                           textcoords="offset points",  # how to position the text
                                           xytext=(10, +2),             # distance from text to points (x,y)
                                           ha='center', fontsize=fontsize,
                                           color='white',  #ec,   #="white",
                                           bbox=dict(boxstyle="circle,pad=0.3",
                                                     fc=fc, ec=ec, lw=2)
                                           )  # horizontal alignment can be left, right or center
        fig.subplots_adjust(
            top=0.955,
            bottom=0.05,
            left=0.154,
            right=0.992,
            hspace=0.0,
            wspace=0.064
        )
        # Draw Boxplot
        if logstats:
            fig.subplots_adjust(
                top=0.933,
                bottom=0.082,
                left=0.154,
                right=0.992,
                hspace=0.0,
                wspace=0.064
            )
            if log:
                axes.flatten()[j + 1].set_xticks(np.arange(0, 6))
                axes.flatten()[j + 1].set_xticklabels(10.0 ** np.arange(0, 6))
                whisL = 5
                whisU = 95
            else:
                axes.flatten()[j + 1].set_xticks(np.arange(1, 23))
                axes.flatten()[j + 1].set_xticklabels(np.arange(1, 23))
                whisL = 10
                whisU = 90
            axes.flatten()[j + 1].tick_params(axis='both', which='major', labelsize=fontsize)
            axes.flatten()[j + 1].set_title(city, fontsize=titlefontsize, fontweight='bold', pad=20)
            axes.flatten()[j + 1].set_yticks(yticks)
            b = sns.boxplot(data=catl1, x=xax, y='category', order=orderedcat, ax=axes.flatten()[j + 1],
                            showmeans=True, meanline=True,
                            flierprops={"marker": "x"},
                            boxprops={"facecolor": fc},  ##### (.3, .5, .7, .5)
                            medianprops={"color": "g", "linewidth": 3},
                            whiskerprops=dict(color=ec),
                            whis=[whisL, whisU],
                            )
            axes.flatten()[j + 1].set_xscale("log")
            axes.flatten()[j + 1].xaxis.grid(True)
            axes.flatten()[j + 1].set_xlim(xmin=0, xmax=10000000)
            #b.set_xlabel(xlabel, fontsize=fontsize+2)
            b.set_xlabel(xlabel, fontsize=MEDIUM_SIZE, weight="bold")
            #plt.xlabel('HVD index', fontsize=MEDIUM_SIZE, weight="bold")
            b.set_ylabel("", fontsize=fontsize)
            j += 2
        else:
            j += 1
        sns.despine(left=True)
        stat.set_index("category", drop=True, inplace=True)
        statdict = stat.to_dict(orient="index")
        dd = {'city': city, 'url':p[0], 'categorization':'Categories','platform':p[3], 'categories': statdict}
        listPortalsCategoryUsage.append(dd)
    plt.show()
    #return listPortalsCategoryUsage
    return


def write_portals_categories_usage(listPortalsCategoryUsage):
    import json

    output_dir = "output/"

    import os
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    PortalsCategoryUsageFile = output_dir + 'portals_category_usage.json'

    file = open(PortalsCategoryUsageFile, 'w')
    s = json.dumps(listPortalsCategoryUsage,
                   indent=4, ensure_ascii=False).encode('utf8').decode('latin1')
    file.writelines(s)
    file.close()


def write_portals_stats(statPortal):
    import json
    output_dir = "output/"
    import os
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    PortalsStatsFile = output_dir + 'portals_stats.csv'
    statPortal.to_csv(PortalsStatsFile, encoding='utf-8', index=False)



def show_cats_HVD(HVD_4_cats, typeChart='HVDi'):
    import pandas as pd
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    SMALL_SIZE = 14
    MEDIUM_SIZE = 16
    BIGGER_SIZE = 20
    fig.subplots_adjust(
        top = 0.978,
        bottom = 0.086,
        left = 0.154,
        right = 0.989,
        hspace = 0.0,
        wspace = 0.064
    )
    df_HVD_4_cats = pd.DataFrame.from_dict(HVD_4_cats, orient='index')
    df_HVD_4_cats.index.name = 'Category'

    plt.yticks(fontsize=MEDIUM_SIZE)
    plt.xticks(fontsize=MEDIUM_SIZE)
    ax.set(ylabel='')
    plt.legend(loc='lower right')

    if typeChart == 'HVDi':
        df_HVD_4_cats = df_HVD_4_cats.sort_values('HVDvalue')
        #ax = df_HVD_4_cats.plot.barh(y='HVDvalue', label='$HVDi_c$')
        bar=ax.barh(df_HVD_4_cats.index, df_HVD_4_cats['HVDvalue'],color='blue')
        ax.legend([bar],['$HVDi_c$'],loc='lower right',fontsize=SMALL_SIZE)
        #ax.set(xlabel='HVD index')
        plt.xlabel('HVD index',fontsize=MEDIUM_SIZE, weight="bold")
    else:
        df_HVD_4_cats = df_HVD_4_cats.sort_values('num_portals')
        #ax = df_HVD_4_cats.plot.barh(y='num_portals', color='r', label='Number of portals')
        bar=ax.barh(df_HVD_4_cats.index, df_HVD_4_cats['num_portals'],color='red', label='Number of portals')
        ax.legend([bar],['Number of portals'],loc='lower right',fontsize=SMALL_SIZE)
        #ax.set(xlabel='Portals coverage')
        plt.xlabel('Portals coverage',fontsize=MEDIUM_SIZE, weight="bold")
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(True)
    plt.show()


def table_cats_portals(categories_HVD, portals, output_dir, file_name, showcats=False):
    symbol = 'o'
    import pandas as pd
    tab_cats_portals = pd.DataFrame()
    tab_cats_portals['Category'] = 'Category'
    portals_list = []
    for p in portals:
        tab_cats_portals[p.city] = p.city
        portals_list.append(p.city)
    tab_cats_portals['Num_portals'] = 'Num_portals'

    for cat, v in categories_HVD.items():
        d = dict({'Category': cat})
        d.update(dict((p, ' ') for p in portals_list))
        d.update({'Num_portals': v['num_portals']})
        # Changed 19/02/2025 AQ for AttributeError: 'DataFrame' object has no attribute 'append'
        tab_cats_portals = tab_cats_portals.append(d, ignore_index=True)
        #
        #tab_cats_portals = tab_cats_portals._append(d, ignore_index=True)
        #
        for city in v['portals']:
            if showcats:
                tab_cats_portals.loc[tab_cats_portals['Category'] == cat, city] = find_original_category(portals, city,
                                                                                                         cat)
            else:
                tab_cats_portals.loc[tab_cats_portals['Category'] == cat, city] = symbol

    tab_cats_portals = tab_cats_portals.sort_values('Num_portals', ascending=False)
    tab_cats_portals = tab_cats_portals.drop('Num_portals', axis=1)

    if showcats:
        file_name = output_dir + "cats_" + file_name
    else:
        file_name = output_dir + symbol + "_" + file_name
    tab_cats_portals.to_csv(file_name, encoding='utf-8', index=False)


def find_original_category(portals, portal, allignedcategory):
    for p in portals:
        if p.city == portal:
            for cats, dictcats in p.categories.items():
                if dictcats['map'] == allignedcategory:
                    return cats
    return None


def portals_Unspecified():
    import os
    import numpy as np
    from matplotlib.ticker import PercentFormatter
    output_dir = "output/"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    portalsFile = output_dir+"portals_category_usage.json"
    with open(portalsFile, 'r') as json_file:
        data = json.load(json_file)
    portals_categories=[]

    for p in data:
        totd=0
        totc=0
        for v in p['categories'].values():
            totd+=v['count']
            totc+=1
        totc -= 1
        portals_categories.append([p['city'],p['categories']['Unspecified']['pcount'],totd,totc])
    fig, ax = plt.subplots()
    y_pos = np.arange(len(portals_categories))
    plt.yticks(fontsize=MEDIUM_SIZE)
    plt.xticks(fontsize=MEDIUM_SIZE)
    ax.barh(y_pos, [round(x[1]*100) for x in portals_categories], align='center',color='grey')
    ax.set_yticks(y_pos)
    ax.set_yticklabels([x[0] for x in portals_categories])
    ax.xaxis.set_major_formatter(PercentFormatter(100, symbol='%'))
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel('')
    ax.set_title('')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(True)
    plt.show()
    #print([(x[0],x[2],x[3]) for x in portals_categories])



if __name__ == '__main__':
    import os
    from datasets_from_portal import portals_sample

    output_dir = "output/"
    input_filename="AllPortalsDatasetsFile.json"
    allPortalsDatasetsFile = output_dir + input_filename

    showcat=True    ## True prints categories histograms for distint metric (as commented below)
    if showcat:
        portals = [["https://data.cityofnewyork.us", 'New York', ' ', 'Socrata', '3253', '8272963']]
        plotpar = Plotpar(nrows=1, ncols=1, sharex=False, sharey=False, figsize=[16, 96], constrained_layout=False)

        ### signature: def show_categories(portals, allPortalsDatasetsFile, plotpar, legendloc='upper right', unspecified=False,downindex=False, logstats=False,log=True,sortcount=False,sortdown=False,sortmean=False,sortmedian=False,HVDvalue=False):

        # Metrics datasets count:
        #show_categories(portals, allPortalsDatasetsFile, plotpar, 'lower right', True, False, False, False,True, False, False, False, False)

        # Metrics number downloads:
        #show_categories(portals, allPortalsDatasetsFile, plotpar, 'lower right',False, False, False, False,False, True, False, False, False)

        # Metrics mean downlaod:
        #show_categories(portals, allPortalsDatasetsFile, plotpar, 'upper right',False, False, False, False,False, False, True, False, False)

        # Metrics median downlaod:
        #show_categories(portals, allPortalsDatasetsFile, plotpar, 'upper right',False, False, False, False,False, False, False, True, False)

        # Metrics HVD:
        #show_categories(portals, allPortalsDatasetsFile, plotpar, 'lower right',False,True, True, True, False, False, False, False, True)     ### stampa HVD, Index (blubles) and Boxplots

        # BoxPLOT 95% (log=True)
        show_categories(portals, allPortalsDatasetsFile, plotpar,'',False,True,True,True,False,False,False,False,False)   ### OK Stampa solo BoxPLOT 95% (log=True)

    else:
        unspecifiedfreq = False
        if unspecifiedfreq:
            portals_Unspecified()

        else:       ## print usage histograms for all portals with data in  "allPortalsDatasetsFile"
            portals = portals_sample()
            plotpar = Plotpar(nrows=3, ncols=3, sharex=False, sharey=False, figsize=[15, 10], constrained_layout=True)
            plot_views_kist_log(portals, allPortalsDatasetsFile, plotpar, typep='all', ylog=False, query=False, geospdt=False,
                                color='black')


